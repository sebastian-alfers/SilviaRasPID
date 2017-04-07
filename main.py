#!/usr/bin/python

from multiprocessing import Process, Manager
import sys
from time import sleep

def server(i, tempState):
    from bottle import route, run, get, post, request, static_file, abort
    from subprocess import call
    from datetime import datetime
    from bottle import SimpleTemplate
    from bottle import route, run, template
    import os

    basedir = os.path.dirname(__file__)
    wwwdir = basedir + '/www/'

    @route('/')
    def docroot():
        return static_file('index.html', wwwdir)

    @route('/temp')
    def docroot():
        tpl = SimpleTemplate('{{avgtemp}}')
        return tpl.render(avgtemp=tempState["avgTemp"])
        return static_file('index.html', wwwdir)

    @route('/<filepath:path>')
    def servfile(filepath):
        return static_file(filepath, wwwdir)

    run(host='0.0.0.0', port=8080, quiet=True)

def updateTemp(getTemp, tempState):
    i = 0
    temphist = [0., 0., 0., 0., 0.]
    tempState["test"]="ab"
    while True:
        temphist[i%5] = getTemp()
        tempState["avgTemp"]=sum(temphist)/len(temphist)
        sleep(1)
        i = i+1

def heating(i, tempState):
    import RPi.GPIO as GPIO

    heating = False
    lowerLimit = 92
    upperLimit = 94

    he_pin = 26
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(he_pin, GPIO.OUT)
    GPIO.output(he_pin, 0)
    try:
        while True:
            temp = tempState["avgTemp"]
            if heating:
                # as long as temp is above limit
                if(temp > upperLimit):
                    # stop heating
                    heating = False
                    print "stop heating at '%s' !!!!!" % temp
                    GPIO.output(he_pin, 0)
                else:
                    print "still heating at %s" % temp

            else:
                # as long as temp is below limit
                if(temp < lowerLimit):
                    # start heating
                    heating = True
                    print "start heating at '%s' !!!!!" % temp
                    GPIO.output(he_pin, 1)
                else:
                    print "still not heating at %s" % temp
            sleep(1)
    finally:
        GPIO.output(he_pin,0)
        GPIO.cleanup()

if __name__ == '__main__':

    args = sys.argv
    errorMsg ="please pass 'dev' or 'prod' as arg"
    MODE_DEV="dev"
    MODE_PROD="prod"

    if(len(args) != 2):
        print errorMsg
        exit(0)

    arg = args[1]

    if  arg != MODE_DEV and arg != MODE_PROD:
        print errorMsg
        exit(0)

    print "running '%s' mode" % arg

    if arg == MODE_DEV:
        import read_temp_dev
        getTemp=read_temp_dev.getTemp
    else:
        import read_temp_prod
        getTemp=read_temp_prod.getTemp

    print "current tempt: %s" % getTemp()

    manager = Manager()
    tempState = manager.dict()
    tempState["avgTemp"] = 0

    print "try to start daemon updateTemp"
    p = Process(target=updateTemp, args=(getTemp, tempState))
    p.daemon = True
    p.start()

    h = Process(target=heating, args=(1, tempState))
    h.daemon = True
    h.start()

    r = Process(target=server, args=(1, tempState))
    r.daemon = True
    r.start()

    print "started daemon updateTemp"
    print p.is_alive()

    while p.is_alive():
        temp =  tempState["avgTemp"]
        #print temp
        sleep(1)