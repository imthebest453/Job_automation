from models.job import Job


class DemoScraper:

    def search(self, keyword):

        jobs = [

            Job(
                title="IT Support Technician",
                company="Example Ltd",
                location="Coventry",
                salary="£28,000",
                url="https://example.com/jobs/it-support-1",
                source="Demo",
                description="Providing IT support and troubleshooting hardware and software issues."
            ),


            Job(
                title="Help Desk Analyst",
                company="XYZ Solutions",
                location="Birmingham",
                salary="£26,000",
                url="https://example.com/jobs/helpdesk-1",
                source="Demo",
                description="Supporting users with technical problems and service requests."
            )

        ]

        return jobs