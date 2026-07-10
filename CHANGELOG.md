# Version 2.0.0

> Updates automatically. Existing setups migrate on update — your mowers'
> entities and history are preserved, so there's nothing to re-add.

## New
- **Multiple mowers per account** are now fully supported. Every mower on your STIHL account shows up as its own device; previously only the first mower was added.
- **Mowers added or removed later are picked up automatically** — a new mower appears on the next update, and a mower that left your account can be deleted from the device page.
- **Re-authentication in the UI**: if your login expires or the password changes, Home Assistant asks you to re-authenticate instead of the integration silently breaking (no more "restart Home Assistant to fix login").
- **Reconfigure**: update your credentials or state-message language from the integration page without removing and re-adding.
- **Diagnostics download** (with credentials and tokens redacted) to make troubleshooting easier.
- **Translations**: config screens and entity names are now available in English, German, French, Dutch, Spanish, Italian, Polish, Czech, Swedish and Norwegian Bokmål.
- A **compatibility hint** on the login screen makes clear this integration only supports STIHL iMow mowers up to **Generation 4** (accounts that work on app.imow.stihl.com; Generation 5 / myimow.stihl.com is not supported).

## Improved
- **Much more stable login.** STIHL session cookies are isolated and tokens are reused across restarts, eliminating the recurring login failures that previously required a Home Assistant restart.
- The integration is now keyed to your STIHL **account id**, so changing your account e-mail address no longer breaks it.
- Entity names and icons now use Home Assistant's translation system, so they follow your selected language and theme.
- The account is polled every 30 seconds.
- **Entities are now organised by category.** Read-only status readouts appear under the device's **Diagnostic** section and the settings toggles under **Configuration**; the main sensors (machine state, charge level, status message) and the mower tracker stay at the top.

## Please note
- **Some entities are now disabled by default** to reduce clutter. They still exist and can be turned on any time via the entity's settings (Settings → Devices & Services → STIHL iMow → the entity → cog → *Enable*). If you're missing one of these after updating, just enable it:
  *Mowing area (feet)*, *Circumference*, *Time zone*, *Last weather check*, *Last GPS position*, *Demo mode*, *Teamable*.
- Existing entities you already use are **not** affected — only the sensors listed above start out disabled for fresh installs and newly discovered mowers.

## Fixed
- Entities no longer disappear intermittently after a restart.
- Mower status/statistics are fetched more reliably (no more upstream timeouts from requesting them too quickly).
- Upgrading from 1.0.x no longer leaves an empty duplicate device behind — your existing mower device is migrated in place, keeping its name, area and automations.


# Version 1.0.3
## BREAKING CHANGES
With this version new entities and device relations are implemented. Coming from a version < 1.0.0 means, that created entities are not longer used or updated by the integration.
I recommend to re-setup the integration by removing and re-installing from the integrations page after updating via HACS.