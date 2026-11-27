import os
import time
from playwright.sync_api import sync_playwright

artifact_dir = "/home/mullainathan/.gemini/antigravity-cli/brain/14a6194d-1561-4011-ac2d-90f19685bcb1"

def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path='/home/mullainathan/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome'
        )
        page = browser.new_page(viewport={'width': 1440, 'height': 900})

        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.on("console", lambda msg: errors.append(f"Console {msg.type}: {msg.text}") if msg.type == 'error' else None)

        print("Navigating to http://localhost:3005/nilambur.html...")
        page.goto('http://localhost:3005/nilambur.html', wait_until='networkidle')
        page.wait_for_timeout(1000)

        # 1. VERIFY WHY US LOWER SIDE IMAGES EXISTENCE & STRUCTURE
        print("\n=== 1. VERIFYING WHY US LOWER SIDE IMAGES STRUCTURE ===")
        why_cards_data = page.evaluate('''() => {
            const cards = Array.from(document.querySelectorAll('.why-side-img-card'));
            return cards.map((c, i) => {
                const badge = c.querySelector('.why-col-badge');
                const btn = c.querySelector('.why-rewipe-btn');
                const laser = c.querySelector('.pixel-wipe-laser-beam');
                const grid = c.querySelector('.pixel-matrix-grid');
                const sheen = c.querySelector('.hero-wood-sheen');
                const hud = c.querySelector('.why-cad-hud');
                const reveal = c.querySelector('.pixel-reveal-img');
                const parent = c.closest('.home-why-item');
                return {
                    idx: i,
                    badgeText: badge ? badge.textContent.trim().replace(/\\s+/g, ' ') : '',
                    hasBtn: !!btn,
                    hasLaser: !!laser,
                    hasGrid: !!grid,
                    hasSheen: !!sheen,
                    hasHud: !!hud,
                    hudText: hud ? hud.textContent.trim().replace(/\\s+/g, ' ') : '',
                    isRevealed: !!reveal,
                    parentClass: parent ? parent.className : ''
                };
            });
        }''')
        print(f"Found {len(why_cards_data)} Why Us side cards:")
        for card in why_cards_data:
            print(" -", card)

        # 2. SCROLL TO EACH WHY US SIDE CARD & VERIFY ANIMATION
        print("\n=== 2. SCROLLING TO WHY US LOWER SIDE IMAGES & TESTING REVEAL ===")
        for i in range(len(why_cards_data)):
            page.evaluate(f'''() => {{
                const card = document.getElementById('whyCard{i}');
                const mi = document.querySelector('.main-inner');
                if (card && mi) {{
                    const rect = card.getBoundingClientRect();
                    mi.scrollTo({{ top: mi.scrollTop + rect.top - 150, behavior: 'instant' }});
                }}
            }}''')
            page.wait_for_timeout(800)

            # Check laser, mask, and 3D hover
            card_state = page.evaluate(f'''() => {{
                const card = document.getElementById('whyCard{i}');
                if (!card) return {{}};
                const laser = card.querySelector('.pixel-wipe-laser-beam');
                const img = card.querySelector('.pixel-reveal-img');
                const rect = card.getBoundingClientRect();
                return {{
                    laserTop: laser ? laser.style.top : '',
                    laserOpacity: laser ? laser.style.opacity : '',
                    maskPos: img ? (img.style.webkitMaskPosition || img.style.maskPosition) : '',
                    rect: {{ x: Math.round(rect.left), y: Math.round(rect.top), w: Math.round(rect.width), h: Math.round(rect.height) }}
                }};
            }}''')
            print(f"Why Card {i} state after scroll:", card_state)

            # Hover over card to trigger 3D perspective tilt & CAD reticle
            page.evaluate(f'''() => {{
                const card = document.getElementById('whyCard{i}');
                if (card) {{
                    const rect = card.getBoundingClientRect();
                    const evt = new MouseEvent('mousemove', {{
                        clientX: rect.left + rect.width * 0.75,
                        clientY: rect.top + rect.height * 0.35,
                        bubbles: true
                    }});
                    card.dispatchEvent(evt);
                }}
            }}''')
            page.wait_for_timeout(300)

            tilt_data = page.evaluate(f'''() => {{
                const card = document.getElementById('whyCard{i}');
                const hud = document.getElementById('archHud');
                return {{
                    transform: card ? card.style.transform : '',
                    archHudText: hud ? hud.textContent : ''
                }};
            }}''')
            print(f"Why Card {i} 3D tilt & HUD:", tilt_data)

            screenshot_path = f"{artifact_dir}/side_img_0{i+1}_why_step_{i+1}.png"
            page.screenshot(path=screenshot_path)
            print(f"Saved {screenshot_path}")

        # 3. TEST INTERACTIVE RE-WIPE ON LOWER SIDE IMAGE
        print("\n=== 3. TESTING INTERACTIVE RE-WIPE ON LOWER SIDE CARD 0 ===")
        rewipe_check = page.evaluate('''() => {
            const btn = document.querySelector('#whyCard0 .why-rewipe-btn');
            if (btn) btn.click();
            const card = document.getElementById('whyCard0');
            const laser = card ? card.querySelector('.pixel-wipe-laser-beam') : null;
            const sheen = card ? card.querySelector('.hero-wood-sheen') : null;
            return {
                clicked: !!btn,
                laserActive: !!laser,
                sheenActive: !!sheen
            };
        }''')
        print("Re-wipe trigger result:", rewipe_check)
        page.wait_for_timeout(500)
        page.screenshot(path=f"{artifact_dir}/side_img_05_why_rewipe_active.png")
        print("Saved side_img_05_why_rewipe_active.png")

        # 4. TEST PLATFORM LOWER SIDE CARDS
        print("\n=== 4. TESTING PLATFORM ATELIER LOWER SIDE CARDS ===")
        page.evaluate('''() => {
            const card = document.getElementById('platCard0');
            const mi = document.querySelector('.main-inner');
            if (card && mi) {
                const rect = card.getBoundingClientRect();
                mi.scrollTo({ top: mi.scrollTop + rect.top - 150, behavior: 'instant' });
            }
        }''')
        page.wait_for_timeout(800)

        plat_card_check = page.evaluate('''() => {
            const cards = Array.from(document.querySelectorAll('.platform-side-img-card'));
            return cards.map(c => ({
                id: c.id,
                hasLaser: !!c.querySelector('.pixel-wipe-laser-beam'),
                hasGrid: !!c.querySelector('.pixel-matrix-grid'),
                hasSheen: !!c.querySelector('.hero-wood-sheen'),
                badge: c.querySelector('.platform-col-badge') ? c.querySelector('.platform-col-badge').textContent.trim() : ''
            }));
        }''')
        print("Platform cards check:", plat_card_check)
        page.screenshot(path=f"{artifact_dir}/side_img_06_platform_side_card.png")
        print("Saved side_img_06_platform_side_card.png")

        # 5. TEST EXPLORE WOODCRAFT COURTYARD LASER WIPE
        print("\n=== 5. TESTING EXPLORE WOODCRAFT COURTYARD LASER WIPE ===")
        page.evaluate('''() => {
            const intro = document.querySelector('.home-intro-wrap');
            const mi = document.querySelector('.main-inner');
            if (intro && mi) {
                const rect = intro.getBoundingClientRect();
                mi.scrollTo({ top: mi.scrollTop + rect.top - 100, behavior: 'instant' });
            }
        }''')
        page.wait_for_timeout(800)
        intro_elements = page.evaluate('''() => {
            const pw = document.getElementById('introPixelWrap');
            return {
                hasLaser: !!(pw && pw.querySelector('.pixel-wipe-laser-beam')),
                hasGrid: !!(pw && pw.querySelector('.pixel-matrix-grid')),
                hasSheen: !!(pw && pw.querySelector('.hero-wood-sheen'))
            };
        }''')
        print("Intro courtyard elements check:", intro_elements)
        page.screenshot(path=f"{artifact_dir}/side_img_07_intro_courtyard_laser.png")
        print("Saved side_img_07_intro_courtyard_laser.png")

        # 6. CONSOLE ERRORS
        print("\n=== Page Errors ===")
        print("Errors count:", len(errors))
        for err in errors:
            print("Error:", err)

        browser.close()

if __name__ == "__main__":
    run_tests()
