from dtos.controllers.responses.logout_response_dto import LogoutResponseDTO

def logout(request, in_memory_cache, user_id):
    print("Inside logout service")

    token_id = request.headers["token_id"]

    del in_memory_cache["user_id_to_token_id_map"][user_id]
    del in_memory_cache["token_id_to_secret_key_map"][token_id]

    return LogoutResponseDTO({
        "code": 200,
        "message": "SUCCESSS"
    })