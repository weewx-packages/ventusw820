# Copyright 2026 weewx-packages
# Distributed under the terms of the GNU Public License (GPLv3 or later)
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest
sys.path.insert(0, str(Path(__file__).parents[1]))
import ventus
import ventusw820 as driver


def test_binary_ble_commands_and_real_disconnect():
    peripheral = Mock()
    ventus.sensorData['stale'] = 42
    assert ventus.read(peripheral) == {}
    assert all(isinstance(call.args[1], bytes) for call in peripheral.writeCharacteristic.call_args_list)
    assert peripheral.waitForNotifications.call_count == 3
    ventus.disconnect(peripheral)
    peripheral.disconnect.assert_called_once()


def test_negative_temperature_and_zero():
    raw = bytearray(15)
    raw[0] = 1
    raw[5:7] = (-1).to_bytes(2, 'big', signed=True)
    raw[12:14] = (0).to_bytes(2, 'big', signed=True)
    ventus.w820Delegate('').handleNotification(0, raw)
    assert ventus.sensorData['indoorTemperature'] == -.1
    assert ventus.sensorData['outdoorTemperature'] == 0


def test_truncated_notification():
    with pytest.raises(ValueError, match='Truncated'):
        ventus.w820Delegate('').handleNotification(0, b'\x03')


def test_partial_read_does_not_reuse_old_values():
    assert not driver.Station.validate_data({'indoorTemperature': 0})
    data = dict.fromkeys(('indoorTemperature', 'indoorHumidity', 'outdoorTemperature',
                         'outdoorHumidity', 'airPressure', 'lowBat', 'windSpeed',
                         'windDirection', 'rainTotal'), 0)
    assert driver.Station.validate_data(data)
    packet = driver.Station.data_to_packet(data, 1234, last_rain=0)
    assert packet['outTemp'] == 0
    assert packet['rain'] == 0


def test_ble_failure_disconnects(monkeypatch):
    peripheral = Mock()
    monkeypatch.setattr(ventus, 'connect', Mock(return_value=peripheral))
    monkeypatch.setattr(ventus, 'read', Mock(side_effect=ValueError('bad packet')))
    station = driver.Station('00:00:00:00:00:00')
    assert station.get_readings() == {}
    peripheral.disconnect.assert_called_once()
    assert station.handle is None


def test_user_driver_configuration():
    assert 'driver = user.ventusw820' in driver.confeditor_loader().default_stanza


def test_wind_message_before_temperature_message():
    temperature = bytearray(15)
    temperature[0:2] = (1, 2)    # degF
    wind = bytearray(19)
    wind[0:2] = (3, 1 << 1)      # mph
    wind[11:13] = (100).to_bytes(2, 'big')
    ventus.sensorData.clear()
    delegate = ventus.w820Delegate('')
    delegate.handleNotification(0, temperature)
    delegate.handleNotification(0, wind)
    expected = ventus.sensorData['windSpeed']
    ventus.sensorData.clear()
    delegate = ventus.w820Delegate('')
    delegate.handleNotification(0, wind)
    assert 'windSpeed' not in ventus.sensorData
    delegate.handleNotification(0, temperature)
    assert ventus.sensorData['windSpeed'] == expected
