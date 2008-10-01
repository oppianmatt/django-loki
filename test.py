#!/usr/bin/env python

from loki.model import Server, BuildBot, BuildMaster, BuildSlave, metadata
from loki.ModelTasks import listitems
from loki.SetupTasks import getConfig, getSession, getEngine

conf = getConfig('dev.conf')
sa_engine = getEngine(conf, echo=True)

#metadata.create_all(bind=sa_engine)

Session = getSession(conf, engine = sa_engine)
