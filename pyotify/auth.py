import os
import json
import urllib.parse
import requests



from . import utils

OAUTH_TOKEN_URL = 'https://accounts.spotify.com/api/token'
OAUTH_AUTHORIZE_URL = 'https://accounts.spotify.com/authorize'
redirect_uri = 'http://localhost:8888/callback/'

class SpotifyAuthError(Exception):
    pass

class SpotifyClientCredentialsAuth():
    def __init__(self, session, client_id, client_secret):
        self.session = session
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_code = None
        self.token = None

    def get_access_token(self):
        if not self.token or utils.is_token_expired(self.token):
            self.access_code = self._request_access_code()
            self.token = self._request_token()
            utils.add_custom_values_to_token(self.token)
            return self.token['access_token']
        return self.token['access_token']

    def _request_token(self):
        data = {
            'grant_type': 'authorization_code',
            'code': self.access_code,
            'redirect_uri': redirect_uri,

        }

        headers = utils.get_authorization_headers(self.client_id, self.client_secret)

        response = requests.post(OAUTH_TOKEN_URL, data=data, headers=headers)
        token = json.loads(response.text)

        return token

    def _request_access_code(self):
        with open('scopes.txt', 'r') as f:
            scope = f.read()
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'scope': scope
        }

        headers = utils.get_authorization_headers(self.client_id, self.client_secret)

        response = requests.get(OAUTH_AUTHORIZE_URL, params=params, headers=headers)

        response.raise_for_status()

        print(response.url)
        code = input('login to spotify and return the code parameter in console:')
        return code

    def is_token_expired(self, token):
        return utils.is_token_expired(token)

    def add_custom_values_to_token(self, token):
        return utils.add_custom_values_to_token(token)

class SpotifyUserAuth():
    def __init__(self, client_id, client_secret, redirect_uri, state=None, scope=None, cached_token_path=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.state = state
        self.scope = utils.normalize_scope(scope)
        self.cached_token_path = cached_token_path

    def get_cached_token(self):
        token = None

        if os.path.exists(self.cached_token_path):
            with open(self.cached_token_path, 'r') as f:
                token = json.loads(f.read())
            if 'scope' not in token:
                return None
            if utils.is_token_expired(token):
                token = self.refresh_access_token(token['refresh_token'])

        return token

    def _get_authorization_headers(self):
        return utils.get_authorization_headers(self.client_id, self.client_secret)

    def get_authorize_url(self, state=None, show_dialog=False):
        payload = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri
        }
        if self.scope:
            payload['scope'] = self.scope
        if state is None:
            state = self.state
        else:
            payload['state'] = state
        if show_dialog:
            payload['show_dialog'] = True

        urlparams = urllib.parse.urlencode(payload)

        return "%s?%s" % (OAUTH_AUTHORIZE_URL, urlparams)

    def refresh_access_token(self, refresh_token):
        payload = {
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'}

        headers = self._get_authorization_headers()

        response = requests.post(OAUTH_TOKEN_URL, data=payload, headers=headers)

        response.raise_for_status()

        token = response.json()
        token = utils.add_custom_values_to_token(token)
        if 'refresh_token' not in token:
            token['refresh_token'] = refresh_token
        return token
