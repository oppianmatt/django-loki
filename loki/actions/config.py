# Copyright 2008, Red Hat, Inc
# Dan Radez <dradez@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
TODO: Document me!
"""

import loki.config

from director import Action
from director.decorators import general_help
from loki.Common import *


class Config(Action):
    """
    loki build config actions
    """

    description_txt = "Manages BuildBot Build Configs"

    @general_help("Lists master's steps.",
                  {'master': 'master name',
                   'path': 'python path to buildbot steps'},
                  ['loki config list --type=step'])
    def list(self, type, master=None, path=None):
        """
        Lists master's steps
        """
        loki.config.list(type, master, path)

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
        loki.config.add(type, bot, module, order)

    @general_help("Delete a build config to a bot.",
                  {'bot': 'Bot name',
                   'order': 'numerical order to execute the step'},
                  ['loki config delete --type=step steps.py --bot=buildslave'
                   '--order=1'])
    def delete(self, type, bot, order):
        """
        Delete a build config from a bot
        """
        loki.config.delete(type, bot, order)

    
    @general_help("Generate and write httpd conf.",
                  {},
                  ['loki config httpd'])
    def httpd(self):
        """
        Generate and write httpd conf
        """
        loki.config.generate_httpd()
