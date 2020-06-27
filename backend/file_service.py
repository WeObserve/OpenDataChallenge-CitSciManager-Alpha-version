import boto3
from aws_config import aws_config
import json
import os
import datetime
from db.mongo.daos import files_dao

def process_upload_file(db_connection, request, user, env):
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

    user_uploading_files = user

    for file_key in request.files:
        try:
            file = request.files[file_key]

            #create new filename
            filename = request.form["uuid"] + "/" + file.filename

            #temporarily save file on server
            file.save(file.filename)

            #s3 upload the temporarily saved file to greendub-uploaded-files-mvp bucket
            s3_response = s3_client.upload_file("./" + file.filename, aws_config[env]["bucket_name"], filename)

            file_document_to_be_created = {
                "original_filename": file.filename,
                "s3_file_path": filename,
                "sender_id": user_uploading_files["_id"],
                "license": request.form["license"],
                "project_id": user_uploading_files["project_id"],
                "created_at": datetime.datetime.utcnow(),
                "meta_data": {
                    "location_name": request.form["location_name"],
                    "latitude": request.form["latitude"],
                    "longitude": request.form["longitude"]
                }
            }

            #make an entry for the file in db
            #optimise this and move upload as well as insert into a txn
            print(files_dao.insert_file(db_connection, file_document_to_be_created))

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

def process_download_file(db_connection, request, user, env):
    process_response = {
        "status": "SUCCESS",
        "is_success": True,
        "files": []
    }

    user_downloading_files = user

    files_associated_with_project = files_dao.get_files_by_project_id(db_connection, user_downloading_files["project_id"])
    files_to_be_downloaded = []

    #filter files by project id
    for file in files_associated_with_project:
        if file["project_id"] == user_downloading_files["project_id"]:
            s3_link = "https://greendub-uploaded-files-mvp.s3-us-west-2.amazonaws.com/" + file["s3_file_path"]
            files_to_be_downloaded.append({
                "s3_link": s3_link,
            })

    process_response["files"] = files_to_be_downloaded

    return process_response