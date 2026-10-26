from abc import ABC, abstractmethod
from datetime import datetime

from sqlalchemy.orm import Session

from models.job import Job


class BaseScraper(ABC):

    @abstractmethod
    def search(self, keyword: str):
        """Return a list of job dictionaries."""
        pass


class JobRepository:

    @staticmethod
    def add_job(db: Session, job):

        existing = db.query(Job).filter(
            Job.url == job.url
        ).first()

        if existing:
            return False

        db.add(job)
        db.commit()

        return True

    @staticmethod
    def get_all_jobs(db: Session):

        return db.query(Job).all()

    @staticmethod
    def search_jobs(db: Session, keyword: str):

        return db.query(Job).filter(
            (Job.title.ilike(f"%{keyword}%")) |
            (Job.company.ilike(f"%{keyword}%"))
        ).all()

    @staticmethod
    def update_status(db: Session, job_id: int, status: str):

        from datetime import datetime

        job = db.query(Job).filter(
            Job.id == job_id
        ).first()

        if not job:
            return False

        # Validate status is one of the allowed choices
        valid_statuses = [
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
        if status not in valid_statuses:
            raise ValueError(
                f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}"
            )

        job.status = status
        job.date_status_changed = datetime.utcnow()

        db.commit()

        return True

    @staticmethod
    def get_applied_jobs(db: Session):

        return db.query(Job).filter(
            Job.status == "Applied"
        ).all()

    @staticmethod
    def get_by_status(db: Session, status: str):

        return db.query(Job).filter(
            Job.status == status
        ).all()

    @staticmethod
    def get_recent_jobs(db: Session, limit: int = 10):

        return db.query(Job).order(
            Job.date_found.desc()
        ).limit(limit).all()

    @staticmethod
    def get_suitable_jobs(db: Session, min_score: int = 0):

        """Get jobs that are suitable based on scoring - to be extended."""
        return db.query(Job).filter(
            Job.status.in_(["Saved", "Preparing", "Applied"])
        ).all()