from director import Action
from director.decorators import general_help

from loki import ConfigTasks
from loki.Common import *
from loki.Log import *


class Config(Action):
    """
    loki build config actions
    """

    description_txt = "Manages BuildBot Build Configs"

    @general_help("Lists master's steps.",
                  {'master': 'master name'},
                  ['loki config list --type=step'])
    def list(self, type, master=None, path=None):
        """
        Lists master's steps
        """
        ConfigTasks.list(type, master, path)

    @general_help("Add a build config to a bot.",
                  {'bot': 'Bot name',
                   'module': 'class path',
                   'order': 'numerical order to execute the step'},
                  ['loki config add --type=step --bot=buildslave --module='
                   'buildbot.steps.shell.RemoteShellCommand --order=1'])
    def add(self, type, bot, module, order):
        """
        Add a build config to a bot.
        """
        ConfigTasks.add(type, bot, module, order)

    @general_help("Add a build config to a bot.",
                  {'bot': 'Bot name',
                   'order': 'numerical order to execute the step'},
                  ['loki config delete --type=step steps.py--bot=buildslave'
                   '--order=1'])
    def delete(self, type, bot, order):
        """
        Delete a build config from a bot
        """
        ConfigTasks.delete(type, bot, order)
