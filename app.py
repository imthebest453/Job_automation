from database.database import Base, SessionLocal, engine
from models.job import Job
from scrapers.demo_scraper import DemoScraper
from services.search_service import SearchService

Base.metadata.create_all(bind=engine)

db = SessionLocal()

service = SearchService(DemoScraper())

added = service.search("IT Support", db)

print(f"{added} new jobs added.")