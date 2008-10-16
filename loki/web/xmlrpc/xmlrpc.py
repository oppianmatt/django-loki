# Copyright 2008, Red Hat, Inc
# Dan Radez <dradez@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
# Originally written by Brendan W. McAdams <brendan.mcadams@thewintergrp.com>
# From http://code.djangoproject.com/wiki/XML-RPC
"""
XML-RPC service code.
"""

import types
import platform
from docutils.core import publish_parts
from SimpleXMLRPCServer import SimpleXMLRPCDispatcher

from django.shortcuts import render_to_response
from django.http import HttpResponse

from web.xmlrpc import views


# Create a Dispatcher; this handles the calls and translates
# info to function maps
if platform.python_version()[:3] == '2.5':
    DISPATCHER = SimpleXMLRPCDispatcher(allow_none=False, encoding=None)
else:
    DISPATCHER = SimpleXMLRPCDispatcher()


def rpc_handler(request):
    """
    The actual handler.

    If post data is defined, it assumes it's XML-RPC and tries to process as
    such. Empty post assumes you're viewing from a browser and tells you about
    the service.

    :Paramaters:
       - `request`: The WSGI request object.
    """
    response = HttpResponse()
    if len(request.POST):
        response.write(DISPATCHER._marshaled_dispatch(request.raw_post_data))
    else:
        methods = DISPATCHER.system_listMethods()

        class Dummy(object):
            """
            Dummy container class.
            """

            def __init__(self, **kwargs):
                """
                Creates the dummy class based off of the keyword args.

                :Paramaters:
                   - `kwargs`: All dictionary of keyword arguments.
                """
                for key in kwargs.keys():
                    self.__setattr__(key, kwargs[key])

        results = []
        for method in methods:
            # this just reads your docblock, so fill it in!
            help = DISPATCHER.system_methodHelp(method)
            html_help = publish_parts(source=help,
                                      writer_name='html')['fragment']
            results.append(Dummy(name=method, help=html_help))

        return render_to_response('xmlrpc/list_functions.html',
                                  {'methods': results})

    response['Content-length'] = str(len(response.content))
    return response


# Register all functions that live in web.xmlrpc.views
for name in dir(views):
    fun = views.__getattribute__(name)
    if type(fun) == types.FunctionType:
        DISPATCHER.register_function(fun, name)
