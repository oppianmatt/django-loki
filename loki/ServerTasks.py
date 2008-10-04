# Copyright 2008, Red Hat, Inc
# Steve 'Ashcrow' Milner <smilner@redhat.com>
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
Server Tasks - These are the actual things that will wrap together everything
else and actually get something done with servers.
"""

import os
import time
import loki.CommonTasks
import loki.ConfigTasks
import loki.ModelTasks
import loki.RemoteTasks
import loki.BotTasks

from loki import Session
from loki.model import Server, BuildBot, BuildMaster, BuildSlave
from loki.Colors import Colors
from loki.Log import *
from loki.Common import *

color = Colors()
Session = Session()
Session = Session.getSession()


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

    server = Session.query(Server).filter_by(name=unicode(name)).first()
    if server != None:
        Fatal('Server %s already exists' % name)

    server = Server(name, profile, basedir, type, comment)

    Session.save(server)
    m = loki.CommonTasks.getminion(server.name)

    try:
        if m.test.ping() != 1:
            raise(Exception('No response from server/func.'))
    except Exception, ex:
        Session.rollback()
        Session.remove()
        Fatal('Server %s Registration Failed.\n%s' % \
             (server.name, '$ func %s ping failed\nError: %s' % \
             (server.name, ex)))

    Session.commit()
    Success('Server %s registered.' % server.name)


def unregister(name, delete_bots=False):
    """
    Unregisters a server

    @param name: the FQDN of a registered server
    @type name: str
    """
    server = Session.query(Server).filter_by(name=unicode(name)).first()

    if server is None:
        Fatal('Server %s does not exist.' % name)

    masters = Session.query(BuildMaster).filter_by(
                  server_id=unicode(server.id)).all()
    if masters != []:
        if delete_bots:
            for master in masters:
                loki.BotTasks.delete(master.name)
        else:
            raise(Exception("Master Bots exist, use --delete-bots to force"))
    slaves = Session.query(BuildSlave).filter_by(
                 server_id=unicode(server.id)).all()
    if slaves != None:
        if delete_bots:
            for slave in slaves:
                loki.BotTasks.delete(slave.name)
        else:
            raise(Exception("Slave Bots exists, use --delete-bots to force"))

    Session.delete(server)
    Session.commit()

    Success('Server %s unregistered.' % name)


def listservers():
    """
    Lists all known servers.

    @param option: Option instance that's calling the callback.
    @type option: Option

    @param opt: Option string passed in.
    @type opt: str

    @param value: The value passed in for the option.
    @type value: str

    @param parser: The optiona parser intance.
    @type parser: OptionParser

    @param Session: SQLAlchemy Session
    @type Session: SQLAlchemy ORM Session Object
    """
    servers = loki.ModelTasks.listitems(SERVER, Session)
    if len(servers) == 0:
        Fatal("No Servers found.")
    msg = ""
    for server in servers:
        status = color.format_string("off", "red")
        m = loki.CommonTasks.getminion(server.name)
        if m.test.ping() == 1:
            status = color.format_string("on", "green")
        msg += "%s (%s).... %s\n" % (color.format_string(server.name, 'blue'),
                                     server.profile,
                                     status)
    Log(msg[:-1])
    return True


def report(name=None):
    """
    Reports server Details

    @param name: the FQDN of a registered server
    @type name: str
    """
    if name != None:
        servers = Session.query(Server).filter_by(name=unicode(name)).all()
    else:
        servers = loki.ModelTasks.listitems(SERVER, Session)

    msg = '\n'
    for server in servers:
        status = color.format_string("off", "red")
        m = loki.CommonTasks.getminion(server.name)
        if m.test.ping() == 1:
            status = color.format_string("on", "green")

        bots = ''
        for bot in server.buildbots:
            bots += "\t%s\n" % bot.name

        msg += "%s: %s\n\tBots Type: %s\n\tProfile: %s\
                \n\tBase Dir: %s\n\tComment: %s\n    %ss:\n%s\n" % \
              (color.format_string(server.name, 'blue'),
               status,
               server.type,
               server.profile,
               server.basedir,
               server.comment,
               server.type.capitalize(),
               bots)
    if msg == '\n':
        Fatal('No Servers Found')

    Log(msg[:-1])
    return True


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
        BotTasks.restart(bot.name)

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
        BotTasks.start(bot.name)

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
        BotTasks.stop(bot.name)

    Success('Complete')
