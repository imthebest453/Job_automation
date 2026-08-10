from playwright.sync_api import sync_playwright

from database.database import SessionLocal
from models.application_profile import ApplicationProfile
from automation.form_filler import fill_application


def start_application(url):

    db = SessionLocal()

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

        print("Basic profile information filled.")

        input(
            "Review the application. "
            "Press ENTER to close the browser..."
        )

        browser.close()