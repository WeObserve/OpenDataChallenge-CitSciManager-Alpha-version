class FetchFilesRequestDTO():
    MANDATORY_FIELDS = ["file_types", "project_id"]

    def __init__(self, request):
        print(self.__class__.__name__ + ": Inside fetch_projects_request_dto constructor")

        json_request = self.validate_request(request)

        self.file_types = json_request["file_types"]
        self.project_id = json_request["project_id"]

    def validate_request(self, request):
        print(self.__class__.__name__ + ": Inside validate_request")

        if request is None or not request.is_json:
            print("Request is null or not a valid json")
            raise Exception("Request is null or not a valid json")

        json_request = request.get_json()

        for field in self.MANDATORY_FIELDS:
            if field not in json_request or len(json_request[field]) == 0:
                raise Exception(field + " is mandatory and should be non empty")

        file_types_without_duplicates = []

        for file_type in json_request["file_types"]:
            if file_type not in ["RAW", "META_DATA"]:
                raise Exception("file_types can only have RAW, META_DATA as elements")

            if file_type not in file_types_without_duplicates:
                file_types_without_duplicates.append(file_type)

        json_request["file_types"] = file_types_without_duplicates

        return json_request