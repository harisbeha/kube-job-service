from django.apps import AppConfig


class ServiceConfig(AppConfig):
    name = 'service'

    def ready(self):
        from kubernetes import config
        config.load_incluster_config()
        return super(ServiceConfig, self).ready()
