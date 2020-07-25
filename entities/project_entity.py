class Project():
    FIELDS = ["_id", "name", "license", "user_project_mapping_type"]

    def __init__(self, project_dict):
        print(self.__class__.__name__ + ": Inside constructor")

        self._id = None
        if "_id" in project_dict:
            self._id = str(project_dict["_id"])
        self.user_project_mapping_type = None
        if "user_project_mapping_type" in project_dict:
            self.user_project_mapping_type = project_dict["user_project_mapping_type"]
        self.name = project_dict["name"]
        self.license = project_dict["license"]

    def convert_to_dict(self):
        print(self.__class__.__name__ + ": Inside convert_to_dict")

        return {
            "_id": self._id,
            "name": self.name,
            "license": self.license,
            "user_project_mapping_type": self.user_project_mapping_type
        }