import json

def validate_request(request, request_type, request_body_type):
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
            request_validity["reason"] = "UUID is amandatory"
            return request_validity

        # get uuid from the request body
        uuid = request_body["uuid"]

    if uuid is None or len(uuid) == 0:
        request_validity["is_valid"] = False
        request_validity["reason"] = "UUID is amandatory"
        return request_validity

    '''
    this is a very bad way of authentication or authorisation
    not recommended at all
    on top of that its an even worse way of handling data
    only doing this since we don't have enough time to set up a proper db and test
    and configure connection pools
    '''

    #load users_table
    users = json.load(
        open("./db/users_table.json", "r"))

    #look for the given uuid
    for user in users:
        if user["uuid"] == uuid:
            if (user["type"] == "sender" and request_type in ("UPLOAD_FILES", "VIEW_DATASTORIES")):
                request_validity["user"] = user
                return request_validity
            elif (user["type"] == "collector" and request_type in ("DOWNLOAD_FILES", "INVITE_USERS", "CREATE_DATASTORY", "VIEW_DATASTORIES")):
                request_validity["user"] = user
                return request_validity
            else:
                request_validity["is_valid"] = False
                request_validity["reason"] = "user cannot perform requested action"
                return request_validity

    request_validity["is_valid"] = False
    request_validity["reason"] = "uuid is invalid"

    return request_validity

