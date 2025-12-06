# Task Manager API (Flask + JWT)

A simple, modular RESTful API for managing tasks, with JWT-based authentication, pagination, filtering, and user roles (`admin`, `user`).

## Features

- User registration & login (`/auth/register`, `/auth/login`)
- JWT authentication (`Authorization: Bearer <token>`)
- Task CRUD:
  - `GET /tasks`
  - `GET /tasks/{id}`
  - `POST /tasks`
  - `PUT /tasks/{id}`
  - `DELETE /tasks/{id}`
- Pagination: `GET /tasks?page=1&per_page=10`
- Filtering by completion: `GET /tasks?completed=true`
- Roles:
  - `admin`: can see/update/delete all tasks
  - `user`: can access only their own tasks
- Swagger documentation at `/apidocs`
- Unit tests with `pytest`

## Setup

```bash
git clone <your-repo-url>
cd task_manager_api

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt
