#!/usr/bin/env bash

./set_trust_anchor.py rp/auto ta/seid ta/swamid
./set_trust_anchor.py rp/expl ta/seid ta/swamid
./set_trust_anchor.py op/op ta/seid ta/swamid
./set_trust_anchor.py intermediate/lu ta/seid ta/swamid
./set_trust_anchor.py intermediate/umu ta/seid ta/swamid

./add_subordinate.py -s rp/auto intermediate/lu
./add_subordinate.py -s rp/expl intermediate/lu
./add_subordinate.py -s op/op intermediate/umu
./add_subordinate.py -s intermediate/umu ta/seid
./add_subordinate.py -s intermediate/umu ta/swamid
./add_subordinate.py -s intermediate/lu ta/seid
./add_subordinate.py -s intermediate/lu ta/swamid
