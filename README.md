# Ventus W820 for WeeWX

A WeeWX driver that reads a Ventus W820 weather station over Bluetooth Low
Energy: indoor and outdoor temperature and humidity, pressure, wind speed and
direction, rain and the battery flag. It supplies no wind gust.

This is an independent continuation of
[daduke/ventusw820](https://github.com/daduke/ventusw820), ported to Python 3
and packaged as a WeeWX extension. The original
[project page](http://daduke.org/coding/ventus.html) has the hardware
background.

## Requirements

- A Ventus W820 and a Bluetooth LE adapter that the user running WeeWX can use.
- [bluepy](https://github.com/IanHarvey/bluepy), installed in the Python
  environment that runs WeeWX. Bluepy builds a native helper on Linux, which
  needs a C compiler, `make`, `pkg-config` and the GLib development headers. On
  Debian and Ubuntu:

  ```sh
  sudo apt install build-essential pkg-config libglib2.0-dev
  python -m pip install 'bluepy==1.3.0'
  ```

  Activate that environment first, so that `python` and `weectl` both come from
  it. For an OS-packaged WeeWX, install a distribution package for bluepy
  instead.

## Installation

Install `ventusw820` from the [WeeWX packages catalog](https://github.com/weewx-packages/catalog/blob/main/packages/ventusw820.md).
The catalog page lists the current release, its WeeWX and Python
requirements, and the install, update and removal commands.

The package installs `ventus.py`, the Bluetooth library, and `ventusw820.py`,
the driver, into the station's `bin/user`. Then select the driver, enter the MAC
address of the W820 when asked, and restart WeeWX:

```sh
weectl station reconfigure --driver=user.ventusw820 --config=/path/to/weewx.conf
```

## Configuration

```ini
[Station]
    station_type = W820

[W820]
    driver = user.ventusw820
    mac = AA:BB:CC:DD:EE:FF
```

| Option | Default | Meaning |
|---|---|---|
| `mac` | none, required | Bluetooth MAC address of the W820. |
| `polling_interval` | `60` | Seconds to wait after each reading. |

The driver opens a new Bluetooth connection for each reading and closes it
afterwards. It drops a reading unless indoor and outdoor temperature and
humidity, pressure, wind speed and direction, the battery flag and the rain
counter are all present.

The driver reports in `METRIC` units:

| W820 value | WeeWX field |
|---|---|
| indoor temperature and humidity | `inTemp`, `inHumidity` |
| outdoor temperature and humidity | `outTemp`, `outHumidity` |
| pressure | `barometer` |
| low battery | `outTempBatteryStatus` |
| wind speed, wind direction | `windSpeed`, `windDir` |
| rain counter | `rainTotal`, from which the driver computes `rain` |

`windDir` is empty while the wind speed is zero.

To check the connection without WeeWX, stop WeeWX and run the driver on its own.
It prints the decoded readings every 60 seconds:

```sh
PYTHONPATH=/path/to/station/bin python -m user.ventusw820 --mac=AA:BB:CC:DD:EE:FF
```

## Limitations

- Not tested on W820 hardware by weewx-packages. Pairing, notification timing
  and reception need checking on your own station.
- The library also decodes UV index, daily, weekly and monthly rain, and wind
  chill. The driver does not pass them to WeeWX.
- The source marks the pressure conversion for a console set to mmHg as wrong.
- The tests decode synthetic notifications. They say nothing about radio range
  or support for a particular Bluetooth adapter.

## Development

Run the tests in a Python environment with WeeWX, bluepy and pytest:

```sh
python -m pytest -q tests
```

## License

> Ventus W820 bluetooth driver and weewx connector
>
> Copyright 2015 Christian Herzog
>
> This program is free software: you can redistribute it and/or modify
> it under the terms of the GNU General Public License as published by
> the Free Software Foundation, either version 3 of the License, or
> (at your option) any later version.
>
> This program is distributed in the hope that it will be useful,
> but WITHOUT ANY WARRANTY; without even the implied warranty of
> MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
> GNU General Public License for more details.

The full text is in [LICENSE](LICENSE). See also [NOTICE](NOTICE).
