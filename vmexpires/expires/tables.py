from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon import tables
from openstack_dashboard import api

import logging

from vmexpires.expires.api.expires import delete as api_delete

LOG = logging.getLogger(__name__)


class MyFilterAction(tables.FilterAction):
    name = "myinstancefilter"

class ExtendAction(tables.LinkAction):
    name = "extend"
    verbose_name = _("Extend duration")
    url = "horizon:vmexpires:expires:extend"
    classes = ("ajax-modal",)
    icon = "camera"

    def allowed(self, request, instance=None):
        return True

class DeleteAction(tables.DeleteAction):
    name = "delete"
    data_type_singular = _("Expire")
    data_type_plural = _("Expires")
    classes = ('btn-danger', 'btn-terminate')

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete expire",
            u"Delete expires",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted expire",
            u"Deleted expires",
            count
        )

    def allowed(self, request, instance=None):
        return False
        '''
        if not api.nova.extension_supported('AdminActions',
                                            request):
            return False
        if not instance:
            return False
        has_permission = policy.check(
            ("vmexpires","vmexpires:delete"), request)
        return has_permission
        '''

    def delete(self, request, expire_id):
        api_delete(request, expire_id)

class InstancesTable(tables.DataTable):
    instance = tables.Column("instance", verbose_name=_("Instance"))
    user = tables.Column("user", verbose_name=_("Owner"))
    expire = tables.Column("expire", verbose_name=_("Expires at"))

    class Meta(object):
        name = "instances"
        verbose_name = _("Instances")
        table_actions = (MyFilterAction, DeleteAction)
        row_actions = (ExtendAction,)
