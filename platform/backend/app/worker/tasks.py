# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""
Celery tasks for scheduled lab actions.

Queue model:
  - scheduler: dispatch_due_actions (fast, cron-like)
  - lab_ops:   execute_deploy, execute_destroy, auto_destroy_dynamic_labs,
               cleanup_stale_deployments (slow, Docker-bound)

Worker invocation:
  celery -A app.worker.celery_app worker -Q lab_ops --concurrency=4
  celery -A app.worker.celery_app worker -Q scheduler --concurrency=2 --beat
"""
from datetime import UTC, datetime, timedelta

from app.worker.celery_app import celery_app


@celery_app.task(name="app.worker.tasks.dispatch_due_actions")
def dispatch_due_actions() -> None:
    from app.database import SessionLocal
    from app.models.scheduled_action import ScheduledAction, ScheduledActionStatus

    db = SessionLocal()
    try:
        now = datetime.now(UTC)
        due = (
            db.query(ScheduledAction)
            .filter(
                ScheduledAction.status == ScheduledActionStatus.PENDING,
                ScheduledAction.scheduled_at <= now,
            )
            .all()
        )
        for action in due:
            action.status = ScheduledActionStatus.EXECUTING
            db.commit()
            if action.action.value == "destroy" and action.deployment_id:
                execute_destroy.apply_async(args=[action.id], queue="lab_ops")
            elif action.action.value == "deploy" and action.lab_template_id:
                execute_deploy.apply_async(args=[action.id], queue="lab_ops")
            else:
                action.status = ScheduledActionStatus.FAILED
                action.error_message = "Missing target (deployment_id or lab_template_id)"
                action.executed_at = now
                db.commit()
    finally:
        db.close()


@celery_app.task(
    name="app.worker.tasks.execute_destroy",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
)
def execute_destroy(self, scheduled_action_id: int) -> None:
    from app.database import SessionLocal
    from app.models.scheduled_action import ScheduledAction, ScheduledActionStatus
    from app.services import audit_service, lab_service

    db = SessionLocal()
    try:
        action = db.get(ScheduledAction, scheduled_action_id)
        if action is None:
            return

        now = datetime.now(UTC)
        try:
            lab_service.stop_lab(action.deployment_id, action.user_id)
            action.status = ScheduledActionStatus.COMPLETED
            action.executed_at = now
            db.commit()
            audit_service.write_audit(
                db,
                action=audit_service.SCHEDULE_EXECUTED,
                user_id=action.user_id,
                team_id=action.team_id,
                deployment_id=action.deployment_id,
                detail={"scheduled_action_id": scheduled_action_id, "action": "destroy"},
            )
        except Exception as exc:
            try:
                raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))
            except self.MaxRetriesExceededError:
                action.status = ScheduledActionStatus.FAILED
                action.error_message = str(exc)
                action.executed_at = now
                db.commit()
    finally:
        db.close()


@celery_app.task(
    name="app.worker.tasks.execute_deploy",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
)
def execute_deploy(self, scheduled_action_id: int) -> None:
    from app.database import SessionLocal
    from app.labs.registry import REGISTRY_BY_ID
    from app.models.lab_template import LabTemplate
    from app.models.scheduled_action import ScheduledAction, ScheduledActionStatus
    from app.services import audit_service, lab_service
    from app.services.deployment_provisioning import prepare_deployment

    db = SessionLocal()
    try:
        action = db.get(ScheduledAction, scheduled_action_id)
        if action is None:
            return

        now = datetime.now(UTC)
        try:
            template = (
                db.query(LabTemplate)
                .filter(LabTemplate.id == action.lab_template_id)
                .with_for_update()
                .first()
            )
            if template is None:
                raise ValueError("Lab template not found")

            lab_def = REGISTRY_BY_ID.get(template.id)
            if lab_def is None:
                raise ValueError("Lab definition missing from registry")

            if action.team_id is not None:
                existing = lab_service.get_active_deployment(db, template.id, team_id=action.team_id)
            else:
                existing = lab_service.get_active_deployment(db, template.id, started_by_id=action.user_id)
            if existing:
                raise ValueError(f"You already have an active deployment of this lab (id={existing.id})")

            deployment = prepare_deployment(
                db,
                template,
                lab_def,
                started_by_id=action.user_id,
                team_id=action.team_id,
            )
            db.commit()
            db.refresh(deployment)

            action.deployment_id = deployment.id
            action.status = ScheduledActionStatus.COMPLETED
            action.executed_at = now
            db.commit()

            lab_service.start_lab(deployment.id, action.user_id)

            audit_service.write_audit(
                db,
                action=audit_service.SCHEDULE_EXECUTED,
                user_id=action.user_id,
                team_id=action.team_id,
                deployment_id=deployment.id,
                detail={"scheduled_action_id": scheduled_action_id, "action": "deploy"},
            )
        except Exception as exc:
            try:
                raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))
            except self.MaxRetriesExceededError:
                action.status = ScheduledActionStatus.FAILED
                action.error_message = str(exc)
                action.executed_at = now
                db.commit()
    finally:
        db.close()


@celery_app.task(name="app.worker.tasks.auto_destroy_dynamic_labs")
def auto_destroy_dynamic_labs() -> None:
    """Destroy dynamic lab deployments that have passed their auto_destroy_at timestamp."""
    from app.database import SessionLocal
    from app.models.deployment import Deployment, DeploymentStatus
    from app.services import lab_service

    db = SessionLocal()
    try:
        now = datetime.now(UTC)
        expired = (
            db.query(Deployment)
            .filter(
                Deployment.dynamic_flag.isnot(None),
                Deployment.auto_destroy_at.isnot(None),
                Deployment.auto_destroy_at <= now,
                Deployment.status == DeploymentStatus.RUNNING,
            )
            .all()
        )
        for deployment in expired:
            lab_service.stop_lab(deployment.id, deployment.started_by_id)
    finally:
        db.close()


@celery_app.task(name="app.worker.tasks.cleanup_stale_deployments")
def cleanup_stale_deployments() -> None:
    """Mark deployments stuck in STARTING > 15 minutes as ERROR.

    Handles the case where the backend process was killed mid-deployment,
    leaving containers running but the DB status never advancing to RUNNING.
    """
    from app.database import SessionLocal
    from app.models.deployment import Deployment, DeploymentStatus
    from app.ws.manager import emit as ws_emit

    db = SessionLocal()
    try:
        cutoff = datetime.now(UTC) - timedelta(minutes=15)
        stale = (
            db.query(Deployment)
            .filter(
                Deployment.status == DeploymentStatus.STARTING,
                Deployment.created_at <= cutoff,
            )
            .all()
        )
        for deployment in stale:
            deployment.status = DeploymentStatus.ERROR
            deployment.error_message = "Deployment timed out in STARTING state (orphan cleanup)"
            db.commit()
            ws_emit("deployment.update", {
                "id": deployment.id,
                "lab_template_id": deployment.lab_template_id,
                "status": "error",
                "error_message": deployment.error_message,
            })
    finally:
        db.close()
