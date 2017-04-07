from random import random

import Adafruit_GPIO.SPI as SPI
import Adafruit_MAX31855.MAX31855 as MAX31855

sensor = MAX31855.MAX31855(spi=SPI.SpiDev(0, 0))
def getTemp():
    return sensor.readTempC()