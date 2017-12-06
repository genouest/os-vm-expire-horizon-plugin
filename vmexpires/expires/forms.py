from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms

from openstack_dashboard import api

from vmexpires.expires.api.expires import list as api_list
from vmexpires.expires.api.expires import get as api_get
from vmexpires.expires.api.expires import extend as api_extend


class Extend(forms.SelfHandlingForm):
    instance_id = forms.CharField(label=_("Instance ID"),
                                  widget=forms.HiddenInput(),
                                  required=False)
    def handle(self, request, data):
        try:
            extend = api_extend(request, data['instance_id'])
            if extend is None:
                exceptions.handle(request,
                              _('Unable to extend VM duration.'))
            return extend
        except Exception:
            exceptions.handle(request,
                              _('Unable to extend VM duration.'))
