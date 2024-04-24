#!/bin/bash

update-ca-certificates
cat /etc/ssl/certs/ca-certificates.crt >> `python -m certifi`