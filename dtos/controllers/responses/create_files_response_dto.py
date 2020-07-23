class CreateFilesResponseDTO():
    def __init__(self, response_dict):
        self.code = response_dict["code"]
        self.message = response_dict["message"]
        self.files = []

        if "files" in response_dict and len(response_dict["files"]) != 0:
            for file in response_dict["files"]:
                self.files.append(file.convert_to_dict())

    def convert_to_dict(self):
        return {
            "code": self.code,
            "message": self.message,
            "files": self.files
        }