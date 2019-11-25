########################################
#   Bitbucket Teamwork Chat Bridge     #
#                                      #
#   Written by Daniel Kappelle, 2016   #
#  Modified by Mateusz Grabowski, 2019 #
########################################

# import modules
import requests
from flask import Flask, request
from pyxtension.Json import Json

# import user config
import config
import payload

from teamwork.bridge import teamwork_app
from sentry.bridge import sentry_app

# Initialize flask app
app = Flask(__name__)

# Add Teamwork Webhook URLs
app.register_blueprint(teamwork_app, url_prefix='/teamwork')

# Add Sentry Webhook URLs
app.register_blueprint(sentry_app, url_prefix='/sentry')


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
    # that matches thee event-key, (: replaced by _), e.g.
    # repo_push
    payload_name = event.replace(":", "_")
    payload_func = getattr(payload, payload_name, None)

    if payload_func:
        # Parse the json data from the webhook
        data = Json(request.get_json())
        output = payload_func(data)
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
        # In case there's no templat for the event
        # throw an error
        print(event)
        return "Couldn't handle this Bitbucket event", 501


def submit_hook(hook_data):
    return submit_chat_hook(hook_data)


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

    channel_id = config.bitbucket_log_map.get(project_key)
    if not channel_id:
        raise ValueError("Unknown project_key `%s`" % project_key)
    url = config.webhook_url + '/chat/v5/rooms/%u/messages.json' % channel_id

    api_key = hook_data.get('author_token')
    if not api_key:
        author_nickname = hook_data.get('author_nickname') \
            or hook_data.get('author_username')
        if not author_nickname:
            raise ValueError("Missing author_nickname in the response: %s" %
                             hook_data)
        api_key = config.bitbucket_users_map.get(author_nickname)
        if not api_key:
            raise ValueError("Unknown author_nickname `%s`" % author_nickname)

    # Post the webhook
    response = requests.post(
        url,
        json=data,
        auth=(api_key, 'x'),
        headers={
            'Content-Type': 'application/json',
            'User-Agent': 'Bitbucket Webhooks Integration'
        }
    )
    response.raise_for_status()
    if response.status_code != 200:
        err = 'Request to mattermost returned an error %s, ' \
            'the response is:\n%s'
        raise ValueError(err % (response.status_code, response.text))


if __name__ == "__main__":
    print "==="
    print "Known commit authors:"
    print '\n'.join(config.bitbucket_users_map.keys())
    print "==="
    # Run flask app on host, this is set in config.py
    app.run(host=config.host, port=config.port)
