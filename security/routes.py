from authentication.auth import Authentication
from flask import abort
from functools import wraps


def requires_auth(func):
    @wraps(func)
    def check_authorization(*args, **kwargs):
        if not Authentication().is_authenticated():
            abort(401)
        return func(*args, **kwargs)
    return check_authorization
