# Copyright 2008-2010, Red Hat, Inc
# Dan Radez <dradez@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import os
from django.conf import settings

BUILDBOT_BASE = getattr(settings, 'BUILDBOT_BASE', 'buildbots')
BUILDBOT_MASTERS = getattr(settings, 'BUILDBOT_MASTERS',
                             os.path.join(BUILDBOT_BASE, 'masters'))
BUILDBOT_SLAVES = getattr(settings, 'BUILDBOT_SLAVES',
                             os.path.join(BUILDBOT_BASE, 'slaves'))
