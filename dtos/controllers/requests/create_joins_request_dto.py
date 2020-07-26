from dtos.controllers.requests.create_join_request_dto import CreateJoinRequestDTO

class CreateJoinsRequestDTO():
    MANDATORY_FIELDS = ["project_id", "joins"]

    def __init__(self, request):
        print(self.__class__.__name__ + ": Inside create_joins_request_dto constructor")

        json_request = self.validate_request(request)

        self.project_id = json_request["project_id"]
        self.joins = []

        for join in json_request["joins"]:
            self.joins.append(CreateJoinRequestDTO(join))

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