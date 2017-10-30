
from unittest import TestCase

from app import application
from ..warning_validator import WarningValidator

validator = WarningValidator(application.config['SCHEMA_DIR'], application.config['REFERENCE_FILE_DIR'])


class AltitudeWarningValidationsTestCase(TestCase):
    def setUp(self):
        validator = WarningValidator(application.config['SCHEMA_DIR'], application.config['REFERENCE_FILE_DIR'])

    def test_valid_altitude_range(self):
        validator .validate(
            {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitude': '1234'},
            {'altitude': '1234', 'altitudeAccuracyValue': 'A', 'altitudeMethodCode': 'AAA', 'altitudeDatumCode': 'BBB',
             'countryCode': 'US', 'stateFipsCode': '55'},
            update=True)
        self.assertNotIn('altitude', validator .warnings)

    def test_invalid_altitude_range(self):
        validator .validate(
            {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitude': '2234'},
            {'altitude': '1234', 'altitudeAccuracyValue': 'A', 'altitudeMethodCode': 'AAA', 'altitudeDatumCode': 'BBB',
             'countryCode': 'US', 'stateFipsCode': '55'},
            update=True)
        self.assertIn('altitude', validator .warnings)

    def test_state_not_in_list(self):
        validator .validate(
            {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitude': '2234'},
            {'altitude': '1234', 'altitudeAccuracyValue': 'A', 'altitudeMethodCode': 'AAA', 'altitudeDatumCode': 'BBB',
             'countryCode': 'US', 'stateFipsCode': '80'},
            update=True)
        self.assertNotIn('altitude', validator .warnings)

    def test_country_not_in_list(self):
        validator .validate(
            {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitude': '2234'},
            {'altitude': '1234', 'altitudeAccuracyValue': 'A', 'altitudeMethodCode': 'AAA', 'altitudeDatumCode': 'BBB',
             'countryCode': 'ZZ', 'stateFipsCode': '80'},
            update=True)
        self.assertNotIn('altitude', validator .warnings)

    def test_missing_country_state(self):
        validator .validate(
            {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitude': '2234'},
            {'altitude': '1234', 'altitudeAccuracyValue': 'A', 'altitudeMethodCode': 'AAA', 'altitudeDatumCode': 'BBB',
             'stateFipsCode': '80'},
            update=True)
        self.assertNotIn('altitude', validator .warnings)

        validator .validate(
            {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitude': '2234'},
            {'altitude': '1234', 'altitudeAccuracyValue': 'A', 'altitudeMethodCode': 'AAA', 'altitudeDatumCode': 'BBB',
             'countryCode': 'US'},
            update=True)
        self.assertNotIn('altitude', validator .warnings)


class WarningValidatorStationNameTestCase(TestCase):

    def test_valid_station_name_matching_quotes(self):
        self.assertTrue(validator.validate({'stationName': 'this is a station'}, {}, update=True))

    def test_valid_station_name_spaces_matching_quotes(self):
        self.assertTrue(validator.validate({'stationName': '     '}, {}, update=True))

    def test_valid_station_name_quote_in_middle(self):
        self.assertTrue(validator.validate({'stationName': "This is USGS's Station"}, {}, update=True))

    def test_invalid_quote_at_end(self):
        self.assertFalse(validator.validate({'stationName': "This is a USGS Station'"}, {}, update=True))

    def test_invalid_quote_at_beginning(self):
        self.assertFalse(validator.validate({'stationName': "'This is a USGS Station"}, {}, update=True))
