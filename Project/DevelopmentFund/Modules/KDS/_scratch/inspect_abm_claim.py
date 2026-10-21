"""
Inspect muhammad.prasetyo login and Ready to Submit flow on KICAO KDS.
"""
from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    print("1. Login as muhammad.prasetyo (ABM)...")
    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
    page.fill('input[name=txtUserName]', 'muhammad.prasetyo')
    page.fill('input[name=txtPassword]', 'bypass')
    page.fill('input[name=txtCaptcha]', 'bypass')
    page.click('button[type=submit]')
    page.wait_for_timeout(2500)

    # Check if role selector popup appears
    role_modal = page.query_selector('#modalChooseRole')
    if role_modal and role_modal.is_visible():
        roles = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('#modalChooseRole table tbody tr')).map(tr => tr.innerText.trim());
        }""")
        print("Available Roles for muhammad.prasetyo:", roles)
        page.click('#modalChooseRole table tbody tr:first-child')
        page.wait_for_timeout(2000)

    print("2. Opening /Transaksi/KlaimDF...")
    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaksi/KlaimDF')
    page.wait_for_timeout(3000)

    print("3. Clicking #btnFind...")
    page.click('#btnFind')
    page.wait_for_timeout(2500)

    iframe = page.wait_for_selector('iframe.fancybox-iframe')
    frame = iframe.content_frame()
    frame.wait_for_load_state('networkidle')

    rows = frame.evaluate("""() => {
        return Array.from(document.querySelectorAll('table tbody tr')).map(tr => 
            Array.from(tr.querySelectorAll('td')).map(td => td.innerText.trim())
        );
    }""")
    print("Claims found in LOV for muhammad.prasetyo:")
    for r in rows:
        print("  ", r)

    browser.close()
