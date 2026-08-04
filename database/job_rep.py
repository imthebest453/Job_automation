from models.job import Job


class JobRepository:


    @staticmethod
    def add_job(db, job):

        db.add(job)
        db.commit()
        db.refresh(job)

        return job



    @staticmethod
    def get_all(db):

        return db.query(Job).all()