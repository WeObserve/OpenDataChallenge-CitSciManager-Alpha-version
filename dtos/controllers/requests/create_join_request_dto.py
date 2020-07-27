class CreateJoinRequestDTO():
    MANDATORY_FIELDS = ["file_id_1", "file_id_2", "columns_for_file_1", "columns_for_file_2", "join_column_for_file_1", "join_column_for_file_2"]

    def __init__(self, request):
        print(self.__class__.__name__ + ": Inside create_join_request_dto constructor")

        json_request = self.validate_request(request)

        self.file_id_1 = json_request["file_id_1"]
        self.file_id_2 = json_request["file_id_2"]
        self.columns_for_file_1 = json_request["columns_for_file_1"]
        self.columns_for_file_2 = json_request["columns_for_file_2"]
        self.join_column_for_file_1 = json_request["join_column_for_file_1"]
        self.join_column_for_file_2 = json_request["join_column_for_file_2"]

    def validate_request(self, request):
        print(self.__class__.__name__ + ": Inside validate_request")

        if request is None:
            print("Request is null or not a valid json")
            raise Exception("Request is null or not a valid json")

        json_request = request

        for field in self.MANDATORY_FIELDS:
            if field not in json_request or len(json_request[field]) == 0:
                raise Exception(field + " is mandatory")

        for column in json_request["columns_for_file_1"]:
            if column is None or len(column) == 0:
                raise Exception("Column header name cannot be an empty string")

        for column in json_request["columns_for_file_2"]:
            if column is None or len(column) == 0:
                raise Exception("Column header name cannot be an empty string")

        if json_request["join_column_for_file_1"] not in json_request["columns_for_file_1"] or json_request["join_column_for_file_2"] not in json_request["columns_for_file_2"]:
            raise Exception("join columns for files must be a part of the selected columns")

        return json_request