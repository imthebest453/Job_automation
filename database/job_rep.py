from sqlalchemy.orm import Session
from models.job import Job


class JobRepository:

    @staticmethod
    def add_job(db: Session, job_data: dict):

        existing = db.query(Job).filter(Job.url == job_data["url"]).first()

        if existing:
            return False

        job = Job(**job_data)

        db.add(job)
        db.commit()

        return True

    @staticmethod
    def get_all_jobs(db: Session):

        return db.query(Job).all()