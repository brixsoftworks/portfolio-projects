from playwright.sync_api import sync_playwright
import time

html_content = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700&family=JetBrains+Mono:wght@500;700&display=swap');
  
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    width: 3428px;
    height: 754px;
    background: transparent;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  svg {
    width: 3428px;
    height: 754px;
  }
  
  .cad-letter {
    font-family: 'Space Grotesk', -apple-system, sans-serif;
    font-size: 340px;
    font-weight: 700;
    fill: none;
    stroke: #282828;
    stroke-width: 4px;
    stroke-linejoin: miter;
    stroke-miterlimit: 4;
    letter-spacing: 0.12em;
  }
  
  .cad-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 56px;
    font-weight: 700;
    fill: none;
    stroke: #525252;
    stroke-width: 2px;
    letter-spacing: 0.28em;
  }

  .cad-crosshair {
    stroke: #737373;
    stroke-width: 1.5px;
    stroke-dasharray: 6 6;
  }

  .cad-tick {
    stroke: #282828;
    stroke-width: 2.5px;
  }
</style>
</head>
<body>
<svg viewBox="0 0 3428 754" fill="none" xmlns="http://www.w3.org/2000/svg">
  <!-- Horizontal & Vertical Construction Guidelines -->
  <line x1="80" y1="120" x2="3348" y2="120" stroke="#a3a3a3" stroke-width="1.5" stroke-dasharray="8 8" opacity="0.6"/>
  <line x1="80" y1="520" x2="3348" y2="520" stroke="#a3a3a3" stroke-width="1.5" stroke-dasharray="8 8" opacity="0.6"/>
  <line x1="80" y1="640" x2="3348" y2="640" stroke="#a3a3a3" stroke-width="1.5" stroke-dasharray="8 8" opacity="0.4"/>
  
  <!-- Outer Corner CAD Bounding Ticks -->
  <path d="M 60 100 L 60 140 M 40 120 L 80 120" stroke="#282828" stroke-width="3"/>
  <path d="M 3368 100 L 3368 140 M 3348 120 L 3388 120" stroke="#282828" stroke-width="3"/>
  <path d="M 60 500 L 60 540 M 40 520 L 80 520" stroke="#282828" stroke-width="3"/>
  <path d="M 3368 500 L 3368 540 M 3348 520 L 3388 520" stroke="#282828" stroke-width="3"/>
  
  <!-- Center Axis Crosshair -->
  <line x1="1714" y1="40" x2="1714" y2="714" stroke="#e5e5e5" stroke-width="1" stroke-dasharray="4 8"/>
  <circle cx="1714" cy="320" r="14" stroke="#737373" stroke-width="2" fill="none"/>
  <line x1="1690" y1="320" x2="1738" y2="320" stroke="#737373" stroke-width="2"/>
  <line x1="1714" y1="296" x2="1714" y2="344" stroke="#737373" stroke-width="2"/>

  <!-- Big CAD Architectural Outlined Title -->
  <text x="1714" y="470" text-anchor="middle" class="cad-letter">AISWARYA</text>
  
  <!-- Subtitle -->
  <text x="1714" y="625" text-anchor="middle" class="cad-sub">DEALERS IN WOODEN FURNITURE &amp; INTERIORS • NILAMBUR</text>
</svg>
</body>
</html>
"""

with open('/tmp/footer_graphic.html', 'w') as f:
    f.write(html_content)

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path='/home/mullainathan/.local/bin/google-chrome',
        headless=True,
        args=['--no-sandbox', '--disable-setuid-sandbox']
    )
    page = browser.new_page(viewport={'width': 3428, 'height': 754}, device_scale_factor=1)
    page.goto('file:///tmp/footer_graphic.html', wait_until='networkidle')
    time.sleep(2)
    page.screenshot(path='/home/mullainathan/projects/nilambur-teak-wood/public/images/aiswarya-footer-big.png', omit_background=True)
    print('Generated aiswarya-footer-big.png successfully!')
    browser.close()
