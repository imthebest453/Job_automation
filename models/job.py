from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
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

    status = Column(String, default="Saved")

    date_found = Column(DateTime, default=datetime.utcnow)
    date_applied = Column(DateTime, nullable=True)

    notes = Column(String, nullable=True)