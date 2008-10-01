from django.conf.urls.defaults import *

from views import *
import os
urlpatterns = patterns('',
    # serve yui files
    (r'^yui/(?P<path>.*)$', 'django.views.static.serve', 
         {'document_root': os.path.join(os.path.dirname(__file__), 'yui').replace('\\','/')}),
    # entry points for ajax calls
    (r'^json/botstatus/([a-z]*)/.*', bot_status),
    (r'^json/botreport/([a-z]*)/.*', bot_report),

    # handle views
    (r'^home/$', home),


    # Example:
    # (r'^web/', include('web.foo.urls')),

    # Uncomment this for admin:
#     (r'^admin/', include('django.contrib.admin.urls')),
)
