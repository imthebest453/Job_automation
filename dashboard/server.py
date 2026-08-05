from flask import Flask, render_template, request, redirect

from database.database import SessionLocal, init_db
from database.job_rep import JobRepository

init_db()

app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)

@app.route("/")
def home():

    db = SessionLocal()

    jobs = JobRepository.get_all_jobs(db)

    return render_template("dashboard.html", jobs=jobs)


@app.post("/search")
def search_jobs():

    keyword = request.form.get("keyword", "").strip()

    if not keyword:
        return redirect("/")

    db = SessionLocal()

    jobs = JobRepository.search_jobs(db, keyword)

    return render_template(
        "dashboard.html",
        jobs=jobs,
        keyword=keyword
    )

if __name__ == "__main__":
    app.run(debug=True)