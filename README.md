
# Home Assistant STIHL iMow
[![CI](https://github.com/ChrisHaPunkt/ha-stihl-imow/actions/workflows/validate_via_cron.yaml/badge.svg?branch=main)](https://github.com/ChrisHaPunkt/ha-stihl-imow/actions/workflows/validate_via_cron.yaml)
[![CI](https://github.com/ChrisHaPunkt/ha-stihl-imow/actions/workflows/release.yaml/badge.svg)](https://github.com/ChrisHaPunkt/ha-stihl-imow/actions/workflows/.yaml)
[![CI](https://github.com/ChrisHaPunkt/ha-stihl-imow/actions/workflows/pushpull.yaml/badge.svg)](https://github.com/ChrisHaPunkt/ha-stihl-imow/actions/workflows/pushpull.yaml)


## HomeAssistant custom component for STIHL iMow lawn mower
A platform which allows you to interact with the STIHL iMow lawn mower.

## Features
This platform is using the [STIHL iMow API](https://app.imow.stihl.com/#) via the [unofficial STIHL iMow Python WebAPI wrapper](https://github.com/ChrisHaPunkt/stihl-imow-webapi) to 
get the information from the mower via the upstream STIHL Server.  

In Home Assistant, this enables me to provide the following:

* Display current state, statistics and settings in Home Assistant,
* Upstream localisation, display state messages in you configured language
* Polling interval, 
* Switch settings like automatic mode or gps protection on or off,
* Initiate an action to a Mower via Home Assistant service call (edgeMowing, toDocking, startMowingFromPoint)

## Installation

### 1.a Using the Home Assistant Community Store ( [HACS](https://hacs.xyz/) ) 
If you're using HACS, add this Github-Repo url as a custom repo:   
`HACS 🠊 custom repositories 🠊 Type: 'Integration' 🠊 URL:`
```
https://github.com/ChrisHaPunkt/ha-stihl-imow.git
```
Afterwards go to your `HACS 🠊 Integrations 🠊 '+ EXPLORE & ADD REPOSITORIES' 🠊 search for 'STIHL'`,   
if you're not presented with a `New repository` banner, to install the component to your server.

### 1.b Without HACS
Otherwise install the component manually by putting the files from `/custom_components/stihl_imow/` in your folder `<config directory>/custom_components/stihl_imow/`

### 2. Restart your Home Assistant
You have to restart Home Assistant to make you server recognize the new integration.

## Configuration
After installing, you have to configure the new component in your Home Assistant. This is done via the UI.  

To do so, add the STIHL iMow Integration in your Servers `Configuration 🠊 Integrations 🠊 '+ ADD INTEGRATION'`.   

Within the configuration flow provide your `https://app.imow.stihl.com/#` credentials to let Home Assistant access the upstream API and configure your preferred language for the state messages.

If you want to, you can adjust the update (polling-)interval. This changes how often Home Assistant is aksing the upstream server for an update. The default and suggested value is 30 seconds.

### Screenshots
#### Integration
![grafik](https://user-images.githubusercontent.com/4389395/124358848-71bad300-dc22-11eb-9095-567a069db925.png)
#### Overview
![grafik](https://user-images.githubusercontent.com/4389395/124358816-4f28ba00-dc22-11eb-81d1-6e72f9a4b16d.png)
#### Service
![grafik](https://user-images.githubusercontent.com/4389395/124358851-74b5c380-dc22-11eb-9435-3248b84e84f6.png)

## Support
If you want to buy me a coffee, feel free: :)
[!["Buy Me A Coffee"](
https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=&slug=chrishapunkt&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff)](https://www.buymeacoffee.com/chrishapunkt)

