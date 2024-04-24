#!/bin/bash

update-ca-certificates
cat /etc/ssl/certs/ca-certificates.crt >> `python -m certifi`

[[ -f "/conf/.env" ]] && source "/conf/.env"

[[ -z "${ENTITY_TYPE}" || ! -d "/app/${ENTITY_TYPE-}" ]] && (
    echo "ERROR: Entity type '$ENTITY_TYPE' not found"
    exit 1
)

cd "/app/${ENTITY_TYPE}" || exit 1

cp -ar /conf/* .
yq -o json -P '. *= load("conf.json")' default.json > merged_conf.json
mkdir -p log

exec python3 /app/entity.py "${ENTITY_NAME}" "merged_conf.json" "${ENTITY_TYPE}"