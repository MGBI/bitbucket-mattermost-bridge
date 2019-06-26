import os

def get_env_setting(setting, default=None, obligatory=True):
    """Get the environment setting or return an exception"""
    var = os.getenv(setting) or default
    if not var and obligatory:
        raise ValueError('Set the {} env variable'.format(setting))
    return var

# Config file, please set the following settings:

# host the bridge is listening for, default: 0.0.0.0
host = get_env_setting('BRIDGE_LISTEN_ADDR', '0.0.0.0')

# listening port, default 5000
port = int(get_env_setting('BRIDGE_LISTEN_PORT', 5000))

# base url to teamwork projects
project_url = get_env_setting('TEAMWORK_PROJECT_BASE_URL')

# url to post bridged webhooks to
webhook_url = project_url

# Username showed in mattermost message
# "Enable Overriding of Usernames from Webhooks" must be turned on to work
username = get_env_setting('MATTERMOST_USERNAME', 'webhook')

# User icon showed in mattermost message
# "Enable Overriding of Icon from Webhooks" must be turned on to work
icon = get_env_setting('MATTERMOST_ICON', '', False)

# maximum number or Teamwork and Bitbucket projects to map
max_maps = 10

# map a Teamwork project id to a Teamwork Chat channel
teamwork_map = {
}
for i in range(1, max_maps):
    try:
        teamwork_map[get_env_setting('TEAMWORK_PROJECT_ID_%u' % i)] =\
            int(get_env_setting('TEAMWORK_CHAT_CHANNEL_ID_%u' % i))
    except ValueError as e:
        break

# map a Bitbucket project key to a Teamwork Chat channel
bitbucket_map = {
}
for i in range(1, max_maps):
    try:
        bitbucket_map[get_env_setting('BITBUCKET_PROJECT_KEY_%u' % i)] =\
            int(get_env_setting('TEAMWORK_CHAT_CHANNEL_ID_%u' % i))
    except ValueError as e:
        break

# map a Bitbucket user to a Teamwork API Token
bitbucket_users_map = {
}
for i in range(1, max_maps):
    try:
        bitbucket_users_map[
            get_env_setting('BITBUCKET_USER_NICKNAME_%u' % i)] =\
            get_env_setting('TEAMWORK_USER_TOKEN_%u' % i)
    except ValueError as e:
        break

# map a Teamwork user to a Teamwork API Token
teamwork_users_map = {
}
for i in range(1, max_maps):
    try:
        teamwork_users_map[get_env_setting('TEAMWORK_USER_ID_%u' % i)] =\
            get_env_setting('TEAMWORK_USER_TOKEN_%u' % i)
    except ValueError as e:
        break

# Teamwork API Token
ci_api_token = get_env_setting('TEAMWORK_CI_USER_TOKEN', obligatory=False)
