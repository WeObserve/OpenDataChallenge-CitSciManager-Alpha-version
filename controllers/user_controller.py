from flask import Blueprint, request
from dtos.controllers.requests.create_user_request_dto import CreateUserRequestDTO
from services import user_service
import json
from dtos.controllers.responses.create_user_response_dto import CreateUserResponseDTO
from functools import partial
from filters.authentication_filter import pseudo_authenticate
from dtos.controllers.requests.invite_user_request_dto import InviteUserRequestDTO
from dtos.controllers.responses.invite_user_response_dto import InviteUserResponseDTO

def construct_blueprint(app_config):
    user_api = Blueprint('user_api', __name__)

    db_connection = app_config["db_connection"]
    env = app_config["env"]
    master_secret_key = app_config["master_secret_key"]
    login_page_url = app_config["login_page_url"]
    email_sender_address = app_config["email_sender_address"]
    db_connection_client = app_config["db_connection_client"]

    authenticate = partial(pseudo_authenticate, app_config=app_config)

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

    @user_api.route('/invite', methods = ['POST'])
    @authenticate
    def invite_user(**kwargs):
        print("Inside invite_user controller")

        try:
            #Convert request into python object
            invite_user_request_dto = InviteUserRequestDTO(request)

            invite_user_response_dto = user_service.invite_user(db_connection, invite_user_request_dto, env, master_secret_key, login_page_url, email_sender_address, kwargs["user_id"], db_connection_client)

            return json.dumps(invite_user_response_dto.convert_to_dict())

        except Exception as e:
            return json.dumps(InviteUserResponseDTO({
                "code": 500,
                "message": str(e)
            }).convert_to_dict())

    @user_api.route('/is-logged-in', methods=['POST'])
    @authenticate
    def check_user_logged_in(**kwargs):
        print("Inside check user logged in")
        print(f'user id is: {kwargs["user_id"]}')
        return {
            "code": 200,
            "message": "SUCCESS"
        }

    return user_api

