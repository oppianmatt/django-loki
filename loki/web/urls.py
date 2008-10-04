from django.conf.urls.defaults import *

from views import *
import os

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
