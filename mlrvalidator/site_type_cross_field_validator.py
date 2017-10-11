from cerberus import Validator

from . import site_type_cross_field_reference


class SiteTypeCrossFieldValidator(Validator):

    def _validate_valid_site_type_cross_field(self, valid_site_type_cross_field, field, value):
        """
        # Check that for a given site type all the not nullable fields are not null
        # and that all nullable fields are null

        The rule's arguments are validated against this schema: {'valid_site_type_cross_field': True}

        """
        if valid_site_type_cross_field:
            site_type_ref = site_type_cross_field_reference.get_site_type_field_dependencies(value)
            not_nullable_attrs = site_type_ref['notNullAttrs']
            nullable_attrs = site_type_ref['nullAttrs']
            nn_attr_field_problems = []
            n_attr_field_problems = []
            for nn_attr in not_nullable_attrs:
                nn_attr_field_val = self.document[nn_attr]
                if len(nn_attr_field_val) == 0:
                    nn_attr_field_problems.append(nn_attr)
                    self._error(nn_attr, 'Must not be null.'.format(value))
            for n_attr in nullable_attrs:
                n_attr_field_val = self.document[n_attr]
                if len(n_attr_field_val) != 0:
                    n_attr_field_problems.append(n_attr)
                    self._error(n_attr, 'Must be null.'.format(value))
            if len(nn_attr_field_problems) > 0 or len(n_attr_field_problems) > 0:
                nn_attrs = ', '.join(nn_attr_field_problems)
                n_attrs = ', '.join(n_attr_field_problems)
                error_message = 'Field errors for siteType code: {}.'.format(value)
                if len(nn_attr_field_problems) > 0:
                    error_message += ' The following fields must not be null: {}.'.format(nn_attrs)
                if len(n_attr_field_problems) > 0:
                    error_message += ' The following fields must be null: {}.'.format(n_attrs)
                return self._error(field, error_message)
