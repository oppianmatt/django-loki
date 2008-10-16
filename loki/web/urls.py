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
Global url mappings.
"""

import os

from django.conf import settings
from django.conf.urls.defaults import *

from web.lokiui.views import bot_status, bot_report

#yui info
YUI_PATH = os.path.join(os.path.dirname(__file__), 'yui').replace('\\', '/')


urlpatterns = patterns('',
    (r'^%sui/' % settings.SITE_ROOT, include('web.lokiui.urls')),
    (r'^%sservice/xmlrpc/' % settings.SITE_ROOT, include('web.xmlrpc.urls')),

    # serve yui files
    (r'^%syui/(?P<path>.*)$' % settings.SITE_ROOT, 'django.views.static.serve',
         {'document_root': YUI_PATH}),
    # entry points for ajax calls
    (r'^%sjson/botstatus/([a-z]*)/.*' % settings.SITE_ROOT, bot_status),
    (r'^%sjson/botreport/([a-z]*)/.*'% settings.SITE_ROOT, bot_report),
)
