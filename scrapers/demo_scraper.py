from scrapers.base_scraper import BaseScraper


class DemoScraper(BaseScraper):

    def search(self, keyword: str):

        return [
            {
                "title": "IT Support Technician",
                "company": "ABC Technologies",
                "location": "Coventry",
                "salary": "£28,000",
                "url": "demo://job1",
                "source": "Demo",
                "description": f"{keyword} support role."
            },
            {
                "title": "Help Desk Analyst",
                "company": "XYZ Solutions",
                "location": "Birmingham",
                "salary": "£26,000",
                "url": "demo://job2",
                "source": "Demo",
                "description": f"{keyword} help desk position."
            }
        ]