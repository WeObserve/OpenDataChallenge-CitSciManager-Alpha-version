def get_project_by_id(db_connection, id):
    return db_connection["projects"].find({"_id": id})[0]