"""Pydantic schemas for job application create, update and response payloads."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.job import JobStatus

__all__ = [
    "JobBase",
    "JobCreate",
    "JobResponse",
    "JobStatus",
    "JobUpdate",
]


class JobBase(BaseModel):
    """Fields a client may supply when creating a job application."""

    company_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the company.",
        examples=["Acme Corp"],
    )
    position_title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Role that was applied for.",
        examples=["Backend Engineer"],
    )
    status: JobStatus = Field(
        default=JobStatus.APPLIED,
        description="Current pipeline stage.",
        examples=[JobStatus.APPLIED],
    )
    salary_range: str | None = Field(
        default=None,
        max_length=255,
        description="Compensation range as advertised.",
        examples=["$120k - $150k"],
    )
    job_url: str | None = Field(
        default=None,
        max_length=2048,
        description="Link to the job posting.",
        examples=["https://example.com/jobs/123"],
    )
    notes: str | None = Field(
        default=None,
        description="Free-form notes about the application.",
    )

    @field_validator("company_name", "position_title", mode="before")
    @classmethod
    def _strip_required_text(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("salary_range", "job_url", mode="before")
    @classmethod
    def _blank_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("notes", mode="before")
    @classmethod
    def _trim_notes(cls, value: object) -> object:
        if value is None:
            return None
        if not isinstance(value, str):
            return value
        return value.strip() or None


class JobCreate(JobBase):
    """Payload for `POST /jobs/`."""


class JobUpdate(BaseModel):
    """Payload for `PUT /jobs/{id}`.

    Every field is optional; only the keys actually present in the request body
    are applied, so a client can PATCH-style update a single field via PUT.
    """

    company_name: str | None = Field(default=None, min_length=1, max_length=255)
    position_title: str | None = Field(default=None, min_length=1, max_length=255)
    status: JobStatus | None = None
    salary_range: str | None = Field(default=None, max_length=255)
    job_url: str | None = Field(default=None, max_length=2048)
    notes: str | None = None

    @field_validator("company_name", "position_title", mode="before")
    @classmethod
    def _strip_required_text(cls, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, str):
            cleaned = value.strip()
            if not cleaned:
                raise ValueError("Field must not be empty when provided.")
            return cleaned
        return value

    @field_validator("salary_range", "job_url", "notes", mode="before")
    @classmethod
    def _blank_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value


class JobResponse(JobBase):
    """A stored job application, including ownership and audit timestamps."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
