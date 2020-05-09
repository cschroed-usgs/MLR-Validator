FROM python:3.6-alpine as build

ENV PIP_CERT=/etc/ssl/certs/ca-certificates.crt

# Add build dependencies (See: https://github.com/gliderlabs/docker-alpine/issues/458)
RUN apk add -U --no-cache gcc build-base linux-headers ca-certificates python3-dev libffi-dev openssl-dev py3-virtualenv

RUN if getent ahosts "sslhelp.doi.net" > /dev/null 2>&1; then \
                wget 'https://s3-us-west-2.amazonaws.com/prod-owi-resources/resources/InstallFiles/SSL/DOIRootCA.cer' -O /usr/local/share/ca-certificates/DOIRootCA2.crt && \
                update-ca-certificates; \
        fi

COPY --chown=1000:1000 requirements.txt /build/requirements.txt

WORKDIR /build

RUN virtualenv --python=python3.6 env
RUN env/bin/pip install -r requirements.txt && env/bin/pip install wheel

COPY --chown=1000:1000 README.md /build/README.md
COPY --chown=1000:1000 MANIFEST.in /build/MANIFEST.in
COPY --chown=1000:1000 *.py /build/
COPY --chown=1000:1000 mlrvalidator /build/mlrvalidator
COPY --chown=1000:1000 json_population_scripts /build/json_population_scripts

RUN env/bin/python -m unittest

# After unit tests complete successfully, remove remote reference lists
# The user will need to mount those files at runtime
RUN rm -rf mlrvalidator/references/remote/*

RUN env/bin/python setup.py bdist_wheel

FROM artifactory.wma.chs.usgs.gov/wma-docker/mlr/mlr-python-base-docker:latest
LABEL maintainer="gs-w_eto_eb_federal_employees@usgs.gov"

ENV listening_port=6027
ENV protocol=https
ENV oauth_server_jwks_url=https://test.gov/oauth/jwks.json
ENV authorized_roles=test_default
ENV artifact_id=usgs-wma-mlr-validator

COPY --chown=1000:1000 --from=build /build/dist/*.whl .

RUN unzip *.whl

HEALTHCHECK CMD curl -k ${protocol}://127.0.0.1:${listening_port}/version | grep -q "\"artifact\": \"${artifact_id}\"" || exit 1
