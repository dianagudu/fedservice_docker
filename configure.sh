#!/bin/bash

# get domain name from argument specified via
# Usage: ./configure.sh [-s src_conf] [-d dest_conf] [-h domain_name] [-c caddy_dir]]
# Example: ./configure.sh -s example-conf -d conf -h localhost -c caddy -y docker-compose.yml

die(){ echo >&2 "$@"; exit 1; }
usage(){
    echo "Usage: $0 [-s src_conf] [-d dest_conf] [-n domain_name] [-c caddy_dir]" >&2;
    echo "Defaults: src_conf=example-conf, dest_conf=conf, domain_name=localhost, caddy_dir=caddy" >&2;
    exit 0;
}

while getopts ":hs:d:c:n:" opt; do
  case $opt in
    h) usage ;;
    s) SRC="$OPTARG" ;;
    d) DEST="$OPTARG" ;;
    n) MY_DOMAIN_NAME="$OPTARG" ;;
    c) CADDY="$OPTARG" ;;
    :)  die "argument needed to -$OPTARG" ;;
    \?) die "invalid switch -$OPTARG" ;;
  esac
done

echo "Using the following configuration:"
echo "  Source config dir    > ${SRC:-example-conf}"
echo "  Dest config dir      > ${DEST:-conf}"
echo "  Caddy dir            > ${CADDY:-caddy}"
echo "  Domain name          > ${MY_DOMAIN_NAME:-localhost}"

echo "copying configuration files from ${SRC:=example-conf} to ${DEST:=conf}..."
cp -r "${SRC:=example-conf}" "${DEST:=conf}"

echo "Preparing caddy configuration in $CADDY..."
mkdir -p "$CADDY/data" "$CADDY/config"
mv "$DEST/Caddyfile" "$CADDY/Caddyfile"

# check if domain name is set
if [ -z "$MY_DOMAIN_NAME" ]; then
    echo "No domain name provided, using localhost"
else
    echo "Using domain name: ${MY_DOMAIN_NAME}"
    # get files that need to be updated
    FILES=$(grep -r 'localhost' $DEST $CADDY | cut -d':' -f1 | sort | uniq)
    echo "Updating all files: $FILES"
    # update domain name in config files
    sed -i -E "s/localhost/${MY_DOMAIN_NAME}/g" ${FILES}
    echo "Updated configuration files in $DEST and $CADDY with domain name: ${MY_DOMAIN_NAME}"
fi

echo "Running setup..."

docker run --rm \
  --user "$(id -u):$(id -g)" \
  -v "$(realpath ${DEST}):/conf" \
  --entrypoint python3 \
  ddgu/fedservice \
  /app/setup.py /conf

echo "Done!"