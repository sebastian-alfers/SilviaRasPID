#!/usr/bin/python

import sys
import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_MAX31855.MAX31855 as MAX31855
from time import sleep

he_pin = 26
GPIO.setmode(GPIO.BCM)
GPIO.setup(he_pin, GPIO.OUT)
args = sys.argv
if(args[1] == "0"):
	print "stop heating"
	GPIO.output(he_pin,0)

if(args[1] == "1"):
        print "start heating"
        GPIO.output(he_pin,1)
        for x in range(0, 30):
		print "heating..."
		sleep(1)

print "cleanup..."
GPIO.cleanup()