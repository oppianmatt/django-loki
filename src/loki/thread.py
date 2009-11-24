# Copyright 2009, Red Hat, Inc
# Dan 'Rezak' Radez <dradez@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
All threaded objects.
"""

import threading


class BuildBotStart(threading.Thread):
    """
    Executes buildbot's start command it a new thread.
    """

    def __init__(self, subOptions, *args, **kwargs):
        """
        Creates an instance of buildBotStart
        """
        self.subOptions = subOptions
        # init the thread
        threading.Thread.__init__(self, *args, **kwargs)
        self.setDaemon(True)

    def run(self):
        """
        Does the hard work.
        """
        sleep(5)
        #import buildbot.scripts.startup
        #buildbot.scripts.startup.start(self.subOptions)
        return True
