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
    Column('value', types.Unicode(100)))

servers = Table('servers', metadata,
    Column('id', types.Integer, primary_key=True),
    Column('name', types.Unicode(100)),
    Column('profile', types.Unicode(50)),
    Column('basedir', types.Unicode(50)),
    Column('type', types.Unicode(10)),
    Column('comment', types.Unicode(100)),
    Column('virtserver_id', types.Integer, ForeignKey('servers.id')))

bots = Table('buildbots', metadata,
    Column('id', types.Integer, primary_key=True),
    Column('server_id', types.Integer, ForeignKey('servers.id')),
    Column('name', types.Unicode(50)),
    Column('type', types.Unicode(10)),
    Column('comment', types.Unicode(100)))

masters = Table('masters', metadata,
    Column('id', types.Integer, ForeignKey('buildbots.id'), primary_key=True),
    Column('config_source', types.Unicode(100)),
    Column('slave_passwd', types.Unicode(10)),
    Column('slave_port', types.Integer),
    Column('web_port', types.Integer))

slaves = Table('slaves', metadata,
    Column('id', types.Integer, ForeignKey('buildbots.id'), primary_key=True),
    Column('master_id', types.Integer, ForeignKey('masters.id')))

configs = Table('configs', metadata,
    Column('id', types.Integer, primary_key=True),
    Column('bot_id', types.Integer, ForeignKey('buildbots.id')),
    Column('type', types.Unicode(10)),
    Column('module', types.Unicode(100)),
    Column('order', types.Integer))

params = Table('params', metadata,
    Column('id', types.Integer, primary_key=True),
    Column('configs_id', types.Integer, ForeignKey('configs.id')),
    Column('name', types.Unicode(50)),
    Column('value', types.Unicode(50)))


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

    def __init__(self, name, profile, basedir, type, comment = u''):
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

    def __init__(self, name, comment = u''):
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

    def __init__(self, name, comment = u'', config_source=u''):
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


class BuildConfig(object):
    """
    BuildConfig class
    """

    def __init__(self, module, order):
        """
        BuildConfig class

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


class BuildStep(BuildConfig):
    """
    BuildStep class
    """
    pass


class BuildStatus(BuildConfig):
    """
    BuildStep class
    """
    pass


class BuildScheduler(BuildConfig):
    """
    BuildStep class
    """
    pass


class BuildParam(object):
    """
    BuildParam class
    """

    def __init__(self, name, value):
        """
        BuildParam class

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
                                  primaryjoin=servers.c.id==bots.c.server_id),
                     'virtserver': relation(Server, remote_side=servers.c.id)}
master_properties = {'slaves': relation(BuildSlave, backref='master',
                               primaryjoin=masters.c.id==slaves.c.master_id),
                     'schedulers': relation(BuildScheduler, backref='master',
                               primaryjoin=bots.c.id==configs.c.bot_id,
                               cascade='all,delete-orphan'),
                     'statuses': relation(BuildStatus, backref='master',
                               primaryjoin=bots.c.id==configs.c.bot_id,
                               cascade='all,delete-orphan')}
slave_properties = {'steps': relation(BuildStep, backref='slave',
                            primaryjoin=bots.c.id==configs.c.bot_id,
                            order_by=configs.c.order,
                            cascade='all,delete-orphan')}
step_properties = {'params': relation(BuildParam, backref='step',
                             primaryjoin=configs.c.id==params.c.configs_id)}
status_properties = {'params': relation(BuildParam, backref='status',
                               primaryjoin=configs.c.id==params.c.configs_id)}
scheduler_properties = {'params': relation(BuildParam, backref='scheduler',
                        primaryjoin=configs.c.id==params.c.configs_id)}


ConfigMapper = mapper(Config, config)
ServerMapper = mapper(
        Server,
        servers,
        properties = server_properties)#, allow_column_override=True)
BuildBotMapper = mapper(
        BuildBot,
        bots,
        polymorphic_on = bots.c.type,
        polymorphic_identity = u'bot')
MasterMapper = mapper(
        BuildMaster,
        masters,
        inherits = BuildBot,
        polymorphic_identity = u'master',
        properties = master_properties)
SlaveMapper = mapper(
        BuildSlave,
        slaves,
        inherits = BuildBot,
        polymorphic_identity = u'slave',
        properties = slave_properties)
ConfigsMapper = mapper(
        BuildConfig,
        configs,
        polymorphic_on = configs.c.type,
        polymorphic_identity = u'config')
StepMapper = mapper(
        BuildStep,
        configs,
        inherits = BuildConfig,
        polymorphic_identity = u'step',
        properties = step_properties)
StatusMapper = mapper(
        BuildStatus,
        configs,
        inherits = BuildConfig,
        polymorphic_identity = u'status',
        properties = status_properties)
SchedulerMapper = mapper(
        BuildScheduler,
        configs,
        inherits = BuildConfig,
        polymorphic_identity = u'scheduler',
        properties = scheduler_properties)
ParamMapper = mapper(BuildParam, params)
