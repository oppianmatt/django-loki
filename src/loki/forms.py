from django.forms.models import modelformset_factory
from django.forms.models import inlineformset_factory

from loki.models import Config, ConfigParam

ConfigParamFormSet = modelformset_factory(ConfigParam)
