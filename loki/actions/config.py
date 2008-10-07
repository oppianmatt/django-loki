from director import Action
from loki import ConfigTasks
from loki.Common import *
from loki.Log import *


class Config(Action):
    """
    loki build config actions
    """

    description_txt = "Manages BuildBot Build Configs"

    def list(self, type, master=None, path=None):
        """
        Lists master's steps

        == help ==
        \nOptions:
        \tmaster:\topt\nmaster name
        Example:\tloki config list --type=step

        == end help ==
        """
        ConfigTasks.list(type, master, path)

    def add(self, type, bot, module, order):
        """
        Add a build config to a bot

        == help ==
        \nOptions:
        \tbot:\treq\nBot's name
        \tmodule:\treq\nclass path
        \torder:\treq\nnumerical order to execute the step
        Example:\tloki config add --type=step --bot=buildslave \
--module=buildbot.steps.shell.RemoteShellCommand --order=1

        == end help ==
        """
        ConfigTasks.add(type, bot, module, order)

    def delete(self, type, bot, order):
        """
        Delete a build config from a bot

        == help ==
        \nOptions:
        \tbot:\treq\nBot's name
        \torder:\treq\nnumerical order to execute the step
        Example:\tloki config delete --type=step steps.py--bot=buildslave \
--order=1

        == end help ==
        """
        ConfigTasks.delete(type, bot, order)
