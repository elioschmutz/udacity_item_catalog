from authentication.errors import AccessTokenValidationError
from flask import session as flask_session
from models import LoginSession
from models import User
import json
import requests


class GithubAuth(object):
    secrets = None
    oauth_endpoint = ''
    secrets_file_name = 'github_secrets.json'

    def __init__(self):
        self.secrets = self._load_secrets()

    def login(self, access_token):
        """Logs in a user based on the auth_code received from the frontend
        """
        token = self._get_app_token(access_token)
        return self._process_login(token)

    def logout(self, access_token):
        pass

    def _get_app_token(self, access_token):
        """Valdiate the accesstoken
        """
        # Verify that the access token is used for the intended user.
        url = 'https://github.com/login/oauth/access_token'
        headers = {'Accept': 'application/json'}
        payload = {
            'client_id': self.secrets['web']['app_id'],
            'client_secret': self.secrets['web']['app_secret'],
            'code': access_token
        }

        response = requests.post(url, data=payload, headers=headers).json()

        if response.get('error'):
            raise AccessTokenValidationError(response.get('error_description'))
        return response.get('access_token')

    def _process_login(self, access_token):
        userinfo = self._lookup_user_info(access_token)
        user = self._get_or_create_user(userinfo)

        # Create a new login-session
        flask_session['access_token'] = access_token
        return LoginSession.create(
            token=access_token,
            provider='facebook',
            user=user)

    def _lookup_user_info(self, access_token):

        userinfo_url = "https://api.github.com/user"
        params = {'access_token': access_token}
        headers = {'Accept': 'application/json'}
        userinfos = requests.get(
            userinfo_url, params=params, headers=headers).json()

        return userinfos

    def _get_or_create_user(self, userinfo):
        # see if user exists, if it doesn't make a new one
        user = User.lookup_by_email(userinfo.get('email'))
        if not user:
            user = User.create(name=userinfo.get('name', ''),
                               email=userinfo.get('email'),
                               picture=userinfo.get('avatar_url', ''))
        return user

    def _load_secrets(self):
        with open(self.secrets_file_name, 'r') as file_:
            return json.loads(file_.read())
