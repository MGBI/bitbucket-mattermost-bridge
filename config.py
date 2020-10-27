import os


def get_env_setting(setting, default=None, obligatory=True):
    """Get the environment setting or return an exception"""
    var = os.getenv(setting) or default
    if var is None and obligatory:
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
teamwork_chat_map = {
}
for i in range(1, max_maps):
    try:
        teamwork_chat_map[
            int(get_env_setting('TEAMWORK_PROJECT_ID_%u' % i))] = \
            int(get_env_setting('TEAMWORK_CHAT_CHANNEL_ID_%u' % i))
    except ValueError:
        break

# map a Bitbucket project key to a Teamwork log channel
bitbucket_log_map = {
}
for i in range(1, max_maps):
    try:
        bitbucket_log_map[
            get_env_setting('BITBUCKET_PROJECT_KEY_%u' % i)] = \
            int(get_env_setting('TEAMWORK_LOG_CHANNEL_ID_%u' % i))
    except ValueError:
        break

# map a Sentry project id to a Teamwork log channel
sentry_log_map = {
}
for i in range(1, max_maps):
    try:
        sentry_log_map[
            int(get_env_setting('SENTRY_PROJECT_ID_%u' % i))] = \
            int(get_env_setting('TEAMWORK_LOG_CHANNEL_ID_%u' % i))
    except ValueError:
        break

# map a Bitbucket user to a Teamwork API token
bitbucket_users_map = {
}
for i in range(1, max_maps):
    try:
        bitbucket_users_map[
            get_env_setting('BITBUCKET_USER_NICKNAME_%u' % i)] = \
            get_env_setting('TEAMWORK_USER_TOKEN_%u' % i)
    except ValueError:
        break

# map a Teamwork user to a Teamwork API token
teamwork_users_map = {
}
for i in range(1, max_maps):
    try:
        teamwork_users_map[
            int(get_env_setting('TEAMWORK_USER_ID_%u' % i))] = \
            get_env_setting('TEAMWORK_USER_TOKEN_%u' % i)
    except ValueError:
        break


# map a Sentry user to a Teamwork API token
sentry_users_map = {
}
for i in range(1, max_maps):
    try:
        sentry_users_map[
            int(get_env_setting('SENTRY_USER_ID_%u' % i))] = \
            get_env_setting('TEAMWORK_USER_TOKEN_%u' % i)
    except ValueError:
        break


# map a Bitbucket user to a Teamwork Chat handle
bitbucket_handles_map = {
}
for i in range(1, max_maps):
    try:
        bitbucket_handles_map[
            get_env_setting('BITBUCKET_USER_NICKNAME_%u' % i)] = \
            get_env_setting('TEAMWORK_USER_HANDLE_%u' % i)
    except ValueError:
        break


# map a Sentry user to a Teamwork Chat handle
sentry_handles_map = {
}
for i in range(1, max_maps):
    try:
        sentry_handles_map[
            int(get_env_setting('SENTRY_USER_ID_%u' % i))] = \
            get_env_setting('TEAMWORK_USER_HANDLE_%u' % i)
    except ValueError:
        break

# Teamwork API Token
ci_api_token = get_env_setting('TEAMWORK_CI_USER_TOKEN', obligatory=False)
