"""
Classes related to running commands locally on a Linux box.
"""
import os
import popen2
from loki.Log import *

# TODO: change the buildbot commands to use the buildbot libs


class OSCommandError(Exception):
    """
    OS Command Error

    @param
    """

    def __init__(self, value, command, error):
        """
        OS Command Error

        @param value: error message
        @type value: string

        @param command: command that was executed
        @type command: string

        @param error: error message from command
        @type error: string
        """
        self.value = value
        self.command = command
        self.error = error

    def __str__(self):
        """
        Turn OSCommandError into a string
        """
        print self.value


class OSCommands:
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
            else:
                Error('Command Failed: %s\n' % command)
                Error(error)
            #TODO: Is allow_except the way to go here?
            if allow_except:
                #Skipping the OSCommandError cuz it's broken
                #raise(OSCommandError('Command Failed: %s' % command, \
                #                         cmd, error))
                raise(Exception('%s\n%s' % (cmd, error)))
            else:
                return False
        return True
