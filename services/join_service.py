from bson import ObjectId
from db.mongo.daos import user_project_mappings_dao, files_dao, joins_dao
from dtos.controllers.responses.create_joins_response_dto import CreateJoinsResponseDTO
from entities.join_entity import Join

def check_user_project_mapping(db_connection, user_id, create_joins_request_dto):
    print("Inside check_user_project_mapping")

    upm_cursor = user_project_mappings_dao.get_user_project_mapping(db_connection, {
        "user_id": ObjectId(user_id),
        "project_id": ObjectId(create_joins_request_dto.project_id),
        "mapping_type": {
            "$in": ["COLLECTOR", "CREATOR"]
        }
    })

    if upm_cursor is None or upm_cursor.count() == 0:
        raise Exception("This user can't join files in this project")


def check_if_these_file_ids_exist_for_this_project(db_connection, create_joins_request_dto, user_id):
    print("Inside check_if_these_file_ids_exist_for_this_project")

    file_ids = []
    file_id_to_selected_columns_map = {}
    join_dicts = []

    for create_join_request_dto in create_joins_request_dto.joins:
        if create_join_request_dto.file_id_1 == create_join_request_dto.file_id_2:
            raise Exception("File cannot be joined with itself")

        if create_join_request_dto.file_id_1 not in file_ids:
            file_ids.append(create_join_request_dto.file_id_1)
            file_id_to_selected_columns_map[create_join_request_dto.file_id_1] = []

            for column in create_join_request_dto.columns_for_file_1:
                if column not in file_id_to_selected_columns_map[create_join_request_dto.file_id_1]:
                    file_id_to_selected_columns_map[create_join_request_dto.file_id_1].append(column)

        if create_join_request_dto.file_id_2 not in file_ids:
            file_ids.append(create_join_request_dto.file_id_2)
            file_id_to_selected_columns_map[create_join_request_dto.file_id_2] = []

            for column in create_join_request_dto.columns_for_file_2:
                if column not in file_id_to_selected_columns_map[create_join_request_dto.file_id_2]:
                    file_id_to_selected_columns_map[create_join_request_dto.file_id_2].append(column)

        join_dicts.append({
            "user_id": ObjectId(user_id),
            "project_id": ObjectId(create_joins_request_dto.project_id),
            "file_id_1": ObjectId(create_join_request_dto.file_id_1),
            "file_id_2": ObjectId(create_join_request_dto.file_id_2),
            "columns_for_file_1": create_join_request_dto.columns_for_file_1,
            "columns_for_file_2": create_join_request_dto.columns_for_file_2,
            "join_column_for_file_1": create_join_request_dto.join_column_for_file_1,
            "join_column_for_file_2": create_join_request_dto.join_column_for_file_2,
            "status": "PENDING"
        })

    file_object_ids = []

    for file_id in file_ids:
        file_object_ids.append(ObjectId(file_id))

    file_cursor = files_dao.get_files(db_connection, {
        "_id": {
            "$in": file_object_ids
        },
        "project_id": ObjectId(create_joins_request_dto.project_id),
        "status": "PROCESSED",
        "file_type": "META_DATA"
    })

    if file_cursor is None or file_cursor.count() != len(file_object_ids):
        raise Exception("Some of these files are not PROCESSED or not a part of this project")

    return file_cursor, file_id_to_selected_columns_map, join_dicts

def check_that_the_selected_columns_are_actually_present_in_the_files(db_connection, file_cursor,
                                                                      file_id_to_selected_columns_map):
    print("Inside check_that_the_selected_columns_are_actually_present_in_the_files")

    for file in file_cursor:
        for column in file_id_to_selected_columns_map[str(file["_id"])]:
            if column not in file["headers"]:
                raise Exception("For some file the selected columns are not a part of the file headers")

def create_joins(db_connection, user_id, create_joins_request_dto, env):
    print("Inside create_joins service")

    #check if this user has a COLLECTOR or CREATOR mapping with the project
    check_user_project_mapping(db_connection, user_id, create_joins_request_dto)

    #check if these file ids exist for this project_id
    file_cursor, file_id_to_selected_columns_map, join_dicts = check_if_these_file_ids_exist_for_this_project(db_connection, create_joins_request_dto, user_id)

    #check that the selected columns are actually present in the files
    check_that_the_selected_columns_are_actually_present_in_the_files(db_connection, file_cursor, file_id_to_selected_columns_map)

    joins_dao.insert_joins(db_connection, join_dicts)

    join_entities = []

    for join_dict in join_dicts:
        join_entities.append(Join(join_dict))

    return CreateJoinsResponseDTO({
        "code": 200,
        "message": "SUCCESS",
        "joins": join_entities
    })