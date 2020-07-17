import uuid
import traceback
from aws_config import config
import boto3
import pandas
import os
from db.mongo.daos import users_dao, projects_dao
import datetime

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