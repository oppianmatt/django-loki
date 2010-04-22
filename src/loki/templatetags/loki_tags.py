# Copyright 2009, Red Hat, Inc
# Dan Radez <dradez@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
loki template tags
"""

import os
import random
import time

from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag('loki/ajax/step.html', takes_context=True)
def step(context, step):
    return {'step': step, 
            'ADMIN_MEDIA_PREFIX': settings.ADMIN_MEDIA_PREFIX,
            'user': context['request'].user,
    }



@register.inclusion_tag('loki/ajax/status.html', takes_context=True)
def status(context, status):
    return {'status': status,
            'ADMIN_MEDIA_PREFIX': settings.ADMIN_MEDIA_PREFIX,
            'user': context['request'].user,
    }


@register.inclusion_tag('loki/ajax/scheduler.html', takes_context=True)
def scheduler(context, scheduler):
    return {'scheduler': scheduler, 
            'ADMIN_MEDIA_PREFIX': settings.ADMIN_MEDIA_PREFIX,
            'user': context['request'].user,
    }

