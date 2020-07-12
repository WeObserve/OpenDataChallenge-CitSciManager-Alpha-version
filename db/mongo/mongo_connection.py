import pymongo
from aws_config import aws_config

def connect_to_db(env):
    global aws_config
    aws_config_env = aws_config[env]
    db_connection = pymongo.MongoClient(
        aws_config_env["mongo_host"],
        username=aws_config_env["mongo_username"],
        password=aws_config_env["mongo_password"]
    )

    return db_connection[aws_config_env["mongo_database"]]