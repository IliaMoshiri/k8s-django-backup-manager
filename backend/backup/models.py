import uuid
from django.db import models
from clusters.models import App

class BackupTask(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    backup_id = models.CharField(max_length=50, unique=True, primary_key=True)
    app = models.ForeignKey(App, on_delete=models.CASCADE, related_name='backups')
    source_path = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    file_path = models.CharField(max_length=255, blank=True, null=True)
    schedule = models.CharField(max_length=100, blank=True, null=True)  # Cron Expression
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.backup_id:
            self.backup_id = f"bkp_{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.backup_id} - App {self.app_id} ({self.status})"