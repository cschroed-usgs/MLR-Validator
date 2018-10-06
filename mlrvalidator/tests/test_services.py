import json
from unittest import TestCase, mock

import jwt

import app

@mock.patch('mlrvalidator.services.warning_validator')
@mock.patch('mlrvalidator.services.error_validator')
class AddValidateTransactionTestCase(TestCase):

    def setUp(self):
        app.application.config['JWT_SECRET_KEY'] = 'secret'
        app.application.config['JWT_PUBLIC_KEY'] = None
        app.application.config['JWT_ALGORITHM'] = 'HS256'
        app.application.config['AUTH_TOKEN_KEY_URL'] = ''
        app.application.config['JWT_DECODE_AUDIENCE'] = None
        app.application.testing = True
        self.app_client = app.application.test_client()
        self.location = {
            "ddotLocation" : {
                "agencyCode": "USGS ",
                "siteNumber": "123456789012345",
                "stationName": "This station name "
            },
            "existingLocation" : {}
        }


    def test_valid_transaction(self, merror_validator, mwarning_validator):
        good_token = jwt.encode({'authorities': ['one_role', 'two_role']}, 'secret')
        merror_validator.validate.return_value = True
        merror_validator.errors = {}
        mwarning_validator.validate.return_value = True
        mwarning_validator.warnings = {}

        response = self.app_client.post('/validators/add',
                                        content_type='application/json',
                                        headers={'Authorization': 'Bearer {0}'.format(good_token.decode('utf-8'))},
                                        data=json.dumps(self.location))
        self.assertEqual(response.status_code, 200)
        merror_validator.validate.assert_called_with(self.location.get('ddotLocation'), {})
        mwarning_validator.validate.assert_called_with(self.location.get('ddotLocation'), {})
        resp_data = json.loads(response.data)
        self.assertEqual(len(resp_data), 1)
        self.assertEqual({'validation_passed_message': 'Validations Passed'}, resp_data)

    def test_transaction_with_error(self, merror_validator, mwarning_validator):
        good_token = jwt.encode({'authorities': ['one_role', 'two_role']}, 'secret')
        merror_validator.validate.return_value = False
        merror_validator.errors = {'stationName': ['Invalid value']}
        mwarning_validator.validate.return_value = True
        mwarning_validator.warnings = {}

        response = self.app_client.post('/validators/add',
                                        content_type='application/json',
                                        headers={'Authorization': 'Bearer {0}'.format(good_token.decode('utf-8'))},
                                        data=json.dumps(self.location))
        self.assertEqual(response.status_code, 200)
        resp_data = json.loads(response.data)
        self.assertEqual(len(resp_data), 1)
        self.assertIn('fatal_error_message', resp_data)


    def test_transaction_with_warning(self, merror_validator, mwarning_validator):
        good_token = jwt.encode({'authorities': ['one_role', 'two_role']}, 'secret')
        merror_validator.validate.return_value = True
        merror_validator.errors = {}
        mwarning_validator.validate.return_value = False
        mwarning_validator.warnings = {'stationName': ['Contains quotes']}

        response = self.app_client.post('/validators/add',
                                        content_type='application/json',
                                        headers={'Authorization': 'Bearer {0}'.format(good_token.decode('utf-8'))},
                                        data=json.dumps(self.location))
        self.assertEqual(response.status_code, 200)
        resp_data = json.loads(response.data)
        self.assertEqual(len(resp_data), 1)
        self.assertIn('warning_message', resp_data)

    def test_transaction_with_error_and_warning(self, merror_validator, mwarning_validator):
        good_token = jwt.encode({'authorities': ['one_role', 'two_role']}, 'secret')
        merror_validator.validate.return_value = False
        merror_validator.errors = {'agencyCode': ['Bad value']}
        mwarning_validator.validate.return_value = False
        mwarning_validator.warnings = {'stationName': ['Contains quotes']}

        response = self.app_client.post('/validators/add',
                                        content_type='application/json',
                                        headers={'Authorization': 'Bearer {0}'.format(good_token.decode('utf-8'))},
                                        data=json.dumps(self.location))
        self.assertEqual(response.status_code, 200)
        resp_data = json.loads(response.data)
        self.assertEqual(len(resp_data), 2)
        self.assertIn('warning_message', resp_data)
        self.assertIn('fatal_error_message', resp_data)

    def test_transaction_with_missing_keys(self, merror_validator, mwarning_validator):
        good_token = jwt.encode({'authorities': ['one_role', 'two_role']}, 'secret')
        response = self.app_client.post('/validators/add',
                                        content_type='application/json',
                                        headers={'Authorization': 'Bearer {0}'.format(good_token.decode('utf-8'))},
                                        data=json.dumps({'ddotLocation': {}})
                                        )
        self.assertEqual(response.status_code, 400)

        response = self.app_client.post('/validators/add',
                                        content_type='application/json',
                                        headers={'Authorization': 'Bearer {0}'.format(good_token.decode('utf-8'))},
                                        data=json.dumps({'existingLocation': {}})
                                        )
        self.assertEqual(response.status_code, 400)

    def test_no_auth_header(self, merror_validator, mwarning_validator):
        response = self.app_client.post('/validators/add',
                                        content_type='application/json',
                                        data=json.dumps({'ddotLocation': {}})
                                        )
        self.assertEqual(response.status_code, 401)

    def test_bad_token(self, merror_validator, mwarning_validator):
        bad_token = jwt.encode({'authorities': ['one_role', 'two_role']}, 'bad_secret')
        response = self.app_client.post('/validators/add',
                                        content_type='application/json',
                                        headers={'Authorization': 'Bearer {0}'.format(bad_token.decode('utf-8'))},
                                        data=json.dumps({'ddotLocation': {}})
                                        )
        self.assertEqual(response.status_code, 422)


