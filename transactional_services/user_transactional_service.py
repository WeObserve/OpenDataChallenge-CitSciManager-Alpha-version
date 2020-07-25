import hashlib
import jwt
import uuid
from db.mongo.daos import users_dao, user_project_mappings_dao
from entities.user_entity import User
from bson import ObjectId
from dtos.controllers.responses.invite_user_response_dto import InviteUserResponseDTO

def invite_user(db_connection, invite_user_request_dto, is_user_creation_required, is_upm_creation_required,
                is_upm_update_required, invited_user_dict, db_connection_client, master_secret_key, project_id):
    print("Inside invite_user transactional service")

    encoded_creds = None
    invited_user_entity = None

    if invited_user_dict:
        invited_user_entity = User(invited_user_dict)

    with db_connection_client.start_session() as session:
        with session.start_transaction():
            if is_user_creation_required:
                auto_generated_user_password = uuid.uuid1().hex

                encoded_creds = jwt.encode({
                    "email": invite_user_request_dto.email,
                    "password": auto_generated_user_password
                }, master_secret_key, algorithm='HS256').decode('utf-8')

                print("generated encoded_creds: " + encoded_creds)

                invited_user_dict = {
                    "email": invite_user_request_dto.email,
                    "password": hashlib.sha256(auto_generated_user_password.encode('utf-8')).hexdigest(),
                    "name": invite_user_request_dto.name,
                    "organisation_name": invite_user_request_dto.organisation_name,
                    "organisation_affiliation": invite_user_request_dto.organisation_affiliation
                }

                user_insert_one_result = users_dao.insert_user_using_txn(db_connection, invited_user_dict, session)

                invited_user_dict["_id"] = user_insert_one_result.inserted_id

                print(invited_user_dict)

                invited_user_entity = User(invited_user_dict)

                print(invited_user_entity.email)
            if is_upm_creation_required:
                user_project_mapping_dict = {
                    "email": invite_user_request_dto.email,
                    "user_id": invited_user_dict["_id"],
                    "project_name": invite_user_request_dto.project_name,
                    "project_id": ObjectId(project_id),
                    "mapping_type": invite_user_request_dto.mapping_type
                }

                upm_insert_one_result = user_project_mappings_dao.insert_user_project_mapping_using_txn(
                    db_connection, user_project_mapping_dict, session)

            if is_upm_update_required:
                user_project_mapping_query_dict = {
                    "user_id": invited_user_dict["_id"],
                    "project_id": ObjectId(project_id)
                }

                updated_upm = {
                    "$set": {
                        "mapping_type": invite_user_request_dto.mapping_type
                    }
                }

                user_project_mappings_dao.update_upm_txn(db_connection, user_project_mapping_query_dict, updated_upm, session)

    return InviteUserResponseDTO({
        "code": 200,
        "message": "SUCCESS",
        "user": invited_user_entity
    }), encoded_creds