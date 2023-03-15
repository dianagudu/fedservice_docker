#!/usr/bin/env bash

cd /conf || exit 1

python3 /app/set_trust_anchor.py rp/auto ta/seid ta/swamid
python3 /app/set_trust_anchor.py rp/expl ta/seid ta/swamid
python3 /app/set_trust_anchor.py op/op ta/seid ta/swamid
python3 /app/set_trust_anchor.py intermediate/lu ta/seid ta/swamid
python3 /app/set_trust_anchor.py intermediate/umu ta/seid ta/swamid

python3 /app/add_subordinate.py -s rp/auto intermediate/lu
python3 /app/add_subordinate.py -s rp/expl intermediate/lu
python3 /app/add_subordinate.py -s op/op intermediate/umu
python3 /app/add_subordinate.py -s intermediate/umu ta/seid
python3 /app/add_subordinate.py -s intermediate/umu ta/swamid
python3 /app/add_subordinate.py -s intermediate/lu ta/seid
python3 /app/add_subordinate.py -s intermediate/lu ta/swamid
