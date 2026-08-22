from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from clusters.models import App
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
            serializer = BackupTaskSerializer(tasks, many=True)
            return Response(serializer.data)

        return Response({"error": "Provide backup_id in URL path or app_id in query params."}, status=status.HTTP_400_BAD_REQUEST)