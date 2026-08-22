from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from kubernetes import client, config
from .models import Cluster, Namespace, App
from .serializers import ClusterSerializer, NamespaceSerializer, AppSerializer
from kubernetes.client import AppsV1Api

class ClusterListCreateView(APIView):
    def get(self, request):
        clusters = Cluster.objects.all()
        serializer = ClusterSerializer(clusters, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ClusterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NamespaceListCreateView(APIView):
    def post(self, request):
        serializer = NamespaceSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        cluster_id = serializer.validated_data['cluster_id']
        ns_name = serializer.validated_data['name']

        try:
            cluster_obj = Cluster.objects.get(id=cluster_id)
        except Cluster.DoesNotExist:
            return Response({"error": "Cluster not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            configuration = client.Configuration()
            addr = cluster_obj.address
            if not addr.startswith("http"):
                addr = f"https://{addr}"
            configuration.host = addr
            configuration.api_key['authorization'] = f"Bearer {cluster_obj.token}"
            configuration.verify_ssl = False

            api_client = client.ApiClient(configuration)
            v1_api = client.CoreV1Api(api_client)

            body = client.V1Namespace(metadata=client.V1ObjectMeta(name=ns_name))
            v1_api.create_namespace(body=body)

        except client.exceptions.ApiException as e:
            if e.status == 409:
                return Response({"error": "Namespace already exists in Kubernetes."}, status=status.HTTP_409_CONFLICT)
            elif e.status in [401, 403]:
                return Response({"error": "Unauthorized or forbidden in Kubernetes."}, status=status.HTTP_403_FORBIDDEN)
            return Response({"error": f"Kubernetes API error: {e.reason}"}, status=status.HTTP_502_BAD_GATEWAY)
        except Exception as e:
            return Response({"error": "Could not connect to Kubernetes cluster."}, status=status.HTTP_502_BAD_GATEWAY)

        namespace_obj = serializer.save(cluster=cluster_obj)
        return Response(NamespaceSerializer(namespace_obj).data, status=status.HTTP_201_CREATED)

    def get(self, request):
        cluster_id = request.query_params.get('cluster_id')
        if not cluster_id:
            return Response({"error": "cluster_id parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        namespaces = Namespace.objects.filter(cluster_id=cluster_id)
        serializer = NamespaceSerializer(namespaces, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NamespaceDetailView(APIView):
    def delete(self, request, pk):
        try:
            namespace_obj = Namespace.objects.get(pk=pk)
        except Namespace.DoesNotExist:
            return Response({"error": "Namespace not found in database."}, status=status.HTTP_404_NOT_FOUND)

        cluster_obj = namespace_obj.cluster

        try:
            configuration = client.Configuration()
            addr = cluster_obj.address
            if not addr.startswith("http"):
                addr = f"https://{addr}"
            configuration.host = addr
            configuration.api_key['authorization'] = f"Bearer {cluster_obj.token}"
            configuration.verify_ssl = False

            api_client = client.ApiClient(configuration)
            v1_api = client.CoreV1Api(api_client)

            v1_api.delete_namespace(name=namespace_obj.name)

        except client.exceptions.ApiException as e:
            if e.status != 404:
                return Response({"error": f"Kubernetes API error: {e.reason}"}, status=status.HTTP_502_BAD_GATEWAY)
        except Exception as e:
            return Response({"error": "Could not connect to Kubernetes cluster."}, status=status.HTTP_502_BAD_GATEWAY)

        namespace_obj.delete()
        return Response({"message": "Namespace deleted successfully."}, status=status.HTTP_200_OK)

class AppListCreateView(APIView):

    def post(self, request):
        serializer = AppSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        namespace_id = serializer.validated_data['namespace_id']
        app_name = serializer.validated_data['name']
        image = serializer.validated_data['image']
        replicas = serializer.validated_data.get('replicas', 1)
        cpu = serializer.validated_data.get('cpu', '100m')
        memory = serializer.validated_data.get('memory', '128Mi')

        try:
            ns_obj = Namespace.objects.get(id=namespace_id)
        except Namespace.DoesNotExist:
            return Response({"error": "Namespace not found in database."}, status=status.HTTP_404_NOT_FOUND)

        cluster_obj = ns_obj.cluster

        try:
            configuration = client.Configuration()
            addr = cluster_obj.address if cluster_obj.address.startswith("http") else f"https://{cluster_obj.address}"
            configuration.host = addr
            configuration.api_key['authorization'] = f"Bearer {cluster_obj.token}"
            configuration.verify_ssl = False

            api_client = client.ApiClient(configuration)
            apps_api = AppsV1Api(api_client)

            deployment_manifest = client.V1Deployment(
                api_version="apps/v1",
                kind="Deployment",
                metadata=client.V1ObjectMeta(name=app_name),
                spec=client.V1DeploymentSpec(
                    replicas=replicas,
                    selector=client.V1LabelSelector(match_labels={"app": app_name}),
                    template=client.V1PodTemplateSpec(
                        metadata=client.V1ObjectMeta(labels={"app": app_name}),
                        spec=client.V1PodSpec(
                            containers=[
                                client.V1Container(
                                    name=app_name,
                                    image=image,
                                    resources=client.V1ResourceRequirements(
                                        limits={"cpu": cpu, "memory": memory},
                                        requests={"cpu": cpu, "memory": memory}
                                    )
                                )
                            ]
                        )
                    )
                )
            )

            apps_api.create_namespaced_deployment(namespace=ns_obj.name, body=deployment_manifest)

        except client.exceptions.ApiException as e:
            if e.status == 409:
                return Response({"error": "Deployment already exists in Kubernetes."}, status=status.HTTP_409_CONFLICT)
            return Response({"error": f"Kubernetes API error: {e.reason}"}, status=status.HTTP_502_BAD_GATEWAY)
        except Exception:
            return Response({"error": "Could not connect to Kubernetes cluster."}, status=status.HTTP_502_BAD_GATEWAY)

        app_obj = serializer.save(namespace=ns_obj)
        return Response(AppSerializer(app_obj).data, status=status.HTTP_201_CREATED)


    def get(self, request):
        namespace_id = request.query_params.get('namespace_id')
        if not namespace_id:
            return Response({"error": "namespace_id parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ns_obj = Namespace.objects.get(id=namespace_id)
        except Namespace.DoesNotExist:
            return Response({"error": "Namespace not found."}, status=status.HTTP_404_NOT_FOUND)

        apps = App.objects.filter(namespace_id=namespace_id)
        result = []

        try:
            cluster_obj = ns_obj.cluster
            configuration = client.Configuration()
            addr = cluster_obj.address if cluster_obj.address.startswith("http") else f"https://{cluster_obj.address}"
            configuration.host = addr
            configuration.api_key['authorization'] = f"Bearer {cluster_obj.token}"
            configuration.verify_ssl = False

            api_client = client.ApiClient(configuration)
            core_api = client.CoreV1Api(api_client)
            k8s_connected = True
        except Exception:
            k8s_connected = False

        for app in apps:
            app_data = AppSerializer(app).data
            
            if k8s_connected:
                try:
                    pods = core_api.list_namespaced_pod(
                        namespace=ns_obj.name,
                        label_selector=f"app={app.name}"
                    )
                    pod_statuses = []
                    for pod in pods.items:
                        is_ready = any(cond.type == 'Ready' and cond.status == 'True' for cond in (pod.status.conditions or []))
                        pod_statuses.append({
                            "pod_name": pod.metadata.name,
                            "phase": pod.status.phase,
                            "ready": is_ready
                        })
                    app_data['live_pods'] = pod_statuses
                except Exception:
                    app_data['live_pods'] = "Could not fetch status from K8s"
            else:
                app_data['live_pods'] = "Kubernetes unreachable"

            result.append(app_data)

        return Response(result, status=status.HTTP_200_OK)


class AppDetailView(APIView):

    def put(self, request, pk):
        try:
            app_obj = App.objects.get(pk=pk)
        except App.DoesNotExist:
            return Response({"error": "App not found in database."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AppSerializer(app_obj, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        ns_obj = app_obj.namespace
        cluster_obj = ns_obj.cluster

        try:
            configuration = client.Configuration()
            addr = cluster_obj.address if cluster_obj.address.startswith("http") else f"https://{cluster_obj.address}"
            configuration.host = addr
            configuration.api_key['authorization'] = f"Bearer {cluster_obj.token}"
            configuration.verify_ssl = False

            api_client = client.ApiClient(configuration)
            apps_api = AppsV1Api(api_client)

            patch_body = {
                "spec": {
                    "replicas": serializer.validated_data.get('replicas', app_obj.replicas),
                    "template": {
                        "spec": {
                            "containers": [{
                                "name": app_obj.name,
                                "image": serializer.validated_data.get('image', app_obj.image),
                                "resources": {
                                    "limits": {
                                        "cpu": serializer.validated_data.get('cpu', app_obj.cpu),
                                        "memory": serializer.validated_data.get('memory', app_obj.memory)
                                    }
                                }
                            }]
                        }
                    }
                }
            }

            apps_api.patch_namespaced_deployment(name=app_obj.name, namespace=ns_obj.name, body=patch_body)

        except client.exceptions.ApiException as e:
            return Response({"error": f"Kubernetes API error: {e.reason}"}, status=status.HTTP_502_BAD_GATEWAY)
        except Exception:
            return Response({"error": "Could not connect to Kubernetes cluster."}, status=status.HTTP_502_BAD_GATEWAY)

        updated_app = serializer.save()
        return Response(AppSerializer(updated_app).data, status=status.HTTP_200_OK)


    def delete(self, request, pk):
        try:
            app_obj = App.objects.get(pk=pk)
        except App.DoesNotExist:
            return Response({"error": "App not found in database."}, status=status.HTTP_404_NOT_FOUND)

        ns_obj = app_obj.namespace
        cluster_obj = ns_obj.cluster

        try:
            configuration = client.Configuration()
            addr = cluster_obj.address if cluster_obj.address.startswith("http") else f"https://{cluster_obj.address}"
            configuration.host = addr
            configuration.api_key['authorization'] = f"Bearer {cluster_obj.token}"
            configuration.verify_ssl = False

            api_client = client.ApiClient(configuration)
            apps_api = AppsV1Api(api_client)

            apps_api.delete_namespaced_deployment(name=app_obj.name, namespace=ns_obj.name)

        except client.exceptions.ApiException as e:
            if e.status != 404:
                return Response({"error": f"Kubernetes API error: {e.reason}"}, status=status.HTTP_502_BAD_GATEWAY)
        except Exception:
            return Response({"error": "Could not connect to Kubernetes cluster."}, status=status.HTTP_502_BAD_GATEWAY)

        app_obj.delete()
        return Response({"message": "App deleted successfully."}, status=status.HTTP_200_OK)