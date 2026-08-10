from database.job_rep import JobRepository


class SearchService:
    def __init__(self, scraper):
        self.scraper = scraper

    def search(self, keyword, db):
        jobs = self.scraper.search(keyword)

        added = 0

        for job in jobs:
            if JobRepository.add_job(db, job):
                added += 1

        return added
    