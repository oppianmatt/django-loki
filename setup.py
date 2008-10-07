#!/usr/bin/env python
#
# Copyright 2009, Red Hat, Inc
# Steve 'Ashcrow' Milner <smilner@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Standard build script.
"""

from distutils.core import setup
from loki import __VERSION__, __LICENSE__


setup(name = "loki",
    version = __VERSION__,
    description = "buildbot helper utility.",
    author = 'Dan Radez, Scott Henson, Steve Milner',
    author_email = 'dradez@redhat.com, \
                    shenson@redhat.com, \
                    smilner@redhat.com',

    data_files=[('/etc/loki/', ['etc/loki.conf'])],

    license = __LICENSE__,

    platforms=["Linux", "Unix"],

    scripts=['bin/loki'],

    packages = ['loki', 'loki.actions'],

    py_modules = ['func.minion.modules.loki_buildbot'],

    classifiers=[
        'License :: OSI Approved ::  GNU General Public License (GPL)',
        'Development Status :: 5 - Production/Stable',
        'Topic :: Software Development :: Libraries :: Python Modules'
        'Operating System :: Unix',
        'Programming Language :: Python', ], )
