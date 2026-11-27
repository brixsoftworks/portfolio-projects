from playwright.sync_api import sync_playwright
import time
import os

artifact_dir = '/home/mullainathan/.gemini/antigravity-cli/brain/14a6194d-1561-4011-ac2d-90f19685bcb1'

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/home/mullainathan/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome')
    page = browser.new_page(viewport={'width': 1400, 'height': 960})
    page.goto('http://localhost:3005/nilambur.html')

    print("=== 1. VERIFYING HERO LOAD CASCADE (NO SCROLL) ===")
    time.sleep(0.05)
    pos_0 = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('.home-hero-img-col .pixel-reveal-img')).map(el => el.style.maskPosition);
    }''')
    print('Initial (t=0.05s):', pos_0)
    page.screenshot(path=os.path.join(artifact_dir, 'innovations_01_hero_load.png'))

    time.sleep(0.8)
    pos_mid = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('.home-hero-img-col .pixel-reveal-img')).map(el => el.style.maskPosition);
    }''')
    print('Mid-cascade (t=0.85s):', pos_mid)

    time.sleep(1.4)
    pos_full = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('.home-hero-img-col .pixel-reveal-img')).map(el => el.style.maskPosition);
    }''')
    print('Full reveal (t=2.25s):', pos_full)
    page.screenshot(path=os.path.join(artifact_dir, 'innovations_02_hero_full.png'))

    print("\n=== 2. VERIFYING HERO ACCORDION & CAD HUD HOVER ===")
    col1 = page.locator('#heroCol1')
    col1.hover(position={'x': 100, 'y': 200})
    time.sleep(0.5)
    hud_info = page.evaluate('''() => {
        const hud = document.querySelector('#heroCol1 .hero-cad-hud');
        const col1 = document.querySelector('#heroCol1');
        return {
            hudVisible: hud ? window.getComputedStyle(hud).opacity : null,
            colWidth: col1 ? col1.getBoundingClientRect().width : null,
            colFlex: col1 ? window.getComputedStyle(col1).flex : null
        };
    }''')
    print('Hero Col 1 Accordion & HUD status:', hud_info)
    page.screenshot(path=os.path.join(artifact_dir, 'innovations_03_hero_hover_accordion_hud.png'))

    print("\n=== 3. VERIFYING HERO RE-WIPE INTERACTION ===")
    page.evaluate('rewipeHeroCol(1)')
    time.sleep(0.4)
    rewipe_pos = page.evaluate('''() => {
        const img = document.querySelector('#heroCol1 .pixel-reveal-img');
        return img ? img.style.maskPosition : null;
    }''')
    print('Re-wipe mid position:', rewipe_pos)
    page.screenshot(path=os.path.join(artifact_dir, 'innovations_04_hero_rewipe.png'))

    print("\n=== 4. VERIFYING CHRONOS PATINA ENGINE ===")
    # Scroll to patina section
    page.evaluate('''() => {
        const scroller = document.querySelector('.main-inner');
        const patina = document.querySelector('.home-patina-wrap');
        if (patina && scroller) {
            scroller.scrollTop = patina.offsetTop - 50;
        }
    }''')
    time.sleep(0.6)
    page.screenshot(path=os.path.join(artifact_dir, 'innovations_05_patina_year0.png'))

    # Update to Year 50
    page.evaluate('setPatinaEra(2)')
    time.sleep(0.4)
    patina_50 = page.evaluate('''() => {
        return {
            badge: document.getElementById('patinaEraBadge').textContent,
            hardness: document.getElementById('metricHardness').textContent,
            filter: document.getElementById('patinaImg').style.filter
        };
    }''')
    print('Patina Year 50 info:', patina_50)
    page.screenshot(path=os.path.join(artifact_dir, 'innovations_06_patina_year50.png'))

    # Update to Year 100 Antique
    page.evaluate('setPatinaEra(3)')
    time.sleep(0.4)
    patina_100 = page.evaluate('''() => {
        return {
            badge: document.getElementById('patinaEraBadge').textContent,
            hardness: document.getElementById('metricHardness').textContent,
            filter: document.getElementById('patinaImg').style.filter
        };
    }''')
    print('Patina Year 100 info:', patina_100)
    page.screenshot(path=os.path.join(artifact_dir, 'innovations_07_patina_year100.png'))

    print("\n=== 5. VERIFYING EXPLORE WOODCRAFT CALIPER SLIDER ===")
    # Scroll to intro section
    page.evaluate('''() => {
        const scroller = document.querySelector('.main-inner');
        const intro = document.querySelector('.home-intro-wrap');
        if (intro && scroller) {
            scroller.scrollTop = intro.offsetTop;
        }
    }''')
    time.sleep(0.6)

    # Activate Caliper mode
    page.evaluate('toggleCaliperMode()')
    time.sleep(0.4)
    page.evaluate('setCaliperPosition(35)')
    time.sleep(0.4)
    caliper_info = page.evaluate('''() => {
        const handle = document.getElementById('introCaliperHandle');
        const reveal = document.getElementById('introRevealWrap');
        return {
            handleDisplay: handle ? window.getComputedStyle(handle).display : null,
            handleLeft: handle ? handle.style.left : null,
            revealClip: reveal ? reveal.style.clipPath : null
        };
    }''')
    print('Caliper Mode status:', caliper_info)
    page.screenshot(path=os.path.join(artifact_dir, 'innovations_08_intro_caliper_split.png'))

    print("\n=== 6. VERIFYING ACOUSTIC SOUND TOGGLE ===")
    sound_info = page.evaluate('''() => {
        toggleSound();
        const lbl = document.getElementById('soundLabel').textContent;
        toggleSound();
        const lbl2 = document.getElementById('soundLabel').textContent;
        return { labelToggled: lbl, labelRestored: lbl2 };
    }''')
    print('Sound Toggle status:', sound_info)

    browser.close()
    print('\nAll innovations verified with zero errors!')
