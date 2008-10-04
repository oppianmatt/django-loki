from director import Action
from loki import ServerTasks
from loki import ConfigTasks


class Server(Action):
    """
    loki server actions
    """

    description_txt = "Manages Servers"

    def list(self):
        """
        -------------------------------
        server list: Lists all servers
        -------------------------------

        == help ==
        \nOptions:\tNone
        Example:\tloki server list

        == end help ==
        """
        ServerTasks.listservers()

    def report(self, name=None):
        """
        --------------------------------------
        server report: Prints server's details
        --------------------------------------

        == help ==
        \nOptions:
        \tname:\topt\tFQDN of a registered server

        Example:
        \tloki server report [--name=server.example.com]

        == end help ==

        @param name: The FQDN of a registered server
        @type name: str
        """
        ServerTasks.report(name)

    def reg(self, name, basedir, type, profile, comment=''):
        """
        ----------------------------------
        server reg: Registers a new server
        ----------------------------------

        == help ==
        \nOptions:
        \tname:\t\treq\tFQDN of the server
        \tbasedir:\treq\tabosulte path where bots will live
        \ttype:\t\treq\ttype of buildbots (master or slave)
        \tprofile:\treq\tarbitrary value to group servers
        \tcomment:\topt\toptional comment

        Example:
        \tloki server reg --name=server.example.com
        \t\t\t--basedir=/bots
        \t\t\t--type=master
        \t\t\t--profile=os-arch
        \t\t\t[--comment="vm on virt server"]

        == end help ==

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

    def unreg(self, name, delete_bots=False):
        """
        -----------------------------------
        server unreg: Unregisteres a server
        -----------------------------------

        == help ==
        \nOptions:
        \tname:\t\treq\tthe FQDN of a registered server
        \tdelete-bots:\topt\tforces existsing bots to be deleted

        Example:
        \tloki server unreg --name=server.example.com
        \t\t\t  [--delete-bots]
        == end help ==

        @param name: the FQDN of a registered server
        @type name: str
        """
        ServerTasks.unregister(name, delete_bots)

    def start(self, name):
        """
        Starts all bots on a server

        == help ==
        \nOptions:
        \tname:\t the FQDN of a registered server

        Example:
        \tloki server start --name=server.example.com
        == end help ==

        @param name: the FQDN of a registered server
        @type name: str
        """
        ServerTasks.startall(name)

    def restart(self, name):
        """
        Restarts all bots on a server

        == help ==
        \nOptions:
        \tname:\t the FQDN of a registered server

        Example:
        \tloki server unreg --name=server.example.com
        == end help ==

        @param name: the FQDN of a registered server
        @type name: str
        """
        ServerTasks.restart(name)

    def stop(self, name):
        """
        Stops all bots on a server

        == help ==
        \nOptions:
        \tname:\t the FQDN of a registered server

        Example:
        \tloki server unreg --name=server.example.com
        == end help ==

        @param name: the FQDN of a registered server
        @type name: str
        """
        ServerTasks.stopall(name)

    def genhome(self):
        """
        Generates an html file listing masters
        and giving links to their ports

        == help ==
        \nOptions: None

        Example:
        \tloki server genhome
        == end help ==
        """
        ConfigTasks.generate_home_page()
