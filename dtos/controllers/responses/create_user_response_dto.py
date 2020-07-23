class CreateUserResponseDTO():
    def __init__(self, response_dict):
        self.code = response_dict["code"]
        self.message = response_dict["message"]
        self.user = None

        if "user" in response_dict and response_dict["user"] is not None:
            self.user = response_dict["user"].convert_to_dict()

    def convert_to_dict(self):
        return {
            "code": self.code,
            "message": self.message,
            "user": self.user
        }