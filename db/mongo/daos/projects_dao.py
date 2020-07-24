def get_project_by_id(db_connection, id):
    return db_connection["projects"].find({"_id": id})[0]

def insert_project_using_txn(db_connection, project, session):
    return db_connection["projects"].insert_one(project, session=session)

def get_projects(db_connection, project_query_dict):
    return db_connection["projects"].find(project_query_dict)