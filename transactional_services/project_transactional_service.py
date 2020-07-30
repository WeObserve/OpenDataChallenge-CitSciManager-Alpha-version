from db.mongo.daos import user_project_mappings_dao
from db.mongo.daos import projects_dao, users_dao
from entities.project_entity import Project
from bson import ObjectId
from dtos.controllers.responses.create_project_response_dto import CreateProjectResponseDTO


def create_project(db_connection, user_id, create_project_request_dto, db_connection_client):
    project_entity = None

    with db_connection_client.start_session() as session:
        with session.start_transaction():
            project_dict = {
                "name": create_project_request_dto.name,
                "license": create_project_request_dto.license
            }

            project_insert_one_result = projects_dao.insert_project_using_txn(db_connection, project_dict, session)

            project_dict["_id"] = project_insert_one_result.inserted_id

            project_entity = Project(project_dict)

            user_entity = users_dao.get_users(db_connection, {"_id": ObjectId(user_id)})[0]

            user_project_mapping_dict = {
                "user_id": user_entity["_id"],
                "email": user_entity["email"],
                "project_id": project_dict["_id"],
                "project_name": project_dict["name"],
                "mapping_type": "CREATOR"
            }

            user_project_mapping_insert_one_result = user_project_mappings_dao.insert_user_project_mapping_using_txn(db_connection, user_project_mapping_dict, session)

    return CreateProjectResponseDTO({
        "code": 200,
        "message": "SUCCESS",
        "project": project_entity
    })



