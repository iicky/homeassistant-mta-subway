# Home Assistant MTA Subway

[![CI](https://github.com/iicky/homeassistant-mta-subway/actions/workflows/test.yml/badge.svg)](https://github.com/iicky/homeassistant-mta-subway/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/iicky/homeassistant-mta-subway/graph/badge.svg)](https://codecov.io/gh/iicky/homeassistant-mta-subway)
[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

> **Disclaimer:** This is an unofficial, community-maintained integration. It is not affiliated with, endorsed by, or sponsored by the Metropolitan Transportation Authority (MTA). The MTA logo and subway bullet icons are used for identification purposes only.

A Home Assistant integration that surfaces NYC subway service status, alerts, and per-direction conditions as native entities. Pulls a curated rollup status from [subwaynow.app](https://www.subwaynow.app/) and live alerts directly from the MTA's GTFS-Realtime feed.

<p align="center">
  <img src="https://raw.githubusercontent.com/iicky/homeassistant-mta-subway/main/images/Subway%20Group%20Screen%20Shot.png" alt="Example subway card in Home Assistant">
</p>

## Features

- **Per-line service status** — one sensor per subway line (1, 2, 3, …, A, B, C, …, plus shuttles and express variants), state is the human-readable rollup ("Good Service", "Delays", "Service Change", "Planned Work", etc.)
- **Per-direction sensors** — northbound and southbound sensors for each line, exposing direction-specific status as a first-class entity
- **Per-line alert binary sensors** — three categories per line (`planned_work`, `delays`, `service_change`) sourced from the MTA's official alerts feed, with active-period filtering and full alert text in attributes
- **Bundled subway bullet icons** — official-style line bullets served from the integration, no external dependencies
- **Config flow** — set up entirely from the Home Assistant UI, no YAML required
- **Options flow** — add or remove tracked lines after install without reinstalling

## Installation

### HACS (recommended)

1. Open HACS in Home Assistant
2. Go to **Integrations** → **⋮ menu** → **Custom repositories**
3. Add `https://github.com/iicky/homeassistant-mta-subway` as an **Integration**
4. Install **MTA Subway** and restart Home Assistant

> Once this integration is accepted into HACS Default, steps 2–3 will be unnecessary — you'll be able to find it directly in HACS search.

### Manual

Copy the `custom_components/mta_subway` directory into your Home Assistant `config/custom_components/` directory and restart.

## Configuration

After installation:

1. **Settings** → **Devices & Services** → **Add Integration**
2. Search for **MTA Subway**
3. Pick the lines you want to track from the multi-select dropdown
4. Done — entities appear immediately

To change which lines you track, open the integration in **Devices & Services** and click **Configure**.

## Entities

For each tracked line, the integration creates:

| Entity | Type | State |
|---|---|---|
| `sensor.mta_subway_<line>` | Sensor | Overall service status (e.g. `Good Service`) |
| `sensor.mta_subway_<line>_north` | Sensor | Northbound status, or unavailable if not reported |
| `sensor.mta_subway_<line>_south` | Sensor | Southbound status |
| `binary_sensor.mta_subway_<line>_planned_work` | Binary | On if active planned-work alert |
| `binary_sensor.mta_subway_<line>_delays` | Binary | On if active delay alert |
| `binary_sensor.mta_subway_<line>_service_change` | Binary | On if active service-change/reroute/suspension |

Each binary sensor exposes `count`, `titles` (top alert headlines), and `alert_types` as attributes for richer automations.

The line sensor also carries `color`, `scheduled`, `direction_statuses`, `delay_summaries`, `service_irregularity_summaries`, and `service_change_summaries` attributes for backwards compatibility.

<p align="center">
  <img src="https://raw.githubusercontent.com/iicky/homeassistant-mta-subway/main/images/Sensor%20States%20Screen%20Shot.png" alt="Example sensor state and attributes in Home Assistant">
</p>

## Upgrading from an older version

If you previously configured the integration via `configuration.yaml`, your config will auto-import to a config entry on first startup after upgrading. You can then remove the `platform: mta_subway` block from `configuration.yaml`. Existing entity IDs and history are preserved.

## Data sources

- **[subwaynow.app](https://www.subwaynow.app/)** — provides the curated "Good Service" / "Delays" / "Planned Work" rollup status. Polled every 60 seconds.
- **[MTA GTFS-Realtime alerts](https://api.mta.info/)** — provides the raw alerts that drive the binary sensors. Polled every 60 seconds. No API key required.

## Credits

Subway line bullet icons originally from [louh's NYC Subway Icons repo](https://github.com/louh/nyc-subway-icons), with minor renaming.
