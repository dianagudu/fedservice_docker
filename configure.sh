#!/bin/bash

# get domain name from argument
MY_DOMAIN_NAME=$1

cp -r example-conf conf
mkdir -p caddy/data caddy/config
cp Caddyfile caddy/Caddyfile

# check if domain name is set
if [ -z "$MY_DOMAIN_NAME" ]; then
    echo "No domain name provided, using localhost"
else
    echo "Using domain name: ${MY_DOMAIN_NAME}"
    # get files that need to be updated
    FILES=$(grep -r 'localhost' conf caddy | cut -d':' -f1 | sort | uniq)
    # update domain name in config files
    sed -i -E "s/localhost/${MY_DOMAIN_NAME}/g" ${FILES}
    # update domain name in docker-compose.yml and create new compose file
    sed -E "s/localhost/${MY_DOMAIN_NAME}/g" docker-compose.yml > docker-compose.${MY_DOMAIN_NAME}.yml
fi

docker-compose run setup
echo "Done!"