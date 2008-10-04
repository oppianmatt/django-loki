from director import Action
from loki import BotTasks, ConfigTasks
from loki.Common import *
from loki.Log import *


class Bot(Action):
    """
    loki bot actions
    """

    description_txt = "Manages Bots"

    def list(self, type=BUILDBOT):
        """
        Lists all bots

        == help ==
        \nOptions:
        \ttype:\topt\nmaster or slave
        Example:\tloki bot list

        == end help ==
        """
        BotTasks.listbots(type)

    def report(self, name=None):
        """
        Prints a bot's details

        == help ==
        \nOptions:
        \tname:\topt\tFQDN of a registered server

        Example:
        \tloki server report [--name=server.example.com]

        == end help ==

        @param name: the name of an existsing bot
        @type name: str
        """
        BotTasks.report(name)

    def create(self, name, type, master=None,
               profile=None, webport=None, slaveport=None, slavepasswd=None):
        """
        Creates a new bot

        == help ==
        \nOptions:
        \tname:\t\treq\tbot name
        \ttype:\t\treq\ttype of buildbot (master or slave)
        \tmaster:\t\tre*\ttype of buildbot (master or slave)
        \tprofile:\topt\tserver profile to require for bot creation
        \twebport:\top*\tport to override autogen of a web port
        \tslaveport:\top*\tport to override autogen of a slave port
        \tslavepasswd:\top*\tpassword to override autogen of a slave password
        \t\tre* required when type=slave, ignored when type=master
        \t\top* optional when type=master, ignored when type=slave

        Example:
        \tloki bot create --name=masterbot
        \t\t\t--type=master
        \t\t\t[--profile=os-arch]

        \tloki bot create --name=slavebot
        \t\t\t--type=slave
        \t\t\t--master=masterbot
        \t\t\t[--profile=os-arch]

        == end help ==

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
            BotTasks.createmaster(name, profile, webport,
                                  slaveport, slavepasswd)
        else:
            if type == SLAVE:
                BotTasks.createslave(name, master, profile)
            else:
                Fatal('invalid bot type, use --type=master or --type=slave')

    def delete(self, name):
        """
        Deletes a bot

        == help ==
        \nOptions:
        \tname:\t\treq\tname of a bot

        Example:
        \tloki bot delete --name=masterbot

        == end help ==

        @param name: the name of an existing bot
        @type name: str
        """
        BotTasks.delete(name)

    def start(self, name=None, type=None):
        """
        Starts a bot

        == help ==
        \nOptions:
        \tname:\treq\tname of a bot
        \ttype:\treq*\tmaster or slave, stops all of passed type

        Example:
        \tloki bot start --name=slavebot
        \tloki bot start --type=master

        == end help ==

        @param name: the name of an existing bot
        @type name: str
        """
        if name == None and type == None:
            Fatal("You must pass --name or --type")
        if name != None:
            BotTasks.start(name)
        if type != None:
            BotTasks.startall(type=type)

    def restart(self, name=None, type=None):
        """
        Restarts a bot

        == help ==
        \nOptions:
        \tname:\treq*\ta the name of a bot
        \ttype:\treq*\tmaster or slave, restarts all of passed type
        \t\t Either --name or --type is required. --type is \
ignored if both are passed.
        Example:
        \tloki bot restart --name=botname
        \tloki bot restart --type=master
        == end help ==

        @param name: the name of an exitsting bot
        @type name: str
        """
        if name == None and type == None:
            Fatal("You must pass --name or --type")
        if name != None:
            BotTasks.restart(name)
        if type != None:
            BotTasks.restartall(type=type)

    def stop(self, name=None, type=None):
        """
        Stop a bot

        == help ==
        \nOptions:
        \tname:\treq*\ta the name of a bot
        \ttype:\treq*\tmaster or slave, stops all of passed type
        \t\t Either --name or --type is required. --type is ignored \
if both are passed.

        Example:
        \tloki bot stop --name=botname
        \tloki bot stop --type=slave
        == end help ==

        @param name: the name of an existing bot
        @type name: str
        """
        if name == None and type == None:
            Fatal("You must pass --name or --type")
        if name != None:
            BotTasks.stop(name)
        if type != None:
            BotTasks.stopall(type=type)

    def update(self, name):
        """
        Update a bot

        == help ==
        \nOptions:
        \tname:\treq*\ta the name of a bot

        Example:
        \tloki bot update --name=botname
        == end help ==

        @param name: the name of an existing bot
        @type name: str
        """
        BotTasks.update(name)

    def reload(self, name):
        """
        Update and reload a bot

        == help ==
        \nOptions:
        \tname:\treq*\ta the name of a bot

        Example:
        \tloki bot reload --name=botname
        == end help ==

        @param name: the name of an existing bot
        @type name: str
        """
        BotTasks.reload(name)

    def gen(self, name):
        """
        Test Generate a bots config

        == help ==
        \nOptions:
        \tname:\treq\t name of a bot

        Example:
        \tloki bot gen --name=botname
        == end help ==

        @param name: the name of an existing bot
        @type name: str
        """
        ConfigTasks.generate_config(name)
