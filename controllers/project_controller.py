from flask import Blueprint, request
from dtos.controllers.requests.create_project_request_dto import CreateProjectRequestDTO
from services import project_service
import json
from dtos.controllers.responses.create_project_response_dto import CreateProjectResponseDTO
from functools import partial
from filters.authentication_filter import pseudo_authenticate

def construct_blueprint(app_config):
    project_api = Blueprint('project_api', __name__)

    db_connection = app_config["db_connection"]
    db_connection_client = app_config["db_connection_client"]
    env = app_config["env"]

    authenticate = partial(pseudo_authenticate, app_config=app_config)

    @project_api.route('', methods = ['POST'])
    @authenticate
    def create_project(**kwargs):
        print("Inside create_project controller")

        try:
            #convert json request to python object
            create_project_request_dto = CreateProjectRequestDTO(request)

            create_project_response_dto = project_service.create_project(db_connection, kwargs["user_id"], create_project_request_dto, env, db_connection_client)

            return json.dumps(create_project_response_dto.convert_to_dict())
        except Exception as e:
            return json.dumps(CreateProjectResponseDTO({
                "code": 500,
                "message": str(e)
            }).convert_to_dict())

    return project_api