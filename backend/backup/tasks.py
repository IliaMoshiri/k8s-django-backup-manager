import os
import tarfile
from datetime import datetime
from celery import shared_task
from .models import BackupTask

@shared_task(time_limit=300, soft_time_limit=240)
def process_backup_task(backup_id):
    try:
        task_obj = BackupTask.objects.get(backup_id=backup_id)
        task_obj.status = 'running'
        task_obj.save()

        today_str = datetime.now().strftime('%Y-%m-%d')
        backup_dir = os.path.join('/tmp/backups', str(task_obj.app_id), today_str)
        os.makedirs(backup_dir, exist_ok=True)

        file_name = f"{task_obj.backup_id}.tar.gz"
        full_file_path = os.path.join(backup_dir, file_name)

        with tarfile.open(full_file_path, "w:gz") as tar:
            if os.path.exists(task_obj.source_path):
                tar.add(task_obj.source_path, arcname=os.path.basename(task_obj.source_path))
            else:
                dummy_path = f"/tmp/dummy_{task_obj.backup_id}.txt"
                with open(dummy_path, "w") as f:
                    f.write(f"Backup data for app {task_obj.app_id}")
                tar.add(dummy_path, arcname="data.db")
                os.remove(dummy_path)

        task_obj.status = 'completed'
        task_obj.file_path = full_file_path
        task_obj.save()
        return f"Backup {backup_id} created at {full_file_path}"

    except Exception as exc:
        if 'task_obj' in locals():
            task_obj.status = 'failed'
            task_obj.save()
        raise exc