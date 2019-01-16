from base import app
from flask import session as flask_session
from models import LoginSession
from models import User
import json


class UserData(object):
    def __init__(self, email, name, img_url):
        self.email = email
        self.name = name
        self.img_url = img_url


class AuthProvider(object):

    secrets_file_name = None
    secrets = None
    provider_name = None

    def __init__(self):
        self.secrets = self.load_secrets()

    def login(self, code):
        """Performs all the required steps to login a user
        """
        access_token, userdata = self.process_auth_provider_login(code)
        return self.process_local_login(access_token, userdata)

    def logout(self, token=''):
        pass

    def process_auth_provider_login(self, code):
        """Is doing everything needed to validate the auth code, fetching an
        access token and user-infos.

        This function should return the access_token and a userdata object.
        """
        raise NotImplementedError

    def process_local_login(self, access_token, userdata):
        """After validating the tokens and fetching the user-infos from the
        auth-provider, it is required to create/get a local user-object
        and safe the access-token for further requests into a session object.
        """
        user = self.get_or_create_user(userdata)

        # Create a new login-session
        flask_session['access_token'] = access_token
        return LoginSession.create(
            token=access_token,
            provider=self.provider_name,
            user=user)

    def get_or_create_user(self, userdata):
        """Returns a user-instance.

        If a user with the given email already exists, it just returns the given
        one. Otherwise, it creates a new user.
        """
        user = User.lookup_by_email(userdata.email)
        if not user:
            user = User.create(name=userdata.name,
                               email=userdata.email,
                               picture=userdata.img_url)
        return user

    def load_secrets(self):
        with app.open_resource(self.secrets_file_name) as f:
            return json.loads(f.read())
