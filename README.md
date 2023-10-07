# alphaesscloud-api
API to AlphaeSS cloud

## Requirements
- python3
- python-requests

## Installation

    git clone https://github.com/ckarrie/alphaesscloud-api/

## Usage

    cd alphaesscloud-api
    python3

```python3
import alphaesscloud_api as ae
client = ae.AlphaClient("my@email.com", "mypassword")
client.login()
client.fetch_system_list()
for sys_id, sys_obj in client.systems.items():
    sys_data = sys_obj.fetch_settings()
    for cp_id, cp_obj in sys_obj.charging_piles.items():
        cp_obj.stop_charging()
```

## Supported
- Start and stop charging
