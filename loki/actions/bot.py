from director import Action
from director.decorators import general_help

from loki import BotTasks, ConfigTasks
from loki.Common import *
from loki.Log import *


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

        :type is the type we are to list.
        """
        BotTasks.listbots(type)

    @general_help("Prints a bot's details.",
                  {'name': 'FQDN of a registered server'},
                  ['tloki server report [--name=example.com]'])
    def report(self, name=None):
        """
        Prints a bot's details

        @param name: the name of an existsing bot
        @type name: str
        """
        BotTasks.report(name)

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
            BotTasks.createmaster(name, profile, webport,
                                  slaveport, slavepasswd)
        else:
            if type == SLAVE:
                BotTasks.createslave(name, master, profile)
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
        BotTasks.delete(name)

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
            BotTasks.start(name)
        if type != None:
            BotTasks.startall(type=type)

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
            BotTasks.restart(name)
        if type != None:
            BotTasks.restartall(type=type)

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
            BotTasks.stop(name)
        if type != None:
            BotTasks.stopall(type=type)

    @general_help("Update a bot.",
                  {'name': 'a the name of a bot'},
                  ['loki bot update --name=botname'])
    def update(self, name):
        """
        Update a bot

        @param name: the name of an existing bot
        @type name: str
        """
        BotTasks.update(name)

    @general_help("Update and reload a bot.",
                  {'name': 'a the name of a bot'},
                  ['loki bot reload --name=botname'])
    def reload(self, name):
        """
        Update and reload a bot

        @param name: the name of an existing bot
        @type name: str
        """
        BotTasks.reload(name)

    @general_help("Generate a bots config.",
                  {'name': 'name of a bot'},
                  ['loki bot gen --name=botname'])
    def config(self, name):
        """
        Generate a bots config

        @param name: the name of an existing bot
        @type name: str
        """
        BotTasks.generate_config(name)
