# Copyright 2008, Red Hat, Inc
# Scott Henson <shenson@redhat.com>
# Steve 'Ashcrow' Milner <smilner@redhat.com>
# Dan Radez <dradez@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

__VERSION__ = '0.3.3'
__LICENSE__ = 'GPLv3'

from loki.SetupTasks import createSession, getConfig, validateModel


class Orm(object):

    session = None

    def __init__(self):
        if self.session == None:
            self.session = createSession(getConfig())
