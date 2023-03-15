#!/usr/bin/env python3
import argparse
import json
import os
import sys
import pathlib
from urllib.parse import quote_plus

from fedservice.example_utils import (
    get_federation_config,
    create_and_write_private_and_public_key_sets,
)


def usage():
    print(
        f"Usage: {sys.argv[0]} ENTITY_CONF_DIR -s SUBORDINATE_CONF_DIR [-p POLICY_FILE]"
    )


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
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", dest="policy")
    parser.add_argument("-s", dest="subordinate")
    parser.add_argument(dest="superior")
    args = parser.parse_args(sys.argv[1:])

    if not args.superior or not args.subordinate:
        usage()
        sys.exit(1)

    _policy = None
    if args.policy:
        try:
            _policy = json.loads(open(args.policy, "r").read())
        except:
            print(f"Policy file not found or invalid json: {args.policy}")
            sys.exit(3)

    superior_conf_dir = get_valid_conf(args.superior)
    subordinate_conf_dir = get_valid_conf(args.subordinate)

    subordinate_conf = get_federation_config(
        subordinate_conf_dir, entity_type(subordinate_conf_dir)
    )
    _keyjar = create_and_write_private_and_public_key_sets(
        subordinate_conf_dir, subordinate_conf
    )

    entity_statement = {"jwks": _keyjar.export_jwks()}
    if _policy:
        entity_statement.update(_policy)

    _fname = (
        pathlib.Path(superior_conf_dir)
        / "subordinates"
        / quote_plus(subordinate_conf["entity_id"])
    )
    with open(_fname, "w") as fp:
        fp.write(json.dumps(entity_statement, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
