from django.conf import settings
from kubernetes import client


def build_job_spec(name, namespace, image, command, environment_variables, cpu, memory, retry_limit=4):
    node_selector = settings.NODE_SELECTORS[namespace]
    split_cpu = str(cpu).split("/")
    split_memory = str(memory).split("/")
    cpu_request = split_cpu[0]
    cpu_limit = split_cpu[-1]
    memory_request = split_memory[0]
    memory_limit = split_memory[-1]
    job = {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {
            "name": name,
        },
        "spec": {
            "template": {
                "spec": {
                    "containers": [
                        {
                            "name": name,
                            "image": image,
                            "command": command,
                            "resources": {
                                "requests": {
                                    "memory": memory_request,
                                    "cpu": cpu_request,
                                },
                                "limits": {
                                    "memory": memory_limit,
                                    "cpu": cpu_limit
                                }
                            },
                            "env": [
                                {"name": i[0], "value": i[1]}
                                for i in environment_variables.iteritems()
                            ]
                        }
                    ],
                    "restartPolicy": "Never",
                    "nodeSelector": node_selector,
                }
            },
            "backoffLimit": retry_limit,
        }
    }
    labels = {
        "job-type": namespace,
    }
    job['spec']['template']['metadata'] = {"labels": labels}
    job['spec']['template']['spec']['affinity'] = {
        "podAffinity": {
            "preferredDuringSchedulingIgnoredDuringExecution": [{"weight": 100, "podAffinityTerm": {
                "labelSelector": {"matchExpressions": [{"key": "job-type", "operator": "In", "values": [namespace]}]},
                "topologyKey": "kubernetes.io/cielo24.com",
            }}]
        }
    }
    return job


def submit(namespace, job_spec):
    batch_client = client.BatchV1Api()
    return batch_client.create_namespaced_job(namespace=namespace, body=job_spec)


def delete(namespace, name):
    batch_client = client.BatchV1Api()
    return batch_client.delete_namespaced_job(namespace=namespace, name=name, body={})


def fetch(namespace, name):
    batch_client = client.BatchV1Api()
    return batch_client.read_namespaced_job(namespace=namespace, name=name)


def list(namespace):
    batch_client = client.BatchV1Api()
    return batch_client.list_namespaced_job(namespace)
