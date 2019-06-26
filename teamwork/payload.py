# Event Payloads:
# https://developer.teamwork.com/projects/webhooks-explained/sample-payloads
import requests
from pyxtension.Json import Json

import config


def __urljoin(*urls):
    base = config.project_url
    return "{}/{}".format(base, "/".join(map(str, urls)))


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

    response = requests.get(
        __urljoin('comments', data.comment.id) + '.json',
        auth=(config.api_token, 'x')
    )
    response.raise_for_status()
    responseData = Json(response.json())
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


def _set_author_infos(resp, data):
    resp['author_id'] = data.eventCreator.id
    resp['author_name'] = '%s %s' % (data.eventCreator.firstName,
                                     data.eventCreator.lastName)
    resp['author_icon'] = data.eventCreator.avatar
    resp['author_link'] = __urljoin('#people', data.eventCreator.id, 'details')
    return resp


def task_created(data):
    resp = _get_default_data()
    resp = _set_task_infos(resp, data)
    resp = _set_task_list_infos(resp, data)
    resp = _set_author_infos(resp, data)
    resp = _set_project_infos(resp, data)

    template = 'Created task %s at %s'
    task_link = '[%s](%s)' % (resp['task_name'], resp['task_link'])
    task_list_link = '[%s](%s)' % (resp['task_list_name'],
                                   resp['task_list_link'])
    resp['text'] = template % (task_link, task_list_link)
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
