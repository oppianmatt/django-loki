# Copyright 2008, Red Hat, Inc
# Dan Radez <dradez@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

__VERSION__ = '0.7.0'
__LICENSE__ = 'GPLv3'

import os

from buildbot.scripts.runner import Options
from buildbot.scripts.runner import createMaster
from buildbot.scripts.runner import createSlave
from buildbot.scripts.runner import restart
from buildbot.scripts.runner import stop
from twisted.python import usage

from loki.thread import BuildBotStart

loki_pwd = os.path.abspath('.')


def build_bot_run(options):
    if '--quiet' not in options:
        options.insert(1, '--quiet')
    config = Options()
    try:
        config.parseOptions(options=options)
    except usage.error, e:
        print "%s:  %s" % (options[0], e)
        print
        c = getattr(config, 'subOptions', config)
        print str(c)
        return 1

    command = config.subCommand
    so = config.subOptions

    if command == "create-master":
        createMaster(so)
    elif command == "upgrade-master":
        upgradeMaster(so)
    elif command == "create-slave":
        createSlave(so)
    elif command == "start":
    ## adapted from
    ## http://stackoverflow.com/questions/972362/spawning-process-from-python
    ## similar recipe http://code.activestate.com/recipes/278731/
        child_pid = os.fork()
        if child_pid == 0:
            # forked child becomes session leader
            os.setsid()
            g_child_pid = os.fork()
            if g_child_pid == 0:
                # second forked process now a non-session-leader,
                # detached from parent, must now close all open files
                try:
                    maxfd = os.sysconf("SC_OPEN_MAX")
                except (AttributeError, ValueError):
                    maxfd = 1024

                for fd in range(maxfd):
                    try:
                        os.close(fd)
                    except OSError:
                    # ERROR, fd wasn't open to begin with (ignored)
                        pass

                # finally execute the buildbot start script
                from buildbot.scripts.startup import start
                start(so)
                os._exit(0)
            else:
                # done with child process
                os._exit(0)
        else:
            print 'waiting'
            os.waitpid(child_pid, 0)
                
    elif command == "stop":
        stop(so, wait=True)
    elif command == "restart":
        restart(so)
    elif command == "reconfig" or command == "sighup":
        from buildbot.scripts.reconfig import Reconfigurator
        Reconfigurator().run(so)
    elif command == "sendchange":
        sendchange(so, True)
    elif command == "debugclient":
        debugclient(so)
    elif command == "statuslog":
        statuslog(so)
    elif command == "statusgui":
        statusgui(so)
    elif command == "try":
        doTry(so)
    elif command == "tryserver":
        doTryServer(so)
    elif command == "checkconfig":
        doCheckConfig(so)

    os.chdir(loki_pwd)
