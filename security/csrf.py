from flask import abort
from flask import request
from flask import session as flask_session
from functools import wraps
import random
import string


def csrf_protection(func):
    @wraps(func)
    def protect(*args, **kwargs):
        if request.method == 'GET':
            csrf_token = ''.join(
                random.choice(string.ascii_uppercase + string.digits)
                for x in xrange(32))

            flask_session['csrf_token'] = csrf_token

        else:
            csrf_token = request.form.get(
                'csrf_token', request.args.get('csrf_token'))
            if flask_session['csrf_token'] != csrf_token:
                abort(403)

        return func(*args, **kwargs)
    return protect
