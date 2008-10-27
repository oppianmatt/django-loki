# Copyright 2009, Red Hat, Inc
# Dan Radez <dradez@redhat.com>
# Steve 'Ashcrow' Milner <smilner@redhat.com>
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

import types


def check_func(value):
    """
    Check the return value of func and throw any exceptions that are found

    @param value: Return value of func call
    """
    if type(value) == types.ListType and \
       len(value) and \
       value[0] == 'REMOTE_ERROR':
        raise(Exception(('\n'.join(value))))
    return value
