#!/bin/bash

mkdir deps
cd deps || exit

echo "################ Clone repositories"
git clone https://github.com/rohe/fedservice

echo "################ Update repositories"
cd fedservice && git pull && cd .. #git apply ../../fix_trust_marks.patch && cd ..

echo "################ Build docker image"
cd ..
# tag with date and time
VERSION=$(date +%Y%m%d%H%M)
docker build -t ddgu/fedservice:"${VERSION}" .
docker build -t ddgu/fedservice:latest .
