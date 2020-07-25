class LoginResponseDTO():
    def __init__(self, response_dict):
        self.code = response_dict["code"]
        self.message = response_dict["message"]
        self.user = None
        self.token_id = None
        self.access_token = None

        if "user" in response_dict and response_dict["user"] is not None:
            self.user = response_dict["user"].convert_to_dict()

        if "token_id" in response_dict and response_dict["token_id"] is not None:
            self.token_id = response_dict["token_id"]

        if "access_token" in response_dict and response_dict["access_token"] is not None:
            self.access_token = response_dict["access_token"]

    def convert_to_dict(self):
        return {
            "code": self.code,
            "message": self.message,
            "user": self.user,
            "token_id": self.token_id,
            "access_token": self.access_token
        }