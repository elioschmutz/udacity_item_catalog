from flask import abort
from flask import request
from flask import session as flask_session
from functools import wraps
import random
import string


def _get_token():
    return request.form.get('csrf_token') or \
        request.args.get('csrf_token') or \
        request.args.get('state')


def csrf_protection(force_validation_on_get=False):
    """Decorator function to protect an rout against csrf.

    If the request method is something else than a GET request or if there is
    a csrf-token in the request, it validates it against
    the token within the current session.

    If there is no token in the request and the request method is GET, it will
    generate and add a new token to the current user session.

    example usage:

    @app.route('/example', methods=['GET', 'POST'])
    @csrf_protection()
    def example_route():
        return 'this is a csrf protected route on POST requests'

    """

    def _csrf_protection(func):
        @wraps(func)
        def protect(*args, **kwargs):
            if not force_validation_on_get and request.method == 'GET':
                csrf_token = ''.join(
                    random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))

                flask_session['csrf_token'] = csrf_token

            else:
                if flask_session['csrf_token'] != _get_token():
                    abort(403)

            return func(*args, **kwargs)
        return protect
    return _csrf_protection
