
# Home Assistant STIHL iMow
[![CI validate](https://img.shields.io/github/actions/workflow/status/ChrisHaPunkt/ha-stihl-imow/validate_via_cron.yaml?style=for-the-badge&logo=github&logoColor=ccc&label=validate)](https://github.com/ChrisHaPunkt/ha-stihl-imow/actions/workflows/validate_via_cron.yaml)
[![CI release](https://img.shields.io/github/actions/workflow/status/ChrisHaPunkt/ha-stihl-imow/release.yaml?style=for-the-badge&logo=github&logoColor=ccc&label=release)](https://github.com/ChrisHaPunkt/ha-stihl-imow/actions/workflows/release.yaml)
[![CI push/pull](https://img.shields.io/github/actions/workflow/status/ChrisHaPunkt/ha-stihl-imow/pushpull.yaml?style=for-the-badge&logo=github&logoColor=ccc&branch=main&label=push%2Fpull)](https://github.com/ChrisHaPunkt/ha-stihl-imow/actions/workflows/pushpull.yaml)
[![latest release](https://img.shields.io/github/v/release/ChrisHaPunkt/ha-stihl-imow?style=for-the-badge&logo=github&logoColor=ccc&label=latest)](https://github.com/ChrisHaPunkt/ha-stihl-imow/releases/latest)
[![release date](https://img.shields.io/github/release-date/ChrisHaPunkt/ha-stihl-imow?style=for-the-badge&logo=github&logoColor=ccc&label=released)](https://github.com/ChrisHaPunkt/ha-stihl-imow/releases/latest)
[![hainstall][hainstallbadge]][hainstall]
[![Buy Me A Coffee](https://img.shields.io/badge/buy%20me%20a-coffee-FFDD00?style=for-the-badge&logo=buymeacoffee&logoColor=000)](https://www.buymeacoffee.com/chrishapunkt)

[hainstall]: https://my.home-assistant.io/redirect/config_flow_start/?domain=stihl_imow
[hainstallbadge]: https://img.shields.io/badge/dynamic/json?style=for-the-badge&logo=home-assistant&logoColor=ccc&label=usage&suffix=%20installs&cacheSeconds=15600&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.stihl_imow.total


# Limitations
### This integration only supports the STIHL iMow Generation up to __4__
This integration is NOT  compatible to Generation 5 mowers from STIHL.   
If your credentials work on https://app.imow.stihl.com/#/ you can use this integration.  
If your credentials are only working on https://myimow.stihl.com/ you can __NOT__ use this integration.
 
See https://github.com/ChrisHaPunkt/stihl-imow-webapi/issues/13 

## HomeAssistant custom component for STIHL iMow lawn mower
A platform which allows you to interact with the STIHL iMow lawn mower.

## Features
This platform is using the [STIHL iMow API](https://app.imow.stihl.com/#) via the [unofficial STIHL iMow Python WebAPI wrapper](https://github.com/ChrisHaPunkt/stihl-imow-webapi) to
get the information from the mower via the upstream STIHL Server.

In Home Assistant, this enables me to provide the following:

* Display current state, statistics and settings in Home Assistant,
* Support for **multiple mowers** on the same STIHL account,
* Upstream localisation: display state messages in your configured language,
* Localised entity names and configuration UI in 10 languages,
* Switch settings like automatic mode, child lock or GPS protection on or off,
* Initiate an action to a mower via the `stihl_imow.intent` action (edge mowing, return to dock, start mowing from point, start mowing),
* Automatic re-authentication and reconfiguration from the UI,
* Diagnostics download (with credentials redacted) for troubleshooting.

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

The integration polls the STIHL cloud every 30 seconds. Following Home Assistant's guidance for cloud services, the polling interval is fixed and not user-configurable.

## Data updates
The integration polls the STIHL cloud API about every 30 seconds and refreshes every entity of every mower from a single fetch per mower. STIHL is a cloud service, so there is no local or push update; the 30-second interval balances freshness against the upstream server's rate limits.

## Supported devices
STIHL iMow robotic mowers of **Generation 4 and earlier** — any mower that appears in your account on https://app.imow.stihl.com. Generation 5 mowers (https://myimow.stihl.com) are not supported (see [Limitations](#limitations)).

## Use cases
- Get a notification when your mower reports an error or gets stuck.
- Send the mower back to its dock when rain is detected or when you start an outdoor activity.
- Track total mowed distance and operating time over time with the statistics sensors.
- Start edge mowing on a schedule.
- Show battery charge level and the current state on a dashboard.

## Example automations
Notify when the mower reports an error:
```yaml
automation:
  - alias: "iMow error notification"
    triggers:
      - trigger: state
        entity_id: binary_sensor.<mower>_error
        to: "on"
    actions:
      - action: notify.notify
        data:
          message: "STIHL iMow error: {{ states('sensor.<mower>_status_message') }}"
```

Send the mower back to the dock at sunset:
```yaml
automation:
  - alias: "iMow dock at sunset"
    triggers:
      - trigger: sun
        event: sunset
    actions:
      - action: stihl_imow.intent
        data:
          mower_device: <your mower device id>
          action: toDocking
```

Start mowing from a defined start point for 60 minutes:
```yaml
      - action: stihl_imow.intent
        data:
          mower_device: <your mower device id>
          action: startMowingFromPoint
          duration: "60"
          startpoint: 1
```

## Troubleshooting
- **"Invalid authentication" or a re-authentication prompt:** your STIHL password changed or the token expired. Use the re-authentication prompt, or `Settings 🠊 Devices & Services 🠊 STIHL iMow 🠊 Reconfigure`, to enter your current password.
- **Integration won't add / "Failed to connect":** verify your credentials work at https://app.imow.stihl.com. If they only work at https://myimow.stihl.com, your mower is Generation 5 and is not supported.
- **Timeouts in the log:** the upstream STIHL server occasionally responds slowly; the integration retries and keeps working. Occasional timeout log lines are harmless.
- **A sensor is missing:** some sensors are disabled by default (e.g. *Mowing area (feet)*, *Time zone*, *Last GPS position*). Enable them from the entity settings. Read-only diagnostic sensors are grouped under the device's *Diagnostic* section and settings switches under *Configuration*.
- **Report a problem:** download diagnostics from `Settings 🠊 Devices & Services 🠊 STIHL iMow 🠊 (three-dot menu) 🠊 Download diagnostics` (credentials are redacted) and attach it to a GitHub issue.

### Screenshots
#### Integration
![grafik](https://user-images.githubusercontent.com/4389395/124358848-71bad300-dc22-11eb-9095-567a069db925.png)
#### Overview
![grafik](https://user-images.githubusercontent.com/4389395/124358816-4f28ba00-dc22-11eb-81d1-6e72f9a4b16d.png)
#### Service
![grafik](https://user-images.githubusercontent.com/4389395/124358851-74b5c380-dc22-11eb-9435-3248b84e84f6.png)

## Support
If you want to buy me a coffee, feel free — use the [Buy Me A Coffee](https://www.buymeacoffee.com/chrishapunkt) badge at the top of this page. :)

