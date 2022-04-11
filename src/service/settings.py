# import standard_environment.base.settings
from copy import deepcopy
import collections

from standard_environment.base.settings import *

INSTALLED_APPS = DJANGO_APPS_WITHOUT_CHANNELS

APP_NAME = 'Transcode Dispatcher'

# Some of the service settings are intentionlly strings.  This isn't a mistake because they're copied into Kube specs.
settings_converters = collections.defaultdict(lambda: lambda ident: ident)
settings_converters['retry_limit'] = int

DEFAULT_TRANSCODE_SETTINGS = {
    'cpu': os.environ.get('DEFAULT_TRANSCODE_CPU', '1'),
    'image': os.environ.get('TRANSCODE_IMAGE', "gcr.io/coresystem-171219/kube-transcode:0.0.1"),
    'memory': os.environ.get('TRANSCODE_MEMORY', '3Gi'),
    'retry_limit': os.environ.get('TRANSCODE_RETRY_LIMIT', 4),
}

TRANSCODE_SERVICES = os.environ.get('TRANSCODE_SERVICES', 'ffmpeg,ffprobe,mp4box,align,sphinx,check-media,handle-blank-audio').split(',')

TRANSCODE_SETTINGS_BY_SERVICE = {i: deepcopy(DEFAULT_TRANSCODE_SETTINGS) for i in TRANSCODE_SERVICES}

settings_keys = DEFAULT_TRANSCODE_SETTINGS.keys()
for svc in TRANSCODE_SERVICES:
    for key in settings_keys:
        val = TRANSCODE_SETTINGS_BY_SERVICE[svc][key]
        var = 'TRANSCODE_{}_{}_OVERRIDE'.format(svc.upper().replace("-", "_"), key.upper())
        TRANSCODE_SETTINGS_BY_SERVICE[svc][key] = settings_converters[key](os.environ.get(var, val))

# A job can dispatch to any of the following namespaces, and will prefer to group with any other job in the following namespaces.
bands=['1h', '2h', '3h', '4h', '5h', '6h', '8h', '10h', '14h', 'large']
TRANSCODE_NAMESPACES = ['transcode-kube']

if DEPLOYMENT_TYPE == 'prod':
    TRANSCODE_NAMESPACES = ['transcode-{}'.format(i) for i in bands]

NODE_SELECTORS = {'transcode-kube': {'group': 'dev'}}

if DEPLOYMENT_TYPE == 'prod':
    NODE_SELECTORS = {'transcode-{}'.format(i): {'band': i} for i in bands}
