from rest_framework import serializers
from .models import BackupTask

class BackupTaskSerializer(serializers.ModelSerializer):
    app_id = serializers.IntegerField()

    class Meta:
        model = BackupTask
        fields = ['backup_id', 'app_id', 'source_path', 'status', 'schedule', 'file_path', 'created_at']
        read_only_fields = ['backup_id', 'status', 'file_path', 'created_at']