#!/bin/bash

mkdir deps
cd deps || exit

echo "################ Clone repositories"
git clone https://github.com/rohe/fedservice
git clone https://github.com/IdentityPython/idpy-oidc.git

echo "################ Update repositories"
cd fedservice && git pull && git checkout 8278eebd66a766cda4f11818d80decc608066f7c && cd ..
cd idpy-oidc && git pull && git checkout issuer_metadata && git checkout 688c1b7a60a58853b3848d7ad0f7e4e5b6143c69 && cd ..

echo "################ Build docker image"
cd ..
# tag with date and time
VERSION=$(date +%Y%m%d%H%M)
docker build -t ddgu/fedservice:"${VERSION}" .
docker build -t ddgu/fedservice:latest .
