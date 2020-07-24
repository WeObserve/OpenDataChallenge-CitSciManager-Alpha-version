class FetchProjectsRequestDTO():
    MANDATORY_FIELDS = ["user_project_mapping_types"]

    def __init__(self, request):
        print(self.__class__.__name__ + ": Inside fetch_projects_request_dto constructor")

        json_request = self.validate_request(request)

        self.user_project_mapping_types = json_request["user_project_mapping_types"]

    def validate_request(self, request):
        print(self.__class__.__name__ + ": Inside validate_request")

        if request is None or not request.is_json:
            print("Request is null or not a valid json")
            raise Exception("Request is null or not a valid json")

        json_request = request.get_json()

        for field in self.MANDATORY_FIELDS:
            if field not in json_request or len(json_request[field]) == 0:
                raise Exception(field + " is mandatory and should be non empty")

        user_project_mapping_types_without_duplicates = []

        for user_project_mapping_type in json_request["user_project_mapping_types"]:
            if user_project_mapping_type not in ["CREATOR", "COLLECTOR", "SENDER"]:
                raise Exception("user_project_mapping_types can only have CREATOR, COLLECTOR, SENDER as elements")

            if user_project_mapping_type not in user_project_mapping_types_without_duplicates:
                user_project_mapping_types_without_duplicates.append(user_project_mapping_type)

        json_request["user_project_mapping_types"] = user_project_mapping_types_without_duplicates

        return json_request