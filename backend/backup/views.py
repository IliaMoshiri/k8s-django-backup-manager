from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from clusters.models import App, Cluster, Namespace
from .models import BackupTask
from .serializers import BackupTaskSerializer
from .tasks import process_backup_task


class BackupAPIView(APIView):

    def post(self, request):
        app_id = request.data.get('app_id')
        source_path = request.data.get('source_path')
        schedule = request.data.get('schedule')

        if not app_id or not source_path:
            return Response({"error": "app_id and source_path are required."}, status=status.HTTP_400_BAD_REQUEST)

        app_obj = get_object_or_404(App, id=app_id)

        task_obj = BackupTask.objects.create(
            app=app_obj,
            source_path=source_path,
            schedule=schedule,
            status='pending'
        )

        process_backup_task.delay(task_obj.backup_id)

        return Response({
            "backup_id": task_obj.backup_id,
            "status": task_obj.status
        }, status=status.HTTP_202_ACCEPTED)

    def get(self, request, backup_id=None):
        if backup_id:
            task_obj = get_object_or_404(BackupTask, backup_id=backup_id)
            return Response({
                "backup_id": task_obj.backup_id,
                "app_id": task_obj.app_id,
                "status": task_obj.status
            })

        app_id = request.query_params.get('app_id')
        if app_id:
            tasks = BackupTask.objects.filter(app_id=app_id)
        else:
            tasks = BackupTask.objects.all()

        serializer = BackupTaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ClusterAPIView(APIView):
    def get(self, request):
        clusters = Cluster.objects.all().values('id', 'name', 'address')
        return Response(list(clusters), status=status.HTTP_200_OK)

    def post(self, request):
        name = request.data.get('name')
        address = request.data.get('address')
        token = request.data.get('token')

        if not name:
            return Response({"error": "Name is required"}, status=status.HTTP_400_BAD_REQUEST)

        cluster = Cluster.objects.create(
            name=name,
            address=address,
            token=token
        )
        return Response({
            "id": cluster.id, 
            "name": cluster.name,
            "address": cluster.address
        }, status=status.HTTP_201_CREATED)


class NamespaceAPIView(APIView):
    def get(self, request):
        cluster_id = request.query_params.get('cluster_id')
        if cluster_id:
            namespaces = Namespace.objects.filter(cluster_id=cluster_id).values('id', 'name', 'cluster_id')
        else:
            namespaces = Namespace.objects.all().values('id', 'name', 'cluster_id')
        return Response(list(namespaces), status=status.HTTP_200_OK)

    def post(self, request):
        name = request.data.get('name')
        cluster_id = request.data.get('cluster_id') or request.data.get('cluster')

        if not name or not cluster_id:
            return Response({"error": "Name and cluster_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        cluster_obj = get_object_or_404(Cluster, id=cluster_id)
        namespace = Namespace.objects.create(name=name, cluster=cluster_obj)

        return Response({
            "id": namespace.id,
            "name": namespace.name,
            "cluster_id": namespace.cluster_id
        }, status=status.HTTP_201_CREATED)

    def delete(self, request, pk=None):
        namespace = get_object_or_404(Namespace, id=pk)
        namespace.delete()
        return Response({"message": "Namespace deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class AppAPIView(APIView):
    def get(self, request, pk=None):
        if pk:
            app_obj = get_object_or_404(App, id=pk)
            return Response({
                "id": app_obj.id,
                "name": app_obj.name,
                "image": app_obj.image,
                "replicas": app_obj.replicas,
                "cpu": app_obj.cpu,
                "memory": app_obj.memory,
                "namespace_id": app_obj.namespace_id
            }, status=status.HTTP_200_OK)

        namespace_id = request.query_params.get('namespace_id')
        if namespace_id:
            apps = App.objects.filter(namespace_id=namespace_id).values(
                'id', 'name', 'image', 'replicas', 'cpu', 'memory', 'namespace_id'
            )
        else:
            apps = App.objects.all().values(
                'id', 'name', 'image', 'replicas', 'cpu', 'memory', 'namespace_id'
            )
        return Response(list(apps), status=status.HTTP_200_OK)

    def post(self, request):
        name = request.data.get('name')
        image = request.data.get('image')
        replicas = request.data.get('replicas', 1)
        cpu = request.data.get('cpu', '100m')
        memory = request.data.get('memory', '128Mi')
        namespace_id = request.data.get('namespace_id') or request.data.get('namespace')

        if not name or not image or not namespace_id:
            return Response({"error": "name, image, and namespace_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        namespace_obj = get_object_or_404(Namespace, id=namespace_id)
        app_obj = App.objects.create(
            name=name,
            image=image,
            replicas=replicas,
            cpu=cpu,
            memory=memory,
            namespace=namespace_obj
        )

        return Response({
            "id": app_obj.id,
            "name": app_obj.name,
            "image": app_obj.image,
            "replicas": app_obj.replicas,
            "namespace_id": app_obj.namespace_id
        }, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None):
        app_obj = get_object_or_404(App, id=pk)
        app_obj.image = request.data.get('image', app_obj.image)
        app_obj.replicas = request.data.get('replicas', app_obj.replicas)
        app_obj.cpu = request.data.get('cpu', app_obj.cpu)
        app_obj.memory = request.data.get('memory', app_obj.memory)
        app_obj.save()

        return Response({
            "id": app_obj.id,
            "name": app_obj.name,
            "image": app_obj.image,
            "replicas": app_obj.replicas,
            "cpu": app_obj.cpu,
            "memory": app_obj.memory,
            "namespace_id": app_obj.namespace_id
        }, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        app_obj = get_object_or_404(App, id=pk)
        app_obj.delete()
        return Response({"message": "App deleted successfully"}, status=status.HTTP_204_NO_CONTENT)