def insert_user_project_mapping_using_txn(db_connection, user_project_mapping, session):
    return db_connection["user_project_mappings"].insert_one(user_project_mapping, session=session)

def get_user_project_mapping(db_connection, user_project_mapping):
    return db_connection["user_project_mappings"].find(user_project_mapping)