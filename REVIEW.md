# Review & Update Plan — `ha-stihl-imow`

Home Assistant custom integration (domain `stihl_imow`) that surfaces STIHL iMOW
mowers via the sibling `imow-webapi` wrapper. This document captures a
best-practices review against the current HA developer docs, prioritized so that
the "restart HA to fix login" workaround is eliminated.

> Cross-reference: the auth/cookie root cause lives in the wrapper — see
> `../stihl-imow-webapi/REVIEW.md`. Items 1–3 below combined with the wrapper's
> cookie-isolation fix are what actually stop the restart cycle.

Sources: HA developer docs — config entries, fetching data / `DataUpdateCoordinator`,
config flow (reauth, unique IDs), entity naming, integration quality scale.

---

## Open follow-ups (next session)

Three loose ends to work on step by step.

### T1. Entity name translations not applied in the UI — ✅ FIXED
- **Confirmed fixed:** setting the **backend/system language** (Settings → System →
  General → Language) and re-creating the entities produced the translated names
  (e.g. "Ladestand"). No code change needed.
- **Resolution: not a code bug — expected HA behavior.** The code is correct
  (`_attr_has_entity_name = True`, `_attr_translation_key` set, no `_attr_name`
  override on sensors, keys present in `strings.json` + all `translations/*.json`,
  hassfest passes).
- **Root cause (HA docs, core/entity → Entity naming):** a translated entity name
  is resolved from the **system (backend) language at entity creation time**, not
  the per-user UI language. Changing the backend language only affects entities
  created *after* the change; existing entities keep their baked-in name.
- **To get German names:**
  1. Settings → System → General → **Language** = Deutsch (the *backend* language,
     not the top-right per-user UI language).
  2. Restart Home Assistant.
  3. **Re-create the entities** — remove and re-add the config entry (or delete the
     mower device). A restart alone will not re-translate existing entities.
- **Note:** in this workspace the integration is symlinked into the running core
  dev instance, so the translation files are already live — no reinstall needed;
  only the backend-language + entity re-creation steps apply.

### T2. Default-disabled entities are not disabled — ✅ FIXED
- **Confirmed fixed:** after purging the stale/orphaned `stihl_imow` registry
  entries and re-adding the integration, the 7 off-by-default entities are created
  with `disabled_by: integration`. No code change needed.
- **Symptom (was):** the 7 entities marked off-by-default still appeared enabled.
- **Root cause:** `entity_registry_enabled_default` only applies the **first time**
  an entity is added to the registry. On the dev instance the `circumference`
  registry entry has `created_at: 2026-07-09` and the same `config_entry_id` as the
  current entry (`01KX5BYPB6…`) — i.e. the config entry was never actually deleted
  (a real delete + re-add yields a new ULID `entry_id` + new `created_at`). So the
  stale entries were reused and the flag never re-applied.
- **Fix / how to verify:** genuinely re-create the entities.
  - UI: Settings → Devices & Services → STIHL iMow → ⋮ → Delete, **confirm the
    device/entities are gone**, then re-add → the 7 come back `disabled_by:
    integration`.
  - Dev shortcut: stop HA, strip `platform: stihl_imow` entries (or the mower
    device) from `config/.storage/core.entity_registry`, start HA.
- **Note:** for end users upgrading in place (not re-adding) the 7 stay enabled;
  fresh adds / newly discovered mowers get them disabled. This is documented HA
  behavior — a forced-disable migration is discouraged (can't tell user-enabled
  from default-enabled).

### T3. Timestamp sensors show a raw ISO string — ✅ FIXED
- **Entities:** `status_last_seen_date`, `status_last_geo_position_date`,
  `last_weather_check`. They were plain string sensors (no `device_class`), so the
  UI showed the raw upstream value (e.g. `2026-07-09T13:50:51+00:00`).
- **Fix applied:** set `ATTR_TYPE: SensorDeviceClass.TIMESTAMP` for the 3
  properties in `IMOW_SENSORS_MAP`, and parse the upstream ISO string into an
  aware UTC `datetime` in `sensor._parse_timestamp` (called from
  `ImowSensorEntity.native_value` only when the device class is TIMESTAMP, so
  binary_sensor/switch are unaffected). Empty/unparseable values → `None`.
- **Tests:** `test_timestamp_sensor_parses_value` asserts the TIMESTAMP class,
  a parsed aware datetime, and `None` for empty/`None`/bad input.

---

## Highest-impact issues (these also worsen the auth bug)

