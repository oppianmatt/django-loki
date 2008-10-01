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
BuildDB Model

Contains: Server, Master, Slave
"""


from sqlalchemy import Column, MetaData, Table, types, ForeignKey
from sqlalchemy.orm import mapper, scoped_session, sessionmaker, relation

metadata = MetaData()

config = Table('config', metadata,
    Column('name', types.Unicode(100), primary_key=True),
    Column('value', types.Unicode))

servers = Table('servers', metadata,
    Column('id', types.Integer, primary_key=True),
    Column('name', types.Unicode),
    Column('profile', types.Unicode),
    Column('basedir', types.Unicode),
    Column('type', types.Unicode),
    Column('comment', types.Unicode))

bots = Table('buildbots', metadata,
    Column('id', types.Integer, primary_key=True),
    Column('server_id', types.Integer, ForeignKey('servers.id')),
    Column('name', types.Unicode),
    Column('type', types.Unicode),
    Column('comment', types.Unicode))

masters = Table('masters', metadata,
    Column('id', types.Integer, ForeignKey('buildbots.id'), primary_key=True),
    Column('config_source', types.Unicode),
    Column('slave_passwd', types.Unicode),
    Column('slave_port', types.Integer),
    Column('web_port', types.Integer))

slaves = Table('slaves', metadata,
    Column('id', types.Integer, ForeignKey('buildbots.id'), primary_key=True),
    Column('master_id', types.Integer, ForeignKey('masters.id')))

steps = Table('steps', metadata,
    Column('id', types.Integer, primary_key=True),
    Column('slave_id', types.Integer, ForeignKey('slaves.id')),
    Column('module', types.Unicode),
    Column('order', types.Integer))

params = Table('params', metadata,
    Column('id', types.Integer, primary_key=True),
    Column('step_id', types.Integer, ForeignKey('steps.id')),
    Column('name', types.Unicode),
    Column('value', types.Unicode))

class Config(object):
    """
    Config Class
    """

    def __init__(self, name, value):
        """
        Config

        @param name: name of the config param
        @type name: string

        @param value: value of the config param
        @type value: string
        """
        self.name = name
        self.value = value

    def __str__(self):
        """
        __str__
        Returns a string representation of the object
        """
        return self.name


class Server(object):
    """
    Server class
    """

    def __init__(self, name, profile, basedir, type, comment = ''):
        """
        Server

        Build Bot Server

        @param name: hostname of the server
        @type name: string

        @param profile: system profile identifier
        @type profile: string

        @param basedir: the base directory where all bots will live
        @type basedir: string

        @param type: type of allowed bots, generally master or slave
        @type type: string

        @param comment: a comment about the host
        @type comment: string
        """
        self.name = name
        self.profile = profile
        self.basedir = basedir
        self.type = type
        self.comment = comment

    def __str__(self):
        """
        __str__
        Returns a string representation of the object
        """
        return self.name


class BuildBot(object):
    """
    Buildbot class
    Could be a master or a slave
    """

    def __init__(self, name, comment = ''):
        """
        BuildBot class

        @param name: name of the bot
        @type name: string

        @param comment: a comment about the bot
        @type comment: string
        """
        self.name = name
        self.comment = comment

    def __str__(self):
        """
        __str__
        Returns a string representation of the object
        """
        return self.name


class BuildMaster(BuildBot):
    """
    BuildMaster class
    """

    def __init__(self, name, comment = '', config_source=''):
        """
        BuildBot class

        @param name: name of the bot
        @type name: string

        @param comment: a comment about the bot
        @type comment: string
        """
        self.config_source = config_source
        BuildBot.__init__(self, name, comment = comment)


class BuildSlave(BuildBot):
    """
    BuildSlave class
    """
    pass


class BuildStep(object):
    """
    BuildStep class
    """
    def __init__(self, module, order):
        """
        BuildiStep class

        @param module: name of the steps module
        @type name: string

        @param comment: order to execute the step
        @type comment: integer
        """
        self.module = module
        self.order = order

    def __str__(self):
        """
        __str__
        Returns a string representation of the object
        """
        return self.module


class BuildStepParam(object):
    """
    BuildStepParam class
    """
    def __init__(self, module, order):
        """
        BuildStepParam class

        @param name: name of param
        @type name: string

        @param value: value of the param
        @type value: string
        """
        self.name = name
        self.value = value

    def __str__(self):
        """
        __str__
        Returns a string representation of the object
        """
        return self.name



server_properties = {'buildbots': relation(BuildBot, backref='server',
                                  primaryjoin=servers.c.id==bots.c.server_id)}
master_properties = {'slaves': relation(BuildSlave, backref='master',
                               primaryjoin=masters.c.id==slaves.c.master_id)}
slave_properties = {'steps': relation(BuildStep, backref='slave',
                            primaryjoin=slaves.c.id==steps.c.slave_id)}
step_properties = {'params': relation(BuildStepParam, backref='step',
                                   primaryjoin=steps.c.id==params.c.step_id)}


ConfigMapper = mapper(Config, config)
ServerMapper = mapper(Server, servers, properties = server_properties)
BuildBotMapper = mapper(
        BuildBot,
        bots,
        polymorphic_on = bots.c.type,
        polymorphic_identity = 'bot')
MasterMapper = mapper(
        BuildMaster,
        masters,
        inherits = BuildBot,
        polymorphic_identity = 'master',
        properties = master_properties)
SlaveMapper = mapper(
        BuildSlave,
        slaves,
        inherits = BuildBot,
        polymorphic_identity = 'slave',
        properties = slave_properties)
StepMapper = mapper(
        BuildStep,
        steps,
        properties = step_properties)
ParamMapper = mapper(BuildStepParam, params)
