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
Various util functions.
"""

from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.db.models import Model


def bind_administration(model_module, admin_module):
    """
    Binds Models with ModelAdmins with magic.

    :Parameters:
       - `model_module`: the module name where our Models live.
       - `admin_module`: the module name where our ModelAdmins live.

        >>> bind_administration('project.app.models', 'project.app.admin')
        >>>
    """
    # import logging
    import logging

    # import both modules
    mimp = __import__(model_module,
                      globals(),
                      locals(),
                      [model_module.split('.')[-1]])
    imp = __import__(admin_module,
                     globals(),
                     locals(),
                     [admin_module.split('.')[-1]])
    # We will hold a nice mapping to return in case the caller wants to verify
    admin_mapping = {}
    # For each item in the admin import
    for item in dir(imp):
        # We try/except because issubclass will freak out if item isnt a class
        try:
            real_admin = getattr(imp, item)
            # If item is a subclass of ModelAdmin then do some real work
            if issubclass(real_admin, ModelAdmin) and real_admin != ModelAdmin:
                logging.debug('%s is a subclass of ModelAdmin' % real_admin)
                # Create a nice mapping
                model_class_name = item.replace('Admin', '')
                real_model = getattr(mimp, model_class_name)
                # Make sure it's actually a Model and not some other item
                if issubclass(real_model, Model):
                    logging.debug('%s is a subclass of Model' % real_model)
                    admin_class_name = item
                    admin_mapping[model_class_name] = real_admin
                    # And register with admin
                    admin.site.register(real_model, real_admin)
                    logging.info('Registered %s with %s' % (
                        model_class_name, admin_class_name))
        except TypeError, te:
            # Not a class, go ahead and pass
            logging.debug('%s is not a class' % item)
