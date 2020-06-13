import flask
from flask import request
import json

app = flask.Flask(__name__)

app.config["DEBUG"] = True

@app.route('/', methods=["GET"])
def home():
    return "wow"


def validate_request(request):
    request_validity = {
        "is_valid": True,
        "reason": None
    }

    # check if uuid is present in request body
    if "uuid" not in request.form:
        request_validity["is_valid"] = False
        request_validity["reason"] = "UUID is amandatory"
        return request_validity

    # get uuid from the request body
    uuid = request.form["uuid"]

    if uuid is None or len(uuid) == 0:
        request_validity["is_valid"] = False
        request_validity["reason"] = "UUID is amandatory"
        return request_validity

    '''
    this is a very bad way of authentication or authorisation
    not recommended at all
    on top of that its an even worse way of handling data
    only doing this since we don't have enough time to set up a proper db and test
    and configure connection pools
    '''

    #load users_table
    users = json.load(
        open("./db/users_table.json", "r"))

    #look for the given uuid
    for user in users:
        if user["uuid"] == uuid:
            return request_validity

    request_validity["is_valid"] = False
    request_validity["reason"] = "uuid is invalid"

    return request_validity

@app.route('/file', methods=["POST"])
def upload_file():
    request_validity = validate_request(request)

    if (not request_validity["is_valid"]):
        return request_validity["reason"]

    process_response = process_upload_file(request)

    return process_response["status"]

app.run()