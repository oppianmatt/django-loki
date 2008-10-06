# Copyright 2008, Red Hat, Inc
# Scott Henson <shenson@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Config tasks.  Tasks related to configuring the Build Masters.

For now these tasks generally relate to git.
"""

import OSCommands
import os

from loki.model import Server, BuildBot, BuildMaster, BuildSlave
from loki import Orm
from loki.ModelTasks import listitems
from loki.Common import *

Session = Orm().session

oscmd = OSCommands.OSCommands(None)
# used to look like this: what was the err for?
# oscmd = OSCommands.OSCommands(None, err=True)


class GitError(Exception):
    """
    Git Error
    """
    pass


class WorkingError(Exception):
    """
    Working Directory Error
    """
    pass


def createrepo(bot, cp):
    """
    Create the git repo.  This includes the working copy.

    @param Name: Name of the build bot
    @type Name: string

    @param cp: A parsed ConfigParser
    @type cp: Config Parser

    @param oscmd: An OSCommands instance.
    @type oscmd: OSCommands
    """
    name = bot.name
    root = cp.get('git', 'repo_root')
    base = cp.get('git', 'base_repo')
    work = cp.get('git', 'work_root')
    git_repo = '%s/%s' % (root, name)
    work_dir = '%s/%s' % (work, name)

    if os.path.exists(git_repo):
        raise(GitError('Git Repo Exists'))

    if os.path.exists(work_dir):
        raise(WorkingError('Working Directory Exists'))
    try:
        oscmd.run_command('git clone --bare %s %s/%s.git' % \
        (base, root, name))

        oscmd.run_command('git clone %s/%s.git %s/%s' % \
        (root, name, work, name))

    except OSCommandError, ex:
        raise(GitError(ex))

    repo_path = cp.get('git', 'repo_path')

    return '%s/%s.git' % (repo_path, name)


def deleterepo(bot, cp):
    """
    Delete the git repo.  This includes the working copy.

    @param Name: Name of the build bot
    @type Name: string

    @param cp: A parsed ConfigParser
    @type cp: Config Parser

    @param oscmd: An OSCommands instance.
    @type oscmd: OSCommands
    """
    name = bot.name
    root = cp.get('git', 'repo_root')
    base = cp.get('git', 'base_repo')
    work = cp.get('git', 'work_root')
    oscmd.run_command('rm -fr %s/%s.git %s/%s' % (root, name, work, name))
    return True


def generate_home_page():
    masters = listitems(MASTER, Session)

    html = "<html>\n"
    html += "<head>\n"
    html += "<title>Loki Home</title>\n"
    html += "</head>\n"
    html += "<body>\n"
    html += "<h1>Masters:</h1>\n"
    html += "<ol>\n"
    for master in masters:
        html += '<li><a href="http://%s:%s/">%s</a></li>\n' \
                % (master.server, master.web_port, master.name)
    html += "</ol>\n"
    html += "</body>\n"
    html += "</html>\n"

    print html
    return html


def generate_config(name):

    master = Session.query(BuildMaster).filter_by(
                     name=unicode(name)).first()
    if master is None:
        Fatal('Master %s does not exist' % name)

    slaves = Session.query(BuildSlave).filter_by(
                     master_id=unicode(master.id)).all()

    buildslaves = ''
    for slave in slaves:
        buildslaves += "\n    BuildSlave('%s', '%s')," % \
            (slave.name, master.slave_passwd)
    print buildslaves
    print template('/etc/loki/master.cfg.tpl',
                   botname=master.name,
                   webhost=master.server,
                   webport=master.web_port,
                   slaveport=master.slave_port,
                   buildslaves=buildslaves)

    """
    slave = Session.query(BuildSlave).filter_by(
                     name=unicode(name)).first()
    if slave == None:
        Fatal('Slave %s does not exist' % name)
    print template('/etc/loki/buildbot.tac.tpl',
                   basedir=("%s/%s") % (slave.server.basedir, slave.name),
                   masterhost=slave.master.server.name,
                   slavename=slave.name,
                   slaveport=slave.master.slave_port,
                   slavepasswd=slave.master.slave_passwd)
    """


def template(tpl, **vars):
    """
    TODO: Document me!
    """
    return open(tpl, 'r').read() % vars
