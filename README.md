
# Home Assistant STIHL iMow
[![CI](https://github.com/ChrisHaPunkt/ha-stihl-imow/actions/workflows/validate_via_cron.yaml/badge.svg?branch=main)](https://github.com/ChrisHaPunkt/ha-stihl-imow/actions/workflows/validate_via_cron.yaml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)


## HomeAssistant custom component for STIHL iMow lawn mower
A platform which allows you to interact with the STIHL iMow lawn mower.

If you want to  
[!["Buy Me A Coffee"](
https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=&slug=chrishapunkt&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff)](https://www.buymeacoffee.com/chrishapunkt)


## Installation

Add the URL to this repo as a custom repo in your HACS UI inside Home Assistant:
``
https://github.com/ChrisHaPunkt/ha-stihl-imow.git
``

## Features
* Display current state, statistics and settings in Home Assistant.
* Entities for error indication

### Installation
You can use HACS or install the component manually by putting the files from `/custom_components/stihl_imow/` in your folder `<config directory>/custom_components/stihl_imow/` 
### Configuration
#### ConfigFlow

The configuration is done via the UI. Install the component via HACS and add the STIHL iMow Integration. Within the configuration flow provide your `https://app.imow.stihl.com/#` credentials to let HA access the API


This platform is using the [STIHL iMow API](https://app.imow.stihl.com/#) via the [unofficial STIHL iMow Python WebAPI wrapper](https://github.com/ChrisHaPunkt/stihl-imow-webapi) to 
get the information from the mower via the upstream STIHL Server.

### Screenshots
#### Integration
![grafik](https://user-images.githubusercontent.com/4389395/124358848-71bad300-dc22-11eb-9095-567a069db925.png)
#### Overview
![grafik](https://user-images.githubusercontent.com/4389395/124358816-4f28ba00-dc22-11eb-81d1-6e72f9a4b16d.png)
#### Service
![grafik](https://user-images.githubusercontent.com/4389395/124358851-74b5c380-dc22-11eb-9435-3248b84e84f6.png)

