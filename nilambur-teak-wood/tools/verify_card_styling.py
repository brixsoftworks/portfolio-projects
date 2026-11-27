from playwright.sync_api import sync_playwright
import time

artifact_dir = '/home/mullainathan/.gemini/antigravity-cli/brain/14a6194d-1561-4011-ac2d-90f19685bcb1'

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path='/home/mullainathan/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome',
        headless=True
    )
    page = browser.new_page(viewport={'width': 1440, 'height': 900})

    print("Navigating to http://localhost:3005/nilambur.html...")
    page.goto('http://localhost:3005/nilambur.html', wait_until='networkidle')
    page.wait_for_timeout(1000)

    # 1. Scroll .main-inner to Act 1 (scrollY = 1620)
    print("\n--- 1. SCROLLING TO ACT 1 (1620px) ---")
    page.evaluate('''() => {
        const mi = document.querySelector('.main-inner');
        if (mi) mi.scrollTo({ top: 1620, behavior: 'instant' });
    }''')
    page.wait_for_timeout(600)
    page.screenshot(path=f"{artifact_dir}/card_styling_act1.png")
    print("Saved card_styling_act1.png")

    # 2. Scroll .main-inner to Act 2 (scrollY = 3010)
    print("\n--- 2. SCROLLING TO ACT 2 (3010px) ---")
    page.evaluate('''() => {
        const mi = document.querySelector('.main-inner');
        if (mi) mi.scrollTo({ top: 3010, behavior: 'instant' });
    }''')
    page.wait_for_timeout(600)
    page.screenshot(path=f"{artifact_dir}/card_styling_act2.png")
    print("Saved card_styling_act2.png")

    # 3. Scroll .main-inner to Act 3 (scrollY = 3990)
    print("\n--- 3. SCROLLING TO ACT 3 (3990px) ---")
    page.evaluate('''() => {
        const mi = document.querySelector('.main-inner');
        if (mi) mi.scrollTo({ top: 3990, behavior: 'instant' });
    }''')
    page.wait_for_timeout(600)
    page.screenshot(path=f"{artifact_dir}/card_styling_act3.png")
    print("Saved card_styling_act3.png")

    # Inspect computed styles of Act 3
    styles = page.evaluate('''() => {
        const act3 = document.getElementById('rrAct3');
        if (!act3) return { error: 'act3 not found' };
        const title = act3.querySelector('.rr-act-title');
        const desc = act3.querySelector('.rr-act-desc');
        const tag = act3.querySelector('.rr-act-tag');
        const specItem = act3.querySelector('.rr-spec-item');
        const specNum = act3.querySelector('.rr-spec-num');
        const specLabel = act3.querySelector('.rr-spec-label');

        const getComputed = (el) => {
            if (!el) return null;
            const s = window.getComputedStyle(el);
            return {
                bg: s.backgroundColor,
                color: s.color,
                fontFamily: s.fontFamily,
                fontSize: s.fontSize,
                fontWeight: s.fontWeight,
                border: s.border,
                borderRadius: s.borderRadius,
                boxShadow: s.boxShadow
            };
        };

        return {
            act3Opacity: window.getComputedStyle(act3).opacity,
            act3: getComputed(act3),
            title: getComputed(title),
            desc: getComputed(desc),
            tag: getComputed(tag),
            specItem: getComputed(specItem),
            specNum: getComputed(specNum),
            specLabel: getComputed(specLabel)
        };
    }''')

    print("\n=== Computed Styles for Act 3 Elements ===")
    for k, v in styles.items():
        print(f"[{k}]: {v}")

    browser.close()
