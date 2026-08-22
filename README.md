# Kubernetes & Django Backup Management API

A robust RESTful API built with **Django REST Framework (DRF)**, **Celery**, and **Redis** for managing and executing asynchronous application backups in a containerized/Kubernetes environment.

---

## 📌 Project Overview
This repository contains the full implementation for both phases of the project:
* **Phase 1:** Architectural specs and core system requirements.
* **Phase 2:** Backup API guidelines, async processing, and scheduling.

The API provides immediate backup execution via background task queues and supports status tracking and scheduled backups.

---

## 🚀 Key Features

* **Asynchronous Backup Execution:** Offloads heavy file archiving tasks to Celery workers, returning immediate `202 Accepted` responses.
* **Status Tracking:** Query backup states (`pending`, `completed`, `failed`) at any time.
* **Structured Archiving:** Saves generated archives systematically under:
  `/tmp/backups/{app_id}/{yyyy-mm-dd}/{backup_id}.tar.gz`
* **Periodic Scheduling Support:** Accepts Cron expressions (e.g., `0 2 * * *`) for automated background execution.
* **Redis Caching & Brokerage:** Uses Redis as both the task message broker and result backend.

---

## 🛠️ Tech Stack

* **Framework:** Django 6.1 / Django REST Framework
* **Task Queue:** Celery 5.6.3
* **Broker & Cache:** Redis
* **Database:** SQLite (Local Development)
* **Language:** Python 3.12

---

## 🔗 API Endpoints Summary

| Method | Endpoint | Description | Request Body / Query Params |
| :--- | :--- | :--- | :--- |
| **POST** | `/backup/` | Trigger instant backup / Schedule cron backup | `{"app_id": 1, "source_path": "/var/lib/myapp/data.db", "schedule": "0 2 * * *"}` |
| **GET** | `/backup/<backup_id>/` | Query status of a specific backup | N/A |
| **GET** | `/backup/?app_id=<id>` | List all backups for a specific application | `app_id` (Query Param) |

---

## 💻 Local Setup Guide

### 1. Prerequisites
Ensure you have Python 3.12+ and Redis Server installed on your system.

### 2. Environment Setup
```bash
# Clone the repository
git clone [https://github.com/YOUR_USERNAME/k8s-django-backup-manager.git](https://github.com/YOUR_USERNAME/k8s-django-backup-manager.git)
cd k8s-django-backup-manager

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database & Services
```bash
# Start Redis service
sudo service redis-server start

# Apply Django migrations
python manage.py migrate
```

### 4. Running the Application
Open two separate terminal windows:

* **Terminal 1 (Django Server):**
```bash
  python manage.py runserver 8000
```

* **Terminal 2 (Celery Worker):**
```bash
  celery -A config worker --loglevel=info
```

## 🧪 Testing the API

### Trigger Instant Backup
```bash
curl -i -X POST [http://127.0.0.1:8000/backup/](http://127.0.0.1:8000/backup/) \
     -H "Content-Type: application/json" \
     -d '{"app_id": 1, "source_path": "/var/lib/myapp/data.db"}'
```

### Trigger Scheduled Backup (Cron)
```bash
curl -i -X POST [http://127.0.0.1:8000/backup/](http://127.0.0.1:8000/backup/) \
     -H "Content-Type: application/json" \
     -d '{"app_id": 1, "source_path": "/var/lib/myapp/data.db", "schedule": "0 2 * * *"}'
```

### Check Backup Status
```bash
curl [http://127.0.0.1:8000/backup/](http://127.0.0.1:8000/backup/)<backup_id>/
```

### List All Backups for an Application
```bash
curl "[http://127.0.0.1:8000/backup/?app_id=1](http://127.0.0.1:8000/backup/?app_id=1)"
```
