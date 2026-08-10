from models.job import Job


class DemoScraper:

    def search(self, keyword):

        all_jobs = [

            Job(
                title="IT Support Technician",
                company="Example Ltd",
                location="Coventry",
                salary="£30,000",
                url="https://example.com/jobs/it-support-technician",
                source="Demo Scraper",
                description="Provide technical support, troubleshoot hardware and software issues."
            ),

            Job(
                title="Help Desk Analyst",
                company="XYZ Solutions",
                location="Birmingham",
                salary="£28,000",
                url="https://example.com/jobs/help-desk-analyst",
                source="Demo Scraper",
                description="Assist users with IT problems and manage support tickets."
            ),

            Job(
                title="Cybersecurity Analyst",
                company="SecureTech",
                location="London",
                salary="£40,000",
                url="https://example.com/jobs/cybersecurity-analyst",
                source="Demo Scraper",
                description="Monitor security threats and investigate cyber incidents."
            )

        ]


        # If search box is empty, return everything
        if not keyword:
            return all_jobs


        keyword = keyword.lower()


        matching_jobs = []


        for job in all_jobs:

            if (
                keyword in job.title.lower()
                or keyword in job.description.lower()
                or keyword in job.company.lower()
            ):
                matching_jobs.append(job)


        return matching_jobs