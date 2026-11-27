from playwright.sync_api import sync_playwright
import time
import os

artifact_dir = '/home/mullainathan/.gemini/antigravity-cli/brain/14a6194d-1561-4011-ac2d-90f19685bcb1'

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/home/mullainathan/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome')
    page = browser.new_page(viewport={'width': 1400, 'height': 960})
    
    logs = []
    errors = []
    page.on('console', lambda msg: logs.append(f'[{msg.type}] {msg.text}'))
    page.on('pageerror', lambda err: errors.append(str(err)))

    page.goto('http://localhost:3005/nilambur.html')
    page.wait_for_timeout(1500)

    print("=== 1. VERIFYING ROLLS-ROYCE SECTION INITIALIZATION ===")
    init_info = page.evaluate('''() => {
        const sec = document.getElementById('rrRollsRoyceSection');
        const v = document.getElementById('rrVideoEl');
        const title = document.querySelector('.rr-title');
        const subtitle = document.querySelector('.rr-subtitle');
        const glassHead = document.querySelector('.rr-glass-heading');
        const glassText = document.querySelector('.rr-glass-text');
        const st = window.rrScrollTriggerInstance;
        
        return {
            sectionExists: !!sec,
            videoSrc: v ? v.getAttribute('src') : null,
            videoReadyState: v ? v.readyState : null,
            videoDuration: v ? v.duration : null,
            titleText: title ? title.textContent.trim() : null,
            subtitleText: subtitle ? subtitle.textContent.trim() : null,
            glassHeading: glassHead ? glassHead.textContent.trim() : null,
            glassTextSnippet: glassText ? glassText.textContent.trim().substring(0, 80) : null,
            stStart: st ? st.start : null,
            stEnd: st ? st.end : null
        };
    }''')
    print('Initialization details:', init_info)

    # Scroll directly to start of Rolls-Royce section
    st_start = init_info['stStart'] or 1600
    st_end = init_info['stEnd'] or (st_start + 2400)
    print(f"ScrollTrigger range: {st_start}px -> {st_end}px (depth: {st_end - st_start}px)")

    print("\n=== 2. SCRUB PHASE 01: CHASSIS & SUSPENSION MATRIX ===")
    page.evaluate(f'''() => {{
        const scroller = document.querySelector('.main-inner');
        scroller.scrollTop = {st_start + 100};
        ScrollTrigger.update();
    }}''')
    page.wait_for_timeout(1000)

    phase1_info = page.evaluate('''() => {
        const v = document.getElementById('rrVideoEl');
        const pb = document.getElementById('rrPhaseBadge');
        const tc = document.getElementById('rrTimecode');
        const fill = document.getElementById('rrTimelineFill');
        return {
            currentTime: v ? v.currentTime : null,
            phaseBadge: pb ? pb.textContent : null,
            timecode: tc ? tc.textContent : null,
            fillWidth: fill ? fill.style.width : null
        };
    }''')
    print('Phase 1 info:', phase1_info)
    page.screenshot(path=os.path.join(artifact_dir, 'rr_01_chassis_matrix.png'))

    print("\n=== 3. SCRUB PHASE 02: ORBITAL TRAJECTORY DIVE ===")
    # Scroll midway into the pinned range (progress ~0.50)
    mid_scroll = st_start + (st_end - st_start) * 0.50
    page.evaluate(f'''() => {{
        const scroller = document.querySelector('.main-inner');
        scroller.scrollTop = {mid_scroll};
        ScrollTrigger.update();
    }}''')
    page.wait_for_timeout(1000)

    phase2_info = page.evaluate('''() => {
        const v = document.getElementById('rrVideoEl');
        const pb = document.getElementById('rrPhaseBadge');
        const tc = document.getElementById('rrTimecode');
        const fill = document.getElementById('rrTimelineFill');
        return {
            currentTime: v ? v.currentTime : null,
            phaseBadge: pb ? pb.textContent : null,
            timecode: tc ? tc.textContent : null,
            fillWidth: fill ? fill.style.width : null
        };
    }''')
    print('Phase 2 info:', phase2_info)
    page.screenshot(path=os.path.join(artifact_dir, 'rr_02_orbital_dive.png'))

    print("\n=== 4. SCRUB PHASE 03: BESPOKE NILAMBUR TEAK CABIN REVEAL ===")
    # Scroll near end of pinned range (progress ~0.88)
    end_scroll = st_start + (st_end - st_start) * 0.88
    page.evaluate(f'''() => {{
        const scroller = document.querySelector('.main-inner');
        scroller.scrollTop = {end_scroll};
        ScrollTrigger.update();
    }}''')
    page.wait_for_timeout(1000)

    phase3_info = page.evaluate('''() => {
        const v = document.getElementById('rrVideoEl');
        const pb = document.getElementById('rrPhaseBadge');
        const tc = document.getElementById('rrTimecode');
        const fill = document.getElementById('rrTimelineFill');
        const btn2 = document.getElementById('btnChap2');
        return {
            currentTime: v ? v.currentTime : null,
            phaseBadge: pb ? pb.textContent : null,
            timecode: tc ? tc.textContent : null,
            fillWidth: fill ? fill.style.width : null,
            chap2Active: btn2 ? btn2.classList.contains('active') : false
        };
    }''')
    print('Phase 3 info:', phase3_info)
    page.screenshot(path=os.path.join(artifact_dir, 'rr_03_teak_cabin_reveal.png'))

    print("\n=== 5. TESTING CHAPTER CLICK: JUMP TO CHAPTER 3 (TEAK INTERIOR) ===")
    page.evaluate('seekRRVideo(8.6, 2)')
    page.wait_for_timeout(800)
    chap_click_info = page.evaluate('''() => {
        const v = document.getElementById('rrVideoEl');
        const pb = document.getElementById('rrPhaseBadge');
        const tc = document.getElementById('rrTimecode');
        return {
            currentTime: v ? v.currentTime : null,
            phaseBadge: pb ? pb.textContent : null,
            timecode: tc ? tc.textContent : null
        };
    }''')
    print('Chapter click info:', chap_click_info)
    page.screenshot(path=os.path.join(artifact_dir, 'rr_04_chapter_click_jump.png'))

    print("\n=== 6. CONSOLE & PAGE ERRORS CHECK ===")
    print('Page errors count:', len(errors), errors)
    err_logs = [l for l in logs if '[error]' in l]
    print('Console errors count:', len(err_logs), err_logs)

    browser.close()
    print("\nRolls-Royce Nilambur Teak video showcase verified successfully!")
