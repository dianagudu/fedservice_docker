#!/usr/bin/env python3
import json
import pathlib
import sys

from fedservice.example_utils import get_federation_config
from fedservice.example_utils import create_and_write_private_and_public_key_sets


def usage():
    print(f"Usage: {sys.argv[0]} ENTITY_CONF_DIR TRUST_ANCHOR_CONFIG_DIR(S) ...")


def get_valid_conf(conf_dir: str):
    path = pathlib.Path(conf_dir)
    if not path.exists() or not path.is_dir():
        print(f"Invalid entity configuration folder: {path}")
        exit(2)
    return str(path)


def entity_type(conf_dir: str):
    parent_dir = str(pathlib.Path(conf_dir).parent.name).lower()
    if parent_dir in ["rp", "op", "ta", "intermediate"]:
        return parent_dir
    print(f"Unknown entity type: {parent_dir}")
    exit(3)


def main():
    if len(sys.argv) < 3:
        usage()
        sys.exit(1)
    target_conf_dir = get_valid_conf(sys.argv[1])
    anchors_conf_dir = [get_valid_conf(ta) for ta in sys.argv[2:]]

    target_conf = get_federation_config(target_conf_dir, entity_type(target_conf_dir))
    print(target_conf, entity_type(target_conf_dir))

    _anchor = {}
    for acd in anchors_conf_dir:
        anchor_conf = get_federation_config(acd, entity_type(acd))
        print(anchor_conf)
        _keyjar = create_and_write_private_and_public_key_sets(acd, anchor_conf)
        _entity_id = anchor_conf["entity_id"]
        _anchor[_entity_id] = _keyjar.export_jwks()

    _fname = pathlib.Path(target_conf_dir) / target_conf["trusted_roots"]
    with open(_fname, "w") as fp:
        fp.write(json.dumps(_anchor, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
