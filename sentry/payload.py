# Event Payloads:
# https://developer.teamwork.com/projects/webhooks-explained/sample-payloads
import config


def _get_default_data():
    return {
        'color': '#FFFFFF',
        'text': 'Not implemented'
    }


def _set_project_infos(resp, data):
    resp['project_id'] = data.project.id
    resp['project_name'] = data.project.name
    return resp


def _set_author_infos(resp, data):
    # fixed author
    resp['author_id'] = data.actor.id
    return resp


def _set_event_infos(resp, data):
    resp['event_action'] = data.action
    resp['event_name'] = data.data.event.title
    resp['event_link'] = data.data.event.web_url
    resp['release'] = data.data.event.release
    return resp


def _set_issue_infos(resp, data):
    resp['issue_action'] = data.action
    resp['issue_name'] = data.data.issue.title
    resp['issue_link'] = data.data.issue.web_url
    resp['release'] = data.data.issue.release
    assignedTo = data.data.issue.assignedTo
    if assignedTo:
        resp['assigned_to_id'] = int(assignedTo.id)
        resp['assigned_to_name'] = assignedTo.name
    return resp


def event_alert(data):
    resp = _get_default_data()
    resp = _set_project_infos(resp, data.data.event)
    resp = _set_author_infos(resp, data)
    resp = _set_event_infos(resp, data)

    template = '%s event %s for %s'
    event_action = resp['event_action'].title()
    event_link = '[%s](%s)' % (resp['event_name'], resp['event_link'])
    release = resp['release']
    resp['text'] = template % (event_action, event_link, release)
    return resp


def issue(data):
    resp = _get_default_data()
    resp = _set_project_infos(resp, data.data.issue)
    resp = _set_author_infos(resp, data)
    resp = _set_issue_infos(resp, data)

    template = '%s issue %s for %s'
    issue_action = resp['issue_action'].title()
    issue_link = '[%s](%s)' % (resp['issue_name'], resp['issue_link'])
    release = resp['release']
    resp['text'] = template % (issue_action, issue_link, release)
    if resp.get('assigned_to_name'):
        resp['text'] += ' assigned to %s' % resp['assigned_to_name']
    if resp['issue_action'] == 'assigned':
        resp['notify_user_id'] = resp['assigned_to_id']
    return resp


def event(data):
    """Only for Sentry 9"""
    resp = _get_default_data()
    # resp = _set_project_infos(resp, data.data.issue)
    resp['project_id'] = data.event.project
    resp['project_name'] = data.project_name

    # resp = _set_author_infos(resp, data)
    resp['author_id'] = 1

    # resp = _set_event_infos(resp, data)
    resp['event_action'] = 'triggered'
    resp['event_name'] = data.event.title
    resp['event_link'] = data.url
    resp['release'] = '<unknown release>'

    template = '%s event %s for %s'
    event_action = resp['event_action'].title()
    event_link = '[%s](%s)' % (resp['event_name'], resp['event_link'])
    release = resp['release']
    resp['text'] = template % (event_action, event_link, release)
    return resp
