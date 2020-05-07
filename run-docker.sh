#!/bin/sh -xe
exec docker run --rm -p 8002:5000 --env-file .env --restart=on-failure mgbi/teamworkchat-bridge
