# Copyright 2026 weewx-packages
# Distributed under the terms of the GNU Public License (GPLv3 or later)
from weecfg.extension import ExtensionInstaller


def loader():
    return ExtensionInstaller(version='0.2.1', name='ventusw820',
        description='Ventus W820 Bluetooth driver', author='Christian Herzog',
        files=[('bin/user', ['ventus.py', 'ventusw820.py'])])
