from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import requests
from models.job import Job


@dataclass
class JobListing:
    """Normalised job listing from any source."""
    title: str
    company: str
    location: str
    salary: str
    url: str
    source: str
    description: str = ""
    date_posted: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None

    def to_model(self) -> Job:
        """Convert to SQLAlchemy Job model."""
        return Job(
            title=self.title,
            company=self.company,
            location=self.location,
            salary=self.salary,
            url=self.url,
            source=self.source,
            description=self.description,
        )


@dataclass
class SearchFilters:
    """Filters for job search."""
    keyword: str = ""
    location: str = "UK"
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    remote_only: bool = False


class JobBoardConnector(ABC):
    """Abstract base class for job board connectors."""

    name: str = "abstract"

    @abstractmethod
    def search(self, filters: SearchFilters) -> List[JobListing]:
        """Search for jobs matching the filters."""
        pass

    @abstractmethod
    def can_apply_automatically(self, job_url: str) -> bool:
        """Whether this source supports automated application."""
        pass

    @abstractmethod
    def get_application_instructions(self, job_url: str) -> str:
        """Get instructions for manual application to this source."""
        pass


class AdzunaConnector(JobBoardConnector):
    """Adzuna job board connector for UK jobs."""

    name = "Adzuna"

    def __init__(self):
        self.app_id = None
        self.app_key = None
        self._load_credentials()

    def _load_credentials(self):
        """Load Adzuna API credentials from environment."""
        import os
        from dotenv import load_dotenv
        load_dotenv()

        self.app_id = os.getenv("ADZUNA_APP_ID")
        self.app_key = os.getenv("ADZUNA_APP_KEY")

        if not self.app_id or not self.app_key:
            raise ValueError(
                "Adzuna API credentials are missing from .env file"
            )

    def search(self, filters: SearchFilters) -> List[JobListing]:
        """Search Adzuna for jobs matching the filters."""
        if not self.app_id or not self.app_key:
            raise ValueError("Adzuna credentials not configured")

        url = "https://api.adzuna.com/v1/api/jobs/gb/search/1"

        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "results_per_page": 20,
            "what": filters.keyword,
            "where": filters.location,
            "content-type": "application/json",
        }

        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            jobs = []
            for item in data.get("results", []):
                job = JobListing(
                    title=item.get("title", "Unknown"),
                    company=item.get("company", {}).get(
                        "display_name", "Unknown"
                    ),
                    location=item.get("location", {}).get(
                        "display_name", "UK"
                    ),
                    salary=self._normalize_salary(item.get("salary")),
                    url=item.get("redirect_url"),
                    source=self.name,
                    description=item.get("description", ""),
                    date_posted=item.get("date_created"),
                    employment_type=item.get("contract_type"),
                    experience_level=item.get("experience_level"),
                )
                jobs.append(job)

            return jobs

        except requests.exceptions.RequestException as e:
            print(f"Adzuna search error: {e}")
            return []

    def can_apply_automatically(self, job_url: str) -> bool:
        """Adzuna job URLs redirect to the original employer site."""
        # Adzuna provides redirect URLs - automation depends on the target site
        return False

    def get_application_instructions(self, job_url: str) -> str:
        """Get instructions for applying via Adzuna."""
        return (
            f"1. Open the job listing at: {job_url}\n"
            "2. Click 'Apply' on the employer's website\n"
            "3. Follow the employer's application process\n"
            "4. Return to JobFlow to track your application"
        )

    @staticmethod
    def _normalize_salary(salary_data) -> str:
        """Normalize Adzuna salary data to string."""
        if salary_data is None:
            return "Not specified"

        if isinstance(salary_data, dict):
            min_sal = salary_data.get("min")
            max_sal = salary_data.get("max")
            if min_sal is not None:
                return f"£{min_sal:,.0f}"
            if max_sal is not None:
                return f"£{max_sal:,.0f}"
            return "Not specified"

        if isinstance(salary_data, (int, float)):
            return f"£{salary_data:,.0f}"

        return str(salary_data)


class DemoConnector(JobBoardConnector):
    """Demo/connector for testing and development."""

    name = "Demo Scraper"

    def search(self, filters: SearchFilters) -> List[JobListing]:
        """Return hardcoded demo jobs for testing."""
        from models.job import Job

        all_jobs = [
            JobListing(
                title="IT Support Technician",
                company="Example Ltd",
                location="Coventry",
                salary="£30,000",
                url="https://example.com/jobs/it-support-technician",
                source=self.name,
                description="Provide technical support, troubleshoot hardware and software issues.",
            ),
            JobListing(
                title="Help Desk Analyst",
                company="XYZ Solutions",
                location="Birmingham",
                salary="£28,000",
                url="https://example.com/jobs/help-desk-analyst",
                source=self.name,
                description="Assist users with IT problems and manage support tickets.",
            ),
            JobListing(
                title="Cybersecurity Analyst",
                company="SecureTech",
                location="London",
                salary="£40,000",
                url="https://example.com/jobs/cybersecurity-analyst",
                source=self.name,
                description="Monitor security threats and investigate cyber incidents.",
            ),
        ]

        # Filter by keyword if provided
        if filters.keyword:
            keyword = filters.keyword.lower()
            all_jobs = [
                j for j in all_jobs
                if keyword in j.title.lower()
                or keyword in j.description.lower()
                or keyword in j.company.lower()
            ]

        return all_jobs

    def can_apply_automatically(self, job_url: str) -> bool:
        """Demo jobs can be filled with prepared profile data."""
        return True

    def get_application_instructions(self, job_url: str) -> str:
        """Get instructions for applying to a demo job."""
        return (
            f"1. This is a demo job for testing purposes\n"
            f"2. Application form will be auto-filled using your profile\n"
            f"3. Review the completed form before submission\n"
            f"4. Confirm submission when ready"
        )


# Connector registry - map source names to connectors
CONNECTOR_REGISTRY: Dict[str, JobBoardConnector] = {}


def register_connector(connector: JobBoardConnector):
    """Register a job board connector."""
    CONNECTOR_REGISTRY[connector.name] = connector


def get_connector(source_name: str) -> Optional[JobBoardConnector]:
    """Get a connector by source name."""
    return CONNECTOR_REGISTRY.get(source_name)


def init_connectors():
    """Initialize all available connectors."""
    from services.job_connectors import AdzunaConnector, DemoConnector

    # Register known connectors
    adzuna = AdzunaConnector()
    register_connector(adzuna)

    # Register demo connector for development/testing
    demo = DemoConnector()
    register_connector(demo)


# Initialize connectors on module import
# Skip Adzuna if credentials not available for initial load
try:
    init_connectors()
except Exception:
    print("Connector initialization completed with warnings")