import requests
from datetime import datetime
import hashlib

from . import const


class AlphaCloudLoginRequired(Exception):
    pass
    

class AlphaCloud(object):
    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._token_data = {}
	    
    def validate_credentials(self, validate_token=True):
	    if not self._username:
		    raise AlphaCloudLoginRequired("Empty username")
	    if not self._password:
		    raise AlphaCloudLoginRequired("Empty password")
	    if validate_token:
		    if not self._token_data:
			    raise AlphaCloudLoginRequired("No token, Login first")						

    def get_auth_headers(self):
	    now = datetime.now()
	    auth_ts = str(int(datetime.timestamp(now)))		
	    hash_str = const.AUTH_SIGNATURE_HASH + auth_ts
	    auth_sig = const.AUTH_SIGNATURE_START + hashlib.sha512(hash_str.encode()).hexdigest() + const.AUTH_SIGNATURE_END
	    auth_headers = {
	        const.JSON_KEY_AUTHSIGNATURE: auth_sig,
	        const.JSON_KEY_AUTHTIMESTAMP: auth_ts,
	    }
	    # maybe do something with expired tokens here		
	    bearer_token = self._token_data.get(const.JSON_KEY_ACCESS_TOKEN, None)
	    if bearer_token:
		    auth_headers[const.JSON_KEY_AUTHORIZATION] = "Bearer {token}".format(token=bearer_token)
	    return auth_headers

    def login(self):
	    self.validate_credentials(validate_token=False)
	    url = BASE_URL + LOGIN_PATH
	    resp = requests.post(url, json={"username": self._username, "password": self._password}, headers=self.get_auth_headers())
	    if resp.status_code == requests.codes.ok:
		    d = resp.json().get('data')
		    self._token_data = {
			    const.JSON_KEY_ACCESS_TOKEN: d[const.JSON_KEY_ACCESS_TOKEN],
			    'ExpiresIn': d['ExpiresIn'],
			    'RefreshTokenKey': d['RefreshTokenKey'],  
			    '_updated_at': datetime.now(),
			    '_expires_in': datetime.now() + datetime.timedelta(seconds=d['ExpiresIn']),		
		    }
	    
    def get_settings(self, system_id=None):
	    self.validate_credentials()
	    url = const.BASE_URL + const.GET_SETTING_PATH
	    params = {}
	    if system_id:
	        params = {
	            'system_id': system_id
	        }
	    resp = requests.get(url, params=params, headers=self.get_auth_headers())
	    if resp.status_code == requests.codes.ok:
		    return resp.json()
	    
		    
	    