### A. Setup forces a full re-login on every start/reload — HIGH
- **Where:** `async_setup_entry` calls `await imow_api.get_token(force_reauth=True)`
  unconditionally, ignoring the persisted `CONF_API_TOKEN` / `CONF_API_TOKEN_EXPIRE_TIME`.
- **Impact:** every HA restart/reload does a fresh scraped login — the exact path
  that trips the cookie/SPA-shell failure.
- **Fix:** construct `IMowApi(token=stored_token, ...)` and only authenticate if the
  token is missing/expired. Reserve `force_reauth=True` for the reauth flow.

### B. Platforms are set up in a detached task (race condition) — HIGH
- **Where:** `hass.async_create_task(hass.config_entries.async_forward_entry_setups(entry, PLATFORMS))`.
- **Impact:** `async_setup_entry` can return before platforms exist → intermittent
  "entities missing after restart" and ordering bugs.
- **Fix:** `await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)`.

### C. No reauth flow despite raising `ConfigEntryAuthFailed` — HIGH (Silver blocker)
- **Where:** `__init__.py` and the coordinator raise `ConfigEntryAuthFailed`
  (which starts a `SOURCE_REAUTH` flow), but `config_flow.py` has **no**
  `async_step_reauth` / `async_step_reauth_confirm`.
- **Impact:** on any auth failure the integration breaks with no UI recovery — the
  reason a manual HA restart is currently needed.
- **Fix:** add `async_step_reauth` + `async_step_reauth_confirm`; re-validate
  credentials, verify the same account with
  `_abort_if_unique_id_mismatch(reason="wrong_account")`, then
  `async_update_reload_and_abort(self._get_reauth_entry(), data_updates=...)`.

