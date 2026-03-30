from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch()
    context = browser.new_context(record_video_dir="videos/")
    page = context.new_page()
    page.goto('http://localhost:8000/public/index.html')

    # Focus the skip link to test visibility
    page.focus('.skip-link')
    page.wait_for_timeout(500) # wait for transition

    page.screenshot(path='ui_screenshot_skip_link.png')

    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
