# Event Payloads:
# https://developer.teamwork.com/projects/webhooks-explained/sample-payloads
import requests
from pyxtension.Json import Json

import config


def __urljoin(*urls):
    base = config.project_url
    return "{}/{}".format(base, "/".join(map(str, urls)))


def __get(url):
    response = requests.get(url, auth=(config.ci_api_token, 'x'))
    response.raise_for_status()
    return Json(response.json())


def _get_default_data():
    return {
        'color': '#FFFFFF',
        'text': 'Not implemented'
    }


def _set_project_infos(resp, data):
    resp['project_id'] = data.project.id
    resp['project_name'] = data.project.name
    return resp


def _set_project_comment_infos(resp, data):
    resp['project_id'] = data.comment.projectId
    return resp


def _set_comment_infos(resp, data):
    resp['comment_id'] = data.comment.id
    resp['comment_body'] = data.comment.body
    resp['comment_object_type'] = data.comment.objectType

    responseData = __get(__urljoin('comments', data.comment.id) + '.json')
    resp['comment_link'] = __urljoin(
        '#' + responseData.comment.get('comment-link'))
    resp['comment_object_name'] = responseData.comment.get('item-name')
    return resp


def _set_task_infos(resp, data):
    resp['task_id'] = data.task.id
    resp['task_name'] = data.task.name
    resp['task_link'] = __urljoin('#tasks', data.task.id)
    return resp


def _set_task_list_infos(resp, data):
    resp['task_list_id'] = data.taskList.id
    resp['task_list_name'] = data.taskList.name
    resp['task_list_link'] = __urljoin('#tasklists', data.taskList.id)
    return resp


def _set_card_infos(resp, data):
    resp['column_name'] = data.column.name
    resp['column_color'] = data.column.color
    resp['project_id'] = data.card.projectId
    resp['task_id'] = data.card.taskId
    resp['task_name'] = data.card.name
    resp['task_link'] = __urljoin('#tasks', data.card.taskId)
    return resp


def _set_board_column_infos(resp, data):
    def get_board_column_tasks(columnId):
        responseData = __get(
            __urljoin('boards', 'columns', columnId, 'cards.json')
        )
        return [int(card.taskId) for card in responseData.cards]

    responseData = __get(
        __urljoin('projects', data.task.projectId, 'boards', 'columns.json'),
    )
    for column in responseData.columns:
        print(data.task.id, get_board_column_tasks(column.id))
        if data.task.id in get_board_column_tasks(column.id):
            resp['column_name'] = column.name
            resp['column_color'] = column.color
            break
    return resp


def _set_board_column_icon(resp, data):
    column_name = resp['column_name']
    if not column_name:
        icon = ':white_circle:'
    elif column_name == 'NEXT':
        icon = ':large_blue_circle:'
    elif column_name == 'CURRENT':
        icon = ':diamond_shape_with_a_dot_inside:'
    elif column_name == 'IN DEVELOPMENT':
        icon = ':large_red_circle:'
    elif column_name == 'ACCEPT':
        icon = ':green_heart:'
    resp['column_icon'] = icon
    return resp


def _set_author_infos(resp, data):
    resp['author_id'] = data.eventCreator.id
    resp['author_name'] = '%s %s' % (data.eventCreator.firstName,
                                     data.eventCreator.lastName)
    resp['author_icon'] = data.eventCreator.avatar
    resp['author_link'] = __urljoin('#people', data.eventCreator.id, 'details')
    return resp


def task_created(data):
    resp = _get_default_data()
    resp = _set_card_infos(resp, data)
    resp = _set_board_column_infos(resp, data)
    resp = _set_board_column_icon(resp, data)
    resp = _set_author_infos(resp, data)
    resp = _set_project_infos(resp, data)

    if not resp.get('column_name'):
        return

    template = 'Created task %s at %s in %s'
    task_link = '[%s](%s)' % (resp['task_name'], resp['task_link'])
    task_list_link = '[%s](%s)' % (resp['task_list_name'],
                                   resp['task_list_link'])
    column = '%s %s' % (resp['column_name'], resp['column_icon'])
    resp['text'] = template % (task_link, task_list_link, column)
    return resp


def card_updated(data):
    resp = _get_default_data()
    resp = _set_task_infos(resp, data)
    resp = _set_board_column_icon(resp, data)
    resp = _set_author_infos(resp, data)

    template = 'Moved task %s to %s'
    task_link = '[%s](%s)' % (resp['task_name'], resp['task_link'])
    column = '%s %s' % (resp['column_name'], resp['column_icon'])
    resp['text'] = template % (task_link, column)
    return resp


def comment_created(data, update=False):
    resp = _get_default_data()
    resp = _set_comment_infos(resp, data)
    resp = _set_author_infos(resp, data)
    resp = _set_project_comment_infos(resp, data)

    if update:
        template = 'Updated comment on this %s\n%s'
    else:
        template = 'Commented on this %s\n%s'
    object_link = '%s: [%s](%s)' % (
        resp['comment_object_type'], resp['comment_object_name'],
        resp['comment_link'])
    comment_body = resp['comment_body']
    resp['text'] = template % (object_link, comment_body)
    return resp


def comment_updated(data):
    return comment_created(data, update=True)
