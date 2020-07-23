from db.mongo.daos import user_project_mappings_dao
from bson import ObjectId
from transactional_services import project_transactional_service

def validate_that_project_name_created_by_this_user_does_not_exist(db_connection, user_id, create_project_request_dto):
    print("Inside validate_that_project_name_created_by_this_user_does_not_exist")

    user_project_mapping_query = {
        "user_id": ObjectId(user_id),
        "project_name": create_project_request_dto.name,
        "mapping_type": "CREATOR"
    }

    user_project_mappings_as_cursor = user_project_mappings_dao.get_user_project_mapping(db_connection, user_project_mapping_query)

    if user_project_mappings_as_cursor is not None and user_project_mappings_as_cursor.count() != 0:
        raise Exception("A project by the same name has already been created by this user")


def create_project(db_connection, user_id, create_project_request_dto, env, db_connection_client):
    print("Inside create_project service")

    #check that there is no project with the same name created by this user
    validate_that_project_name_created_by_this_user_does_not_exist(db_connection, user_id, create_project_request_dto)

    #create project and then a user_project_mapping in the same transaction
    return project_transactional_service.create_project(db_connection, user_id, create_project_request_dto, db_connection_client)