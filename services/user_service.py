import uuid
import traceback
from aws_config import config
import boto3
import pandas
import os
from db.mongo.daos import users_dao, projects_dao, user_project_mappings_dao
import datetime
import hashlib
from entities.user_entity import User
import jwt
from bson import ObjectId
from transactional_services import user_transactional_service

def process_invite_users(db_connection, request, user, env):
    print("Inside process_invite_users")

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
                        aws_access_key_id=config[env].access_key_id,                  #["access_key_id"],
                        aws_secret_access_key=config[env].secret_access_key,        #["secret_access_key"],
                        region_name="us-west-2"
                    )

        print("Got ses client")

        users = users_dao.get_users_by_project_id(db_connection, user["project_id"])

        print("Users for this project id")
        print(users)

        project = projects_dao.get_project_by_id(db_connection, user["project_id"])

        print("Project:")
        print(project)

        user_sending_invitation = user

        existing_user_emails_for_this_project = {
            "SENDER": [],
            "COLLECTOR": []
        }

        # collect senders and collectors emails for this project
        for user in users:
            existing_user_emails_for_this_project[user["type"]].append(user["email"])

        print("Existing user emails for this project:")
        print(existing_user_emails_for_this_project)

        users_to_be_created = []

        for file_key in request.files:
            try:
                file = request.files[file_key]

                #create new filename
                filename = request.form["uuid"] + "/" + file.filename

                #temporarily save file on server
                file.save(file.filename)

                print("Temporarily saved file on server")

                #create a pandas data frame from the csv file
                user_invitation_file_df = pandas.read_csv(open("./" + file.filename, "r", encoding='utf-8'))

                print("Read file into df")
                print(user_invitation_file_df)
                print(user_invitation_file_df.columns)


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
                        "uuid": uuid.uuid1().hex,
                        "created_at": datetime.datetime.utcnow()
                    }

                    users_to_be_created.append(user_to_be_created)

                os.remove("./" + file.filename)
            except Exception as e:
                print(e)

        #make documents for the users that were created in db
        users_dao.insert_users(db_connection, users_to_be_created)

        for user_created in users_to_be_created:
            # send email to users that are to be created using ses
            ses_response = ses_client.send_email(
                Destination={
                    "ToAddresses": [user_created["email"]]
                },
                Message={
                    "Body": {
                        "Text": {
                            "Charset": "UTF-8",
                            "Data": "You were invited to THE_LINK_GOES_HERE by " + user_sending_invitation[
                                "email"] + " to contribute to project " + project["name"]
                                    + ". Your uuid for the role of " + user_created["type"]
                                    + " is " + user_created["uuid"]
                        }
                    },
                    "Subject": {
                        "Charset": "UTF-8",
                        "Data": "Invitation from Greendubs"
                    }
                },
                Source="anindyapandey@gmail.com"
            )

        return process_response
    except Exception as e:
        print(traceback.format_exc())
        process_response["is_success"] = False
        process_response["status"] = "FAILED"
        process_response["message"] = str(e)
        return process_response


def send_invitation_email(created_user, env, login_page_url_with_creds, email_sender_address):
    print("Inside send_invitation_email")

    ses_client = boto3.client('ses',
                              aws_access_key_id=config[env].access_key_id,  # ["access_key_id"],
                              aws_secret_access_key=config[env].secret_access_key,  # ["secret_access_key"],
                              region_name="us-west-2"
                              )

    print("Got ses client")

    ses_response = ses_client.send_email(
        Destination={
            "ToAddresses": [created_user.email]
        },
        Message={
            "Body": {
                "Text": {
                    "Charset": "UTF-8",
                    "Data": "You are invited to " + login_page_url_with_creds
                }
            },
            "Subject": {
                "Charset": "UTF-8",
                "Data": "Invitation from Greendubs"
            }
        },
        Source=email_sender_address
    )

def create_user(db_connection, create_user_request_dto, env, master_secret_key, login_page_url, email_sender_address):
    print("Inside create_user service")

    users_with_given_email_as_cursor = users_dao.get_users(db_connection, {"email": create_user_request_dto.email})

    if users_with_given_email_as_cursor is not None and users_with_given_email_as_cursor.count() != 0:
        raise Exception("User with given email id already exists")

    user_dict, encoded_creds = populate_user_dict_from_create_user_request_dto(create_user_request_dto, master_secret_key)
    print(user_dict)

    inserted_user_id = users_dao.insert_user(db_connection, user_dict).inserted_id

    user_dict["_id"] = inserted_user_id

    created_user = User(user_dict)

    send_invitation_email(created_user, env, login_page_url + encoded_creds, email_sender_address)

    return created_user

