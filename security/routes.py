from authentication.auth import Authentication
from flask import abort
from functools import wraps


def requires_auth(func):
    """Decorator function to protect a route against unauthenticated users.

    If the current visitor is not authenticated, this function will raise
    a 401 error.

    Example usage:

    @app.route('/example', methods=['GET', 'POST'])
    @requires_auth
    def example_route():
        return 'this is a csrf protected route on POST requests'

    """
    @wraps(func)
    def check_authorization(*args, **kwargs):
        if not Authentication().is_authenticated():
            abort(401)
        return func(*args, **kwargs)
    return check_authorization
