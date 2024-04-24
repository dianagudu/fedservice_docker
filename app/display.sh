#!/bin/bash

/app/update_certs.sh

exec python3 /app/display_entity.py "$@"