#!/usr/bin/env python3
import os
import sys

from cryptojwt.utils import importer
from fedservice.combo import FederationCombo
from flask import Config
from flask.app import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from idpyoidc.client.util import lower_or_upper
from idpyoidc.logging import configure_logging
from idpyoidc.ssl_context import create_context
from idpyoidc.util import load_config_file
from fedservice.appclient import init_oidc_rp_handler
from idpyoidc.configure import Configuration
from idpyoidc.configure import create_from_config_file
from fedservice.configure import FedRPConfiguration

from fedservice.utils import make_federation_combo
from utils import load_values_from_file

dir_path = os.path.dirname(os.path.realpath(__file__))

#template_dir = os.path.join(dir_path, 'templates')


def init_app(config_file, name=None, subdir="", **kwargs) -> Flask:
    name = name or __name__
    _cnf = load_config_file(f"{config_file}")
    _cnf = load_values_from_file(_cnf)

    if "template_dir" in _cnf:
        kwargs["template_folder"] = os.path.join(dir_path, subdir, _cnf["template_dir"])

    app = Flask(name, static_url_path='', **kwargs)
    app.wsgi_app = ProxyFix(app.wsgi_app)
    sys.path.insert(0, dir_path)
    app.config['SECRET_KEY'] = os.urandom(12).hex()

    entity = importer(f"{subdir}.views.entity")
    app.register_blueprint(entity)

    # Initialize the oidc_provider after views to be able to set correct urls
    app.cnf = _cnf
    app.cnf["cwd"] = dir_path
    app.server = make_federation_combo(**app.cnf["entity"])

    # app.srv_config = create_from_config_file(Configuration,
    #                                         entity_conf=[
    #                                             {"class": FedRPConfiguration,
    #                                             "attr": "rp"}],
    #                                         filename=config_file, base_path=dir_path)
    app.rp_config = create_from_config_file(
        Configuration,
        filename=config_file, base_path=dir_path)

    # Initialize the rp after views to be able to set correct urls
    app.rph = init_oidc_rp_handler(app, dir_path)

    return app


if __name__ == "__main__":
    print(sys.argv)
    name = sys.argv[1]
    conf = sys.argv[2]
    subdir = sys.argv[3]
    template_dir = os.path.join(dir_path, 'templates')
    app = init_app(conf, name, subdir=subdir)
    if "logging" in app.cnf:
        configure_logging(config=app.cnf["logging"])
    _web_conf = app.cnf["webserver"]

    print('Listening on {}:{}'.format(_web_conf.get('domain'), _web_conf.get('port')))
    # app.rph.federation_entity.collector.web_cert_path = _cert
    app.run(host=_web_conf.get('domain'), port=_web_conf.get('port'),
            debug=_web_conf.get("debug", False))
