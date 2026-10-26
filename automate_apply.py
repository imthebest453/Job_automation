#!/usr/bin/env python3
"""
Full automation: periodically searches for new IT jobs and applies automatically.

Usage:
    python automate_apply.py

This script:
1. Starts Flask server (if not running) to access routes
2. Periodically searches for new jobs using keyword(s)
3. Automatically applies to each new job using Playwright
4. Repeats with configurable interval
"""

import time
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.database import init_db, get_db, SessionLocal
from database.job_rep import JobRepository
from scrapers.adzuna_scraper import AdzunaScraper
from automation.application import start_application
from models.job import Job
from models.application_profile import ApplicationProfile


def ensure_profile():
    """Ensure an application profile exists; prompt if not."""
    db = SessionLocal()
    try:
        profile = db.query(ApplicationProfile).first()
        if not profile:
            print("No application profile found.")
            print("Please set up your profile first via the web UI at /profile")
            print("Or provide details below:")
            name = input("  Full name: ") or "John Doe"
            email = input("  Email: ") or "john@example.com"
            phone = input("  Phone: ") or "123-456-7890"
            address = input("  Address: ") or "123 Main St"
            city = input("  City: ") or "City"
            postcode = input("  Postcode: ") or "12345"

            from datetime import datetime
            profile = ApplicationProfile(
                full_name=name,
                email=email,
                phone=phone,
                address=address,
                city=city,
                postcode=postcode,
            )
            db.add(profile)
            db.commit()
            print("Profile created.")
        return db.query(ApplicationProfile).first()
    finally:
        db.close()


def find_and_apply(keyword="IT Support", max_jobs=10):
    """Search for jobs and apply to new ones."""
    db = SessionLocal()
    try:
        # Get jobs already applied or saved
        all_jobs = JobRepository.get_all_jobs(db)
        applied_ids = {j.id for j in JobRepository.get_applied_jobs(db)}

        # Search for new jobs
        scraper = AdzunaScraper()
        new_jobs = scraper.search(keyword)

        applied_count = 0
        for job in new_jobs:
            if job.id > max_jobs:
                continue
            if job.id in applied_ids:
                continue

            print(f"\nApplying to: {job.title} at {job.company} (ID: {job.id})")
            try:
                start_application(job.url)
                JobRepository.update_status(db, job.id, "Applied")
                applied_count += 1
                print(f"✓ Applied successfully to {job.title}")
            except Exception as e:
                print(f"✗ Failed to apply to {job.title}: {e}")

        if applied_count == 0:
            print("No new jobs to apply for.")

        return applied_count
    finally:
        db.close()


def main_loop(keyword="IT Support", interval=300, max_jobs_per_run=10):
    """Main automation loop."""
    print("=" * 60)
    print("JobFlow Automated Apply System")
    print("=" * 60)
    print(f"Keyword: {keyword}")
    print(f"Check interval: {interval // 60} minutes")
    print(f"Max jobs per run: {max_jobs_per_run}")
    print("Press Ctrl+C to stop")
    print()

    # Ensure profile exists
    profile = ensure_profile()
    if not profile:
        print("Cannot proceed without a profile. Exiting.")
        return

    print(f"Profile ready: {profile.full_name}\n")

    try:
        while True:
            try:
                find_and_apply(keyword=keyword, max_jobs=max_jobs_per_run)
            except Exception as e:
                print(f"Error in apply cycle: {e}")

            print(f" sleeping {interval // 60} minutes...")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nStopping automated apply system.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Automated Job Application")
    parser.add_argument("--keyword", default="IT Support", help="Job search keyword")
    parser.add_argument("--interval", type=int, default=300, help="Check interval in seconds (300=5min)")
    parser.add_argument("--max-jobs", type=int, default=10, help="Max jobs to apply per cycle")
    parser.add_argument("--once", action="store_true", help="Run once instead of looping")

    args = parser.parse_args()

    if args.once:
        ensure_profile()
        find_and_apply(keyword=args.keyword, max_jobs=args.max_jobs)
    else:
        main_loop(
            keyword=args.keyword,
            interval=args.interval,
            max_jobs_per_run=args.max_jobs,
        )