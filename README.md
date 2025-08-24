# OIDC federation implementation

[Forked from https://github.com/SUNET/fedservice]

## Project structure

- [deps/fedservice](deps/fedservice): Python implementation of OIDC federation
- [app](app): Python (w/ Flask) code to run different federation entities
- [example-conf](example-conf): configuration folder for example federation setup
- [example-rp2](example-rp2): example relying party that uses an external federation

## Federation example

This repo builds a federation which consists of:

- relying parties:
  - [auto](https://auto.localhost): RP that uses automatic registration
  - [expl](https://expl.localhost): RP that uses explicit registration
- OIDC providers:
  - [op](https://op.localhost)
- intermediate entities:
  - [umu](https://umu.localhost)
  - [lu](https://lu.localhost)
- trust anchors:
  - [seid](https://seid.localhost)

The trust relationships are depicted below:

![Federation Example](FederationExample.jpg "Federation example")

### Build Docker Image

The docker image is available on [Docker Hub](https://hub.docker.com/r/ddgu/fedservice/). You can pull it with the following command:

```bash
    docker pull ddgu/fedservice
```

However, if you want to build the docker image yourself, you must first retrieve the latest source code for its dependencies. The script `build.sh` will do this for you, and then build the docker image.

```bash
    ./build.sh
```

This will create a directory called `deps` and clone the following repositories into it:

* [fedservice](https://github.com/rohe/fedservice)
* [idpy-oidc](https://github.com/IdentityPython/idpy-oidc)

It will also apply any necessary patches to the dependencies.

Then it will build the docker image `ddgu/fedservice` and tag it with the current date and time.

### Configure test environment

An example setup is provided in the `example-conf` directory. The `example-conf` directory contains an `entities.json` file and multiple directories, one for each entity type.

The following entity types are supported:

* `op`: openid provider
* `rp`: relying party
* `intermediate`: intermediate entity in a federation
* `ta`: trust anchor

Each entity type directory contains subdirectories, one for each entity, named after the entity and containing the configuration file for that entity, named `config.json`.

The `entities.json` file contains a dictionary of entities, where the key is the entity name and the value is a dictionary containing the following keys:

* `type`: the entity type
* `authority_hints`: a list of authority hints for the entity
* `trust_anchors`: a list of trust anchors for the entity

To configure the test environment, you must run the `configure.sh` script, which will copy the content of `example-conf` to a new folder `conf` and create additional configuration files for each entity, based on the `entities.json` file (such as `authority_hints.json` and `trust_anchors.json`). The script will also create a `caddy` directory, which contains the configuration files for the Caddy web server. A Caddyfile must be present in the `example-conf` directory, which will be copied to the `caddy` directory.

If you are not running the test environment on your local machine, you must also pass the domain name to the `configure.sh` script, and it will first replace the domain name in the configuration files with the domain name of the machine you are running the test environment on.

```bash
Usage: ./configure.sh [-s src_conf] [-d dest_conf] [-n domain_name] [-c caddy_dir]
Defaults: src_conf=example-conf, dest_conf=conf, domain_name=localhost, caddy_dir=caddy
```

#### Test environment with external entities

If you want to use the test environment with external entities, you can use the `example-rp2` directory, which contains an example relying party that uses an external federation. In this case, only the `rp2` entity (an RP with automatic registration) is configured, and it will use existing trust anchors and authority hints to discover the other entities in the federation. These must be up and running, to be able to retrieve their keys.

You can create the configuration folder for this example with the following command:

```bash
./configure.sh -s example-rp2 -d conf-rp2 -n oidf-pilot.edugain.org -c caddy-edugain
```

This will create a new folder `conf-rp2` with the configuration files for the RP, and a new folder `caddy-edugain` with the Caddy configuration files. The domain name `oidf-pilot.edugain.org` will be used in the configuration files. We also provide a docker compose file `docker-compose-rp2.yml` that you can use to run the RP with the external federation.


### Deploy test environment

To deploy the test environment, you only need the `conf` and `caddy` directories, as well as the `docker-compose.yml` file.

```bash
    docker network create caddy
    docker-compose up -d
```

### Testing

All the entities will expose the `/.well-known/openid-federation` endpoint, according to the OIDCfed specification.

You can also display the payload of an entity that has the provided entity id (given by its URL) as follows:

```bash
docker-compose run display https://seid.localhost
```

If the entity is an intermediate or trust anchor, that is has subordinates, it will also list the subordinates.

You can also use the `ofcli` tool without installing it, by running the following command:

```bash
docker-compose run ofcli <command>
```

### Adding trust marks

You can add trust marks to an entity by adding a file named `trust_marks` in the entity's configuration directory. The file must contain a JSON array of objects, where each object contains the following keys:

- `trust_mark`: the trust mark as a JWT
- `trust_mark_type`: the type of the trust mark (a URI)

For example, to add a SIRTFI trust mark to the RP `expl`, create the file `conf/rp/expl/trust_marks` with the following content:

```json
[{"trust_mark": "<JWT>", "trust_mark_type": "https://refeds.org/sirtfi"}]
```

Replace `<JWT>` with the actual trust mark JWT.

Then modify the `conf/rp/expl/conf.json` file to include the `trust_marks` configuration:

```json
"trust_marks": {
  "class": "idpyoidc.storage.jsonfile.JsonArrayFile",
  "kwargs": {
    "file_name": "trust_marks"
  }
}
```

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

The setup uses Let's Encrypt certificates and Docker swarm. The compose file is [here](docker-compose.tii.yml).

You can also display the payload of an entity that has the provided entity id (given by its URL) as follows:

```bash
docker-compose run display https://swamid.fedservice.testbed.oidcfed.incubator.geant.org
```

## Onboarding an entity to an existing federation

As an example, to onboard the OP 'https://op.localhost' to the italian federation (trust anchor 'https://trust-anchor.spid-cie.localhost/'), you need to:

- add the trust anchor to the OP's list of authority hints:

  ```bash
  $ cat conf/op/op/authority_hints.json
  [
    "https://trust-anchor.spid-cie.localhost/",
    "https://umu.localhost"
  ]
  ```

- add the trust anchor to the OP's list of trusted roots, with the corresponding jwks:

  ```bash
  $ cat conf/op/op/trusted_roots.json
  {
    "https://seid.localhost": {
      "keys": [
        ...
      ]
    },
    "https://swamid.localhost": {
      "keys": [
        ...
      ]
    },
    "https://trust-anchor.spid-cie.localhost/": {
      "keys": [
        ...
      ]
    }
  }
  ```

- restart the OP container
  ```bash
  docker-compose restart op
  ```
- onboard the OP to the trust anchor at https://trust-anchor.spid-cie.localhost/onboarding/landing

## Onboarding a new entity in this federation

[!Note] This section might be outdated.

For example, add an RP as a direct subordinate of the trust anchor 'https://swamid.localhost':

- make sure the entity has configured the trust anchor as an authority hint
- OPTIONAL: add `swamid` as trusted root for the RP, with its corresponding jwks
- onboard it by submitting a POST request to the trust anchor's onboarding endpoint:
  ```bash
  curl -d "sub={RP's entity_id}" -X POST https://swamid.localhost/onboarding
  ```

- ALTERNATIVELY, you can do it manually by:
  - adding the entity as a subordinate of the trust anchor by adding a new file in `conf/ta/swamid/subordinates/{urlencoded_entity_id}`: the file should contain the entity's jwks

  ```bash
  $ cat conf/ta/swamid/subordinates/https%3A%2F%2Fgorp.localhost
  {
    "keys": [
      ...
    ]
  }
  ```
  - restarting the trust anchor container

- if you run the setup locally, you might need to add the new entity name to your /etc/hosts file (e.g. `127.0.0.1 gorp.localhost`), as well as an alias in the traefik network, in `traefik/docker-compose.yml`. Then restart the traefik container.

----

This work was started in and supported by the
[Geant Trust & Identity Incubator](https://connect.geant.org/trust-and-identity-incubator).

<img src="https://wiki.geant.org/download/attachments/120500419/incubator_logo.jpg" alt="Trust & Identity Incubator logo" height="75"/>
