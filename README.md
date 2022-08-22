# Home Assistant MTA Subway Service Status Sensor

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

## Overview

A sensor to provide MTA Subway service statuses for Home Assistant. The sensor reads from the [goodservice.io](goodservice.io) API and provides both the overall line status as a sensor state as well as status descriptions and route directions as sensor attributes. The train line states are updated every minute from the detailed [goodservice.io](https://www.goodservice.io/api/routes?detailed=1) route endpoint.

Credit for the line icons goes to [louh](https://github.com/louh) and his great [NYC Subway Icons repo](https://github.com/louh/nyc-subway-icons) (used with some slight renaming).

### Sensor States
- Good Service
- Planned Work
- Slow
- Not Good
- Delays
- Service Change

<p align="center">
  <img src="https://raw.githubusercontent.com/iicky/homeassistant-mta-subway/master/images/Subway%20Group%20Screen%20Shot.png" alt="Example subway card in Home Assistant">
</p>

### Sensor Attributes

**Color**<br>
Indicates the color of the subway line.

**Scheduled**<br>
Indicates whether the route is scheduled or not.

**Direction statuses**<br>
Indicates the route status for both route directions.

**Delay summaries**<br>
A full description of route delays for both directions.

**Service irregularity summaries**<br>
A full description of any service irregularity summaries currently occuring on the line for both route directions.

**Service change summaries**<br>
A full description of any planned work currently for both directions individually and combined.

<br>
<p align="center">
  <img src="https://raw.githubusercontent.com/iicky/homeassistant-mta-subway/master/images/Sensor%20States%20Screen%20Shot.png" alt="Example sensor state and attributes in Home Assistant">
</p>

## Installation

To install the sensor, copy the `mta_subway` folder under `custom_components` to a directory called `custom_components` in your Home Assistant configuration directory.

To use, add the following configuration to your `configuration.yaml` file for Home Assistant, removing any lines that you do not want to monitor:

```
sensor:
  - platform: mta_subway
    line:
      - '1'
      - '2'
      - '3'
      - '4'
      - '5'
      - '6'
      - '6X'
      - '7'
      - '7X'
      - 'A'
      - 'B'
      - 'C'
      - 'D'
      - 'E'
      - 'F'
      - 'FX'
      - 'G'
      - 'J'
      - 'L'
      - 'M'
      - 'N'
      - 'Q'
      - 'R'
      - 'GS'
      - 'FS'
      - 'H'
      - 'SI'
      - 'W'
      - 'Z'
```
