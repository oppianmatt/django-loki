# Copyright 2008, Red Hat, Inc
# Dan Radez <dradez@redhat.com>
# Steve 'Ashcrow' Milner <smilner@redhat.com>
# Scott Henson <shenson@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
BotTasks - These are the actual things that will wrap together everything
else and actually get something done.
"""

import os
import time
import loki.RemoteTasks as RemoteTasks

from loki.Common import *
from loki import Orm
from loki.model import Server
from loki.model import Server
from loki.model import BuildBot
from loki.model import BuildMaster
from loki.model import BuildSlave
from loki.model import BuildConfig
from loki.model import BuildParam
from loki.Log import *
from loki.ModelTasks import listitems
from loki.ModelTasks import allocserver
from loki.ModelTasks import allocport
from loki.ModelTasks import genpasswd
from loki.Colors import Colors

color = Colors()
Session = Orm().session


def liststeps(master=None, path=None):
    """
    Lists all steps

    @param master: Optional name master bot to get steps
    @type master: str
    """
    #get the master if passed
    if master != None:
        servers = Session.query(Server).filter_by(name=unicode(master),
                                        type=unicode('master')).all()
    else:
        servers = Session.query(Server).filter_by(type=unicode('master')).all()

    if servers is None:
        if master != None:
            Fatal("Server %s does not exist or is not a Master." % master)
        else:
            Fatal("No Master Servers found.")

    msg = ""
    for server in servers:
        steps = RemoteTasks.getsteps(server, path)
        msg += "%s:\n" % color.format_string(server.name, "blue")
        for step in steps:
            msg += "\t%s: %s\n" % (
                color.format_string(step, "white"),
                _format_step(steps[step]))

    Log(msg[:-1])
    return True


def addstep(builder, step, order):
    """
    add a build step to a build slave.

    @param builder: Name of the build slave
    @type builder: str

    @param step: path to the class being added
    @type step: str

    @param order: numerical order the step will be executed
    @type order: integer
    """
    slave = Session.query(BuildSlave).filter_by(name=unicode(builder)).first()
    if slave == None:
        Fatal("Build Slave %s does not exist." % builder)

    stepname = step.split('.')[-1]
    steps = RemoteTasks.getsteps(slave.master.server,
                                 '.'.join(step.split('.')[:-1]))
    step_dict = {}

    print _format_step(steps[stepname])

    ## for each req get the value from stdin
    for req in steps[stepname][1]:
        sys.stdout.write("%s: " % req)
        hold_val = sys.stdin.readline()
        hold_val = hold_val.rstrip('\n')
        if hold_val == '':
            Fatal("%s is a required parameter" % req)
        step_dict[req] = hold_val.rstrip('\n')

    ## for each opt get the value from stdin
    for opt in steps[stepname][2]:
        sys.stdout.write("%s (%s): " % (opt, steps[stepname][2][opt]))
        hold_val = sys.stdin.readline()
        hold_val = hold_val.rstrip('\n')
        if hold_val != '':
            step_dict[opt] = hold_val

    #make a Build Step
    dbstep = BuildConfig(unicode(step), order)
    Session.save(dbstep)
    #add params
    for param in step_dict:
        dbparam = BuildStepParam(unicode(param), unicode(step_dict[param]))
        dbstep.params.append(dbparam)
        Session.save(dbparam)

    #save steps/params
    slave.configs.append(dbstep)

    Session.commit()
    #report steps
    Log(showsteps(slave))
    return True


def deletestep(builder, order):
    """
    delete step to a build slave.

    @param builder: Name of the build slave
    @type builder: str

    @param order: numerical order the step will be executed
    @type order: integer
    """
    slave = Session.query(BuildSlave).filter_by(name=unicode(builder)).first()
    if slave == None:
        Fatal("Build Slave %s does not exist." % builder)
    for step in slave.steps:
        if int(step.order) == int(order):
            Warn('Deleted step %s' % step)
            Session.delete(step)
    Session.commit()


def _format_step(step):
    """
    format and return a string represenation of a step

    @param step: the step to format
    @type step: ('step.path.name', (req,params), { 'opt' : 'default' } )
    """
    fmt = "%s(" % step[0]
    params = []
    params.extend(step[1])
    for opt in step[2]:
        params.append("%s=%s" % (opt, step[2][opt]))
    fmt += ', '.join(params)
    fmt += ")"
    return fmt


def showsteps(slave):
    """
    format and return a list of steps for a slave

    @param slave: the slave to print steps for
    @type slave: BuildSlave
    """
    fmt = ''
    for step in slave.configs:
        fmt += "    %s: %s\n" % (
            color.format_string(step.order, "blue"),
            color.format_string(step.module, "blue"))
        step.params.reverse()
        for param in step.params:
            fmt += "\t%s: %s\n" % (
                color.format_string(param.name, "white"),
                param.value)
    return fmt
