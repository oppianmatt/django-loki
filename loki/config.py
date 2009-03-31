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
Config API - handles config objects for bots
"""

import os
import time
import loki.remote.server
import loki.bot
import ConfigParser

from loki.Common import *
from loki import Orm
from loki.model import Server
from loki.model import BuildBot
from loki.model import BuildMaster
from loki.model import BuildSlave
from loki.model import BuildStep
from loki.model import BuildStatus
from loki.model import BuildScheduler
from loki.model import BuildParam
from loki.Colors import Colors


def list(type, master=None, path=None):
    """
    Lists Build Configs from a master

    @param master: Optional name master bot to get steps
    @type master: str
    """
    #get the master if passed
    if master != None:
        servers = Orm().session.query(Server).filter_by(name=unicode(master),
                                        type=unicode('master')).all()
    else:
        servers = Orm().session.query(Server).filter_by(
                                        type=unicode('master')).all()

    if servers is None:
        if master != None:
            Fatal("Server %s does not exist or is not a Master." % master)
        else:
            Fatal("No Master Servers found.")

    msg = ""
    for server in servers:
        clses = loki.remote.server.getclasses(server, path)
        msg += "%s:\n" % Colors().format_string(server.name, "blue")
        for cls in clses:
            msg += "\t%s: %s\n" % (
                Colors().format_string(cls, "white"),
                _format_class(clses[cls]))

    Log(msg[:-1])
    return True


def add(type, bot, path, order):
    """
    add a build config to a bot

    @param bot: Name of the bot
    @type bot: str

    @param path: path to the class being added
    @type path: str

    @param order: numerical order the class will be executed
    @type order: integer
    """

    #make a Build Config Object
    if type == STEP:
        dbcls = BuildStep(unicode(path), order)
        bot = Orm().session.query(BuildSlave).filter_by(
                                      name=unicode(bot)).first()
        cfg = bot.steps
        master = bot.master.server
    else:
        bot = Orm().session.query(BuildMaster).filter_by(
                                      name=unicode(bot)).first()
        master = bot.server
        if type == STATUS:
            dbcls = BuildStatus(unicode(path), order)
            cfg = bot.statuses
        else:
            if type == SCHEDULER:
                dbcls = BuildScheduler(unicode(path), order)
                cfg = bot.schedulers
            else:
                Fatal('%s is an invalid type.' % type)
    Orm().session.save(dbcls)

    #be sure we got a bot
    if bot == None:
        Fatal("Bot %s does not exist." % bot)

    #load the class and get parameters
    clsname = path.split('.')[-1]
    clses = loki.remote.server.getclasses(master,
                                 '.'.join(path.split('.')[:-1]))
    cls_dict = {}

    print _format_class(clses[clsname])

    ## for each req get the value from stdin
    for req in clses[clsname][1]:
        sys.stdout.write("%s: " % req)
        hold_val = sys.stdin.readline()
        hold_val = hold_val.rstrip('\n')
        if hold_val == '':
            Fatal("%s is a required parameter" % req)
        cls_dict[req] = hold_val.rstrip('\n')

    ## for each opt get the value from stdin
    for opt in clses[clsname][2]:
        sys.stdout.write("%s (%s): " % (opt, clses[clsname][2][opt]))
        hold_val = sys.stdin.readline()
        hold_val = hold_val.rstrip('\n')
        if hold_val != '':
            cls_dict[opt] = hold_val

    #add params
    for param in cls_dict:
        dbparam = BuildParam(unicode(param), unicode(cls_dict[param]))
        dbcls.params.append(dbparam)
        Orm().session.save(dbparam)

    #save the config object
    cfg.append(dbcls)

    Orm().session.commit()

    Log(showclasses(type, bot))
    return True


def delete(type, bot, order):
    """
    delete config from a bot.

    @param type: type of Config object
    @type type: str

    @param bot: Name of the build slave
    @type bot: str

    @param order: numerical index
    @type order: integer
    """
    if type == STEP:
        bot = Orm().session.query(BuildSlave).filter_by(
                                       name=unicode(bot)).first()
        cfg = bot.steps
    else:
        bot = Orm().session.query(BuildMaster).filter_by(
                                       name=unicode(bot)).first()
        if type == STATUS:
            cfg = bot.statuses
        else:
            if type == SCHEDULER:
                cfg = bot.schedulers
            else:
                Fatal('%s is an invalid type.' % type)
    #be sure we got a bot
    if bot == None:
        Fatal("Bot %s does not exist." % bot)
    for cls in cfg:
        if int(cls.order) == int(order):
            Warn('Deleted Build Config %s' % cls)
            Orm().session.delete(cls)
    Orm().session.commit()


def showclasses(type, bot):
    """
    format and return a list of classes for a bot

    @param type: the type of class to print
    @type type: str
    @param bot: the bot to print classes for
    @type bot: BuildBot
    """
    if type == STEP:
        cfg = bot.steps
    else:
        if type == STATUS:
            cfg = bot.statuses
        else:
            if type == SCHEDULER:
                cfg = bot.schedulers
            else:
                Fatal('%s is an invalid type.' % type)
    fmt = ''
    for cls in cfg:
        fmt += "    %s: %s\n" % (
            Colors().format_string(cls.order, "blue"),
            Colors().format_string(cls.module, "blue"))
        cls.params.reverse()
        for param in cls.params:
            fmt += "\t%s: %s\n" % (
                Colors().format_string(param.name, "white"),
                param.value)
    return fmt


def generate_httpd():
    """
    generate an httpd conf.d file for loki web and
    proxy passing master web interfaces
    """
    # Set up the config parser
    cp = ConfigParser.ConfigParser()
    setattr(cp, 'file_name', CONFIGFILE)
    cp.read(cp.file_name)

    web = dict(cp.items('web'))
    if 'enabled' not in web:
        web['enabled'] = 'False'
    if 'prefix' not in web:
        web['prefix'] = ''

    if web['enabled'] == 'True':
        masters = loki.bot.get(type=MASTER)

        httpd = 'RewriteEngine on\n'
        for master in masters:
            httpd += 'ProxyPass %s/%s/\thttp://%s:%s/\n' \
                    % (web['prefix'],
                       master.name,
                       master.server,
                       master.web_port)
        if web['prefix'] != '':
            httpd += 'RewriteRule ^%s$ %s/ [R,L]\n' % \
                     (web['prefix'], web['prefix'])
        httpd += '<Location "%s/">\n' % web['prefix']
        httpd += '    SetHandler python-program\n'
        httpd += '    PythonHandler django.core.handlers.modpython\n'
        httpd += '    SetEnv DJANGO_SETTINGS_MODULE loki.web.settings\n'
        if web['prefix'] != '':
            httpd += '    PythonOption django.root %s\n' % web['prefix']
        httpd += '    PythonDebug on\n'
        httpd += '</Location>\n\n'
        if web['prefix'] != '':
            httpd += 'RewriteRule ^/json(.*) %s/json$1 [R,L]\n' % web['prefix']
        httpd += 'Alias /yui /usr/lib/python2.4/site-packages/loki/web/yui\n\n'

        print httpd
        return httpd


def _format_class(cls):
    """
    format and return a string represenation of a class

    @param cls: the class to format
    @type cls: ('cls.path.name', (req,params), { 'opt' : 'default' } )
    """
    fmt = "%s(" % cls[0]
    params = []
    params.extend(cls[1])
    for opt in cls[2]:
        params.append("%s=%s" % (opt, cls[2][opt]))
    fmt += ', '.join(params)
    fmt += ")"
    return fmt
