# Copyright 2008, Red Hat, Inc
# Scott Henson <shenson@redhat.com>
# Dan Radez <dradez@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
BuildDB Setup Tasks

Used to initialize any resources that BuildDB uses
"""

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import engine_from_config
from loki.Common import *
from loki.model import metadata, Config
import ConfigParser


def createEngine(cp, echo=False):
    """Call me at the beginning of the application.
       'bind' is a SQLAlchemy engine or connection, as returned by
       sa.create_engine, sa.engine_from_config, or engine.connect().

    FIXME: Functions should not be mixed case.
    """
    config = {}
    for key in cp.options('app:main'):
        config[key] = cp.get('app:main', key)
    sa_engine = engine_from_config(config, 'sqlalchemy.', echo=echo)
    return sa_engine


def createSession(cp, engine=None):
    """
    Initialize the ORM Session

    FIXME: Functions should not be mixed case.

    @param cp: Config Parser containing configs for SA
    @type cp: ConfgiParser
    """
    if engine is None:
        sa_engine = createEngine(cp)
    else:
        sa_engine = engine
    Session = scoped_session( \
        sessionmaker(transactional=True, autoflush=True, bind=sa_engine))
    return Session


def getConfig(config=CONFIGFILE):
    """
    Get the config parser object
    FIXME: Functions should not be mixed case.
    """
    # Set up the config parser
    cp = ConfigParser.ConfigParser()
    setattr(cp, 'file_name', config)
    cp.read(cp.file_name)
    return cp


def validateModel(Session, show_warn=True):
    """
    TODO: Document me!
    FIXME: Functions should not be mixed case.
    """
    try:
        check_db = Session.query(Config).filter_by(name=u'dbversion').first()
    except:
        check_db = Config('dbversion', '0')
    if check_db.value == DBVERSION:
        return check_db.value

    if getattr(check_db, 'value') == '0' and show_warn:
        Warn("Database schema doesn't seem to exist. \
              \n run loki store setup if that's not what you're doing")
    if getattr(check_db, 'value') != '0' and show_warn:
        Warn("Database schema needs to be upgraded. \
              \n run loki store upgrade if that's not what you're doing")
    return check_db.value


def createSchema():
    """
    TODO: Document me!
    FIXME: Functions should not be mixed case.
    """
    # Set up the config parser
    cp = ConfigParser.ConfigParser()
    setattr(cp, 'file_name', CONFIGFILE)
    cp.read(cp.file_name)

    sa_engine = createEngine(cp)
    Session = createSession(None, sa_engine)
    if validateModel(Session, show_warn=False) != '0':
        Fatal('Database Schema already exists')


    metadata.create_all(bind=sa_engine)

    config = Config(u'dbversion', unicode(DBVERSION))
    Session.save(config)
    Session.commit()

    if validateModel(Session, show_warn=False) == '0':
        Fatal('Database Schema Setup Failed')
    else:
        Success('Database Schema Setup Completed Successfully')


def updateSchema():
    """
    TODO: Document me!
    FIXME: Functions should not be mixed case.
    """
    # Set up the config parser
    cp = ConfigParser.ConfigParser()
    setattr(cp, 'file_name', CONFIGFILE)
    cp.read(cp.file_name)

    sa_engine = createEngine(cp)
    Session = createSession(None, sa_engine)
    model_v = validateModel(Session, show_warn=False)
    if model_v == '1':
        metadata.tables['configs'].create(sa_engine, True)
        metadata.tables['params'].create(sa_engine, True)
        db_v = Session.query(Config).filter_by(name=u'dbversion').first()
        db_v.value = u'2'
        Session.commit()
        Success('Schema update 1 -> 2 Complete')
    if model_v == '2':
        Success('Your Scheme is up-to-date')
