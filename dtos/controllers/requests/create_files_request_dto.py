from dtos.controllers.requests.create_file_request_dto import CreateFileRequestDTO

class CreateFilesRequestDTO():
    MANDATORY_FIELDS = ["project_id", "files"]

    def __init__(self, request):
        print(self.__class__.__name__ + ": Inside create_project_request_dto constructor")

        json_request = self.validate_request(request)

        self.project_id = json_request["project_id"]
        self.files = []

        for file in json_request["files"]:
            self.files.append(CreateFileRequestDTO(file))

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