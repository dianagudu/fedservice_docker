#!/bin/bash

[[ -f "/conf/.env" ]] && source "/conf/.env"

[[ -z "${ENTITY_TYPE}" || ! -d "/app/${ENTITY_TYPE-}" ]] && (
    echo "ERROR: Entity type '$ENTITY_TYPE' not found"
    exit 1
)

cd "/app/${ENTITY_TYPE}" || exit 1

cp -ar /conf/* .

[[ ! -f "./conf.json" ]] && (
    echo "ERROR: Config file not found"
    exit 1
)

yq -o json -P '. *= load("conf.json")' default.json > merged_conf.json

exec python3 entity.py "${ENTITY_NAME}" "merged_conf.json"
