# SyncFlow

> A real-time synchronization backend built with FastAPI.

SyncFlow is a backend-focused project inspired by collaborative platforms like **Google Docs**, **Notion**, and **Figma Multiplayer**.

Rather than building a full collaborative editor, SyncFlow focuses on the infrastructure that powers real-time applications, including:

- Persistent WebSocket connections
- Real-time event broadcasting
- Connection lifecycle management
- User presence tracking
- Synchronization between connected clients

The goal of this project is to explore the engineering challenges behind scalable real-time systems while keeping the frontend intentionally lightweight.

---

## Features

- ⚡ Real-time communication using WebSockets
- 👥 Live user presence tracking
- 📡 Event broadcasting to connected clients
- 🔄 Connection management
- 🗄 PostgreSQL persistence
- 🎨 Server-rendered UI using Jinja2 + HTMX
- 💨 Tailwind CSS v4
- 🐳 Dockerized production setup
- 🔄 Alembic database migrations

---

## Tech Stack

### Backend

- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL

### Frontend

- Jinja2
- HTMX
- Tailwind CSS v4

### Development

- uv (package manager)
- Docker
- Docker Compose

> **Note**
>
> Development uses **uv** for dependency management because of its excellent performance.
> Production images use **pip** inside Docker for broader compatibility and a simpler deployment process.

---

## Project Structure

```text
.
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── ...
│
├── static/
├── templates/
├── alembic/
├── Dockerfile
├── docker-compose.yml
└── ...
```

---

## Getting Started

### Clone the repository

```bash
git clone https://github.com/maruf-hossen-5566/syncflow.git

cd syncflow
```

---

### Install dependencies

Using **uv**

```bash
uv sync
```

or with pip

```bash
pip install -r requirements.txt
```

---

### Environment Variables

Create a `.env` file.

```env
PROJECT_NAME=syncflow

ADMIN_USER=postgres
ADMIN_PASSWORD=password

DATABASE_URL=postgresql://postgres:password@localhost:5432/syncflow_db
```

---

### Run PostgreSQL

```bash
docker compose up -d db
```

---

### Run database migrations

```bash
alembic upgrade head
```

---

### Run Tailwind

Development

```bash
npm run dev:css
```

Production build

```bash
npm run build:css
```

---

### Run FastAPI

```bash
uv run uvicorn app.main:app --reload
```

or

```bash
uvicorn app.main:app --reload
```

---

## Docker

Build

```bash
docker compose build
```

Start

```bash
docker compose up
```

The production Docker image uses a **multi-stage build**:

1. Build Tailwind CSS using Node.js
2. Generate a minified production stylesheet
3. Build the FastAPI image
4. Copy only the generated CSS into the final image

This keeps the runtime image lightweight by excluding Node.js and development dependencies.

---

Built as a backend engineering project to explore the design and implementation of real-time synchronization systems using FastAPI, WebSockets, PostgreSQL, and modern Python tooling.