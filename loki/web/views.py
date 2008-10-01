from django.shortcuts import render_to_response
from django.http import HttpResponse
from loki import Session 
from loki.ModelTasks import listitems
from loki.ModelTasks import getbot
from loki.RemoteTasks import status
from django.utils import simplejson
from loki.Common import *
import types

Session = Session()
Session = Session.getSession()

def serialize_sqlalchemy(obj):
    serialized = {}
    for item in obj.__dict__.iteritems():
        try:
            x = simplejson.dumps(item[1])
            serialized[item[0]] = item[1]
        except Exception, x:
            pass
            #if hasattr(item[1], "__dict__"):
            #    serialize_sqlalchemy(item[1])
    serialized = simplejson.dumps(serialized)
    return serialized

def home(request):
    masters = listitems(MASTER, Session)
    slaves = listitems(SLAVE, Session)
    return render_to_response('home.html', locals())

def bot_status(request, botname):
    if status(getbot(botname, Session)):
        botstatus = 'on'
        stsclr = 'green'
    else:
        botstatus = 'off'
        stsclr = 'red'
    data = { 'botname' : botname, 'botstatus' : botstatus, 'stsclr' : stsclr }
    results = simplejson.dumps(data)
    return HttpResponse(results, mimetype='application/json;')

def bot_report(request, botname):
    bot = getbot(botname, Session)
    results = serialize_sqlalchemy(bot)
    return HttpResponse(results, mimetype='test;')
