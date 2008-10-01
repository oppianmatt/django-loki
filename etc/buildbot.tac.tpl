
from twisted.application import service
from buildbot.slave.bot import BuildSlave

basedir = r'%(basedir)s'
buildmaster_host = '%(masterhost)s'
port = %(slaveport)s
slavename = '%(slavename)s'
passwd = '%(slavepasswd)s'
keepalive = 600
usepty = 1
umask = None

application = service.Application('buildslave')
s = BuildSlave(buildmaster_host, port, slavename, passwd, basedir,
               keepalive, usepty, umask=umask)
s.setServiceParent(application)

