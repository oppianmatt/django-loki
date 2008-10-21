# Copyright 2008, Red Hat, Inc
# Dan Radez <dradez@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
import loki.server
import loki.remote.server
from director import Action
from director.decorators import general_help
from loki.Common import *
from loki.Colors import Colors

class Server(Action):
    """
    loki server actions
    """

    description_txt = "Manages Servers"

    @general_help('Lists all servers', examples=['loki server list'])
    def list(self):
        """
        Lists all servers.
        """
        servers = loki.server.get()
        if len(servers) == 0:
            Fatal("No Servers found.")
        msg = ""
        for server in servers:
            status = Colors().format_string("off", "red")
            if loki.remote.server.status(server) == True:
                status = Colors().format_string("on", "green")
            msg += "%s (%s).... %s\n" % (Colors().format_string(server.name, 'blue'),
                                         server.profile,
                                         status)
        Log(msg[:-1])

    @general_help('Prints server details',
                  {'name': 'FQDN of a registered server'},
                  ['loki server report [--name=server.example.com]'])
    def report(self, name=None):
        """
        Prints server's details

        @param name: The FQDN of a registered server
        @type name: str
        """
        if name != None:
            servers = loki.server.get(name=unicode(name))
        else:
            servers = loki.server.get()

        msg = '\n'
        for server in servers:
            status = color.format_string("off", "red")
            m = loki.remote.server.getminion(server.name)
            if m.test.ping() == 1:
                status = color.format_string("on", "green")

            bots = ''
            for bot in server.buildbots:
                bots += "\t%s\n" % bot.name

            msg += "%s: %s\n\tBots Type: %s\n\tProfile: %s\
                    \n\tBase Dir: %s\n\tComment: %s\n    %ss:\n%s\n" % \
                  (color.format_string(server.name, 'blue'),
                   status,
                   server.type,
                   server.profile,
                   server.basedir,
                   server.comment,
                   server.type.capitalize(),
                   bots)
        if msg == '\n':
            Fatal('No Servers Found')

        Log(msg[:-1])


    @general_help('Registers a new server',
                  {'name': 'FQDN of the server',
                   'basedir': 'abosulte path where bots will live',
                   'type': 'type of buildbots (master or slave)',
                   'profile': 'arbitrary value to group servers',
                   'comment': 'optional comment'},
                  ['loki server reg --name=server.example.com',
                   '\t\t--basedir=/bots',
                   '\t\t--type=master',
                   '\t\t--profile=os-arch',
                   '\t\t[--comment="vm on virt server"]'])
    def reg(self, name, basedir, type, profile, comment=''):
        """
        Registers a new server

        @param name: The FQDN of the server
        @type name: str

        @param basedir: absolute path where bots will live
        @type basedir: str

        @param type: type of buildbots (master or slave)
        @type type: str

        @param profile: arbitrary value to group servers
        @type profile: str

        @param comment: an optional comment
        @type comment: str
        """
        loki.server.register(name, basedir, type, profile, comment)
        Success('Server %s registered' % name)

    @general_help('Unregisters a new server',
                  {'name': 'the FQDN of a registered server',
                   'delete-bots': 'forces existsing bots to be deleted'},
                  ['loki server unreg --name=server.example.com '
                   '[--delete-bots]'])
    def unreg(self, name, delete_bots=False):
        """
        Unregisteres a server

        @param name: the FQDN of a registered server
        @type name: str
        """
        loki.server.unregister(name, delete_bots)
        Success('Server %s unregistered' % name)

    @general_help('Starts all bots on a server',
                  {'name': 'the FQDN of a registered server'},
                  ['loki server start --name=server.example.com'])
    def start(self, name):
        """
        Starts all bots on a server

        @param name: the FQDN of a registered server
        @type name: str
        """
        loki.server.startall(name)

    @general_help('Restarts all bots on a server',
                  {'name': 'the FQDN of a registered server'},
                  ['loki server unreg --name=server.example.com'])
    def restart(self, name):
        """
        Restarts all bots on a server

        @param name: the FQDN of a registered server
        @type name: str
        """
        loki.server.restart(name)

    @general_help('Stops all bots on a server',
                  {'name': 'the FQDN of a registered server'},
                  ['loki server unreg --name=server.example.com'])
    def stop(self, name):
        """
        Stops all bots on a server

        @param name: the FQDN of a registered server
        @type name: str
        """
        loki.server.stopall(name)

    @general_help('Generates an html file listing masters',
                  examples=['loki server genhome'])
    def genhome(self):
        """
        Generates an html file listing masters
        and giving links to their ports
        """
        loki.config.generate_home_page()
