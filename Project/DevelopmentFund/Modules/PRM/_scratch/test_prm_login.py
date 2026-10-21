from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    print("1. Opening PRM Login...")
    page.goto('https://newprmdev.kalbenutritionals.web.id/Account/Login')
    page.wait_for_timeout(2000)

    print("2. Filling credentials for 050311...")
    page.fill('#Login_txtUserName', '050311')
    page.fill('#Login_txtPassword', 'bypass')
    page.fill('#Login_txtCaptcha', 'bypass')
    page.screenshot(path='d:/Work/Source/TestCase_Generator/Project/DevelopmentFund/PRM/evidence/prm_login_filled.png')

    print("3. Submitting login...")
    page.click('button[type=submit], input[type=submit]')
    page.wait_for_timeout(3500)

    print(f"Current URL: {page.url}")
    print(f"Page Title: {page.title()}")

    # Check for error if any
    error_msg = page.evaluate("""() => {
        const err = document.querySelector('.validation-summary-errors, .alert-danger, .field-validation-error');
        return err ? err.innerText.trim() : "";
    }""")
    if error_msg:
        print(f"Login Warning/Error: {error_msg}")

    # Check if directed to Account/Setting
    if 'Setting' in page.url:
        print("Handling Account/Setting role selection...")
        page.screenshot(path='d:/Work/Source/TestCase_Generator/Project/DevelopmentFund/PRM/evidence/prm_setting_page.png')
        # Select role if needed and submit
        btn_submit = page.query_selector('button[type=submit], input[type=submit]')
        if btn_submit:
            btn_submit.click()
            page.wait_for_timeout(3000)
            print(f"URL after Setting submit: {page.url}")

    # Check menus and user info
    user_info = page.evaluate("""() => {
        const name = document.querySelector('.user-name, .username, .user-panel, .dropdown-user, .profile-name')?.innerText?.trim();
        const menus = Array.from(document.querySelectorAll('.sidebar-menu a, .nav a, .main-menu a')).map(a => ({
            text: a.innerText.replace(/\\s+/g, ' ').trim(),
            href: a.href
        })).filter(x => x.text.length > 0);
        return { name, menus };
    }""")

    print(f"Logged-in User in PRM: {user_info['name']}")
    print(f"PRM Menus found count: {len(user_info['menus'])}")
    for m in user_info['menus']:
        if any(k in m['text'].lower() for k in ['klaim', 'claim', 'fund', 'kds', 'df', 'transaksi']):
            print(f"  > {m['text']} => {m['href']}")

    page.screenshot(path='d:/Work/Source/TestCase_Generator/Project/DevelopmentFund/PRM/evidence/prm_after_login.png')
    browser.close()
