#!/bin/bash

# get domain name from argument
MY_DOMAIN_NAME=$1

# check if domain name is set
if [ -z "$MY_DOMAIN_NAME" ]; then
    echo "Please provide a domain name as argument"
    exit 1
fi

# get files that need to be updated
FILES=$(grep -r 'fedservice.lh' conf traefik docker-compose.yml | cut -d':' -f1 | sort | uniq)

# update domain name in config files
sed -i -E "s/fedservice.lh/${MY_DOMAIN_NAME}/g" ${FILES}