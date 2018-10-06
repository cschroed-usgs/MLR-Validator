
from unittest import TestCase

from app import application
from ..error_validator import ErrorValidator

validator = ErrorValidator(application.config['SCHEMA_DIR'], application.config['REFERENCE_FILE_DIR'])


class ErrorValidatorAgencyCodeTestCase(TestCase):
    # We are leaving out the landNet validations for now as there too many questions as to how these will work
    # The existing land net validation is also well tested by unit tests.

    def test_agency_code_no_padding_is_valid(self):
        self.assertTrue(validator.validate({'agencyCode': 'USGS'}, {}))

    def test_agency_code_padding_is_valid(self):
        self.assertTrue(validator.validate({'agencyCode': 'USGS '}, {}))

    def test_agency_code_lower_padding_is_invalid(self):
        self.assertFalse(validator.validate({'agencyCode': 'usgs   '}, {}))

    def test_agency_code_lower_no_padding_is_invalid(self):
        self.assertFalse(validator.validate({'agencyCode': 'usgs'}, {}))

    def test_agency_code_not_in_ref_list_padding_is_invalid(self):
        self.assertFalse(validator.validate({'agencyCode': 'XYZ   '}, {}))

    def test_agency_code_not_in_ref_list_no_padding_is_invalid(self):
        self.assertFalse(validator.validate({'agencyCode': 'XYZ'}, {}))

    def test_agency_code_not_in_ref_list_padding_too_long_is_invalid(self):
        self.assertFalse(validator.validate({'agencyCode': 'XYZ     '}, {}))
        self.assertEqual(len(validator.errors.get('agencyCode')), 2)

    def test_agency_code_in_ref_list_padding_too_long_is_invalid(self):
        self.assertFalse(validator.validate({'agencyCode': 'USGS      '}, {}))
        self.assertEqual(len(validator.errors.get('agencyCode')), 1)

    def test_agency_code_null_is_invalid(self):
        self.assertFalse(validator.validate({'agencyCode': ''}, {}))
        self.assertEqual(len(validator.errors.get('agencyCode')), 1)

    def test_agency_code_null_padding_is_invalid(self):
        self.assertFalse(validator.validate({'agencyCode': ' '}, {}))
        self.assertEqual(len(validator.errors.get('agencyCode')), 1)

    def test_agency_code_padding_too_long_is_invalid(self):
        self.assertFalse(validator.validate({'agencyCode': '           '}, {}))
        self.assertEqual(len(validator.errors.get('agencyCode')), 2)

    def test_agency_code_missing_on_insert_is_invalid(self):
        validator.validate({'siteNumber': '9876543210'}, )
        self.assertIn('agencyCode', validator.errors)


class ErrorValidatorSiteNumberTestCase(TestCase):

    def test_only_digits_is_valid(self):
        self.assertTrue(validator.validate({'siteNumber': '01234'}, {}))

    def test_only_digits_trailing_space_is_valid(self):
        self.assertTrue(validator.validate({'siteNumber': '01234   '}, {}))

    def test_null_value_no_pad_is_invalid(self):
        self.assertFalse(validator.validate({'siteNumber': ''}, {}))
        self.assertEqual(len(validator.errors.get('siteNumber')), 1)

    def test_null_value_pad_is_invalid(self):
        self.assertFalse(validator.validate({'siteNumber': ' '}, {}))
        self.assertEqual(len(validator.errors.get('siteNumber')), 1)

    def test_non_digit_is_invalid(self):
        self.assertFalse(validator.validate({'siteNumber': 'a6'}, {}))

    def test_non_digit_special_char_is_invalid(self):
        self.assertFalse(validator.validate({'siteNumber': '$'}, {}))

    def test_only_digits_blank_space_is_invalid(self):
        self.assertFalse(validator.validate({'siteNumber': '32   4'}, {}))

    def test_only_digits_too_long_is_invalid(self):
        self.assertFalse(validator.validate({'siteNumber': '0126954826512369548'}, {}))
        self.assertEqual(len(validator.errors.get('siteNumber')), 1)

    def test_invalid_chars_too_long_is_invalid(self):
        self.assertFalse(validator.validate({'siteNumber': '01269d82g651y23e69s548'}, {}))
        self.assertEqual(len(validator.errors.get('siteNumber')), 2)

    def test_only_spaces_too_long_is_invalid(self):
        self.assertFalse(validator.validate({'siteNumber': '                    '}, {}))
        self.assertEqual(len(validator.errors.get('siteNumber')), 2)

    def test_site_number_ll_valid(self):
        validator.validate({'siteTypeCode': 'AT', 'siteNumber': '012345678901234'}, {})
        self.assertNotIn('siteNumber', validator.errors)

    def test_site_number_dsll_min_length_valid(self):
        validator.validate({'siteTypeCode': 'GL', 'siteNumber': '12345678'}, {})
        self.assertNotIn('siteNumber', validator.errors)

    def test_site_number_dsll_max_length_valid(self):
        validator.validate({'siteTypeCode': 'GL', 'siteNumber': '012345678901234'}, {})
        self.assertNotIn('siteNumber', validator.errors)

    def test_site_number_wu_min_length_first_digit_valid(self):
        self.assertTrue(validator.validate({'siteTypeCode': 'AW', 'siteNumber': '9876543210'}, {}))

    def test_site_number_wu_max_length_first_digit_valid(self):
        self.assertTrue(validator.validate({'siteTypeCode': 'AW', 'siteNumber': '987654321098765'}, {}))

    def test_site_number_llwu_max_length_first_digit_valid(self):
        validator.validate({'siteTypeCode': 'FA-CI', 'siteNumber': '987654321098765'}, {})
        self.assertNotIn('siteNumber', validator.errors)

    def test_site_number_llwu_max_length_valid(self):
        validator.validate({'siteTypeCode': 'FA-CI', 'siteNumber': '087654321098765'}, {})
        self.assertNotIn('siteNumber', validator.errors)

    def test_site_number_llwu_min_length_valid(self):
        validator.validate({'siteTypeCode': 'FA-CI', 'siteNumber': '9876543210'}, {})
        self.assertNotIn('siteNumber', validator.errors)

    def test_no_site_type_invalid(self):
        self.assertFalse(validator.validate({'siteTypeCode': ' ', 'siteNumber': '12345678'}, {}))

    def test_no_site_number_invalid(self):
        self.assertFalse(validator.validate({'siteTypeCode': 'AT', 'siteNumber': ' '}, {}))

    def test_site_number_ll_invalid(self):
        self.assertFalse(validator.validate({'siteTypeCode': 'AT', 'siteNumber': '01234567890123'}, {}))

    def test_site_number_dsll_less_than_min_length_invalid(self):
        self.assertFalse(validator.validate({'siteTypeCode': 'GL', 'siteNumber': '1234567'}, {}))

    def test_site_number_dsll_greater_than_max_length_invalid(self):
        self.assertFalse(validator.validate({'siteTypeCode': 'GL', 'siteNumber': '0123456789012345'}, {}))

    def test_site_number_wu_less_than_min_length_first_digit_invalid(self):
        self.assertFalse(validator.validate({'siteTypeCode': 'AW', 'siteNumber': '987654321'}, {}))

    def test_site_number_wu_no_first_digit_invalid(self):
        self.assertFalse(validator.validate({'siteTypeCode': 'AW', 'siteNumber': '8765432109'}, {}))

    def test_site_number_wu_greater_than_max_length_first_digit_invalid(self):
        self.assertFalse(validator.validate({'siteTypeCode': 'AW', 'siteNumber': '987654321098765432'}, {}))

    def test_site_number_llwu_greater_than_max_length_invalid(self):
        self.assertFalse(validator.validate({'siteTypeCode': 'FA-CI', 'siteNumber': '98765432109876543'}, {}))

    def test_site_number_llwu_less_than_min_length_invalid(self):
        self.assertFalse(validator.validate({'siteTypeCode': 'FA-CI', 'siteNumber': '59876543'}, {}))

    def test_site_number_llwu_wrong_first_digit_invalid(self):
        self.assertFalse(validator.validate({'siteTypeCode': 'FA-CI', 'siteNumber': '087654321098'}, {}))


class ErrorValidatorStationNameTestCase(TestCase):

    def test_valid_chars_all_lower_is_valid(self):
        self.assertTrue(validator.validate({'stationName': 'br549'}, {}))

    def test_valid_chars_mix_upper_lower_is_valid(self):
        self.assertTrue(validator.validate({'stationName': 'YYyyNnNN'}, {}))

    def test_valid_chars_all_upper_is_valid(self):
        self.assertTrue(validator.validate({'stationName': 'ABCD'}, {}))

    def test_valid_chars_space_in_middle_is_valid(self):
        self.assertTrue(validator.validate({'stationName': 'br 549'}, {}))

    def test_allowed_special_chars_is_valid(self):
        self.assertTrue(validator.validate({'stationName': 'a-b'}, {}))

    def test_leading_space_is_valid(self):
        self.assertTrue(validator.validate({'stationName': '   BR549'}, {}))

    def test_trailing_space_is_valid(self):
        self.assertTrue(validator.validate({'stationName': 'BR549   '}, {}))

    def test_null_value_no_pad_is_invalid(self):
        self.assertFalse(validator.validate({'stationName': ''}, {}))
        self.assertEqual(len(validator.errors.get('stationName')), 1)

    def test_null_value_pad_is_invalid(self):
        self.assertFalse(validator.validate({'stationName': ' '}, {}))
        self.assertEqual(len(validator.errors.get('stationName')), 1)

    def test_bad_special_char_pound_sign_is_invalid(self):
        self.assertFalse(validator.validate({'stationName': 'br5#49'}, {}))

    def test_bad_special_char_tab_is_invalid(self):
        self.assertFalse(validator.validate({'stationName': 'br\t549'}, {}))

    def test_bad_special_char_backslash_is_invalid(self):
        self.assertFalse(validator.validate({'stationName': 'br\\549'}, {}))

    def test_bad_special_char_dollar_sign_is_invalid(self):
        self.assertFalse(validator.validate({'stationName': '$br549'}, {}))

    def test_bad_special_char_caret_is_invalid(self):
        self.assertFalse(validator.validate({'stationName': 'b^r549'}, {}))

    def test_bad_special_char_asterisk_is_invalid(self):
        self.assertFalse(validator.validate({'stationName': 'br5*49'}, {}))

    def test_bad_special_char_double_quotes_is_invalid(self):
        self.assertFalse(validator.validate({'stationName': 'br54"9'}, {}))

    def test_bad_special_char_underscore_is_invalid(self):
        self.assertFalse(validator.validate({'stationName': 'br549_'}, {}))

    def test_valid_chars_too_long_is_invalid(self):
        self.assertFalse(
            validator.validate({'stationName': '0126954826512369548fesgdrs0126954826512369548fesgdrs'}, {}))
        self.assertEqual(len(validator.errors.get('stationName')), 1)

    def test_invalid_chars_too_long_is_invalid(self):
        self.assertFalse(
            validator.validate({'stationName': '01269d8#**2g65\\1y23e69s548                         '}, {}))
        self.assertEqual(len(validator.errors.get('stationName')), 2)

    def test_only_spaces_too_long_is_invalid(self):
        self.assertFalse(
            validator.validate({'stationName': '                                                            '}, {}))
        self.assertEqual(len(validator.errors.get('stationName')), 2)


