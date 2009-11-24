#!/usr/bin/env python
"""
Standard build script.
"""

__docformat__ = 'restructuredtext'


import os
import sys

from distutils.core import Command, setup
from os import path

sys.path.insert(0, 'src')

from loki import __version__, __license__, __author__


class SetupBuildCommand(Command):
    """
    Master setup build command to subclass from.
    """

    user_options = []

    def initialize_options(self):
        """
        Setup the current dir.
        """
        self._dir = os.getcwd()

    def finalize_options(self):
        """
        No clue ... but it's required.
        """
        pass


class SphinxCommand(SetupBuildCommand):
    """
    Creates HTML documentation using Sphinx.
    """

    description = "Generate documentation via sphinx"

    def run(self):
        """
        Run the DocCommand.
        """
        print "Creating html documentation ..."

        try:
            from sphinx.application import Sphinx

            if not os.access(path.join('docs', 'html'), os.F_OK):
                os.mkdir(path.join('docs', 'html'))
            buildername = 'html'
            outdir = path.abspath(path.join('docs', 'html'))
            doctreedir = os.path.join(outdir, '.doctrees')

            confdir = path.abspath('docs')
            srcdir = path.abspath('docs')
            freshenv = False

            # Create the builder
            app = Sphinx(srcdir, confdir, outdir, doctreedir, buildername,
                         {}, sys.stdout, sys.stderr, freshenv)

            # And build!
            app.builder.build_all()
            print "Your docs are now in %s" % outdir
        except ImportError, ie:
            print >> sys.stderr, "You don't seem to have the following which"
            print >> sys.stderr, "are required to make documentation:"
            print >> sys.stderr, "\tsphinx.application.Sphinx"
            print >> sys.stderr, ie
        except Exception, ex:
            print >> sys.stderr, "FAIL! exiting ... (%s)" % ex


class RPMBuildCommand(SetupBuildCommand):
    """
    Creates an RPM based off spec files.
    """

    description = "Build an rpm based off of the top level spec file(s)"

    def run(self):
        """
        Run the RPMBuildCommand.
        """
        try:
            if os.system('./setup.py sdist'):
                raise Exception("Couldn't call ./setup.py sdist!")
                sys.exit(1)
            if not os.access('dist/rpms/', os.F_OK):
                os.mkdir('dist/rpms/')
            dist_dir = os.path.join(os.getcwd(), 'dist')
            rpm_cmd = 'rpmbuild -ba --clean \
                                    --define "_rpmdir %s/rpms/" \
                                    --define "_srcrpmdir %s/rpms/" \
                                    --define "_sourcedir %s" *spec' % (
                      dist_dir, dist_dir, dist_dir)
            if os.system(rpm_cmd):
                raise Exception("Could not create the rpms!")
        except Exception, ex:
            print >> sys.stderr, str(ex)


class ViewDocCommand(SetupBuildCommand):
    """
    Quick command to view generated docs.
    """

    def run(self):
        """
        Opens a webbrowser on docs/html/index.html
        """
        import webbrowser

        print ("NOTE: If you have not created the docs first this will not be "
               "helpful. If you don't see any documentation in your browser "
               "run ./setup.py doc first.")
        if not webbrowser.open('docs/html/index.html'):
            print >> sys.stderr, "Could not open on your webbrowser."


class DjangoTestCommand(SetupBuildCommand):
    """
    Quick command to view generated docs.
    """

    def run(self):
        """
        Simply executes the django test cases.
        """
        try:
            # Import yaml just to make sure it's available since the
            # tests need it
            import yaml
            os.system('./src/example_project/manage.py test')
        except ImportError, ie:
            print >> sys.stderr, "You must have PyYAML installed to test."


def get_sources(map_list):
    """
    Simple function to make it easy to get everything under a directory as
    a source list.

    :Parameters:
       - `src`: the location on the file system to use as a root.
       - `dst`: the target location to use as a root.
       - `recursive`: include subdirs.
    """
    file_list = []
    for map in map_list:
        dst, src, recursive = map
        for afile in os.listdir(src):
            this_dir_list = []
            full_path = os.path.join(src, afile)
            if os.path.isfile(full_path):
                this_dir_list.append(full_path)
            else:
                if recursive:
                    file_list.extend(
                        get_sources([(os.path.join(dst, afile),
                                      full_path,
                                      recursive)]))
            file_list.append((dst, this_dir_list))
    return file_list


setup(name = "Django-app-loki",
    version = __version__,
    description = "A buildbot management application",
    long_description = "A buildbot management application",
    author = __author__,
    author_email = 'dradez@redhat.com',
    url = "http://www.fedorahosted.org/loki/",
    platforms = ['linux'],

    license = __license__,

    classifiers = [
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python'],

    data_files = get_sources([('share/django/apps/loki',
                               os.path.join('src',
                                            'loki'),
                               True)]),

    cmdclass = {'rpm': RPMBuildCommand,
                'doc': SphinxCommand,
                'viewdoc': ViewDocCommand,
                'test': DjangoTestCommand})
