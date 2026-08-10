from flask import Flask, render_template, request, redirect

from database.database import SessionLocal, init_db
from database.job_rep import JobRepository

from models.job import Job
from models.application_profile import ApplicationProfile

from scrapers.adzuna_scraper import AdzunaScraper

from automation.application import start_application

init_db()

app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)


@app.route("/")
def home():

    db = SessionLocal()

    try:
        jobs = JobRepository.get_all_jobs(db)

        return render_template(
            "dashboard.html",
            jobs=jobs
        )

    finally:
        db.close()


@app.post("/search")
def search_jobs():

    keyword = request.form.get("keyword", "").strip()

    if not keyword:
        return redirect("/")

    scraper = AdzunaScraper()

    jobs = scraper.search(keyword)

    db = SessionLocal()

    for job in jobs:
        try:
            JobRepository.add_job(db, job)
        except Exception:
            db.rollback()

    return render_template(
        "dashboard.html",
        jobs=jobs,
        keyword=keyword
    )

@app.post("/update-status/<int:job_id>")
def update_status(job_id):

    status = request.form.get("status")

    db = SessionLocal()

    try:
        JobRepository.update_status(
            db,
            job_id,
            status
        )

        return redirect("/")

    finally:
        db.close()


@app.route("/applications")
def applications():

    db = SessionLocal()

    try:
        jobs = JobRepository.get_applied_jobs(db)

        return render_template(
            "applications.html",
            jobs=jobs
        )

    finally:
        db.close()


@app.route("/apply/<int:job_id>")
def apply_job(job_id):

    db = SessionLocal()

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if not job:
        return "Job not found", 404

    start_application(job.url)

    return redirect("/")

@app.route("/profile", methods=["GET", "POST"])
def profile():

    db = SessionLocal()

    profile = db.query(ApplicationProfile).first()

    if request.method == "POST":

        if not profile:
            profile = ApplicationProfile()
            db.add(profile)

        profile.full_name = request.form.get("full_name")
        profile.email = request.form.get("email")
        profile.phone = request.form.get("phone")
        profile.address = request.form.get("address")
        profile.city = request.form.get("city")
        profile.postcode = request.form.get("postcode")
        profile.skills = request.form.get("skills")
        profile.experience = request.form.get("experience")
        profile.education = request.form.get("education")

        db.commit()

        return redirect("/profile")

    return render_template(
        "profile.html",
        profile=profile
    )
    
    
    
if __name__ == "__main__":
    app.run(debug=True)