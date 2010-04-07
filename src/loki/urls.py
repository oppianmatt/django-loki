# Copyright 2008-2010, Red Hat, Inc
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
from django.contrib.auth.views import login
from django.contrib.auth.views import logout_then_login


# App views
urlpatterns = patterns('loki.views',
    (r'^$', 'home'),
    (r'^favicon.ico/?$', 'home'),
    (r'^login/$', login),
    (r'^logout/$', logout_then_login),
    (r'^import/(steps|status|scheduler)/', 'import_config'),
    (r'^ajax/config/step/save/([0-9]+)/', 'config_step_save'),
    (r'^ajax/config/status/save/([0-9]+)/', 'config_status_save'),
    (r'^ajax/config/scheduler/save/([0-9]+)/', 'config_scheduler_save'),
    (r'^ajax/config/(step|status|scheduler)/load/([0-9]+)/', 'config_load'),
    (r'^ajax/config/(step|status|scheduler)/delete/', 'config_delete'),
    (r'^ajax/config/(step|status|scheduler)/add/([0-9]+)/([0-9]+)/',
        'config_add'),
    (r'^admin/', include(admin.site.urls)),
    (r'^([^/]+)/$', 'home'),
    (r'^([^/]+)/([^/]+)/$', 'home'),
)
