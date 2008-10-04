# Copyright 2009, Red Hat, Inc
# Scott Henson <shenson@redhat.com>
# Steve 'Ashcrow' Milner <smilner@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Buildbot Func Module
"""

import os
import popen2
import time
import inspect
import buildbot.steps
from func.minion.modules import func_module


class OSCommands(object):
    """
    Proxies common shell commands.
    """

    def __init__(self, logger = None):
        """
        OSCommands

        @param logger: logger object to log to
        @type logger: log.logger
        """
        self.logger = logger

    def run_command(self, command, allow_except=True):
        """
        Pipe that does command dirty work with the OS.

        @param command: command to run in the shell.
        @type command: str

        @return: output file object.
        """
        cmd = popen2.Popen4(command)
        if cmd.wait():
            error = '\n'.join(cmd.fromchild.readlines())
            if self.logger is None:
                self.logger.error('Command Failed: %s' % command)
                self.logger.error(error)
            #TODO: Is allow_except the way to go here?
            if allow_except:
                #Skipping the OSCommandError cuz it's broken
                #raise(OSCommandError('Command Failed: %s' % command, \
                #                         cmd, error))
                raise(Exception('%s\n%s' % (cmd, error)))
            else:
                return False
        return True


class BuildBotModule(func_module.FuncModule):
    """
    BuildBot creation class
    """
    version = "0.3.5"
    api_version = "0.0.1"
    description = "A module to create and user buildbot masters and slaves."

    def __init__(self):
        """
        Creates the BuildBot object and registers it with Func
        """
        self.methods = {
            "create_master": self.create_master,
            "create_slave": self.create_slave,
            "write_config": self.write_config,
            "delete": self.delete,
            "start": self.start,
            "stop": self.stop,
            "restart": self.restart,
            "reload": self.reload,
            "update": self.update,
            "status": self.status,
            "exists": self.exists,
            "list": self.list,
            "showsteps": self.showsteps}
        func_module.FuncModule.__init__(self)
        self.oscmd = OSCommands(logger = self.logger)

    def create_master(self, name, gitrepo, path):
        """
        Buildbot Master Creator

        @param name: Name of the Buildbot Master
        @type name: string

        @param gitrepo: Git repository to clone to create the config
        @type gitrepo: string

        @param path: Path to the build bot configs
        @type path: string
        """
        #for i in range(20):
        #    if os.path.exists(gitrepo):
        #        break
        #    time.sleep(1)
        try:
            self.__create_user(name, path)
            self.__git(name, path, 'clone', gitrepo=gitrepo)
            self.oscmd.run_command('buildbot create-master %s' % \
                               self.__bot(name, path))
            self.oscmd.run_command('cd %s ;git checkout HEAD; git pull' % \
                                   (self.__bot(name, path)))
            self.oscmd.run_command('chown -R %s.buildbots %s ' % \
                               (name, self.__bot(name, path)))
        except Exception, ex:
            self.logger.error('Buildbot Master %s Creation Failed'%name)
            self.__delete_user(name, path, allow_except = False)
            raise(Exception(ex))
        self.logger.info('BuildBot Master %s Created'%name)
        return True

    def create_slave(self, name, master, passwd, path):
        """
        Buildbot Slave Creator

        @param name: Name of the Buildbot Slave
        @type name: string

        @param master: URI of the buildbot master in the form server.name:port
        @type master: string

        @param passwd: Buildbot Password
        @type passwd: string
        """
        try:
            bot = self.__bot(name, path)
            self.__create_user(name, path)
            if not os.path.exists(bot):
                self.oscmd.run_command('mkdir %s' % bot)
            self.oscmd.run_command('buildbot create-slave %s %s %s %s' % \
                                   (bot, master, name, passwd))
            self.oscmd.run_command('chown -R %s.buildbots %s ' % (name, bot))
        except Exception, ex:
            self.logger.error('Buildbot Slave %s Creation Failed'%name)
            self.__delete_user(name, path, allow_except = False)
            raise(Exception(ex))
        self.logger.info('BuildBot Slave %s Created'%name)
        return True

    def write_config(self, name, path, file, content):
        """
        Write a config file

        @param name: Name of a BuildBot
        @type name: str

        @param path: path to buildbot's parent dir
        @type path: str

        @param file: config's file name
        @type file: str

        @param content: content of config file
        @type content: str
        """
        config_file = "%s/%s/%s" % (path, name, file)
        config = open(config_file, 'w')
        config.write(content)
        config.close()
        return os.path.exists(config_file)

    def delete(self, name, path):
        """
        Delete a buildbot

        @param name: Name of the Buildbot
        @type name: string
        """
        return self.__delete_user(name, path)

    def start(self, name, path):
        """
        Start a buildbot

        @param name: Name of the Buildbot
        @type name: string
        """
        status = self.status(name, path)
        if status is False:
            return self.__bot_command(name, path, 'start')
        return status

    def stop(self, name, path):
        """
        Stop a buildbot

        @param name: Name of the Buildbot
        @type name: string
        """
        status = self.status(name, path)
        if status is True:
            return self.__bot_command(name, path, 'stop', allow_except = False)
        return status

    def restart(self, name, path):
        """
        Restart a buildbot

        @param name: Name of the Buildbot
        @type name: string
        """
        status = self.status(name, path)
        if status is True:
            return self.__bot_command(name, path, 'restart')
        return status

    def reload(self, name, path):
        """
        reload a buildbot

        @param name: Name of the Buildbot
        @type name: string

        @return: True if reloaded,
                 False if not reloaded,
                 None if bot doesn't exist
        @rtype: bool
        """
        status = self.status(name, path)
        if status is True:
            return self.__bot_command(name, path, 'sighup', \
                                           allow_except = False)
        return status

    def update(self, name, path):
        """
        Update the configurations for a BuildBot

        @param name: Name of the Buildbot
        @type name: string
        """
        return self.__git(name, path, 'pull')

    def exists(self, name, path):
        """
        If the buildbot Exists

        @param name: Name of the Buildbot
        @type name: string

        @return: True if exists, False if not
        @rtype: bool
        """
        bot = self.__bot(name, path)
        if os.path.exists(bot):
            return True
        return False

    def status(self, name, path):
        """
        Status of the buildbot

        @param name: Name of the Buildbot
        @type name: string

        @return: True if running, otherwise False.
        @rtype: bool
        """
        bot = self.__bot(name, path)
        pidfile = "%s/twistd.pid" % bot
        if os.path.exists(pidfile):
            pid = open(pidfile).readline().strip()
            if self.oscmd.run_command("ps %s > /dev/null" % pid) is True:
                return True
        return False

    def list(self, path):
        """
        List the buildbots on the host

        @param path: Path to the build bot configs
        @type path: string

        @return: List of build bots
        @rtype: list of strings
        """
        dirs = os.listdir(path)
        bots = []
        for pos in dirs:
            tac = '%s/%s/buildbot.tac' % (path, pos)
            if os.path.isdir('%s/%s' % (path, pos)) and os.path.exists(tac):
                bots.append(pos)

        return bots

    def __bot(self, name, path):
        """
        Returns the path to the bot

        @param name: Name of the BuildBot
        @type name: string

        @param path: Path to the build bot configs
        @type path: string
        """

        return os.path.realpath('%s/%s' % (path, name))

    def __bot_command(self, name, path, cmd, allow_except = True):
        """
        Runs the command against the bot

        @param name: Name of the BuildBot
        @type name: string

        @param path: Path to the build bot configs
        @type path: string

        @param cmd: command to run against the bot
        @type cmd: string

        @return: True if command succeeded, otherwise error message
        @rtype: bool or string
        """
        curdir = self.__bot_dir(name, path)
        bot_cmd = 'buildbot %s %s' % (cmd, self.__bot(name, path))
        sucmd = 'su - %s -c ' % name
        try:
            os.chdir(curdir)
            return self.oscmd.run_command('%s "%s"' % (sucmd, bot_cmd),
                                 allow_except = allow_except)
        except Exception, ex:
            raise(Exception(ex))

    def __bot_dir(self, name, path):
        """
        Changes to the bot directory

        @param name: Name of the Buildbot
        @type name: string

        @param path: Path to the build bot configs
        @type path: string

        @return: name of the former directory
        @rtype: string
        """

        bot = self.__bot(name, path)
        curdir = os.getcwd()
        os.chdir(bot)
        return curdir

    def __git(self, name, path, cmd, gitrepo=None):
        """
        Run a command on a git repo into the selected buildbot

        @param name: Name of the Buildbot
        @type name: string

        @param path: Path to the build bot configs
        @type path: string

        @param cmd: Git command to run
        @type cmd: string

        @param gitrepo: location of the git repo to clone
        @type gitrepo: string
        """
        bot = self.__bot(name, path)
        exists = os.path.exists(bot)

        try:
            if cmd == 'clone':
                curdir = os.getcwd()
                os.chdir(path)
                ret = self.oscmd.run_command('git %s %s %s/%s' % \
                                             (cmd, gitrepo, path, name))
            elif exists:
                curdir = self.__bot_dir(name, path)
                ret = self.oscmd.run_command('git %s' % cmd)
                self.oscmd.run_command('chown -R %s .' % name)
            else:
                curdir = os.getcwd()
                ret = 'Not Cloning and Bot does not exist'
        except Exception, ex:
            raise(Exception(ex))
        os.chdir(curdir)
        return ret

    def __create_user(self, name, path):
        """
        Create a user to put a bot into

        @param name: Name of the Buildbot
        @type name: string

        @param path: Path to the build bot configs
        @type path: string

        @return: True if successful False otherwise
        @rtype: bool
        """
        self.oscmd.run_command('groupadd -r -f buildbots')
        opts = '-M -g buildbots -r -d %s/%s' % (path, name)
        self.oscmd.run_command('luseradd %s %s' %(opts, name))
        return True

    def __delete_user(self, name, path, allow_except = True):
        """
        Delete a user to put a bot into

        @param name: Name of the Buildbot
        @type name: string

        @param path: Path to the build bot configs
        @type path: string

        @return: True if successful False otherwise
        @rtype: bool
        """
        try:
            opts = '-r'
            self.oscmd.run_command('userdel %s %s' %(opts, name))
        except Exception, ex:
            self.logger.critical('Unable to delete user %s.'%name)
            if allow_except:
                raise(Exception(ex))
        return True

    def showsteps(self, pkg='buildbot.steps'):
        """
        Get a list of tuples representing steps
        each tuple will have the name of a class in the module
        a list of required parameters and
        a dict of optional parameters and their defaults

        @param obj: a python package
        @type obj: module

        @return: dict of tuples 'StepName'
                 : ('classname', ['reqs'], {'opts': None})
        """
        #x = __import__(pkg, fromlist=['module'])
        x = __import__(pkg, globals(), locals(), [pkg])

        modules = []
        #Check if x is a directory and get it's modules
        if hasattr(x, '__path__'):
            for f in os.listdir(x.__path__[0]):
                if f.endswith('.py') and f != '__init__.py':
                    modules.append(f.split('.')[0])
        #or it is a module so adjust
        else:
            modules.append(pkg.split('.')[-1])
            pkg = '.'.join(pkg.split('.')[0:-1])


        steps = {}
        for m in modules:
            #y = __import__("%s.%s" % (pkg, m), fromlist=['module'])
            y = __import__("%s.%s" % (pkg, m), globals(), locals(), ['module'])
            for i in inspect.getmembers(y):
                if inspect.isclass(i[1]) and \
                   i[1].__module__.startswith("%s.%s" % (pkg, m)) and \
                   not i[0].startswith('_'):
                    req = []
                    opt = {}
                    i_init = inspect.getargspec(i[1].__init__)
                    c = 0
                    for a in i_init[0]:
                        if a != 'self':
                            if i_init[3] == None:
                                opt[a] = 'LokiNone'
                            else:
                                if c < len(i_init[3]):
                                    if i_init[3][c] == None:
                                        opt[a] = 'LokiNone'
                                    else:
                                        opt[a] = i_init[3][c]
                                else:
                                    req.append(a)
                        c = c + 1
                    steps[i[0]] = ("%s.%s" % (i[1].__module__, i[0]), req, opt)
        return steps


methods = BuildBotModule()
register_rpc = methods.register_rpc
