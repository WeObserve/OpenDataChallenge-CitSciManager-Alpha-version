class CreateFileRequestDTO():
    MANDATORY_FIELDS = ["file_name", "s3_link", "relative_s3_path", "file_type"]

    def __init__(self, request):
        print(self.__class__.__name__ + ": Inside create_file_request_dto constructor")

        json_request = self.validate_request(request)

        self.file_name = json_request["file_name"]
        self.s3_link = json_request["s3_link"]
        self.relative_s3_path = json_request["relative_s3_path"]
        self.file_type = json_request["file_type"]

    def validate_request(self, request):
        print(self.__class__.__name__ + ": Inside validate_request")

        if request is None:
            print("Request is null or not a valid json")
            raise Exception("Request is null or not a valid json")

        json_request = request

        for field in self.MANDATORY_FIELDS:
            if field not in json_request or len(json_request[field]) == 0:
                raise Exception(field + " is mandatory")

        if json_request["file_type"] not in ["RAW", "META_DATA"]:
            raise Exception("file_type possible values are RAW and META_DATA")

        return json_request