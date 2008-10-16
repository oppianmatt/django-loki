import loki.server
from director import Action
from director.decorators import general_help


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
            status = color.format_string("off", "red")
            if server.status() == True:
                status = color.format_string("on", "green")
            msg += "%s (%s).... %s\n" % (color.format_string(server.name, 'blue'),
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
        ServerTasks.report(name)

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
        ServerTasks.register(name, basedir, type, profile, comment)

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
        ServerTasks.unregister(name, delete_bots)

    @general_help('Starts all bots on a server',
                  {'name': 'the FQDN of a registered server'},
                  ['loki server start --name=server.example.com'])
    def start(self, name):
        """
        Starts all bots on a server

        @param name: the FQDN of a registered server
        @type name: str
        """
        ServerTasks.startall(name)

    @general_help('Restarts all bots on a server',
                  {'name': 'the FQDN of a registered server'},
                  ['loki server unreg --name=server.example.com'])
    def restart(self, name):
        """
        Restarts all bots on a server

        @param name: the FQDN of a registered server
        @type name: str
        """
        ServerTasks.restart(name)

    @general_help('Stops all bots on a server',
                  {'name': 'the FQDN of a registered server'},
                  ['loki server unreg --name=server.example.com'])
    def stop(self, name):
        """
        Stops all bots on a server

        @param name: the FQDN of a registered server
        @type name: str
        """
        ServerTasks.stopall(name)

    @general_help('Generates an html file listing masters',
                  examples=['loki server genhome'])
    def genhome(self):
        """
        Generates an html file listing masters
        and giving links to their ports
        """
        ConfigTasks.generate_home_page()
