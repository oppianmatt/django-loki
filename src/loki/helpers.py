# Copyright 2008-2010, Red Hat, Inc
# Dan Radez <dradez@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

def generate_master_cfg(master):

    buildslaves = ''
    builders = []
    factories = ''
    modules = []
    statuses = ''
    schedulers = ''
    ct = 1
    for slave in master.slaves:
        #remebers the slaves
        buildslaves += "\n    BuildSlave('%s', '%s')," % \
            (slave.name, slave.passwd)
        #create buildfactory
        b = '%s_%s' % (master.name, slave.name)
        factories += '%s = factory.BuildFactory()\n' % b
        for step in slave.steps:
            if step.module not in modules:
                modules.append(step.module)
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
    for status in master.statuses:
        statuses += "c['status'].append(%s)" % _generate_class(status)
        modules.append(status.module)

    #restructure the imports
    imports = ''
    for x in modules:
        imports += 'from %s import %s\n' % (
                    '.'.join(x.split('.')[:-1]),
                    x.split('.')[-1])

    #generate the template
    t = _template('master.cfg.tpl',
               botname=master.name,
               webhost=master.server,
               webport=master.web_port,
               slaveport=master.slave_port,
               buildslaves=buildslaves,
               imports=imports,
               factories=factories,
               builders=','.join(builders),
               statuses=statuses,
               schedulers=schedulers)
