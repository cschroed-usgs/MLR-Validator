
from unittest import TestCase, mock

from ..error_validator import ErrorValidator

@mock.patch('mlrvalidator.validators.error_validator.SingleFieldValidator')
@mock.patch('mlrvalidator.validators.error_validator.CrossFieldErrorValidator')
@mock.patch('mlrvalidator.validators.error_validator.CrossFieldRefErrorValidator')
@mock.patch('mlrvalidator.validators.error_validator.TransitionValidator')
@mock.patch('mlrvalidator.validators.error_validator.open', mock.mock_open(read_data=''))
class ErrorValidatorErrorsTestCase(TestCase):

    def test_all_valid(self, mtran_class, mref_class, mcross_class, msingle_field_class):
        mtran = mtran_class.return_value
        mref = mref_class.return_value
        mcross = mcross_class.return_value
        msingle_field = msingle_field_class.return_value

        mtran.validate.return_value = True
        mtran.errors = {}
        mref.validate.return_value = True
        mref.errors = {}
        mcross.validate.return_value = True
        mcross.errors = {}
        msingle_field.validate.return_value = True
        msingle_field.errors = {}

        validator = ErrorValidator('schema_dir', 'ref_dir')
        result = validator.validate({'A': 'This', 'B': 'That'}, {})
        self.assertTrue(result)
        self.assertEqual(len(validator.errors), 0)

        result = validator.validate({'A': 'This', 'B': 'That'}, {'B': 'Them'})
        self.assertTrue(result)
        self.assertEqual(len(validator.errors), 0)

    def test_single_field_invalid(self, mtran_class, mref_class, mcross_class, msingle_field_class):
        mtran = mtran_class.return_value
        mref = mref_class.return_value
        mcross = mcross_class.return_value
        msingle_field = msingle_field_class.return_value

        mtran.validate.return_value = True
        mtran.errors = {}
        mref.validate.return_value = True
        mref.errors = {}
        mcross.validate.return_value = True
        mcross.errors = {}
        msingle_field.validate.return_value = False
        msingle_field.errors = {'A' : ['Invalid']}

        validator = ErrorValidator('schema_dir', 'ref_dir')
        result = validator.validate({'A': 'This', 'B': 'That'}, {})
        self.assertFalse(result)
        self.assertEqual(len(validator.errors), 1)
        self.assertIn('A', validator.errors)

        result = validator.validate({'A': 'This', 'B': 'That'}, {'B': 'Them'})
        self.assertFalse(result)
        self.assertEqual(len(validator.errors), 1)
        self.assertIn('A', validator.errors)

    def test_cross_field_invalid(self, mtran_class, mref_class, mcross_class, msingle_field_class):
        mtran = mtran_class.return_value
        mref = mref_class.return_value
        mcross = mcross_class.return_value
        msingle_field = msingle_field_class.return_value

        mtran.validate.return_value = True
        mtran.errors = {}
        mref.validate.return_value = True
        mref.errors = {}
        mcross.validate.return_value = False
        mcross.errors = {'B': ['Invalid']}
        msingle_field.validate.return_value = True
        msingle_field.errors = {}

        validator = ErrorValidator('schema_dir', 'ref_dir')
        result = validator.validate({'A': 'This', 'B': 'That'}, {})
        self.assertFalse(result)
        self.assertEqual(len(validator.errors), 1)
        self.assertIn('B', validator.errors)

        result = validator.validate({'A': 'This', 'B': 'That'}, {'B': 'Them'})
        self.assertFalse(result)
        self.assertEqual(len(validator.errors), 1)
        self.assertIn('B', validator.errors)

    def test_ref_invalid(self, mtran_class, mref_class, mcross_class, msingle_field_class):
        mtran = mtran_class.return_value
        mref = mref_class.return_value
        mcross = mcross_class.return_value
        msingle_field = msingle_field_class.return_value

        mtran.validate.return_value = True
        mtran.errors = {}
        mref.validate.return_value = False
        mref.errors = {'B': ['Bad']}
        mcross.validate.return_value = True
        mcross.errors = {}
        msingle_field.validate.return_value = True
        msingle_field.errors = {}

        validator = ErrorValidator('schema_dir', 'ref_dir')
        result = validator.validate({'A': 'This', 'B': 'That'}, {})
        self.assertFalse(result)
        self.assertEqual(len(validator.errors), 1)
        self.assertIn('B', validator.errors)

        result = validator.validate({'A': 'This', 'B': 'That'}, {'B': 'Them'})
        self.assertFalse(result)
        self.assertEqual(len(validator.errors), 1)
        self.assertIn('B', validator.errors)

    def test_tran_invalid(self, mtran_class, mref_class, mcross_class, msingle_field_class):
        mtran = mtran_class.return_value
        mref = mref_class.return_value
        mcross = mcross_class.return_value
        msingle_field = msingle_field_class.return_value

        mtran.validate.return_value = False
        mtran.errors = {'B': ['Bad transition']}
        mref.validate.return_value = True
        mref.errors = {}
        mcross.validate.return_value = True
        mcross.errors = {}
        msingle_field.validate.return_value = True
        msingle_field.errors = {}

        validator = ErrorValidator('schema_dir', 'ref_dir')
        result = validator.validate({'A': 'This', 'B': 'That'})
        self.assertTrue(result)
        self.assertEqual(len(validator.errors), 0)

        result = validator.validate({'A': 'This', 'B': 'That'}, {'B': 'Them'})
        self.assertFalse(result)
        self.assertEqual(len(validator.errors), 1)
        self.assertIn('B', validator.errors)

    def test_multiple_errors(self, mtran_class, mref_class, mcross_class, msingle_field_class):
        mtran = mtran_class.return_value
        mref = mref_class.return_value
        mcross = mcross_class.return_value
        msingle_field = msingle_field_class.return_value

        mtran.validate.return_value = False
        mtran.errors = {'B': ['Bad transition']}
        mref.validate.return_value = False
        mref.errors = {'B': ['Bad ref']}
        mcross.validate.return_value = False
        mcross.errors = {'A': ['Invalid cross']}
        msingle_field.validate.return_value = False
        msingle_field.errors = {'B': ['Missing']}
        validator = ErrorValidator('schema_dir', 'ref_dir')
        result = validator.validate({'A': 'This', 'B': 'That'})
        self.assertFalse(result)
        self.assertEqual(len(validator.errors), 2)
        self.assertEqual(len(validator.errors.get('A')), 1)
        self.assertEqual(len(validator.errors.get('B')), 2)

        result = validator.validate({'A': 'This', 'B': 'That'}, {'B': 'Them'})
        self.assertFalse(result)
        self.assertEqual(len(validator.errors), 2)
        self.assertEqual(len(validator.errors.get('A')), 1)
        self.assertEqual(len(validator.errors.get('B')), 3)

    def test_identity_update(self, mtran_class, mref_class, mcross_class, msingle_field_class):
        mtran = mtran_class.return_value
        mref = mref_class.return_value
        mcross = mcross_class.return_value
        msingle_field = msingle_field_class.return_value

        mtran.validate.return_value = True
        mtran.errors = {}
        mref.validate.return_value = True
        mref.errors = {}
        mcross.validate.return_value = True
        mcross.errors = {}
        msingle_field.validate.return_value = True
        msingle_field.errors = {}

        validator = ErrorValidator('schema_dir', 'ref_dir')
        # it is valid for a valid site to update to an identical version of itself.
        self.assertTrue(validator.validate({'agencyCode': 'USGS', 'siteNumber': '12345678'},
                                            {'agencyCode': 'USGS', 'siteNumber': '12345678'}))
        self.assertEqual(len(validator.errors), 0)
        self.assertFalse('duplicate_site' in validator.errors)








