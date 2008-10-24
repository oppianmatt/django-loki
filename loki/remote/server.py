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

import func.overlord.client as fc


def getminion(host):
    """
    Gets the func client connection for the host

    @param host: The host to return the connection to
    @type host: string

    @return: A func client
    @rtype: func.overlord.client.Overload
    """
    return fc.Overlord(host, noglobs=True)


def status(server):
    """
    Pings a server to be sure func is running

    @param server: The host to return the connection to
    @type server: string

    @return: True or false
    @rtype: Boolean
    """
    m = getminion(server.name)
    return m.test.ping()