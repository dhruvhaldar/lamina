import time
from playwright.sync_api import sync_playwright

def verify_ply_badges():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Go to local app
        page.goto("http://localhost:8000")

        # Wait for page load
        page.wait_for_selector("h1")

        # Find the stack input
        stack_input = page.locator("#stack")

        # Wait for initial preview to render
        page.wait_for_selector(".ply-badge")

        # Take screenshot of initial state
        page.screenshot(path="initial_state.png")
        print("Initial state screenshot captured.")

        # Change input to something complex with spaces
        stack_input.fill("0 45 -45 90")

        # Trigger input event (fill does this, but being explicit is safe)
        stack_input.dispatch_event("input")

        # Wait for update
        time.sleep(0.5)

        # Take screenshot of new state
        page.screenshot(path="updated_state.png")
        print("Updated state screenshot captured.")

        # Verify elements exist
        badges = page.locator(".ply-badge")
        count = badges.count()
        print(f"Found {count} ply badges.")

        # Check text content of first badge
        first_badge_text = badges.first.text_content()
        print(f"First badge text: {first_badge_text}")

        browser.close()

if __name__ == "__main__":
    verify_ply_badges()
