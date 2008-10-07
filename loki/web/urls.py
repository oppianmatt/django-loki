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

from django.conf.urls.defaults import *

from views import *


# mock the apache django.root option
# http://www.example.com/loki/
dr = 'loki/'
# http://www.example.com/
#dr=''

#yui info
yui_path = os.path.join(os.path.dirname(__file__), 'yui')
yui_path = yui_path.replace('\\', '/')


urlpatterns = patterns('',
    # serve yui files
    (r'^%syui/(?P<path>.*)$' % dr, 'django.views.static.serve',
         {'document_root': yui_path}),
    # entry points for ajax calls
    (r'^%sjson/botstatus/([a-z]*)/.*' % dr, bot_status),
    (r'^%sjson/botreport/([a-z]*)/.*'% dr, bot_report),

    # handle views
    (r'^%s$' % dr, home),


    # Example:
    # (r'^web/', include('web.foo.urls')),

    # Uncomment this for admin:
#     (r'^admin/', include('django.contrib.admin.urls')),
)
