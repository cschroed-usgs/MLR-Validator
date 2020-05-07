import os
import requests
import json

from flask import Flask
from jwt.algorithms import RSAAlgorithm

application = Flask(__name__)

application.config.from_object('config')

PROJECT_DIR = os.path.dirname(__file__)
if os.path.exists(os.path.join(PROJECT_DIR, '.env')):
    application.config.from_pyfile('.env')

if application.config.get('AUTH_JWKS_URL'):
    # Retrieve data from jwks_uri endpoint
    jwkSet = requests.get(application.config.get('AUTH_JWKS_URL'), verify=application.config['AUTH_CERT_PATH'])
    # Retrieve first RS256 jwk entry from response and use it to construct the RSA public key
    for index, jwk in enumerate(jwkSet.json()['keys']):
        if jwk['alg'] == 'RS256':
            application.config['JWT_PUBLIC_KEY'] = RSAAlgorithm.from_jwk(json.dumps(jwk))
            application.config['JWT_ALGORITHM'] = 'RS256'
            break
elif application.config.get('AUTH_TOKEN_KEY_URL'):
    resp = requests.get(application.config.get('AUTH_TOKEN_KEY_URL'), verify=application.config['AUTH_CERT_PATH'])
    application.config['JWT_PUBLIC_KEY'] = resp.json()['value']
    application.config['JWT_ALGORITHM'] = 'RS256'




from mlrvalidator.services import *

if __name__ == '__main__':
    application.run()