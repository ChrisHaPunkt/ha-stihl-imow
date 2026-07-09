# AGENTS.md — ha-stihl-imow

Home Assistant custom integration (`custom_components/stihl_imow/`, domain `stihl_imow`) that surfaces STIHL iMOW mowers. It is a thin HA adapter over the `imow-webapi` PyPI package (developed in the sibling `stihl-imow-webapi` folder). Distributed via HACS; `iot_class` is `cloud_polling`.

## Architecture
- `__init__.py` — `async_setup_entry` builds an `IMowApi` from the config entry, then creates a single `DataUpdateCoordinator`. Its `_async_update_data` calls `imow_api.receive_mower_by_id(mower_id)` and stashes `mower_state.statistics` on the returned `MowerState`. The coordinator lives in `hass.data[DOMAIN][entry_id]["coordinator"]`. `LoginError` → `ConfigEntryAuthFailed` (triggers reauth flow); `ApiMaintenanceError` → `UpdateFailed`.
- Platforms are fixed: `PLATFORMS = ["sensor", "binary_sensor", "switch", "device_tracker"]`. Entities are generated dynamically from the `MowerState` fields, not hand-declared.
- `entity.py` — `ImowBaseEntity(CoordinatorEntity)` is the shared base. `get_value_from_mowerstate()` treats a property name containing `_` as a "complex" nested lookup (`status_mainState` → `mowerstate.status["mainState"]`); otherwise a flat attribute. All display metadata (icon, unit, device_class, is-switch, has-picture) comes from `IMOW_SENSORS_MAP`.
- `maps.py` — `IMOW_SENSORS_MAP` is the source of truth mapping each mower property to `{ATTR_TYPE, ATTR_UOM, ATTR_ICON, ATTR_SWITCH, ATTR_PICTURE}`. `ENTITY_STRIP_OUT_PROPERTIES` lists fields to hide. **To add/adjust an entity, edit this map — do not add per-entity classes.**
- `__init__.py:extract_properties_by_type()` splits mower properties by Python type so `sensor.py` gets non-bool fields and `binary_sensor.py`/`switch.py` get bools (`ATTR_SWITCH` decides switch vs binary_sensor).
- `services.py` — registers the `stihl_imow.intent` service (schema in `IMOW_INTENT_SCHEMA`, UI in `services.yaml`). It resolves a mower from `mower_device` (via device registry) or `mower_name`, then calls `imow_api.intent(...)` with `IMowActions`.

## Conventions
- All constants/`ATTR_*`/`CONF_*` keys live in `const.py`; import from there rather than using string literals. `DOMAIN = "stihl_imow"`, `LOGGER = logging.getLogger(__package__)`.
- Follow HA integration norms: async coroutines, `_LOGGER` per module, config via UI config flow (`config_flow.py`) — there is no YAML config. User-facing strings go in `strings.json` + `translations/en.json`.
- Device identity: `unique_id` = `{device_id}_{idx}_{property_name}`; device registration uses `(DOMAIN, mower_id)` identifiers (see `ImowBaseEntity.device_info`).
- The pinned upstream dependency is in `manifest.json` (`"imow-webapi==0.8.4"`). Keep it in sync when the sibling wrapper changes; bump `version` in `manifest.json` for releases.

## Workflows
- Manual install for testing: copy `custom_components/stihl_imow/` into a HA config's `custom_components/`, restart HA, add the integration via UI.
- No local unit-test suite here; validation is via GitHub Actions (`hassfest`/HACS validation on push/PR). Test behavioral changes against a running HA instance.
- When touching data flow, remember entities read only from `coordinator.data` (a `MowerState`); new upstream fields must exist on that object and be registered in `IMOW_SENSORS_MAP`.

## Gotchas
- Entity availability depends on fields STIHL returns; a missing property means the entity silently won't appear. Cross-check `IMOW_SENSORS_MAP` keys against actual `MowerState` attributes.
- `_async_update_data` sleeps 1s between the state and statistics calls to avoid upstream timeouts — keep such throttling when editing polling logic.
