#!/bin/bash

/app/update_certs.sh

[[ -f "/conf/.env" ]] && source "/conf/.env"

[[ -z "${ENTITY_TYPE}" || ! -d "/app/${ENTITY_TYPE-}" ]] && (
    echo "ERROR: Entity type '$ENTITY_TYPE' not found"
    exit 1
)

cd "/app/${ENTITY_TYPE}" || exit 1

cp /app/utils.py .
cp -ar /conf/* .
yq -o json -P '. *= load("conf.json")' default.json > merged_conf.json
mkdir -p log
cp /app/entity.py "/app/${ENTITY_TYPE}/entity.py"

exec python3 "/app/${ENTITY_TYPE}/entity.py" "${ENTITY_TYPE}" "merged_conf.json"