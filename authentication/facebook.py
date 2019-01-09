from flask import session as flask_session
from models import LoginSession
from models import User
import json
import requests


class FacebookAuth(object):
    secrets = None
    oauth_endpoint = ''
    secrets_file_name = 'facebook_secrets.json'

    def __init__(self):
        self.secrets = self._load_secrets()

    def login(self, access_token):
        """Logs in a user based on the auth_code received from the frontend
        """
        token = self._get_app_token(access_token)
        return self._process_login(token)

    def logout(self, access_token):
        requests.post('https://accounts.google.com/o/oauth2/revoke',
                      params={'token':access_token},
                      headers={'content-type': 'application/x-www-form-urlencoded'})

    def _get_app_token(self, access_token):
        """Valdiate the accesstoken
        """
        # Verify that the access token is used for the intended user.
        url = 'https://graph.facebook.com/oauth/access_token'
        params = {
            'grant_type': 'fb_exchange_token',
            'client_id': self.secrets['web']['app_id'],
            'client_secret': self.secrets['web']['app_secret'],
            'fb_exchange_token': access_token
        }

        result = requests.get(url, params=params)

        '''
        Due to the formatting for the result from the server token exchange we have to
        split the token first on commas and select the first index which gives us the key : value
        for the server access token then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used directly in the graph
        api calls
        '''
        return result.json().get('access_token')
        # return result.split(',')[0].split(':')[1].replace('"', '')

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
        userinfo_url = "https://graph.facebook.com/v2.8/me"
        params = {'access_token': access_token, 'fields': 'name,id,email'}
        userinfos = requests.get(userinfo_url, params=params).json()

        img_url = 'https://graph.facebook.com/v2.8/me/picture'
        params = {
            'access_token': access_token,
            'redirect': 0,
            'height': 200,
            'width': 200,
            }

        result = requests.get(img_url, params=params).json()
        userinfos['picture'] = result["data"]["url"]

        return userinfos

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
