from db.mongo.daos import user_project_mappings_dao, projects_dao
from bson import ObjectId
from transactional_services import project_transactional_service
from dtos.controllers.responses.fetch_projects_response_dto import FetchProjectsResponseDTO
from entities.project_entity import Project

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


def fetch_project_id_to_user_project_mapping_type_map(db_connection, user_id, fetch_projects_request_dto):
    print("Inside fetch_project_id_to_user_project_mapping_type_map")

    possible_user_project_mapping_types = ["CREATOR", "COLLECTOR", "SENDER"]

    consider_user_project_mapping_types = False
    user_project_mapping_query_dict = {
        "user_id": ObjectId(user_id)
    }

    for possible_user_project_mapping_type in possible_user_project_mapping_types:
        if possible_user_project_mapping_type not in fetch_projects_request_dto.user_project_mapping_types:
            consider_user_project_mapping_types = True
            break

    if consider_user_project_mapping_types:
        user_project_mapping_query_dict["mapping_type"] = {"$in": fetch_projects_request_dto.user_project_mapping_types}

    print(user_project_mapping_query_dict)

    user_project_mapping_cursor = user_project_mappings_dao.get_user_project_mapping(db_connection, user_project_mapping_query_dict)

    if user_project_mapping_cursor is None or user_project_mapping_cursor.count() == 0:
        print("No user_project_mappings found")
        return {}

    project_id_to_user_project_mapping_type_map = {}

    for user_project_mapping_dict in user_project_mapping_cursor:
        project_id_to_user_project_mapping_type_map[str(user_project_mapping_dict["project_id"])] = user_project_mapping_dict["mapping_type"]

    return project_id_to_user_project_mapping_type_map

def fetch_projects(db_connection, user_id, fetch_projects_request_dto, env):
    print("Inside fetch_projects service")

    #fetch project_id to user_project_mapping_type map
    project_id_to_user_project_mapping_type_map = fetch_project_id_to_user_project_mapping_type_map(db_connection, user_id, fetch_projects_request_dto)\

    if not project_id_to_user_project_mapping_type_map:
        return FetchProjectsResponseDTO({
            "code": 200,
            "message": "SUCCESS",
            "projects": []
        })

    #build list of ObjectId project_ids
    project_ids = []

    for project_id in project_id_to_user_project_mapping_type_map:
        project_ids.append(ObjectId(project_id))

    #fetch projects for project_ids in the map populated in previous step
    project_cursor = projects_dao.get_projects(db_connection, {"_id": {"$in": project_ids}})

    if project_cursor is None or project_cursor.count() == 0:
        return FetchProjectsResponseDTO({
            "code": 200,
            "message": "SUCCESS",
            "projects": []
        })

    project_entities = []

    for project_dict in project_cursor:
        project_dict["user_project_mapping_type"] = project_id_to_user_project_mapping_type_map[str(project_dict["_id"])]
        project_entities.append(Project(project_dict))

    return FetchProjectsResponseDTO({
        "code": 200,
        "message": "SUCCESS",
        "projects": project_entities
    })