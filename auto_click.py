from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto("http://localhost:8501")

    time.sleep(3)

    # คลิก dropdown company
    page.click("text=Company")

    # เลือก CompanyA
    page.click("text=CompanyA")

    # คลิก dropdown month
    page.click("text=January")

    # เลือก January
    page.click("text=January")

    # กดปุ่ม Generate
    page.click("text=Generate")

    time.sleep(5)

    browser.close()