import time
from playwright.sync_api import sync_playwright

def snap():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://localhost:8000/public/")
        page.wait_for_selector("h1")
        page.screenshot(path="ui_screenshot.png", full_page=True)
        browser.close()

if __name__ == "__main__":
    snap()
