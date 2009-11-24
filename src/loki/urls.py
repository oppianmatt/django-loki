# Copyright 2008, Red Hat, Inc
# Dan Radez <dradez@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin


# App views
urlpatterns = patterns('loki.views',
    (r'^$', 'home'),
    (r'^introspect/(steps|status|scheduler)/', 'introspect'),
    (r'^admin/', include(admin.site.urls)),
    (r'^([^/]+)/$', 'home'),
    (r'^([^/]+)/(start|stop|reconfig)/$', 'home'),
    (r'^([^/]+)/([^/]+)/$', 'home'),
    (r'^([^/]+)/([^/]+)/(start|stop|reconfig)/$', 'home'),
)
