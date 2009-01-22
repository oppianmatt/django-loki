# Copyright 2009, Red Hat, Inc
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
"""
functions that handle remote connections over func
and execute tasks remotely
"""

import types
import xmlrpclib
import loki.server

from os import tmpfile

from loki.Common import *
from loki.remote import check_func, getminion


def state(server):
    """
    Return the vm's status according to the virthost.
    """
    virtserver = getminion(server.virtserver.name)
    vms = check_func(virtserver.virt.state())
    server_name = _under_the_dots(server.name)
    for vm in vms:
        s = vm.split(' ')
        if s[0] == server_name:
            return s[1]
    return 'nonexistant'

    
def install(cobbler, server):
    """
    Use the func virt  module to install a vm

    @param cobbler: The fqdn of the cobbler server to provision from
    @type cobbler: String

    @param server: the server object to spin up a vm off of
    @type server: SQLAlchemy Server Object

    @return: return from func
    @rtype: func return
    """
    virtserver = getminion(server.virtserver.name)
    return check_func(virtserver.virt.install(_under_the_dots(server.name)))


def create(server):
    """
    Issue the create command to a vm on a virtserver

    @param server: The server you want to shutdown
    @type Server: SQLAlchemy Model
    """
    virtserver = getminion(server.virtserver.name)
    return check_func(virtserver.virt.create(_under_the_dots(server.name)))


def shutdown(server):
    """
    Issue the shutdown command to a vm on a virtserver.

    @param server: The server you want to shutdown
    @type Server: SQLAlchemy Model
    """
    virtserver = getminion(server.virtserver.name)
    return check_func(virtserver.virt.shutdown(_under_the_dots(server.name)))


def _under_the_dots(str):
    """
    change all . to _ in a string
    """
    return str.replace(".", "_")
