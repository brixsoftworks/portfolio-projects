from playwright.sync_api import sync_playwright
import time

artifact_dir = '/home/mullainathan/.gemini/antigravity-cli/brain/14a6194d-1561-4011-ac2d-90f19685bcb1'

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path='/home/mullainathan/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome',
        headless=True
    )
    page = browser.new_page(viewport={'width': 1440, 'height': 900})

    errors = []
    logs = []
    page.on('pageerror', lambda err: errors.append(str(err)))
    page.on('console', lambda msg: logs.append(f"[{msg.type}] {msg.text}"))

    print("Navigating to http://localhost:3005/nilambur.html...")
    page.goto('http://localhost:3005/nilambur.html', wait_until='networkidle')
    page.wait_for_timeout(1000)

    # 1. VERIFY HERO ADVANCED ANIMATIONS
    print("\n=== 1. VERIFYING HERO SECTION ENHANCEMENTS ===")
    hero_check = page.evaluate('''() => {
        const col0 = document.getElementById('heroCol0');
        const laser = col0 ? col0.querySelector('.pixel-wipe-laser-beam') : null;
        const sheen = col0 ? col0.querySelector('.hero-wood-sheen') : null;
        return {
            hasCol0: !!col0,
            hasLaser: !!laser,
            hasSheen: !!sheen
        };
    }''')
    print("Hero elements check:", hero_check)

    # Hover over heroCol0 to test 3D tilt
    page.hover('#heroCol0')
    page.wait_for_timeout(300)
    tilt_style = page.evaluate('''() => {
        const col = document.getElementById('heroCol0');
        return col ? col.style.transform : 'none';
    }''')
    print("Hero 3D tilt transform on hover:", tilt_style)
    page.screenshot(path=f"{artifact_dir}/anim_01_hero_tilt_sheen.png")
    print("Saved anim_01_hero_tilt_sheen.png")

    # Trigger Re-wipe on Hero Col 1
    page.click('#heroCol1 .hero-rewipe-btn')
    page.wait_for_timeout(500)
    page.screenshot(path=f"{artifact_dir}/anim_02_hero_rewipe_laser.png")
    print("Saved anim_02_hero_rewipe_laser.png")

    # 2. VERIFY ROLLS-ROYCE HOVER RETICLE & TELEMETRY SCROLL
    print("\n=== 2. VERIFYING ROLLS-ROYCE CANVAS TELEMETRY & RETICLE ===")
    # Move mouse inside RR section
    rr_section = page.locator('#rrRollsRoyceSection')
    page.evaluate('''() => {
        const mi = document.querySelector('.main-inner');
        if (mi) mi.scrollTo({ top: 1620, behavior: 'instant' });
    }''')
    page.wait_for_timeout(500)

    # Move cursor inside RR Section to test Reticle
    page.mouse.move(720, 450)
    page.wait_for_timeout(300)
    reticle_data = page.evaluate('''() => {
        const r = document.getElementById('rrReticle');
        const hud = document.getElementById('rrReticleHud');
        return {
            display: r ? window.getComputedStyle(r).display : 'none',
            left: r ? r.style.left : '',
            top: r ? r.style.top : '',
            hudText: hud ? hud.textContent : ''
        };
    }''')
    print("RR Reticle Data:", reticle_data)
    page.screenshot(path=f"{artifact_dir}/anim_03_rr_reticle_act1.png")
    print("Saved anim_03_rr_reticle_act1.png")

    # Scroll to Act 3 (scrollY: 3990) to test live telemetry & animated counters
    print("\n--- Scrolling to Act 3 to test Dynamic Numbers ---")
    page.evaluate('''() => {
        const mi = document.querySelector('.main-inner');
        if (mi) mi.scrollTo({ top: 3990, behavior: 'instant' });
    }''')
    page.wait_for_timeout(1000)

    act3_data = page.evaluate('''() => {
        const wmTL = document.querySelector('.rr-watermark.top-left span:last-child');
        const wmBR = document.querySelector('.rr-watermark.bottom-right span');
        const specNums = Array.from(document.querySelectorAll('#rrAct3 .rr-spec-num')).map(el => el.textContent);
        return {
            wmTopLeft: wmTL ? wmTL.textContent : '',
            wmBottomRight: wmBR ? wmBR.textContent : '',
            specNums: specNums
        };
    }''')
    print("Act 3 Live Telemetry & Numbers:", act3_data)
    page.screenshot(path=f"{artifact_dir}/anim_04_rr_act3_telemetry_numbers.png")
    print("Saved anim_04_rr_act3_telemetry_numbers.png")

    # 3. VERIFY 3D EXPLODED MORTISE & TENON JOINERY
    print("\n=== 3. VERIFYING MORTISE & TENON JOINERY ADVANCED ANIMATIONS ===")
    page.evaluate('''() => {
        const card = document.querySelector('.joinery-schematic-card');
        const mi = document.querySelector('.main-inner');
        if (card && mi) {
            const rect = card.getBoundingClientRect();
            mi.scrollTo({ top: mi.scrollTop + rect.top - 120, behavior: 'instant' });
        }
    }''')
    page.wait_for_timeout(800)

    # Click to toggle lock
    print("Clicking INTERLOCK JOINT ↔ EXPLODE VIEW...")
    page.evaluate("() => document.querySelector('.joinery-btn')?.click()")
    page.wait_for_timeout(1000)

    joinery_locked_check = page.evaluate('''() => {
        const tenon = document.getElementById('tenonBlock');
        const pin = document.getElementById('lockingPin');
        const readout = document.getElementById('dimReadout');
        const wave1 = document.getElementById('acousticWave1');
        const wave2 = document.getElementById('acousticWave2');
        const heatmap = document.getElementById('stressHeatmap');

        return {
            tenonTransform: tenon ? tenon.getAttribute('transform') : '',
            pinTransform: pin ? pin.getAttribute('transform') : '',
            readoutText: readout ? readout.textContent : '',
            hasWave1: !!wave1,
            hasWave2: !!wave2,
            hasHeatmap: !!heatmap
        };
    }''')
    print("Joinery locked state:", joinery_locked_check)
    page.screenshot(path=f"{artifact_dir}/anim_05_joinery_interlocked_fea.png")
    print("Saved anim_05_joinery_interlocked_fea.png")

    # Click again to explode
    page.evaluate("() => document.querySelector('.joinery-btn')?.click()")
    page.wait_for_timeout(1000)
    page.screenshot(path=f"{artifact_dir}/anim_06_joinery_exploded.png")
    print("Saved anim_06_joinery_exploded.png")

    # 4. VERIFY INTRO CALIPER SLIDER
    print("\n=== 4. VERIFYING INTRO CALIPER MEASURE HUD ===")
    page.evaluate('''() => {
        const btn = document.getElementById('introCaliperBtn');
        const mi = document.querySelector('.main-inner');
        if (btn && mi) {
            const rect = btn.getBoundingClientRect();
            mi.scrollTo({ top: mi.scrollTop + rect.top - 200, behavior: 'instant' });
        }
    }''')
    page.wait_for_timeout(600)
    page.evaluate("() => document.getElementById('introCaliperBtn')?.click()")
    page.wait_for_timeout(600)
    caliper_hud = page.evaluate('''() => {
        const hud = document.querySelector('.intro-caliper-measure-hud');
        return hud ? hud.textContent : 'none';
    }''')
    print("Caliper measure HUD text:", caliper_hud)
    page.screenshot(path=f"{artifact_dir}/anim_07_caliper_active_hud.png")
    print("Saved anim_07_caliper_active_hud.png")

    # 5. VERIFY GI COIN LEVITATION
    print("\n=== 5. VERIFYING GI COIN 3D INTERACTION ===")
    page.evaluate('''() => {
        const coin = document.getElementById('giCoin');
        const mi = document.querySelector('.main-inner');
        if (coin && mi) {
            const rect = coin.getBoundingClientRect();
            mi.scrollTo({ top: mi.scrollTop + rect.top - 200, behavior: 'instant' });
        }
    }''')
    page.wait_for_timeout(500)
    page.evaluate("() => document.getElementById('giCoin')?.click()")
    page.wait_for_timeout(700)
    page.screenshot(path=f"{artifact_dir}/anim_08_gi_coin_spin.png")
    print("Saved anim_08_gi_coin_spin.png")

    print("\n=== Page Errors ===")
    print("Errors count:", len(errors))
    for err in errors:
        print("Error:", err)

    browser.close()
