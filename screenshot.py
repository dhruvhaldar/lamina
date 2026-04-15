from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("http://127.0.0.1:3000")
    page.wait_for_timeout(1000)
    page.screenshot(path="lamina_home.png", full_page=True)
    browser.close()
