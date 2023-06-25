# Alfen Wallbox - HomeAssistant Integration

This is a custom component to allow control of Alfen Wallboxes in [HomeAssistant](https://home-assistant.io).

The component is a fork of the [Garo Wallbox custom integration](https://github.com/sockless-coding/garo_wallbox).

![image](https://github.com/leeyuentuen/alfen_wallbox/assets/1487966/a25af9bc-a6b3-496d-9c04-6812825cb375)

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
