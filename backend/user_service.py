import uuid
import json
from aws_config import aws_config
import boto3
import pandas
import os

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