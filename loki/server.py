# Copyright 2008, Red Hat, Inc
# Dan Radez <dradez@redhat.com>
# Steve 'Ashcrow' Milner <smilner@redhat.com>
# Scott Henson <shenson@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Server API - work with servers
"""

import os
import time
import string

from random import choice
from sqlalchemy.sql import select
from sqlalchemy.sql import func

from loki import Orm
from loki.model import Server, BuildBot, BuildMaster, BuildSlave
from loki.Colors import Colors
from loki.Common import *


def register(name, basedir, type, profile, comment=''):
    """
    Registers a server

    @param name: The FQDN of the server
    @type name: str

    @param basedir: absolute path where bots will live
    @type name: str

    @param type: type of buildbots (master or slave)
    @type type: str

    @param profile: arbitrary value to group servers
    @type profile: str

    @param comment: an optional comment
    @type comment: str
    """

    server = get(name=unicode(name))
    if server != None:
        raise(Exception('Server %s already exists' % name))

    server = Server(name, profile, basedir, type, comment)

    Orm().session.save(server)
    m = loki.remote.server.getminion(server.name)

    try:
        if m.test.ping() != 1:
            raise(Exception('No response from server/func.'))
    except Exception, ex:
        Orm().session.rollback()
        Orm().session.remove()
        raise(Exception('Server %s Registration Failed.\n%s' % \
             (server.name, '$ func %s ping failed\nError: %s' % \
             (server.name, ex))))

    Orm().session.commit()
    return True


def unregister(name, delete_bots=False):
    """
    Unregisters a server

    @param name: the FQDN of a registered server
    @type name: str
    """
    server = get(name=unicode(name))

    if server is None:
        raise(Exception('Server %s does not exist.' % name))

    masters = Orm().session.query(BuildMaster).filter_by(
                  server_id=unicode(server.id)).all()
    if masters != []:
        if delete_bots:
            for master in masters:
                loki.loki.bot.delete(master.name)
        else:
            raise(Exception("Master Bots exist, use --delete-bots to force"))
    slaves = Session.query(BuildSlave).filter_by(
                 server_id=unicode(server.id)).all()
    if slaves != None:
        if delete_bots:
            for slave in slaves:
                loki.loki.bot.delete(slave.name)
        else:
            raise(Exception("Slave Bots exists, use --delete-bots to force"))

    Orm().session.delete(server)
    Orm().session.commit()

    return True


def get(name=None):
    """
    Lists all the servers

    @param name: the FQDN of a registered server
    @type name: str
    """
    if name != None:
        servers = Session.query(Server).filter_by(name=unicode(name)).all()
    else:
        servers = Session.query(Server).all()

    return servers


def restartall(name):
    """
    Restarts all of the bots on a server.

    @param name: FQDN of server to restart bots on.
    @type name: str
    """
    server = Session.query(Server).filterby_by(name=unicode(name)).first()
    if server is None:
        Fatal("No registered servers found.")

    bots = server.buildbots
    if len(bots) == 0:
        Fatal("No Buildbots attached to server %s." % server.name)

    for bot in bots:
        loki.bot.restart(bot.name)

    Success('Complete')


def startall(name):
    """
    Starts all of the bots on a server.

    @param name: FQDN of server to start bots on.
    @type name: str
    """
    server = Session.query(Server).get_by(name=unicode(name))
    if server is None:
        Fatal("No registered server found.")

    bots = server.buildbots
    if len(bots) == 0:
        Fatal("No Buildbots attached to server %s." % server.name)

    for bot in bots:
        loki.bot.start(bot.name)

    Success('Complete')


def stopall(name):
    """
    Stops all bots on a server.

    @param name: FQDN of server to stop bots on.
    @type name: str
    """
    server = Session.query(Server).get_by(name=unicode(name))
    if server is None:
        Fatal("No registered server found.")

    bots = server.buildbots
    if len(bots) == 0:
        Fatal("No Buildbots attached to server %s." % server.name)

    for bot in bots:
        loki.bot.stop(bot.name)

    Success('Complete')


def allocserver(type, profile, Session):
    """
    Allocate a server of the type.  Will return the server with the fewest
    bots currently on it.

    @param type: Type of bot being created
    @type type: string

    @param profile: a profile to apply to the server filter
    @type profile: string
    """
    if profile == None:
        servers = Session.query(Server).filter_by(type=unicode(type)).all()
    else:
        servers = Session.query(Server).filter_by(
                      type=unicode(type), profile=unicode(profile)).all()

    if len(servers) == 0:
        return None
    if len(servers)== 1:
        return servers[0]
    counts = {}
    for server in servers:
        counts[server] = 0

    mincount = min(counts.values())
    for server in servers:
        if counts[server] == mincount:
            return server

    return None
