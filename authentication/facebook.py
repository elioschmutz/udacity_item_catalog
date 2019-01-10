from authentication.base import AuthProvider
from authentication.base import UserData
import requests


class FacebookAuth(AuthProvider):
    secrets_file_name = 'facebook_secrets.json'
    provider_name = 'facebook'

    def process_auth_provider_login(self, code):
        access_token = self._get_app_token(code)
        userdata = self._lookup_user_info(access_token)

        return access_token, userdata

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

        return UserData(
            userinfos.get('email'),
            userinfos.get('name'),
            userinfos.get('picture'))
