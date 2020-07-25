class User():
    FIELDS = ["_id", "user_id", "email", "project_id", "project_name", "mapping_type"]

    def __init__(self, project_user_mapping_dict):
        print(self.__class__.__name__ + ": Inside constructor")

        self._id = None
        if "_id" in project_user_mapping_dict:
            self._id = str(project_user_mapping_dict["_id"])
        self.user_id = str(project_user_mapping_dict["user_id"])
        self.project_id = str(project_user_mapping_dict["project_id"])
        self.email = project_user_mapping_dict["email"]
        self.mapping_type = project_user_mapping_dict["mapping_type"]
        self.project_name = project_user_mapping_dict["project_name"]

    def convert_to_dict(self):
        print(self.__class__.__name__ + ": Inside convert_to_dict")

        return {
            "_id": self._id,
            "user_id": self.user_id,
            "project_id": self.project_id,
            "mapping_type": self.mapping_type,
            "email": self.email,
            "project_name": self.project_name
        }