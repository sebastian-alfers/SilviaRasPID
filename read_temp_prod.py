
from math import isnan

import Adafruit_GPIO.SPI as SPI
import Adafruit_MAX31855.MAX31855 as MAX31855

sensor = MAX31855.MAX31855(spi=SPI.SpiDev(0, 0))
prevTemp = 0
def getTemp():
    temp = sensor.readTempC()
    if not isnan(temp):
        prevTemp = temp

    return prevTemp
