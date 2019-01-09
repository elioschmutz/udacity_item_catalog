from authentication.google import GoogleAuth
from flask import g
from flask import session as flask_session
from models import LoginSession

providers = {
    'google': GoogleAuth()
}


class Authentication(object):

    def login(self, provider, *args, **kwargs):
        return providers.get(provider).login(*args, **kwargs)

    def logout(self):
        current_provider = self.get_current_login_provider()
        if not current_provider:
            return

        token = self.access_token()

        # Remove the local login session
        g.current_login_session.delete()
        del g.current_login_session
        del g.current_user
        del flask_session['access_token']

        # Invalidate provider token
        current_provider.logout(token)

    def restore_session(self):
        token = self.access_token()
        if not token:
            return

        LoginSession.lookup_by_token(token)
        session = LoginSession.lookup_by_token(token)
        if not session:
            return

        g.current_user = session.user
        g.current_login_session = session

    def is_authenticated(self):
        return hasattr(g, 'current_user') and bool(g.current_user)

    def access_token(self):
        return flask_session.get('access_token')

    def get_current_login_provider(self):
        if not self.is_authenticated():
            return None
        return providers.get(g.current_login_session.provider)
