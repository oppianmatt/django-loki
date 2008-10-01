# Copyright 2008, Red Hat, Inc
# Steve 'Ashcrow' Milner <smilner@redhat.com>
# Scott Henson <shenson@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Log - Responsible for cool output
"""

import sys

from loki.Colors import Colors

color = Colors()


def Fatal(err, ErrorCode=-1):
    """
    Print the error and exit

    @param err: Error message to print
    @type err: string
    """

    err = color.format_string(err, 'red')
    sys.stderr.write(err+'\n')
    sys.exit(ErrorCode)


def Success(msg):
    """
    Print the success message and exit

    @param msg: The message to print out
    @type msg: string
    """

    msg = color.format_string(msg, 'green')
    sys.stdout.write(msg+'\n')
    sys.exit(0)


def Info(msg):
    """
    Print the information and returns

    @param msg: The message to print out
    @type msg: string
    """
    msg = color.format_string(msg, 'blue')
    print msg

    return True


def Warn(msg):
    """
    Print the warning and returns

    @param msg: The message to print out
    @type msg: string
    """
    msg = color.format_string(msg, 'yellow')
    print msg

    return True


def Error(msg):
    """
    Print the error and returns

    @param msg: The message to print out
    @type msg: string
    """
    msg = color.format_string(msg, 'red')
    print msg

    return True


def Log(msg):
    """
    Print the Log line and returns

    @param msg: The message to print out
    @type msg: string
    """
    print msg

    return True
