#!/bin/bash

mkdir deps
cd deps || exit

echo "################ Clone repositories"
git clone https://github.com/SUNET/fedservice
git clone https://github.com/IdentityPython/idpy-oidc.git

echo "################ Update repositories"
cd fedservice && git pull && git checkout draft43_trust_mark_evaluation && cd ..
cd idpy-oidc && git pull && git checkout issuer_metadata && cd ..

echo "################ Applying patches"
cd fedservice && git apply ../../patches/fedservice.patch && cd ..
cd idpy-oidc && git apply ../../patches/idpy-oidc.patch && cd ..

echo "################ Build docker image"
cd ..
# tag with date and time
VERSION=$(date +%Y%m%d%H%M)
docker build -t ddgu/fedservice:"${VERSION}" .
docker build -t ddgu/fedservice:latest .
