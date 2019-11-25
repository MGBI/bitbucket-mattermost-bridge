**Forked from:**
https://github.com/danielkappelle/bitbucket-mattermost-bridge

# Integrated Bitbucket, Teamwork Project and Sentry -> Teamwork Chat bridge.
[![Docker Pulls](https://img.shields.io/docker/pulls/mgbi/teamworkchat-bridge.svg?maxAge=8600)][hub]
[![License](https://img.shields.io/github/license/mgbi/teamworkchat-bridge.svg?maxAge=8600)]()

[hub]: https://hub.docker.com/r/mgbi/teamworkchat-bridge/

## Bitbucket -> Teamwork Chat bridge
This tool converts the Bitbucket webhook request so that Teamwork Chat can interpret it properly.
Code:
```
./bridge.py
```

## Teamwork Project -> Teamwork Chat bridge
This tool converts the Teamwork Project webhook request so that Teamwork Chat can interpret it properly.
Code:
```
./teamwork/bridge.py
```

## Sentry -> Teamwork Chat bridge
This tool converts the Sentry webhook request so that Teamwork Chat can interpret it properly.
Code:
```
./sentry/bridge.py
```

# Installation
This installation guide is based on `Ubuntu 14.04` with `Python 2.7` and `pip` installed.

## Clone repo
`$ git clone https://github.com/MGBI/bitbucket-mattermost-bridge`

## Install dependencies
`$ pip install -r requirements.txt`

## Edit config
You can edit config to hardcode variable
`$ vim config.py` or `$ nano config.py` (or whatever editor you prefer)

Or you can use environment variables to set your bridge configuration.
Here is the available variables:

* TEAMWORK_CHAT_HOOK (mandatory) : url to post bridged webhooks to
* BRIDGE_LISTEN_ADDR : host the bridge is listening for, default: 0.0.0.0
* BRIDGE_LISTEN_PORT : listening port, default 5000
* MATTERMOST_USERNAME : Username showed in mattermost message (**Enable Overriding of Usernames from Webhooks** must be turned on mattermost)
* MATTERMOST_ICON : User icon showed in mattermost message (**Enable Overriding of Icon from Webhooks** must be turned on mattermost)

## Run the bridge
### Directly
This can be useful for debugging

`$ python bridge.py`

### As a daemon
If you don't have already installed upstart:
```
$ sudo apt-get update
$ sudo apt-get install upstart
```

Create the upstartfile
`$ vim /etc/init/bitbucket-mattermost-bridge.conf` (or nano, or gedit...)

```
description "Bitbucket mattermost integration"
author  "Daniel Kappelle <daniel.kappelle@gmail.com>"

start on runlevel [234]
stop on runlevel [0156]

chdir /path/to/bitbucket-mattermost-bridge/
exec python /path/to/bitbucket-mattermost-bridge/bridge.py
respawn
```

You can now start/stop/restart the daemon using

`$ sudo start|stop|restart bitbucket-mattermost-bridge`

### With docker

```
docker build -t bitbucket-mattermost-bridge .
docker run -d -e TEAMWORK_CHAT_HOOK=https://chat.example.com/hooks/ -p 5000:5000 bitbucket-mattermost-bridge
```
or better:
```
./build-docker-image.sh
./run-docker.sh    or    docker-compose up
```

# Trouble
If there's any trouble, please contact me or create an issue
