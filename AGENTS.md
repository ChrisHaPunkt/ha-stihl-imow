# AGENTS.md — ha-stihl-imow

Home Assistant custom integration (`custom_components/stihl_imow/`, domain `stihl_imow`) that surfaces STIHL iMOW mowers. It is a thin HA adapter over the `imow-webapi` PyPI package (developed in the sibling `stihl-imow-webapi` folder). Distributed via HACS; `iot_class` is `cloud_polling`.

## Architecture
- `__init__.py` — `async_setup` registers the integration services once. `async_setup_entry` builds an `IMowApi` on a cookie-isolated session (`async_create_clientsession`), reuses the stored token (only re-authenticating when it is missing/expired or on a 401), creates an `ImowDataUpdateCoordinator`, runs the first refresh, persists any rotated token, reconciles the entry `unique_id` to the STIHL **account id**, migrates legacy entity unique ids, then `await`s `async_forward_entry_setups`. `LoginError` → `ConfigEntryAuthFailed` (triggers the reauth flow); `ApiMaintenanceError` → `ConfigEntryNotReady` / `UpdateFailed`. The coordinator is stored on `entry.runtime_data` (typed `ImowConfigEntry`), **not** `hass.data`.
- `coordinator.py` — `ImowDataUpdateCoordinator(DataUpdateCoordinator[dict[str, MowerState]])`. `_async_update_data` calls `receive_mowers()` then, per mower, `receive_mower_state_with_statistics(mower.id)`, returning `dict[mower_id, MowerState]`. **Multiple mowers per account are supported**; entities and devices are created per mower.
- Platforms are fixed: `PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.SWITCH, Platform.DEVICE_TRACKER]`. Entities are generated dynamically from the `MowerState` fields, not hand-declared. Each platform declares `PARALLEL_UPDATES` (`0` for reads, `1` for the `switch` command platform).
- `entity.py` — `ImowBaseEntity(CoordinatorEntity[ImowDataUpdateCoordinator])` is the shared base, keyed by `mower_id`. It sets `_attr_has_entity_name`, `_attr_translation_key`, `_attr_unique_id = f"{mower_id}_{property}"`, an entity category (none for `PRIMARY_PROPERTIES`, `CONFIG` for switches, else `DIAGNOSTIC`), and `_attr_entity_registry_enabled_default` from `DISABLED_BY_DEFAULT_PROPERTIES`. `get_value_from_mowerstate()` reads `coordinator.data[mower_id]`, treating a property name containing `_` as a nested lookup (`status_mainState` → `status["mainState"]`).
- `maps.py` — `IMOW_SENSORS_MAP` is the source of truth mapping each property to `{ATTR_TYPE, ATTR_UOM, ATTR_SUGGESTED_UOM?, ATTR_STATE_CLASS?, ATTR_ICON, ATTR_SWITCH, ATTR_PICTURE}`. Also `ENTITY_STRIP_OUT_PROPERTIES` (never exposed), `PRIMARY_PROPERTIES` (no diagnostic category), and `DISABLED_BY_DEFAULT_PROPERTIES` (created but off by default). **To add/adjust an entity, edit this map AND add a name under the matching platform in `strings.json` (+ `translations/en.json`) — do not add per-entity classes.**
- `__init__.py:extract_properties_by_type()` splits mower properties by Python type so `sensor.py` gets non-bool fields and `binary_sensor.py`/`switch.py` get bools (`ATTR_SWITCH` decides switch vs binary_sensor).
- `services.py` — registers the `stihl_imow.intent` service once (schema `IMOW_INTENT_SCHEMA`, UI in `services.yaml`). It resolves a mower from `mower_device` (device registry) or `mower_name`, then calls `imow_api.intent(...)` with `IMowActions`.
- `diagnostics.py` — dumps the coordinator's per-mower state with credentials/token redacted. `icons.json` provides entity icon translations. `quality_scale.yaml` tracks the Platinum rules.

## Conventions
- All constants/`ATTR_*`/`CONF_*` keys live in `const.py`; import from there rather than using string literals. `DOMAIN = "stihl_imow"`.
- Follow HA integration norms: async coroutines, `_LOGGER = logging.getLogger(__name__)` per module, config via UI config flow (`config_flow.py`, with `reauth` and `reconfigure` steps) — there is no YAML config. User-facing strings go in `strings.json` + all `translations/*.json` (10 languages).
- Device identity: entity `unique_id` = `{mower_id}_{property}` (`{mower_id}_tracker` for the tracker); the config entry `unique_id` is the STIHL **account id** (from `receive_account()`), not the e-mail (which can change). Device registration uses `(DOMAIN, mower_id)` identifiers.
- Legacy entity unique ids (`{mower_id}_{idx}_{property}`) are migrated **in place** by `_migrate_entity_unique_ids` (`er.async_migrate_entries`), so entities/history are preserved across the 2.x upgrade.
- The pinned upstream dependency is in `manifest.json` (`"imow-webapi==0.11.0"`). Keep it in sync when the sibling wrapper changes; bump `version` in `manifest.json` for releases. `quality_scale` is `platinum`.

## Workflows
- Tests live in `tests/` (pytest + `pytest-homeassistant-custom-component`). Run in the test venv: `source .venv-test/bin/activate && python -m pytest tests/ -q` (~32 tests, ~94% coverage).
- Type-check with `mypy custom_components/stihl_imow` (strict, config in `mypy.ini`). Lint with `flake8 .` (CI enforces the default max line length of 79) and `black -l 78 .`.
- `hassfest` runs via the HA core checkout: `python -m script.hassfest --integration-path <path>`.
- CI (GitHub Actions, `.github/workflows/pushpull.yaml`): Tests, hassfest Validate, HACS Action, and style (black + flake8). Uses `actions/checkout@v5`.
- Manual install for testing: copy `custom_components/stihl_imow/` into a HA config's `custom_components/`, restart HA, add the integration via UI.

## Gotchas
- `coordinator.data` is a `dict[mower_id, MowerState]`; entities read only from it. A new upstream field must exist on `MowerState`, be registered in `IMOW_SENSORS_MAP`, **and** have a translation in `strings.json` or the entity shows up unnamed.
- Entity availability depends on fields STIHL returns; a missing property means the entity silently won't appear. Cross-check `IMOW_SENSORS_MAP` keys against actual `MowerState` attributes.
- The 1s throttle between the state and statistics calls now lives in the **wrapper** (`imow-webapi`), not the coordinator — do not re-add a `sleep` in `_async_update_data`.
- `entity_registry_enabled_default` only applies the first time an entity is created; re-adding the integration will not retroactively disable already-existing entities.
- Timestamp sensors (`last seen`, `last GPS position`, `last weather check`) use `SensorDeviceClass.TIMESTAMP` and must return an aware `datetime` (parsed in `sensor._parse_timestamp`), never a raw ISO string.