def populate_user_dict_from_create_user_request_dto(create_user_request_dto, master_secret_key):
    print("Inside populate_user_dict_from_create_user_request_dto")

    auto_generated_user_password = uuid.uuid1().hex

    encoded_creds = jwt.encode({"email": create_user_request_dto.email, "password": auto_generated_user_password}, master_secret_key, algorithm='HS256').decode('utf-8')

    print("generated encoded_creds: " + encoded_creds)

    return {
        "email": create_user_request_dto.email,
        "password": hashlib.sha256(auto_generated_user_password.encode('utf-8')).hexdigest(),
        "name": create_user_request_dto.name,
        "organisation_name": create_user_request_dto.organisation_name,
        "organisation_affiliation": create_user_request_dto.organisation_affiliation
    }, encoded_creds


def check_if_user_creation_is_required(db_connection, invite_user_request_dto):
    print("Inside check_if_user_creation_is_required")

    user_cursor = users_dao.get_users(db_connection, {"email": invite_user_request_dto.email})

    if user_cursor is None or user_cursor.count() == 0:
        return True, {}

    return False, user_cursor[0]

def validate_that_user_can_invite_others_for_this_project(db_connection, invite_user_request_dto, user_id):
    print("Inside validate_that_user_can_invite_others_for_this_project")

    user_project_mapping_cursor = user_project_mappings_dao.get_user_project_mapping(db_connection, {
        "project_name": invite_user_request_dto.project_name,
        "user_id": ObjectId(user_id),
        "mapping_type": {
            "$in": ["COLLECTOR", "CREATOR"]
        }
    })

    if user_project_mapping_cursor is None or user_project_mapping_cursor.count() == 0:
        raise Exception("User can't invite users for this project")

    return user_project_mapping_cursor[0]["project_id"]

def check_if_upm_creation_is_required(db_connection, invite_user_request_dto):
    print("Inside check_if_upm_creation_is_required")

    upm_cursor = user_project_mappings_dao.get_user_project_mapping(db_connection, {
        "project_name": invite_user_request_dto.project_name,
        "email": invite_user_request_dto.email
    })

    if upm_cursor is None or upm_cursor.count() == 0:
        return True, False

    if invite_user_request_dto.mapping_type == "COLLECTOR":
        if upm_cursor[0]["mapping_type"] == "SENDER":
            return False, True
        elif upm_cursor[0]["mapping_type"] == "COLLECTOR":
            raise Exception("This user for this project already exists in this role")
        elif upm_cursor[0]["mapping_type"] == "CREATOR":
            raise Exception("This user already has these permissions for this project")

    if invite_user_request_dto.mapping_type == "SENDER":
        if upm_cursor[0]["mapping_type"] == "SENDER":
            raise Exception("This user for this project already exists in this role")
        elif upm_cursor[0]["mapping_type"] == "COLLECTOR":
            raise Exception("This user already has these permissions for this project")
        elif upm_cursor[0]["mapping_type"] == "CREATOR":
            raise Exception("This user already has these permissions for this project")

    raise Exception("Something is wrong")

def invite_user(db_connection, invite_user_request_dto, env, master_secret_key, login_page_url, email_sender_address, user_id, db_connection_client):
    print("Inside invite_user service")

    #validate that user can invite others for this project
    project_id = validate_that_user_can_invite_others_for_this_project(db_connection, invite_user_request_dto, user_id)

    is_user_creation_required = None
    is_upm_creation_required = None
    is_upm_update_required = None
    invited_user = None

    #check if user creation is required
    is_user_creation_required, invited_user = check_if_user_creation_is_required(db_connection, invite_user_request_dto)

    if is_user_creation_required:
       is_upm_creation_required = True
    else:
        is_upm_creation_required, is_upm_update_required = check_if_upm_creation_is_required(db_connection, invite_user_request_dto)

    invite_user_response_dto, encoded_creds = user_transactional_service.invite_user(db_connection, invite_user_request_dto, is_user_creation_required, is_upm_creation_required, is_upm_update_required, invited_user, db_connection_client, master_secret_key, project_id)

    if encoded_creds is not None:
        send_invitation_email(User(invite_user_response_dto.user), env, login_page_url + encoded_creds, email_sender_address)

    return invite_user_response_dto