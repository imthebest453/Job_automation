from flask import Flask, render_template,  request,  redirect

from database.database import SessionLocal
from database.job_rep import JobRepository
from scrapers.demo_scraper import DemoScraper
from services.search_service import SearchService

app = Flask(__name__)


@app.route("/")
def dashboard():

    db = SessionLocal()

    try:
        jobs = JobRepository.get_all(db)

        return render_template(
            "dashboard.html",
            jobs=jobs
        )

    finally:
        db.close()

@app.post("/search")
def search_jobs():

    keyword = request.form.get("keyword")

    db = SessionLocal()

    try:

        service = SearchService(DemoScraper())

        service.search(keyword, db)

    finally:
        db.close()


    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)