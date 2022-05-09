# Alfen Wallbox - HomeAssistant Integration

This is a custom component to allow control of Alfen Wallboxes in [HomeAssistant](https://home-assistant.io).

The component is a fork of the [Garo Wallbox custom integration](https://github.com/sockless-coding/garo_wallbox).

![Screenshot](https://github.com/egnerfl/alfen_wallbox/blob/master/doc/screenshot.png)

## Installation

### Install using HACS (recomended)
If you do not have HACS installed yet visit https://hacs.xyz for installation instructions.
In HACS go to the Integrations section hit the big + at the bottom right and search for **Alfen Wallbox**.

### Install manually
Clone or copy this repository and copy the folder 'custom_components/alfen_wallbox' into '<homeassistant config>/custom_components/alfen_wallbox'

## Configuration

Once installed the Alfen Wallbox integration can be configured via the Home Assistant integration interface 
where you can enter the IP address of the device.

### Energy consumption

To measure the energy consumption of the Wallbox you can combine the `_active_power_total` sensor with the [Riemann sum integral - Integration](https://www.home-assistant.io/integrations/integration/).

``` yaml
  - platform: integration
    source: sensor.alfen_wallbox_active_power_total
    name: Alfen Wallbox Energy Total
    unique_id: alfen_wallbox_energy_total
    unit_prefix: k
    round: 2
    method: left
```

This way you can monitor the energy consumption in the Home Assistant Energy Dashboard.
