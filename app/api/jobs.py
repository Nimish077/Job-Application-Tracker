"""Job application CRUD endpoints.

Every route is authenticated and every query is filtered by the caller's
``user_id``, so one account can never read or mutate another account's rows.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, DbSession
from app.models.job import JobApplication, JobStatus
from app.models.user import User
from app.schemas.job import JobCreate, JobResponse, JobUpdate

router = APIRouter(prefix="/jobs", tags=["jobs"])

NOT_FOUND_DETAIL = "Job application not found."


def _get_owned_job_or_404(db: Session, job_id: int, user: User) -> JobApplication:
    """Fetch a job application, enforcing ownership in the WHERE clause.

    Looking up by ``id`` alone would let an attacker enumerate other users'
    applications, so ``user_id`` is always part of the same query. A row owned
    by someone else is reported as 404 rather than 403, which avoids confirming
    that the id exists at all.
    """
    job = db.scalar(
        select(JobApplication).where(
            JobApplication.id == job_id,
            JobApplication.user_id == user.id,
        )
    )
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=NOT_FOUND_DETAIL,
        )
    return job


@router.get(
    "/",
    response_model=list[JobResponse],
    summary="List my job applications",
)
def list_job_applications(
    db: DbSession,
    current_user: CurrentUser,
    status_filter: Annotated[
        JobStatus | None,
        Query(alias="status", description="Filter by pipeline stage."),
    ] = None,
) -> list[JobApplication]:
    """Return only the applications belonging to the authenticated user."""
    statement = select(JobApplication).where(JobApplication.user_id == current_user.id)

    if status_filter is not None:
        statement = statement.where(JobApplication.status == status_filter)

    statement = statement.order_by(JobApplication.created_at.desc(), JobApplication.id.desc())

    return list(db.scalars(statement).all())


@router.post(
    "/",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a job application",
)
def create_job_application(
    payload: JobCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> JobApplication:
    """Create an application owned by the authenticated user.

    ``user_id`` comes from the access token, never from the request body.
    """
    job = JobApplication(
        **payload.model_dump(),
        user_id=current_user.id,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    return job


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    summary="Get a single job application",
    responses={404: {"description": "Not found, or not owned by the caller."}},
)
def get_job_application(
    db: DbSession,
    current_user: CurrentUser,
    job_id: Annotated[int, Path(ge=1, description="Job application ID.")],
) -> JobApplication:
    """Return one application, provided the caller owns it."""
    return _get_owned_job_or_404(db, job_id, current_user)


@router.put(
    "/{job_id}",
    response_model=JobResponse,
    summary="Update a job application",
    responses={404: {"description": "Not found, or not owned by the caller."}},
)
def update_job_application(
    payload: JobUpdate,
    db: DbSession,
    current_user: CurrentUser,
    job_id: Annotated[int, Path(ge=1, description="Job application ID.")],
) -> JobApplication:
    """Apply a partial update.

    Only keys actually present in the request body are written, so omitted
    fields keep their stored values.
    """
    job = _get_owned_job_or_404(db, job_id, current_user)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(job, field, value)

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a job application",
    responses={
        404: {"description": "Not found, or not owned by the caller."},
        204: {"description": "Deleted."},
    },
)
def delete_job_application(
    db: DbSession,
    current_user: CurrentUser,
    job_id: Annotated[int, Path(ge=1, description="Job application ID.")],
) -> Response:
    """Delete an application owned by the caller."""
    job = _get_owned_job_or_404(db, job_id, current_user)

    db.delete(job)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
