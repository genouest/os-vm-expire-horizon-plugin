from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs

from openstack_dashboard import api
from vmexpires.expires import tables
from vmexpires.expires.api.expires import list as api_list
from vmexpires.expires.api.expires import get as api_get

import logging
from django.conf import settings
import datetime
import time

LOG = logging.getLogger(__name__)


class InstanceTab(tabs.TableTab):
    name = _("Instances Tab")
    slug = "instances_tab"
    table_classes = (tables.InstancesTable,)
    template_name = ("horizon/common/_detail_table.html")
    preload = False

    def has_more_data(self, table):
        #return self._has_more
        return False

    def get_instances_data(self):
        try:
            return api_list(self.request)
        except Exception as e:
            self._has_more = False
            error_message = _('Unable to get instances')
            exceptions.handle(self.request, error_message)
            LOG.exception(str(e))

            return []

class MypanelTabs(tabs.TabGroup):
    slug = "mypanel_tabs"
    tabs = (InstanceTab,)
    sticky = True
