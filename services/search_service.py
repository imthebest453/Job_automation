from services.job_connectors import (
    JobListing,
    SearchFilters,
    JobBoardConnector,
    get_connector,
    CONNECTOR_REGISTRY,
)
from services.matching_service import get_suitable_jobs, calculate_suitability


class SearchService:
    def __init__(self, connector_name: str = "Demo"):
        self.connector = get_connector(connector_name)
        if not self.connector:
            from services.job_connectors import init_connectors
            init_connectors()
            self.connector = get_connector(connector_name)

    def search(self, keyword: str, db) -> int:
        """Search for jobs using the configured connector.

        Returns the number of new jobs added to the database.
        """

        if not self.connector:
            print("No connector available")
            return 0

        # Convert keyword to search filters
        filters = SearchFilters(keyword=keyword)

        # Search using the connector
        listings = self.connector.search(filters)

        added = 0

        for listing in listings:
            try:
                job = listing.to_model()
                # Check for duplicate by URL
                from database.database import SessionLocal
                from models.job import Job as JobModel

                db = SessionLocal()
                existing = db.query(JobModel).filter(
                    JobModel.url == job.url
                ).first()

                if not existing:
                    db.add(job)
                    db.commit()
                    added += 1
                db.close()

            except Exception as e:
                print(f"Error adding job from {listing.source}: {e}")
                db.close() if 'db' in dir() else None
                continue

        return added