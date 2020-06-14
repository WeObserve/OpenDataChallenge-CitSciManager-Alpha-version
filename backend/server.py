import flask
from flask import request
import json
import datetime
import boto3
from aws_config import aws_config
import os
import pandas
import uuid

app = flask.Flask(__name__)

app.config["DEBUG"] = True

def validate_request(request, request_type, request_body_type):
    request_validity = {
        "is_valid": True,
        "reason": None
    }

    uuid = None

    if request_body_type == "form":
        # check if uuid is present in request body
        if "uuid" not in request.form:
            request_validity["is_valid"] = False
            request_validity["reason"] = "UUID is amandatory"
            return request_validity

        # get uuid from the request body
        uuid = request.form["uuid"]
    elif request_body_type == "json":
        if not request.is_json:
            request_validity["is_valid"] = False
            request_validity["reason"] = "request should be a valid json"
            return request_validity

        request_body = request.get_json()

        # check if uuid is present in request body
        if request_body is None or "uuid" not in request_body:
            request_validity["is_valid"] = False
            request_validity["reason"] = "UUID is amandatory"
            return request_validity

        # get uuid from the request body
        uuid = request_body["uuid"]

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
            if (user["type"] == "sender" and request_type in ("UPLOAD_FILES", "VIEW_DATASTORIES")):
                request_validity["user"] = user
                return request_validity
            elif (user["type"] == "collector" and request_type in ("DOWNLOAD_FILES", "INVITE_USERS", "CREATE_DATASTORY", "VIEW_DATASTORIES")):
                request_validity["user"] = user
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

def process_invite_users(request, user):
    process_response = {
        "status": "SUCCESS",
        "is_success": True,
        "message": "Users invited"
    }

    if (request.files is None or len(request.files) == 0):
        return {
            "status": "SUCCESS",
            "is_success": True,
            "message": "No user invitation files found in request"
        }

    try:
        ses_client = boto3.client('ses',
                        aws_access_key_id=aws_config["access_key_id"],
                        aws_secret_access_key=aws_config["secret_access_key"],
                        region_name="us-west-2"
                    )
        # load users_table
        users = json.load(
            open("./db/users_table.json", "r"))

        user_sending_invitation = user
        existing_user_emails_for_this_project = {
            "sender": [],
            "collector": []
        }

        # collect senders and collectors emails for this project
        for user in users:
            if user["project_id"] == user_sending_invitation["project_id"]:
                existing_user_emails_for_this_project[user["type"]].append(user["email"])

        user_emails_to_send_invitation_to = []
        users_to_be_created = []

        for file_key in request.files:
            try:
                file = request.files[file_key]

                #create new filename
                filename = request.form["uuid"] + "/" + file.filename

                #temporarily save file on server
                file.save(file.filename)

                #create a pandas data frame from the csv file
                user_invitation_file_df = pandas.read_csv(open("./" + file.filename, "r"))

                for index, row in user_invitation_file_df.iterrows():
                    user_email = row["email"]
                    user_name = row["name"]
                    user_type = row["type"]

                    if (user_email in existing_user_emails_for_this_project[user_type]):
                        continue

                    user_to_be_created = {
                        "name": user_name,
                        "email": user_email,
                        "type": user_type,
                        "project_id": user_sending_invitation["project_id"],
                        "uuid": uuid.uuid1().hex
                    }

                    users_to_be_created.append(user_to_be_created)
                    user_emails_to_send_invitation_to.append(user_to_be_created["email"])

                os.remove("./" + file.filename)
            except Exception as e:
                print(e)

        # send email to users that are to be created using ses
        ses_response = ses_client.send_email(
            Destination={
                "ToAddresses": user_emails_to_send_invitation_to
            },
            Message={
                "Body": {
                    "Text": {
                        "Charset": "UTF-8",
                        "Data": "You were invited to THE_LINK_GOES_HERE by " + user_sending_invitation["email"] + " to contribute to project " + user_sending_invitation["project_id"]
                    }
                },
                "Subject": {
                    "Charset": "UTF-8",
                    "Data": "Invitation from Greendubs"
                }
            },
            Source="anindyapandey@gmail.com"
        )

        #add users to be created to the list of users
        users = users + users_to_be_created

        #make entries for the users that were created in db
        #must be replaced by a proper db
        json.dump(users, open("./db/users_table.json", "w"))

        return process_response
    except Exception as e:
        print(e)
        process_response["is_success"] = False
        process_response["status"] = "FAILED"
        process_response["message"] = str(e)
        return process_response

def process_download_file(request):
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

def process_create_datastory(request, user):
    process_response = {
        "status": "SUCCESS",
        "is_success": True
    }

    if ("datastory_name" not in request.form or len(request.form["datastory_name"]) == 0
        or "datastory_content" not in request.form or len(request.form["datastory_content"]) == 0):
        return {
            "status": "FAILED",
            "is_success": False,
            "message": "datastory_name and datastory_content are mandatory"
        }

    # load datastories_table
    datastories = json.load(
        open("./db/datastories_table.json", "r"))

    user_creating_datastory = user

    datastories_created_for_this_project = []

    # collect datastory names of datastories created for this project
    for datastory in datastories:
        if datastory["project_id"] == user_creating_datastory["project_id"]:
            datastories_created_for_this_project.append(datastory["name"])

    if (request.form["datastory_name"] in datastories_created_for_this_project):
        return {
            "status": "FAILED",
            "is_success": False,
            "message": "a datastory by this name already exists for this project"
        }

    datastory_to_be_created = {
        "name": request.form["datastory_name"],
        "content": request.form["datastory_content"],
        "project_id": user_creating_datastory["project_id"],
        "user_uuid": user_creating_datastory["uuid"]
    }

    datastories.append(datastory_to_be_created)

    json.dump(datastories, open("./db/datastories_table.json", "w"))

    return process_response

def process_view_datastory(request, user):
    process_response = {
        "status": "SUCCESS",
        "is_success": True
    }

    request_body = request.get_json()

    if (("get_all_datastories" not in request_body or not request_body["get_all_datastories"]) and ("datastory_name" not in request_body or len(request_body["datastory_name"]) == 0)):
        process_response["status"] = "FAILED"
        process_response["is_success"] = False
        process_response["message"] = "request body must have either get_all_datastories field set to true or must have a non empty datastory_name field"

    # load datastories_table
    datastories = json.load(
        open("./db/datastories_table.json", "r"))

    user_viewing_datastory = user

    datastories_created_for_this_project = []

    # collect datastory names of datastories created for this project
    for datastory in datastories:
        if datastory["project_id"] == user_viewing_datastory["project_id"]:
            datastories_created_for_this_project.append(datastory)

    if ("get_all_datastories" in request_body and request_body["get_all_datastories"]):
        process_response["datastories"] = datastories_created_for_this_project
    else:
        datastories_with_given_name = []
        for datastory in datastories_created_for_this_project:
            if datastory["name"] == request_body["datastory_name"]:
                datastories_with_given_name.append(datastory)
        process_response["datastories"] = datastories_with_given_name

    return process_response

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

app.run()