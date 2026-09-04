# 🚀 Kubernetes & Django Backup Management Platform

A production-ready, cloud-native backup orchestration platform for managing, scheduling, executing, and tracking backup operations.

The platform features a **Django REST Framework (DRF)** backend, **React Single Page Application (SPA)**, **Celery asynchronous task processing**, and **PostgreSQL database**, fully orchestrated on a **Kubernetes (K3s)** cluster using **Traefik Ingress Controller**.

---

## 📌 Overview & Architecture

This platform provides asynchronous backup management for containerized workloads.

Long-running archiving and backup operations are offloaded to background **Celery workers** through **Redis**, preventing them from blocking standard API requests. Kubernetes manages container execution, service discovery, workload orchestration, and internal networking, while Traefik handles external ingress traffic and path-based routing.

### 🌐 Cluster Traffic Architecture

```text
                                  [ Public Internet ]
                                           │
                                           ▼
                      [ Traefik Ingress Controller (Port 80) ]
                       │ (Host: moshiri.osdl.ir)          │
          Path: /      │                                  │ Path: /api & /admin
                       ▼                                  ▼
      [ Frontend Service (ClusterIP) ]            [ Backend Service (ClusterIP) ]
                       │                                  │
                       ▼                                  ▼
             [ Frontend Pod (Nginx) ]             [ Backend Pod (Django) ]
                                                   │          │
                                   Database Conn   │          │ Task Queue
                                                   ▼          ▼
                                       [ PostgreSQL Pod ]  [ Redis Pod ]
                                                              │
                                                              ▼
                                                     [ Celery Worker Pod ]
```

### 🔄 Request & Task Flow

```text
Client
  │
  ▼
Traefik Ingress
  │
  ├── / ────────────────► Frontend
  │
  └── /api, /admin ─────► Django Backend
                              │
                              ├──► PostgreSQL
                              │
                              └──► Redis
                                     │
                                     ▼
                               Celery Worker
                                     │
                                     ▼
                              Backup Operation
```

---

## ✨ Key Features

* ⚡ Asynchronous backup execution
* 📅 Scheduled backups using Cron expressions
* 📊 Backup job status tracking
* 🔎 Backup filtering by Application ID
* 🌐 RESTful API with Django REST Framework
* 🖥️ React-based Single Page Application
* 🐳 Fully containerized with Docker
* ☸️ Kubernetes-native deployment
* 🚦 Traefik-based ingress and path routing
* 🗄️ PostgreSQL persistent database
* 🔄 Redis message broker
* ⚙️ Celery background workers
* 🔐 Kubernetes Secrets for sensitive database credentials

---

## 🛠️ Complete Tech Stack

| Category             | Technology                        | Purpose                                         |
| :------------------- | :-------------------------------- | :---------------------------------------------- |
| **Frontend**         | React, Vite                       | Single Page Application                         |
| **Web Server**       | Nginx                             | Production frontend serving                     |
| **Backend API**      | Django 6.1, Django REST Framework | REST API and business logic                     |
| **Async Processing** | Celery 5.6.3                      | Background backup task execution                |
| **Message Broker**   | Redis                             | Celery task queue and result backend            |
| **Database**         | PostgreSQL 15 (Alpine)            | Persistent relational data storage              |
| **Orchestration**    | Kubernetes (K3s)                  | Container orchestration and workload management |
| **Ingress**          | Traefik                           | Reverse proxy and path-based routing            |
| **Containerization** | Docker                            | Application containerization                    |

---

# ☁️ Kubernetes Deployment Guide

The application is designed to run on a **Kubernetes (K3s)** cluster.

## 1. Create Database Secret

Create a Kubernetes Secret to securely store the PostgreSQL password:

```bash
kubectl create secret generic postgres-secret \
  --from-literal=password=YOUR_SECURE_PASSWORD
```

Replace `YOUR_SECURE_PASSWORD` with your actual secure database password.

---

## 2. Build and Push Container Images

### Backend

```bash
docker build -t iliamosh/backup-backend:v1 ./backend
docker push iliamosh/backup-backend:v1
```

### Frontend

```bash
docker build -t iliamosh/backup-frontend:v1 ./frontend
docker push iliamosh/backup-frontend:v1
```

---

## 3. Deploy Kubernetes Manifests

Deploy the application workloads and services:

```bash
kubectl apply -f k8s/app.yaml
```

Apply the Traefik ingress routing rules:

```bash
kubectl apply -f k8s/ingress.yaml
```

Verify the deployment:

```bash
kubectl get pods
kubectl get services
kubectl get ingress
```

---

## 4. Run Database Migrations

Execute Django migrations inside the backend deployment:

```bash
kubectl exec -it deployment/backend -- \
  python manage.py migrate
```

---

## 5. Collect Static Files

```bash
kubectl exec -it deployment/backend -- \
  python manage.py collectstatic --noinput
```

---

# 🔗 API Reference & Endpoints

All public API requests are exposed through the Traefik Ingress:

```text
http://moshiri.osdl.ir
```

