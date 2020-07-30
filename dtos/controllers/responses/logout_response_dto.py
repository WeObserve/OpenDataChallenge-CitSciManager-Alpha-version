class LogoutResponseDTO():
    def __init__(self, response_dict):
        self.code = response_dict["code"]
        self.message = response_dict["message"]

    def convert_to_dict(self):
        return {
            "code": self.code,
            "message": self.message,
        }