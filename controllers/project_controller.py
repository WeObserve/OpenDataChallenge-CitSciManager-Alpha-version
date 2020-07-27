from flask import Blueprint, request
from dtos.controllers.requests.create_project_request_dto import CreateProjectRequestDTO
from dtos.controllers.responses.fetch_projects_response_dto import FetchProjectsResponseDTO
from dtos.controllers.requests.fetch_projects_request_dto import FetchProjectsRequestDTO
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

    @project_api.route('', methods=['GET'])
    @authenticate
    def get_create_project():
        print("Inside get create_project controller")

        try:
            return {
            "code": 200,
            "message": "SUCCESS"
           }
        except Exception as e:
            return{
                "code": 500,
                "message": str(e)
            }


    @project_api.route('/fetch', methods=['POST'])
    @authenticate
    def fetch_projects(**kwargs):
        print("Inside fetch_projects controller")

        try:
            # convert json request to python object
            fetch_projects_request_dto = FetchProjectsRequestDTO(request)

            fetch_projects_response_dto = project_service.fetch_projects(db_connection, kwargs["user_id"],
                                                                         fetch_projects_request_dto, env)

            return json.dumps(fetch_projects_response_dto.convert_to_dict())
        except Exception as e:
            return json.dumps(FetchProjectsResponseDTO({
                "code": 500,
                "message": str(e)
            }).convert_to_dict())

    return project_api