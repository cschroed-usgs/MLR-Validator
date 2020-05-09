# MLR-Validator

Validates inserts and updates to the MLR system
[![Build Status](https://travis-ci.org/USGS-CIDA/MLR-Validator.svg?branch=master)](https://travis-ci.org/USGS-CIDA/MLR-Validator)
[![Coverage Status](https://coveralls.io/repos/github/USGS-CIDA/MLR-Validator/badge.svg)](https://coveralls.io/github/USGS-CIDA/MLR-Validator)

## Service Description

This service is part of the MLR microservices and is responsible for performing single-location validation for location adds or updates. Locations being added/updated in MLR from DDOt files have many validations that they must pass before they can be persisted in the database and this service is responsible for performing those validations. The only validations outside the scope of this service are those that require making queries against the MLR Database which are the location uniqueness validations. These validations are run by the Legacy CRU service. The rule of thumb we have used for splitting the validations is that this service, the MLR Validator, is responsible for validating the components of a single lcoation including parameter values, ranges, reference list links, and others. If a location is successfully validated by this service it could be added to the MLR Database assuming there was no data currently in the database. Validations that are relative to the current contents of the MLR Database are handled by the Legacy CRU service because this service has no direct connection to the MLR Database to perform those validations.

The MLR Validator is designed in such a way that if one validation fails the process will still continue and run all validations against the submitted location. This decision was made because users would prefer to know about _all_ of the issues in their file at once rather than having to resubmit and fix the file multiple times if only a single error was shown per-run.

There are two different endpoints to execute validation of a single location JSON file: `/validators/add` and `/validators/update`. Add and update transactions share many validations, however there are some validations that are run in only one case or the other (such as transition validations, described below). As a result, we use two different endpoints for validation. While the DDot file itself contains the transaction type of each transaction being performed (add or update), the monitoring location data itself within each transaction does _not_. This is why we cannot have the validator service itself decide whether the input location is for an add or update, and instead this must be provided as part of the request by hitting one of the two API endpoints. Specifics about each API endpoint (such as the request and response formats) can be read from the service Swagger API documentation.

The MLR Validator runs several different kinds of validations including single-field and cross-field validations.

Single-field validations are those that are checking the value of a single field of the location for validity. These validations do not depend on the values of any other fields of the location and only look at the value of a single field at a time. Validations in this category include acceptable value ranges, reference list checks (to ensure a value appears on a reference list), null/empty checks, and other related things.

Cross-field validations are those that check the value of multiple fields of a location in conjunction to determine validity. These validations do depend on the value of multiple fields of the location and can include more complicated branching logic for various different situations. Validations in this category include checking for the existence of certain fields when other fields have a specific value (such as a ensuring a location has primary and secondary use codes defined when it has a tertiary use code defined), checking value ranges for one field when another field has a certain value (such as ensuring the provided latitude and longitude coordinates are within the provdided state), and other related things.

In addition to these two primary kinds of validations, there are multiple validation _types_ as well including Error and Warning validations.

Error validations are those that _must_ pass for the location to be considered valid and allowed to be persisted within the MLR Database. If an error validation fails the location being validated _cannot_ be persisted into the database and must be modified by the submitting user.

Warning validations are those that are _not_ required to pass for the location to be considered valid. If a location fails several warning validations the user is notified of these failures but the location is still allowed to be persisted into the MLR Database.

Several other types of validations exist such as Transition validations which are run only during location updates and check that when certain fields are being _changed_ from one value to another value they follow certain rules and guidelines.

## Building and Running

This project has been built and tested with python 3.6.x. To build the project locally you will need
python 3 and virtualenv installed.

```bash
% virtualenv --python=python3 env
% env/bin/pip install -r requirements.txt
```

### Reference Lists

In order to run the app or the tests, external reference list files must be placed in the `mlrvalidator/references/remote` directory.
If you have the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html) and [saml2aws](https://github.com/Versent/saml2aws) installed, run this from the repo root to get started:

```bash
aws s3 sync s3://prod-owi-resources/resources/Application/mlr/test/configuration/mlr-validator/remote-references/ ./mlrvalidator/references/remote
```

### Testing

After you have installed reference lists, you can run the tests:

```bash
env/bin/python -m unittest
```

### Running

After you have installed reference lists, you can run the application locally:

```bash
% env/bin/python app.py
```

The swagger documentation can then be accessed at <http://127.0.0.1:5000/api> (when running locally using the above command).

## Configuration

Configuration is read from `config.py`. `config.py` tries to read most values from environment variables and provides defaults if they do not exist. A user running this app can customize config values by defining environment variables referenced in `config.py`.

Configuration is also read from an optional `.env` Python file. Any python variable defined in `.env` overrides values set in `config.py` For instance, though `DEBUG = False` in `config.py`, you can turn debug on by creating a `.env` file with the following:

```python
DEBUG = True
```

For local development, you will need to provide a JWT token to the service. This can be done through the Swagger
documents by clicking the Authorize button and entering 'Bearer your.jwt.token'.

You can use a valid JWT token generated by another service. You will need to set it's JWT_PUBLIC_KEY to the public
key used to generate the token, as well as the JWT_DECODE_AUDIENCE (if any) and the JWT_ALGORITHM
(if different than RS256). If you don't want to verify the cert on this service, set AUTH_CERT_PATH to False.

Alternatively, you can generate your own token by using the python package jwt. In the python interpreter, do the following

```python
import jwt
jwt.encode({'authorities': ['one_role', 'two_role']}, 'secret', algorithm='HS256')
```

The output of this command will be the token that you can use. You will need to set JWT_SECRET_KEY to 'secret' in
your local .env file. See <http://flask-jwt-simple.readthedocs.io/en/latest/options.html> for the other options that
you can use.

## Running with Docker

This application can also be run locally using the docker container built during the build process, though this does not allow the application to be run in debug mode. The included `docker-compose` file has 2 profiles to choose from when running the application locally:

1. mlr-validator: This is the default profile which runs the application as it would be in our cloud environment. This is not recommended for local development as it makes configuring connections to other services running locally on your machine more difficult.

2. mlr-validator-local-dev: This is the profile which runs the application as it would be in the mlr-local-dev project, and is configured to make it easy to replace the mlr-validator instance in the local-dev project with this instance. It is run the same as the `mlr-validator` profile, except it uses the docker host network driver.

### Setting up SSL

This application is configured to run over HTTPS and thus requires SSL certificates to be setup before it can be run via Docker. When running this container alone and not with an MLR Local Dev setup SSL certificates can be configured easily by simply running the included `create_keys.sh` script in the `docker/certificates` directory.

When intending to run this application alongside other MLR service running from the MLR Local Dev project you should use the certificate files generated by the MLR Local Dev project. This is important because in order for the MLR Local Dev services to connect to this service they must trust the certificate it is serving, which is most easily accomplished locally by using the same certificate for SSL among all of the MLR services.

In addition to its own SSL certs, this service must also be able to connect to a running Water Auth server locally, and thus must trust the SSL certificate being served by Water Auth. This can be accomplished by copy-pasting the .crt file that Water Auth is serving into the `docker/certificates/import_certs` folder of this project. Any .crt file put into the `import_certs` directory will be loaded into the certificate store used by Python within the container and trusted by the application.

When using MLR Local Dev this means copying the certificates that MLR Local Dev generates into 2 places in this project:

1. `docker/certificates` to be used as the SSL certs served by this service

2. `docker/certificates/import_certs` to have this service trust other services serving the MLR Local Dev SSL certs

### Building Changes

To build and run the application after completing the above steps you can run: `docker-compose up --build {profile}`, replacing `{profile}` with one of the options listed above.

The swagger documentation can then be accessed at <http://127.0.0.1:6027/api>

## Connecting with mlr-local-dev when running mlr-validator _outside_ of docker

You can run the MLR-Validator locally alongside the [mlr-local-dev](https://github.com/USGS-CIDA/mlr-local-dev) project which runs the other MLR application services in Docker. This gives you the option of debugging the Validator through the MLR UI rather than through Swagger. There are small config changes as well as needing to run the Validator with https.

Use the instructions on mlr-local-dev to get it running with two differences:

Modify the path to the Validator that the [mlr-gateway](https://github.com/USGS-CIDA/mlr-local-dev/blob/master/docker-reference/configuration/mlr-gateway/config.env#L10) configuration has, to point at the non-Docker Validator service instead.

```yaml
mlrgateway_legacyValidatorServers=https://localhost:5000
```

When starting the services in Terminal 3, remove the `mlr-validator` from the `docker-compose up` command suggested in the [Running](https://github.com/USGS-CIDA/mlr-local-dev#running) section

Then in the `.env` file you created, add:

```python
SERVICE_CERT_PATH="/home/user/mlr/mlr-local-dev/ssl/wildcard.crt"
SERVICE_CERT_KEY="/home/user/mlr/mlr-local-dev/ssl/wildcard.key"
```

**To run the Validator with the cert and public key from mlr-local-dev:**

In the Validator's `app.py` file, modify the last few lines to include pulling the cert path and cert key from mlr-local-dev into new strings we'll use to run the Flask app securely:

```python
if __name__ == '__main__':
    cert = application.config['SERVICE_CERT_PATH']
    key = application.config['SERVICE_CERT_KEY']
    application.run(ssl_context=(cert, key))
```

When you start debugging, it should now run securely at <https://127.0.0.1:5000/api> and debugging through the MLR UI is now possible.
