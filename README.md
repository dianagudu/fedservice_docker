# OIDC federation implementation

[Forked from https://github.com/rohe/fedservice]

## Project structure

- [fedservice](fedservice): Python implementation of OIDC federation
- [app](app): Python (w/ Flask) code to run different federation entities
- [conf](conf): configuration folder for example federation setup

## Federation example

This repo builds a federation which consists of:

- relying parties:
  - [auto](https://auto.fedservice.lh): RP that uses automatic registration
  - [expl](https://expl.fedservice.lh): RP that uses explicit registration
- OIDC providers:
  - [op](https://op.fedservice.lh)
- intermediate entities:
  - [umu](https://umu.fedservice.lh)
  - [lu](https://lu.fedservice.lh)
- trust anchors:
  - [seid](https://seid.fedservice.lh)
  - [swamid](https://swamid.fedservice.lh)

The trust relationships are depicted below:

![Federation Example](FederationExample.jpg "Federation example")

Each entity has a configuration folder in [conf/{entity_type}/{entity_name}](conf).

The entities will run at [https://{entity_name}.fedservice.lh](https://{entity_name}.fedservice.lh).

If you need to change the domain names, replace `fedservice.lh` everywhere where it appears in:

- [conf](conf)
- [docker-compose.yml](docker-compose.yml)
- [traefik](traefik)

Or use the provided script:

```bash
./update-domain.sh $MY_DOMAIN
```

### Initial setup

You will first need to generate jwks keys for each entity and create the trust relationships. To do this, run:

```bash
docker-compose run setup
```

This will add all the necessary keys and configurations in conf.

You can customise anything in the configuration files in conf, if necessary.

### Traefik

Configure and run the traefik reverse proxy. This will allow you to access the federation entities at the domain names mentioned above.

- create a self-signed certificate for the domain name `fedservice.lh` and its sub-domains:

```bash
# If it's the first install of mkcert, run
mkcert -install
mkcert -cert-file traefik/certs/local-cert.pem -key-file traefik/certs/local-key.pem "fedservice.lh" "*.fedservice.lh"
```

- create a docker network for traefik

```bash
docker network create traefik
```

- start the traefik container (this will run in the background)

```bash
docker-compose -f traefik/docker-compose.yml up -d
```

### Run the federation

To start up all the federation entities, run:

```bash
docker-compose up
```

### Testing

All the entities will expose the `/.well-known/openid-federation` endpoint, according to the OIDCfed specification.

You can also display the payload of an entity that has the provided entity id (given by its URL) as follows:

```bash
docker-compose run display https://swamid.fedservice.lh
```

If the entity is an intermediate or trust anchor, that is has subordinates, it will also list the subordinates.

## GEANT T&II setup

We have a testbed federation setup at `fedservice.testbed.oidcfed.incubator.geant.org`:

- relying parties:
  - [auto](https://auto.fedservice.testbed.oidcfed.incubator.geant.org): RP that uses automatic registration
  - [expl](https://expl.fedservice.testbed.oidcfed.incubator.geant.org): RP that uses explicit registration
- OIDC providers:
  - [op](https://op.fedservice.testbed.oidcfed.incubator.geant.org)
- intermediate entities:
  - [umu](https://umu.fedservice.testbed.oidcfed.incubator.geant.org)
  - [lu](https://lu.fedservice.testbed.oidcfed.incubator.geant.org)
- trust anchors:
  - [seid](https://seid.fedservice.testbed.oidcfed.incubator.geant.org)
  - [swamid](https://swamid.fedservice.testbed.oidcfed.incubator.geant.org)

The setup uses Let's Encrypt certificates. The compose file is [here](docker-compose.tii.yml).

You can also display the payload of an entity that has the provided entity id (given by its URL) as follows:

```bash
docker-compose run display https://swamid.fedservice.testbed.oidcfed.incubator.geant.org
```
