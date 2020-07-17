from pymongo import MongoClient
from aws_config import config


def connect_to_db(env):
    aws_config_env = config[env]
    db_connection = MongoClient(
        aws_config_env.mongo_host,
        username=aws_config_env.mongo_username,
        password=aws_config_env.mongo_password,
        maxPoolSize=50,
        wtimeOut=2500
    )

    return db_connection[aws_config_env.mongo_database]