# Copyright 2008, Red Hat, Inc
# Scott Henson <shenson@redhat.com>
# Dan Radez <dradez@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Tasks performed on the model.
Usually used to get all of a certain class of items.
"""

import string

from random import choice
from sqlalchemy.sql import select
from sqlalchemy.sql import func
from loki.model import Server, BuildBot, BuildMaster, BuildSlave, masters
from loki.Log import *
from loki.Common import *


def listitems(type, Session):
    """
    Makes a list of items for the user to view.

    @param type: The type of item to look at.
    @type type: str
    """
    if type == SERVER:
        return Session.query(Server).all()
    if type == BUILDBOT:
        return Session.query(BuildBot).all()
    if type == MASTER:
        return Session.query(BuildMaster).all()
    if type == SLAVE:
        return Session.query(BuildSlave).all()
    Warn('Unknown Type: %s' % type)
    return None


def getbot(botname, Session):
    return Session.query(BuildBot).filter_by(name=unicode(botname)).first()

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
        servers = Session.query(Server).filter_by(type=unicode(type), profile=unicode(profile)).all()

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


def allocport(type, override, Session):
    """
    Allocate a port of passed type.

    @param type: type of port (web or slave)
    @type type: str

    @param override: user defined to override allocation
    @type: str
    """
    if override != None:
        return override

    if type == WEB:
        web_port = Session.execute(select([func.max(masters.c.web_port)])).scalar()
        if web_port == None:
            return '2000'
        return web_port+1
    if type == SLAVE:
        slave_port = Session.execute(select([func.max(masters.c.slave_port)])).scalar()
        if slave_port== None:
            return '9000'
        return slave_port+1


def genpasswd(override, length=8, chars=string.letters + string.digits):
    """
    Generate a password

    @param override: user defined to override generation
    @type: str
    """
    if override != None:
        return override
    #next line stolen from http://code.activestate.com/recipes/59873/
    return ''.join([choice(chars) for i in range(length)])
