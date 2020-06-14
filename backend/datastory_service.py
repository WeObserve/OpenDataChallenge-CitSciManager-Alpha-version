import json

def process_create_datastory(request, user):
    process_response = {
        "status": "SUCCESS",
        "is_success": True
    }

    if ("datastory_name" not in request.form or len(request.form["datastory_name"]) == 0
        or "datastory_content" not in request.form or len(request.form["datastory_content"]) == 0):
        return {
            "status": "FAILED",
            "is_success": False,
            "message": "datastory_name and datastory_content are mandatory"
        }

    # load datastories_table
    datastories = json.load(
        open("./db/datastories_table.json", "r"))

    user_creating_datastory = user

    datastories_created_for_this_project = []

    # collect datastory names of datastories created for this project
    for datastory in datastories:
        if datastory["project_id"] == user_creating_datastory["project_id"]:
            datastories_created_for_this_project.append(datastory["name"])

    if (request.form["datastory_name"] in datastories_created_for_this_project):
        return {
            "status": "FAILED",
            "is_success": False,
            "message": "a datastory by this name already exists for this project"
        }

    datastory_to_be_created = {
        "name": request.form["datastory_name"],
        "content": request.form["datastory_content"],
        "project_id": user_creating_datastory["project_id"],
        "user_uuid": user_creating_datastory["uuid"]
    }

    datastories.append(datastory_to_be_created)

    json.dump(datastories, open("./db/datastories_table.json", "w"))

    return process_response

def process_view_datastory(request, user):
    process_response = {
        "status": "SUCCESS",
        "is_success": True
    }

    request_body = request.get_json()

    if (("get_all_datastories" not in request_body or not request_body["get_all_datastories"]) and ("datastory_name" not in request_body or len(request_body["datastory_name"]) == 0)):
        process_response["status"] = "FAILED"
        process_response["is_success"] = False
        process_response["message"] = "request body must have either get_all_datastories field set to true or must have a non empty datastory_name field"

    # load datastories_table
    datastories = json.load(
        open("./db/datastories_table.json", "r"))

    user_viewing_datastory = user

    datastories_created_for_this_project = []

    # collect datastory names of datastories created for this project
    for datastory in datastories:
        if datastory["project_id"] == user_viewing_datastory["project_id"]:
            datastories_created_for_this_project.append(datastory)

    if ("get_all_datastories" in request_body and request_body["get_all_datastories"]):
        process_response["datastories"] = datastories_created_for_this_project
    else:
        datastories_with_given_name = []
        for datastory in datastories_created_for_this_project:
            if datastory["name"] == request_body["datastory_name"]:
                datastories_with_given_name.append(datastory)
        process_response["datastories"] = datastories_with_given_name

    return process_response
