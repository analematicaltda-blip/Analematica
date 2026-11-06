"""Small bounded Meta read client. Only OAuth token exchange may POST.
Never follow provider pagination URLs or return raw errors/tokens to callers.
"""
import hashlib
import hmac
import re
import requests

class MetaGraphError(Exception):
    def __init__(self, kind, status=502):
        self.kind, self.status = kind, status
        super().__init__(kind)

class MetaGraph:
    def __init__(self, version, app_id, secret, token=None):
        if not re.fullmatch(r'v\d{1,2}\.\d', version):
            raise MetaGraphError('configuration_invalid', 409)
        self.base = 'https://graph.facebook.com/' + version
        self.app_id, self.secret, self.token = app_id, secret, token

    def _request(self, method, path, params=None, data=None):
        if not re.fullmatch(r'[A-Za-z0-9_/-]+', path) or '..' in path:
            raise MetaGraphError('request_invalid', 422)
        if method != 'GET' and not (method == 'POST' and path == 'oauth/access_token'):
            raise MetaGraphError('advertising_writes_disabled', 403)
        headers = {'Accept': 'application/json'}
        params = dict(params or {})
        if self.token:
            headers['Authorization'] = 'Bearer ' + self.token
            params['appsecret_proof'] = hmac.new(self.secret.encode(), self.token.encode(), hashlib.sha256).hexdigest()
        try:
            response = requests.request(method, self.base + '/' + path, headers=headers, params=params, data=data, timeout=(5, 20), allow_redirects=False)
            if 300 <= response.status_code < 400:
                raise MetaGraphError('unexpected_redirect')
            if len(response.content) > 2 * 1024 * 1024:
                raise MetaGraphError('response_too_large')
            body = response.json()
        except (requests.RequestException, ValueError):
            raise MetaGraphError('network_or_response_error') from None
        if not isinstance(body, dict):
            raise MetaGraphError('response_invalid')
        if 'error' in body or not response.ok:
            error = body.get('error') if isinstance(body.get('error'), dict) else {}
            code = error.get('code')
            if code == 190:
                raise MetaGraphError('authorization_expired', 401)
            if code in [10, 200, 294]:
                raise MetaGraphError('permission_missing', 403)
            if code in [4, 17, 32, 613] or response.status_code == 429:
                raise MetaGraphError('rate_limited', 429)
            raise MetaGraphError('provider_request_failed')
        return body

    def get(self, path, **params):
        return self._request('GET', path, params=params)

    def exchange_system(self, code, redirect_uri):
        body = self._request('POST', 'oauth/access_token', data={'client_id': self.app_id, 'client_secret': self.secret, 'redirect_uri': redirect_uri, 'code': code})
        if not isinstance(body.get('access_token'), str) or not body['access_token']:
            raise MetaGraphError('token_missing')
        return body

    def exchange(self, code, redirect_uri):
        short = self._request('POST', 'oauth/access_token', data={'client_id': self.app_id, 'client_secret': self.secret, 'redirect_uri': redirect_uri, 'code': code})
        token = short.get('access_token')
        if not isinstance(token, str) or not token:
            raise MetaGraphError('token_missing')
        long = self._request('POST', 'oauth/access_token', data={'grant_type': 'fb_exchange_token', 'client_id': self.app_id, 'client_secret': self.secret, 'fb_exchange_token': token})
        if not isinstance(long.get('access_token'), str) or not long['access_token']:
            raise MetaGraphError('token_missing')
        return long
