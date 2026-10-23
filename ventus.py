# Modified 2026-10-22 by weewx-packages.
# Modified 2026-10-23 by weewx-packages: convert wind speed only once the
# temperature unit is known.
import bluepy.btle as btle
import array

# read measurements from Ventus W820 weather station via bluetooth 
# (c) 2015 Christian Herzog <daduke@daduke.org>
# project website: http://daduke.org/coding/ventus.html
#
# we always provide metric units, no matter what mode the W820 is in
# temps: degC
# humidity: %
# pressure: hPa
# rain: mm
# wind speed: km/h
# wind direction: 0: N, 1: NNE ... 15: NNW
#
# reverse enginieered using a BLE sniffer and the Ventus Android app
#
# requires bluepy: https://github.com/IanHarvey/bluepy


sensorData = {}
w820 = 0

class w820Delegate(btle.DefaultDelegate):
    def __init__(self, hndl):
        btle.DefaultDelegate.__init__(self)
        self.hndl=hndl;
        # (raw speed, wind unit) of a type 3 message that arrived before the
        # type 1 message, see setWindSpeed()
        self.pendingWind = None

    def handleNotification(self, cHandle, data):
       #data = data.encode("hex")
       data = array.array('B', data)
       if not data or len(data) < {1: 15, 2: 5, 3: 19}.get(data[0], 1):
           raise ValueError('Truncated W820 notification')
       if data[0] == 1:
               sensorData['degF'] = 0
               sensorData['indoorTemperature'] = int.from_bytes(data[5:7], 'big', signed=True) / 10.0
               sensorData['indoorHumidity'] = data[7]
               sensorData['outdoorTemperature'] = int.from_bytes(data[12:14], 'big', signed=True) / 10.0
               sensorData['outdoorHumidity'] = data[14]
               if (data[1] & 2) != 0:   # degF
                       sensorData['indoorTemperature'] = (sensorData['indoorTemperature'] - 32) / 1.8
                       sensorData['outdoorTemperature'] = (sensorData['outdoorTemperature'] - 32) / 1.8
                       sensorData['degF'] = 1
               if (data[1] & 8) != 0:
                       sensorData['lowBat'] = 1
               else:
                       sensorData['lowBat'] = 0
               if self.pendingWind is not None:
                       self.setWindSpeed(*self.pendingWind)
                       self.pendingWind = None
        

       elif data[0] == 2:
               pressureUnit = ((data[1]) & 6) >> 1
               if pressureUnit > 2:
                       pressureUnit = 2
               sensorData['airPressure'] = ((data[3] * 256) + data[4])
               if pressureUnit == 0:    #Pascalish
                       sensorData['airPressure'] /= 10.0
               elif pressureUnit == 1:  #mm Hg, but wrong
                       sensorData['airPressure'] /= 10.0
               elif pressureUnit == 2:  #inches Hg
                       sensorData['airPressure'] *= 0.338639
       elif data[0] == 3:
               rainUnit = data[1] & 16  #0: mm, 16: inches
               if rainUnit == 16:
                       rainFactor = 0.01 * 25.4
               else:
                       rainFactor = 0.1
               windUnit = (data[1] & 14) >> 1
               if windUnit > 4: #0: km/h, 1: mph, 2: m/s, 3: knots, 4: bft
                       windUnit = 4
               sensorData['UV'] = data[18]
               sensorData['rainDaily'] = ( (data[3] * 256) + data[4] ) * rainFactor
               sensorData['rainWeekly'] = ( (data[5] * 256) + data[6] ) * rainFactor
               sensorData['rainMonthly'] = ( ((data[7] * 65536) + (data[8] * 256)) + data[9] ) * rainFactor
               sensorData['rainTotal'] = ( ((data[15] * 65536) + (data[16] * 256)) + data[17] ) * rainFactor
               sensorData['windChill'] = ((data[13] * 256) + data[14])/10.0
               sensorData['windDirection'] = data[10]
               windSpeed = (data[11] * 256) + data[12]
               if windUnit in (1, 2, 3) and 'degF' not in sensorData:
                       self.pendingWind = (windSpeed, windUnit)
               else:
                       self.setWindSpeed(windSpeed, windUnit)

    def setWindSpeed(self, windSpeed, windUnit):
       # In mph, m/s and knots the W820 scales the speed differently depending
       # on its temperature unit, which only message type 1 carries. Nothing in
       # read() makes type 1 arrive before type 3, so a type 3 message that comes
       # first is held in pendingWind until type 1 has set sensorData['degF'].
       sensorData['windSpeed'] = windSpeed
       if windUnit == 0:
               sensorData['windSpeed'] *= 0.1
       if windUnit == 1:
               sensorData['windSpeed'] = sensorData['windSpeed'] * 0.1 * 1.60934
               if sensorData['degF'] == 0:      # bug in W820: wind speeds not in km/h depend on temperature unit!!!
                       sensorData['windSpeed'] *= 0.01313868613138686131
       elif windUnit == 2:
               sensorData['windSpeed'] = sensorData['windSpeed'] * 0.1 * 3.6
               if sensorData['degF'] == 0:      # bug in W820: wind speeds not in km/h depend on temperature unit!!!
                       sensorData['windSpeed'] *= 0.01157742402315484804
       elif windUnit == 3:
               sensorData['windSpeed'] = sensorData['windSpeed'] * 0.1 * 1.85199539525386
               if sensorData['degF'] == 0:      # bug in W820: wind speeds not in km/h depend on temperature unit!!!
                       sensorData['windSpeed'] *= 0.03782505910165484633
        
def connect(mac):
    return btle.Peripheral(mac, 'random')


def setTime(w820, time):
    w820.writeCharacteristic(0x000b, time, True)


def read(w820):
    sensorData.clear()
    w820.setDelegate(w820Delegate(''))
    w820.writeCharacteristic(0x000e, b'\x01\x00', True)
    for command in (b'\xb0\x01\x00\x00', b'\x40\x01\x00\x00', b'\x40\x01\x00\x00'):
        w820.writeCharacteristic(0x000b, command, True)
        w820.waitForNotifications(1)
    return dict(sensorData)


def disconnect(w820):
    w820.disconnect()
