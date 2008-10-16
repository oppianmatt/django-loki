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


def create_master(auth, name, profile, webport):
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


def create_slave(auth, name, slaveport, slavepasswd):
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
