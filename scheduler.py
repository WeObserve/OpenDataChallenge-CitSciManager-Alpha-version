from apscheduler.schedulers.background import BackgroundScheduler
import time
from db.mongo import mongo_connection
from db.mongo.daos import files_dao
from aws_config import config
from pyspark.sql import SparkSession

env = "staging"

spark = SparkSession.builder \
            .appName("app_name") \
            .getOrCreate()

spark._jsc.hadoopConfiguration().set("fs.s3n.awsAccessKeyId", config[env].access_key_id)
spark._jsc.hadoopConfiguration().set("fs.s3n.awsSecretAccessKey", config[env].secret_access_key)
spark._jsc.hadoopConfiguration().set("fs.s3n.impl","org.apache.hadoop.fs.s3native.NativeS3FileSystem")
spark._jsc.hadoopConfiguration().set("fs.s3n.aws.credentials.provider","org.apache.hadoop.fs.s3a.BasicAWSCredentialsProvider")
spark._jsc.hadoopConfiguration().set("fs.s3n.endpoint", "us-west-2.amazonaws.com")

mongo_db_connection = mongo_connection.connect_to_db(env)[config[env].mongo_database]


def process_uploaded_files():
    print("Inside process_uploaded_files")

    processing_files_cursor = files_dao.get_files(mongo_db_connection, {"status": "PROCESSING"})

    if processing_files_cursor is not None and processing_files_cursor.count() != 0:
        print("There are some files still being processed hence skipping")
        return

    uploaded_files_cursor = files_dao.get_files(mongo_db_connection, {"file_type": "META_DATA", "status": "UPLOADED"})

    if uploaded_files_cursor is None or uploaded_files_cursor.count() == 0:
        print("There are no new meta data files uploaded hence skipping")
        return

    uploaded_file_to_process = uploaded_files_cursor[0]

    files_dao.update_file(mongo_db_connection, {"_id": uploaded_file_to_process["_id"]}, {"$set": {"status": "PROCESSING"}})

    bucket_name = uploaded_file_to_process["s3_link"][8:].split('.')[0]

    print('s3n://' + bucket_name + "/" + uploaded_file_to_process["relative_path"])

    df = spark.read.csv('s3n://' + bucket_name + "/" + uploaded_file_to_process["relative_path"], header=True).limit(1)

    files_dao.update_file(mongo_db_connection, {"_id": uploaded_file_to_process["_id"]},
                          {"$set": {"status": "PROCESSED", "headers": df.first().__fields__}})

scheduler = BackgroundScheduler({'apscheduler.timezone': 'Asia/Calcutta'})

job = scheduler.add_job(process_uploaded_files, 'interval', minutes = 1)

scheduler.start()

scheduler.print_jobs()

try:
    while True:
        time.sleep(1)
except(KeyboardInterrupt, SystemExit):
    scheduler.shutdown()