from functools import wraps, partial
from flask import request
import json
import jwt

def pseudo_authenticate(f, app_config):
    @wraps(f)
    def check_token(*args, **kwargs):
        try:
            if "token_id" not in request.headers or "access_token" not in request.headers:
                return json.dumps({
                    "code": 401,
                    "message": "token_id or access_token missing in headers"
                })

            token_id = request.headers["token_id"]
            access_token = request.headers["access_token"]

            if token_id is None or access_token is None or len(token_id) == 0 or len(access_token) == 0:
                return json.dumps({
                    "code": 401,
                    "message": "token_id or access_token missing in headers"
                })

            in_memory_cache = app_config["in_memory_cache"]
            token_id_to_secret_key_map = in_memory_cache["token_id_to_secret_key_map"]

            secret_key = token_id_to_secret_key_map[token_id]

            if secret_key is None or len(secret_key) == 0:
                return json.dumps({
                    "code": 401,
                    "message": "Please login again"
                })

            access_token_bytes = access_token.encode()

            try:
                payload = jwt.decode(access_token_bytes, secret_key)

                kwargs["user_id"] = payload["_id"]

                return f(*args, **kwargs)
            except Exception as e:
                return json.dumps({
                    "code": 401,
                    "message": str(e)
                })
        except Exception as e:
            return json.dumps({
                "code": 401,
                "message": str(e)
            })

    return check_token