class CreateProjectResponseDTO():
    def __init__(self, response_dict):
        self.code = response_dict["code"]
        self.message = response_dict["message"]
        self.project = None

        if "project" in response_dict and response_dict["project"] is not None:
            self.project = response_dict["project"].convert_to_dict()

    def convert_to_dict(self):
        return {
            "code": self.code,
            "message": self.message,
            "project": self.project
        }