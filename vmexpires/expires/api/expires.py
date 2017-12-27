from django.conf import settings
import datetime
import time
import logging

import requests

from openstack_dashboard.api import base

from horizon.utils.memoized import memoized
from horizon.utils.memoized import memoized_with_request
from horizon import exceptions

LOG = logging.getLogger(__name__)

VERSIONS = base.APIVersionManager("vmexpire", preferred_version=1)

def get_auth_params_from_request(request):
    auth_url = base.url_for(request, 'identity')
    vmexpire_urls = []
    for service_name in ('vmexpire',):
        try:
            vmexpire_url = base.url_for(request, service_name)
            vmexpire_urls.append((service_name, vmexpire_url))
        except exceptions.ServiceCatalogException:
            pass
    if not vmexpire_urls:
        raise exceptions.ServiceCatalogException(
            "no vmexpire service configured")
    vmexpire_urls = tuple(vmexpire_urls)  # need to make it cacheable
    return(
        request.user.username,
        request.user.token.id,
        request.user.tenant_id,
        vmexpire_urls,
        auth_url,
    )

@memoized_with_request(get_auth_params_from_request)
def vmexpireclient(request_auth_params, version=None):
    if version is None:
        api_version = VERSIONS.get_active_version()
        version = api_version['version']
    insecure = getattr(settings, 'OPENSTACK_SSL_NO_VERIFY', False)
    cacert = getattr(settings, 'OPENSTACK_SSL_CACERT', None)

    username, token_id, tenant_id, vmexpire_urls, auth_url = request_auth_params
    try:
        version = base.Version(version)
    except Exception:
        version = str(version)
    service_names = ('vmexpire',)
    for name, vmexpire_url in vmexpire_urls:
        if name in service_names:
            break
    else:
        raise exceptions.ServiceCatalogException(
            "VmExpire {version} requested but no '{service}' service "
            "type available in Keystone catalog.".format(version=version,
                                                         service=service_names)
        )
    c = {
        'version': version,
        'username': username,
        'token_id': token_id,
        'project_id': tenant_id,
        'auth_url': auth_url,
        'insecure': insecure,
        'cacert': cacert,
        'http_log_debug': settings.DEBUG,
        'auth_token': token_id,
        'management_url': vmexpire_url
    }
    return c


class Instance(object):
    def __init__(self):
        self.id = None
        self.user = None
        self.instance = None
        self.expire = time.mktime(datetime.datetime.now().timetuple())
        self.created_at = datetime.datetime.now().isoformat()
        self.updated_at = self.created_at


def get(request, id):
    username = request.user.username
    project_id = request.user.tenant_id
    data = vmexpireclient(request)
    elt = None
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': data['auth_token']}
    try:
        elt = requests.get(data['management_url'] + '/vmexpire/' + str(id), headers=headers)
    except Exception as e:
        LOG.exception(e)
        return None
    if elt.status_code != 200:
        return None

    res_json = elt.json()['vmexpire']
    tabelt = Instance()
    tabelt.id = res_json['id']
    tabelt.user = res_json['user_id']
    tabelt.instance = res_json['instance_id']
    tabelt.expire = datetime.datetime.fromtimestamp(res_json['expire']).isoformat()
    tabelt.created_at = res_json['created']
    tabelt.updated_at = res_json['updated']
    return tabelt

def delete(request, id):
    return None

def extend(request, id):
    instance = get(request, id)
    if instance is None:
        return None
    data = vmexpireclient(request)
    elt = None
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': data['auth_token']}
    try:
        elt = requests.put(data['management_url'] + '/vmexpire/' + str(id), headers=headers)
    except Exception as e:
        LOG.error("failed to send put")
        LOG.exception(e)
        return None
    if elt.status_code != 202:
        return None
    res_json = elt.json()['vmexpire']
    instance.expire = res_json['expire']
    return instance

def list(request):
    username = request.user.username
    project_id = request.user.tenant_id
    list = []
    data = vmexpireclient(request)
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': data['auth_token']}
    try:
        instances = requests.get(data['management_url'] + '/vmexpire/', headers=headers)
    except Exception as e:
        LOG.exception(e)
        return list
    if instances.status_code != 200:
        return list
    res_json = instances.json()
    for elt in res_json['vmexpires']:
        tabelt = Instance()
        tabelt.id = elt['id']
        tabelt.user = elt['user_id']
        tabelt.instance = elt['instance_id']
        tabelt.expire = datetime.datetime.fromtimestamp(elt['expire']).isoformat()
        tabelt.created_at = elt['created']
        tabelt.updated_at = elt['updated']
        list.append(tabelt)
    return list
