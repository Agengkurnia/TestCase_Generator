from playwright.sync_api import sync_playwright
import time
from pathlib import Path

out_dir = Path('d:/Work/Source/TestCase_Generator/Project/DevelopmentFund/KDS/evidence')
out_dir.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})
    
    print('1. Navigating to Login page...')
    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login', timeout=30000)
    page.wait_for_timeout(1000)
    page.screenshot(path=str(out_dir / 'login_page.png'))
    
    print('2. Filling credentials for Muslih...')
    page.fill('input[name=txtUserName]', 'Muslih')
    page.fill('input[name=txtPassword]', 'bypass')
    page.fill('input[name=txtCaptcha]', 'bypass')
    page.screenshot(path=str(out_dir / 'login_filled.png'))
    
    print('3. Submitting login form...')
    page.click('button[type=submit], input[type=submit], .btn-primary')
    page.wait_for_timeout(3000)
    
    print('4. Current URL after submit:', page.url)
    page.screenshot(path=str(out_dir / 'after_login.png'))
    
    # Check if ChooseRole page
    if 'ChooseRole' in page.url:
        print('5. ChooseRole page detected!')
        # Wait a moment for AJAX role population
        page.wait_for_timeout(1500)
        roles = page.eval_on_selector_all('#txtRole option', 'opts => opts.map(o => ({text: o.text, value: o.value}))')
        print('Available roles:', roles)
        page.screenshot(path=str(out_dir / 'choose_role.png'))
        
        # Select first valid role if options exist
        valid_roles = [r for r in roles if r['value']]
        if valid_roles:
            selected_role = valid_roles[0]
            print(f"Selecting role: {selected_role['text']} ({selected_role['value']})")
            page.select_option('#txtRole', selected_role['value'])
            page.wait_for_timeout(500)
            page.click('button[type=submit], input[type=submit], #btn-login')
            page.wait_for_timeout(3000)
            print('URL after selecting role:', page.url)
            page.screenshot(path=str(out_dir / 'after_role_selected.png'))
    
    # Print page info
    title = page.title()
    print('Final Page Title:', title)
    print('Final URL:', page.url)
    
    user_badge = page.query_selector('.user-menu, .navbar-custom-menu, .user-panel, .info')
    if user_badge:
        print('User Badge:', user_badge.inner_text().strip())
    
    # Check menu items
    menu_items = page.eval_on_selector_all('.sidebar-menu li a', 'els => els.map(e => e.innerText.trim()).filter(Boolean)')
    print('Sidebar Menu count:', len(menu_items))
    print('First 10 menu items:', menu_items[:10])
    
    # Try navigating to MKPPDF and KlaimDF
    print('\n6. Testing navigation to /Transaksi/MKPPDF...')
    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaksi/MKPPDF', timeout=30000)
    page.wait_for_timeout(2000)
    print('MKPPDF URL:', page.url)
    print('MKPPDF Title:', page.title())
    page.screenshot(path=str(out_dir / 'mkppdf_page_muslih.png'))
    
    print('\n7. Testing navigation to /Transaksi/KlaimDF...')
    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaksi/KlaimDF', timeout=30000)
    page.wait_for_timeout(2000)
    print('KlaimDF URL:', page.url)
    print('KlaimDF Title:', page.title())
    page.screenshot(path=str(out_dir / 'klaimdf_page_muslih.png'))
    
    browser.close()
    print('\nSUCCESS: Test login session completed!')
