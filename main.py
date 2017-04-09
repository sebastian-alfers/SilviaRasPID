#!/usr/bin/python

import sys
from multiprocessing import Process, Manager
from time import sleep


def server(i, tempState):
    import json
    from bottle import static_file
    from bottle import route, run
    import os

    basedir = os.path.dirname(__file__)
    wwwdir = basedir + '/www/'

    @route('/')
    def docroot():
        return static_file('index.html', wwwdir)

    @route('/temp')
    def temp():
        return json.dumps(tempState.copy())

    @route('/<filepath:path>')
    def servfile(filepath):
        return static_file(filepath, wwwdir)

    run(host='0.0.0.0', port=8080, quiet=True)


def updateTemp(getTemp, tempState):
    import PID
    sample_time = 0.1

    Pw = 2.9
    Iw = 0.3
    Dw = 40.0
    pid = PID.PID(Pw, Iw, Dw)
    pid.SetPoint = tempState["setTemp"]
    pid.setSampleTime(1)

    i = 0
    temphist = [0., 0., 0., 0., 0.]
    pidHist = [0., 0., 0., 0., 0., 0., 0., 0., 0., 0.]
    while True:
        temphist[i % 5] = getTemp()
        avgTmp = sum(temphist) / len(temphist)

        pid.update(avgTmp)
        pidHist[i % 10] = pid.output
        avgPid = sum(pidHist) / len(pidHist)

        tempState["avgTemp"] = avgTmp
        tempState["avgPid"] = avgPid

        sleep(0.5)
        i = i + 1


def heating(i, tempState):
    import RPi.GPIO as GPIO

    heating = False
    lowerLimit = 92
    upperLimit = 94

    he_pin = 26
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(he_pin, GPIO.OUT)
    GPIO.output(he_pin, 0)
    """
        negative tempState["avgPid"]    >   tempState["avgTemp"] is above setTemp   > do not heat        
        positive tempState["avgPid"]    >   tempState["avgTemp"] is below setTemp   > do heat
    """
    try:
        while True:
            avgTemp = tempState["avgTemp"]
            avgPid = tempState["avgPid"]
            heatTime = 0
            sleepTime = 0
            if (avgPid) < 0:
                # temp is above setTemp > do NOT heat
                sleepTime = abs(avgPid)/10
            elif avgPid > 0:
                # temp is below setTemp > do heat
                heatTime = avgPid / 10

            if (heatTime == 0 and sleepTime == 0):
                sleep(1)

            if(heatTime > 2):
                heatTime = 2
                sleepTime = 4
                print "cut heating from %f to 5 seconds" % heatTime

            if(sleepTime > 5):
                sleepTime = 5
                print "cut sleeping from %f to 5 seconds" % sleepTime

            if(heatTime > 0):
                print "heat: %f, temp: %f, pid: %f" % (heatTime, avgTemp, avgPid)
                GPIO.output(he_pin, 1)
                tempState["isHeating"] = True
                sleep(heatTime)

            if (sleepTime > 0):
                print "sleep: %f, temp: %f, pid: %f" % (sleepTime, avgTemp, avgPid)
                GPIO.output(he_pin, 0)
                tempState["isHeating"] = False
                sleep(sleepTime)

            if (sleepTime == 0 and heatTime == 0):
                sleep(1)
            """
            
            if (avgTemp > tempState["setTemp"] - 1 and avgTemp < tempState["setTemp"] + 1):
                print "temp:'%f', pid: %f " % (avgTemp, avgPid)

            if heating:
                # as long as temp is above limit
                if (avgTemp > upperLimit):
                    # stop heating
                    heating = False
                    tempState["isHeating"] = False
                    print "stop heating at temp:'%f', pid: %f " % (avgTemp, avgPid)
                    GPIO.output(he_pin, 0)
                    # else:
                    # print "still heating at %s" % avgTemp

            else:
                # as long as temp is below limit
                if (avgTemp < lowerLimit):
                    # start heating
                    heating = True
                    tempState["isHeating"] = True
                    print "start heating at temp:'%f', pid: %f " % (avgTemp, avgPid)
                    GPIO.output(he_pin, 1)
                    # else:
                    # print "still not heating at %s" % avgTemp

            sleep(1)
            """

    finally:
        GPIO.output(he_pin, 0)
        GPIO.cleanup()


if __name__ == '__main__':

    args = sys.argv
    errorMsg = "please pass 'dev' or 'prod' as arg"
    MODE_DEV = "dev"
    MODE_PROD = "prod"

    if (len(args) != 2):
        print errorMsg
        exit(0)

    arg = args[1]

    if arg != MODE_DEV and arg != MODE_PROD:
        print errorMsg
        exit(0)

    print "running '%s' mode" % arg

    if arg == MODE_DEV:
        import read_temp_dev

        getTemp = read_temp_dev.getTemp
    else:
        import read_temp_prod

        getTemp = read_temp_prod.getTemp

    print "current tempt: %s" % getTemp()

    manager = Manager()
    tempState = manager.dict()
    tempState["avgTemp"] = 0
    tempState["avgPid"] = 0
    tempState["setTemp"] = 93

    print "try to start daemon updateTemp"
    p = Process(target=updateTemp, args=(getTemp, tempState))
    p.daemon = True
    p.start()

    sleep(10)
    print "start heating after booting temp and pid..."

    r = Process(target=server, args=(1, tempState))
    r.daemon = True
    r.start()


    h = Process(target=heating, args=(1, tempState))
    h.daemon = True
    h.start()


    print "started daemon updateTemp"
    print p.is_alive()

    while p.is_alive():
        temp = tempState["avgTemp"]
        # print temp
        #sleep(1)
