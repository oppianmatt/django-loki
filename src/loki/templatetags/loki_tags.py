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

register = template.Library()


@register.inclusion_tag('loki/ajax/step.html')
# The first argument *must* be called "context" here.
def step(step):
    return {'step': step, }


@register.inclusion_tag('loki/ajax/status.html')
def status(status):
    return {'status': status, }
