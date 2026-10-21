Ventus W820 bluetooth driver and weewx connector
================================================

The Ventus W820 is a bluetooth enabled weather station. This repository provides a library to read the values of the sensors and a driver for the [weewx](http://www.weewx.com/) weather station software 

The library requires [bluepy](https://github.com/IanHarvey/bluepy) for the BLE communication 

Project website: [http://daduke.org/coding/ventus.html](http://daduke.org/coding/ventus.html)

How to use it:
  * install [bluepy](https://github.com/IanHarvey/bluepy)
  * `ventus.py` is the low level library that talks to the weather station, copy it to a standard python library path (e.g. `/usr/local/lib/python2.7/site-packages/`
  * `ventusw820.py` is the weewx driver, it goes into the weewx driver directory
  * define your Ventus station in the weewx config file:
```
[W820]
    # This section is for the Ventus W820 weather station.

    # MAC address of bluetooth interface
    mac = <your W820 bluetooth MAC address goes here>

    # The driver to use:
    driver = weewx.drivers.ventusw820

    polling_interval = 60
```
  * define your default station as a W820:
```
station_type = W820
```

that's it! Contact me if you have any questions.

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

## Independent continuation

This repository retains daduke/ventusw820's full history and the GPL-3.0-or-later
license stated above. Version 0.2.1 supports Python 3, byte-valued Bluetooth
commands and the WeeWX user driver directory. It rejects incomplete readings,
clears stale notifications and closes the Bluetooth connection after each read.

Install bluepy with `python -m pip install bluepy`. Building bluepy on Debian or
Ubuntu needs a C compiler, pkg-config and GLib development headers. Then install:

```
weectl extension install https://github.com/weewx-packages/ventusw820/archive/refs/tags/v0.2.1.zip
weectl station reconfigure --driver=user.ventusw820 --config=/path/to/weewx.conf
```

Set `mac` and `polling_interval` in `[W820]`. Both `ventus.py` and `ventusw820.py`
belong in the installation's `bin/user` directory. Run `python -m pytest -q tests`
for Bluetooth-command, notification and measurement tests. bluepy 1.3.0 builds
and imports under Python 3.10 and 3.14 in the isolated test environments.
Pairing, radio notification timing and reconnection need verification on a W820.
