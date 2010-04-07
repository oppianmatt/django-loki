# Copyright 2008-2010, Red Hat, Inc
# Dan Radez <dradez@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from loki.models import *
from django.contrib import admin
from django.contrib.contenttypes import generic


class ConfigParamInline(admin.TabularInline):
    model = ConfigParam


class StatusParamInline(admin.TabularInline):
    model = StatusParam


class StepParamInline(admin.TabularInline):
    model = StepParam


class SchedulerParamInline(admin.TabularInline):
    model = SchedulerParam


class HostAdmin(admin.ModelAdmin):
    pass


class MasterAdmin(admin.ModelAdmin):
    pass


class SlaveAdmin(admin.ModelAdmin):
    list_display = ('master', 'name')
    list_display_links = ('name', )


class ConfigAdmin(admin.ModelAdmin):
    inlines = [ConfigParamInline, ]


class StatusAdmin(admin.ModelAdmin):
    inlines = [StatusParamInline, ]


class StepAdmin(admin.ModelAdmin):
    inlines = [StepParamInline, ]


class SchedulerAdmin(admin.ModelAdmin):
    inlines = [SchedulerParamInline, ]
