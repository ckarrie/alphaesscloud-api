# alphaesscloud-api
API to AlphaeSS cloud

## Requirements
- python3
- python-requests

## Installation

    git clone https://github.com/ckarrie/alphaesscloud-api/

## Usage example

    cd alphaesscloud-api
    python3

```python3
import alphaesscloud_api as ae
client = ae.AlphaClient("my@email.com", "mypassword")
client.login()
client.fetch_system_list()
for sys_id, sys_obj in client.systems.items():
    sys_data = sys_obj.fetch_settings()
    sys_obj.set_soc_cap(min_soc=26, max_soc=100)  # set SOC to 26-100%
    for cp_id, cp_obj in sys_obj.charging_piles.items():
        cp_obj.stop_charging()
```

## Goals

- charge AlphaESS battery and EV battery at the same time using PV only
    - in ECO Mode (1) this does not work, because it only charges the car if the SOC reaches 100%
    - in MAX Mode (4) this works, if you calculate the available Ampere for AlphaESS battery and House Load:
        - 2kW for AlphaESS battery: 2000W/(3x230V) = 3A per Phase
        - 2kW for House Load: 2000W/(3x230V) = 3A per Phase
        - `AlphaChargingPile.change_charging_current(ampere)` with `ampere` = PV(A) - 6A

## Code reference/documentation

### `AlphaClient`

Represents a user account

#### `AlphaClient(username, password)`

Set plain login credentials

#### `AlphaClient.login()`

Method to generate required get/post headers

#### `AlphaClient.fetch_system_list()`

Required method to fill attribute `AlphaClient.systems`

#### `AlphaClient.systems`

Dict of AlphaESS systems for this user (key = system id, value = `AlphaSystem` instance)

### `AlphaSystem`

Represents a AlphaESS System

#### `AlphaSystem.fetch_settings()`

Required method to fill attribute `AlphaSystem.charging_piles` and set model names and version numbers

### `AlphaSystem.set_soc_cap(min_soc=20, max_soc=100)`

Set min and max State of Charge for the battery

### `AlphaChargingPile`

Represents a charging pile (aka Wallbox)

#### `AlphaChargingPile.stop_charging()`

stops charging on that pile

#### `AlphaChargingPile.start_charging()`

starts charging on that pile

#### `AlphaChargingPile.fetch_charging_status()`

returns text representation of current charging state

#### `AlphaChargingPile.change_charging_mode(mode)`

sets charging `mode`:
- `1`: `SLOW` 
- `2`: `NORMAL` 
- `3`: `FAST` 
- `4`: `MAX`

#### `AlphaChargingPile.change_charging_current(ampere)`

- `ampere` between `6` and `16`
- works only if `AlphaChargingPile.change_charging_mode(mode=4)`

## Supported
- System:
    - Set SOC (min/max) via `AlphaSystem.set_soc_cap`
- EV Charger / Wallbox:
    - Set Charging Mode
        - `1`: `SLOW` aka "ECO-Ladung > Langsamladung"
        - `2`: `NORMAL` aka "ECO-Ladung > Schonladung"
        - `3`: `FAST` aka "ECO-Ladung > Schnelladung"
        - `4`: `MAX` aka "Kundenspezifische Ladeleistung", use `AlphaChargingPile.change_charging_current` for Ampere per Phase
    - Start and stop charging
    - Get Charging Status
 
## Special Thanks to
- [@vdwals](https://github.com/vdwals) - see https://github.com/CharlesGillanders/homeassistant-alphaESS/issues/70