@mock.patch('mlrvalidator.services.warning_validator')
@mock.patch('mlrvalidator.services.error_validator')
class UpdateValidateTransactionTestCase(TestCase):

    def setUp(self):
        app.application.config['JWT_SECRET_KEY'] = 'secret'
        app.application.config['JWT_PUBLIC_KEY'] = None
        app.application.config['JWT_ALGORITHM'] = 'HS256'
        app.application.config['AUTH_TOKEN_KEY_URL'] = ''
        app.application.config['JWT_DECODE_AUDIENCE'] = None
        app.application.testing = True
        self.app_client = app.application.test_client()
        self.location = {
            "ddotLocation" : {
                "agencyCode": "USGS ",
                "siteNumber": "123456789012345",
                "stationName": "This station name "
            },
            "existingLocation" : {
                'agencyCode': 'USGS ',
                'siteNumber': '123456789012345',
                'stationName': 'New station name'
            }
        }


    def test_valid_transaction(self, merror_validator, mwarning_validator):
        good_token = jwt.encode({'authorities': ['one_role', 'two_role']}, 'secret')
        merror_validator.validate.return_value = True
        merror_validator.errors = {}
        mwarning_validator.validate.return_value = True
        mwarning_validator.warnings = {}

        response = self.app_client.post('/validators/update',
                                        content_type='application/json',
                                        headers={'Authorization': 'Bearer {0}'.format(good_token.decode('utf-8'))},
                                        data=json.dumps(self.location))
        self.assertEqual(response.status_code, 200)
        merror_validator.validate.assert_called_with(self.location.get('ddotLocation'), self.location.get('existingLocation'))
        mwarning_validator.validate.assert_called_with(self.location.get('ddotLocation'), self.location.get('existingLocation'))
        resp_data = json.loads(response.data)
        self.assertEqual(len(resp_data), 1)
        self.assertEqual({'validation_passed_message': 'Validations Passed'}, resp_data)

    def test_transaction_with_error(self, merror_validator, mwarning_validator):
        good_token = jwt.encode({'authorities': ['one_role', 'two_role']}, 'secret')
        merror_validator.validate.return_value = False
        merror_validator.errors = {'stationName': ['Invalid value']}
        mwarning_validator.validate.return_value = True
        mwarning_validator.warnings = {}

        response = self.app_client.post('/validators/update',
                                        content_type='application/json',
                                        headers={'Authorization': 'Bearer {0}'.format(good_token.decode('utf-8'))},
                                        data=json.dumps(self.location))
        self.assertEqual(response.status_code, 200)
        resp_data = json.loads(response.data)
        self.assertEqual(len(resp_data), 1)
        self.assertIn('fatal_error_message', resp_data)


    def test_transaction_with_warning(self, merror_validator, mwarning_validator):
        good_token = jwt.encode({'authorities': ['one_role', 'two_role']}, 'secret')
        merror_validator.validate.return_value = True
        merror_validator.errors = {}
        mwarning_validator.validate.return_value = False
        mwarning_validator.warnings = {'stationName': ['Contains quotes']}

        response = self.app_client.post('/validators/update',
                                        content_type='application/json',
                                        headers={'Authorization': 'Bearer {0}'.format(good_token.decode('utf-8'))},
                                        data=json.dumps(self.location))
        self.assertEqual(response.status_code, 200)
        resp_data = json.loads(response.data)
        self.assertEqual(len(resp_data), 1)
        self.assertIn('warning_message', resp_data)

    def test_transaction_with_error_and_warning(self, merror_validator, mwarning_validator):
        good_token = jwt.encode({'authorities': ['one_role', 'two_role']}, 'secret')
        merror_validator.validate.return_value = False
        merror_validator.errors = {'agencyCode': ['Bad value']}
        mwarning_validator.validate.return_value = False
        mwarning_validator.warnings = {'stationName': ['Contains quotes']}

        response = self.app_client.post('/validators/update',
                                        content_type='application/json',
                                        headers={'Authorization': 'Bearer {0}'.format(good_token.decode('utf-8'))},
                                        data=json.dumps(self.location))
        self.assertEqual(response.status_code, 200)
        resp_data = json.loads(response.data)
        self.assertEqual(len(resp_data), 2)
        self.assertIn('warning_message', resp_data)
        self.assertIn('fatal_error_message', resp_data)

    def test_transaction_with_missing_keys(self, merror_validator, mwarning_validator):
        good_token = jwt.encode({'authorities': ['one_role', 'two_role']}, 'secret')
        response = self.app_client.post('/validators/update',
                                        content_type='application/json',
                                        headers={'Authorization': 'Bearer {0}'.format(good_token.decode('utf-8'))},
                                        data=json.dumps({'ddotLocation': {}})
                                        )
        self.assertEqual(response.status_code, 400)

        response = self.app_client.post('/validators/add',
                                        content_type='application/json',
                                        headers={'Authorization': 'Bearer {0}'.format(good_token.decode('utf-8'))},
                                        data=json.dumps({'existingLocation': {}})
                                        )
        self.assertEqual(response.status_code, 400)

    def test_no_auth_header(self, merror_validator, mwarning_validator):
        response = self.app_client.post('/validators/update',
                                        content_type='application/json',
                                        data=json.dumps({'ddotLocation': {}})
                                        )
        self.assertEqual(response.status_code, 401)

    def test_bad_token(self, merror_validator, mwarning_validator):
        bad_token = jwt.encode({'authorities': ['one_role', 'two_role']}, 'bad_secret')
        response = self.app_client.post('/validators/update',
                                        content_type='application/json',
                                        headers={'Authorization': 'Bearer {0}'.format(bad_token.decode('utf-8'))},
                                        data=json.dumps({'ddotLocation': {}})
                                        )
        self.assertEqual(response.status_code, 422)