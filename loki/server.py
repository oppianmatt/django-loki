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
import loki.remote.server

from random import choice
from sqlalchemy.sql import select
from sqlalchemy.sql import func

from loki import Orm
from loki.model import Server, BuildBot, BuildMaster, BuildSlave
from loki.Colors import Colors
from loki.Common import *


def register(name, basedir, type, profile, comment=u'', virtserver=u''):
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

    server = Server(unicode(name),
                    unicode(profile),
                    unicode(basedir),
                    unicode(type),
                    unicode(comment))

    server.virtserver = get(name=unicode(virtserver))
    Orm().session.save(server)
    m = loki.remote.server.getminion(server.name)

    try:
        if server.virtserver == None and m.test.ping() != 1:
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
    slaves = Orm().session.query(BuildSlave).filter_by(
                 server_id=unicode(server.id)).all()
    if len(slaves) > 0:
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
    #get the server object
    if name != None:
        servers = Orm().session.query(
            Server).filter_by(name=unicode(name)).first()
    else:
        servers = Orm().session.query(Server).all()

    return servers


def allocserver(type, profile):
    """
    Allocate a server of the type.  Will return the server with the fewest
    bots currently on it.

    @param type: Type of bot being created
    @type type: string

    @param profile: a profile to apply to the server filter
    @type profile: string
    """
    if profile == None:
        servers = Orm().session.query(
            Server).filter_by(type=unicode(type)).all()
    else:
        servers = Orm().session.query(Server).filter_by(
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
