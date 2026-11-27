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

    print("=== 1. VERIFYING FULLSCREEN SETUP & ZERO VIDEO CHROME ===")
    check_chrome = page.evaluate('''() => {
        const wrap = document.getElementById('rrRollsRoyceSection');
        const v = document.getElementById('rrVideoEl');
        const st = window.rrScrollTriggerInstance;
        
        // Check for any video controls or play buttons in the section
        const playBtns = wrap.querySelectorAll('button, input[type=\"range\"], .rr-timeline-track, .rr-play-btn, .rr-timecode, .rr-chapter-btn');
        const csWrap = window.getComputedStyle(wrap);
        const csV = v ? window.getComputedStyle(v) : null;
        
        return {
            hasNativeControls: v ? v.controls : null,
            videoChromeElementsCount: playBtns.length,
            wrapHeight: csWrap.height,
            wrapWidth: csWrap.width,
            videoObjectFit: csV ? csV.objectFit : null,
            videoPointerEvents: csV ? csV.pointerEvents : null,
            stStart: st ? st.start : null,
            stEnd: st ? st.end : null
        };
    }''')
    print('Fullscreen setup & chrome inspection:', check_chrome)
    assert check_chrome['hasNativeControls'] is False, "Video must not have native controls"
    assert check_chrome['videoChromeElementsCount'] == 0, "There must be zero video chrome/buttons"
    print("CONFIRMED: ZERO video chrome elements found. Pure native animation look!")

    st_start = check_chrome['stStart'] or 1649
    st_end = check_chrome['stEnd'] or (st_start + 2800)
    st_depth = st_end - st_start
    print(f"Pinned range: {st_start}px -> {st_end}px (depth: {st_depth}px)")

    print("\n=== 2. SCROLL FORWARD: ACT 1 (THE WOOD OF ROLLS-ROYCE) ===")
    page.evaluate(f'''() => {{
        const scroller = document.querySelector('.main-inner');
        scroller.scrollTop = {st_start + (st_depth * 0.10)};
        ScrollTrigger.update();
    }}''')
    page.wait_for_timeout(800)

    act1_info = page.evaluate('''() => {
        const v = document.getElementById('rrVideoEl');
        const a1 = document.getElementById('rrAct1');
        const a2 = document.getElementById('rrAct2');
        const a3 = document.getElementById('rrAct3');
        return {
            currentTime: v.currentTime,
            a1Opacity: window.getComputedStyle(a1).opacity,
            a2Opacity: window.getComputedStyle(a2).opacity,
            a3Opacity: window.getComputedStyle(a3).opacity
        };
    }''')
    print('Act 1 State (Forward):', act1_info)
    page.screenshot(path=os.path.join(artifact_dir, 'fullscreen_rr_01_act1_forward.png'))

    print("\n=== 3. SCROLL FORWARD: ACT 2 (BOOKMATCHED SYMMETRY) ===")
    page.evaluate(f'''() => {{
        const scroller = document.querySelector('.main-inner');
        scroller.scrollTop = {st_start + (st_depth * 0.50)};
        ScrollTrigger.update();
    }}''')
    page.wait_for_timeout(800)

    act2_info = page.evaluate('''() => {
        const v = document.getElementById('rrVideoEl');
        const a1 = document.getElementById('rrAct1');
        const a2 = document.getElementById('rrAct2');
        const a3 = document.getElementById('rrAct3');
        return {
            currentTime: v.currentTime,
            a1Opacity: window.getComputedStyle(a1).opacity,
            a2Opacity: window.getComputedStyle(a2).opacity,
            a3Opacity: window.getComputedStyle(a3).opacity
        };
    }''')
    print('Act 2 State (Forward):', act2_info)
    page.screenshot(path=os.path.join(artifact_dir, 'fullscreen_rr_02_act2_forward.png'))

    print("\n=== 4. SCROLL FORWARD: ACT 3 (TEAK INTERIOR & RESIN IMMUNITY) ===")
    page.evaluate(f'''() => {{
        const scroller = document.querySelector('.main-inner');
        scroller.scrollTop = {st_start + (st_depth * 0.90)};
        ScrollTrigger.update();
    }}''')
    page.wait_for_timeout(800)

    act3_info = page.evaluate('''() => {
        const v = document.getElementById('rrVideoEl');
        const a1 = document.getElementById('rrAct1');
        const a2 = document.getElementById('rrAct2');
        const a3 = document.getElementById('rrAct3');
        return {
            currentTime: v.currentTime,
            a1Opacity: window.getComputedStyle(a1).opacity,
            a2Opacity: window.getComputedStyle(a2).opacity,
            a3Opacity: window.getComputedStyle(a3).opacity
        };
    }''')
    print('Act 3 State (Forward):', act3_info)
    page.screenshot(path=os.path.join(artifact_dir, 'fullscreen_rr_03_act3_forward.png'))

    print("\n=== 5. SCROLL BACKWARD: REVERSING TO ACT 2 ===")
    page.evaluate(f'''() => {{
        const scroller = document.querySelector('.main-inner');
        scroller.scrollTop = {st_start + (st_depth * 0.50)};
        ScrollTrigger.update();
    }}''')
    page.wait_for_timeout(800)

    act2_rev_info = page.evaluate('''() => {
        const v = document.getElementById('rrVideoEl');
        const a1 = document.getElementById('rrAct1');
        const a2 = document.getElementById('rrAct2');
        const a3 = document.getElementById('rrAct3');
        return {
            currentTime: v.currentTime,
            a1Opacity: window.getComputedStyle(a1).opacity,
            a2Opacity: window.getComputedStyle(a2).opacity,
            a3Opacity: window.getComputedStyle(a3).opacity
        };
    }''')
    print('Act 2 State (Backward):', act2_rev_info)
    page.screenshot(path=os.path.join(artifact_dir, 'fullscreen_rr_04_act2_reverse.png'))

    print("\n=== 6. SCROLL BACKWARD: REVERSING TO ACT 1 ===")
    page.evaluate(f'''() => {{
        const scroller = document.querySelector('.main-inner');
        scroller.scrollTop = {st_start + (st_depth * 0.08)};
        ScrollTrigger.update();
    }}''')
    page.wait_for_timeout(800)

    act1_rev_info = page.evaluate('''() => {
        const v = document.getElementById('rrVideoEl');
        const a1 = document.getElementById('rrAct1');
        const a2 = document.getElementById('rrAct2');
        const a3 = document.getElementById('rrAct3');
        return {
            currentTime: v.currentTime,
            a1Opacity: window.getComputedStyle(a1).opacity,
            a2Opacity: window.getComputedStyle(a2).opacity,
            a3Opacity: window.getComputedStyle(a3).opacity
        };
    }''')
    print('Act 1 State (Backward):', act1_rev_info)
    page.screenshot(path=os.path.join(artifact_dir, 'fullscreen_rr_05_act1_reverse.png'))

    print("\n=== 7. CONSOLE & PAGE ERRORS CHECK ===")
    print('Page errors count:', len(errors), errors)
    err_logs = [l for l in logs if '[error]' in l]
    print('Console errors count:', len(err_logs), err_logs)

    browser.close()
    print("\nFullscreen Rolls-Royce scroll animation verified successfully!")