| Method | Endpoint                   | Description                                            | Request Body / Query     |
| :----- | :------------------------- | :----------------------------------------------------- | :----------------------- |
| `POST` | `/api/backup/`             | Trigger an instant backup or create a scheduled backup | JSON body                |
| `GET`  | `/api/backup/<id>/`        | Query the status of a specific backup job              | —                        |
| `GET`  | `/api/backup/?app_id=<id>` | List backups for a specific application                | `app_id` query parameter |
| `GET`  | `/admin/`                  | Django administrative panel                            | —                        |

---

## 📦 Create an Instant Backup

### Endpoint

```text
POST /api/backup/
```

### Request

```json
{
  "app_id": 1,
  "source_path": "/var/lib/myapp/data.db"
}
```

---

## 📅 Schedule a Recurring Backup

The `schedule` field accepts a Cron expression.

### Endpoint

```text
POST /api/backup/
```

### Request

```json
{
  "app_id": 1,
  "source_path": "/var/lib/myapp/data.db",
  "schedule": "0 2 * * *"
}
```

The above Cron expression schedules the backup to run every day at **02:00**.

---

## 🔍 Query Backup Status

### Endpoint

```text
GET /api/backup/<backup_id>/
```

Example:

```bash
curl -X GET \
  http://moshiri.osdl.ir/api/backup/1/
```

---

# 💻 Local Development Setup

The application can also be run locally without Kubernetes.

## Prerequisites

Make sure the following are installed:

* Python 3.12+
* Node.js 18+
* PostgreSQL
* Redis
* Git

---

## 1. Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create a Python virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment:

### Linux / macOS

```bash
source venv/bin/activate
```

### Windows

```powershell
venv\Scripts\activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Create the environment configuration:

```bash
cp .env.example .env
```

Run database migrations:

```bash
python manage.py migrate
```

Start the Django development server:

```bash
python manage.py runserver 8000
```

The backend will be available at:

```text
http://localhost:8000
```

---

## 2. Celery Worker

Open a separate terminal and navigate to the backend directory:

```bash
cd backend
source venv/bin/activate
```

Start the Celery worker:

```bash
celery -A config worker --loglevel=info
```

The Celery worker is responsible for executing backup operations asynchronously.

---

## 3. Frontend Setup

Navigate to the frontend directory:

```bash
cd frontend
```

Install Node.js dependencies:

```bash
npm install
```

Start the Vite development server:

```bash
npm run dev
```

---

# 🧪 Testing the Production API

## Trigger an Instant Backup

```bash
curl -i -X POST \
  http://moshiri.osdl.ir/api/backup/ \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": 1,
    "source_path": "/var/lib/myapp/data.db"
  }'
```

---

## Schedule a Cron Backup

```bash
curl -i -X POST \
  http://moshiri.osdl.ir/api/backup/ \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": 1,
    "source_path": "/var/lib/myapp/data.db",
    "schedule": "0 2 * * *"
  }'
```

---

## Query Backup Status

```bash
curl -X GET \
  http://moshiri.osdl.ir/api/backup/<backup_id>/
```

Replace `<backup_id>` with the ID returned when the backup was created.

---

# 📂 Kubernetes Manifests

The Kubernetes configuration is located in the `k8s/` directory:

```text
k8s/
├── app.yaml
└── ingress.yaml
```

### `app.yaml`

Contains the Kubernetes resources required for the application, including:

* PostgreSQL
* Redis
* Django Backend
* React Frontend
* Celery Worker
* Kubernetes Services

### `ingress.yaml`

Contains the Traefik Ingress configuration responsible for routing external traffic:

```text
moshiri.osdl.ir/
        │
        ├── /        → Frontend
        │
        ├── /api     → Backend API
        │
        └── /admin   → Django Admin
```

---

# 🔐 Security Considerations

Sensitive credentials should not be hard-coded into the source code or container images.

The Kubernetes deployment uses **Kubernetes Secrets** for sensitive database credentials.

For local development, environment-specific configuration should be stored in `.env`.

Make sure `.env` is excluded from Git:

```gitignore
.env
venv/
__pycache__/
*.pyc
node_modules/
```

---

# 🏗️ Production Architecture Summary

The complete deployment architecture can be summarized as:

```text
                         ┌──────────────────┐
                         │     Internet     │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │     Traefik      │
                         │ Ingress Controller│
                         └────────┬─────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
             ┌─────────────┐             ┌─────────────┐
             │   Frontend  │             │   Backend   │
             │ React+Nginx │             │   Django    │
             └─────────────┘             └──────┬──────┘
                                                │
                              ┌─────────────────┼─────────────────┐
                              │                 │                 │
                              ▼                 ▼                 ▼
                       ┌────────────┐    ┌────────────┐    ┌────────────┐
                       │ PostgreSQL │    │   Redis    │    │   Celery   │
                       │  Database  │    │   Broker   │───►│   Worker   │
                       └────────────┘    └────────────┘    └────────────┘
```

---

# 🚀 Deployment Workflow

```text
Source Code
     │
     ▼
Docker Build
     │
     ▼
Docker Hub
     │
     ▼
K3s Cluster
     │
     ├── Traefik Ingress
     │
     ├── React + Nginx
     │
     ├── Django + DRF
     │
     ├── PostgreSQL
     │
     ├── Redis
     │
     └── Celery Worker
```

---

# 👨‍💻 Author

**Ilia Moshiri**

Computer Engineering Student