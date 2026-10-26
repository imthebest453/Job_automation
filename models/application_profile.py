from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text

from database.database import Base


class ApplicationProfile(Base):
    __tablename__ = "application_profile"

    id = Column(Integer, primary_key=True)

    full_name = Column(String)
    email = Column(String)
    phone = Column(String)

    address = Column(String)
    city = Column(String)
    postcode = Column(String)

    cv_path = Column(String)

    skills = Column(Text)
    experience = Column(Text)
    education = Column(Text)

    # Additional identifier fields
    national_insurance = Column(String, default="")
    right_to_work = Column(String, default="")
    availability_date = Column(String, default="")

    # Preferences
    preferred_roles = Column(Text, default="")
    preferred_locations = Column(Text, default="")
    job_types = Column(String, default="")  # full-time, part-time, contract, etc.
    salary_expectations = Column(String, default="")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)