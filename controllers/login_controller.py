from flask import Blueprint, request
from dtos.controllers.requests.login_request_dto import LoginRequestDTO
from services import login_service
import json
from dtos.controllers.responses.login_response_dto import LoginResponseDTO


def construct_blueprint(app_config):
    login_api = Blueprint('login_api', __name__)

    db_connection = app_config["db_connection"]
    env = app_config["env"]
    in_memory_cache = app_config["in_memory_cache"]
    secret_key = app_config["master_secret_key"]

    @login_api.route('', methods = ['POST'])
    def login():
        print("Inside login controller")

        try:
            #Convert request into python object
            login_request_dto = LoginRequestDTO(request)

            login_response_dto = login_service.login(db_connection, login_request_dto, in_memory_cache, secret_key, env)

            return json.dumps(login_response_dto.convert_to_dict())

        except Exception as e:
            return json.dumps(LoginResponseDTO({
                "code": 500,
                "message": str(e)
            }).convert_to_dict())

    return login_api