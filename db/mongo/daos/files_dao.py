def insert_file(db_connection, file):
    return db_connection["files"].insert_one(file)

def get_files_by_project_id(db_connection, project_id):
    return db_connection["files"].find({"project_id": project_id})