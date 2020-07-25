import os

class CreateUserRequestDTO():
    MANDATORY_FIELDS = ["email", "organisation_name", "organisation_affiliation", "name"]

    def __init__(self, request):
        print(self.__class__.__name__ + ": Inside create_user_request_dto constructor")

        json_request = self.validate_request(request)

        self.email = json_request["email"]
        self.organisation_name = json_request["organisation_name"]
        self.organisation_affiliation = json_request["organisation_affiliation"]
        self.name = json_request["name"]

    def validate_request(self, request):
        print(self.__class__.__name__ + ": Inside validate_request")

        if request is None or not request.is_json:
            print("Request is null or not a valid json")
            raise Exception("Request is null or not a valid json")

        json_request = request.get_json()

        for field in self.MANDATORY_FIELDS:
            if field not in json_request or len(json_request[field]) == 0:
                raise Exception(field + " is mandatory")

        return json_request