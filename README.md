
# Home Assistant STIHL iMow
[![CI](https://github.com/ChrisHaPunkt/ha-stihl-imow/actions/workflows/validate_via_cron.yaml/badge.svg?branch=main)](https://github.com/ChrisHaPunkt/ha-stihl-imow/actions/workflows/validate_via_cron.yaml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)


[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)

## HomeAssistant custom component for STIHL iMow lawn mower
A platform which allows you to interact with the STIHL iMow lawn mower.

### Warning
This is an early development version. Things are going to change in upcoming releases like entity names and the information currently available in the entity attributes will become own entities. 

## Features
* Display current state as human readable string if the action is already known by the python-api package. If not, the corresponding number is displayed. Information like `RainStaus` or `BladeService` are available on the attributes on the `sensor.imow_<mower>_state`) 
* Fetch statistics `TotalBladeOperatingTime`,`TotalDistanceTravelled`, `TotalOperatingTime` (Available via attributes in `sensor.imow_<mower>_total_operating_time`)
* Fetch all mower upstream information like battery_level, current settings or location (Available via attributes in `sensor.imow_<mower>_battery_level`)

### Installation
You can use HACS or install the component manually by putting the files from `/custom_components/stihl_imow/` in your folder `<config directory>/custom_components/stihl_imow/` 
### Configuration
#### ConfigFlow

The configuration is done via the UI. Install the component via HACS and add the STIHL iMow Integration. Within the configuration flow provide your `https://app.imow.stihl.com/#` credentials to let HA access the API


This platform is using the [STIHL iMow API](https://app.imow.stihl.com/#) via the [unofficial STIHL iMow Python WebAPI wrapper](https://github.com/ChrisHaPunkt/stihl-imow-webapi) to 
get the information from the mower via the upstream STIHL Server.

### Screenshots

![Bildschirmfoto vom 2021-06-06 17-55-35](https://user-images.githubusercontent.com/4389395/120931107-71e1b480-c6f0-11eb-8a3b-ceb1fd82c8dc.png)  
![Bildschirmfoto vom 2021-06-06 17-52-10](https://user-images.githubusercontent.com/4389395/120931060-42cb4300-c6f0-11eb-9573-d91162d25506.png)  
![Bildschirmfoto vom 2021-06-06 17-52-51](https://user-images.githubusercontent.com/4389395/120931062-452d9d00-c6f0-11eb-8299-b160addc2fce.png)  
![Bildschirmfoto vom 2021-06-06 17-53-34](https://user-images.githubusercontent.com/4389395/120931065-45c63380-c6f0-11eb-9689-3fc8caf51ab1.png)  


