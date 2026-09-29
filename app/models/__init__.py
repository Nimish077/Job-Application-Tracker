"""SQLAlchemy ORM models.

Every model is imported here so that ``Base.metadata`` is fully populated
before Alembic performs autogeneration.
"""

from app.models.job import JobApplication, JobStatus
from app.models.user import User

__all__ = ["JobApplication", "JobStatus", "User"]
