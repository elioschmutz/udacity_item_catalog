from authentication.base import AuthProvider
from authentication.base import UserData
from authentication.errors import AccessTokenValidationError
from oauth2client.client import flow_from_clientsecrets
import requests


class GoogleAuth(AuthProvider):
    oauth_endpoint = 'https://www.googleapis.com/oauth2/v1'
    secrets_file_name = 'google_secrets.json'
    provider_name = 'google'

    def process_auth_provider_login(self, code):
        """Logs in a user based on the auth_code received from the frontend
        """
        credentials = self._get_credentials_object(code)
        access_token = credentials.access_token

        self._validate_access_token(credentials)

        userdata = self._lookup_user_info(access_token)

        return access_token, userdata

    def logout(self, access_token):
        requests.post('https://accounts.google.com/o/oauth2/revoke',
                      params={'token': access_token},
                      headers={'content-type': 'application/x-www-form-urlencoded'})

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

    def _validate_access_token(self, credentials):
        """Valdiate the accesstoken
        """
        # Verify that the access token is used for the intended user.
        tokeninfo = self._get_token_info(credentials.access_token)
        gplus_id = credentials.id_token['sub']
        if tokeninfo['user_id'] != gplus_id:
            raise AccessTokenValidationError(
                "Token's user ID doesn't match given user ID.")

        # Verify that the access token is valid for this app.
        if tokeninfo['issued_to'] != self.secrets['web']['client_id']:
            raise AccessTokenValidationError(
                "Token's client ID does not match app's.")

    def _lookup_user_info(self, access_token):
        userinfo_url = "{}/userinfo".format(self.oauth_endpoint)
        params = {'access_token': access_token, 'alt': 'json'}
        userinfos = requests.get(userinfo_url, params=params).json()

        return UserData(
            userinfos.get('email'),
            userinfos.get('name'),
            userinfos.get('picture'))
