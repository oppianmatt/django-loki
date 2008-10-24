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
Yui specific functions and classes.
"""

import types
from decimal import *

from django.db import models
from django.utils import simplejson as json
from django.core.serializers.json import DateTimeAwareJSONEncoder


def json_encode(data):
    """
    From http://blog.michaeltrier.com/2007/7/30/json-generic-serializer.

    Simple json creator for ajax (unlike the django serializer which is for
    object transference).
    """

    def _any(data):
        """
        TODO: Document me!
        """
        ret = None
        if type(data) is types.ListType:
            ret = _list(data)
        elif type(data) is types.DictType:
            ret = _dict(data)
        elif isinstance(data, Decimal):
            # json.dumps() cant handle Decimal
            ret = str(data)
        elif isinstance(data, models.query.QuerySet):
            # Actually its the same as a list ...
            ret = _list(data)
        elif isinstance(data, models.Model):
            ret = _model(data)
        else:
            ret = data
        return ret

    def _model(data):
        """
        TODO: Document me!
        """
        ret = {}
        # If we only have a model, we only want to encode the fields.
        for f in data._meta.fields:
            ret[f.attname] = _any(getattr(data, f.attname))
        # And additionally encode arbitrary properties that had been added.
        fields = dir(data.__class__) + ret.keys()
        add_ons = [k for k in dir(data) if k not in fields]
        for k in add_ons:
            ret[k] = _any(getattr(data, k))
        return ret

    def _list(data):
        """
        TODO: Document me!
        """
        ret = []
        for v in data:
            ret.append(_any(v))
        return ret

    def _dict(data):
        """
        TODO: Document me!
        """
        ret = {}
        for k, v in data.items():
            ret[k] = _any(v)
        return ret

    ret = _any(data)

    return json.dumps(ret, cls=DateTimeAwareJSONEncoder)
