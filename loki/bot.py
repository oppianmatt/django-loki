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
Bot API - work with the buildbots
"""

import os
import time
import string
import loki.server

from random import choice
from sqlalchemy.sql import select
from sqlalchemy.sql import func
from loki.Common import *
from loki import Orm
from loki.model import Server, BuildBot, BuildMaster, BuildSlave, masters
from loki.Colors import Colors


def createmaster(name, profile=None, webport=None,
                       slaveport=None, slavepasswd=None):
    """
    Creates a master buildbot

    @param name: The name of the bot
    @type name: str

    @param profile: server profile to use
    @type profile: str

    @param webport: port to override autogen of a web port
    @type webport: str

    @param slaveport: port to override autogen of a slave port
    @type slaveport: str

    @param slavepasswd: password to override autogen of a slave password
    @type slavepasswd: str
    """
    # Check if master already Exists
    if Orm().session.query(BuildMaster).filter_by(
                     name=unicode(name)).first() is not None:
        raise(Exception('Master %s already exists.\n' % name))

    bot = BuildMaster(unicode(name))
    bot.slave_port = allocport(SLAVE, slaveport, Orm().session)
    bot.slave_passwd = unicode(genpasswd(slavepasswd))
    bot.web_port = allocport(WEB, webport, Orm().session)
    bot.config_source = u'loki'

    # SQLAlchemy Orm().session... marking where to Rollback to
    # Attempt to Allocate Server and roll back if failure
    server = loki.server.allocserver(MASTER, profile, Orm().session)
    if server is None:
        Orm().session.rollback()
        Orm().session.remove()
        rasie(Exception('No servers available.'))

    server.buildbots.append(bot)

    Orm().session.save(bot)
    try:
        loki.remote.bot.create_master(bot)
        if not loki.remote.bot.exists(bot):
            raise(Exception('Remote creation tasks failed'))
    except Exception, ex:
        Orm().session.rollback()
        Orm().session.remove()
        rasie(Exception('Failed to create Master %s.\n%s' % (name, ex)))

    Orm().session.commit()
    return True


def createslave(name, master, profile):
    """
    Creates a buildbot slave.

    @param name: The name of the bot
    @type name: str

    @param master: bot's master bot
    @type master: str

    @param profile: server profile to use
    @type profile: str
    """
    if master == None:
        Fatal("Please specify slave bot's master using --master")
    #check if slave already exists
    if Orm().session.query(BuildSlave).filter_by(
                     name=unicode(name)).first() is not None:
        Fatal('Slave %s already exists.\n' % name)


    bot = BuildSlave(unicode(name))

    server = loki.server.allocserver(SLAVE, profile, Orm().session)
    if server is None:
        Orm().session.rollback()
        Fatal('No servers available.\n')

    server.buildbots.append(bot)

    master = Orm().session.query(BuildMaster).filter_by(name=unicode(master)).first()
    if master is None:
        Orm().session.rollback()
        Fatal('Master %s does not exist' % master)

    master.slaves.append(bot)

    #Orm().session.save(bot)
    try:
        loki.remote.bot.create_slave(bot)
        if not loki.remote.bot.exists(bot):
            raise(Exception('Remote creation tasks failed'))
    except Exception, ex:
        Orm().session.rollback()
        raise(Exception('Failed to create Slave %s.\n %s' % (name, ex)))

    Orm().session.commit()
    return True

def delete(name):
    """
    Deletes a buildbot master or slave.

    @param name: The name of the bot
    @type name: str
    """

    bot = get(name=unicode(name))

    if bot is None:
        rasie(Exception('BuildBot %s does not exist.' % name))

    try:
        if loki.remote.bot.exists(bot):
            loki.remote.bot.delete(bot)
        if loki.remote.bot.exists(bot):
            raise(Exception('Remote deletion Failed'))
    except Exception, ex:
        Orm().session.rollback()
        Orm().session.remove()
        raise(Exception('Failed to delete BuildBot %s.\n %s' % (name, ex)))

    Orm().session.delete(bot)
    #Orm().session.save(bot)
    Orm().session.commit()

    return True

def get(type=BUILDBOT, name=None):
    """
    get bot objects

    @param type: Optional type of bot to filter by
    @type type: str

    @param name: Optional name of bot to filter by
    @type name: str
    """

    if type == BUILDBOT:
        qry =  Orm().session.query(BuildBot)
    if type == MASTER:
        qry =  Orm().session.query(BuildMaster)
    if type == SLAVE:
        qry =  Orm().session.query(BuildSlave)
    
    if name == None:
        return qry.all()
    else:
        return qry.filter_by(name=unicode(name)).first()


def start(name):
    """
    Restarts a master or slave.

    @param name: Name of the bot
    @type name: str
    """
    restart(name, action="Start")


def restart(name, action="Restart"):
    """
    Restarts a master or slave.

    @param name: Name of the bot
    @type name: str

    @param action: action to report attempted
    @type action: str
    """
    bot = loki.bot.get(name=unicode(name))
    try:
        loki.remote.bot.restart(bot)
    except Exception, ex:
        raise(Exepetion('%s Failed: %s' % (action, ex)))
    Success('%s Complete' % action)


def startall(type):
    """
    Starts all of a bot type

    @param type: master or slave
    @type type: str
    """
    bots = loki.bot.get(type=type)
    if bots is None:
        raise(Exception("No %ss found." % type.capitalize()))
    msg = ""
    for bot in bots:
        ret = False
        try:
            if not loki.remote.bot.status(bot):
                ret = loki.remote.bot.restart(bot)
        except Exception, ex:
            Error('%s %s failed to Start: \n %s' % (
                                   type.capitalize(),
                                    bot.name, ex))
        if ret is True:
            Info('%s %s Started.' % (type.capitalize(), bot.name))

    return True


def restartall(type):
    """
    Restarts all of a bot type

    @param type: master or slave
    @type type: str
    """
    bots = loki.bot.get(type=type)
    if bots is None:
        raise(Exception("No %ss found." % type.capitalize()))
    msg = ""
    for bot in bots:
        ret = False
        try:
            if loki.remote.bot.status(bot):
                ret = loki.remote.bot.restart(bot)
        except Exception, ex:
            Error('%s %s failed to restart: \n %s' % (type.capitalize(),
                                                      bot.name, ex))
        if ret is True:
            Info('%s %s restarted.' % (type.capitalize(), bot.name))

    return True


def stop(name):
    """
    Stops a master or slave.

    @param name: name of a bot
    @type name: str
    """
    bot = loki.bot.get(name=unicode(name))
    try:
        loki.remote.bot.stop(bot)
    except Exception, ex:
        raise(Exception('Stop Failed: %s' % ex))
    Success('Stop Complete')


def stopall(type):
    """
    Stops all masters.

    @param type: master or slave
    @type type: str
    """
    bots = loki.bot.get(type=type)
    if bots is None:
        raise(Exception("No %ss found." % type.capitalize()))
    msg = ""
    for bot in bots:
        ret = False
        try:
            ret = loki.remote.bot.stop(bot)
        except Exception, ex:
            Error('%s %s failed to stop: \n %s' % (type.capitalize(),
                                                   bot.name, ex))
        if ret is True:
            Info('%s %s stopped.' % (type.capitalize(), bot.name))

    return True


def update(name):
    """
    Update a master or slave.

    @param name: name of a buildbot
    @type name: str
    """
    bot = Orm().session.query(BuildBot).filter_by(name=unicode(name)).first()
    if bot.type != MASTER:
        Fatal('Build Bot is not a master. Only masters can be updated.')
    try:
        loki.remote.bot.update(bot)
    except Exception, ex:
        Fatal('Update Failed: %s' % ex)
    Success('Update Complete')


def reload(name):
    """
    Reload a master or slave.

    @param name: name of a buildbot
    @type name: str
    """
    bot = loki.bot.get(name=unicode(name))
    if bot.type != "master":
        raise(Exception('Build Bot is not a master, Only masters can be reloaded'))
    try:
        loki.remote.bot.update(bot)
        loki.remote.bot.reload(bot)
    except Exception, ex:
        raise(Exception(('Reload Failed: %s' % ex)))
    return True


def generate_config(name):

    bot = Orm().session.query(BuildBot).filter_by(
                     name=unicode(name)).first()
    if bot is None:
        raise(Exception('Bot %s does not exist' % name))

    if bot.type == MASTER:
        master = Orm().session.query(BuildMaster).filter_by(
                     name=unicode(name)).first()
        slaves = master.slaves

        buildslaves = ''
        builders = []
        factories = ''
        modules = []
        statuses = ''
        schedulers = ''
        ct = 1
        for slave in slaves:
            #remebers the slaves
            buildslaves += "\n    BuildSlave('%s', '%s')," % \
                (slave.name, bot.slave_passwd)
            #create buildfactory
            b = '%s_%s' % (bot.name, slave.name)
            factories += '%s = factory.BuildFactory()\n' % b
            for step in slave.steps:
                if step.module not in modules:
                    modules.append(step.module)
                factories += "%s.addStep(%s)\n" % (b,
                                      _generate_class(step))
            #create builder from factory
            factories += "b%s = {'name': '%s',\n" % (ct, slave.name)
            factories += "      'slavename': '%s',\n" % slave.name
            factories += "      'builddir': '%s',\n" % slave.name
            factories += "      'factory': %s, }\n\n" % b
            # remember the builders
            builders.append('b%s' % ct)
            ct += 1

        #generate statuses
        for status in master.statuses:
            statuses += "c['status'].append(%s)" % _generate_class(status)
            modules.append(status.module)

        #restructure the imports
        imports = ''
        for x in modules:
            imports += 'from %s import %s\n' % (
                        '.'.join(x.split('.')[:-1]),
                        x.split('.')[-1])

        #generate the template
        t = _template('/etc/loki/master.cfg.tpl',
                   botname=bot.name,
                   webhost=bot.server,
                   webport=bot.web_port,
                   slaveport=bot.slave_port,
                   buildslaves=buildslaves,
                   imports=imports,
                   factories=factories,
                   builders=','.join(builders),
                   statuses=statuses,
                   schedulers=schedulers)

    if bot.type == SLAVE:
        t = _template('/etc/loki/buildbot.tac.tpl',
                   basedir=("%s/%s") % (bot.server.basedir, bot.name),
                   masterhost=bot.master.server.name,
                   slavename=bot.name,
                   slaveport=bot.master.slave_port,
                   slavepasswd=bot.master.slave_passwd)

    #write the file to the bot over func
    return loki.remote.bot.config(bot, t)

def allocport(type, override):
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
        web_port = Orm().session.execute(select([func.max(
        masters.c.web_port)])).scalar()
        if web_port == None:
            return '2000'
        return web_port+1
    if type == SLAVE:
        slave_port = Orm().session.execute(select(
        [func.max(masters.c.slave_port)])).scalar()
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


def _template(tpl, **vars):
    """
    TODO: Document me!
    """
    return open(tpl, 'r').read() % vars


def _generate_class(cls):
   gcls = cls.module.split('.')[-1]
   gprm = ["%s=%s" % (param.name, param.value) for param in cls.params]
   return "%s(%s)"% (gcls,\
                     ', '.join(gprm))
