# Copyright 2009, Red Hat, Inc
# Steve 'Ashcrow' Milner <smilner@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Common taks shared by the different layers.
Generally they accept a bot, but thats not law.
"""

import func.overlord.client as fc


def getminion(host):
    """
    Gets the func client connection for the host

    @param host: The host to return the connection to
    @type host: string

    @return: A func client
    @rtype: func.overlord.client.Overload
    """
    return fc.Overlord(host, noglobs=True)


def getbot(bot):
    """
    Returns the client corresponding to the bot

    @param bot: The bot you wish to get the client for
    @type bot: SQLAlchemy Model

    @return: A func client
    @rtype: func.overlord.client.Client
    """
    server = bot.server.name
    return getminion(server)


def getpath(bot=None, server=None):
    """
    Returns the base path for the bot

    @return: the base path
    @rtype: string
    """
    if bot is not None and server is None:
        return bot.server.basedir
    elif bot is None and server is not None:
        return server.basedir
    elif bot is not None and server is not None:
        if server == bot.server:
            return server.basedir
        else:
            raise(Exception('Bot not found on Server, path is ambiguous'))
    else:
        raise(Exception('Must specify a bot or a server'))
