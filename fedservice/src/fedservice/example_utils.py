#!/usr/bin/env python3
import json
import os
from typing import Dict, Optional, List
from pathlib import Path

from cryptojwt.key_jar import init_key_jar
from oidcmsg.configure import create_from_config_file
from oidcmsg.configure import Base
from oidcmsg.configure import lower_or_upper


class Configuration(Base):
    """Entity Configuration Base"""

    uris = ["redirect_uris", "issuer", "base_url", "server_name", "entity_id"]

    def __init__(
        self,
        conf: Dict,
        base_path: str = "",
        entity_conf: Optional[List[dict]] = None,
        file_attributes: Optional[List[str]] = None,
        domain: Optional[str] = "",
        port: Optional[int] = 0,
        dir_attributes: Optional[List[str]] = None,
    ):
        Base.__init__(
            self,
            conf,
            base_path=base_path,
            file_attributes=file_attributes,
            dir_attributes=dir_attributes,
            domain=domain,
            port=port,
        )

        self.web_conf = lower_or_upper(self.conf, "webserver")

        if entity_conf:
            self.extend(
                conf=self.conf,
                base_path=base_path,
                domain=self.domain,
                port=self.port,
                entity_conf=entity_conf,
                file_attributes=self._file_attributes,
                dir_attributes=self._dir_attributes,
            )


def get_federation_config(conf_dir: str, entity_type: str):
    _conf_file = Path(conf_dir) / "conf.json"
    if not _conf_file.exists():
        _conf_file = Path(conf_dir) / "merged_conf.json"
        if _conf_file.exists():
            raise Exception(f"No config file found in {conf_dir}")

    _config = create_from_config_file(Configuration, filename=str(_conf_file))

    if entity_type == "op":
        return _config["conf"]["op"]["server_info"]["federation"]
    else:
        return _config["conf"]["federation"]


def create_and_write_private_and_public_key_sets(conf_dir: str, config: Configuration):
    _key_conf = config["keys"].copy()
    _key_conf["public_path"] = os.path.join(conf_dir, _key_conf["public_path"])
    _key_conf["private_path"] = os.path.join(conf_dir, _key_conf["private_path"])
    _keyjar = init_key_jar(**_key_conf)

    return _keyjar
