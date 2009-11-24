# Copyright 2008, Red Hat, Inc
# Dan Radez <dradez@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import os
import inspect

def _template(tpl, **vars):
    """
    tpl: template file path
    **vars: variables to interpolate into the template
    """
    return open(tpl, 'r').read() % vars

def _generate_class(cls):
    """
    TODO: Document me!
    """
    gcls = cls.type.module.split('.')[-1]
    gprm = []
    for param in cls.params.all():
        if param.val[0] in ['[','{']:
            gprm.append("%s=%s" % (param.type.name, param.val))
        else:
            gprm.append("%s='%s'" % (param.type.name, param.val))
    return "%s(%s)" % (gcls, ', '.join(gprm))

def introspect_module(path='buildbot.steps'):
    """
    Get a list of tuples representing classes for config
    each tuple will have the name of a class in the module
    a list of required parameters and
    a dict of optional parameters and their defaults

    @param obj: a python package or module path
    @type obj: module

    @return: dict of tuples 'ClassName'
             : ('classpath', ['reqs'], {'opts': None})
    """
    #x = __import__(pkg, fromlist=['module'])
    x = __import__(path, globals(), locals(), [str(path)])

    modules = []
    #Check if x is a directory and get it's modules
    if hasattr(x, '__path__'):
        for f in os.listdir(x.__path__[0]):
            if f.endswith('.py') and f != '__init__.py':
                modules.append(f.split('.')[0])
    #or it is a module so adjust
    else:
        modules.append(path.split('.')[-1])
        path = '.'.join(path.split('.')[0:-1])


    classes = {}
    for m in modules:
        #y = __import__("%s.%s" % (pkg, m), fromlist=['module'])
        y = __import__("%s.%s" % (path, m),
                       globals(), locals(), ['module'])
        for i in inspect.getmembers(y):
            if inspect.isclass(i[1]) and not i[0].startswith('_')\
               and i[1].__module__.startswith("%s.%s" % (path, m))\
               and hasattr(i[1], '__init__'):
                req = []
                opt = {}
                i_init = inspect.getargspec(i[1].__init__)
                i_init_args = [x for x in reversed(i_init[0][1:])]
                if i_init[3] != None:
                    i_init_defaults = [x for x in reversed(i_init[3])]
                c = 0
                for a in i_init_args:
                    if i_init[3] == None:
                        req.append(a)
                    else:
                        if c < len(i_init_defaults):
                            if i_init_defaults[c] == None:
                                opt[a] = None
                                # XMLRPC can't handle None, this was used when
                                #we were using func to do this. 
                                #opt[a] = 'LokiNone'
                            else:
                                opt[a] = i_init_defaults[c]
                        else:
                            req.append(a)
                    c = c + 1
                classes[i[0]] = ("%s.%s" % (i[1].__module__, i[0]),
                                 req,
                                 opt)
    return classes
