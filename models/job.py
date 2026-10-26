from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text
from database.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)
    company = Column(String)
    location = Column(String)
    salary = Column(String)

    url = Column(String, unique=True, nullable=False)
    source = Column(String)
    description = Column(String)

    # Status tracking with explicit choices
    STATUS_CHOICES = [
        "Saved",
        "Viewed",
        "Preparing",
        "Applied",
        "Confirmation Needed",
        "Interview",
        "Rejected",
        "Offer",
        "Withdrawn",
    ]

    status = Column(
        String,
        default="Saved",
    )

    date_found = Column(DateTime, default=datetime.utcnow)
    date_applied = Column(DateTime, nullable=True)
    date_status_changed = Column(DateTime, default=datetime.utcnow)

    notes = Column(String, nullable=True)

    # Application tracking
    application_count = Column(Integer, default=0)

    # Suitability scoring
    suitability_score = Column(Integer, default=0)  # 0-100
    suitability_factors = Column(Text, default="")  # JSON breakdown of match factors
    missing_requirements = Column(Text, default="")  # JSON list of mandatory reqs not met