from authentication.google import GoogleAuth
from models import LoginSession
from flask import g

providers = {
    'google': GoogleAuth
}


class Authentication(object):

    def login(self, provider, *args, **kwargs):
        return providers.get(provider)().login(*args, **kwargs)

    def restore_session(self, token):
        if not token:
            return

        LoginSession.lookup_by_token(token)
        session = LoginSession.lookup_by_token(token)
        if not session:
            return

        g.current_user = session.user

    def is_authenticated(self):
        return bool(g.current_user)