### O. Inject a cookie-isolated session into the wrapper — HIGH (fixes the cookie bug, HA side)
- **Where:** `async_setup_entry` and `validate_input` pass
  `async_get_clientsession(hass)` (HA's **shared** session + cookie jar) into
  `IMowApi`.
- **Impact:** STIHL auth cookies leak into HA's global jar; a later `force_reauth`
  lands on the logged-in SPA shell → the wrapper's `NoneType` crash. This is the
  HA-side half of the wrapper's finding #1.
- **Fix:** build the client with a dedicated, cookie-isolated session:
  ```python
  from homeassistant.helpers.aiohttp_client import async_create_clientsession
  imow = IMowApi(aiohttp_session=async_create_clientsession(hass), ...)
  ```
  `async_create_clientsession` is HA's recommended helper for cookie-based clients
  (it gives each client its own cookie jar) and is the aligned counterpart to the
  wrapper keeping its injected-session contract. See
  `../stihl-imow-webapi/REVIEW.md` → "How this library fits the HA integration".

---

## Config-entry / data model

### D. Use `entry.runtime_data` instead of `hass.data[DOMAIN][entry_id]` — MEDIUM
- Current standard: a typed entry + `runtime_data`.
  ```python
  type ImowConfigEntry = ConfigEntry[ImowCoordinator]
  # in async_setup_entry:
  entry.runtime_data = coordinator
  ```
- Replaces the `hass.data.setdefault(DOMAIN, {})` bookkeeping and the manual `pop`
  in `async_unload_entry`.

### E. Don't store volatile mower state in the config entry — MEDIUM
- **Where:** `validate_input` writes the entire mower `__dict__` into
  `CONF_MOWER_STATE`.
- **Impact:** config entries should hold small, stable config; this bloats
  `.storage` and goes stale.
- **Fix:** persist only `email`, `token`, `token_expire`, `mower_id`, `language`,
  `polling_interval`. Fetch state at runtime via the coordinator.

### F. No `unique_id` on the config entry — MEDIUM
- **Where:** `config_flow.py` never calls `async_set_unique_id` /
  `_abort_if_unique_id_configured`.
- **Impact:** duplicate entries possible; reauth can't match the right entry.
- **Fix:** for a cloud service, use the mower id or the lowercased account email:
  `await self.async_set_unique_id(...)` then `self._abort_if_unique_id_configured()`.

### G. Fragile schema access needs a migration — LOW
- **Where:** `async_setup_entry` works around `email`/`username` key drift inline.
- **Fix:** formalize with `async_migrate_entry` + `VERSION` / `MINOR_VERSION` and
  normalize the stored data once.

---

## Coordinator

### H. Typed coordinator subclass + pass `config_entry` — MEDIUM
- **Where:** inline `update_method=` form without a subclass and without
  `config_entry`.
- **Fix:** subclass `DataUpdateCoordinator[MowerState]`, put logic in
  `_async_update_data`, and pass `config_entry=entry` to `super().__init__()`
  (newer HA warns/requires it). Consider `always_update=False` if `MowerState`
  implements `__eq__`.

### I. Replace `async_timeout` with `asyncio.timeout` — LOW
- **Where:** `_async_update_data` uses `async_timeout.timeout(...)` (deprecated for
  Python 3.11+).
- **Fix:** `async with asyncio.timeout(...)`; drop the `import async_timeout`.

### J. Move the `asyncio.sleep(1)` throttle into the wrapper — LOW
- The upstream-pacing `sleep` between the state and statistics calls should live in
  `imow-webapi`, keeping the coordinator declarative.

### P. Polling interval must NOT be user-configurable — MEDIUM (HA rule)
- **Where:** `STEP_ADVANCED` in `config_flow.py` offers
  `CONF_ATTR_POLLING_INTERVALL` = `vol.In([20, 30, 60, 120, 300])`, stored in the
  config entry and used as `update_interval`.
- **Impact:** HA guidance is explicit — never expose `scan_interval` /
  `update_interval` / polling frequency in the config flow; the integration decides
  the interval. Also, the **cloud-service minimum is 60s**, so `20`/`30` violate
  the floor.
- **Fix:** remove the polling-interval option; set `update_interval`
  programmatically (e.g. a fixed `>= 60s` constant). If migrating, drop the stored
  value in `async_migrate_entry`.

### Q. Declare `PARALLEL_UPDATES` in each platform — LOW (HA rule)
- **Where:** platform files (`sensor.py`, `binary_sensor.py`, `switch.py`,
  `device_tracker.py`).
- **Fix:** add `PARALLEL_UPDATES = 0` for the coordinator-based read platforms
  (data comes from the coordinator, not per-entity polling); use `1` for the
  command platform (`switch`) if serializing writes to the cloud is desired.

### R. Don't let users set the config entry name — LOW (HA rule)
- **Where:** `async_create_entry(title=CONF_ENTRY_TITLE, ...)` uses a static title.
- **Fix:** name the entry automatically from a stable source (e.g. the mower name
  or account), not a hard-coded/user-facing name. Users can rename later in the UI.

---

## Services

### K. Register services once, not per entry — LOW
- **Where:** `async_setup_services(hass, entry)` runs on every entry setup.
- **Fix:** register global services a single time (in `async_setup` or guarded on
  first entry); unregister/clean up when the last entry unloads. `async_unload_entry`
  should also clean up.

---

## Manifest

### L. Modernize `manifest.json` — LOW
- Add `"integration_type": "hub"` (or `"device"`).
- Add `"loggers": ["imow"]`.
- Drop empty `"homekit": {}`, `"ssdp": []`, `"zeroconf": []` (only keep discovery
  keys actually used).
- Optionally add `quality_scale.yaml` + `"quality_scale"` once targeting a tier.
- Keep bumping `"version"` and the `imow-webapi==x.y.z` pin together.

---

## Entities

### M. `has_entity_name` + translated names — MEDIUM
- New integrations must set `_attr_has_entity_name = True` and use translated entity
  names (`translation_key` + the `entity` section of `strings.json`) rather than
  hard-coded English. Verify `entity.py` sets this; prefer icon translations
  (`icons.json`) over the discouraged `icon` property where practical.

### N. Add a diagnostics platform — MEDIUM (Gold tier, high value)
- A `diagnostics.py` that dumps the coordinator's `MowerState` with
  credentials/token **redacted** makes future auth issues self-service to debug via
  the UI download button.

---

## Multiple mowers per account

### S. Support more than one mower on a STIHL account — MEDIUM
- **Where:** `config_flow.validate_input` and `__init__.async_setup_entry` only
  ever use `mowers[0]`; the config entry, coordinator, and device are all built
  around a single mower id. A STIHL account with two or more mowers exposes only
  the first; the rest are silently dropped (see the wrapper `receive_mowers()`
  returning a list).
- **Impact:** users with multiple mowers can't see all of them; the single
  `unique_id = mower_id` also means a second account-level entry can't be added
  cleanly.
- **Options (pick one):**
  1. **One config entry per mower.** The `user` step lists the account's mowers
     and either creates an entry per selected mower or auto-creates one entry per
     mower. `unique_id = mower_id` per entry (already the case). Simple, but each
     entry re-authenticates/holds its own session and token.
  2. **One config entry per account + config subentries per mower.** The entry
     stores the account credentials/token; each mower is a subentry with its own
     coordinator and device. Matches HA's "hub with sub-devices" model and shares
     one authenticated session/token across mowers. `unique_id` = account
     (lowercased email); subentry `unique_id` = mower id.
  3. **One config entry per account, multiple devices.** Single coordinator
     fetches all mowers (`receive_mowers()`), entities are created per mower and
     registered to per-mower devices via `DeviceInfo`. One session/token, one poll
     cycle. Simplest data flow; no subentry UI.
- **Recommendation:** option 3 (single account entry, one coordinator returning a
  list keyed by mower id, entities/devices per mower). It shares auth, keeps a
  single poll, and avoids duplicate logins — which best fits the
  cookie-isolation/token-reuse design. Requires: coordinator returns
  `dict[mower_id, MowerState]`; entities take a `mower_id`; `unique_id` becomes
  `{account}_{mower_id}_{property}`; `unique_id` of the entry becomes the account.
  This is a **breaking** data-model change (entry `unique_id` + entity ids), so it
  pairs naturally with the 2.0.0 major bump and the entity-naming change (M).
- **Interaction with M:** best sequenced **with or right after M**, since both
  touch `entity.py`/platform entity construction and `unique_id`.

---

## Quality-scale snapshot

| Tier | Status | Blockers |
|------|--------|----------|
| 🥉 Bronze | Mostly met | B (await forwards), P (no user-set polling), R (no user-set name) |
| 🥈 Silver | Not met | C (no reauth), O (cookie-isolated session), robust error/backoff (see wrapper review) |
| 🥇 Gold | Not met | N (diagnostics), reconfigure/options, translated entities (M) |
| 🏆 Platinum | Not met | async deps (met via `imow-webapi`), websession injection (O), strict typing |

---

## How the library and integration fit together

The wrapper (`imow-webapi`) and this integration must agree on session/cookie
ownership. HA's own guidance settles it:

- **Integration injects the session** (websession injection, Platinum). For a
  cookie-based client, inject `async_create_clientsession(hass)` — a session with
  its **own cookie jar** — not the shared `async_get_clientsession(hass)`
  (finding O).
- **Wrapper keeps the injected-session contract**, never closes a session it
  doesn't own, and defensively clears STIHL cookies before each fresh auth
  (`../stihl-imow-webapi/REVIEW.md` findings #1, #2, #10).
- **Token lifecycle:** the integration persists `token` + `token_expire` and
  passes the token back on setup (finding A); the wrapper honors an injected token
  and only re-authenticates when missing/expired or on a 401 (wrapper findings #4,
  #5). Auth failures surface as `ConfigEntryAuthFailed` → reauth flow (finding C).

With those contracts in place the "restart HA to fix login" cycle disappears: the
cookie jar is scoped per client, logins are rare and single-flight, and any auth
failure self-heals through the reauth flow instead of a restart.

---

## Suggested order of work

1. **B + A + O** — await forwards; reuse the stored token; inject a cookie-isolated
   session. Immediate stability; removes the cookie-leak class of failure.
2. **C + F** — reauth flow + `unique_id`. Recovery without HA restarts.
3. **D + E + G + P + R** — `runtime_data`, slim entry data, migration, drop
   user-set polling/name. Clean, rule-compliant data model.
4. **H + I + J + Q** — typed coordinator, `asyncio.timeout`, move throttle to
   wrapper, `PARALLEL_UPDATES`.
5. **K + L + M + N** — services, manifest, entity naming, diagnostics.

Items 1–2, combined with the wrapper's cookie-isolation fix, are what stop the
"restart HA to fix login" cycle.

---

## Validation

- Manual install: copy `custom_components/stihl_imow/` into a HA config's
  `custom_components/`, restart HA, add the integration via the UI.
- CI: `hassfest` / HACS validation runs on push/PR.
- After bumping the wrapper, update the `manifest.json` requirement pin to match.

---

## Open questions

- Unique ID source: mower id or lowercased account email? (Email is simplest for a
  single-account cloud service; mower id ties the entry to one mower.)
- Should the config entry hold one mower per entry (current shape) or support
  multiple mowers per account (subentries)?
- Target quality tier for this pass (Bronze polish vs. push to Silver with reauth)?
- Fixed polling interval to standardize on now that it's no longer user-set
  (finding P) — e.g. 60s or 120s?
