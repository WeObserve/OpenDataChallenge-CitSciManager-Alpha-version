class CreateJoinsResponseDTO():
    def __init__(self, response_dict):
        self.code = response_dict["code"]
        self.message = response_dict["message"]
        self.joins = []

        if "joins" in response_dict and len(response_dict["joins"]) != 0:
            for join in response_dict["joins"]:
                self.joins.append(join.convert_to_dict())

    def convert_to_dict(self):
        return {
            "code": self.code,
            "message": self.message,
            "joins": self.joins
        }