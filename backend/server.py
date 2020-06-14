import flask
from flask import request
import json
import datetime
import boto3
from aws_config import aws_config
import os

app = flask.Flask(__name__)

app.config["DEBUG"] = True

def validate_request(request, request_type):
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
            if (user["type"] == "sender" and request_type == "UPLOAD_FILES") or (user["type"] == "collector" and request_type == "DOWNLOAD_FILES"):
                return request_validity
            else:
                request_validity["is_valid"] = False
                request_validity["reason"] = "user cannot perform requested action"
                return request_validity

    request_validity["is_valid"] = False
    request_validity["reason"] = "uuid is invalid"

    return request_validity


def process_upload_file(request):
    process_response = {
        "status": "SUCCESS",
        "is_success": True,
        "message": "All files uploaded"
    }

    if (request.files is None or len(request.files) == 0):
        return {
            "status": "SUCCESS",
            "is_success": True,
            "message": "No files uploaded since no files found in request"
        }

    process_response["number_of_files_to_be_uploaded"] = len(request.files)
    process_response["number_of_files_uploaded"] = 0
    process_response["files_that_could_not_be_uploaded"] = []
    process_response["reasons"] = []

    s3_client = boto3.client('s3',
                             aws_access_key_id=aws_config["access_key_id"],
                             aws_secret_access_key=aws_config["secret_access_key"],
                             )
    # load users_table
    users = json.load(
        open("./db/users_table.json", "r"))

    user_uploading_files = None

    # look for the given uuid
    for user in users:
        if user["uuid"] == request.form["uuid"]:
            user_uploading_files = user

    for file_key in request.files:
        try:
            file = request.files[file_key]

            #create new filename
            filename = request.form["uuid"] + "/" + file.filename

            #temporarily save file on server
            file.save(file.filename)

            #s3 upload the temporarily saved file to greendub-uploaded-files-mvp bucket
            s3_response = s3_client.upload_file("./" + file.filename, aws_config["bucket_name"], filename)

            #load files_table
            files = json.load(open("./db/files_table.json", "r"))

            files.append({
                "original_filename": file.filename,
                "s3_file_path": filename,
                "user_uuid": request.form["uuid"],
                "license": request.form["license"],
                "project": user_uploading_files["project_id"],
                "meta_data": {
                    "file_created_at": datetime.datetime.fromtimestamp(
                        float(int(request.form["time"])/1000)).strftime('%Y-%m-%d %H:%M:%S.%f'),
                    "location_name": request.form["location_name"],
                    "latitude": request.form["latitude"],
                    "longitude": request.form["longitude"]
                }
            })

            #make an entry for the file in db
            #must be replaced by a proper db
            json.dump(files, open("./db/files_table.json", "w"))

            process_response["number_of_files_uploaded"] = process_response["number_of_files_uploaded"] + 1
            os.remove("./" + file.filename)
        except Exception as e:
            print(e)
            process_response["files_that_could_not_be_uploaded"].append(request.files[file_key].filename)
            process_response["reasons"].append(str(e))

    if process_response["number_of_files_uploaded"] != process_response["number_of_files_to_be_uploaded"]:
        process_response["status"] = "PARTIAL_SUCCESS"

    if process_response["number_of_files_uploaded"] == 0:
        process_response["status"] = "FAILED"
        process_response["is_success"] = False

    return process_response

def process_download_response(request):
    process_response = {
        "status": "SUCCESS",
        "is_success": True,
        "files": []
    }

    # load users_table
    users = json.load(
        open("./db/users_table.json", "r"))

    user_downloading_files = None

    # look for the given uuid
    for user in users:
        if user["uuid"] == request.form["uuid"]:
            user_downloading_files = user

    # load files_table
    files = json.load(open("./db/files_table.json", "r"))

    files_to_be_downloaded = []

    #filter files by project id
    for file in files:
        if file["project"] == user_downloading_files["project_id"]:
            file["s3_link"] = "https://greendub-uploaded-files-mvp.s3-us-west-2.amazonaws.com/" + file["s3_file_path"]
            files_to_be_downloaded.append(file)

    process_response["files"] = files_to_be_downloaded

    return process_response

@app.route('/file', methods=["POST"])
def upload_file():
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

@app.route('/file', methods=["GET"])
def download_file():
    response = {
        "success_response": None,
        "error_response": None
    }

    request_validity = validate_request(request, "DOWNLOAD_FILES")

    if (not request_validity["is_valid"]):
        response["error_response"] = {
            "request_validity": request_validity
        }

        return json.dumps(response)

    process_response = process_download_response(request)

    if process_response["is_success"]:
        response["success_response"] = process_response
    else:
        response["error_response"] = process_response

    return response

app.run()