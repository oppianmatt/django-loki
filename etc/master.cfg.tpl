# -*- python -*-
# ex: set syntax=python:

# This is a sample buildmaster config file. It must be installed as
# 'master.cfg' in your buildmaster's base directory (although the filename
# can be changed with the --basedir option to 'mktap buildbot master').

# It has one job: define a dictionary named BuildmasterConfig. This
# dictionary has a variety of keys to control different aspects of the
# buildmaster. They are documented in docs/config.xhtml .


# This is the dictionary that the buildmaster pays attention to. We also use
# a shorter alias to save typing.
c = BuildmasterConfig = {}

####### BUILDSLAVES

# the 'slaves' list defines the set of allowable buildslaves. Each element is
# a tuple of bot-name and bot-password. These correspond to values given to
# the buildslave's mktap invocation.
from buildbot.buildslave import BuildSlave
c['slaves'] = [%(buildslaves)s]

# to limit to two concurrent builds on a slave, use
#  c['slaves'] = [BuildSlave("bot1name", "bot1passwd", max_builds=2)]


# 'slavePortnum' defines the TCP port to listen on. This must match the value
# configured into the buildslaves (with their --master option)

c['slavePortnum'] = %(slaveport)s

####### CHANGESOURCES

# the 'change_source' setting tells the buildmaster how it should find out
# about source code changes. Any class which implements IChangeSource can be
# put here: there are several in buildbot/changes/*.py to choose from.

from buildbot.changes.pb import PBChangeSource
c['change_source'] = PBChangeSource()

# For example, if you had CVSToys installed on your repository, and your
# CVSROOT/freshcfg file had an entry like this:
#pb = ConfigurationSet([
#    (None, None, None, PBService(userpass=('foo', 'bar'), port=4519)),
#    ])

# then you could use the following buildmaster Change Source to subscribe to
# the FreshCVS daemon and be notified on every commit:
#
#from buildbot.changes.freshcvs import FreshCVSSource
#fc_source = FreshCVSSource("cvs.example.com", 4519, "foo", "bar")
#c['change_source'] = fc_source

# or, use a PBChangeSource, and then have your repository's commit script run
# 'buildbot sendchange', or use contrib/svn_buildbot.py, or
# contrib/arch_buildbot.py :
#
#from buildbot.changes.pb import PBChangeSource
#c['change_source'] = PBChangeSource()


####### SCHEDULERS

## configure the Schedulers

#from buildbot.scheduler import Scheduler
c['schedulers'] = []
#c['schedulers'].append(Scheduler(name="all", branch=None,
#                                 treeStableTimer=2*60,
#                                 builderNames=["buildbot-full"]))

%(schedulers)s


####### BUILDERS

# the 'builders' list defines the Builders. Each one is configured with a
# dictionary, using the following keys:
#  name (required): the name used to describe this bilder
#  slavename (required): which slave to use, must appear in c['bots']
#  builddir (required): which subdirectory to run the builder in
#  factory (required): a BuildFactory to define how the build is run
#  periodicBuildTime (optional): if set, force a build every N seconds

# buildbot/process/factory.py provides several BuildFactory classes you can
# start with, which implement build processes for common targets (GNU
# autoconf projects, CPAN perl modules, etc). The factory.BuildFactory is the
# base class, and is configured with a series of BuildSteps. When the build
# is run, the appropriate buildslave is told to execute each Step in turn.

# the first BuildStep is typically responsible for obtaining a copy of the
# sources. There are source-obtaining Steps in buildbot/steps/source.py for
# CVS, SVN, and others.

from buildbot.process import factory
%(imports)s

%(factories)s

c['builders'] = [%(builders)s]

####### STATUS TARGETS

# 'status' is a list of Status Targets. The results of each build will be
# pushed to these targets. buildbot/status/*.py has a variety to choose from,
# including web pages, email senders, and IRC bots.

c['status'] = []

from buildbot.status import html
c['status'].append(html.WebStatus(http_port=%(webport)s))

# from buildbot.status import mail
# c['status'].append(mail.MailNotifier(fromaddr="buildbot@localhost",
#                                      extraRecipients=["builds@example.com"],
#                                      sendToInterestedUsers=False))
#
# from buildbot.status import words
# c['status'].append(words.IRC(host="irc.example.com", nick="bb",
#                              channels=["#example"]))
#
# from buildbot.status import client
# c['status'].append(client.PBListener(9988))

%(statuses)s


####### DEBUGGING OPTIONS

# if you set 'debugPassword', then you can connect to the buildmaster with
# the diagnostic tool in contrib/debugclient.py . From this tool, you can
# manually force builds and inject changes, which may be useful for testing
# your buildmaster without actually commiting changes to your repository (or
# before you have a functioning 'sources' set up). The debug tool uses the
# same port number as the slaves do: 'slavePortnum'.

#c['debugPassword'] = "debugpassword"

# if you set 'manhole', you can ssh into the buildmaster and get an
# interactive python shell, which may be useful for debugging buildbot
# internals. It is probably only useful for buildbot developers. You can also
# use an authorized_keys file, or plain telnet.
#from buildbot import manhole
#c['manhole'] = manhole.PasswordManhole("tcp:9999:interface=127.0.0.1",
#                                       "admin", "password")


####### PROJECT IDENTITY

# the 'projectName' string will be used to describe the project that this
# buildbot is working on. For example, it is used as the title of the
# waterfall HTML page. The 'projectURL' string will be used to provide a link
# from buildbot HTML pages to your project's home page.

c['projectName'] = "%(botname)s"
c['projectURL'] = "http://buildbot.sourceforge.net/"

# the 'buildbotURL' string should point to the location where the buildbot's
# internal web server (usually the html.Waterfall page) is visible. This
# typically uses the port number set in the Waterfall 'status' entry, but
# with an externally-visible host name which the buildbot cannot figure out
# without some help.

c['buildbotURL'] = "http://%(webhost)s:%(webport)s/"
