
# Alfen Wallbox - HomeAssistant Integration

This is a custom component to allow control of Alfen Wallboxes in [HomeAssistant](https://home-assistant.io).

The component is a fork of the [Garo Wallbox custom integration](https://github.com/sockless-coding/garo_wallbox).

![Screenshot 2023-07-02 at 18 09 47](https://github.com/leeyuentuen/alfen_wallbox/assets/1487966/322e9e05-117f-4adc-b159-7177533fde01)

![Screenshot 2023-07-02 at 18 09 58](https://github.com/leeyuentuen/alfen_wallbox/assets/1487966/310f0537-9bc4-49a0-9552-0c8414b97425)

![Screenshot 2023-07-02 at 18 10 13](https://github.com/leeyuentuen/alfen_wallbox/assets/1487966/f5e2670d-4bd8-40d2-bbbe-f0628cff6273)


Example of running in Services:
Note; the name of the configured charging point is "wallbox" in these examples.

Changing Green Share %
```
service: alfen_wallbox.set_green_share
data:
  entity_id: sensor.wallbox
  value: 95
```

Changing Comfort Charging Power in Watt
```
service: alfen_wallbox.set_comfort_power
data:
  entity_id: sensor.wallbox
  value: 1450
```

Enable phase switching
```
service: alfen_wallbox.enable_phase_switching
data:
  entity_id: sensor.wallbox
```


Disable phase switching
```
service: alfen_wallbox.disable_phase_switching
data:
  entity_id: sensor.wallbox
```

> After reverse engineering the API myself I found out that there is already a python libary wrapping the Alfen API.
> https://gitlab.com/LordGaav/alfen-eve/-/tree/develop/alfeneve

## Installation

### Install using HACS (recomended)
If you do not have HACS installed yet visit https://hacs.xyz for installation instructions.
In HACS go to the Integrations section hit the big + at the bottom right and search for **Alfen Wallbox**.

### Install manually
Clone or copy this repository and copy the folder 'custom_components/alfen_wallbox' into '<homeassistant config>/custom_components/alfen_wallbox'

## Configuration

Once installed the Alfen Wallbox integration can be configured via the Home Assistant integration interface 
where you can enter the IP address of the device.

### Home Assistant Energy Dashboard
The wallbox can be added to the Home Assistant Energy Dashboard using the `_meter_reading` sensor.
