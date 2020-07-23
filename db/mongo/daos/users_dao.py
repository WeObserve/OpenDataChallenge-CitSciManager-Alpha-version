def get_user_by_uuid(db_connection, uuid):
    return db_connection["users"].find({"uuid": uuid})[0]

def get_users_by_project_id(db_connection, project_id):
    return db_connection["users"].find({"project_id": project_id})

def insert_users(db_connection, users):
    return db_connection["users"].insert_many(users)

def insert_user(db_connection, user):
    return db_connection["users"].insert_one(user)

def get_users(db_connection, user):
    return db_connection["users"].find(user)