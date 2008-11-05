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

import loki.remote.vm
import loki.server

from loki.Common import *
from loki.Colors import Colors
from loki.model import Server
from loki import Orm
from director import Action
from director.decorators import general_help


class Vm(Action):
    """
    loki server actions
    """

    description_txt = "Manages Virtual Servers"

    @general_help('Install a VM', examples=['loki vm install \
--cobbler=cobbler.example.com --name=server.example.com'])
    def install(self, name, cobbler):
        """
        Issue the command to install a vm on a virtserver using cobbler
        """
        server = loki.server.get(name=name)
        if server == None:
            Fatal("%s not registered.")
        if loki.remote.server.status(server.virtserver) == True:
            loki.remote.vm.install(server, cobbler)
        else:
            Fatal('Virt server did not respond to ping.')

    @general_help('Start a VM', examples=['loki vm create \
--name server.example.com'])
    def create(self, name):
        """
        Issue the create command to a vm
        """
        self._gen_command(name, loki.remote.vm.create)

    @general_help('Shutdown a VM', examples=['loki vm create \
--name server.example.com'])
    def shutdown(self, name):
        """
        Issue the shutdown command to a vm
        """
        self._gen_command(name, loki.remote.vm.shutdown)

    def _gen_command(self, name, command):
        """
        Issue a command to a vm
        """
        server = loki.server.get(name=name)
        if server == None:
            Fatal("%s not registered.")

        if loki.remote.server.status(server.virtserver) == True:
            command(server)
        else:
            Fatal('Virt server did not respond to ping.')
