# Copyright 2008, Red Hat, Inc
# Dan Radez <dradez@redhat.com>
# Scott Henson <shenson@redhat.com>
# Steve 'Ashcrow' Milner <smilner@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

__VERSION__ = '0.6.1'
__LICENSE__ = 'GPLv3'

from loki.store import createSession, getConfig


class Orm(object):
    """
    TODO: Document me!
    """

    __shared_state = {'session': None}

    def __init__(self):
        self.__dict__ = self.__shared_state
        if self.session == None:
            self.session = createSession(getConfig())

    def session(self):
        return self.session
