# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon.utils import memoized
from horizon import tabs
from horizon import views
from horizon import forms

from vmexpires.expires import tabs as vmexpires_tabs

from vmexpires.expires \
    import forms as instance_forms

from vmexpires.expires.api.expires import list as api_list
from vmexpires.expires.api.expires import get as api_get

class IndexView(tabs.TabbedTableView):
    # A very simple class-based view...
    tab_group_class = vmexpires_tabs.MypanelTabs
    template_name = 'vmexpires/expires/index.html'

    def get_data(self, request, context, *args, **kwargs):
        # Add data to the context here...
        return context

class ExtendView(forms.ModalFormView):
    form_class = instance_forms.Extend
    template_name = 'vmexpires/expires/extend.html'
    success_url = reverse_lazy("horizon:vmexpires:expires:index")
    modal_id = "extend_modal"
    modal_header = _("Extend instance duration")
    submit_label = _("Extend")
    submit_url = "horizon:vmexpires:expires:extend"

    @memoized.memoized_method
    def get_object(self):
        try:
            return api_get(self.request, self.kwargs["instance_id"])
        except Exception:
            exceptions.handle(self.request,
                              _("Unable to retrieve instance."))

    def get_initial(self):
        return {"instance_id": self.kwargs["instance_id"]}

    def get_context_data(self, **kwargs):
        context = super(ExtendView, self).get_context_data(**kwargs)
        instance_id = self.kwargs['instance_id']
        context['instance_id'] = instance_id
        context['instance'] = self.get_object()
        context['submit_url'] = reverse(self.submit_url, args=[instance_id])
        return context
