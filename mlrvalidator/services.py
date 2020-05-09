import time

import pkg_resources

from flask import request
from flask_restplus import Api, Resource, fields
from werkzeug.exceptions import BadRequest

from app import application
from .flask_restplus_jwt import JWTRestplusManager, jwt_required


# This will add the Authorize button to the swagger docs
from .validators.error_validator import ErrorValidator
from .validators.warning_validator import WarningValidator

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

api = Api(application,
          title='MLR Validator',
          description='Provides a service to take a json input of an MLR transaction, validate it, respond back with a response containing the validation results',
          default='Validator',
          default_label='Validator',
          doc='/api',
          authorizations=authorizations
          )

# Setup the Flask-JWT-Simple extension
jwt = JWTRestplusManager(api, application)

ddot_location_model = api.model('DdotLocationModel', {
    "agencyCode": fields.String(),
    "agencyUseCode": fields.String(),
    "altitude": fields.String(),
    "altitudeAccuracyValue": fields.String(),
    "altitudeDatumCode": fields.String(),
    "altitudeMethodCode": fields.String(),
    "aquiferCode": fields.String(),
    "aquiferTypeCode": fields.String(),
    "basinCode": fields.String(),
    "contributingDrainageArea": fields.String(),
    "coordinateAccuracyCode": fields.String(),
    "coordinateDatumCode": fields.String(),
    "coordinateMethodCode": fields.String(),
    "countryCode": fields.String(),
    "countyCode": fields.String(),
    "dataReliabilityCode": fields.String(),
    "dataTypesCode": fields.String(),
    "daylightSavingsTimeFlag": fields.String(),
    "districtCode": fields.String(),
    "drainageArea": fields.String(),
    "firstConstructionDate": fields.String(),
    "gwFileCode": fields.String(),
    "holeDepth": fields.String(),
    "hydrologicUnitCode": fields.String(),
    "instrumentsCode": fields.String(),
    "landNet": fields.String(),
    "latitude": fields.String(),
    "longitude": fields.String(),
    "mapName": fields.String(),
    "mapScale": fields.String(),
    "minorCivilDivisionCode": fields.String(),
    "nationalAquiferCode": fields.String(),
    "nationalWaterUseCode": fields.String(),
    "primaryUseOfSiteCode": fields.String(),
    "primaryUseOfWaterCode": fields.String(),
    "projectNumber": fields.String(),
    "remarks": fields.String(),
    "secondaryUseOfSiteCode": fields.String(),
    "secondaryUseOfWaterCode": fields.String(),
    "siteEstablishmentDate": fields.String(),
    "siteNumber": fields.String(),
    "siteTypeCode": fields.String(),
    "siteWebReadyCode": fields.String(),
    "sourceOfDepthCode": fields.String(),
    "stateFipsCode": fields.String(),
    "stationName": fields.String(),
    "stationIx": fields.String(), #Whereas most fields come from the ddot ingester service, this field is added by the transformer service
    "tertiaryUseOfSiteCode": fields.String(),
    "tertiaryUseOfWaterCode": fields.String(),
    "timeZoneCode": fields.String(),
    "topographicCode": fields.String(),
    "wellDepth": fields.String(),
})

location_model = api.clone('LocationModel', ddot_location_model, {
    "created": fields.String(),
    "createdBy": fields.String(),
    "decimalLatitude": fields.Integer(),
    "decimalLongitude": fields.Integer(),
    "id": fields.Integer(),
    "updated": fields.String(),
    "updatedBy": fields.String(),
})

validate_location_model = api.model('ValidateLocationModel', {
    'ddotLocation': fields.Nested(ddot_location_model),
    'existingLocation': fields.Nested(location_model)
})

error_model = api.model('ErrorModel', {
    'error_message': fields.String(required=True)
})

validation_model = api.model('SuccessModel', {'validation_passed_message': fields.String(),
                                              'warning_message': fields.String(),
                                              'fatal_error_message': fields.String()})


def _validate_response(req_json, update=False):
    if 'ddotLocation' not in req_json or 'existingLocation' not in req_json:
        raise BadRequest('Request is missing required components (ddotLocation and/or existingLocation).')
    ddot_location = req_json.get('ddotLocation')
    existing_location = req_json.get('existingLocation')

    start = time.time()
    error_validator = ErrorValidator(application.config['SCHEMA_DIR'], application.config['REFERENCE_FILE_DIR'])
    warning_validator = WarningValidator(application.config['SCHEMA_DIR'], application.config['REFERENCE_FILE_DIR'])
    validator_setup_time = time.time() - start
    print("Validator setup completed in {} seconds".format(validator_setup_time))

    no_errors = error_validator.validate(ddot_location, existing_location, update=update)
    no_warnings = warning_validator.validate(ddot_location, existing_location)

    response = {}
    if not no_errors:
        response["fatal_error_message"] = error_validator.errors
    if not no_warnings:
        response["warning_message"] = warning_validator.warnings
    if no_errors and no_warnings:
        response["validation_passed_message"] = 'Validations Passed'

    return response, 200


@api.route('/validators/add')
class AddValidator(Resource):

    @api.response(200, 'Successfully validated', validation_model)
    @api.response(400, 'Invalid validation request', error_model)
    @api.response(401, 'Not authorized', error_model)
    @api.response(422, 'Invalid token', error_model)
    @api.response(500, 'Error during validation', error_model)
    @api.doc(security='apikey')
    @api.expect(validate_location_model)
    @jwt_required
    def post(self):
        try:
            response, status = _validate_response(request.get_json())
        except BadRequest as err:
            response, status = {'error_message': err.description}, 400
        
        return response, status


@api.route('/validators/update')
class UpdateValidator(Resource):

    @api.response(200, 'Successfully validated', validation_model)
    @api.response(400, 'Invalid validation request', error_model)
    @api.response(401, 'Not authorized', error_model)
    @api.response(422, 'Invalid token', error_model)
    @api.response(500, 'Error during validation', error_model)
    @api.doc(security='apikey')
    @api.expect(validate_location_model)
    @jwt_required
    def post(self):
        try:
            response, status = _validate_response(request.get_json(), update=True)
        except BadRequest as err:
            response, status = {'error_message': err.description}, 400
        
        return response, status


version_model = api.model('VersionModel', {
    'version': fields.String,
    'artifact': fields.String
})


@api.route('/version')
class Version(Resource):

    @api.response(200, 'Success', version_model)
    def get(self):
        try:
            distribution = pkg_resources.get_distribution('usgs_wma_mlr_validator')
        except pkg_resources.DistributionNotFound:
            resp = {
                "version": "local_development",
                "artifact": None
            }
        else:
            resp = {
                "version": distribution.version,
                "artifact": distribution.project_name
            }
        return resp

@api.errorhandler
def default_error_handler(error):
    '''Default error handler'''
    return {'error_message': str(error)}, getattr(error, 'code', 500)