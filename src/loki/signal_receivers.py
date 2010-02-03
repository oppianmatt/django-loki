# Copyright 2008-2010, Red Hat, Inc
# Dan Radez <dradez@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import os

from loki.settings import *
from loki.helpers import generate_master_cfg
from loki.model_helpers import build_bot_run
from buildbot.scripts.runner import Options, createMaster


def post_save_bot(sender, instance, created, **kwargs):
    """
    post save call back

    :Parameters:
       - sender: the sending object.
       - instance: instance of the object being saved
       - created: if a new record was created
       - kwargs: any keyword arguments
    """
    # create bot if new
    if created:
        build_bot_run(instance.buildbot_create)

    # update the config file
    instance.generate_cfg()

    if hasattr(instance, 'master'):
        instance.master.generate_cfg()
        if instance.master.alive:
            build_bot_run(['sighup', instance.master.path])

    if instance.alive:
        build_bot_run(['sighup', instance.path])


def post_delete_bot(sender, instance, **kwargs):
    """
    post delete call back

    :Parameters:
       - sender: the sending object.
       - instance: instance of the object being saved
       - kwargs: any keyword arguments
    """
    # stop bot
    bot_path = os.path.join(BUILDBOT_MASTERS, instance.name)
    if instance.alive:
        build_bot_run(['stop', instance.path])

    # delete bot
    if os.path.isdir(instance.path):
        import shutil
        shutil.rmtree(instance.path)
