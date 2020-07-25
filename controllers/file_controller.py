from flask import Blueprint, request
from dtos.controllers.requests.create_files_request_dto import CreateFilesRequestDTO
from services import file_service
import json
from dtos.controllers.responses.create_files_response_dto import CreateFilesResponseDTO
from functools import partial
from filters.authentication_filter import pseudo_authenticate
from dtos.controllers.requests.fetch_files_request_dto import FetchFilesRequestDTO
from dtos.controllers.responses.fetch_files_response_dto import FetchFilesResponseDTO

def construct_blueprint(app_config):
    file_api = Blueprint('file_api', __name__)

    db_connection = app_config["db_connection"]
    env = app_config["env"]

    authenticate = partial(pseudo_authenticate, app_config=app_config)

    @file_api.route('', methods = ['POST'])
    @authenticate
    def create_file(**kwargs):
        print("Inside create_file controller")

        try:
            #convert json request to python object
            create_files_request_dto = CreateFilesRequestDTO(request)

            create_files_response_dto = file_service.create_files(db_connection, kwargs["user_id"], create_files_request_dto, env)

            return json.dumps(create_files_response_dto.convert_to_dict())
        except Exception as e:
            return json.dumps(CreateFilesResponseDTO({
                "code": 500,
                "message": str(e)
            }).convert_to_dict())

    @file_api.route('/fetch', methods = ['POST'])
    @authenticate
    def fetch_files(**kwargs):
        print("Inside fetch_files controller")

        try:
            #convert json request to python object
            fetch_files_request_dto = FetchFilesRequestDTO(request)

            fetch_files_response_dto = file_service.fetch_files(db_connection, kwargs["user_id"], fetch_files_request_dto, env)

            return json.dumps(fetch_files_response_dto.convert_to_dict())
        except Exception as e:
            return json.dumps(FetchFilesResponseDTO({
                "code": 500,
                "message": str(e)
            }).convert_to_dict())

    return file_api

