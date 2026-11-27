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

        # 1. SCROLL TO FOOTER
        print("\n=== 1. SCROLLING TO ADVANCED FOOTER ===")
        page.evaluate('''() => {
            const mi = document.querySelector('.main-inner');
            if (mi) mi.scrollTo({ top: mi.scrollHeight, behavior: 'instant' });
        }''')
        page.wait_for_timeout(1000)

        # 2. VERIFY FOOTER TELEMETRY BAR
        print("\n=== 2. VERIFYING FOOTER TELEMETRY BAR ===")
        telem_data = page.evaluate('''() => {
            const bar = document.querySelector('.footer-telemetry-bar');
            const time = document.getElementById('footerLiveTime');
            return {
                barExists: !!bar,
                timeText: time ? time.textContent : '',
                fullText: bar ? bar.textContent.trim().replace(/\\s+/g, ' ') : ''
            };
        }''')
        print("Telemetry Bar Data:", telem_data)
        assert telem_data['barExists'], "Footer telemetry bar missing"
        assert 'IST' in telem_data['timeText'], "Live clock IST format missing"

        # 3. VERIFY FOOTER INQUIRY INTENT CHIPS
        print("\n=== 3. VERIFYING INQUIRY INTENT CHIPS ===")
        chips_data = page.evaluate('''() => {
            const chips = Array.from(document.querySelectorAll('.intent-chip')).map(c => c.textContent.trim());
            const activeChip = document.querySelector('.intent-chip.active');
            return {
                chips: chips,
                activeChip: activeChip ? activeChip.textContent.trim() : ''
            };
        }''')
        print("Chips Data:", chips_data)
        assert len(chips_data['chips']) == 4, "Expected 4 intent chips"

        # Click ROLLS-ROYCE CABIN chip
        print("Clicking 'ROLLS-ROYCE CABIN' chip...")
        page.evaluate('''() => {
            const btn = Array.from(document.querySelectorAll('.intent-chip')).find(c => c.textContent.includes('ROLLS-ROYCE'));
            if (btn) btn.click();
        }''')
        page.wait_for_timeout(300)
        chip_click_result = page.evaluate('''() => {
            const active = document.querySelector('.intent-chip.active');
            const input = document.getElementById('email');
            return {
                activeText: active ? active.textContent.trim() : '',
                inputPlaceholder: input ? input.placeholder : ''
            };
        }''')
        print("Chip click result:", chip_click_result)
        assert 'ROLLS-ROYCE' in chip_click_result['activeText'], "Active chip not updated"

        # 4. VERIFY 3D BRASS MEDALLION IN FOOTER LOGO
        print("\n=== 4. VERIFYING FOOTER 3D BRASS MEDALLION ===")
        seal_data = page.evaluate('''() => {
            const med = document.getElementById('footerSealMedallion');
            const caption = document.querySelector('.footer-seal-caption');
            return {
                medExists: !!med,
                captionText: caption ? caption.textContent.trim().replace(/\\s+/g, ' ') : ''
            };
        }''')
        print("Seal Data:", seal_data)
        assert seal_data['medExists'], "Medallion missing"

        # Click to tumble seal
        print("Clicking 3D Brass Medallion to tumble...")
        page.evaluate('''() => {
            const med = document.getElementById('footerSealMedallion');
            if (med) med.click();
        }''')
        page.wait_for_timeout(400)
        tumble_check = page.evaluate('''() => {
            const med = document.getElementById('footerSealMedallion');
            return med ? med.style.transform : '';
        }''')
        print("Medallion transform during tumble:", tumble_check)

        # 5. VERIFY FOOTER BLUEPRINT MASTER CARD
        print("\n=== 5. VERIFYING FOOTER BLUEPRINT MASTER CARD ===")
        bp_data = page.evaluate('''() => {
            const card = document.getElementById('footerBlueprintCard');
            const laser = document.getElementById('footerLaserBeam');
            const sheen = document.getElementById('footerSheen');
            const callouts = Array.from(document.querySelectorAll('.footer-bp-callout')).map(c => c.textContent.trim());
            const hud = document.querySelector('.footer-cad-hud');
            return {
                cardExists: !!card,
                laserExists: !!laser,
                sheenExists: !!sheen,
                callouts: callouts,
                hudText: hud ? hud.textContent.trim().replace(/\\s+/g, ' ') : ''
            };
        }''')
        print("Blueprint Card Data:", bp_data)
        assert bp_data['cardExists'], "Blueprint card missing"
        assert len(bp_data['callouts']) == 3, f"Expected 3 callouts, got {len(bp_data['callouts'])}"

        # Hover over blueprint card to trigger 3D perspective tilt
        page.evaluate('''() => {
            const card = document.getElementById('footerBlueprintCard');
            if (card) {
                const rect = card.getBoundingClientRect();
                const evt = new MouseEvent('mousemove', {
                    clientX: rect.left + rect.width * 0.7,
                    clientY: rect.top + rect.height * 0.35,
                    bubbles: true
                });
                card.dispatchEvent(evt);
            }
        }''')
        page.wait_for_timeout(300)
        bp_tilt = page.evaluate('''() => {
            const card = document.getElementById('footerBlueprintCard');
            const hud = document.getElementById('archHud');
            return {
                transform: card ? card.style.transform : '',
                hudText: hud ? hud.textContent : ''
            };
        }''')
        print("Blueprint 3D tilt & reticle:", bp_tilt)

        # Screenshot Footer Top (Telemetry, Form with Chips, 3D Medallion)
        screenshot1 = f"{artifact_dir}/footer_01_telemetry_chips_medallion.png"
        page.screenshot(path=screenshot1)
        print(f"Saved {screenshot1}")

        # Scroll down slightly to center blueprint card
        page.evaluate('''() => {
            const card = document.getElementById('footerBlueprintCard');
            const mi = document.querySelector('.main-inner');
            if (card && mi) {
                const rect = card.getBoundingClientRect();
                mi.scrollTo({ top: mi.scrollTop + rect.top - 80, behavior: 'instant' });
            }
        }''')
        page.wait_for_timeout(500)

        # Trigger Re-Scan button
        print("\n=== 6. TESTING RE-SCAN BLUEPRINT BUTTON ===")
        page.evaluate('''() => {
            const btn = document.querySelector('.footer-rescan-btn');
            if (btn) btn.click();
        }''')
        page.wait_for_timeout(400)
        rescan_state = page.evaluate('''() => {
            const laser = document.getElementById('footerLaserBeam');
            const sheen = document.getElementById('footerSheen');
            return {
                laserTop: laser ? laser.style.top : '',
                laserOpacity: laser ? laser.style.opacity : ''
            };
        }''')
        print("Rescan active state:", rescan_state)

        screenshot2 = f"{artifact_dir}/footer_02_blueprint_laser_callouts.png"
        page.screenshot(path=screenshot2)
        print(f"Saved {screenshot2}")

        # 7. TEST RETURN TO CANOPY [TOP] ELEVATOR
        print("\n=== 7. TESTING RETURN TO CANOPY [TOP] ELEVATOR ===")
        page.evaluate('''() => {
            const btn = document.querySelector('.footer-back-to-top-btn');
            if (btn) btn.click();
        }''')
        page.wait_for_timeout(1000)
        top_scroll = page.evaluate('''() => {
            const mi = document.querySelector('.main-inner');
            return mi ? mi.scrollTop : window.scrollY;
        }''')
        print("Scroll position after Return to Canopy:", top_scroll)

        screenshot3 = f"{artifact_dir}/footer_03_top_canopy_returned.png"
        page.screenshot(path=screenshot3)
        print(f"Saved {screenshot3}")

        # 8. CONSOLE ERRORS
        print("\n=== Console Errors ===")
        filtered_errors = [e for e in errors if '404' not in e]
        print("Non-404 Errors count:", len(filtered_errors))
        for err in filtered_errors:
            print("Error:", err)
        assert len(filtered_errors) == 0, f"Found JavaScript errors: {filtered_errors}"

        print("\nALL FOOTER TESTS PASSED WITH ZERO JAVASCRIPT ERRORS!")
        browser.close()

if __name__ == "__main__":
    run_tests()
