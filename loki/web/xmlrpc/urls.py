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

from django.conf.urls.defaults import *


urlpatterns = patterns('',
    (r'$', 'web.xmlrpc.xmlrpc.rpc_handler'),
)
