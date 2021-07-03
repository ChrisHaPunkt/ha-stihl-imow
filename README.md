
# Home Assistant STIHL iMow
[![CI](https://github.com/ChrisHaPunkt/ha-stihl-imow/actions/workflows/validate_via_cron.yaml/badge.svg?branch=main)](https://github.com/ChrisHaPunkt/ha-stihl-imow/actions/workflows/validate_via_cron.yaml)
[![CI](https://github.com/ChrisHaPunkt/ha-stihl-imow/actions/workflows/release.yaml/badge.svgn)](https://github.com/ChrisHaPunkt/ha-stihl-imow/actions/workflows/.yaml)
[![CI](https://github.com/ChrisHaPunkt/ha-stihl-imow/actions/workflows/pushpull.yaml/badge.svg)](https://github.com/ChrisHaPunkt/ha-stihl-imow/actions/workflows/pushpull.yaml)


## HomeAssistant custom component for STIHL iMow lawn mower
A platform which allows you to interact with the STIHL iMow lawn mower.

## Features
* Display current state, statistics and settings in Home Assistant,
* Switch settings on and off,
* Initiate a Job to a Mower via Home Assistant Services

If you want to 
[!["Buy Me A Coffee"](
https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=&slug=chrishapunkt&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff)](https://www.buymeacoffee.com/chrishapunkt)



### Installation
You can use HACS or install the component manually by putting the files from `/custom_components/stihl_imow/` in your folder `<config directory>/custom_components/stihl_imow/`

Otherwise add this Repo to your HACS:
``
https://github.com/ChrisHaPunkt/ha-stihl-imow.git
``
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

