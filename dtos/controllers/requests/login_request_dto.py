class LoginRequestDTO():
    MANDATORY_FIELDS = ["email", "password"]

    def __init__(self, request):
        print(self.__class__.__name__ + ": Inside constructor")

        json_request = self.validate_request(request)

        self.email = json_request["email"]
        self.password = json_request["password"]

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