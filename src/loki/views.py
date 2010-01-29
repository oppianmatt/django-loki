# Copyright 2008, Red Hat, Inc
# Dan Radez <dradez@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import time

from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import user_passes_test

from loki.models import Master, Slave, Config, ConfigParam
from loki.models import Status, Step, StepParam, Scheduler
from loki.models import  status_content_type
from loki.models import  step_content_type
from loki.models import  scheduler_content_type

from loki.model_helpers import introspect_module
from loki.forms import ConfigParamFormSet


def home(request, master=None, slave=None):
    context = {}
    context['bots'] = Master.objects.all()
    context['steps'] = Config.objects.filter(content_type=step_content_type)
    context['status'] = Config.objects.filter(content_type=status_content_type)
    action = None
    if request.method == 'GET' and 'action' in request.GET:
        if request.GET['action'] in ['start', 'stop', 'reconfig']:
            action = request.GET['action']
    if slave:
        slave = Slave.objects.get(name=slave)
        if action:
            slave.buildbot_run(action)
            time.sleep(1)
            return HttpResponseRedirect(reverse('loki.views.home',
                                        args=[slave.master.name, slave.name]))
        context['slave'] = slave
        return render_to_response('loki/slave.html', context)
    elif master:
        master = Master.objects.get(name=master)
        if action:
            master.buildbot_run(action)
            time.sleep(1)
            return HttpResponseRedirect(reverse('loki.views.home',
                                            args=[master.name]))
        context['master'] = master
        return render_to_response('loki/master.html', context)
    return render_to_response('loki/home.html', context)


def config_add(request, type, bot_id, config_id):
    config = Config.objects.get(pk=config_id)
    config_num = 0
    if type == 'step':
        slave = Slave.objects.get(pk=bot_id)
        step_with_max_num = Step.objects.filter(slave=slave).order_by('-num')
        if step_with_max_num:
            max_num = step_with_max_num[0].num
            config_num = max_num + 1
    context = {'type': type,
               'bot': bot_id,
               'config': config,
               'config_num': config_num, }

    return render_to_response('loki/ajax/config.html', context)


def config_load(request, type, config_id):
    if type == 'step':
        config = Step.objects.get(pk=config_id)
    elif type == 'status':
        config = Status.objects.get(pk=config_id)
    context = {type: config, }

    return render_to_response('loki/ajax/%s.html' % type, context)


def config_step_save(request, bot_id):
    result = ''
    if request.method == 'POST':
        slave = Slave.objects.get(id=bot_id) 
        data = request.POST.copy()
        # get a step or create a newone
        if 'step_id' in data and data['step_id']:
            step = Step.objects.get(id=data['step_id'])
            step.num = data['config_num']
            del data['step_id']
        else:
            config = Config.objects.get(id=data['config_type_id'])
            step = Step(slave=slave, type=config, num=data['config_num'])
            step.save()
            del data['config_type_id']
        del data['config_num']

        params_2_add = []
        # update existing params
        for p in step.params.all():
            #TODO: update existing params
            #      only to creating a new one
            #      so just passing for now
            # how: check if default, if changed, save it
            #      then delete the key from the dict
            #      so it's not reprocessed
            #      and add the param to the params 2 add
            pass
        # add new params
        for p, v in data.items():
            param_type = ConfigParam.objects.get(id=p)
            if v != param_type.default:
                param = StepParam(step=step, type=param_type, val=v)
                params_2_add.append(param)
        step.params = params_2_add
        step.save()
        result = step.id
    return HttpResponse(result)


def config_status_save(request, bot_id):
    result = ''
    if request.method == 'POST':
        try:
            master = Master.objects.get(id=bot_id) 
            data = request.POST.copy()
            # get a status or create a newone
            if 'status_id' in data and data['status_id']:
                status = Status.objects.get(id=data['status_id'])
                del data['status_id']
            else:
                config = Config.objects.get(id=data['config_type_id'])
                status = Status(slave=slave, type=config)
                status.save()
                del data['config_type_id']
            del data['status_num']

            params_2_add = []
            # update existing params
            for p in status.params.all():
                #TODO: update existing params
                #      only to creating a new one
                #      so just passing for now
                # how: check if default, if changed, save it
                #      then delete the key from the dict
                #      so it's not reprocessed
                #      and add the param to the params 2 add
                pass
            # add new params
            for p, v in data.items():
                param_type = ConfigParam.objects.get(id=p)
                if v != param_type.default:
                    param = StatusParam(status=status, type=param_type, val=v)
                    params_2_add.append(param)
            status.params = params_2_add
            status.save()
            result = status.id
        except Exception, e:
            result = e

    return HttpResponse(result)


def config_delete(request, type):
    result = ''
    if request.method == 'POST':
        data = request.POST
        if type == 'step':
            config = Step.objects.get(id=data['step_id'])
        elif type == 'status':
            config = Status.objects.get(id=data['status_id'])
        config.delete()
    return HttpResponse(result)


@user_passes_test(lambda u: u.is_superuser)
def introspect(request, type):
    # do import if we're importing
    if request.method == 'POST' and 'import' in request.POST:
        content_types = {
            'status': status_content_type,
            'steps': step_content_type,
            'scheduler': scheduler_content_type,
        }
        module = request.POST['import']
        path = '.'.join(module.split('.')[:-1])
        name = request.POST['import'].split('.')[-1]
        introspected = introspect_module(path=path)
        imported_config = introspected[name]
        new_config = Config.objects.create(name=name, module=module,
                                         content_type=content_types[type])
        new_config.save()
        try:
            for req in imported_config[1]:
                ConfigParam.objects.create(type=new_config, name=req,
                                           required=True).save()
            for opt, default in imported_config[2].items():
                ConfigParam.objects.create(type=new_config, name=opt,
                                           default=str(default)).save()
        except Exception, e:
            new_config.delete()
            raise e

        return HttpResponseRedirect(reverse('loki.views.introspect',
                                    args=[type]))

    # not importing so get configs in the db and configs from the path
    configs = [mod[0] for mod in Config.objects.values_list('module')]
    path = 'buildbot.%s' % type
    if request.method == 'GET' and 'path' in request.GET:
        path = request.GET['path']
    introspected = introspect_module(path=path)

    # calculate which introspected cofigs are already in the db
    del_classes = []
    for config in introspected:
        if introspected[config][0] in configs:
            del_classes.append(config)

    # remove the existing configs from the displayed list.
    for del_class in del_classes:
        del introspected[del_class]

    # render
    context = {'path': path,
                'type': type,
                'classes': introspected, }
    return render_to_response('loki/introspect.html', context)
