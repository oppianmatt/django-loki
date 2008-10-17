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
BotTasks - These are the actual things that will wrap together everything
else and actually get something done.
"""

import os
import time

from loki.Common import *
from loki import Orm
from loki.model import Server, BuildBot, BuildMaster, BuildSlave
from loki.Log import *
from loki.Colors import Colors

Session = Orm().session


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
    if Session.query(BuildMaster).filter_by(
                     name=unicode(name)).first() is not None:
        Fatal('Master %s already exists.\n' % name)

    bot = BuildMaster(unicode(name))
    bot.slave_port = allocport(SLAVE, slaveport, Session)
    bot.slave_passwd = unicode(genpasswd(slavepasswd))
    bot.web_port = allocport(WEB, webport, Session)
    bot.config_source = u'loki'

    # SQLAlchemy Session... marking where to Rollback to
    # Attempt to Allocate Server and roll back if failure
    server = allocserver(MASTER, profile, Session)
    if server is None:
        Session.rollback()
        Session.remove()
        Fatal('No servers available.')

    server.buildbots.append(bot)

    Session.save(bot)
    try:
        RemoteTasks.create_master(bot)
        if not RemoteTasks.exists(bot):
            raise(Exception('Remote creation tasks failed'))
    except Exception, ex:
        Session.rollback()
        Session.remove()
        Fatal('Failed to create Master %s.\n%s' % (name, ex))

    Session.commit()
    Success('Build Master %s Created.' % bot.name)

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
    if Session.query(BuildSlave).filter_by(
                     name=unicode(name)).first() is not None:
        Fatal('Slave %s already exists.\n' % name)


    bot = BuildSlave(unicode(name))

    server = allocserver(SLAVE, profile, Session)
    if server is None:
        Session.rollback()
        Fatal('No servers available.\n')

    server.buildbots.append(bot)

    master = Session.query(BuildMaster).filter_by(name=unicode(master)).first()
    if master is None:
        Session.rollback()
        Fatal('Master %s does not exist' % master)

    master.slaves.append(bot)

    #Session.save(bot)
    try:
        RemoteTasks.create_slave(bot)
        if not RemoteTasks.exists(bot):
            raise(Exception('Remote creation tasks failed'))
    except Exception, ex:
        Session.rollback()
        Fatal('Failed to create Slave %s.\n %s' % (name, ex))

    Session.commit()
    Success('Build Slave %s Created.\n' % name)


def delete(name):
    """
    Deletes a buildbot master or slave.

    @param name: The name of the bot
    @type name: str
    """

    bot = Session.query(BuildBot).filter_by(name=unicode(name)).first()

    if bot is None:
        Fatal('BuildBot %s does not exist.' % name)

    try:
        RemoteTasks.delete(bot)
        if RemoteTasks.exists(bot):
            Fatal('Remote deletion Failed')
    except Exception, ex:
        Session.rollback()
        Session.remove()
        Fatal('Failed to delete BuildBot %s.\n %s' % (name, ex))

    Session.delete(bot)
    #Session.save(bot)
    Session.commit()

    Success('BuildBot %s Deleted.' % name)


def get(type=BUILDBOT, name=None):
    """
    get bot objects

    @param type: Optional type of bot to filter by
    @type type: str

    @param name: Optional name of bot to filter by
    @type name: str
    """

    if type == BUILDBOT:
        qry =  Session.query(BuildBot)
    if type == MASTER:
        qry =  Session.query(BuildMaster)
    if type == SLAVE:
        qry =  Session.query(BuildSlave)
    
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
    bot = Session.query(BuildBot).filter_by(name=unicode(name)).first()
    try:
        RemoteTasks.restart(bot)
    except Exception, ex:
        Fatal('%s Failed: %s' % (action, ex))
    Success('%s Complete' % action)


def startall(type):
    """
    Starts all of a bot type

    @param type: master or slave
    @type type: str
    """
    bots = listitems(type, Session)
    if bots is None:
        Fatal("No %ss found." % type.capitalize())
    msg = ""
    for bot in bots:
        ret = False
        try:
            if not RemoteTasks.status(bot):
                ret = RemoteTasks.restart(bot)
        except Exception, ex:
            Error('%s %s failed to Start: \n %s' % (
                                   type.capitalize(),
                                    bot.name, ex))
        if ret is True:
            Info('%s %s Started.' % (type.capitalize(), bot.name))

    Success('Complete')


def restartall(type):
    """
    Restarts all of a bot type

    @param type: master or slave
    @type type: str
    """
    bots = listitems(type, Session)
    if bots is None:
        Fatal("No %ss found." % type.capitalize())
    msg = ""
    for bot in bots:
        ret = False
        try:
            if RemoteTasks.status(bot):
                ret = RemoteTasks.restart(bot)
        except Exception, ex:
            Error('%s %s failed to restart: \n %s' % (type.capitalize(),
                                                      bot.name, ex))
        if ret is True:
            Info('%s %s restarted.' % (type.capitalize(), bot.name))

    Success('Complete')


def stop(name):
    """
    Stops a master or slave.

    @param name: name of a bot
    @type name: str
    """
    bot = Session.query(BuildBot).filter_by(name=unicode(name)).first()
    try:
        RemoteTasks.stop(bot)
    except Exception, ex:
        Fatal('Stop Failed: %s' % ex)
    Success('Stop Complete')


def stopall(type):
    """
    Stops all masters.

    @param type: master or slave
    @type type: str
    """
    bots = listitems(type, Session)
    if bots is None:
        Fatal("No %ss found." % type.capitalize())
    msg = ""
    for bot in bots:
        ret = False
        try:
            ret = RemoteTasks.stop(bot)
        except Exception, ex:
            Error('%s %s failed to stop: \n %s' % (type.capitalize(),
                                                   bot.name, ex))
        if ret is True:
            Info('%s %s stopped.' % (type.capitalize(), bot.name))

    Success('Complete')


def update(name):
    """
    Update a master or slave.

    @param name: name of a buildbot
    @type name: str
    """
    bot = Session.query(BuildBot).filter_by(name=unicode(name)).first()
    if bot.type != MASTER:
        Fatal('Build Bot is not a master. Only masters can be updated.')
    try:
        RemoteTasks.update(bot)
    except Exception, ex:
        Fatal('Update Failed: %s' % ex)
    Success('Update Complete')


def reload(name):
    """
    Reload a master or slave.

    @param name: name of a buildbot
    @type name: str
    """
    bot = Session.query(BuildBot).filter_by(name=unicode(name)).first()
    if bot.type != "master":
        Fatal('Build Bot is not a master, Only masters can be reloaded')
    try:
        RemoteTasks.update(bot)
        RemoteTasks.reload(bot)
    except Exception, ex:
        Fatal('Reload Failed: %s' % ex)
    Success('Reload Complete')


def generate_config(name):

    bot = Session.query(BuildBot).filter_by(
                     name=unicode(name)).first()
    if bot is None:
        Fatal('Bot %s does not exist' % name)

    if bot.type == MASTER:
        master = Session.query(BuildMaster).filter_by(
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
    if not RemoteTasks.config(bot, t):
        Success('config unchanged.')
    else:
        Success('Config updated.')


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
