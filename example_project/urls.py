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
admin.autodiscover()


urlpatterns = patterns('',
    (r'^', include('loki.urls')),

)
# static media content through Django ONLY for development
if settings.DEBUG == True:
    mediapatterns = patterns('django.views',
        (r'^%sjs/(?P<path>.*)$' % settings.MEDIA_URL, 'static.serve',
            {'document_root': '%sjs' % settings.STATIC_DOC_ROOT}),
        (r'^%scss/(?P<path>.*)$' % settings.MEDIA_URL, 'static.serve',
            {'document_root': '%scss' % settings.STATIC_DOC_ROOT}),
        (r'^%simages/(?P<path>.*)$' % settings.MEDIA_URL, 'static.serve',
            {'document_root': '%simages' % settings.STATIC_DOC_ROOT}),
    )
    # put media patterns first sunce loki has a catch all
    mediapatterns += urlpatterns
    urlpatterns = mediapatterns
