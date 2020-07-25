def insert_file(db_connection, file):
    return db_connection["files"].insert_one(file)

def get_files_by_project_id(db_connection, project_id):
    return db_connection["files"].find({"project_id": project_id})

def get_files(db_connection, file):
    return db_connection["files"].find(file)

def insert_files(db_connection, files):
    return db_connection["files"].insert_many(files)

def update_file(db_connection, file, update):
    return db_connection["files"].update_one(file, update)