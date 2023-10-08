# Basics
DICT_FALLBACK = -1

# URLs
BASE_URL = "https://cloud.alphaess.com/api/"
LOGIN_PATH = "Account/Login"
GET_SETTING_PATH = "Account/GetCustomUseESSSetting"
GET_SYSTEM_LIST_PATH = "Account/GetCustomUseESSList"

# JSON/HEADERS Keys
JSON_KEY_ACCESS_TOKEN = "AccessToken"
JSON_KEY_AUTHSIGNATURE = "Authsignature"
JSON_KEY_AUTHTIMESTAMP = "Authtimestamp"
JSON_KEY_AUTHORIZATION = "Authorization"

# Cloud
# thanks to https://bitbucket.org/vdwals/alphaesscloud2mqtt/src/master/src/main/java/de/vdw/io/alpha2mqtt/config/Constants.java
AUTH_SIGNATURE_START = "al8e4s"
AUTH_SIGNATURE_HASH = "LS885ZYDA95JVFQKUIUUUV7PQNODZRDZIS4ERREDS0EED8BCWSS"
AUTH_SIGNATURE_END = "ui893ed"

# Charging Pile
MAX_CURRENT_RANGE = range(6, 16)

CHARGING_MODE_SLOW = 1
CHARGING_MODE_NORMAL = 2
CHARGING_MODE_FAST = 3
CHARGING_MODE_MAX = 4

CHARGING_MODES = {
    CHARGING_MODE_SLOW: 'Slow',
    CHARGING_MODE_NORMAL: 'Normal',
    CHARGING_MODE_FAST: 'Fast',
    CHARGING_MODE_MAX: 'Customer / Max'
}

CHARGINGPILE_STATUS = {
    DICT_FALLBACK: 'CHARGINGPILE_STATUS CODE NOT FOUND',  # internal
    3: 'Charging',
    4: 'Insufficient power',  # unzureichende Leistung
    6: 'Charging stopped',
}
