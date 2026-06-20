# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from celery import Celery

from app.config import settings
from app.core.logging import configure_logging

configure_logging()

celery_app = Celery(
    "octorig",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    # Fetch one task at a time so lab_ops workers don't hoard jobs they can't start
    worker_prefetch_multiplier=1,
    # Ack only after the task completes so a worker crash re-queues the task
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    # Dedicated queues so slow Docker ops (lab_ops) can't starve the scheduler queue
    task_routes={
        "app.worker.tasks.execute_deploy": {"queue": "lab_ops"},
        "app.worker.tasks.execute_destroy": {"queue": "lab_ops"},
        "app.worker.tasks.auto_destroy_dynamic_labs": {"queue": "lab_ops"},
        "app.worker.tasks.cleanup_stale_deployments": {"queue": "lab_ops"},
        "app.worker.tasks.dispatch_due_actions": {"queue": "scheduler"},
    },
    beat_schedule={
        "dispatch-due-scheduled-actions": {
            "task": "app.worker.tasks.dispatch_due_actions",
            "schedule": 60.0,
            "options": {"queue": "scheduler"},
        },
        "auto-destroy-dynamic-labs": {
            "task": "app.worker.tasks.auto_destroy_dynamic_labs",
            "schedule": 60.0,
            "options": {"queue": "lab_ops"},
        },
        "cleanup-stale-deployments": {
            "task": "app.worker.tasks.cleanup_stale_deployments",
            "schedule": 300.0,   # every 5 minutes
            "options": {"queue": "lab_ops"},
        },
    },
)
