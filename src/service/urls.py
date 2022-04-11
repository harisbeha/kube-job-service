from django.conf.urls import url

from .views import list_jobs, delete_job, create_job, get_job

urlpatterns = [
    url(r'^create/(?P<namespace>[a-zA-Z0-9-]+)/(?P<job_name>[a-zA-Z0-9-]+)$', create_job),
    url(r'^delete/(?P<namespace>[a-zA-Z0-9-]+)/(?P<job_name>[a-zA-Z0-9-]+)$', delete_job),
    url(r'^list/(?P<namespace>[a-zA-Z0-9-]+)$', list_jobs),
    url(r'^get/(?P<namespace>[a-zA-Z0-9-]+)/(?P<job_name>[a-zA-Z0-9-]+)$', get_job),
]
