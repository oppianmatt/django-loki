# Copyright 2008, Red Hat, Inc
# Dan Radez <dradez@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
from director import Action
from director.decorators import general_help

import loki.bot
import loki.remote.bot
import loki.config
from loki.Colors import Colors
from loki.Common import *


class Bot(Action):
    """
    loki bot actions
    """
    description_txt = "Manages Bots"

    @general_help("Lists all bots.",
                  {'type': 'master or slave'},
                  ['loki bot list'])
    def list(self, type=BUILDBOT):
        """
        Lists all bots

        @param type: Optional type of bot to filter by
        @type type: str
        """
        bots = loki.bot.get()
        if len(bots) == 0 and type == BUILDBOT:
            Fatal("No Bots found.")
        if len(bots) == 0:
            Fatal("No %s Bots found." % type)

        for bot in bots:
            status = Colors().format_string("off", "red")
            if loki.remote.bot.status(bot) is True:
                status = Colors().format_string("on", "green")
            msg = "%s: %s .... %s\n" % \
                  (Colors().format_string(bot.name, "white"),
                   Colors().format_string(bot.server.name, 'blue'),
                   status)
            Log(msg[:-1])


    @general_help("Prints a bot's details.",
                  {'name': 'FQDN of a registered server'},
                  ['tloki server report [--name=example.com]'])
    def report(self, name=None):
        """
        Prints a bot's details

        @param name: the name of an existsing bot
        @type name: str
        """
        if name == None:
            bots = loki.bot.get()
        else:
            bots = []
            bots.append(loki.bot.get(name=name))
        msg = "\n"
        masters = ''
        slaves = ''
        for bot in bots:
            status = Colors().format_string("off", "red")
            if loki.remote.bot.status(bot) is True:
                status = Colors().format_string("on", "green")
            if bot.server.type == MASTER:
                masters += "%s: %s\n\tServer: %s\n\tType: %s\n\tProfile: %s\
                        \n\tSlave/Web Port: %s/%s\n\tSlave Passwd: %s\n" % \
                      (Colors().format_string(bot.name, "blue"),
                       status,
                       bot.server.name,
                       bot.server.type,
                       bot.server.profile,
                       bot.slave_port,
                       bot.web_port,
                       bot.slave_passwd)
            if bot.server.type == SLAVE:
                 slaves += "%s: %s\n\tServer: %s\n\tType: %s\
                            \n\tMaster: %s\n\tProfile: %s\n" %\
                           (Colors().format_string(bot.name, "blue"),
                            status,
                            bot.server.name,
                            bot.server.type,
                            bot.master,
                            bot.server.profile)

        if name != None:
            msg += "%s%s\n" % (masters, slaves)
        else:
            msg += "%s\n\n%s\n%s\n\n%s\n" % \
                (Colors().format_string("Masters:", "white"),
                 masters,
                 Colors().format_string("Slaves:", "white"),
                 slaves)
        if bot.type == MASTER:
            msg += '  Build Statuses:\n'
            msg += loki.config.showclasses(STATUS, bot)
            msg += '\n'
            msg += '  Build Schedulers:\n'
            msg += loki.config.showclasses(SCHEDULER, bot)
            msg += '\n'

        if bot.type == SLAVE:
            msg += '  Build Steps:\n'
            msg += loki.config.showclasses(STEP, bot)
            msg += '\n'

        Log(msg[:-1])


    @general_help("Creates a new bot",
                  {'name': 'bot name',
                   'type': 'type of buildbot (master or slave)',
                   'master': 'type of buildbot (master or slave)',
                   'profile': 'server profile to require for bot creation',
                   'webport': 'port to override autogen of a web port',
                   'slaveport': 'port to override autogen of a slave port',
                   'slavepasswd': 'slave password to override autogen'},
                  ['loki bot create --name=masterbot --type=master',
                   'loki bot create --name=name --type=slave --master=mastr'])
    def create(self, name, type, master=None,
               profile=None, webport=None, slaveport=None, slavepasswd=None):
        """
        Creates a new bot

        @param name: The name of the bot
        @type name: str

        @param type: type of buildbot (master or slave)
        @type type: str

        @param master: name of existing master
            required when type=slave
        @type master: str

        @param profile: server profile to use
        @type profile: str

        @param webport: port to override autogen of a web port
            optional when type=master
        @type webport: str

        @param slaveport: port to override autogen of a slave port
            optional when type=master
        @type slaveport: str

        @param slavepasswd: password to override autogen of a slave password
            optional when type=master
        @type slavepasswd: str
        """
        if type == MASTER:
            try:
                loki.bot.createmaster(name, profile, webport,
                                      slaveport, slavepasswd)  
            except Exception, ex:
                Fatal(ex)
            Success('Build Master %s Created.\n' % name)
        else:
            if type == SLAVE:
                try:
                    loki.bot.createslave(name, master, profile)
                except Exception, ex:
                    Fatal(ex)
                Success('Build Slave %s Created.\n' % name)
            else:
                Fatal('invalid bot type, use --type=master or --type=slave')


    @general_help("Deletes a bot.",
                  {'name': 'name of a bot'},
                  ['tloki bot delete --name=masterbot'])
    def delete(self, name):
        """
        Deletes a bot

        @param name: the name of an existing bot
        @type name: str
        """
        loki.bot.delete(name)
        Success('BuildBot %s Deleted.' % name)

    @general_help("Starts a bot.",
                  {'name': 'name of a bot',
                   'type':' master or slave, stops all of passed type'},
                  ['loki bot start --name=slavebot',
                   'loki bot start --type=master'])
    def start(self, name=None, type=None):
        """
        Starts a bot

        @param name: the name of an existing bot
        @type name: str
        """
        if name == None and type == None:
            Fatal("You must pass --name or --type")
        if name != None:
            loki.bot.start(name)
        if type != None:
            loki.bot.startall(type=type)

    @general_help("Starts a bot.",
                  {'name': 'a the name of a bot',
                   'type': 'master or slave, restarts all of passed type'},
                  ['loki bot restart --name=botname',
                   'loki bot restart --type=master'])
    def restart(self, name=None, type=None):
        """
        Restarts a bot

        @param name: the name of an exitsting bot
        @type name: str
        """
        if name == None and type == None:
            Fatal("You must pass --name or --type")
        if name != None:
            loki.bot.restart(name)
        if type != None:
            loki.bot.restartall(type=type)

    @general_help("Stops a bot.",
                  {'name': 'a the name of a bot',
                   'type': 'master or slave, stops all of passed type'},
                  ['loki bot stop --name=botname',
                   'loki bot stop --type=slave'])
    def stop(self, name=None, type=None):
        """
        Stop a bot

        @param name: the name of an existing bot
        @type name: str
        """
        if name == None and type == None:
            Fatal("You must pass --name or --type")
        if name != None:
            loki.bot.stop(name)
        if type != None:
            loki.bot.stopall(type=type)

    @general_help("Update a bot.",
                  {'name': 'a the name of a bot'},
                  ['loki bot update --name=botname'])
    def update(self, name):
        """
        Update a bot

        @param name: the name of an existing bot
        @type name: str
        """
        loki.bot.update(name)

    @general_help("Update and reload a bot.",
                  {'name': 'a the name of a bot'},
                  ['loki bot reload --name=botname'])
    def reload(self, name):
        """
        Update and reload a bot

        @param name: the name of an existing bot
        @type name: str
        """
        loki.bot.reload(name)

    @general_help("Generate a bots config.",
                  {'name': 'name of a bot'},
                  ['loki bot gen --name=botname'])
    def config(self, name):
        """
        Generate a bots config

        @param name: the name of an existing bot
        @type name: str
        """
        loki.bot.generate_config(name)
