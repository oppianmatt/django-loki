# Copyright 2008, Red Hat, Inc
# Dan Radez <dradez@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
TODO: Document me!
"""

import loki.store

from director import Action
from director.decorators import general_help


class Store(Action):
    """
    loki server action.
    """

    description_txt = "Manages Database Store"

    @general_help("Setup the Database Schema.", examples=['loki store setup'])
    def setup(self):
        """
        Setup the Database Schema.
        """
        loki.store.createSchema()

    @general_help("Setup the Database Schema.", examples=['loki store update'])
    def update(self):
        """
        Update the Database Schema.
        """
        loki.store.updateSchema()
