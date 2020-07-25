from flask import Blueprint, request
from dtos.controllers.requests.create_user_request_dto import CreateUserRequestDTO
from services import user_service
import json
from dtos.controllers.responses.create_user_response_dto import CreateUserResponseDTO

def construct_blueprint(app_config):
    user_api = Blueprint('user_api', __name__)

    db_connection = app_config["db_connection"]
    env = app_config["env"]
    master_secret_key = app_config["master_secret_key"]
    login_page_url = app_config["login_page_url"]
    email_sender_address = app_config["email_sender_address"]

    @user_api.route('', methods = ['POST'])
    def create_user():
        print("Inside create_user controller")

        try:
            #Convert request into python object
            create_user_request_dto = CreateUserRequestDTO(request)

            user_created = user_service.create_user(db_connection, create_user_request_dto, env, master_secret_key, login_page_url, email_sender_address)

            return json.dumps(CreateUserResponseDTO({
                "code": 200,
                "message": "SUCCESS",
                "user": user_created
            }).convert_to_dict())

        except Exception as e:
            return json.dumps(CreateUserResponseDTO({
                "code": 500,
                "message": str(e)
            }).convert_to_dict())

    return user_api