# -*- coding: utf-8 -*-
"""
 Copyright 2005 Spike^ekipS <spikeekips@gmail.com>

    This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import re
import os
import sys

from django.core.management.base import BaseCommand

__author__ = "Spike^ekipS <spikeekips@gmail.com>,\
 Dan Radez <dradez@redhat.com>"
__version__= "0.1"
__nonsense__ = ""


class Command(BaseCommand):
    help = "Starts a lightweight Web server for development."
    args = '[optional port numbers, ex: 8000,8001,8002 default: 8001]'

    def handle(self, action=None, ports='8001', *args, **options):
        path = re.compile("/%s$" % re.escape(
                               os.path.basename(__file__))).sub("", __file__)
        ports = ports.split(',')

        if not action:
            print "Usage: ./manage.py twistd {start|stop|restart} [ports]"
            sys.exit()

        def run(cmd):
            os.system(cmd)

        prog_stop = \
        """kill -9 `cat twistd/%(port)s.pid`"""

        prog_stand = \
        """ENV_WWW_PORT=%(port)s twistd -ny %(path)s/twistd_run.py\
 --pidfile=twistd/%(port)s.pid"""

        prog_start = \
        """ENV_WWW_PORT=%(port)s twistd -y %(path)s/twistd_run.py\
 --pidfile=twistd/%(port)s.pid --logfile=twistd/%(port)s.log"""

        os.putenv("DJANGO_SETTINGS_MODULE", "settings")

        #for i in dir(conf):
        #    if not i.startswith("__"):
        #        v = getattr(conf, i)
        #        if v is None:
        #            v = ""
        #        else:
        #            v = str(v)
        #        os.putenv("DOT_%s" % i, v)

        if action == "stand":
            print "Standing"
            for i in ports:
                run(prog_stand % {"port": i, "path": path, })
                break
        elif action == "start":
            print "Starting"
            for i in ports:
                run(prog_start % {"port": i, "path": path, })
        elif action == "stop":
            print "Stopping"
            for i in ports:
                run(prog_stop % {"port": i, "path": path, })
        elif action == "restart":
            print "Restarting"
            for i in ports:
                run(prog_stop % {"port": i, "path": path, })
                run(prog_start % {"port": i, "path": path, })
        else:
            print "Usage: %s {start|stop|restart} [ports]" % sys.argv[0]
            sys.exit()
