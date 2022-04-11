import json

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
import kube_api
from .kube_api import build_job_spec
from kubernetes.client.rest import ApiException as KubeApiException
import functools

def catch_kube_api_error(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KubeApiException as e:
            return JsonResponse(status=e.status, data={"error": str(e.reason)})
    return wrapped



@csrf_exempt
@require_GET
@catch_kube_api_error
def list_jobs(request, namespace):
    if namespace not in settings.TRANSCODE_NAMESPACES:
        return HttpResponse(400, "Not a valid transcoding namespace.")
    jobs = kube_api.list(namespace)
    return JsonResponse(status=200, data=jobs.to_dict())


@csrf_exempt
@require_GET
@catch_kube_api_error
def get_job(request, namespace, job_name):
    if namespace not in settings.TRANSCODE_NAMESPACES:
        return HttpResponse(400, "Not a valid transcoding namespace.")
    job = kube_api.fetch(namespace, job_name)
    return JsonResponse(status=200, data=job.to_dict())


@csrf_exempt
@require_POST
@catch_kube_api_error
def delete_job(request, namespace, job_name):
    if namespace not in settings.TRANSCODE_NAMESPACES:
        return HttpResponse(400, "Not a valid transcoding namespace.")
    resp=kube_api.delete(namespace, job_name)
    return JsonResponse(status=200, data=resp.to_dict())

@csrf_exempt
@require_POST
@catch_kube_api_error
def create_job(request, namespace, job_name):
    if namespace not in settings.TRANSCODE_NAMESPACES:
        return HttpResponse(status=400, data={"error": "Not a valid transcoding namespace."})
    params = json.loads(request.body)
    service = params['service']
    if service not in settings.TRANSCODE_SERVICES:
        return JsonResponse(status=400, data={"error": "Not a supported service."})
    config = params['config']
    config['DEIS_APP'] = 'transcode'
    command = ['bash', '-c', "cd /app; ./{}.sh".format(service)]
    job_spec = build_job_spec(
        command=command,
        environment_variables=config,
        namespace=namespace,
        name=job_name,
        **settings.TRANSCODE_SETTINGS_BY_SERVICE[service])
    resp = kube_api.submit(namespace, job_spec)
    return JsonResponse(status=200, data=resp.to_dict())
