from database.database import Base, SessionLocal, engine
from models.job import Job
from models.application_profile import ApplicationProfile

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Use the first available connector (Demo Scraper by default)
from services.job_connectors import CONNECTOR_REGISTRY
connector_name = list(CONNECTOR_REGISTRY.keys())[0] if CONNECTOR_REGISTRY else "Demo Scraper"

# Import and initialize Flask app only when needed
def create_app():
    """Create and configure the Flask application."""
    import os
    from flask import Flask, render_template, request, redirect, url_for
    from database.job_rep import JobRepository
    from services.search_service import SearchService
    from services.matching_service import get_suitable_jobs, calculate_suitability

    basedir = os.path.abspath(os.path.dirname(__file__))

    service = SearchService(connector_name)

    app = Flask(
        __name__,
        static_folder=os.path.join(basedir, "dashboard", "static"),
        template_folder=os.path.join(basedir, "dashboard", "templates")
    )

    @app.route("/")
    def home():

        db = SessionLocal()

        try:
            # Get all jobs and calculate suitability scores
            profile = db.query(ApplicationProfile).first()

            if profile:
                suitable_jobs = get_suitable_jobs(db, profile, min_score=20)
                # Attach scoring to each job
                for job in suitable_jobs:
                    result = calculate_suitability(job, profile)
                    job.suitability_score = result["score"]
                    job.suitability_factors = result["factors"]
                    job.missing_requirements = result["missing"]
            else:
                suitable_jobs = JobRepository.get_all_jobs(db)

            return render_template(
                "dashboard.html",
                jobs=JobRepository.get_all_jobs(db),
                suitable_jobs=suitable_jobs,
                profile=profile
            )

        finally:
            db.close()

    @app.route("/search", methods=["GET", "POST"])
    def search_jobs():

        keyword = request.form.get("keyword", "").strip()

        if not keyword:
            return redirect("/")

        from services.job_connectors import SearchFilters
        filters = SearchFilters(keyword=keyword)
        listings = service.connector.search(filters)

        db = SessionLocal()

        added = 0
        for listing in listings:
            try:
                from models.job import Job as JobModel
                job = listing.to_model()
                existing = db.query(JobModel).filter(
                    JobModel.url == job.url
                ).first()

                if not existing:
                    db.add(job)
                    db.commit()
                    added += 1
                db.close()

            except Exception as e:
                db.close() if 'db' in dir() else None
                continue

        # Calculate suitability scores if we have a profile
        profile = db.query(ApplicationProfile).first() if db.is_active else None
        suitable_jobs = []
        if profile:
            suitable_jobs = get_suitable_jobs(db, profile, min_score=20)

        return render_template(
            "dashboard.html",
            jobs=JobRepository.get_all_jobs(db) if db.is_active else [],
            suitable_jobs=suitable_jobs,
            profile=profile,
            keyword=keyword
        )

    @app.route("/update-status/<int:job_id>")
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

    return app

# Only run search when app.py is executed directly (not when imported)
if __name__ == "__main__":
    from services.search_service import SearchService
    service = SearchService(connector_name)
    added = service.search("IT Support", db)
    print(f"{added} new jobs added from {connector_name} connector")

    # Create and run the Flask app
    app = create_app()
    app.run(debug=True)