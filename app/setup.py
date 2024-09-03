#!/usr/bin/env python3
import json
import sys
import os

from fedservice import combo
from idpyoidc.util import load_config_file

from fedservice.combo import FederationCombo
from fedservice.utils import make_federation_combo
from utils import load_values_from_file


# get the configuration folder from the command line
if len(sys.argv) != 2:
    print("Usage: python3 setup.py <config_folder>")
    sys.exit(1)
config_folder = sys.argv[1]

# check if the configuration folder exists and is a directory
if not os.path.isdir(config_folder):
    print(f"Error: {config_folder} is not a directory")
    sys.exit(1)


ENTITY = json.loads(open(f"{config_folder}/entities.json", "r").read())


def get_federation_entity(entity):
    if isinstance(entity, FederationCombo):
        return entity["federation_entity"]
    else:
        return entity


fed_entity = {}
combo_entity = {}

for ent, info in ENTITY.items():
    os.chdir(f"{config_folder}/{info['type']}/{ent}")
    _cnf = load_values_from_file(load_config_file("conf.json"))
    _ent = make_federation_combo(**_cnf["entity"])
    if isinstance(_ent, FederationCombo):
        fed_entity[ent] = _ent["federation_entity"]
        combo_entity[ent] = _ent
    else:
        fed_entity[ent] = _ent

subordinates = {}
trust_anchor = {}

for ent, info in ENTITY.items():
    print(f"*** {ent} ***")
    os.chdir(f"{config_folder}/{info['type']}/{ent}")
    if "authority_hints" in info and info["authority_hints"]:
        authorities = []
        for auth in info["authority_hints"]:
            authorities.append(fed_entity[auth].entity_id)
            if auth not in subordinates:
                subordinates[auth] = {}
            _ent_id = get_federation_entity(fed_entity[ent]).entity_id
            _sub_info = {
                "jwks": get_federation_entity(fed_entity[ent]).keyjar.export_jwks(),
                "authority_hints": [fed_entity[auth].entity_id],
            }
            if fed_entity[ent].server.subordinate != {}:
                _sub_info["intermediate"] = True
            if ent in combo_entity:
                _sub_info["entity_type"] = list(combo_entity[ent]._part.keys())
            else:
                _sub_info["entity_type"] = ["federation_entity"]

            subordinates[auth][_ent_id] = _sub_info
        print(f"authority_hints: {authorities}")
        with open("authority_hints.json", "w") as fp:
            fp.write(json.dumps(authorities))
    if "trust_anchors" in info and info["trust_anchors"]:
        trust_anchor[ent] = {}
        for anch in info["trust_anchors"]:
            _fed_entity = get_federation_entity(fed_entity[anch])
            _ent_id = _fed_entity.entity_id
            trust_anchor[ent][_ent_id] = _fed_entity.keyjar.export_jwks()
    if "trust_marks" in info and info["trust_marks"]:
        trust_marks = []
        for issuer_id, tm_id in info["trust_marks"].items():
            os.chdir(f"{config_folder}/tmi/{issuer_id}")
            _fed_entity = get_federation_entity(fed_entity[issuer_id])
            _tm_issuer = combo_entity[issuer_id]
            entity_id = get_federation_entity(fed_entity[ent]).entity_id
            trust_marks.append(_tm_issuer.create_trust_mark(tm_id, entity_id))
        os.chdir(f"{config_folder}/{info['type']}/{ent}")
        with open("trust_marks.json", "w") as fp:
            fp.write(json.dumps(trust_marks))


trust_anchors = {}
for ent, info in trust_anchor.items():
    for k, v in info.items():
        trust_anchors[k] = v

for auth, val in subordinates.items():
    os.chdir(f"{config_folder}/{ENTITY[auth]['type']}/{auth}")
    with open("subordinates.json", "w") as fp:
        fp.write(json.dumps(val))

    print(f"*** subordinates@{auth} ***")
    for sub, info in val.items():
        print(f"--- {sub} ---")
        print(info)

for ent, val in trust_anchor.items():
    os.chdir(f"{config_folder}/{ENTITY[ent]['type']}/{ent}")
    with open("trust_anchors.json", "w") as fp:
        fp.write(json.dumps(val))

    print(f"*** trust_anchors@{ent} ***")
    for sub, info in val.items():
        print(f"--- {sub} ---")
        print(info)
