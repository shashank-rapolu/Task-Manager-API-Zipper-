# app/tasks/routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from

from app.extensions import db
from app.models import Task

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


def current_user():
    """
    Helper to get current user identity from JWT.
    Returns a dict like {"id": <user_id>, "role": "<role>"}.
    """
    return get_jwt_identity()


def is_admin(identity: dict) -> bool:
    """
    Check if the current user identity has admin role.
    """
    return identity.get("role") == "admin"


@tasks_bp.get("")
@jwt_required()
@swag_from({
    "tags": ["Tasks"],
    "summary": "List tasks with pagination and filtering",
    "parameters": [
        {
            "name": "page",
            "in": "query",
            "schema": {"type": "integer", "default": 1},
            "description": "Page number for pagination"
        },
        {
            "name": "per_page",
            "in": "query",
            "schema": {"type": "integer", "default": 10},
            "description": "Number of tasks per page"
        },
        {
            "name": "completed",
            "in": "query",
            "schema": {"type": "string", "enum": ["true", "false"]},
            "description": "Filter by completed status"
        }
    ],
    "responses": {
        "200": {
            "description": "List of tasks"
        }
    }
})
def list_tasks():
    """
    Get all tasks for the current user.
    Admins can see all tasks.
    Supports pagination and filtering by completion status.
    """
    identity = current_user()
    user_id = identity.get("id")
    admin = is_admin(identity)

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    completed_param = request.args.get("completed", type=str)

    query = Task.query

    # Regular user: only their own tasks; admin: all tasks
    if not admin:
        query = query.filter_by(user_id=user_id)

    # Optional filtering by completed=true/false
    if completed_param is not None:
        if completed_param.lower() == "true":
            query = query.filter_by(completed=True)
        elif completed_param.lower() == "false":
            query = query.filter_by(completed=False)

    pagination = query.order_by(Task.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    tasks = [task.to_dict() for task in pagination.items]

    return jsonify({
        "tasks": tasks,
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
        "per_page": pagination.per_page
    }), 200


@tasks_bp.get("/<int:task_id>")
@jwt_required()
def get_task(task_id: int):
    """
    Get a single task by ID.
    Only the task owner or admin can see it.
    """
    identity = current_user()
    user_id = identity.get("id")
    admin = is_admin(identity)

    task = Task.query.get_or_404(task_id)

    # Authorization check
    if not admin and task.user_id != user_id:
        return jsonify({"message": "You are not allowed to view this task"}), 403

    return jsonify(task.to_dict()), 200


@tasks_bp.post("")
@jwt_required()
def create_task():
    """
    Create a new task for the current user.
    """
    identity = current_user()
    user_id = identity.get("id")

    data = request.get_json() or {}
    title = data.get("title")
    description = data.get("description", "")

    if not title:
        return jsonify({"message": "title is required"}), 400

    task = Task(
        title=title,
        description=description,
        completed=False,
        user_id=user_id
    )

    db.session.add(task)
    db.session.commit()

    return jsonify(task.to_dict()), 201


@tasks_bp.put("/<int:task_id>")
@jwt_required()
def update_task(task_id: int):
    """
    Update an existing task.
    Only the task owner or admin can update.
    """
    identity = current_user()
    user_id = identity.get("id")
    admin = is_admin(identity)

    task = Task.query.get_or_404(task_id)

    if not admin and task.user_id != user_id:
        return jsonify({"message": "You are not allowed to update this task"}), 403

    data = request.get_json() or {}
    title = data.get("title")
    description = data.get("description")
    completed = data.get("completed")

    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if completed is not None:
        task.completed = bool(completed)

    db.session.commit()

    return jsonify(task.to_dict()), 200


@tasks_bp.delete("/<int:task_id>")
@jwt_required()
def delete_task(task_id: int):
    """
    Delete a task.
    Only the task owner or admin can delete.
    """
    identity = current_user()
    user_id = identity.get("id")
    admin = is_admin(identity)

    task = Task.query.get_or_404(task_id)

    if not admin and task.user_id != user_id:
        return jsonify({"message": "You are not allowed to delete this task"}), 403

    db.session.delete(task)
    db.session.commit()

    return jsonify({"message": "Task deleted"}), 200
