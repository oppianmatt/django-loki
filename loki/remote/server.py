# Copyright 2009, Red Hat, Inc
# Dan Radez <dradez@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
functions that handle remote connections over func
and execute tasks remotely
"""

import types
import loki.remote.vm
from loki.remote import check_func, getminion


def status(server):
    """
    Pings a server to be sure func is running

    @param server: The host to return the connection to
    @type server: string

    @return: True or false
    @rtype: Boolean
    """
    if server.virtserver != None:
        if loki.remote.vm.state(server) == 'running':
            return True
        else:
            return False
    else:
        m = getminion(server.name)
        return m.test.ping()


def getclasses(server, path):
    """
    Gets a master server's classes from a path

    @param bot: The server you want to get steps from
    @type bot: SQLAlchemy Model
    """
    m = getminion(server.name)
    if path == None:
        clses = m.loki_buildbot.showclasses()
    else:
        clses = m.loki_buildbot.showclasses(path)
    #clean up LokiNone strings to be type None
    if type(clses) == types.DictType:
        for cls in clses:
            for param in clses[cls][2]:
                if clses[cls][2][param] == 'LokiNone':
                    clses[cls][2][param] = None
    return check_func(clses)
