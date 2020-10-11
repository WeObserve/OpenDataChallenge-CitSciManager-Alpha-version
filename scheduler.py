from apscheduler.schedulers.background import BlockingScheduler
import time
from db.mongo import mongo_connection
from db.mongo.daos import files_dao, joins_dao, users_dao
from entities.user_entity import User
from aws_config import config
from pyspark.sql import SparkSession
import datetime
import pandas
import s3fs
import boto3

env = "staging"

def log_to_file(strng):
    log_file = open("./slog.txt", "a")
    log_file.write(strng)
    log_file.close()

log_to_file("About to start\n")

spark = SparkSession.builder \
            .appName("app_name") \
            .getOrCreate()

spark._jsc.hadoopConfiguration().set("fs.s3n.awsAccessKeyId", config[env].access_key_id)
spark._jsc.hadoopConfiguration().set("fs.s3n.awsSecretAccessKey", config[env].secret_access_key)
spark._jsc.hadoopConfiguration().set("fs.s3n.impl","org.apache.hadoop.fs.s3native.NativeS3FileSystem")
spark._jsc.hadoopConfiguration().set("fs.s3n.aws.credentials.provider","org.apache.hadoop.fs.s3a.BasicAWSCredentialsProvider")
spark._jsc.hadoopConfiguration().set("fs.s3n.endpoint", "us-west-2.amazonaws.com")

mongo_db_connection = mongo_connection.connect_to_db(env)[config[env].mongo_database]

log_to_file("spark setup done\n")

def send_join_done_email(created_user, env, s3_link, email_sender_address):
    log_to_file("Inside send_invitation_email\n")

    ses_client = boto3.client('ses',
                              aws_access_key_id=config[env].access_key_id,  # ["access_key_id"],
                              aws_secret_access_key=config[env].secret_access_key,  # ["secret_access_key"],
                              region_name="us-west-2"
                              )

    log_to_file("Got ses client\n")

    ses_response = ses_client.send_email(
        Destination={
            "ToAddresses": [created_user.email]
        },
        Message={
            "Body": {
                "Text": {
                    "Charset": "UTF-8",
                    "Data": "Join file link " + s3_link
                }
            },
            "Subject": {
                "Charset": "UTF-8",
                "Data": "Join complete message from Greendubs"
            }
        },
        Source=email_sender_address
    )