class ErrorValidatorLatitudeTestCase(TestCase):

    def test_null_no_pad_latitude_empty_string_dependencies_is_valid(self):
        self.assertTrue(validator.validate({'latitude': '', 'longitude': '',
                                            'coordinateAccuracyCode': '', 'coordinateDatumCode': '',
                                            'coordinateMethodCode': ''}, {}))

    def test_null_no_pad_latitude_dependencies_missing_is_valid(self):
        self.assertTrue(validator.validate({'latitude': ''}, {}))

    def test_null_pad_latitude_dependencies_missing_is_valid(self):
        self.assertTrue(validator.validate({'latitude': ' '}, {}))

    def test_null_pad_latitude_pad_dependencies_is_valid(self):
        self.assertTrue(validator.validate({'latitude': ' ', 'longitude': ' ',
                                            'coordinateAccuracyCode': ' ', 'coordinateDatumCode': ' ',
                                            'coordinateMethodCode': ' '}, {}))

    def test_positive_dms_is_valid(self):
        self.assertTrue(validator.validate({'latitude': ' 123456', 'longitude': ' 1234556',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_positive_single_digit_degrees_is_valid(self):
        self.assertTrue(validator.validate({'latitude': ' 023456', 'longitude': ' 1234556',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_positive_zero_degrees_with_ms_is_valid(self):
        self.assertTrue(validator.validate({'latitude': ' 003456', 'longitude': ' 1234556',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_positive_zero_degrees_single_digit_minutes_is_valid(self):
        self.assertTrue(validator.validate({'latitude': ' 000456', 'longitude': ' 1234556',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_positive_zero_degrees_zero_minutes_with_seconds_is_valid(self):
        self.assertTrue(validator.validate({'latitude': ' 000056', 'longitude': ' 1234556',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_positive_zero_degrees_zero_minutes_single_digit_seconds_is_valid(self):
        self.assertTrue(validator.validate({'latitude': ' 000006', 'longitude': ' 1234556',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_positive_zero_degrees_zero_minutes_zero_seconds_is_valid(self):
        self.assertTrue(validator.validate({'latitude': ' 000000', 'longitude': ' 1234556',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_positive_max_degrees_max_minutes_max_seconds_is_valid(self):
        self.assertTrue(validator.validate({'latitude': ' 905959', 'longitude': ' 1234556',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_positive_dms_with_10ths_seconds_is_valid(self):
        self.assertTrue(validator.validate({'latitude': ' 900000.0', 'longitude': ' 1234556',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_positive_dms_with_100ths_seconds_is_valid(self):
        self.assertTrue(
            validator.validate({'latitude': ' 900000.93', 'longitude': ' 1234556',
                                'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                'coordinateMethodCode': 'C'}, {}))

    def test_positive_dms_with_1000ths_seconds_is_valid(self):
        self.assertTrue(
            validator.validate({'latitude': ' 900000.093', 'longitude': ' 1234556',
                                'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                'coordinateMethodCode': 'C'}, {}))

    def test_negative_dms_is_valid(self):
        self.assertTrue(validator.validate({'latitude': '-123456', 'longitude': ' 1234556',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_negative_single_digit_degrees_is_valid(self):
        self.assertTrue(validator.validate({'latitude': '-023456', 'longitude': ' 1234556',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_negative_zero_degrees_with_ms_is_valid(self):
        self.assertTrue(validator.validate({'latitude': '-003456', 'longitude': ' 1234556',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_negative_zero_degrees_single_digit_minutes_is_valid(self):
        self.assertTrue(validator.validate({'latitude': '-000456', 'longitude': ' 1234556',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_negative_zero_degrees_zero_minutes_with_seconds_is_valid(self):
        self.assertTrue(validator.validate({'latitude': '-000056', 'longitude': ' 1234556',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_negative_zero_degrees_zero_minutes_single_digit_seconds_is_valid(self):
        self.assertTrue(validator.validate({'latitude': '-000006', 'longitude': ' 1234556',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_negative_zero_degrees_zero_minutes_zero_seconds_is_valid(self):
        self.assertTrue(validator.validate({'latitude': '-000000', 'longitude': ' 1234556',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_negative_max_degrees_max_minutes_max_seconds_is_valid(self):
        self.assertTrue(validator.validate({'latitude': '-905959', 'longitude': ' 1234556',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_negative_dms_with_10ths_seconds_is_valid(self):
        self.assertTrue(validator.validate({'latitude': '-900000.0', 'longitude': ' 1234556',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_negative_dms_with_100ths_seconds_is_valid(self):
        self.assertTrue(
            validator.validate({'latitude': '-900000.93', 'longitude': ' 1234556',
                                'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                'coordinateMethodCode': 'C'}, {}))

    def test_negative_dms_with_1000ths_seconds_is_valid(self):
        self.assertTrue(
            validator.validate({'latitude': '-900000.093', 'longitude': ' 1234556',
                                'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                'coordinateMethodCode': 'C'}, {}))

    def test_missing_seconds_is_invalid(self):
        self.assertFalse(validator.validate({'latitude': ' 9020', 'longitude': ' 1234556',
                                             'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))

    def test_missing_minutes_seconds_is_invalid(self):
        self.assertFalse(validator.validate({'latitude': ' 90', 'longitude': ' 1234556',
                                             'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))

    def test_over_max_degrees_is_invalid(self):
        self.assertFalse(validator.validate({'latitude': ' 990000', 'longitude': ' 1234556',
                                             'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))

    def test_over_max_minutes_is_invalid(self):
        self.assertFalse(validator.validate({'latitude': ' 207500', 'longitude': ' 1234556',
                                             'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))

    def test_over_max_seconds_is_invalid(self):
        self.assertFalse(validator.validate({'latitude': ' 200066', 'longitude': ' 1234556',
                                             'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))

    def test_too_many_seconds_decimals_is_invalid(self):
        self.assertFalse(validator.validate({'latitude': ' 200023.9234', 'longitude': ' 1234556',
                                             'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))
        self.assertEqual(len(validator.errors.get('latitude')), 1)

    def test_dangling_decimal_is_invalid(self):
        self.assertFalse(validator.validate({'latitude': ' 200023.', 'longitude': ' 1234556',
                                             'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))
        self.assertEqual(len(validator.errors.get('latitude')), 1)

    def test_too_long_is_invalid(self):
        self.assertFalse(validator.validate({'latitude': ' 20003234', 'longitude': ' 1234556',
                                             'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))
        self.assertEqual(len(validator.errors.get('latitude')), 1)

    def test_longer_than_maxlength_is_invalid(self):
        self.assertFalse(validator.validate({'latitude': ' 203300203234', 'longitude': ' 1234556',
                                             'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))
        self.assertEqual(len(validator.errors.get('latitude')), 2)

    def test_longer_than_maxlength_spaces_is_invalid(self):
        self.assertFalse(validator.validate({'latitude': '             ', 'longitude': ' 1234556',
                                             'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))
        self.assertEqual(len(validator.errors.get('latitude')), 1)
        self.assertIn('latitude', validator.errors.get('location')[0])

    def test_latitude_without_longitude_is_invalid(self):
        self.assertFalse(validator.validate({'latitude': ' 040000',
                                             'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))
        self.assertIn('latitude', validator.errors.get('location')[0])

    def test_good_latitude_null_dependencies_is_invalid(self):
        self.assertFalse(validator.validate({'latitude': ' 123456', 'longitude': '',
                                             'coordinateAccuracyCode': '', 'coordinateDatumCode': '',
                                             'coordinateMethodCode': ''}, {}))
        self.assertIn('latitude', validator.errors.get('location')[0])

    def test_good_latitude_non_exist_dependencies_is_invalid(self):
        self.assertFalse(validator.validate({'latitude': ' 123456'}, {}))
        self.assertIn('latitude', validator.errors.get('location')[0])

    def test_good_latitude_good_longitude_null_dependencies_is_invalid(self):
        self.assertFalse(validator.validate({'latitude': ' 123456', 'longitude': ' 1234556',
                                             'coordinateAccuracyCode': '', 'coordinateDatumCode': '',
                                             'coordinateMethodCode': ''}, {}))
        self.assertIn('latitude', validator.errors.get('location')[0])

    def test_good_latitude_good_longitude_null_2_dependencies_is_invalid(self):
        self.assertFalse(validator.validate({'latitude': ' 123456', 'longitude': ' 1234556',
                                             'coordinateAccuracyCode': '1', 'coordinateDatumCode': '',
                                             'coordinateMethodCode': ''}, {}))
        self.assertIn('latitude', validator.errors.get('location')[0])

    def test_good_latitude_good_longitude_null_1_dependency_is_invalid(self):
        self.assertFalse(validator.validate({'latitude': ' 123456', 'longitude': ' 1234556',
                                             'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': ''}, {}))
        self.assertIn('latitude', validator.errors.get('location')[0])

    def test_first_char_not_space_or_negative_is_invalid(self):
        self.assertFalse(validator.validate({'latitude': '200023', 'longitude': ' 1234556',
                                             'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))

    def test_non_digit_is_invalid(self):
        self.assertFalse(validator.validate({'latitude': ' 200u23', 'longitude': ' 1234556',
                                             'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))

    def test_invalid_null_code_for_site_type(self):
        validator.validate({'latitude': '', 'longitude': '',
                            'coordinateAccuracyCode': '', 'coordinateDatumCode': '',
                            'coordinateMethodCode': '', 'siteTypeCode': 'AT'}, {})
        self.assertIn('latitude', validator.errors['siteTypeCode'][0])

        validator.validate({'latitude': '', 'longitude': '',
                            'coordinateAccuracyCode': '', 'coordinateDatumCode': '',
                            'coordinateMethodCode': '', 'siteTypeCode': 'AG'}, {})
        self.assertNotIn('siteTypeCode', validator.errors)

        validator.validate({'latitude': ' 123456', 'longitude': ' 1234556',
                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                            'coordinateMethodCode': 'C', 'siteTypeCode': 'AS'}, {})
        self.assertNotIn('siteTypeCode', validator.errors)


class ErrorValidatorLongitudeTestCase(TestCase):

    def test_null_no_pad_longitude_empty_string_dependencies_is_valid(self):
        self.assertTrue(validator.validate({'longitude': '', 'latitude': '',
                                            'coordinateAccuracyCode': '', 'coordinateDatumCode': '',
                                            'coordinateMethodCode': ''}, {}))

    def test_null_no_pad_longitude_dependencies_missing_is_valid(self):
        self.assertTrue(validator.validate({'longitude': ''}, {}))

    def test_null_pad_longitude_dependencies_missing_is_valid(self):
        self.assertTrue(validator.validate({'longitude': ' '}, {}))

    def test_null_pad_longitude_pad_dependencies_is_valid(self):
        self.assertTrue(validator.validate({'longitude': ' ', 'latitude': ' ',
                                            'coordinateAccuracyCode': ' ', 'coordinateDatumCode': ' ',
                                            'coordinateMethodCode': ' '}, {}))

    def test_positive_dms_is_valid(self):
        self.assertTrue(validator.validate({'longitude': ' 1234556', 'latitude': ' 123456',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_positive_double_digit_degrees_is_valid(self):
        self.assertTrue(validator.validate({'longitude': ' 0234556', 'latitude': ' 123456',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_positive_single_digit_degrees_is_valid(self):
        self.assertTrue(validator.validate({'longitude': ' 0034556', 'latitude': ' 123456',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_positive_zero_degrees_with_ms_is_valid(self):
        self.assertTrue(validator.validate({'longitude': ' 0004556', 'latitude': ' 123456',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_positive_zero_degrees_single_digit_minutes_is_valid(self):
        self.assertTrue(validator.validate({'longitude': ' 0000556', 'latitude': ' 123456',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_positive_zero_degrees_zero_minutes_with_seconds_is_valid(self):
        self.assertTrue(validator.validate({'longitude': ' 0000056', 'latitude': ' 123456',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_positive_zero_degrees_zero_minutes_single_digit_seconds_is_valid(self):
        self.assertTrue(validator.validate({'longitude': ' 0000006', 'latitude': ' 123456',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_positive_zero_degrees_zero_minutes_zero_seconds_is_valid(self):
        self.assertTrue(validator.validate({'longitude': ' 0000000', 'latitude': ' 123456',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_positive_max_degrees_max_minutes_max_seconds_is_valid(self):
        self.assertTrue(validator.validate({'longitude': ' 1805959', 'latitude': ' 123456',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_positive_dms_with_10ths_seconds_is_valid(self):
        self.assertTrue(validator.validate({'longitude': ' 1234556.2', 'latitude': ' 123456',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_positive_dms_with_100ths_seconds_is_valid(self):
        self.assertTrue(
            validator.validate({'longitude': ' 1234556.23', 'latitude': ' 123456',
                                'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                'coordinateMethodCode': 'C'}, {}))

    def test_positive_dms_with_1000ths_seconds_is_valid(self):
        self.assertTrue(
            validator.validate({'longitude': ' 1234556.326', 'latitude': ' 123456',
                                'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                'coordinateMethodCode': 'C'}, {}))

    def test_negative_dms_is_valid(self):
        self.assertTrue(validator.validate({'longitude': '-1234556', 'latitude': ' 123456',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_negative_double_digit_degrees_is_valid(self):
        self.assertTrue(validator.validate({'longitude': '-0234556', 'latitude': ' 123456',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_negative_single_digit_degrees_is_valid(self):
        self.assertTrue(validator.validate({'longitude': '-0034556', 'latitude': ' 123456',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_negative_zero_degrees_with_ms_is_valid(self):
        self.assertTrue(validator.validate({'longitude': '-0004556', 'latitude': ' 123456',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_negative_zero_degrees_single_digit_minutes_is_valid(self):
        self.assertTrue(validator.validate({'longitude': '-0000556', 'latitude': ' 123456',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_negative_zero_degrees_zero_minutes_with_seconds_is_valid(self):
        self.assertTrue(validator.validate({'longitude': '-0000056', 'latitude': ' 123456',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_negative_zero_degrees_zero_minutes_single_digit_seconds_is_valid(self):
        self.assertTrue(validator.validate({'longitude': '-0000006', 'latitude': ' 123456',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_negative_zero_degrees_zero_minutes_zero_seconds_is_valid(self):
        self.assertTrue(validator.validate({'longitude': '-0000000', 'latitude': ' 123456',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_negative_max_degrees_max_minutes_max_seconds_is_valid(self):
        self.assertTrue(validator.validate({'longitude': '-1805959', 'latitude': ' 123456',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_negative_dms_with_10ths_seconds_is_valid(self):
        self.assertTrue(validator.validate({'longitude': '-1234556.2', 'latitude': ' 123456',
                                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_negative_dms_with_100ths_seconds_is_valid(self):
        self.assertTrue(
            validator.validate({'longitude': '-1234556.23', 'latitude': ' 123456',
                                'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                'coordinateMethodCode': 'C'}, {}))

    def test_negative_dms_with_1000ths_seconds_is_valid(self):
        self.assertTrue(
            validator.validate({'longitude': '-1234556.326', 'latitude': ' 123456',
                                'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                'coordinateMethodCode': 'C'}, {}))

    def test_missing_seconds_is_invalid(self):
        self.assertFalse(validator.validate({'longitude': ' 12345', 'latitude': ' 123456',
                                             'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))

    def test_missing_minutes_seconds_is_invalid(self):
        self.assertFalse(validator.validate({'longitude': ' 123', 'latitude': ' 123456',
                                             'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))

    def test_over_max_degrees_is_invalid(self):
        self.assertFalse(validator.validate({'longitude': ' 1934556', 'latitude': ' 123456',
                                             'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))

    def test_over_max_minutes_is_invalid(self):
        self.assertFalse(validator.validate({'longitude': ' 1238556', 'latitude': ' 123456',
                                             'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))

    def test_over_max_seconds_is_invalid(self):
        self.assertFalse(validator.validate({'longitude': ' 1234576', 'latitude': ' 123456',
                                             'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))

    def test_too_many_seconds_decimals_is_invalid(self):
        self.assertFalse(validator.validate({'longitude': ' 1234556.2689', 'latitude': ' 123456',
                                             'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))
        self.assertEqual(len(validator.errors.get('longitude')), 1)

    def test_dangling_decimal_is_invalid(self):
        self.assertFalse(validator.validate({'longitude': ' 1234556.', 'latitude': ' 123456',
                                             'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))
        self.assertEqual(len(validator.errors.get('longitude')), 1)

    def test_too_long_is_invalid(self):
        self.assertFalse(validator.validate({'longitude': ' 12345566', 'latitude': ' 123456',
                                             'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))
        self.assertEqual(len(validator.errors.get('longitude')), 1)

    def test_longer_than_maxlength_is_invalid(self):
        self.assertFalse(validator.validate({'longitude': ' 12345561232112', 'latitude': ' 123456',
                                             'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))
        self.assertEqual(len(validator.errors.get('longitude')), 2)

    def test_longer_than_maxlength_spaces_is_invalid(self):
        self.assertFalse(validator.validate({'longitude': '               ', 'latitude': ' 123456',
                                             'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))
        self.assertEqual(len(validator.errors.get('longitude')), 1)
        self.assertIn('longitude', validator.errors.get('location')[0])

    def test_longitude_without_latitude_is_invalid(self):
        self.assertFalse(validator.validate({'longitude': ' 0400000',
                                             'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))
        self.assertIn('longitude', validator.errors.get('location')[0])

    def test_good_longitude_null_dependencies_is_invalid(self):
        self.assertFalse(validator.validate({'longitude': ' 0123456', 'latitude': '',
                                             'coordinateAccuracyCode': '', 'coordinateDatumCode': '',
                                             'coordinateMethodCode': ''}, {}))
        self.assertIn('longitude', validator.errors.get('location')[0])

    def test_good_longitude_non_exist_dependencies_is_invalid(self):
        self.assertFalse(validator.validate({'longitude': ' 0123456'}, {}))
        self.assertIn('longitude', validator.errors.get('location')[0])

    def test_good_longitude_good_latitude_null_dependencies_is_invalid(self):
        self.assertFalse(validator.validate({'longitude': ' 1234556', 'latitude': ' 123456',
                                             'coordinateAccuracyCode': '', 'coordinateDatumCode': '',
                                             'coordinateMethodCode': ''}, {}))
        self.assertIn('longitude', validator.errors.get('location')[0])

    def test_good_longitude_good_latitude_null_2_dependencies_is_invalid(self):
        self.assertFalse(validator.validate({'longitude': ' 1234556', 'latitude': ' 123456',
                                             'coordinateAccuracyCode': '1', 'coordinateDatumCode': '',
                                             'coordinateMethodCode': ''}, {}))
        self.assertIn('longitude', validator.errors.get('location')[0])

    def test_good_longitude_good_latitude_null_1_dependency_is_invalid(self):
        self.assertFalse(validator.validate({'longitude': ' 1234556', 'latitude': ' 123456',
                                             'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': ''}, {}))
        self.assertIn('longitude', validator.errors.get('location')[0])

    def test_first_char_not_space_or_negative_is_invalid(self):
        self.assertFalse(validator.validate({'longitude': '1234556', 'latitude': ' 123456',
                                             'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))

    def test_non_digit_is_invalid(self):
        self.assertFalse(validator.validate({'longitude': ' 123h556', 'latitude': ' 123456',
                                             'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))

    def test_invalid_null_code_for_site_type(self):
        validator.validate({'latitude': '', 'longitude': '',
                            'coordinateAccuracyCode': '', 'coordinateDatumCode': '',
                            'coordinateMethodCode': '', 'siteTypeCode': 'AT'}, {})
        self.assertIn('longitude', validator.errors['siteTypeCode'][0])

        validator.validate({'latitude': '', 'longitude': '',
                            'coordinateAccuracyCode': '', 'coordinateDatumCode': '',
                            'coordinateMethodCode': '', 'siteTypeCode': 'AG'}, {})
        self.assertNotIn('siteTypeCode', validator.errors)

        validator.validate({'latitude': ' 123456', 'longitude': ' 1234556',
                            'coordinateAccuracyCode': '1', 'coordinateDatumCode': 'BARBADOS',
                            'coordinateMethodCode': 'C', 'siteTypeCode': 'AS'}, {})
        self.assertNotIn('siteTypeCode', validator.errors)


class ErrorValidatorCoordinateAccuracyCodeTestCase(TestCase):

    def test_coordinate_accuracy_code_digit_in_ref_list_is_valid(self):
        self.assertTrue(validator.validate({'coordinateAccuracyCode': '1', 'longitude': ' 1234556',
                                            'latitude': ' 123456', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_coordinate_accuracy_code_char_in_ref_list_is_valid(self):
        self.assertTrue(validator.validate({'coordinateAccuracyCode': 'E', 'longitude': ' 1234556',
                                            'latitude': ' 123456', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateMethodCode': 'C'}, {}))

    def test_coordinate_accuracy_code_null_lat_long_null_is_valid(self):
        self.assertTrue(validator.validate({'coordinateAccuracyCode': '', 'longitude': '',
                                            'latitude': '', 'coordinateDatumCode': '',
                                            'coordinateMethodCode': ''}, {}))

    def test_coordinate_accuracy_code_longer_than_maxlength_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateAccuracyCode': 'E1', 'longitude': ' 1234556',
                                             'latitude': ' 123456', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))
        self.assertEqual(len(validator.errors.get('coordinateAccuracyCode')), 2)

    def test_coordinate_accuracy_code_longer_than_maxlength_spaces_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateAccuracyCode': '  ', 'longitude': ' 1234556',
                                             'latitude': ' 123456', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))
        result = validator.errors.get('coordinateAccuracyCode')
        self.assertEqual(len(validator.errors.get('coordinateAccuracyCode')), 1)
        self.assertIn('coordinateAccuracyCode', validator.errors.get('location')[0])

    def test_coordinate_accuracy_code_lower_char_in_ref_list_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateAccuracyCode': 'e', 'longitude': ' 1234556',
                                             'latitude': ' 123456', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))

    def test_coordinate_accuracy_code_null_pad_lat_long_not_null_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateAccuracyCode': ' ', 'longitude': ' 1234556',
                                             'latitude': ' 123456', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))
        self.assertIn('coordinateAccuracyCode', validator.errors.get('location')[0])

    def test_coordinate_accuracy_code_null_no_pad_lat_long_not_null_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateAccuracyCode': '', 'longitude': ' 1234556',
                                             'latitude': ' 123456', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))
        self.assertIn('coordinateAccuracyCode', validator.errors.get('location')[0])

    def test_coordinate_accuracy_code_null_no_pad_lat_not_null_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateAccuracyCode': '', 'longitude': '',
                                             'latitude': ' 123456', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))
        self.assertIn('coordinateAccuracyCode', validator.errors.get('location')[0])

    def test_coordinate_accuracy_code_null_no_pad_lat_not_null_long_pad_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateAccuracyCode': '', 'longitude': ' ',
                                             'latitude': ' 123456', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))
        self.assertIn('coordinateAccuracyCode', validator.errors.get('location')[0])

    def test_coordinate_accuracy_code_null_no_pad_long_not_null_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateAccuracyCode': '', 'longitude': ' 1234556',
                                             'latitude': '', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))
        self.assertIn('coordinateAccuracyCode', validator.errors.get('location')[0])

    def test_coordinate_accuracy_code_null_no_pad_long_not_null_lat_pad_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateAccuracyCode': '', 'longitude': ' 1234556',
                                             'latitude': ' ', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))
        self.assertIn('coordinateAccuracyCode', validator.errors.get('location')[0])

    def test_coordinate_accuracy_code_not_null_lat_long_null_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateAccuracyCode': 'E', 'longitude': '',
                                             'latitude': '', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))
        self.assertIn('coordinateAccuracyCode', validator.errors.get('location')[0])

    def test_coordinate_accuracy_code_not_null_lat_null_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateAccuracyCode': 'E', 'longitude': ' 1234556',
                                             'latitude': '', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))
        self.assertIn('coordinateAccuracyCode', validator.errors.get('location')[0])

    def test_coordinate_accuracy_code_not_null_long_null_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateAccuracyCode': 'E', 'longitude': '',
                                             'latitude': ' 123456', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateMethodCode': 'C'}, {}))
        self.assertIn('coordinateAccuracyCode', validator.errors.get('location')[0])


class ErrorValidatorCoordinateMethodCodeTestCase(TestCase):

    def test_coordinate_method_code_char_in_ref_list_is_valid(self):
        self.assertTrue(validator.validate({'coordinateMethodCode': 'C', 'longitude': ' 1234556',
                                            'latitude': ' 123456', 'coordinateDatumCode': 'BARBADOS',
                                            'coordinateAccuracyCode': 'E'}, {}))

    def test_coordinate_method_code_null_lat_long_null_is_valid(self):
        self.assertTrue(validator.validate({'coordinateMethodCode': '', 'longitude': '',
                                            'latitude': '', 'coordinateDatumCode': '',
                                            'coordinateAccuracyCode': ''}, {}))

    def test_coordinate_method_code_lower_char_in_ref_list_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateMethodCode': 'c', 'longitude': ' 1234556',
                                             'latitude': ' 123456', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateAccuracyCode': 'E'}, {}))

    def test_coordinate_method_code_longer_than_maxlength_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateMethodCode': 'C3', 'longitude': ' 1234556',
                                             'latitude': ' 123456', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateAccuracyCode': 'E'}, {}))
        self.assertEqual(len(validator.errors.get('coordinateMethodCode')), 2)

    def test_coordinate_method_code_longer_than_maxlength_spaces_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateMethodCode': '  ', 'longitude': ' 1234556',
                                             'latitude': ' 123456', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateAccuracyCode': 'E'}, {}))
        self.assertEqual(len(validator.errors.get('coordinateMethodCode')), 1)
        self.assertIn('coordinateMethodCode', validator.errors.get('location')[0])

    def test_coordinate_method_code_null_pad_lat_long_not_null_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateMethodCode': ' ', 'longitude': ' 1234556',
                                             'latitude': ' 123456', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateAccuracyCode': 'E'}, {}))
        self.assertIn('coordinateMethodCode', validator.errors.get('location')[0])

    def test_coordinate_method_code_null_no_pad_lat_long_not_null_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateMethodCode': '', 'longitude': ' 1234556',
                                             'latitude': ' 123456', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateAccuracyCode': 'E'}, {}))
        self.assertIn('coordinateMethodCode', validator.errors.get('location')[0])

    def test_coordinate_method_code_null_no_pad_lat_not_null_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateMethodCode': '', 'longitude': '',
                                             'latitude': ' 123456', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateAccuracyCode': 'E'}, {}))
        self.assertIn('coordinateMethodCode', validator.errors.get('location')[0])

    def test_coordinate_method_code_null_no_pad_lat_not_null_long_pad_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateMethodCode': '', 'longitude': ' ',
                                             'latitude': ' 123456', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateAccuracyCode': 'E'}, {}))
        self.assertIn('coordinateMethodCode', validator.errors.get('location')[0])

    def test_coordinate_method_code_null_no_pad_long_not_null_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateMethodCode': '', 'longitude': ' 1234556',
                                             'latitude': '', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateAccuracyCode': 'E'}, {}))
        self.assertIn('coordinateMethodCode', validator.errors.get('location')[0])

    def test_coordinate_method_code_null_no_pad_long_not_null_lat_pad_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateMethodCode': '', 'longitude': ' 1234556',
                                             'latitude': ' ', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateAccuracyCode': 'E'}, {}))
        self.assertIn('coordinateMethodCode', validator.errors.get('location')[0])

    def test_coordinate_method_code_not_null_lat_long_null_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateMethodCode': 'C', 'longitude': '',
                                             'latitude': '', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateAccuracyCode': 'E'}, {}))
        self.assertIn('coordinateMethodCode', validator.errors.get('location')[0])

    def test_coordinate_method_code_not_null_lat_null_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateMethodCode': 'C', 'longitude': ' 1234556',
                                             'latitude': '', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateAccuracyCode': 'E'}, {}))
        self.assertIn('coordinateMethodCode', validator.errors.get('location')[0])

    def test_coordinate_method_code_not_null_long_null_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateMethodCode': 'C', 'longitude': '',
                                             'latitude': ' 123456', 'coordinateDatumCode': 'BARBADOS',
                                             'coordinateAccuracyCode': 'E'}, {}))
        self.assertIn('coordinateMethodCode', validator.errors.get('location')[0])


class ErrorValidatorCoordinateDatumCodeTestCase(TestCase):

    def test_coordinate_datum_code_char_in_ref_list_is_valid(self):
        self.assertTrue(validator.validate({'coordinateDatumCode': 'BARBADOS', 'longitude': ' 1234556',
                                            'latitude': ' 123456', 'coordinateMethodCode': 'C',
                                            'coordinateAccuracyCode': 'E'}, {}))

    def test_coordinate_datum_code_lower_char_in_ref_list_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateDatumCode': 'barbados', 'longitude': ' 1234556',
                                             'latitude': ' 123456', 'coordinateMethodCode': 'c',
                                             'coordinateAccuracyCode': 'E'}, {}))

    def test_coordinate_datum_code_longer_than_maxlength_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateDatumCode': 'BARBADOS9103', 'longitude': ' 1234556',
                                             'latitude': ' 123456', 'coordinateMethodCode': 'C3',
                                             'coordinateAccuracyCode': 'E'}, {}))
        self.assertEqual(len(validator.errors.get('coordinateDatumCode')), 2)

    def test_coordinate_datum_code_longer_than_maxlength_spaces_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateDatumCode': '             ', 'longitude': ' 1234556',
                                             'latitude': ' 123456', 'coordinateMethodCode': '  ',
                                             'coordinateAccuracyCode': 'E'}, {}))
        self.assertEqual(len(validator.errors.get('coordinateDatumCode')), 1)
        self.assertIn('coordinateDatumCode', validator.errors.get('location')[0])

    def test_coordinate_datum_code_null_pad_lat_long_not_null_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateDatumCode': ' ', 'longitude': ' 1234556',
                                             'latitude': ' 123456', 'coordinateMethodCode': 'C',
                                             'coordinateAccuracyCode': 'E'}, {}))
        self.assertIn('coordinateDatumCode', validator.errors.get('location')[0])

    def test_coordinate_datum_code_null_no_pad_lat_long_not_null_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateDatumCode': '', 'longitude': ' 1234556',
                                             'latitude': ' 123456', 'coordinateMethodCode': 'C',
                                             'coordinateAccuracyCode': 'E'}, {}))
        self.assertIn('coordinateDatumCode', validator.errors.get('location')[0])

    def test_coordinate_datum_code_null_no_pad_lat_not_null_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateDatumCode': '', 'longitude': '',
                                             'latitude': ' 123456', 'coordinateMethodCode': 'C',
                                             'coordinateAccuracyCode': 'E'}, {}))
        self.assertIn('coordinateDatumCode', validator.errors.get('location')[0])

    def test_coordinate_datum_code_null_no_pad_lat_not_null_long_pad_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateDatumCode': 'BARBADOS', 'longitude': ' ',
                                             'latitude': ' 123456', 'coordinateMethodCode': 'C',
                                             'coordinateAccuracyCode': 'E'}, {}))
        self.assertIn('coordinateDatumCode', validator.errors.get('location')[0])

    def test_coordinate_datum_code_null_no_pad_long_not_null_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateDatumCode': '', 'longitude': ' 1234556',
                                             'latitude': '', 'coordinateMethodCode': 'C',
                                             'coordinateAccuracyCode': 'E'}, {}))
        self.assertIn('coordinateDatumCode', validator.errors.get('location')[0])

    def test_coordinate_datum_code_null_no_pad_long_not_null_lat_pad_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateDatumCode': '', 'longitude': ' 1234556',
                                             'latitude': ' ', 'coordinateMethodCode': 'C',
                                             'coordinateAccuracyCode': 'E'}, {}))
        self.assertIn('coordinateDatumCode', validator.errors.get('location')[0])

    def test_coordinate_datum_code_not_null_lat_long_null_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateDatumCode': 'BARBADOS', 'longitude': '',
                                             'latitude': '', 'coordinateMethodCode': 'C',
                                             'coordinateAccuracyCode': 'E'}, {}))
        self.assertIn('coordinateDatumCode', validator.errors.get('location')[0])

    def test_coordinate_datum_code_not_null_lat_null_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateDatumCode': 'BARBADOS', 'longitude': ' 1234556',
                                             'latitude': '', 'coordinateMethodCode': 'C',
                                             'coordinateAccuracyCode': 'E'}, {}))
        self.assertIn('coordinateDatumCode', validator.errors.get('location')[0])

    def test_coordinate_datum_code_not_null_long_null_is_invalid(self):
        self.assertFalse(validator.validate({'coordinateDatumCode': 'BARBADOS', 'longitude': '',
                                             'latitude': ' 123456', 'coordinateMethodCode': 'C',
                                             'coordinateAccuracyCode': 'E'}, {}))
        self.assertIn('coordinateDatumCode', validator.errors.get('location')[0])


class AltitudeErrorValidationsTestCase(TestCase):

    def test_optional(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitude': ' '}, {})
        self.assertNotIn('altitude', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678'}, {})
        self.assertNotIn('altitude', validator.errors)

    def test_reciprocal_dependency(self):
        validator.validate(
            {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitude': '12345', 'altitudeAccuracyValue': 'a',
             'altitudeMethodCode': 'A', 'altitudeDatumCode': 'BBB'}, {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('altitude', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitudeAccuracyValue': ' '},
                           {'altitude': '12345', 'altitudeAccuracyValue': '1', 'altitudeMethodCode': 'A',
                            'altitudeDatumCode': 'BBB'})
        self.assertIn('altitude', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitudeMethodCode': ' '},
                           {'altitude': '12345', 'altitudeAccuracyValue': '1', 'altitudeMethodCode': 'A',
                            'altitudeDatumCode': 'BBB'})
        self.assertIn('altitude', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitudeDatumCode': ' '},
                           {'altitude': '12345', 'altitudeAccuracyValue': '1', 'altitudeMethodCode': 'A',
                            'altitudeDatumCode': 'BBB'})
        self.assertIn('altitude', validator.errors)


    def test_max_length(self):
        validator.validate(
            {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitude': '12345', 'altitudeAccuracyValue': '1',
             'altitudeMethodCode': 'A', 'altitudeDatumCode': 'BBB'}, {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('altitude', validator.errors)

        validator.validate(
            {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitude': '123456789', 'altitudeAccuracyValue': '1',
             'altitudeMethodCode': 'A', 'altitudeDatumCode': 'BBB'},
            {'agencyCode': 'USGS ', 'siteNumber': '12345678', })
        self.assertIn('altitude', validator.errors)

    def test_numeric(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitude': '12345'},
                           {'altitude': '1234', 'altitudeAccuracyValue': '1', 'altitudeMethodCode': 'A',
                            'altitudeDatumCode': 'BBB'})
        self.assertNotIn('altitude', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitude': '-12345'},
                           {'altitude': '1234', 'altitudeAccuracyValue': '1', 'altitudeMethodCode': 'A',
                            'altitudeDatumCode': 'BBB'})
        self.assertNotIn('altitude', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitude': '12345.1'},
                           {'altitude': '1234', 'altitudeAccuracyValue': '1', 'altitudeMethodCode': 'A',
                            'altitudeDatumCode': 'BBB'})
        self.assertNotIn('altitude', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitude': '-12A'},
                           {'altitude': '1234', 'altitudeAccuracyValue': '1', 'altitudeMethodCode': 'A',
                            'altitudeDatumCode': 'BBB'})
        self.assertIn('altitude', validator.errors)

    def test_two_decimal_precison(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitude': '12345.23'},
                           {'altitude': '1234', 'altitudeAccuracyValue': '1', 'altitudeMethodCode': 'A',
                            'altitudeDatumCode': 'BBB'})
        self.assertNotIn('altitude', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitude': '12345.233'},
                           {'altitude': '1234', 'altitudeAccuracyValue': '1', 'altitudeMethodCode': 'A',
                            'altitudeDatumCode': 'BBB'})
        self.assertIn('altitude', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitude': '-1234.23'},
                           {'altitude': '1234', 'altitudeAccuracyValue': '1', 'altitudeMethodCode': 'A',
                            'altitudeDatumCode': 'BBB'})
        self.assertNotIn('altitude', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitude': '-1234.233'},
                           {'altitude': '1234', 'altitudeAccuracyValue': '1', 'altitudeMethodCode': 'A',
                            'altitudeDatumCode': 'BBB'})
        self.assertIn('altitude', validator.errors)


class AltitudeDatumCodeTestCase(TestCase):

    def test_optional(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678'}, )
        self.assertNotIn('altitudeDatumCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitudeDatumCode': '   '}, )
        self.assertNotIn('altitudeDatumCode', validator.errors)


    def test_in_reference_list(self):
        validator.validate(
            {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitude': '12345', 'altitudeAccuracyValue': '1',
             'altitudeMethodCode': 'A', 'altitudeDatumCode': 'BARGECANAL'},
            {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('altitudeDatumCode', validator.errors)

    def test_not_in_reference_list(self):
        validator.validate(
            {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitude': '12345', 'altitudeAccuracyValue': '1',
             'altitudeMethodCode': 'A', 'altitudeDatumCode': 'NAVD10'},
            {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('altitudeDatumCode', validator.errors)


class AltitudeMethodCodeTestCase(TestCase):

    def test_optional(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678'}, )
        self.assertNotIn('altitudeMethodCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitudeMethodCode': ' '}, )
        self.assertNotIn('altitudeMethodCode', validator.errors)


    def test_in_reference_list(self):
        validator.validate(
            {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitude': '12345', 'altitudeAccuracyValue': '1',
             'altitudeMethodCode': 'D', 'altitudeDatumCode': 'BARGECANAL'},
            {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('altitudeMethodCode', validator.errors)

    def test_not_in_reference_list(self):
        validator.validate(
            {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitude': '12345', 'altitudeAccuracyValue': '1',
             'altitudeMethodCode': 'B', 'altitudeDatumCode': 'BARGECANAL'},
            {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('altitudeMethodCode', validator.errors)


class AltitudeAccuracyValueTestCase(TestCase):

    def test_optional(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678'}, )
        self.assertNotIn('altitudeAccuracyValue', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitudeAccuracyValue': ' '}, )
        self.assertNotIn('altitudeAccuracyValue', validator.errors)

    def test_max_length(self):
        validator.validate(
            {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitude': '12345', 'altitudeAccuracyValue': '123',
             'altitudeMethodCode': 'D', 'altitudeDatumCode': 'BARGECANAL'},
            {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('altitudeAccuracyValue', validator.errors)

        validator.validate(
            {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitude': '12345', 'altitudeAccuracyValue': '1234',
             'altitudeMethodCode': 'D', 'altitudeDatumCode': 'BARGECANAL'},
            {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('altitudeAccuracyValue', validator.errors)

    def test_numeric(self):
        validator.validate(
            {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitude': '12345', 'altitudeAccuracyValue': '.3',
             'altitudeMethodCode': 'D', 'altitudeDatumCode': 'BARGECANAL'},
            {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('altitudeAccuracyValue', validator.errors)

        validator.validate(
            {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitude': '12345', 'altitudeAccuracyValue': '-.3',
             'altitudeMethodCode': 'D', 'altitudeDatumCode': 'BARGECANAL'},
            {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('altitudeAccuracyValue', validator.errors)

        validator.validate(
            {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'altitude': '12345', 'altitudeAccuracyValue': 'A.3',
             'altitudeMethodCode': 'D', 'altitudeDatumCode': 'BARGECANAL'},
            {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('altitudeAccuracyValue', validator.errors)


class NationalAquiferCodeTestCase(TestCase):

    def test_optional(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678'}, )
        self.assertNotIn('nationalAquiferCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'nationalAquiferCode': ' '}, )
        self.assertNotIn('nationalAquiferCode', validator.errors)

    def test_max_length(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'nationalAquiferCode': 'ABCDEFGHIJ'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('nationalAquiferCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'nationalAquiferCode': 'ABCDEFGHIJK'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('nationalAquiferCode', validator.errors)

    def test_aquifer_in_country_state(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'nationalAquiferCode': 'N100AKUNCD'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'stateFipsCode': 'US',
                            'stateFipsCode': '02'})
        self.assertNotIn('nationalAquiferCode', validator.errors)

    def test_aquifer_not_in_country_state(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'nationalAquiferCode': 'N100ALLUVL'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US',
                            'stateFipsCode': '02'})
        self.assertIn('nationalAquiferCode', validator.errors)

    def test_aquifer_country_state_not_in_ref_list(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'nationalAquiferCode': 'N100AKUNCD'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'AZ',
                            'stateFipsCode': '02'})
        self.assertIn('nationalAquiferCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'nationalAquiferCode': 'N100AKUNCD'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'RM',
                            'stateFipsCode': '02'})
        self.assertIn('nationalAquiferCode', validator.errors)

    def test_invalid_non_null_code_site_type(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'nationalAquiferCode': 'N100AKUNCD'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteTypeCode': 'ST-CA'})
        self.assertIn('nationalAquiferCode', validator.errors['siteTypeCode'][0])

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'nationalAquiferCode': ' '},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteTypeCode': 'ST-CA'})
        self.assertNotIn('siteTypeCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'nationalAquiferCode': 'N100AKUNCD'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteTypeCode': 'FA-CI'})
        self.assertNotIn('siteTypeCode', validator.errors)


class AquiferCodeTestCase(TestCase):

    def test_optional(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678'}, )
        self.assertNotIn('aquiferCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'aquiferCode': ' '}, )
        self.assertNotIn('aquiferCode', validator.errors)

    def test_max_length(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'aquiferCode': '122CTHLS'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('aquiferCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'aquiferCode': '122CTHLSS'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('aquiferCode', validator.errors)

    def test_aquifer_in_country_state(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'aquiferCode': '400PCMB'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US',
                            'stateFipsCode': '01'})
        self.assertNotIn('aquiferCode', validator.errors)

    def test_aquifer_not_in_country_state(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'aquiferCode': '400PCMB'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US',
                            'stateFipsCode': '02'})
        self.assertIn('aquiferCode', validator.errors)

    def test_aquifer_for_country_state_not_in_ref_list(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'aquiferCode': '400PCMB'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US',
                            'stateFipsCode': '80'})
        self.assertIn('aquiferCode', validator.errors)

    def test_invalid_non_null_code_for_site_type(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'aquiferCode': '400PCMB'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US', 'stateFipsCode': '01',
                            'siteTypeCode': 'ST-CA'})
        self.assertIn('aquiferCode', validator.errors['siteTypeCode'][0])

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'aquiferCode': ' '},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US', 'stateFipsCode': '01',
                            'siteTypeCode': 'ST-CA'})
        self.assertNotIn('siteTypeCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'aquiferCode': '400PCMB'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US', 'stateFipsCode': '01',
                            'siteTypeCode': 'AG'})
        self.assertNotIn('siteTypeCode', validator.errors)


class AquiferTypeCodeTestCase(TestCase):

    def test_optional(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678'}, )
        self.assertNotIn('aquiferTypeCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'aquiferTypeCode': ' '}, )
        self.assertNotIn('aquiferTypeCode', validator.errors)

    def test_max_length(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'aquiferTypeCode': 'U'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('aquiferTypeCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'aquiferTypeCode': 'UU'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('aquiferTypeCode', validator.errors)

    def test_aquifer_type_in_reference_list(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'aquiferTypeCode': 'U'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('aquiferTypeCode', validator.errors)

    def test_aquifer_type_not_in_reference_list(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'aquiferTypeCode': 'A'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('aquiferTypeCode', validator.errors)

    def test_invalid_non_null_code_for_site_type(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'aquiferTypeCode': ' '},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteTypeCode': 'ST-CA'})
        self.assertNotIn('siteTypeCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'aquiferTypeCode': 'U'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteTypeCode': 'ST-CA'})
        self.assertIn('aquiferTypeCode', validator.errors['siteTypeCode'][0])

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'aquiferTypeCode': 'U'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteTypeCode': 'AG'})
        self.assertNotIn('siteTypeCode', validator.errors)


class AgencyUseCodeTestCase(TestCase):

    def test_optional(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678'}, )
        self.assertNotIn('agencyUseCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'agencyUseCode': ' '}, )
        self.assertNotIn('agencyUseCode', validator.errors)

    def test_max_length(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'agencyUseCode': 'R'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('agencyUseCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'agencyUseCode': 'RR'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('agencyUseCode', validator.errors)

    def test_in_reference_list(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'agencyUseCode': 'R'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('agencyUseCode', validator.errors)

    def test_not_in_reference_list(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'agencyUseCode': 'U'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('agencyUseCode', validator.errors)


class DataReliabilityCodeTestCase(TestCase):

    def test_optional_for_site_type_code(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteTypeCode': 'SB-CV'}, )
        self.assertNotIn('dataReliabilityCode', validator.errors['siteTypeCode'][0])

        validator.validate(
            {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'dataReliabilityCode': ' ', 'siteTypeCode': 'SB-CV'}, )
        self.assertNotIn('dataReliabilityCode', validator.errors['siteTypeCode'][0])

    def test_not_optional_for_site_type_code(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteTypeCode': 'SP'}, )
        self.assertIn('dataReliabilityCode', validator.errors['siteTypeCode'][0])

        validator.validate(
            {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'dataReliabilityCode': ' ', 'siteTypeCode': 'SP'}, )
        self.assertIn('dataReliabilityCode', validator.errors['siteTypeCode'][0])

    def test_max_length(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'dataReliabilityCode': 'L'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('dataReliabilityCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'dataReliabilityCode': 'LL'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('dataReliabilityCode', validator.errors)

    def test_in_reference_list(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'dataReliabilityCode': 'L'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('dataReliabilityCode', validator.errors)

    def test_not_in_reference_list(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'dataReliabilityCode': 'A'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('dataReliabilityCode', validator.errors)


class DistrictCodeTestCase(TestCase):

    def test_required(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'districtCode': '55'}, )
        self.assertNotIn('districtCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'districtCode': ' '}, )
        self.assertIn('districtCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678'}, )
        self.assertIn('districtCode', validator.errors)

    def test_max_length(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'districtCode': '122'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('districtCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'districtCode': '1222'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('districtCode', validator.errors)

    def test_in_reference_list(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'districtCode': '55'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('districtCode', validator.errors)

    def test_not_in_reference_list(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'districtCode': '90'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('districtCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'districtCode': '1'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('districtCode', validator.errors)


class CountryCodeTestCase(TestCase):

    def test_required(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US'}, )
        self.assertNotIn('countryCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': ' '}, )
        self.assertIn('countryCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678'}, )
        self.assertIn('countryCode', validator.errors)

    def test_max_length(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('countryCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'USS'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('countryCode', validator.errors)

    def test_in_reference_list(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('countryCode', validator.errors)

    def test_not_in_reference_list(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'ZZ'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('countryCode', validator.errors)


class StateFipsCode(TestCase):

    def test_required(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'stateFipsCode': 'US'}, )
        self.assertNotIn('stateFipsCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'stateFipsCode': ' '}, )
        self.assertIn('stateFipsCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678'}, )
        self.assertIn('stateFipsCode', validator.errors)

    def test_max_length(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'stateFipsCode': '55'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('stateFips', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'stateFipsCode': '055'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('stateFipsCode', validator.errors)

    def test_in_reference_list(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'stateFipsCode': '55'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US'})
        self.assertNotIn('stateFipsCode', validator.errors)

    def test_not_in_reference_list(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'stateFipsCode': '80'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US'})
        self.assertIn('stateFipsCode', validator.errors)

    def test_latitude_in_us_state_range(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'latitude': ' 430000'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'stateFipsCode': '55',
                            'countryCode': 'US'})
        self.assertNotIn('latitude', validator.errors)

    def test_latitude_not_in_us_state_range(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'latitude': ' 420000'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'stateFipsCode': '55',
                            'countryCode': 'US'})
        self.assertIn('latitude', validator.errors)

    def test_longitude_in_us_state_range(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'longitude': ' 0870000'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'stateFipsCode': '55',
                            'countryCode': 'US'})
        self.assertNotIn('longitude', validator.errors)

    def test_longitude_not_in_us_state_range(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'longitude': ' 0930000'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'stateFipsCode': '55',
                            'countryCode': 'US'})
        self.assertIn('longitude', validator.errors)


class CountyCodeTestCase(TestCase):

    def test_required(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US', 'stateFipsCode': '55',
                            'countyCode': '003'}, )
        self.assertNotIn('countyCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US', 'stateFipsCode': '55',
                            'countyCode': ''}, )
        self.assertIn('countyCode', validator.errors)

        validator.validate(
            {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US', 'stateFipsCode': '55'}, )
        self.assertIn('countyCode', validator.errors)

    def test_max_length(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countyCode': '003'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US', 'stateFipsCode': '55',
                            'countyCode': '005'})
        self.assertNotIn('countyCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countyCode': '0003'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US', 'stateFipsCode': '55',
                            'countyCode': '005'})
        self.assertIn('countyCode', validator.errors)

    def test_in_reference_list(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countyCode': '003'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US', 'stateFipsCode': '55',
                            'countyCode': '005'})
        self.assertNotIn('countyCode', validator.errors)

    def test_not_in_reference_list(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countyCode': '002'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US', 'stateFipsCode': '55',
                            'countyCode': '005'})
        self.assertIn('countyCode', validator.errors)


class MinorCivilDivisionCodeTestCase(TestCase):

    def test_optional(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US', 'stateFipsCode': '55',
                            'countyCode': '005'}, )
        self.assertNotIn('minorCivilDivisionCode', validator.errors)

    def test_null_mcd_code(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US', 'stateFipsCode': '55',
                            'countyCode': '001'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'minorCivilDivisionCode': None})
        self.assertNotIn('minorCivilDivisionCode', validator.errors)

        validator.validate(
            {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'minorCivilDivisionCode': None, 'countryCode': 'US',
             'stateFipsCode': '55',
             'countyCode': '001'}, {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('minorCivilDivisionCode', validator.errors)

    def test_ref_in_list(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'minorCivilDivisionCode': '00275'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US', 'stateFipsCode': '55',
                            'countyCode': '001'})
        self.assertNotIn('minorCivilDivisionCode', validator.errors)

    def test_ref_not_in_list(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'minorCivilDivisionCode': '00277'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US', 'stateFipsCode': '55',
                            'countyCode': '001'})
        self.assertIn('minorCivilDivisionCode', validator.errors)

    def test_country_state_county_not_in_list(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'minorCivilDivisionCode': '00277'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'CN', 'stateFipsCode': '55',
                            'countyCode': '001'})
        self.assertIn('minorCivilDivisionCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'minorCivilDivisionCode': '00277'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US', 'stateFipsCode': '85',
                            'countyCode': '001'})
        self.assertIn('minorCivilDivisionCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'minorCivilDivisionCode': '00277'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US', 'stateFipsCode': '55',
                            'countyCode': '002'})
        self.assertIn('minorCivilDivisionCode', validator.errors)


class HydrologicUnitCodeTestCase(TestCase):

    def test_optional(self):
        validator.validate(
            {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US', 'stateFipsCode': '55'}, )
        self.assertNotIn('hydrologicUnitCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US', 'stateFipsCode': '55',
                            'hydrologicUnitCode': '  '}, )
        self.assertNotIn('hydrologicUnitCode', validator.errors)

    def test_valid_huc_in_ref_list(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'hydrologicUnitCode': '07'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US',
                            'stateFipsCode': '55'})
        self.assertNotIn('hydrologicUnitCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'hydrologicUnitCode': '0701'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US',
                            'stateFipsCode': '27'})
        self.assertNotIn('hydrologicUnitCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'hydrologicUnitCode': '070102'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US',
                            'stateFipsCode': '27'})
        self.assertNotIn('hydrologicUnitCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'hydrologicUnitCode': '07010206'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US',
                            'stateFipsCode': '27'})
        self.assertNotIn('hydrologicUnitCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'hydrologicUnitCode': '0701020609'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US',
                            'stateFipsCode': '27'})
        self.assertNotIn('hydrologicUnitCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'hydrologicUnitCode': '070102060903'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US',
                            'stateFipsCode': '27'})
        self.assertNotIn('hydrologicUnitCode', validator.errors)

    def test_valid_huc_not_in_ref_list(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'hydrologicUnitCode': '08'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US',
                            'stateFipsCode': '55'})
        self.assertIn('hydrologicUnitCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'hydrologicUnitCode': '0708'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US',
                            'stateFipsCode': '55'})
        self.assertIn('hydrologicUnitCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'hydrologicUnitCode': '070103'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US',
                            'stateFipsCode': '55'})
        self.assertIn('hydrologicUnitCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'hydrologicUnitCode': '07010207'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US',
                            'stateFipsCode': '55'})
        self.assertIn('hydrologicUnitCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'hydrologicUnitCode': '0701020608'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US',
                            'stateFipsCode': '55'})
        self.assertIn('hydrologicUnitCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'hydrologicUnitCode': '070102060904'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US',
                            'stateFipsCode': '55'})
        self.assertIn('hydrologicUnitCode', validator.errors)

    def test_special_value(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'hydrologicUnitCode': '99999999'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'countryCode': 'US',
                            'stateFipsCode': '55'})
        self.assertNotIn('hydrologicUnitCode', validator.errors)


class BasinCodeTestCase(TestCase):

    def test_optional(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678'}, )
        self.assertNotIn('basinCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'basinCode': '  '}, )
        self.assertNotIn('basinCode', validator.errors)

    def test_max_length(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'basinCode': 'AA'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('basinCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'basinCode': 'AAA'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('basinCode', validator.errors)


class MapNameTestCase(TestCase):
    def test_optional(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678'}, )
        self.assertNotIn('mapName', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'mapName': '  '}, )
        self.assertNotIn('mapName', validator.errors)

    def test_max_length(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'mapName': '12345678901234567890'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('mapName', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'mapName': '123456789012345678901'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('mapName', validator.errors)


class MapScaleTestCase(TestCase):

    def test_optional(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678'}, )
        self.assertNotIn('mapScale', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'mapScale': '  '}, )
        self.assertNotIn('mapScale', validator.errors)

    def test_max_length(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'mapScale': '1234567'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('mapScale', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'mapScale': '12345678'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('mapScale', validator.errors)

    def test_invalid_chars(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'mapScale': ' 123456'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('mapScale', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'mapScale': 'A123456'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('mapScale', validator.errors)


class NationalWaterUseCodeTestCase(TestCase):

    def test_optional(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678'}, )
        self.assertNotIn('nationalWaterUseCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'nationalWaterUse': ' '}, )
        self.assertNotIn('nationalWaterUseCode', validator.errors)

    def test_valid_code_for_site_type(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'nationalWaterUseCode': 'DO'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteTypeCode': 'FA-CI'})
        self.assertNotIn('nationalWaterUseCode', validator.errors)

    def test_invalid_code_for_site_type(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'nationalWaterUseCode': 'DO'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteTypeCode': 'FA-FON'})
        self.assertIn('nationalWaterUseCode', validator.errors)

    def test_invalid_non_null_code_for_site_type(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'nationalWaterUseCode': 'DO'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteTypeCode': 'FA-QC'})
        self.assertIn('nationalWaterUseCode', validator.errors['siteTypeCode'][0])

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'nationalWaterUseCode': ' '},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteTypeCode': 'FA-QC'})
        self.assertNotIn('siteTypeCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'nationalWaterUseCode': 'DO'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteTypeCode': 'AG'})
        self.assertNotIn('siteTypeCode', validator.errors)


class PrimaryUseOfSiteTestCase(TestCase):

    def test_optional(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678'}, )
        self.assertNotIn('primaryUseOfSite', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'primaryUseOfSite': ' '}, )
        self.assertNotIn('primaryUseOfSite', validator.errors)

    def test_max_length(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'primaryUseOfSite': 'A'}, )
        self.assertNotIn('primaryUseOfSite', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'primaryUseOfSite': 'AA'}, )
        self.assertIn('primaryUseOfSite', validator.errors)

    def test_in_reference(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'primaryUseOfSite': 'A'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('primaryUseOfSite', validator.errors)

    def test_not_in_reference(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'primaryUseOfSite': 'B'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('primaryUseOfSite', validator.errors)

    def test_invalid_non_null_code_for_site_type(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'primaryUseOfSite': 'A'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteTypeCode': 'AW'})
        self.assertIn('primaryUseOfSite', validator.errors['siteTypeCode'][0])

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'primaryUseOfSite': ' '},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteTypeCode': 'AW'})
        self.assertNotIn('siteTypeCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'primaryUseOfSite': ' '},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteTypeCode': 'AG'})
        self.assertNotIn('siteTypeCode', validator.errors)

    def test_invalid_null_code_for_site_type(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'primaryUseOfSite': ' '},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteTypeCode': 'GW'})
        self.assertIn('primaryUseOfSite', validator.errors['siteTypeCode'][0])

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'primaryUseOfSite': 'A'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteTypeCode': 'GW'})
        self.assertNotIn('siteTypeCode', validator.errors)


class SecondaryUseOfSite(TestCase):

    def test_optional(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678'}, )
        self.assertNotIn('secondaryUseOfSite', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'secondaryUseOfSite': ' '}, )
        self.assertNotIn('secondaryUseOfSite', validator.errors)

    def test_max_length(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'secondaryUseOfSite': 'C'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'primaryUseOfSite': 'A'})
        self.assertNotIn('secondaryUseOfSite', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'secondaryUseOfSite': 'CC'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'primaryUseOfSite': 'A'})
        self.assertIn('secondaryUseOfSite', validator.errors)

    def test_in_reference(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'secondaryUseOfSite': 'C'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'primaryUseOfSite': 'A'})
        self.assertNotIn('secondaryUseOfSite', validator.errors)

    def test_not_in_reference(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'secondaryUseOfSite': 'B'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'primaryUseOfSite': 'A'})
        self.assertIn('secondaryUseOfSite', validator.errors)

    def test_secondary_without_primary(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'secondaryUseOfSite': 'C'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('secondaryUseOfSite', validator.errors)

    def test_invalid_non_null_code_for_site_type(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'secondaryUseOfSite': 'C'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteTypeCode': 'AW'})
        self.assertIn('secondaryUseOfSite', validator.errors['siteTypeCode'][0])

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'secondaryUseOfSite': ' '},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteTypeCode': 'AW'})
        self.assertNotIn('siteTypeCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'secondaryUseOfSite': ' '},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteTypeCode': 'AG'})
        self.assertNotIn('siteTypeCode', validator.errors)


class TertiaryUseOfSiteCode(TestCase):

    def test_optional(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678'}, )
        self.assertNotIn('tertiaryUseOfSiteCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'tertiaryUseOfSiteCode': ' '}, )
        self.assertNotIn('tertiaryUseOfSiteCode', validator.errors)

    def test_max_length(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'tertiaryUseOfSiteCode': 'Z'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'primaryUseOfSite': 'A',
                            'secondaryUseOfSite': 'C'})
        self.assertNotIn('tertiaryUseOfSiteCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'tertiaryUseOfSiteCode': 'ZZ'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'primaryUseOfSite': 'A',
                            'secondaryUseOfSite': 'C'})
        self.assertIn('tertiaryUseOfSiteCode', validator.errors)

    def test_in_reference(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'tertiaryUseOfSiteCode': 'Z'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'primaryUseOfSite': 'A',
                            'secondaryUseOfSite': 'C'})
        self.assertNotIn('tertiaryUseOfSiteCode', validator.errors)

    def test_not_in_reference(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'tertiaryUseOfSiteCode': 'B'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'primaryUseOfSite': 'A',
                            'secondaryUseOfSite': 'C'})
        self.assertIn('tertiaryUseOfSiteCode', validator.errors)

    def test_tertiary_without_secondary(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'tertiaryUseOfSiteCode': 'B'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('tertiaryUseOfSiteCode', validator.errors)

    def test_invalid_non_null_code_for_site_type(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'tertiaryUseOfSiteCode': 'C'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteTypeCode': 'AW'})
        self.assertIn('tertiaryUseOfSiteCode', validator.errors['siteTypeCode'][0])

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'tertiaryUseOfSiteCode': ' '},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteTypeCode': 'AW'})
        self.assertNotIn('siteTypeCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'tertiaryUseOfSiteCode': ' '},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteTypeCode': 'AG'})
        self.assertNotIn('siteTypeCode', validator.errors)


class PrimaryUseOfWaterCodeTestCase(TestCase):

    def test_optional(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678'}, )
        self.assertNotIn('primaryUseOfWaterCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'primaryUseOfWaterCode': ' '}, )
        self.assertNotIn('primaryUseOfWaterCode', validator.errors)

    def test_max_length(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'primaryUseOfWaterCode': 'A'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('primaryUseOfWaterCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'primaryUseOfWaterCode': 'AA'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('primaryUseOfWaterCode', validator.errors)

    def test_valid_ref_list(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'primaryUseOfWaterCode': 'A'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('primaryUseOfWaterCode', validator.errors)

    def test_invalid_ref_list(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'primaryUseOfWaterCode': 'G'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('primaryUseOfWaterCode', validator.errors)


class SecondaryUseOfWaterCodeTestCase(TestCase):

    def test_optional(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678'}, )
        self.assertNotIn('secondaryUseOfWaterCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'secondaryUseOfWaterCode': ' '}, )
        self.assertNotIn('secondaryUseOfWaterCode', validator.errors)

    def test_max_length(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'secondaryUseOfWaterCode': 'B'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'primaryUseOfWaterCode': 'A'})
        self.assertNotIn('secondaryUseOfWaterCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'secondaryUseOfWaterCode': 'BB'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'primaryUseOfWaterCode': 'A'})
        self.assertIn('secondaryUseOfWaterCode', validator.errors)

    def test_in_ref_list(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'secondaryUseOfWaterCode': 'B'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'primaryUseOfWaterCode': 'A'})
        self.assertNotIn('secondaryUseOfWaterCode', validator.errors)

    def test_not_in_ref_list(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'secondaryUseOfWaterCode': 'G'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'primaryUseOfWaterCode': 'A'})
        self.assertIn('secondaryUseOfWaterCode', validator.errors)

    def test_null_primary_with_secondary(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'secondaryUseOfWaterCode': 'B'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('secondaryUseOfWaterCode', validator.errors)


class TertiaryUseOfWaterCodeTestCase(TestCase):

    def test_optional(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678'}, )
        self.assertNotIn('tertiaryUseOfWaterCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'tertiaryUseOfWaterCode': ' '}, )
        self.assertNotIn('tertiaryUseOfWaterCode', validator.errors)

    def test_max_length(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'tertiaryUseOfWaterCode': 'U'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'primaryUseOfWaterCode': 'A',
                            'secondaryUseOfWaterCode': 'B'})
        self.assertNotIn('tertiaryUseOfWaterCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'tertiaryUseOfWaterCode': 'UU'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'primaryUseOfWaterCode': 'A',
                            'secondaryUseOfWaterCode': 'B'})
        self.assertIn('tertiaryUseOfWaterCode', validator.errors)

    def test_in_ref_list(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'tertiaryUseOfWaterCode': 'U'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'primaryUseOfWaterCode': 'A',
                            'secondaryUseOfWaterCode': 'B'})
        self.assertNotIn('tertiaryUseOfWaterCode', validator.errors)

    def test_not_in_ref_list(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'tertiaryUseOfWaterCode': 'V'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'primaryUseOfWaterCode': 'A',
                            'secondaryUseOfWaterCode': 'B'})
        self.assertIn('tertiaryUseOfWaterCode', validator.errors)

    def test_null_secondary_with_tertiary(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'tertiaryUseOfWaterCode': 'V'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('tertiaryUseOfWaterCode', validator.errors)


class TopographicCodeTestCase(TestCase):

    def test_optional(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678'}, )
        self.assertNotIn('topographicCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'topographicCode': ' '}, )
        self.assertNotIn('topographicCode', validator.errors)

    def test_max_length(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'topographicCode': 'A'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('topographicCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'topographicCode': 'AA'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('topographicCode', validator.errors)

    def test_in_ref_list(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'topographicCode': 'A'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('topographicCode', validator.errors)

    def test_not_in_ref_list(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'topographicCode': 'Z'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('topographicCode', validator.errors)


class InstrumentsCode(TestCase):

    def test_optional(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678'}, )
        self.assertNotIn('instrumentsCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'instrumentsCode': '   '}, )
        self.assertNotIn('instrumentsCode', validator.errors)

    def test_max_length(self):
        validator.validate(
            {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'instrumentsCode': 'YNYNYNYNYNYNYNYNYNYNYNYNYNYNYN'},
            {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('instrumentsCode', validator.errors)

        validator.validate(
            {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'instrumentsCode': 'YNYNYNYNYNYNYNYNYNYNYNYNYNYNYNY'},
            {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('instrumentsCode', validator.errors)

    def test_invalid_characters(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'instrumentsCode': '  YYYYNNN'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('instrumentsCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'instrumentsCode': '  YYYXNNN'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('instrumentsCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'instrumentsCode': '  YYY*NNN'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('instrumentsCode', validator.errors)


class DataTypesCode(TestCase):

    def test_optional(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678'}, )
        self.assertNotIn('dataTypesCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'dataTypesCode': '   '}, )
        self.assertNotIn('dataTypesCode', validator.errors)

    def test_max_length(self):
        validator.validate(
            {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'dataTypesCode': 'AION AION AION AION AION AION '},
            {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('dataTypesCode', validator.errors)

        validator.validate(
            {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'dataTypesCode': 'AION AION AION AION AION AION A'},
            {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('dataTypesCode', validator.errors)

    def test_invalid_characters(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'dataTypesCode': '  AIONAOIN'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('dataTypesCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'dataTypesCode': '  AIOXAOIN'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('dataTypesCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'dataTypesCode': '  AION*AOIN'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('dataTypesCode', validator.errors)


class ContributingDrainageAreaTestCase(TestCase):

    def test_optional(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678'}, )
        self.assertNotIn('contributingDrainageArea', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'contributingDrainageArea': '   '}, )
        self.assertNotIn('contributingDrainageArea', validator.errors)

    def test_max_length(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'contributingDrainageArea': '12345678'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'drainageArea': '99999999'})
        self.assertNotIn('contributingDrainageArea', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'contributingDrainageArea': '123456789'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'drainageArea': '99999999'})
        self.assertIn('contributingDrainageArea', validator.errors)

    def test_positive_numeric(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'contributingDrainageArea': '12345678'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'drainageArea': '99999999'})
        self.assertNotIn('contributingDrainageArea', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'contributingDrainageArea': '123.4567'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'drainageArea': '99999999'})
        self.assertNotIn('contributingDrainageArea', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'contributingDrainageArea': '-1234567'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'drainageArea': '99999999'})
        self.assertIn('contributingDrainageArea', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'contributingDrainageArea': '123A567'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'drainageArea': '99999999'})
        self.assertIn('contributingDrainageArea', validator.errors)

    def test_missing_drainage_area(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'contributingDrainageArea': '123A567'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('contributingDrainageArea', validator.errors)

    def test_cannot_be_larger_than_drainage_area(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'contributingDrainageArea': '100'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'drainageArea': '101'})
        self.assertNotIn('drainageArea', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'contributingDrainageArea': '100'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'drainageArea': '100'})
        self.assertNotIn('drainageArea', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'contributingDrainageArea': '100'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'drainageArea': '99'})
        self.assertIn('drainageArea', validator.errors)

    def test_invalid_non_null_code_for_site_type(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'contributingDrainageArea': '123.4567'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'contributingDrainageArea': '99999999',
                            'siteTypeCode': 'FA-DV'})
        self.assertIn('contributingDrainageArea', validator.errors['siteTypeCode'][0])

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'contributingDrainageArea': ''},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'contributingDrainageArea': '',
                            'siteTypeCode': 'FA-DV'})
        self.assertNotIn('siteTypeCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'contributingDrainageArea': ''},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'contributingDrainageArea': '',
                            'siteTypeCode': 'ST'})
        self.assertNotIn('siteTypeCode', validator.errors)


class DrainageAreaTestCase(TestCase):

    def test_optional(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678'}, )
        self.assertNotIn('drainageArea', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'drainageArea': '   '}, )
        self.assertNotIn('drainageArea', validator.errors)

    def test_max_length(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'drainageArea': '12345678'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('drainageArea', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'drainageArea': '123456789'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('drainageArea', validator.errors)

    def test_positive_numeric(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'drainageArea': '12345678'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('drainageArea', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'drainageArea': '-2345678'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('drainageArea', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'drainageArea': '123A5678'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('drainageArea', validator.errors)

    def test_invalid_non_null_code_for_site_type(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'drainageArea': '99999999'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'drainageArea': '99999999',
                            'siteTypeCode': 'FA-DV'})
        self.assertIn('drainageArea', validator.errors['siteTypeCode'][0])

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'drainageArea': '', },
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'drainageArea': '',
                            'siteTypeCode': 'FA-DV'})
        self.assertNotIn('siteTypeCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'drainageArea': ''},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'drainageArea': '', 'siteTypeCode': 'ST'})
        self.assertNotIn('siteTypeCode', validator.errors)


class FirstConstructionDateTestCase(TestCase):

    def test_optional(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678'}, )
        self.assertNotIn('firstConstructionDate', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'firstConstructionDate': '   '}, )
        self.assertNotIn('firstConstructionDate', validator.errors)

    def test_max_length(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'firstConstructionDate': '19921112'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('firstConstructionDate', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'firstConstructionDate': '199211121'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('firstConstructionDate', validator.errors)

    def test_valid_date(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'firstConstructionDate': '19921112'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('firstConstructionDate', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'firstConstructionDate': '1992111'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('firstConstructionDate', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'firstConstructionDate': '19921330'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('firstConstructionDate', validator.errors)

    def test_partial_dates(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'firstConstructionDate': '1992'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('firstConstructionDate', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'firstConstructionDate': '199210'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('firstConstructionDate', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'firstConstructionDate': '1992101'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('firstConstructionDate', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'firstConstructionDate': '19921'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('firstConstructionDate', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'firstConstructionDate': '199'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('firstConstructionDate', validator.errors)

    def test_construction_date_before_inventory_date(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'firstConstructionDate': '19920315'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteEstablishmentDate': '19920320'})
        self.assertNotIn('site_dates', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'firstConstructionDate': '1992'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteEstablishmentDate': '19920320'})
        self.assertNotIn('site_dates', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'firstConstructionDate': '19920315'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteEstablishmentDate': '1993'})
        self.assertNotIn('site_dates', validator.errors)


    def test_construction_date_after_inventory_date(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'firstConstructionDate': '19920315'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteEstablishmentDate': '19920220'})
        self.assertIn('site_dates', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'firstConstructionDate': '1993'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteEstablishmentDate': '19920320'})
        self.assertIn('site_dates', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'firstConstructionDate': '19920315'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteEstablishmentDate': '1991'})
        self.assertIn('site_dates', validator.errors)


class SiteEstablishmentDate(TestCase):
    def test_optional(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678'}, )
        self.assertNotIn('siteEstablishmentDate', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteEstablishmentDate': '   '}, )
        self.assertNotIn('siteEstablishmentDate', validator.errors)

    def test_max_length(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteEstablishmentDate': '19921112'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('siteEstablishmentDate', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteEstablishmentDate': '199211121'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('siteEstablishmentDate', validator.errors)

    def test_valid_date(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteEstablishmentDate': '19921112'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('siteEstablishmentDate', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteEstablishmentDate': '1992111'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('siteEstablishmentDate', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteEstablishmentDate': '19921330'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('siteEstablishmentDate', validator.errors)

    def test_partial_dates(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteEstablishmentDate': '1992'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('siteEstablishmentDate', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteEstablishmentDate': '199210'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('siteEstablishmentDate', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteEstablishmentDate': '1992101'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('siteEstablishmentDate', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteEstablishmentDate': '19921'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('siteEstablishmentDate', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteEstablishmentDate': '199'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('siteEstablishmentDate', validator.errors)

    def test_construction_date_before_inventory_date(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteEstablishmentDate': '19920315'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'firstConstructionDate': '19920215'})
        self.assertNotIn('site_dates', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteEstablishmentDate': '1993'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'firstConstructionDate': '19920215'})
        self.assertNotIn('site_dates', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteEstablishmentDate': '199203'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'firstConstructionDate': '19920215'})
        self.assertNotIn('site_dates', validator.errors)

    def test_construction_date_after_inventory_date(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteEstablishmentDate': '19920215'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'firstConstructionDate': '19920315'})
        self.assertIn('site_dates', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteEstablishmentDate': '199202'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'firstConstructionDate': '19920315'})
        self.assertIn('site_dates', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteEstablishmentDate': '1992'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'firstConstructionDate': '19920315'})
        self.assertIn('site_dates', validator.errors)


class HoleDepthTestCase(TestCase):

    def test_optional(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678'}, )
        self.assertNotIn('holeDepth', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'holeDepth': '   '}, )
        self.assertNotIn('holeDepth', validator.errors)

    def test_max_length(self):
        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'holeDepth': ' 1234567'},
                           {'agencyCode': 'USGS', 'siteNumber': '12345678'})
        self.assertNotIn('holeDepth', validator.errors)

        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'holeDepth': ' 12345678'},
                           {'agencyCode': 'USGS', 'siteNumber': '12345678'})
        self.assertIn('holeDepth', validator.errors)

    def test_numeric(self):
        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'holeDepth': ' 1234567'},
                           {'agencyCode': 'USGS', 'siteNumber': '12345678'})
        self.assertNotIn('holeDepth', validator.errors)

        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'holeDepth': '-1234567'},
                           {'agencyCode': 'USGS', 'siteNumber': '12345678'})
        self.assertNotIn('holeDepth', validator.errors)

        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'holeDepth': ' 1234.67'},
                           {'agencyCode': 'USGS', 'siteNumber': '12345678'})
        self.assertNotIn('holeDepth', validator.errors)

        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'holeDepth': ' 123A567'},
                           {'agencyCode': 'USGS', 'siteNumber': '12345678'})
        self.assertIn('holeDepth', validator.errors)

    def test_invalid_non_null_code_for_site_type(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'holeDepth': '12345'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteTypeCode': 'FA-QC'})
        self.assertIn('holeDepth', validator.errors['siteTypeCode'][0])

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'holeDepth': ' '},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteTypeCode': 'FA-QC'})
        self.assertNotIn('siteTypeCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '9876543210', 'holeDepth': '12345'},
                           {'agencyCode': 'USGS ', 'siteNumber': '9876543210', 'siteTypeCode': 'GW'})
        self.assertNotIn('siteTypeCode', validator.errors)


class WellDepthTestCase(TestCase):

    def test_optional(self):
        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678'}, )
        self.assertNotIn('wellDepth', validator.errors)

        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'wellDepth': '  '}, )
        self.assertNotIn('wellDepth', validator.errors)

    def test_max_length(self):
        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'wellDepth': ' 1234567'},
                           {'agencyCode': 'USGS', 'siteNumber': '12345678'})
        self.assertNotIn('wellDepth', validator.errors)

        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'wellDepth': ' 12345678'},
                           {'agencyCode': 'USGS', 'siteNumber': '12345678'})
        self.assertIn('wellDepth', validator.errors)

    def test_numeric(self):
        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'wellDepth': ' 1234567'},
                           {'agencyCode': 'USGS', 'siteNumber': '12345678'})
        self.assertNotIn('wellDepth', validator.errors)

        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'wellDepth': '-1234567'},
                           {'agencyCode': 'USGS', 'siteNumber': '12345678'})
        self.assertNotIn('wellDepth', validator.errors)

        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'wellDepth': ' 1234.67'},
                           {'agencyCode': 'USGS', 'siteNumber': '12345678'})
        self.assertNotIn('wellDepth', validator.errors)

        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'wellDepth': ' 123A567'},
                           {'agencyCode': 'USGS', 'siteNumber': '12345678'})
        self.assertIn('wellDepth', validator.errors)

    def test_well_depth_greater_than_hole_depth(self):
        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'wellDepth': ' 123567'},
                           {'agencyCode': 'USGS', 'siteNumber': '12345678', 'holeDepth': ' 120000'})
        self.assertIn('depths', validator.errors)

    def test_well_depth_less_than_hole_depth(self):
        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'wellDepth': ' 123567'},
                           {'agencyCode': 'USGS', 'siteNumber': '12345678', 'holeDepth': ' 130000'})
        self.assertNotIn('depths', validator.errors)

    def test_depth_when_one_is_blank(self):
        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'wellDepth': ' 123567'},
                           {'agencyCode': 'USGS', 'siteNumber': '12345678', 'holeDepth': ' '})
        self.assertNotIn('depths', validator.errors)

        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'holeDepth': ' 123567'},
                           {'agencyCode': 'USGS', 'siteNumber': '12345678', 'wellDepth': ' '})
        self.assertNotIn('depths', validator.errors)

    def test_invalid_non_null_code_for_site_type(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'wellDepth': '12345'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteTypeCode': 'FA-QC'})
        self.assertIn('wellDepth', validator.errors['siteTypeCode'][0])

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'wellDepth': ' '},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteTypeCode': 'FA-QC'})
        self.assertNotIn('siteTypeCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '9876543210', 'wellDepth': '12345'},
                           {'agencyCode': 'USGS ', 'siteNumber': '9876543210', 'siteTypeCode': 'GW'})
        self.assertNotIn('siteTypeCode', validator.errors)


class SourceOfDepthCodeTestCase(TestCase):

    def test_optional(self):
        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678'}, )
        self.assertNotIn('sourceOfDepthCode', validator.errors)

        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'sourceOfDepthCode': ' '}, )
        self.assertNotIn('sourceOfDepthCode', validator.errors)

    def test_max_length(self):
        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'sourceOfDepthCode': 'A'},
                           {'agencyCode': 'USGS', 'siteNumber': '12345678'})
        self.assertNotIn('sourceOfDepthCode', validator.errors)

        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'sourceOfDepthCode': 'AA'},
                           {'agencyCode': 'USGS', 'siteNumber': '12345678'})
        self.assertIn('sourceOfDepthCode', validator.errors)

    def test_in_ref_list(self):
        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'sourceOfDepthCode': 'A'},
                           {'agencyCode': 'USGS', 'siteNumber': '12345678'})
        self.assertNotIn('sourceOfDepthCode', validator.errors)

    def test_not_in_ref_list(self):
        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'sourceOfDepthCode': 'B'},
                           {'agencyCode': 'USGS', 'siteNumber': '12345678'})
        self.assertIn('sourceOfDepthCode', validator.errors)

    def test_invalid_non_null_code_for_site_type(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'sourceOfDepthCode': 'B'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteTypeCode': 'FA-QC'})
        self.assertIn('sourceOfDepthCode', validator.errors['siteTypeCode'][0])

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'sourceOfDepthCode': ' '},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteTypeCode': 'FA-QC'})
        self.assertNotIn('siteTypeCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '9876543210', 'sourceOfDepthCode': 'B'},
                           {'agencyCode': 'USGS ', 'siteNumber': '9876543210', 'siteTypeCode': 'GW'})
        self.assertNotIn('siteTypeCode', validator.errors)


class ProjectNumberTestCase(TestCase):

    def test_optional(self):
        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678'}, )
        self.assertNotIn('projectNumber', validator.errors)

        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'projectNumber': '   '}, )
        self.assertNotIn('projectNumber', validator.errors)

    def test_max_length(self):
        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'projectNumber': '123456789ABC'},
                           {'agencyCode': 'USGS', 'siteNumber': '12345678'})
        self.assertNotIn('projectNumber', validator.errors)

        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'projectNumber': '123456789ABCD'},
                           {'agencyCode': 'USGS', 'siteNumber': '12345678'})
        self.assertIn('projectNumber', validator.errors)


class TimeZoneCodeTestCase(TestCase):

    def test_required(self):
        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678'}, )
        self.assertIn('timeZoneCode', validator.errors)

        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'timeZoneCode': '  '}, )
        self.assertIn('timeZoneCode', validator.errors)

        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'timeZoneCode': 'EST'}, )
        self.assertNotIn('timeZoneCode', validator.errors)

    def test_max_length(self):
        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'timeZoneCode': 'ZP-11'},
                           {'agencyCode': 'USGS', 'siteNumber': '12345678'})
        self.assertNotIn('timeZoneCode', validator.errors)

        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'timeZoneCode': 'ZZP-11'},
                           {'agencyCode': 'USGS', 'siteNumber': '12345678'})
        self.assertIn('timeZoneCode', validator.errors)

    def test_in_ref_list(self):
        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'timeZoneCode': 'ZP-11'},
                           {'agencyCode': 'USGS', 'siteNumber': '12345678'})
        self.assertNotIn('timeZoneCode', validator.errors)

    def test_not_in_ref_list(self):
        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'timeZoneCode': 'ZP-10'},
                           {'agencyCode': 'USGS', 'siteNumber': '12345678'})
        self.assertIn('timeZoneCode', validator.errors)


class DaylightSavingsTimeFlag(TestCase):

    def test_required(self):
        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678'}, )
        self.assertIn('daylightSavingsTimeFlag', validator.errors)

        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'daylightSavingsTimeFlag': '  '}, )
        self.assertIn('daylightSavingsTimeFlag', validator.errors)

        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'daylightSavingsTimeFlag': 'Y'}, )
        self.assertNotIn('daylightSavingsTimeFlag', validator.errors)

    def test_max_length(self):
        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'daylightSavingsTimeFlag': 'Y'}, )
        self.assertNotIn('daylightSavingsTimeFlag', validator.errors)

        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'daylightSavingsTimeFlag': 'YY'}, )
        self.assertIn('daylightSavingsTimeFlag', validator.errors)

    def test_in_ref_list(self):
        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'daylightSavingsTimeFlag': 'Y'}, )
        self.assertNotIn('daylightSavingsTimeFlag', validator.errors)

    def test_not_in_ref_list(self):
        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'daylightSavingsTimeFlag': 'A'}, )
        self.assertIn('daylightSavingsTimeFlag', validator.errors)


class SiteTypeCodeTestCase(TestCase):

    def test_required(self):
        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678'}, )
        self.assertIn('siteTypeCode', validator.errors)

        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'siteTypeCode': '  '}, )
        self.assertIn('siteTypeCode', validator.errors)

        validator.validate({'agencyCode': 'USGS', 'siteNumber': '9876543210', 'siteTypeCode': 'FA-CS'}, )
        self.assertNotIn('siteTypeCode', validator.errors)

    def test_max_length(self):
        validator.validate({'agencyCode': 'USGS', 'siteNumber': '9876543210', 'siteTypeCode': 'FA-CS'},
                           {'agencyCode': 'USGS', 'siteNumber': '9876543210', 'siteTypeCode': 'FA-CS'})
        self.assertNotIn('siteTypeCode', validator.errors)

        validator.validate({'agencyCode': 'USGS', 'siteNumber': '9876543210', 'siteTypeCode': 'FA-CIIII'},
                           {'agencyCode': 'USGS', 'siteNumber': '9876543210', 'siteTypeCode': 'FA-CI'})
        self.assertIn('siteTypeCode', validator.errors)

    def test_in_ref_list(self):
        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'siteTypeCode': 'FA-CS'},
                           {'agencyCode': 'USGS', 'siteNumber': '12345678', 'siteTypeCode': 'FA-CI'})
        self.assertNotIn('siteTypeCode', validator.errors)

    def test_not_in_ref_list(self):
        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'siteTypeCode': 'FA-CJ'},
                           {'agencyCode': 'USGS', 'siteNumber': '12345678', 'siteTypeCode': 'FA-CI'})
        self.assertIn('siteTypeCode', validator.errors)

    def test_for_allowed_transition(self):
        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'siteTypeCode': 'FA-CS'},
                           {'agencyCode': 'USGS', 'siteNumber': '12345678', 'siteTypeCode': 'FA-PV'})
        self.assertNotIn('siteTypeCode', validator.errors)

    def test_for_invalid_transition(self):
        validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678', 'siteTypeCode': 'FA-CS'},
                           {'agencyCode': 'USGS', 'siteNumber': '12345678', 'siteTypeCode': 'FA-OF'})
        self.assertIn('siteTypeCode', validator.errors)


class RemarksTestCase(TestCase):

    def test_optional(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678'}, )
        self.assertNotIn('remarks', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'remarks': ''}, )
        self.assertNotIn('remarks', validator.errors)

    def test_max_lenth(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678',
                            'remarks': '12345678901234567890123456789012345678901234567890'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertNotIn('remarks', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678',
                            'remarks': '123456789012345678901234567890123456789012345678901'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678'})
        self.assertIn('remarks', validator.errors)


class SiteWebReadyCode(TestCase):

    def test_required(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678'}, )
        self.assertIn('siteWebReadyCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteWebReadyCode': ' '}, )
        self.assertIn('siteWebReadyCode', validator.errors)

        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteWebReadyCode': 'P'}, )
        self.assertNotIn('siteWebReadyCode', validator.errors)

    def test_in_ref_list(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteWebReadyCode': 'Y'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteWebReadyCode': 'P'})
        self.assertNotIn('siteWebReadyCode', validator.errors)

    def test_not_in_ref_list(self):
        validator.validate({'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteWebReadyCode': 'C'},
                           {'agencyCode': 'USGS ', 'siteNumber': '12345678', 'siteWebReadyCode': 'P'})
        self.assertIn('siteWebReadyCode', validator.errors)