class FetchProjectsResponseDTO():
    def __init__(self, response_dict):
        self.code = response_dict["code"]
        self.message = response_dict["message"]
        self.projects = []

        if "projects" in response_dict and len(response_dict["projects"]) != 0:
            for project in response_dict["projects"]:
                self.projects.append(project.convert_to_dict())

    def convert_to_dict(self):
        return {
            "code": self.code,
            "message": self.message,
            "projects": self.projects
        }