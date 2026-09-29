"""Job application ORM model and its status enum."""

from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


def _utcnow() -> datetime:
    """Timezone-aware UTC now, used for ``created_at`` / ``updated_at``."""
    return datetime.now(timezone.utc)


class JobStatus(str, enum.Enum):
    """Pipeline stage of a tracked job application."""

    APPLIED = "Applied"
    INTERVIEWING = "Interviewing"
    OFFER = "Offer"
    REJECTED = "Rejected"


# `values_callable` stores the human-readable value ("Applied") rather than the
# member name ("APPLIED") in the database.
job_status_enum = SAEnum(
    JobStatus,
    name="job_status",
    values_callable=lambda enum_cls: [member.value for member in enum_cls],
    validate_strings=True,
)


class JobApplication(Base):
    """A single job application, always scoped to exactly one user."""

    __tablename__ = "job_applications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    position_title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[JobStatus] = mapped_column(
        job_status_enum,
        default=JobStatus.APPLIED,
        nullable=False,
    )
    salary_range: Mapped[str | None] = mapped_column(String(255), nullable=True)
    job_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        onupdate=_utcnow,
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="jobs")

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return (
            f"<JobApplication id={self.id} user_id={self.user_id} "
            f"company={self.company_name!r} status={self.status!r}>"
        )
