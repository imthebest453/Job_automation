def start_application(url, job_id=None):

    def _run_application():
        db = SessionLocal()

        try:
            profile = db.query(ApplicationProfile).first()

            if not profile:
                print("No application profile found.")
                return

            with sync_playwright() as p:

                browser = p.chromium.launch(
                    headless=False
                )

                page = browser.new_page()

                page.goto(
                    url,
                    wait_until="domcontentloaded"
                )

                print("Application page opened:")
                print(page.title())

                fill_application(
                    page,
                    profile
                )

                print("Profile information filled.")

                # Allow user to review the filled form before closing
                # Use a non-blocking approach - just wait a bit then prompt
                import threading
                import time

                review_event = threading.Event()

                def wait_for_review():
                    """Wait for user to press Enter in console."""
                    try:
                        input(
                            "Review the application. "
                            "Press ENTER to close the browser..."
                        )
                        review_event.set()
                    except (EOFError, KeyboardInterrupt):
                        review_event.set()

                # Start input watcher in background thread
                reviewer_thread = threading.Thread(target=wait_for_review, daemon=True)
                reviewer_thread.start()

                # Wait for review or timeout after 30 seconds
                review_done = review_event.wait(timeout=30)

                if not review_done:
                    print("Review timeout - closing browser anyway.")

                browser.close()

            # Update job status to "Applied" after browser closes
            # Create a new session since the original one may be detached
            db_status = SessionLocal()
            try:
                from database.job_rep import JobRepository
                JobRepository.update_status(db_status, job_id, "Applied")
                print(f"Job status updated to Applied (job_id: {job_id})")
            finally:
                db_status.close()

        finally:
            db.close()

    # Run in background thread so Flask server remains responsive
    thread = threading.Thread(target=_run_application, daemon=True)
    thread.start()
    print("Application automation started in background thread.")