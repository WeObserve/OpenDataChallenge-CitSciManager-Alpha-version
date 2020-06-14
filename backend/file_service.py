import boto3
from aws_config import aws_config
import json
import os
import datetime

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