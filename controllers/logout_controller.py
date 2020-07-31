from flask import Blueprint, request
from services import logout_service
import json
from dtos.controllers.responses.logout_response_dto import LogoutResponseDTO
from functools import partial
from filters.authentication_filter import pseudo_authenticate

def construct_blueprint(app_config):
    logout_api = Blueprint('logout_api', __name__)

    in_memory_cache = app_config["in_memory_cache"]

    authenticate = partial(pseudo_authenticate, app_config=app_config)

    @logout_api.route('', methods = ['POST'])
    @authenticate
    def logout(**kwargs):
        print("Inside logout controller")

        try:
            logout_response_dto = logout_service.logout(request, in_memory_cache, kwargs["user_id"])

            return json.dumps(logout_response_dto.convert_to_dict())

        except Exception as e:
            return json.dumps(LogoutResponseDTO({
                "code": 500,
                "message": str(e)
            }).convert_to_dict())

    return logout_api