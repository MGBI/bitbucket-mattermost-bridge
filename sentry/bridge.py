import requests
from flask import Blueprint, request
from pyxtension.Json import Json

import config
from sentry import payload

sentry_app = Blueprint('sentry_app', __name__)


@sentry_app.route("/hooks/", methods=['POST'])
def bridge_hook():
    # The event key is used to determine the type of event
    # e.g. installation, event_alert, issue, error.created
    event = request.headers.get('Sentry-Hook-Resource')

    # The template folder is searched for a template file
    # that matches thee event-key, (. replaced by _), e.g.
    # task_created
    # TODO: Sentry 10
    # assert event is not None
    payload_name = 'event'
    payload_func = getattr(payload, payload_name, None)

    if payload_func:
        # Parse the json data from the webhook
        data = Json(request.get_json())
        output = payload_func(data)
        if not output:
            print("%s ignored" % event)
            return "Ignored"
        # Submit the new, bridged, webhook to the mattermost
        # incoming webhook
        try:
            submit_hook(output)
        except (ValueError, AttributeError) as e:
            msg = str(request.get_json()) + '\n' + str(e)
            print(msg)
            return msg, 400
        return "Done"
    else:
        # In case there's no template for the event
        # throw an error
        print(event)
        return "Couldn't handle this Sentry event", 501


def submit_hook(hook_data):
    return submit_chat_hook(hook_data)


def submit_chat_hook(hook_data):
    text = hook_data.get('text')
    if not text:
        raise ValueError("Missing text in the response: %s" % hook_data)

    notify_user_id = hook_data.get('notify_user_id')
    if notify_user_id:
        handle = config.sentry_handles_map.get(notify_user_id)
        if not handle:
            raise ValueError("Unknown notify_user_id `%s`" % notify_user_id)
        text = '@%s %s' % (handle, text)

    # This function submits the new hook to Teamwork Chat
    data = {
        'message': {
            'body': text
        }
    }
    project_id = hook_data.get('project_id')
    if not project_id:
        raise ValueError("Missing project_id in the response: %s" % hook_data)

    channel_id = config.sentry_log_map.get(project_id)
    if not channel_id:
        raise ValueError("Unknown project_id `%s`" % project_id)
    url = config.webhook_url + '/chat/v5/rooms/%u/messages.json' % channel_id

    author_id = hook_data.get('author_id')
    if not author_id:
        raise ValueError("Missing author_id in the response: %s" %
                         hook_data)
    api_key = config.sentry_users_map.get(author_id)
    if not api_key:
        raise ValueError("Unknown author_id `%s`" % author_id)

    # Post the webhook
    response = requests.post(
        url,
        json=data,
        auth=(api_key, 'x'),
        headers={
            'Content-Type': 'application/json',
            'User-Agent': 'Teamwork Webhooks Integration'
        }
    )
    response.raise_for_status()
