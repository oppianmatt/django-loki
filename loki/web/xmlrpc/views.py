# Copyright 2008, Red Hat, Inc
# Dan Radez <dradez@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
# Originally written by Brendan W. McAdams <brendan.mcadams@thewintergrp.com>
# From http://code.djangoproject.com/wiki/XML-RPC
"""
XML-RPC functions.

ALL functions here will be exposed. If you import functions make sure to
do it inside a function you want exposed. Keep in mind that you should
use reST to document these as they will be rendered if someone hits the
xmlrpc service via browser.
"""


# General service methods not related to loki specificly


def ping(auth):
    """
    Verifies the service is up.

    :Paramaters:
       - `auth`: Tuple of username and password to authenticate with
    """
    return "pong"


def health(auth):
    """
    Verifies the services are working OK.

    :Paramaters:
       - `auth`: Tuple of username and password to authenticate with
    """
    import os
    from django.conf import settings

    all = {}
    # Start with verifying we have access to OS commands we need
    cmds = {'ssh-keygen': False}

    command = "which %s > /dev/null 2> /dev/null"
    for key in cmds.keys():
        if os.system(command % key) == 0:
            cmds[key] = True
    all.update(cmds)

    # Check library requirements
    libs = {'loki': False,
            'func': False}
    for key in libs.keys():
        try:
            garbage = __import__(key)
            libs[key] = True
        except ImportError, ie:
            pass
    all.update(libs)

    # check access requirements
    access = {'ssh key repo perms':  False}
    if os.access(settings.XMLRPC_SSHKEY_REPO, os.W_OK):
        access['ssh key repo perms'] = True
    all.update(access)

    return all


# Methods related to the functionality of loki


def create_ssh_key(auth, username, comment):
    """
    Creates a public and private ssh key returning back the public one.

    :Paramaters:
       - `auth`: Tuple of username and password to authenticate with
       - `username`: The username to create the key for.
       - `comment`: The comment to append to the key
    """
    from os import system, close, path
    from tempfile import mkdtemp

    from django.conf import settings

    dir = mkdtemp(suffix=".%s" % username, prefix=settings.XMLRPC_SSHKEY_REPO)

    # TODO: VERIFY INPUT IS SAFE!!!!! It is most likely NOT
    system(
        'ssh-keygen -b 1024 -N "" -C "%s" -f %s > /dev/null 2> /dev/null' % (
               comment, path.join(dir, username)))
    # We don't HAVE to explicitly open and close but, lets not go magical
    key_fobj = open(path.join(dir, "%s.pub" % username), "r")
    public_key = key_fobj.read()[:-1]
    key_fobj.close()

    return public_key


# Exposed bot methods


def bot_create_master(auth, name, profile, webport):
    """
    Creates a build master.

    :Paramaters:
       - `auth`: Tuple of username and password to authenticate with
       - `name`: The name of the new master.
       - `profile`: server profile to use for bot creation
       - `webport`: the port the general buildbot ui will listen on
    """
    type = 'master'

    return "I am a stub"


def bot_create_slave(auth, name, slaveport, slavepasswd):
    """
    Creates a build slave.

    :Paramaters:
       - `auth`: Tuple of username and password to authenticate with
       - `name`: The name of the new slave.
       - `slaveport`: the port the general buildbot ui will listen on
       - `slavepasswd`: the port the general buildbot ui will listen on
    """
    type = 'slave'

    return "I am a stub"


def bot_list_masters(auth):
    """
    Lists all masters.

    :Paramaters:
       - `auth`: Tuple of username and password to authenticate with
    """
    type = 'master'


    return "I am a stub"


def bot_list_slaves(auth):
    """
    Lists all slaves.

    :Paramaters:
       - `auth`: Tuple of username and password to authenticate with
    """
    type = 'slave'

    return "I am a stub"


def bot_reload_master(auth, name):
    """
    Lists all slaves.

    :Paramaters:
       - `auth`: Tuple of username and password to authenticate with
       - `name`: The name of the master to reload.
    """
    return "I am a stub"


def bot_report(auth, name):
    """
    Lists all slaves.

    :Paramaters:
       - `auth`: Tuple of username and password to authenticate with
       - `name`: FQDN of a registered server.
    """
    return "I am a stub"


def bot_restart_master(auth, name):
    """
    Restarts a master.

    :Paramaters:
       - `auth`: Tuple of username and password to authenticate with
       - `name`: Name of the master to restart.
    """
    type = 'master'

    return "I am a stub"


def bot_restart_slave(auth, name):
    """
    Restarts a slave.

    :Paramaters:
       - `auth`: Tuple of username and password to authenticate with
       - `name`: Name of the slave to restart.
    """
    type = 'slave'

    return "I am a stub"


def bot_start_master(auth, name):
    """
    Starts a master.

    :Paramaters:
       - `auth`: Tuple of username and password to authenticate with
       - `name`: Name of the master to start.
    """
    type = 'master'

    return "I am a stub"


def bot_start_slave(auth, name):
    """
    Starts a slave.

    :Paramaters:
       - `auth`: Tuple of username and password to authenticate with
       - `name`: Name of the slave to start.
    """
    type = 'slave'

    return "I am a stub"


def bot_stop_master(auth, name):
    """
    Stops a master.

    :Paramaters:
       - `auth`: Tuple of username and password to authenticate with
       - `name`: Name of the master to stop.
    """
    type = 'master'

    return "I am a stub"


def bot_stop_slave(auth, name):
    """
    Stops a slave.

    :Paramaters:
       - `auth`: Tuple of username and password to authenticate with
       - `name`: Name of the slave to restart.
    """
    type = 'slave'

    return "I am a stub"


def bot_update(auth, name):
    """
    Updates a master.

    :Paramaters:
       - `auth`: Tuple of username and password to authenticate with
       - `name`: Name of the slave to restart.
    """
    type = 'slave'

    return "I am a stub"


# Exposed server methods (subset)


def server_report(auth, name):
    """
    Updates a master.

    :Paramaters:
       - `auth`: Tuple of username and password to authenticate with
       - `name`: FQDN of a registered server
    """
    return "I am a stub"


# Exposed config methods


def config_list(auth, master):
    """
    Updates a master.

    :Paramaters:
       - `auth`: Tuple of username and password to authenticate with
       - `master`: The master to list steps for
    """
    return "I am a stub"
