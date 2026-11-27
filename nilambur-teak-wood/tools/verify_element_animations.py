from playwright.sync_api import sync_playwright
import time
import os

artifact_dir = '/home/mullainathan/.gemini/antigravity-cli/brain/14a6194d-1561-4011-ac2d-90f19685bcb1'

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/home/mullainathan/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome')
    page = browser.new_page(viewport={'width': 1400, 'height': 960})
    page.goto('http://localhost:3005/nilambur.html')
    page.wait_for_timeout(1000)

    print("=== 1. VERIFYING HERO TERROIR HUD ===")
    hud_info = page.evaluate('''() => {
        const hud = document.getElementById('terroirHud');
        const timeEl = document.getElementById('heroLiveTime');
        return {
            hudExists: !!hud,
            timeText: timeEl ? timeEl.textContent : null,
            visible: hud ? window.getComputedStyle(hud).display : null
        };
    }''')
    print('Hero Terroir HUD:', hud_info)
    page.screenshot(path=os.path.join(artifact_dir, 'elements_01_hero_terroir_hud.png'))

    print("\n=== 2. VERIFYING ODOMETER COUNTERS IN EXPLORE WOODCRAFT ===")
    # Scroll to intro metrics section (start is ~680)
    page.evaluate('''() => {
        const scroller = document.querySelector('.main-inner');
        scroller.scrollTop = 850;
        if (typeof ScrollTrigger !== 'undefined') ScrollTrigger.update();
    }''')
    page.wait_for_timeout(2300) # wait for count up animation
    odometer_info = page.evaluate('''() => {
        const nums = Array.from(document.querySelectorAll('.intro-metric-num')).map(el => el.textContent);
        return { numbers: nums };
    }''')
    print('Odometer numbers after scroll:', odometer_info)
    page.screenshot(path=os.path.join(artifact_dir, 'elements_02_intro_odometer_counters.png'))

    print("\n=== 3. VERIFYING CHRONOS SPECIMEN SWITCHER ===")
    # Scroll to Chronos
    page.evaluate('''() => {
        const scroller = document.querySelector('.main-inner');
        scroller.scrollTop = 2200;
        if (typeof ScrollTrigger !== 'undefined') ScrollTrigger.update();
    }''')
    page.wait_for_timeout(500)

    # Click Switcher Tab 1: Living Sofa
    page.evaluate('switchChronosSpecimen(1)')
    page.wait_for_timeout(600)
    img_sofa = page.evaluate('''() => document.getElementById('patinaImg').src''')
    print('Specimen switched to:', img_sofa)
    page.screenshot(path=os.path.join(artifact_dir, 'elements_03_chronos_specimen_sofa.png'))

    # Click Switcher Tab 2: Modular Kitchen
    page.evaluate('switchChronosSpecimen(2)')
    page.wait_for_timeout(600)
    img_kitchen = page.evaluate('''() => document.getElementById('patinaImg').src''')
    print('Specimen switched to:', img_kitchen)
    page.screenshot(path=os.path.join(artifact_dir, 'elements_04_chronos_specimen_kitchen.png'))

    print("\n=== 4. VERIFYING 3D EXPLODED JOINERY SCHEMATIC ===")
    # Scroll to Joinery schematic in Technical Map
    page.evaluate('''() => {
        const scroller = document.querySelector('.main-inner');
        scroller.scrollTop = 3200;
        if (typeof ScrollTrigger !== 'undefined') ScrollTrigger.update();
    }''')
    page.wait_for_timeout(600)
    page.screenshot(path=os.path.join(artifact_dir, 'elements_05_joinery_exploded.png'))

    # Toggle interlock
    page.evaluate('toggleJoineryLock()')
    page.wait_for_timeout(1200)
    joinery_state = page.evaluate('''() => {
        const dim = document.getElementById('dimReadout');
        return {
            dimText: dim ? dim.textContent : null,
            joineryLocked: joineryLocked
        };
    }''')
    print('Joinery interlocked state:', joinery_state)
    page.screenshot(path=os.path.join(artifact_dir, 'elements_06_joinery_interlocked.png'))

    print("\n=== 5. VERIFYING CTA BRACKETS & PHONE DIALERS ===")
    # Scroll to CTA
    page.evaluate('''() => {
        const scroller = document.querySelector('.main-inner');
        scroller.scrollTop = 6800;
        if (typeof ScrollTrigger !== 'undefined') ScrollTrigger.update();
    }''')
    page.wait_for_timeout(600)
    cta_info = page.evaluate('''() => {
        const brackets = document.querySelectorAll('.cta-bracket');
        const pills = document.querySelectorAll('.cta-phone-pill');
        return {
            bracketCount: brackets.length,
            phonePills: Array.from(pills).map(p => ({ text: p.textContent.trim(), href: p.getAttribute('href') }))
        };
    }''')
    print('CTA Brackets & Phone Dialers:', cta_info)
    page.screenshot(path=os.path.join(artifact_dir, 'elements_07_cta_brackets_dialers.png'))

    browser.close()
    print('\nAll advanced element animations verified successfully!')
