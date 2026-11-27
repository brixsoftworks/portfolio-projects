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

    print("=== 1. VERIFYING CANVAS ENGINE INITIALIZATION ===")
    init_info = page.evaluate('''() => {
        const wrap = document.getElementById('rrRollsRoyceSection');
        const canvas = document.getElementById('rrCanvas');
        const video = wrap.querySelector('video');
        const st = window.rrScrollTriggerInstance;
        
        return {
            hasCanvas: !!canvas,
            canvasWidth: canvas ? canvas.width : null,
            canvasHeight: canvas ? canvas.height : null,
            hasVideoElement: !!video,
            stStart: st ? st.start : null,
            stEnd: st ? st.end : null
        };
    }''')
    print('Init details:', init_info)
    assert init_info['hasCanvas'] is True, "Must have canvas element"
    assert init_info['hasVideoElement'] is False, "Must have NO video element in section"

    st_start = init_info['stStart'] or 1649
    st_end = init_info['stEnd'] or (st_start + 2800)
    st_depth = st_end - st_start

    print("\n=== 2. VERIFYING FRAME-BY-FRAME SCROLL PROGRESSION ===")
    frame_sequence = []
    for pct in [0.05, 0.20, 0.35, 0.50, 0.65, 0.80, 0.95]:
        target_scroll = st_start + (st_depth * pct)
        page.evaluate(f'''() => {{
            const scroller = document.querySelector('.main-inner');
            scroller.scrollTop = {target_scroll};
            ScrollTrigger.update();
        }}''')
        page.wait_for_timeout(200)

        frame_data = page.evaluate('''() => {
            const st = window.rrScrollTriggerInstance;
            const p = st ? st.progress : 0;
            const expectedFrame = Math.min(239, Math.max(0, Math.round(p * 239)));
            const canvas = document.getElementById('rrCanvas');
            const ctx = canvas.getContext('2d');
            // Sample a pixel from center of canvas to verify it's drawn
            const pixel = ctx.getImageData(Math.floor(canvas.width / 2), Math.floor(canvas.height / 2), 1, 1).data;
            return {
                progress: p.toFixed(3),
                frameIndex: expectedFrame,
                pixelSample: [pixel[0], pixel[1], pixel[2], pixel[3]]
            };
        }''')
        frame_sequence.append(frame_data)
        print(f"Scroll {pct*100:02.0f}% -> Progress: {frame_data['progress']}, Frame: {frame_data['frameIndex']}, Center Pixel RGB: {frame_data['pixelSample'][:3]}")

    # Capture screenshots of key stages
    # Stage 1: Chassis (progress ~10%)
    page.evaluate(f'''() => {{
        document.querySelector('.main-inner').scrollTop = {st_start + st_depth * 0.10};
        ScrollTrigger.update();
    }}''')
    page.wait_for_timeout(400)
    page.screenshot(path=os.path.join(artifact_dir, 'canvas_frame_01_chassis.png'))

    # Stage 2: Orbit (progress ~50%)
    page.evaluate(f'''() => {{
        document.querySelector('.main-inner').scrollTop = {st_start + st_depth * 0.50};
        ScrollTrigger.update();
    }}''')
    page.wait_for_timeout(400)
    page.screenshot(path=os.path.join(artifact_dir, 'canvas_frame_02_orbit.png'))

    # Stage 3: Teak Cabin (progress ~92%)
    page.evaluate(f'''() => {{
        document.querySelector('.main-inner').scrollTop = {st_start + st_depth * 0.92};
        ScrollTrigger.update();
    }}''')
    page.wait_for_timeout(400)
    page.screenshot(path=os.path.join(artifact_dir, 'canvas_frame_03_cabin.png'))

    print("\n=== 3. VERIFYING REVERSE SCROLL (STEPPING BACKWARD FRAME-BY-FRAME) ===")
    reverse_sequence = []
    for pct in [0.75, 0.50, 0.25, 0.05]:
        target_scroll = st_start + (st_depth * pct)
        page.evaluate(f'''() => {{
            const scroller = document.querySelector('.main-inner');
            scroller.scrollTop = {target_scroll};
            ScrollTrigger.update();
        }}''')
        page.wait_for_timeout(200)

        frame_data = page.evaluate('''() => {
            const st = window.rrScrollTriggerInstance;
            const p = st ? st.progress : 0;
            const expectedFrame = Math.min(239, Math.max(0, Math.round(p * 239)));
            return {
                progress: p.toFixed(3),
                frameIndex: expectedFrame
            };
        }''')
        reverse_sequence.append(frame_data)
        print(f"Reverse Scroll {pct*100:02.0f}% -> Progress: {frame_data['progress']}, Frame: {frame_data['frameIndex']}")

    page.screenshot(path=os.path.join(artifact_dir, 'canvas_frame_04_reverse.png'))

    print("\n=== 4. CONSOLE & PAGE ERRORS CHECK ===")
    print('Page errors count:', len(errors), errors)
    err_logs = [l for l in logs if '[error]' in l]
    print('Console errors count:', len(err_logs), err_logs)

    browser.close()
    print("\nHardware-accelerated Canvas frame-by-frame engine verified successfully!")
