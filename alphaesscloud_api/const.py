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
CHARGING_MODES = {
    1: 'Slow',
    2: 'Normal',
    3: 'Fast',
    4: 'Customer / Max'
}
CHARGINGPILE_STATUS = {
    -1: 'CHARGINGPILE_STATUS CODE NOT FOUND',  # internal
    3: 'Charging',
    6: 'Charging stopped',
}
