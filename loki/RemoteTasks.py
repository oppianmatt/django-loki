# Copyright 2008, Red Hat, Inc
# Steve 'Ashcrow' Milner <smilner@redhat.com>
# Scott Henson <shenson@redhat.com>
# Dan Radez <dradez@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Remote tasks.
These tasks take a buildbot model object
and make the call to the build nodes to do the actual work.
"""

import types
from CommonTasks import getminion, getbot, getpath
from loki.Log import Fatal


def restart(bot):
    """
    Restarts a bot.

    @param bot: The bot you wish to restart
    @type bot: SQLAlchemy Model
    """
    if status(bot):
        rbot = getbot(bot)
        rpath = getpath(bot=bot)
        return __check_func(rbot.loki_buildbot.restart(bot.name, rpath))
    else:
        return start(bot)


def start(bot):
    """
    Starts a bot.

    @param bot: The bot you wish to start
    @type bot: SQLAlchemy Model
    """
    if not status(bot):
        rbot = getbot(bot)
        rpath = getpath(bot=bot)
        return __check_func(rbot.loki_buildbot.start(bot.name, rpath))
    return None


def stop(bot):
    """
    Stops a bot.

    @param bot: The bot you wish to stop
    @type bot: SQLAlchemy Model
    """
    if status(bot):
        rbot = getbot(bot)
        rpath = getpath(bot=bot)
        return __check_func(rbot.loki_buildbot.stop(bot.name, rpath))
    return None


def exists(bot):
    """
    Find if a bot exists

    @param bot: The bot to check existance of
    @type bot: SQLAlchemy Model
    """
    rbot = getbot(bot)
    rpath = getpath(bot=bot)
    rbot_exists = rbot.loki_buildbot.exists(bot.name, rpath)
    return __check_func(rbot_exists)


def status(bot):
    """
    Find if a bot is up or not

    @param bot: The bot you wish to get status of
    @type bot: SQLAlchemy Model
    """
    rbot = getbot(bot)
    rpath = getpath(bot=bot)
    rbot_status = rbot.loki_buildbot.status(bot.name, rpath)
    return __check_func(rbot_status)


def reload(bot):
    """
    reload a buildbot

    @param bot: The bot you wish to reload
    @type bot: SQLAlchemy Model
    """
    if status(bot):
        rbot = getbot(bot)
        rpath = getpath(bot=bot)
        return __check_func(rbot.loki_buildbot.reload(bot.name, rpath))
    return None


def update(bot):
    """
    Update the configurations for a BuildBot

    @param bot: The bot you wish to update
    @type bot: SQLAlchemy Model
    """
    rbot = getbot(bot)
    rpath = getpath(bot=bot)
    if __check_func(rbot.loki_buildbot.update(bot.name, rpath)):
        return reload(bot)
    return None


def create_master(bot):
    """
    Buildbot Master Creator

    @param bot: The master bot you wish to create
    @type bot: SQLAlchemy Model
    """
    rbot = getbot(bot)
    rpath = getpath(bot=bot)
    name = bot.name
    config = bot.config_source
    if exists(bot):
        raise(Exception('Master Exists on Node'))
    return __check_func(rbot.loki_buildbot.create_master(name, config, rpath))


def create_slave(bot):
    """
    Buildbot Slave Creator

    @param bot: The slave bot you wish to create
    @type bot: SQLAlchemy Model
    """
    rbot = getbot(bot)
    rpath = getpath(bot=bot)
    name = bot.name
    master = bot.master.server
    passwd = bot.master.slave_passwd
    port = bot.master.slave_port
    master_url = '%s:%s' % (master, port)
    if exists(bot):
        raise(Exception('Slave Exists on Node'))
    return __check_func(rbot.loki_buildbot.create_slave(name,
                                                   master_url,
                                                   passwd,
                                                   rpath))


def delete(bot):
    """
    Delete a buildbot

    @param bot: The bot you wish to delete
    @type bot: SQLAlchemy Model
    """
    if not exists(bot):
        return True
    if status(bot):
        stop(bot)
    rbot = getbot(bot)
    return __check_func(rbot.loki_buildbot.delete())


def getsteps(server, path):
    """
    Gets a master's buildsteps

    @param bot: The server you want to get steps from
    @type bot: SQLAlchemy Model
    """
    m = getminion(server.name)
    if path == None:
        stps = m.loki_buildbot.showsteps()
    else:
        stps = m.loki_buildbot.showsteps(path)
    #clean up LokiNone strings to be type None
    if type(stps) == types.DictType:
        for step in stps:
            for param in stps[step][2]:
                if stps[step][2][param] == 'LokiNone':
                    stps[step][2][param] = None
    return __check_func(stps)


def __check_func(value):
    """
    Check the return value of func and throw any exceptions that are found

    @param value: Return value of func call
    """

    #print value
    if type(value) == types.ListType and len(value) and value[0] == 'REMOTE_ERROR':
        Fatal('\n'.join(value))
    return value
