import json
import logging
import os

from cryptojwt import KeyJar
from cryptojwt.jws.jws import factory
from fedservice.message import EntityStatement


logger = logging.getLogger(__name__)

def _import(val):
    path = val[len("file:"):]
    if os.path.isfile(path) is False:
        logger.info(f"No such file: {path}")
        return None

    with open(path, "r") as fp:
        _dat = fp.read()
        if val.endswith('.json'):
            return json.loads(_dat)
        elif val.endswith(".py"):
            return _dat

    raise ValueError("Unknown file type")


def load_values_from_file(config):
    res = {}
    for key, val in config.items():
        if isinstance(val, str) and val.startswith("file:"):
            res[key] = _import(val)
        elif isinstance(val, dict):
            res[key] = load_values_from_file(val)
        elif isinstance(val, list):
            _list = []
            for v in val:
                if isinstance(v, dict):
                    _list.append(load_values_from_file(v))
                elif isinstance(val, str) and val.startswith("file:"):
                    res[key] = _import(val)
                else:
                    _list.append(v)
            res[key] = _list

    for k, v in res.items():
        config[k] = v

    return config


def get_entity_jwks(entity_id):
    import requests

    try:
        _response = requests.get(entity_id + "/.well-known/openid-federation")
        _response.raise_for_status()
        _jws = factory(_response.text)
        return _jws.jwt.payload().get('jwks', None)
    except requests.RequestException as e:
        logger.error(f"Failed to fetch JWKS from {entity_id}: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON from {entity_id}: {e}")
        return None