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
Custom Option Types for optparse.
More could be added for now there is just the unicode
type to automagically convert all our strings into unicode
"""

from copy import copy
from optparse import Option, OptionValueError


def check_unicode(option, opt, value):
    try:
        return unicode(value)
    except ValueError:
        raise OptionValueError(
            "option %s: invalid unicode value: %r" % (opt, value))


class Unicode(Option):
    TYPES = Option.TYPES + ("unicode", )
    TYPE_CHECKER = copy(Option.TYPE_CHECKER)
    TYPE_CHECKER["unicode"] = check_unicode
