#!/bin/bash

/app/update_certs.sh

exec python3 -m ofcli "$@"