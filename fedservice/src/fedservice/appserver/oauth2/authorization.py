import logging
from typing import List
from typing import Optional

from fedservice.entity.utils import get_federation_entity
from idpyoidc.message import oauth2
from idpyoidc.message.oauth2 import OauthClientMetadata
from idpyoidc.node import topmost_unit
from idpyoidc.server.oauth2 import authorization

from fedservice.entity.function import apply_policies
from fedservice.entity.function import collect_trust_chains
from fedservice.entity.function import verify_trust_chains
from fedservice.exception import NoTrustedChains

logger = logging.getLogger(__name__)


class Authorization(authorization.Authorization):
    msg_type = oauth2.AuthorizationRequest
    response_cls = oauth2.AuthorizationResponse
    error_msg = oauth2.ResponseMessage

    _supports = authorization.Authorization._supports.copy()
    _supports.update({
        "request_authentication_signing_alg_values_supported": ["RS256"],
        "request_authentication_methods_supported": {
            "authorization_endpoint": [
                "request_object"
            ],
            "pushed_authorization_request_endpoint": [
                "private_key_jwt",
            ]
        }
    })

    def __init__(self, upstream_get, conf: Optional[dict] = None, **kwargs):
        authorization.Authorization.__init__(self, upstream_get, **kwargs)
        # self.pre_construct.append(self._pre_construct)
        self.post_parse_request.append(self._reset_client_id)
        self.new_client_id = kwargs.get('new_client_id', False)
        self.config = conf or {}

    def _reset_client_id(self, request, client_id, context, **kwargs):
        request['client_id'] = client_id
        return request

    def find_client_keys(self, iss):
        return self.do_automatic_registration(iss, [])

    def do_automatic_registration(self, entity_id: str, provided_trust_chain: List[str]):
        if provided_trust_chain:
            # So I get the TA's entity statement first
            provided_trust_chain.reverse()
            trust_chains = verify_trust_chains(self, [provided_trust_chain])
        else:
            chains, signed_entity_configuration = collect_trust_chains(self, entity_id)
            trust_chains = verify_trust_chains(self, chains, signed_entity_configuration)

        trust_chains = apply_policies(self, trust_chains)

        if not trust_chains:
            raise NoTrustedChains()

        # pick one of the possible
        trust_chain = trust_chains[0]
        _fe = topmost_unit(self)['federation_entity']
        _fe.trust_chain_anchor = trust_chain.anchor

        # handle the registration request as in the non-federation case.
        # If there is a jwks_uri in the metadata import keys
        _jwks_uri = trust_chain.metadata['openid_relying_party'].get('jwks_uri')
        if _jwks_uri:
            _keyjar = self.upstream_get('attribute', 'keyjar')
            _keyjar.add_url(entity_id, _jwks_uri)

        req = OauthClientMetadata(**trust_chain.metadata['openid_relying_party'])
        req['client_id'] = entity_id
        kwargs = {}
        kwargs['new_id'] = self.new_client_id

        op = topmost_unit(self)['openid_relaying_party']
        _registration = op.get_endpoint("registration")
        response_info = _registration.non_fed_process_request(req=req, **kwargs)

        try:
            return response_info["response_args"]["client_id"]
        except KeyError:
            return None

    def client_authentication(self, request, auth=None, **kwargs):
        _cid = request["client_id"]
        _context = self.upstream_get("context")
        # If this is a registered client then this should return some info
        client_info = _context.cdb.get(_cid)
        if client_info is None:
            if 'automatic' in _context.provider_info.get('client_registration_types_supported'):
                # try the federation way
                _trust_chain = request.get('trust_chain', [])
                registered_client_id = self.do_automatic_registration(_cid, _trust_chain)
                if registered_client_id is None:
                    return {
                        'error': 'unauthorized_client',
                        'error_description': 'Unknown client'
                    }
                else:
                    logger.debug('Automatic registration done')
                    if registered_client_id != _cid:
                        request["client_id"] = registered_client_id
                        kwargs["also_known_as"] = {_cid: registered_client_id}
                        client_info = _context.cdb[registered_client_id]
                        _context.cdb[_cid] = client_info
                        client_info['entity_id'] = _cid
                        # _context.cdb[registered_client_id] = client_info
            else:
                return {
                    'error': 'unauthorized_client',
                    'error_description': 'Unknown client'
                }

        # then do client authentication
        return authorization.Authorization.client_authentication(
            self, request, auth, **kwargs)

    def extra_response_args(self, aresp, **kwargs):
        _cid = kwargs.get("client_id")
        if _cid:
            _fe = get_federation_entity(self)
            aresp['trust_anchor_id'] = _fe.get_trust_chain(_cid).anchor
        return aresp
