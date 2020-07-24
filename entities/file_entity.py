class File():
    FIELDS = ["_id", "file_name", "s3_link", "relative_path", "project_id", "creator_id", "status", "headers", "file_type"]

    def __init__(self, file_dict):
        print(self.__class__.__name__ + ": Inside constructor")

        self._id = None
        if "_id" in file_dict:
            self._id = str(file_dict["_id"])
        self.file_name = file_dict["file_name"]
        self.s3_link = file_dict["s3_link"]
        self.relative_path = file_dict["relative_path"]
        self.project_id = str(file_dict["project_id"])
        self.creator_id = str(file_dict["creator_id"])
        self.status = file_dict["status"]
        self.headers = None
        if "headers" in file_dict:
            self.headers = file_dict["headers"]
        self.file_type = file_dict["file_type"]

    def convert_to_dict(self):
        print(self.__class__.__name__ + ": Inside convert_to_dict")

        return {
            "_id": self._id,
            "file_name": self.file_name,
            "s3_link": self.s3_link,
            "relative_path": self.relative_path,
            "project_id": self.project_id,
            "creator_id": self.creator_id,
            "status": self.status,
            "headers": self.headers,
            "file_type": self.file_type
        }