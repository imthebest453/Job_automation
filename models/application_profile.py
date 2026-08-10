from sqlalchemy import Column, Integer, String, Text
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