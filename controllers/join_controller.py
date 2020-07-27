from flask import Blueprint, request
from dtos.controllers.requests.create_joins_request_dto import CreateJoinsRequestDTO
from services import join_service
import json
from dtos.controllers.responses.create_joins_response_dto import CreateJoinsResponseDTO
from functools import partial
from filters.authentication_filter import pseudo_authenticate

def construct_blueprint(app_config):
    join_api = Blueprint('join_api', __name__)

    db_connection = app_config["db_connection"]
    env = app_config["env"]

    authenticate = partial(pseudo_authenticate, app_config=app_config)

    @join_api.route('', methods = ['POST'])
    @authenticate
    def create_joins(**kwargs):
        print("Inside create_joins controller")

        try:
            #convert json request to python object
            create_joins_request_dto = CreateJoinsRequestDTO(request)

            create_joins_response_dto = join_service.create_joins(db_connection, kwargs["user_id"], create_joins_request_dto, env)

            return json.dumps(create_joins_response_dto.convert_to_dict())
        except Exception as e:
            return json.dumps(CreateJoinsResponseDTO({
                "code": 500,
                "message": str(e)
            }).convert_to_dict())

    return join_api

