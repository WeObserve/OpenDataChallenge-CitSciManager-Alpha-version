class User():
    FIELDS = ["_id", "email", "password"]

    def __init__(self, user_dict):
        print(self.__class__.__name__ + ": Inside constructor")

        self._id = None
        if "_id" in user_dict:
            self._id = str(user_dict["_id"])
        self.email = user_dict["email"]
        self.password = user_dict["password"]

    def convert_to_dict(self):
        print(self.__class__.__name__ + ": Inside conert_to_dict")

        return {
            "_id": self._id,
            "email": self.email,
            "password": self.password
        }