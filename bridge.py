########################################
#   Bitbucket Mattermost Bridge        #
#                                      #
#   Written by Daniel Kappelle, 2016   #
#  Modified by Mateusz Grabowski, 2019 #
########################################

# import modules
import json
import requests
from flask import Flask, request
from pyxtension.Json import Json

# import user config
import config
import payload

# Initialize flask app
app = Flask(__name__)

# Folder for the template files
template_folder = "templates/"


@app.route("/")
def home_page():
    tpl = '''
    <h1>Bitbucket Teamwork Chat Bridge</h1>
    <p>Please refer to the repo on
    <a href='https://github.com/MGBI/bitbucket-mattermost-bridge'>
        Github
    </a> for the Readme.</p>
    '''
    return tpl


@app.route("/hooks/", methods=['GET', 'POST'])
@app.route("/hooks/<hook>", methods=['GET', 'POST'])
def bridge_hook(hook=''):
        # This function does all the magic

        # The event key is used to determine the type of event
        # e.g. repo:push, issue:created, etc.
        event = request.headers.get('X-Event-Key')

        # The template folder is searched for a template file
        # that matches thee event-key, (: replaced by -), e.g.
        # repo-push
        payload_name = event.replace(":", "_")
        payload_func = getattr(payload, payload_name, None)

        if payload_func:
            # Parse the json data from the webhook
            data = Json(request.get_json())
            output = payload_func(data)
            # Submit the new, bridged, webhook to the mattermost
            # incoming webhook
            submit_hook(config.webhook_url + hook, output)
            return "Done"
        else:
            # In case there's no templat for the event
            # throw an error
            print(event)
            return "Couldn't handle this event", 501


def submit_hook(url, hook_data):
    return submit_chat_hook(hook_data)

    # This function submits the new hook to mattermost
    data = {
        'attachments': [hook_data],
        'username': config.username,
        'icon_url': config.icon,
    }
    # Post the webhook
    response = requests.post(
        url,
        data=json.dumps(data),
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        err = 'Request to mattermost returned an error %s, the response is:\n%s'
        raise ValueError(err % (response.status_code, response.text))


def submit_chat_hook(hook_data):
    text = hook_data.get('text')
    if not text:
        raise ValueError("Missing text in the response: %s" % hook_data)

    # This function submits the new hook to Teamwork Chat
    data = {
        'message': {
            'body': text
        }
    }
    project_key = hook_data.get('project_key')
    if not project_key:
        raise ValueError("Missing project_key in the response: %s" % hook_data)
    channel_id = config.channels_map.get(project_key)
    if not channel_id:
        raise ValueError("Unknown project_key `%s`" % project_key)
    url = config.webhook_url + '/chat/v5/rooms/%u/messages.json' % channel_id

    author_nickname = hook_data.get('author_nickname')
    if not author_nickname:
        raise ValueError("Missing author_nickname in the response: %s" % hook_data)
    api_key = config.authors_map.get(author_nickname)
    if not api_key:
        raise ValueError("Unknown author_nickname `%s`" % author_nickname)

    # Post the webhook
    response = requests.post(
        url,
        data=json.dumps(data),
        auth=(api_key, 'x'),
        headers={
            'Content-Type': 'application/json',
            'User-Agent': 'Bitbucket Webhooks Integraion'
        }
    )
    response.raise_for_status()
    if response.status_code != 200:
        err = 'Request to mattermost returned an error %s, the response is:\n%s'
        raise ValueError(err % (response.status_code, response.text))


if __name__ == "__main__":
        # Run flask app on host, this is set in config.py
        app.run(host=config.host, port=config.port)
