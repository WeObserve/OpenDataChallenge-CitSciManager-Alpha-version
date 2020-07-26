class Join():
    FIELDS = ["_id", "file_id_1", "file_id_2", "columns_for_file_1", "columns_for_file_2", "join_column_for_file_1", "join_column_for_file_2", "status"]

    def __init__(self, join_dict):
        print(self.__class__.__name__ + ": Inside constructor")

        self._id = None
        if "_id" in join_dict:
            self._id = str(join_dict["_id"])
        self.file_id_1 = str(join_dict["file_id_1"])
        self.file_id_2 = str(join_dict["file_id_2"])
        self.columns_for_file_1 = join_dict["columns_for_file_1"]
        self.columns_for_file_2 = join_dict["columns_for_file_2"]
        self.join_column_for_file_1 = join_dict["join_column_for_file_1"]
        self.join_column_for_file_2 = join_dict["join_column_for_file_2"]
        self.status = join_dict["status"]
        self.project_id = str(join_dict["project_id"])
        self.user_id = str(join_dict["user_id"])

    def convert_to_dict(self):
        print(self.__class__.__name__ + ": Inside convert_to_dict")

        return {
            "_id": self._id,
            "project_id": self.project_id,
            "user_id": self.user_id,
            "file_id_1": self.file_id_1,
            "file_id_2": self.file_id_2,
            "columns_for_file_1": self.columns_for_file_1,
            "columns_for_file_2": self.columns_for_file_2,
            "join_column_for_file_1": self.join_column_for_file_1,
            "status": self.status,
            "join_column_for_file_2": self.join_column_for_file_2
        }