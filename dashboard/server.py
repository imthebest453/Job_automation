from flask import Flask, render_template

from database.database import SessionLocal
from database.job_rep import JobRepository


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



if __name__ == "__main__":
    app.run(debug=True)