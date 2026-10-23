# Ventus W820 for WeeWX

Read a Ventus W820 weather station over Bluetooth Low Energy. The driver supplies
indoor/outdoor temperature and humidity, pressure, wind direction/speed, battery
status and rain increments. It does not supply gust measurements.

This is an independent continuation of [daduke/ventusw820](https://github.com/daduke/ventusw820).
Release 0.2.1 uses Python 3 and installs both Bluetooth support and the driver in
WeeWX's user directory. It rejects incomplete readings and closes each connection.

## Install

An existing WeeWX station is required. Replace `/path/to/weewx.conf`
with its configuration file before running the commands.

Use the Python environment and `weectl` belonging to your WeeWX station. The catalog release requires Python >=3.10 and WeeWX >=5.2,<6.

Before running the commands, activate the existing virtual environment that
runs your WeeWX service. Both `python` and `weectl` must come from that
environment. For an OS-packaged WeeWX installation, use compatible distribution
packages instead, or migrate WeeWX and its service to a virtual environment
first. Installing into an unrelated virtual environment will not supply the
running service with dependencies.

Bluepy builds a native helper on Linux. Before installing it, install a C
compiler, `make`, `pkg-config` and GLib development headers. On Debian/Ubuntu,
the packages are `build-essential`, `pkg-config` and `libglib2.0-dev`.
Then install the runtime dependency into the activated WeeWX environment:

```sh
python -m pip install 'bluepy==1.3.0'
```

```sh
weectl extension install https://github.com/weewx-packages/ventusw820/releases/download/v0.2.1/ventusw820-0.2.1.zip --config=/path/to/weewx.conf
weectl station reconfigure --driver=user.ventusw820 --config=/path/to/weewx.conf
```

A downloaded copy of this same archive can be passed instead of the URL.
These commands work with stock WeeWX 5; no package-manager integration is
required.

## Connect the station

Enter your W820 Bluetooth MAC address in `weewx.conf`:

```ini
[Station]
    station_type = W820
[W820]
    driver = user.ventusw820
    mac = AA:BB:CC:DD:EE:FF
    polling_interval = 60
```

Restart your WeeWX service after changing the configuration. The service user
must have access to the Bluetooth adapter. Both `ventus.py` and `ventusw820.py`
are installed under the station's `bin/user`; do not copy them into Python 2
libraries or `weewx.drivers`.

Pairing, notification timing and reception need verification on your W820.
The decoder's offline checks do not establish radio range or Linux adapter support.
See the original [project page](http://daduke.org/coding/ventus.html) for hardware background.

License
-------

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

<!-- Documentation updated 2026-10-23 by weewx-packages. -->
