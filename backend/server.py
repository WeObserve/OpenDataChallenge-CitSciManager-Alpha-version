import flask
from flask import request
import json
from file_service import process_upload_file, process_download_file
from user_service import process_invite_users
from common_service import validate_request
from db.mongo import mongo_connection

env = "staging"
mongo_db_connection = mongo_connection.connect_to_db(env)

app = flask.Flask(__name__)

app.config["DEBUG"] = True

@app.route('/files', methods=["POST"])
def upload_files():
    response = {
        "success_response": None,
        "error_response": None
    }

    request_validity = validate_request(mongo_db_connection, request, "UPLOAD_FILES", "form")

    if (not request_validity["is_valid"]):
        response["error_response"] = {
            "request_validity": request_validity
        }

        return json.dumps(response)

    process_response = process_upload_file(mongo_db_connection, request, request_validity["user"], env)

    if process_response["is_success"]:
        response["success_response"] = process_response
    else:
        response["error_response"] = process_response

    return response

@app.route('/files', methods=["GET"])
def download_files():
    response = {
        "success_response": None,
        "error_response": None
    }

    request_validity = validate_request(mongo_db_connection, request, "DOWNLOAD_FILES", "form")

    if (not request_validity["is_valid"]):
        response["error_response"] = {
            "request_validity": request_validity
        }

        return json.dumps(response)

    process_response = process_download_file(mongo_db_connection, request, request_validity["user"], env)

    if process_response["is_success"]:
        response["success_response"] = process_response
    else:
        response["error_response"] = process_response

    return response

@app.route('/users', methods=["POST"])
def invite_users():
    response = {
        "success_response": None,
        "error_response": None
    }

    request_validity = validate_request(mongo_db_connection, request, "INVITE_USERS", "form")

    if (not request_validity["is_valid"]):
        response["error_response"] = {
            "request_validity": request_validity
        }

        return json.dumps(response)

    process_response = process_invite_users(mongo_db_connection, request, request_validity["user"], env)

    if process_response["is_success"]:
        response["success_response"] = process_response
    else:
        response["error_response"] = process_response

    return response

app.run(host="0.0.0.0")