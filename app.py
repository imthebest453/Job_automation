from database.database import Base, SessionLocal, engine
from database.job_rep import JobRepository
from models.job import Job
from scrapers.demo_scraper import DemoScraper

Base.metadata.create_all(bind=engine)

db = SessionLocal()

scraper = DemoScraper()

jobs = scraper.search("IT Support")

for job in jobs:
    JobRepository.add_job(db, job)

print("Jobs currently in the database:\n")

for job in JobRepository.get_all_jobs(db):
    print(f"{job.title} | {job.company} | {job.location}")