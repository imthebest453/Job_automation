from flask import Flask, render_template

from database.database import SessionLocal
from database.job_rep import JobRepository

app = Flask(__name__)

@app.route("/")
def home():

    db = SessionLocal()

    jobs = JobRepository.get_all_jobs(db)

    return render_template("index.html", jobs=jobs)


if __name__ == "__main__":
    app.run(debug=True)