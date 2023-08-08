from typing import Optional
from typing import Union
import requests

from cryptojwt import JWT
from cryptojwt import KeyJar
from cryptojwt.jws.jws import factory

from oidcmsg import oidc
from oidcmsg.message import Message
from oidcop.endpoint import Endpoint
from oidcop.endpoint_context import init_service

from fedservice.exception import FedServiceError
from fedservice.entity_statement.collect import (
    construct_well_known_url,
    unverified_entity_statement,
)


class OnBoarding(Endpoint):
    request_cls = oidc.Message
    # response_cls = EntityIDList
    response_format = "json"
    name = "onboarding"

    def __init__(self, server_get, **kwargs):
        Endpoint.__init__(self, server_get, **kwargs)
        # self.post_construct.append(self.create_entity_statement)
        self.metadata_api = None
        _subs = kwargs["subordinates"]

        if "class" in _subs and "kwargs" in _subs:
            self.server_get("context").subordinates = init_service(_subs)
        else:
            self.server_get("context").subordinates = _subs

    def process_request(self, request=None, **kwargs):
        _context = self.server_get("context")
        _db = _context.subordinates
        _sub = request.get("sub", None)
        if not _sub:
            raise FedServiceError("Missing entity ID (sub) to onboard as subordinate")
        if _sub == _context.entity_id:
            raise FedServiceError("Cannot onboard as subordinate to self")
        if _sub in list(_db.keys()):
            raise FedServiceError("Entity ID (sub) already onboarded")
        # get the subordinate's entity statement
        _url = construct_well_known_url(_sub, "openid-federation")
        _resp = requests.request("GET", _url)
        if _resp.status_code != 200:
            raise FedServiceError("Could not fetch entity statement from subordinate")
        # get the entity statement for keys
        payload = unverified_entity_statement(_resp.text)
        # check if this entity appears as authority hint in entity configuration
        if _context.entity_id not in payload.get("authority_hints", []):
            raise FedServiceError(
                f"Entity {_context.entity_id} needs to appear as authority_hint for {_sub} to allow onboarding"
            )
        # add subordinate
        _db[_sub] = {"jwks": payload["jwks"]}

        return {"response_args": payload["jwks"]}

    def response_info(
        self,
        response_args: Optional[dict] = None,
        request: Optional[Union[Message, dict]] = None,
        **kwargs,
    ) -> dict:
        return response_args
