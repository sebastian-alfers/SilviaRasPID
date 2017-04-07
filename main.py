#!/usr/bin/python

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

    run(host='0.0.0.0', port=8080)

def updateTemp(getTemp, tempState):
    i = 0
    temphist = [0., 0., 0., 0., 0.]
    tempState["test"]="ab"
    while True:
        temphist[i%5] = getTemp()
        tempState["avgTemp"]=sum(temphist)/len(temphist)
        sleep(1)
        i = i+1

if __name__ == '__main__':

    from multiprocessing import Process, Manager
    import sys
    import read_temp_dev
    import read_temp_prod
    from time import sleep

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
        getTemp=read_temp_dev.getTemp
    else:
        getTemp=read_temp_prod.getTemp

    print "current tempt: %s" % getTemp()

    manager = Manager()
    tempState = manager.dict()
    tempState["avgTemp"] = 0

    print "try to start daemon updateTemp"
    p = Process(target=updateTemp, args=(getTemp, tempState))
    p.daemon = True
    p.start()

    r = Process(target=server, args=(1, tempState))
    r.daemon = True
    r.start()

    print "started daemon updateTemp"
    print p.is_alive()

    while p.is_alive():
        print tempState["avgTemp"]
        sleep(1)
