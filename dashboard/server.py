from flask import Flask, render_template, request, redirect
from datetime import datetime

from database.database import SessionLocal, init_db
from database.job_rep import JobRepository

from models.job import Job
from models.application_profile import ApplicationProfile

from scrapers.adzuna_scraper import AdzunaScraper

from automation.application import start_application
import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

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
        profile.preferred_roles = request.form.get("preferred_roles")
        profile.preferred_locations = request.form.get("preferred_locations")
        profile.job_types = request.form.get("job_types")
        profile.salary_expectations = request.form.get("salary_expectations")

        cv = request.files.get("cv")

        if cv and cv.filename:

            filename = secure_filename(cv.filename)

            upload_folder = os.path.join(
                os.getcwd(),
                "uploads"
            )

            os.makedirs(
                upload_folder,
                exist_ok=True
            )

            cv_path = os.path.join(
                upload_folder,
                filename
            )

            cv.save(cv_path)

            profile.cv_path = cv_path

        db.commit()

        return redirect("/profile")

    return render_template(
        "profile.html",
        profile=profile
    )
    
    
@app.route("/test-application")
def test_application():

    return render_template("test_application.html")


@app.route("/apply/<int:job_id>")
def apply_job(job_id):

    db = SessionLocal()

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if not job:
        db.close()
        return "Job not found", 404

    # Check if already applied
    if job.status == "Applied":
        db.close()
        return "You have already applied to this job.", 409

    # Mark job as "Preparing" so user can't apply twice
    job.status = "Preparing"
    db.commit()
    db.close()

    # Start Playwright automation in background
    from automation.application import start_application
    start_application(job.url, job_id=job.id)

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)