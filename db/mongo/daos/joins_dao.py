def insert_joins(db_connection, joins):
    return db_connection["joins"].insert_many(joins)

def get_joins(db_connection, join_dict):
    return db_connection["joins"].find(join_dict)


def update_join(db_connection, join_dict, update):
    return db_connection["joins"].update_one(join_dict, update)