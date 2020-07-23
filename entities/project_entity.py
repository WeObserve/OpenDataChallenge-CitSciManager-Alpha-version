class Project():
    FIELDS = ["_id", "name", "license"]

    def __init__(self, project_dict):
        print(self.__class__.__name__ + ": Inside constructor")

        self._id = None
        if "_id" in project_dict:
            self._id = str(project_dict["_id"])
        self.name = project_dict["name"]
        self.license = project_dict["license"]

    def convert_to_dict(self):
        print(self.__class__.__name__ + ": Inside convert_to_dict")

        return {
            "_id": self._id,
            "name": self.name,
            "license": self.license
        }