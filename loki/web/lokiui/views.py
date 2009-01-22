# Copyright 2008, Red Hat, Inc
# Dan Radez <dradez@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Global views.
"""

import types

from django.shortcuts import render_to_response
from django.http import HttpResponse
from loki import Orm
from loki.bot import get as bot_get
from loki.server import get as server_get
from loki.remote.bot import getbot, status
from django.utils import simplejson
from loki.Common import *


Session = Orm().session


def serialize_sqlalchemy(obj):
    """
    TODO: Document me.
    """
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
    """
    TODO: Document me.
    """
    masters = bot_get(MASTER)
    slaves = bot_get(SLAVE)
    return render_to_response('home.html', locals())


def bot_status(request, botname):
    """
    TODO: Document me.
    """
    if status(getbot(botname)):
        botstatus = 'on'
        stsclr = 'green'
    else:
        botstatus = 'off'
        stsclr = 'red'
    data = {'botname': botname, 'botstatus': botstatus, 'stsclr': stsclr}
    results = simplejson.dumps(data)
    return HttpResponse(results, mimetype='application/json;')


def bot_report(request, botname):
    """
    TODO: Document me.
    """
    bot = getbot(botname)
    results = serialize_sqlalchemy(bot)
    return HttpResponse(results, mimetype='test;')