def process_uploaded_files():
    try:
        log_to_file("Inside process_uploaded_files\n")

        processing_files_cursor = files_dao.get_files(mongo_db_connection, {"status": "PROCESSING"})

        if processing_files_cursor is not None and processing_files_cursor.count() != 0:
            log_to_file("There are some files still being processed hence skipping\n")
            return

        processing_joins_cursor = joins_dao.get_joins(mongo_db_connection, {"status": "PROCESSING"})

        if processing_joins_cursor is not None and processing_joins_cursor.count() != 0:
            log_to_file("There are some joins still being processed hence skipping\n")
            return

        uploaded_files_cursor = files_dao.get_files(mongo_db_connection, {"file_type": "META_DATA", "status": "UPLOADED"})
        pending_joins_cursor = joins_dao.get_joins(mongo_db_connection, {"status": "PENDING"})

        if (uploaded_files_cursor is None or uploaded_files_cursor.count() == 0) and (pending_joins_cursor is None or pending_joins_cursor.count() == 0):
            log_to_file("There are no new meta data files uploaded and no pending joins hence skipping\n")

            return

        if uploaded_files_cursor is not None and uploaded_files_cursor.count() != 0:
            uploaded_file_to_process = uploaded_files_cursor[0]

            files_dao.update_file(mongo_db_connection, {"_id": uploaded_file_to_process["_id"]}, {"$set": {"status": "PROCESSING"}})

            bucket_name = uploaded_file_to_process["file_link"][8:].split('.')[0]

            index = 8

            for ch in uploaded_file_to_process["file_link"][8:]:
                if ch == '/':
                    break
                index = index + 1

            index = index + 1

            url = 's3n://' + bucket_name + "/" + uploaded_file_to_process["file_link"][index:]

            log_to_file(url + "\n")

            df = spark.read.csv(url, header=True).limit(1)

            files_dao.update_file(mongo_db_connection, {"_id": uploaded_file_to_process["_id"]},
                                  {"$set": {"status": "PROCESSED", "headers": df.first().__fields__}})

            log_to_file("uploaded file processing done\n")

        else:
            pending_join_to_process = pending_joins_cursor[0]

            joins_dao.update_join(mongo_db_connection, {"_id": pending_join_to_process["_id"]}, {"$set": {"status": "PROCESSING"}})

            files_to_be_joined_cursor = files_dao.get_files(mongo_db_connection, {
                "_id": {
                    "$in": [pending_join_to_process["file_id_1"], pending_join_to_process["file_id_2"]]
                },
                "status": "PROCESSED",
                "file_type": "META_DATA"
            })

            if files_to_be_joined_cursor is None or files_to_be_joined_cursor.count() != 2:
                log_to_file("No files found for joining hence skipping\n")

                joins_dao.update_join(mongo_db_connection, {"_id": pending_join_to_process["_id"]},
                                      {"$set": {"status": "PROCESSED"}})
                return

            file1 = None
            file2 = None

            for file in files_to_be_joined_cursor:
                if str(file["_id"]) == str(pending_join_to_process["file_id_1"]):
                    file1 = file
                    continue
                if str(file["_id"]) == str(pending_join_to_process["file_id_2"]):
                    file2 = file

            bucket_name_for_file_1 = file1["file_link"][8:].split('.')[0]
            bucket_name_for_file_2 = file2["file_link"][8:].split('.')[0]

            index = 8

            for ch in file1["file_link"][8:]:
                if ch == '/':
                    break
                index = index + 1

            index = index + 1

            url_for_file_1 = 's3n://' + bucket_name_for_file_1 + "/" + file1["file_link"][index:]


            index = 8

            for ch in file2["file_link"][8:]:
                if ch == '/':
                    break
                index = index + 1

            index = index + 1

            url_for_file_2 = 's3n://' + bucket_name_for_file_2 + "/" + file2["file_link"][index:]


            log_to_file(url_for_file_1 + "\n")

            log_to_file(url_for_file_2 + "\n")


            df1 = spark.read.csv(url_for_file_1, header=True)
            df2 = spark.read.csv(url_for_file_2, header=True)

            df1 = df1.select(pending_join_to_process["columns_for_file_1"])
            df2 = df2.select(pending_join_to_process["columns_for_file_2"])

            new_column_names_for_df2 = []
            for column in df2.columns:
                new_column_names_for_df2.append('b' + column)

            df2 = df2.toDF(*new_column_names_for_df2)

            df = df1.join(df2, df1[pending_join_to_process["join_column_for_file_1"]] == df2['b' + pending_join_to_process["join_column_for_file_2"]], how="inner")

            columns = []
            rep_count = 0
            for column in df.columns:
                if column in columns:
                    df = df.withColumnRenamed(column, str(rep_count) + column)
                    columns.append(str(rep_count) + column)
                    continue
                columns.append(column)

            df.show()

            log_to_file("join done...trying to upload to s3\n")

            pd_df = df.toPandas()

            bytes_to_write = pd_df.to_csv(None, index=False).encode()

            fs = s3fs.S3FileSystem(key=config[env].access_key_id, secret=config[env].secret_access_key)

            with fs.open("s3://" + bucket_name_for_file_1 + "/joins/" + str(pending_join_to_process["_id"]) + ".csv", 'wb') as f:
                f.write(bytes_to_write)

            file_dict = {
                "name": str(pending_join_to_process["_id"]) + ".csv",
                "file_link": "https://" + bucket_name_for_file_1 + ".s3-us-west-2.amazonaws.com/joins/" + str(pending_join_to_process["_id"]) + ".csv",
                "project_id": pending_join_to_process["project_id"],
                "uploaded_by_user_id": pending_join_to_process["user_id"],
                "status": "PROCESSED",
                "headers": df.columns,
                "file_type": "META_DATA"
            }

            files_dao.insert_file(mongo_db_connection, file_dict)

            user = users_dao.get_users(mongo_db_connection, {"_id": pending_join_to_process["user_id"]})[0]

            send_join_done_email(User(user), env, file_dict["file_link"], config[env].email_sender_address)

            joins_dao.update_join(mongo_db_connection, {"_id": pending_join_to_process["_id"]}, {"$set": {"status": "PROCESSED"}})

            log_to_file("pending join processing done\n")

    except Exception as e:
        log_to_file(str(e))

if __name__ == '__main__':
    log_to_file("\nI reached this")

    scheduler = BlockingScheduler({'apscheduler.timezone': 'Asia/Calcutta'})

    job = scheduler.add_job(process_uploaded_files, 'interval', minutes = 1, next_run_time=datetime.datetime.now())

    scheduler.start()

    scheduler.print_jobs()

    try:
        while True:
            time.sleep(1)
    except(KeyboardInterrupt, SystemExit):
        scheduler.shutdown()