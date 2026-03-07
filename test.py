from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://localhost:8000/public/")
        page.wait_for_selector(".ply-badge")
        print("Found ply badge")
        browser.close()

if __name__ == "__main__":
    run()
