import uuid
import jwt
from db.mongo.daos import users_dao
import hashlib
from entities.user_entity import User
from dtos.controllers.responses.login_response_dto import LoginResponseDTO

def validate_email_id_and_password_and_fetch_user(db_connection, login_request_dto, secret_key):
    print("Inside validate_email_id_and_password_and_fetch_user")

    users_with_given_email_as_cursor = users_dao.get_users(db_connection, {"email": login_request_dto.email})

    if users_with_given_email_as_cursor is None or users_with_given_email_as_cursor.count() == 0:
        raise Exception("User with given email id does not exist")

    for user in users_with_given_email_as_cursor:
        decoded_password = jwt.decode(login_request_dto.password.encode(), secret_key, verify=True)["password"]
        if user["password"] == hashlib.sha256(decoded_password.encode('utf-8')).hexdigest():
            return User(user)

    raise Exception("Password is incorrect")


def create_new_token_id_secret_key_access_token(user_entity, user_id_to_token_id_map, token_id_to_secret_key_map, secret_key_master):
    print("Inside create_new_token_id_secret_key_access_token")

    secret_key = uuid.uuid1().hex

    token_id = jwt.encode({'secret_key': secret_key}, secret_key_master, algorithm='HS256').decode('utf-8')
    access_token = jwt.encode({'_id': user_entity._id}, secret_key, algorithm='HS256').decode('utf-8')

    user_id_to_token_id_map[user_entity._id] = token_id
    token_id_to_secret_key_map[token_id] = secret_key

    print(f'token id: {token_id}')
    print(f'access_token: {access_token}')
    return {
        "token_id": token_id,
        "access_token": access_token
    }

def login(db_connection, login_request_dto, in_memory_cache, secret_key, env):
    print("Inside login service")

    user_id_to_token_id_map = in_memory_cache["user_id_to_token_id_map"]
    token_id_to_secret_key_map = in_memory_cache["token_id_to_secret_key_map"]
    print(f'user id token map: {user_id_to_token_id_map}')
    print(f'token id to secret key map:{token_id_to_secret_key_map}')
    #Validate email id and password and get user from db
    user_entity = validate_email_id_and_password_and_fetch_user(db_connection, login_request_dto, secret_key)

    if user_entity._id in user_id_to_token_id_map:
        token_id = user_id_to_token_id_map[user_entity._id]
        if token_id is not None and len(token_id) != 0:
            if token_id in token_id_to_secret_key_map:
                del token_id_to_secret_key_map[token_id]
        del user_id_to_token_id_map[user_entity._id]

    #create new token_id and secret key and access token for user
    creds = create_new_token_id_secret_key_access_token(user_entity, user_id_to_token_id_map, token_id_to_secret_key_map, secret_key)

    return LoginResponseDTO({
        "code": 200,
        "message": "SUCCESS",
        "user": user_entity,
        "token_id": creds["token_id"],
        "access_token": creds["access_token"]
    })