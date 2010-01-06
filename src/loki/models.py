# Copyright 2008, Red Hat, Inc
# Dan Radez <dradez@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import os

from django.db import models
from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from loki import build_bot_run
from loki.settings import *
from loki.bind_administration import bind_administration
from loki.signal_receivers import post_save_bot
from loki.signal_receivers import post_delete_bot
from loki.model_helpers import _template
from loki.model_helpers import _generate_class

# these are for filters later
# need to try catch them because syncdb
# will fail because it hasn't created the content_type table
# but needs it to ge these types
try:
    status_content_type = ContentType.objects.get(
                            app_label="loki", model="status")
    step_content_type = ContentType.objects.get(
                            app_label="loki", model="step")
    scheduler_content_type = ContentType.objects.get(
                            app_label="loki", model="scheduler")
except:
    status_content_type = step_content_type = scheduler_content_type = 0


class Host(models.Model):
    hostname = models.CharField(max_length=200, unique=True)

    def __unicode__(self):
        return self.hostname


class Bot(models.Model):

    class Meta(object):
        """
        Meta attributes for Package.
        """
        abstract = True

    def buildbot_run(self, action):
        build_bot_run([action, self.path])

    def pid(self):
        pid = 0
        pid_file = os.path.join(self.path, 'twistd.pid')
        if os.path.exists(pid_file):
            pid_fd = open(pid_file, 'r')
            pid = pid_fd.read()
            pid_fd.close()
        return int(pid)

    alive = property(lambda self: self.pid() and \
                os.path.exists(os.path.join('/proc', str(self.pid()))))


class Master(Bot):
    host = models.ForeignKey(Host, related_name='masters')
    name = models.SlugField(max_length=25)
    slave_port = models.IntegerField(max_length=5)
    web_port = models.IntegerField(max_length=5)

    path = property(lambda self: os.path.join(BUILDBOT_MASTERS, self.name))
    buildbot_create = property(lambda self: ['create-master', self.path])

    def __unicode__(self):
        return self.name

    def generate_cfg(self):
        buildslaves = ''
        factories = ''
        statuses = ''
        schedulers = ''
        imports = ''
        builders = []
        modules = []
        ct = 1

        for slave in self.slaves.all():
            #generate the BuildSlave objects
            buildslaves += "\n    BuildSlave('%s', '%s')," % \
                (slave.name, slave.passwd)
            #create buildfactory
            b = '%s_%s' % (self.name, slave.name)
            b = b.replace('-', '__dash__')
            factories += '%s = factory.BuildFactory()\n' % b
            for step in slave.steps.all():
                if step.type not in modules:
                    modules.append(step.type)
                factories += "%s.addStep(%s)\n" % (b,
                                      _generate_class(step))
            #create builder from factory
            factories += "b%s = {'name': '%s',\n" % (ct, slave.name)
            factories += "      'slavename': '%s',\n" % slave.name
            factories += "      'builddir': '%s',\n" % slave.name
            factories += "      'factory': %s, }\n\n" % b
            # remember the builders
            builders.append('b%s' % ct)
            ct += 1

        #generate statuses
        #for status in self.statuses:
        #    statuses += "c['status'].append(%s)" % _generate_class(status)
        #    modules.append(status.module)

        #restructure the imports
        for x in modules:
            imports += 'from %s import %s\n' % (
                        '.'.join(x.module.split('.')[:-1]),
                         x.module.split('.')[-1])

        #generate the template
        t = _template('loki/master.cfg.tpl',
                botname=self.name,
                webhost=self.host,
                webport=self.web_port,
                slaveport=self.slave_port,
                buildslaves=buildslaves,
                imports=imports,
                factories=factories,
                builders=','.join(builders),
                statuses=statuses,
                schedulers=schedulers)
        cfg = open(os.path.join(self.path, 'master.cfg'), 'w')
        cfg.write(t)
        cfg.close()


class Slave(Bot):
    host = models.ForeignKey(Host, related_name='slaves')
    master = models.ForeignKey(Master, related_name='slaves')
    name = models.SlugField(max_length=25)
    passwd = models.SlugField(max_length=25)

    path = property(lambda self: os.path.join(BUILDBOT_SLAVES, self.name))
    buildbot_create = property(lambda self: ['create-slave', self.path,
                        '%s:%s' % (self.master.host, self.master.slave_port),
                        self.name, self.passwd])

    def __unicode__(self):
        return self.name

    def generate_cfg(self):
        t = _template('loki/slave.cfg.tpl',
                basedir=os.path.abspath(self.path),
                masterhost=self.master.host,
                slavename=self.name,
                slaveport=self.master.slave_port,
                slavepasswd=self.passwd)
        cfg = open(os.path.join(self.path, 'buildbot.tac'), 'w')
        cfg.write(t)
        cfg.close()


class Config(models.Model):
    """
    A definition of what configs are available
    """
    name = models.CharField(max_length=25)
    module = models.CharField(max_length=200, unique=True)
    content_type = models.ForeignKey(ContentType)

    def __unicode__(self):
        return self.name


class ConfigParam(models.Model):
    name = models.CharField(max_length=25)
    type = models.ForeignKey(Config, related_name='params')
    default = models.CharField(max_length=200, blank=True, null=True)
    required = models.BooleanField(default=False)

    def __unicode__(self):
        req = ''
        if self.required:
            req = ' *'
        return '%s :: %s%s' % (self.type, self.name, req)


class Status(models.Model):
    master = models.ForeignKey(Master, related_name='status')
    type = models.ForeignKey(Config, related_name='status_type',
                             limit_choices_to={
                                 'content_type': status_content_type})

    def __unicode__(self):
        return '%s :: %s' % (self.master, self.type)


class StatusParam(models.Model):
    status = models.ForeignKey(Status, related_name='params')
    type = models.ForeignKey(ConfigParam)
    val = models.CharField(max_length=200)

    def __unicode__(self):
        return '%s :: %s' % (self.status, self.val)


class Step(models.Model):
    slave = models.ForeignKey(Slave, related_name='steps')
    type = models.ForeignKey(Config, related_name='step_type',
                             limit_choices_to={
                                 'content_type': step_content_type})
    num = models.IntegerField()

    def __unicode__(self):
        return '%s :: %s' % (self.slave, self.type)


class StepParam(models.Model):
    step = models.ForeignKey(Step, related_name='params')
    type = models.ForeignKey(ConfigParam)
    val = models.CharField(max_length=200)

    def __unicode__(self):
        return '%s :: %s' % (self.step, self.val)


class Scheduler(models.Model):
    slave = models.ForeignKey(Slave, related_name='schedulers')
    type = models.ForeignKey(Config, related_name='scheduler_type',
                             limit_choices_to={
                                 'content_type': scheduler_content_type})

    def __unicode__(self):
        return '%s :: %s' % (self.slave, self.type)


class SchedulerParam(models.Model):
    scheduler = models.ForeignKey(Scheduler, related_name='params')
    type = models.ForeignKey(ConfigParam)
    val = models.CharField(max_length=200)

    def __unicode__(self):
        return '%s :: %s' % (self.scheduler, self.val)

bind_administration('loki.models', 'loki.admin')
post_save.connect(post_save_bot, sender=Master)
post_delete.connect(post_delete_bot, sender=Master)
post_save.connect(post_save_bot, sender=Slave)
post_delete.connect(post_delete_bot, sender=Slave)
