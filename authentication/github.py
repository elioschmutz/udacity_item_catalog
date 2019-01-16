from authentication.base_provider import AuthProvider
from authentication.base_provider import UserData
from authentication.errors import AccessTokenValidationError
import requests


class GithubAuth(AuthProvider):
    secrets_file_name = 'github_secrets.json'
    provider_name = 'github'

    def process_auth_provider_login(self, code):
        access_token = self._get_app_token(code)
        userdata = self._lookup_user_info(access_token)

        return access_token, userdata

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

    def _lookup_user_info(self, access_token):
        userinfo_url = "https://api.github.com/user"
        params = {'access_token': access_token}
        headers = {'Accept': 'application/json'}
        userinfos = requests.get(
            userinfo_url, params=params, headers=headers).json()

        return UserData(
            userinfos.get('email'),
            userinfos.get('name'),
            userinfos.get('avatar_url'))
