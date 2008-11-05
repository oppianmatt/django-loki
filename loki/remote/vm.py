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
from loki.remote.server import getminion
from loki.remote import check_func


def install(cobbler, server):
    """
    Returns the client corresponding to the bot

    @param bot: The bot you wish to get the client for
    @type bot: SQLAlchemy Model

    @return: A func client
    @rtype: func.overlord.client.Client
    """
    server = bot.server.name
    return getminion(server)


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
    return str.replace(".", "_")
