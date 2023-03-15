# OIDC federation implementation

[Forked from https://github.com/rohe/fedservice]

## Project structure

- [fedservice](fedservice): Python implementation of OIDC federation
- [app](app): Python (w/ Flask) code to run different federation entities
- [conf](conf): configuration folder for example federation setup

## Federation example

This repo builds a federation which consists of:

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

The trust relationships are depicted below:

![Federation Example](FederationExample.jpg "Federation example")

Each entity has a configuration folder in [conf/{entity_type}/{entity_name}](conf).

The entities will run at [https://{entity_name}.fedservice.testbed.oidcfed.incubator.geant.org](https://{entity_name}.fedservice.testbed.oidcfed.incubator.geant.org).

If you need to change the domain names, replace `fedservice.testbed.oidcfed.incubator.geant.org` everywhere where it appears in [conf](conf) and [docker-compose.yml](docker-compose.yml).

### Initial setup

You will first need to generate keys for each entity and create the trust relationships. To do this, run:

```bash
docker-compose run setup
```

This will add all the necessary keys and configurations in conf.

You can customise anything in the configuration files in conf, if necessary.

### Run the federation

To start up all the federation entities, run:

```bash
docker-compose up
```

### Testing

All the entities will expose the `/.well-known/openid-federation` endpoint, according to the OIDCfed specification.

You can also display the payload of an entity that has the provided entity id (given by its URL) as follows:

```bash
docker-compose run display https://swamid.fedservice.testbed.oidcfed.incubator.geant.org
```

If the entity is an intermediate or trust anchor, that is has subordinates, it will also list the subordinates.
