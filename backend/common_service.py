import json
from db.mongo.daos import users_dao

def validate_request(db_connection, request, request_type, request_body_type):
    request_validity = {
        "is_valid": True,
        "reason": None
    }

    uuid = None

    if request_body_type == "form":
        # check if uuid is present in request body
        if "uuid" not in request.form:
            request_validity["is_valid"] = False
            request_validity["reason"] = "UUID is amandatory"
            return request_validity

        # get uuid from the request body
        uuid = request.form["uuid"]
    elif request_body_type == "json":
        if not request.is_json:
            request_validity["is_valid"] = False
            request_validity["reason"] = "request should be a valid json"
            return request_validity

        request_body = request.get_json()

        # check if uuid is present in request body
        if request_body is None or "uuid" not in request_body:
            request_validity["is_valid"] = False
            request_validity["reason"] = "UUID is mandatory"
            return request_validity

        # get uuid from the request body
        uuid = request_body["uuid"]

    if uuid is None or len(uuid) == 0:
        request_validity["is_valid"] = False
        request_validity["reason"] = "UUID is amandatory"
        return request_validity

    user = users_dao.get_user_by_uuid(db_connection, uuid)

    if (user["type"] == "SENDER" and request_type in ("UPLOAD_FILES", "VIEW_DATASTORIES")):
        request_validity["user"] = user
        return request_validity
    elif (user["type"] == "COLLECTOR" and request_type in ("DOWNLOAD_FILES", "INVITE_USERS", "CREATE_DATASTORY", "VIEW_DATASTORIES")):
        request_validity["user"] = user
        return request_validity
    else:
        request_validity["is_valid"] = False
        request_validity["reason"] = "user cannot perform requested action"
        return request_validity
