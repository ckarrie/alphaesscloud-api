import requests
from datetime import datetime, timedelta
import hashlib

from . import const


class AlphaCloudLoginRequired(Exception):
    pass

class AlphaCloudLoginExpired(Exception):
    pass


def _validate_credentials(client, validate_token=True):
    if not client._username:
        raise AlphaCloudLoginRequired("Empty username")
    if not client._password:
        raise AlphaCloudLoginRequired("Empty password")
    if validate_token:
        if not client._token_data:
            raise AlphaCloudLoginRequired("No token, Login first")
        exprires_in = client._token_data.get('_expires_in')
        if expires_in >= datetime.now():
            raise AlphaCloudLoginExpired("Login expired")

def _get_auth_headers(client):
    now = datetime.now()
    auth_ts = str(int(datetime.timestamp(now)))		
    hash_str = const.AUTH_SIGNATURE_HASH + auth_ts
    auth_sig = const.AUTH_SIGNATURE_START + hashlib.sha512(hash_str.encode()).hexdigest() + const.AUTH_SIGNATURE_END
    auth_headers = {
        const.JSON_KEY_AUTHSIGNATURE: auth_sig,
        const.JSON_KEY_AUTHTIMESTAMP: auth_ts,
    }
    # maybe do something with expired tokens here		
    bearer_token = client._token_data.get(const.JSON_KEY_ACCESS_TOKEN, None)
    if bearer_token:
        auth_headers[const.JSON_KEY_AUTHORIZATION] = "Bearer {token}".format(token=bearer_token)
    return auth_headers


class AlphaClient(object):
    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._token_data = {}
        self.systems = {}
	    
    def validate_credentials(self, validate_token=True):
        return _validate_credentials(client=self, validate_token=validate_token)

    def get_auth_headers(self):
        return _get_auth_headers(client=self)

    def login(self):
        self.validate_credentials(validate_token=False)
        url = const.BASE_URL + const.LOGIN_PATH
        resp = requests.post(url, json={"username": self._username, "password": self._password}, headers=self.get_auth_headers())
        if resp.status_code == requests.codes.ok:
            d = resp.json().get('data')
            self._token_data = {
                const.JSON_KEY_ACCESS_TOKEN: d[const.JSON_KEY_ACCESS_TOKEN],
                'ExpiresIn': d['ExpiresIn'],
                'RefreshTokenKey': d['RefreshTokenKey'],  
                '_updated_at': datetime.now(),
                '_expires_in': datetime.now() + timedelta(seconds=d['ExpiresIn']),		
            }

    def fetch_system_list(self):
        self.validate_credentials()
        url = const.BASE_URL + const.GET_SYSTEM_LIST_PATH
        resp = requests.get(url, headers=self.get_auth_headers())
        if resp.status_code == requests.codes.ok:
            for system_dict in resp.json().get('data', []):
                system_obj = AlphaSystem(client=self, data=system_dict)
                self.systems[system_obj.system_id] = system_obj
        return self.systems


class AlphaSystem(object):
    def __init__(self, client, data):
        self.client = client
        self.system_id = data.get('system_id')
        self.sys_sn = data.get('sys_sn')
        self.bakbox_ver = data.get('bakbox_ver')
        self.data = {}
        self.last_fetched_settings = None
        self.model_inverter = None
        self.model_battery = None
        self.version_backupbox = None
        self.has_backupbox = False

    def validate_credentials(self, validate_token=True):
        return _validate_credentials(client=self.client, validate_token=validate_token)

    def get_auth_headers(self):
        return _get_auth_headers(client=self.client)

    def fetch_settings(self):
        self.validate_credentials()
        url = const.BASE_URL + const.GET_SETTING_PATH
        params = {
            'system_id': self.system_id
        }
        resp = requests.get(url, params=params, headers=self.get_auth_headers())
        if resp.status_code == requests.codes.ok:
            data = resp.json().get('data', {})
            self.last_fetched_settings = datetime.now()
            # update local vars
            self.model_inverter = data.get('minv', None)
            self.model_battery = data.get('mbat', None)
            self.version_backupbox = data.get('bakbox_ver', None)
            self.has_backupbox = self.version_backupbox is not None            
            self.data = data
            return data

    def __str__(self):
        return '<AlphaSystem {sys_sn}>'.format(system_id=self.sys_sn)


