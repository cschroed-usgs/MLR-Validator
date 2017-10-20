
from collections import defaultdict
import os

from .country_state_reference_validator import CountryStateReferenceValidator
from .reference import States, NationalWaterUseCodes

class CrossFieldRefValidator:

    def __init__(self, reference_dir):
        self.aquifer_ref_validator = CountryStateReferenceValidator(os.path.join(reference_dir, 'aquifer.json'), 'aquiferCodes, aquiferCode')
        self.huc_ref_validator = CountryStateReferenceValidator(os.path.join(reference_dir, 'huc.json'), 'hydrologicUnitCodes', 'hydrologicUnitCode')
        self.mcd_ref_validator = CountryStateReferenceValidator(os.path.join(reference_dir, 'mcd.json'), 'minorCivilDivsionCodes', 'minorCivilDivisionCode')
        self.national_aquifer_ref_validator = CountryStateReferenceValidator(os.path.join(reference_dir, 'national_aquifer.json'), 'nationalAquiferCodes', 'nationalAquiferCode')
        self.counties_ref_validator = CountryStateReferenceValidator(os.path.join(reference_dir, 'county.json'), 'counties', 'countyCode')

        self.states_ref = States(os.path.join(reference_dir, 'state.json'))
        self.national_water_use_ref = NationalWaterUseCodes(os.path.join(reference_dir, 'national_water_use_json'))

        self._errors = []

    def _validate_states(self):
        '''
        :return: boolean
        '''

        country = self.merged_document.get('countryCode', '').strip()
        state = self.merged_document.get('stateFipsCode', '').strip()

        valid = True
        if country and state:
            state_list = self.states_ref.get_state_codes(country)
            valid = state in state_list if state_list else True
            if not valid:
                self._errors.append({'stateFipsCode': '{0} is not in the reference list for country {1}.'.format(state, country)})

        return valid

    def _validate_national_water_use_code(self):
        '''
        :return: boolean
        '''

        site_type = self.merged_document.get('siteTypeCode', '').strip()
        water_use = self.merged_document.get('nationalWaterUseCode', '').strip()

        valid = True
        if site_type and water_use:
            valid = water_use in self.national_water_use_ref.get_national_water_use_codes(site_type)
            if not valid:
                self._errors.append({'nationalWaterUseCode': '{0} is not in the referces list for siteTypeCode {1}'.format(water_use, site_type)})

        return valid

    def validate(self, document, existing_document):
        '''
        :param dict document:
        :param dict existing_document:
        :return: boolean
        '''
        self._errors = []
        self.merged_document = existing_document.copy()
        self.merged_document.update(document)

        valid_aquifer = self.aquifer_ref_validator.validate(document, existing_document)
        valid_huc = self.huc_ref_validator.validate(document, existing_document)
        valid_mcd = self.mcd_ref_validator.validate(document, existing_document)
        valid_national_aquifer = self.national_aquifer_ref_validator.validate(document, existing_document)
        valid_counties = self.counties_ref_validator.validate(document, existing_document)

        valid_states = self._validate_states()
        valid_national_water_use = self._validate_national_water_use_code()


        self._errors.extend([err for err in [self.aquifer_ref_validator.errors,
                             self.huc_ref_validator.errors,
                             self.mcd_ref_validator.errors,
                             self.national_aquifer_ref_validator.errors,
                             self.counties_ref_validator.errors
                             ] if err is not None])

        return valid_aquifer and valid_huc and valid_mcd and valid_national_aquifer and valid_counties and valid_states and valid_national_water_use

    @property
    def errors(self):
        return self._errors