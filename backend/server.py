import flask
from flask import request
import json
from file_service import process_upload_file, process_download_file
from user_service import process_invite_users
from datastory_service import process_create_datastory, process_view_datastory
from common_service import validate_request

app = flask.Flask(__name__)

app.config["DEBUG"] = True

@app.route('/files', methods=["POST"])
def upload_files():
    response = {
        "success_response": None,
        "error_response": None
    }

    request_validity = validate_request(request, "UPLOAD_FILES")

    if (not request_validity["is_valid"]):
        response["error_response"] = {
            "request_validity": request_validity
        }

        return json.dumps(response)

    process_response = process_upload_file(request)

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

    request_validity = validate_request(request, "DOWNLOAD_FILES", "form")

    if (not request_validity["is_valid"]):
        response["error_response"] = {
            "request_validity": request_validity
        }

        return json.dumps(response)

    process_response = process_download_file(request)

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

    request_validity = validate_request(request, "INVITE_USERS", "form")

    if (not request_validity["is_valid"]):
        response["error_response"] = {
            "request_validity": request_validity
        }

        return json.dumps(response)

    process_response = process_invite_users(request, request_validity["user"])

    if process_response["is_success"]:
        response["success_response"] = process_response
    else:
        response["error_response"] = process_response

    return response

@app.route('/datastories', methods=["POST"])
def create_datastory():
    response = {
        "success_response": None,
        "error_response": None
    }

    request_validity = validate_request(request, "CREATE_DATASTORY", "form")

    if (not request_validity["is_valid"]):
        response["error_response"] = {
            "request_validity": request_validity
        }

        return json.dumps(response)

    process_response = process_create_datastory(request, request_validity["user"])

    if process_response["is_success"]:
        response["success_response"] = process_response
    else:
        response["error_response"] = process_response

    return response

@app.route('/datastories/view', methods=["POST"])
def view_datastory():
    response = {
        "success_response": None,
        "error_response": None
    }

    request_validity = validate_request(request, "VIEW_DATASTORIES", "json")

    if (not request_validity["is_valid"]):
        response["error_response"] = {
            "request_validity": request_validity
        }

        return json.dumps(response)

    process_response = process_view_datastory(request, request_validity["user"])

    if process_response["is_success"]:
        response["success_response"] = process_response
    else:
        response["error_response"] = process_response

    return response

app.run(host="0.0.0.0")