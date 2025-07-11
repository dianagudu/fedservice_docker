#!/usr/bin/env python3
import json
import sys
import os

from idpyoidc.storage.abfile import AbstractFileSystem
from idpyoidc.util import load_config_file

from fedservice.combo import FederationCombo
from fedservice.utils import make_federation_combo
from utils import load_values_from_file, get_entity_jwks


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
            if auth not in fed_entity:
                print(f"Authority {auth} not found, assuming not a fedservice entity but rather given by entity ID...")
                authorities.append(auth)
            else:
                # otherwise it is a fedservice entity, get the entity ID and add current entity as subordinate
                authorities.append(fed_entity[auth].entity_id)
                if auth not in subordinates:
                    subordinates[auth] = {}
                _ent_id = get_federation_entity(fed_entity[ent]).entity_id
                _sub_info = {
                    "jwks": get_federation_entity(fed_entity[ent]).keyjar.export_jwks(),
                }
                if fed_entity[ent].server.subordinate != {}:
                    _sub_info["intermediate"] = True
                if ent in combo_entity:
                    _sub_info["entity_types"] = list(combo_entity[ent]._part.keys())
                else:
                    _sub_info["entity_types"] = ["federation_entity"]
                subordinates[auth][_ent_id] = _sub_info
        # write authority hints to a file
        print(f"authority_hints: {authorities}")
        with open("authority_hints", "w") as fp:
            for auth in authorities:
                fp.write(f"{auth}\n")
    if "trust_anchors" in info and info["trust_anchors"]:
        trust_anchor[ent] = {}
        for anch in info["trust_anchors"]:
            if anch not in fed_entity:
                print(f"Trust anchor {anch} not found, assuming not a fedservice entity but rather given by entity ID...")
                # get keys from the well-known URL of anch
                trust_anchor[ent][anch] = get_entity_jwks(anch)
            else:
                # otherwise it is a fedservice entity, get the entity ID and add current entity as trust anchor
                _fed_entity = get_federation_entity(fed_entity[anch])
                _ent_id = _fed_entity.entity_id
                trust_anchor[ent][_ent_id] = _fed_entity.keyjar.export_jwks()


trust_anchors = {}
for ent, info in trust_anchor.items():
    for k, v in info.items():
        trust_anchors[k] = v

for auth, val in subordinates.items():
    os.chdir(f"{config_folder}/{ENTITY[auth]['type']}/{auth}")
    sub_dict = AbstractFileSystem(
        fdir="subordinates",
        key_conv="idpyoidc.util.Base64",
        value_conv="idpyoidc.util.JSON",
    )
    for k, v in val.items():
        sub_dict[k] = v

    print(f"*** subordinates@{auth} ***")
    for sub, info in val.items():
        print(f"--- {sub} ---")
        print(info)

for ent, val in trust_anchor.items():
    os.chdir(f"{config_folder}/{ENTITY[ent]['type']}/{ent}")
    ta_dict = AbstractFileSystem(
        fdir="trust_anchors",
        key_conv="idpyoidc.util.Base64",
        value_conv="idpyoidc.util.JSON",
    )
    for k, v in val.items():
        ta_dict[k] = v

    print(f"*** trust_anchors@{ent} ***")
    for sub, info in val.items():
        print(f"--- {sub} ---")
        print(info)
