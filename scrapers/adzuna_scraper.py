import os
import requests

from dotenv import load_dotenv
from models.job import Job


load_dotenv()


class AdzunaScraper:

    def __init__(self):
        self.app_id = os.getenv("ADZUNA_APP_ID")
        self.app_key = os.getenv("ADZUNA_APP_KEY")

    def search(self, keyword):

        if not self.app_id or not self.app_key:
            raise ValueError(
                "Adzuna API credentials are missing from .env"
            )

        url = "https://api.adzuna.com/v1/api/jobs/gb/search/1"

        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "results_per_page": 20,
            "what": keyword,
            "where": "UK",
            "content-type": "application/json"
        }

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        jobs = []

        for item in data.get("results", []):

            job = Job(
                title=item.get("title", "Unknown"),
                company=item.get("company", {}).get(
                    "display_name",
                    "Unknown"
                ),
                location=item.get("location", {}).get(
                    "display_name",
                    "UK"
                ),
                salary=str(
                    item.get("salary_min")
                    or item.get("salary_max")
                    or "Not specified"
                ),
                url=item.get("redirect_url"),
                source="Adzuna",
                description=item.get("description", "")
            )

            jobs.append(job)

        return jobs