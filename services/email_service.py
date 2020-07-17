import boto3
from aws_config import config


class EmailService:
    def __init__(self):
        pass

    def send_email_datastory(self,datastory_details, env):
        try:
            ses_client = boto3.client('ses',
                              aws_access_key_id=config[env].access_key_id,
                              aws_secret_access_key=config[env].secret_access_key,
                              region_name="us-west-2"
                              )

            print("Got ses client")
            for sender, details in datastory_details.get('senders').items():
            # send email to senders
                ses_response = ses_client.send_email(
                    Destination={
                        "ToAddresses": [details["email"]]
                    },
                    Message={
                        "Body": {
                            "Text": {
                            "Charset": "UTF-8",
                            "Data": "Thank you "+ details.get('name')+
                                " for your contribution to the project " + datastory_details.get('name') +
                                ". Click the link to view the published datastory. http://127.0.0.1:5000/datastories/"
                                + datastory_details.get('unique_url')
                            }
                        },
                        "Subject": {
                            "Charset": "UTF-8",
                            "Data": "Thank you from Greendubs" + datastory_details.get('name')
                        }
                    },
                    Source="kiranmayi.klc@gmail.com"
                )
        except Exception as e:
            print(e)
