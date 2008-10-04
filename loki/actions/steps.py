from director import Action
from loki import StepsTasks
from loki import ConfigTasks
from loki.Common import *
from loki.Log import *


class Steps(Action):
    """
    loki steps actions
    """

    description_txt = "Manages BuildBot Steps"

    def list(self, master=None, path=None):
        """
        Lists master's steps

        == help ==
        \nOptions:
        \tmaster:\topt\nmaster name
        Example:\tloki steps list

        == end help ==
        """
        StepsTasks.liststeps(master, path)

    def add(self, builder, step, order):
        """
        Add a step to a builders steps

        == help ==
        \nOptions:
        \tbuilder:\treq\nBuild Slave's name
        \tstep:\treq\nclass path to step
        \torder:\treq\nnumerical order to execute the step
        Example:\tloki steps add --builder=buildslave \
--step=buildbot.steps.shell.RemoteShellCommand --order=1

        == end help ==
        """
        StepsTasks.addstep(builder, step, order)
