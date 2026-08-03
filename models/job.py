from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

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

    applied = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)