import requests
from datetime import datetime, timedelta
import hashlib

from . import const


class AlphaCloudLoginRequired(Exception):
    pass

class AlphaCloudLoginExpired(Exception):
    pass



class AlphaClient(object):
    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._token_data = {}
        self.systems = {}
	    
    def validate_credentials(self, validate_token=True):
        if not self._username:
            raise AlphaCloudLoginRequired("Empty username")
        if not self._password:
            raise AlphaCloudLoginRequired("Empty password")
        if validate_token:
            if not self._token_data:
                raise AlphaCloudLoginRequired("No token, Login first")
            expires_in = self._token_data.get('_expires_in')
            if expires_in <= datetime.now():
                raise AlphaCloudLoginExpired("Login expired")

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
        self.charging_piles = {}

    def fetch_settings(self):
        self.client.validate_credentials()
        url = const.BASE_URL + const.GET_SETTING_PATH
        params = {
            'system_id': self.system_id
        }
        resp = requests.get(url, params=params, headers=self.client.get_auth_headers())
        if resp.status_code == requests.codes.ok:
            data = resp.json().get('data', {})
            self.last_fetched_settings = datetime.now()
            # update local vars
            self.model_inverter = data.get('minv', None)
            self.model_battery = data.get('mbat', None)
            self.version_backupbox = data.get('bakbox_ver', None)
            self.has_backupbox = self.version_backupbox is not None
            # charging piles
            for cp_data in data.get('charging_pile_list', []):
                chargingpile_obj = AlphaChargingPile(alpha_system=self, data=cp_data)
                self.charging_piles[chargingpile_obj.chargingpile_id] = chargingpile_obj
            self.data = data
            return data

    def __str__(self):
        return f'<AlphaSystem {self.sys_sn}>'


class AlphaChargingPile(object):
    def __init__(self, alpha_system, data):
        self.alpha_system = alpha_system
        self.chargingpile_sn = data.get('chargingpile_sn')
        self.chargingpile_id = data.get('chargingpile_id')
        self.max_current = int(data.get('max_current'))
        self.data = data

    def stop_charging(self):
        self.alpha_system.client.validate_credentials()
        url = const.BASE_URL + 'ESS/StopCharging'
        resp = requests.post(url, json={'sys_sn': self.alpha_system.sys_sn, 'chargingpile_sn': self.chargingpile_sn}, headers=self.alpha_system.client.get_auth_headers())
        return resp.status_code == requests.codes.ok

    def start_charging(self):
        self.alpha_system.client.validate_credentials()
        url = const.BASE_URL + 'ESS/StartCharging'
        resp = requests.post(url, json={'sys_sn': self.alpha_system.sys_sn, 'chargingpile_sn': self.chargingpile_sn}, headers=self.alpha_system.client.get_auth_headers())
        return resp.status_code == requests.codes.ok

    def post_settings(self, json_data=None):
        self.alpha_system.client.validate_credentials()
        url = const.BASE_URL + 'Account/CustomUseESSSetting'
        resp = requests.post(url, json=json_data, headers=self.alpha_system.client.get_auth_headers())
        if resp.status_code == requests.codes.ok:
            return True

    def _generate_settings_json(self, update_kvp={}):
        cp_data = self.data.copy()
        cp_data.update(update_kvp)
        cp_data['system_id'] = self.alpha_system.system_id
        sys_data = self.alpha_system.data.copy()
        for i, cp in enumerate(sys_data.get('charging_pile_list')):
            if cp.get('chargingpile_id') == self.chargingpile_id:
                sys_data['charging_pile_list'][i] = cp_data
                sys_data.update(cp_data)
        return sys_data

    def change_charging_mode(self, mode):
        if mode in const.CHARGING_MODES.keys():
            sys_data = self._generate_settings_json(update_kvp={'chargingmode': str(mode})
            changed = self.post_settings(json_data=sys_data)
            if changed:
                # update self
                self.alpha_system.fetch_settings()            

    def change_charging_current(self, ampere):
        current_ampere = self.max_current
        ampere = int(ampere)
        if ampere in const.MAX_CURRENT_RANGE:
            sys_data = self._generate_settings_json(update_kvp={'max_current': str(ampere})            
            changed = self.post_settings(json_data=sys_data)
            if changed:
                # update self
                self.alpha_system.fetch_settings()
