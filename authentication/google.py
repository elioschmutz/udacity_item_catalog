from flask import session as flask_session
from models import LoginSession
from models import User
from oauth2client.client import flow_from_clientsecrets
import json
import requests


class AccessTokenValidationError(Exception):
    """
    """


class GoogleAuth(object):
    error = None
    secrets = None
    oauth_endpoint = 'https://www.googleapis.com/oauth2/v1'
    secrets_file_name = 'google_secrets.json'

    def __init__(self):
        self.secrets = self._load_secrets()

    def login(self, auth_code):
        """Logs in a user based on the auth_code received from the frontend
        """
        credentials = self._get_credentials_object(auth_code)
        tokeninfo = self._get_token_info(credentials.access_token)

        self._validate_access_token(credentials, tokeninfo)
        return self._process_login(credentials)

    def _get_credentials_object(self, code):
        """Upgrade the authorization code into a credentials object
        """
        oauth_flow = flow_from_clientsecrets(self.secrets_file_name, scope='')
        oauth_flow.redirect_uri = 'postmessage'
        return oauth_flow.step2_exchange(code)

    def _get_token_info(self, access_token):
        """Looksup the token infos:
        """
        url = '{}/tokeninfo?access_token={}'.format(
            self.oauth_endpoint, access_token)

        result = requests.get(url).json()

        if result.get('error') is not None:
            raise AccessTokenValidationError(result.get('error'))

        return result

    def _validate_access_token(self, credentials, tokeninfo):
        """Valdiate the accesstoken
        """
        # Verify that the access token is used for the intended user.
        gplus_id = credentials.id_token['sub']
        if tokeninfo['user_id'] != gplus_id:
            raise AccessTokenValidationError(
                "Token's user ID doesn't match given user ID.")

        # Verify that the access token is valid for this app.
        if tokeninfo['issued_to'] != self.secrets['web']['client_id']:
            raise AccessTokenValidationError(
                "Token's client ID does not match app's.")

    def _process_login(self, credentials):
        userinfo = self._lookup_user_info(credentials.access_token)
        user = self._get_or_create_user(userinfo)

        # Create a new login-session
        flask_session['access_token'] = credentials.access_token
        return LoginSession.create(
            token=credentials.access_token,
            provider='google',
            user=user)

    def _lookup_user_info(self, access_token):
        # Get user info
        userinfo_url = "{}/userinfo".format(self.oauth_endpoint)
        params = {'access_token': access_token, 'alt': 'json'}
        return requests.get(userinfo_url, params=params).json()

    def _get_or_create_user(self, userinfo):
        # see if user exists, if it doesn't make a new one
        user = User.lookup_by_email(userinfo.get('email'))
        if not user:
            user = User.create(name=userinfo.get('name', ''),
                               email=userinfo.get('email'),
                               picture=userinfo.get('picture', ''))
        return user

    def _load_secrets(self):
        with open(self.secrets_file_name, 'r') as file_:
            return json.loads(file_.read())
