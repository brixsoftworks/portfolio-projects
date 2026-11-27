import re

with open('/home/mullainathan/projects/nilambur-teak-wood/clean_aiswarya_builder.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ==============================================================================
# 1. UPDATE CSS IN head_injections
# ==============================================================================
innovations_css = """
      /* === INNOVATION 1: ACOUSTIC WOOD TAP SOUND TOGGLE === */
      .sound-toggle-btn {
        position: fixed !important;
        top: 18px !important;
        right: 90px !important;
        z-index: 9999 !important;
        background: rgba(28, 24, 21, 0.9) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        color: #efece6 !important;
        border: 1px solid rgba(217, 119, 6, 0.45) !important;
        padding: 7px 14px !important;
        border-radius: 999px !important;
        font-size: 11px !important;
        font-family: 'Geistmono', monospace !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
      }
      .sound-toggle-btn:hover {
        background: var(--content--brand) !important;
        color: #fff !important;
        border-color: var(--content--brand) !important;
        transform: scale(1.03) !important;
      }
      .sound-wave-dot {
        width: 6px !important;
        height: 6px !important;
        border-radius: 50% !important;
        background: #10b981 !important;
        transition: background 0.2s ease !important;
      }
      .sound-wave-dot.muted {
        background: #ef4444 !important;
      }

      /* === INNOVATION 2: ARCHITECTURAL DRAFTING CROSSHAIR CURSOR === */
      .arch-crosshair {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        pointer-events: none !important;
        z-index: 9998 !important;
        display: none;
        transform: translate(-50%, -50%) !important;
      }
      .arch-crosshair-circle {
        width: 32px !important;
        height: 32px !important;
        border: 1px dashed rgba(250, 54, 0, 0.65) !important;
        border-radius: 50% !important;
        position: relative !important;
      }
      .arch-crosshair-h {
        position: absolute !important;
        top: 15px !important;
        left: -12px !important;
        width: 56px !important;
        height: 1px !important;
        background: rgba(250, 54, 0, 0.8) !important;
      }
      .arch-crosshair-v {
        position: absolute !important;
        left: 15px !important;
        top: -12px !important;
        width: 1px !important;
        height: 56px !important;
        background: rgba(250, 54, 0, 0.8) !important;
      }
      .arch-crosshair-hud {
        position: absolute !important;
        top: 36px !important;
        left: 36px !important;
        background: rgba(28, 24, 21, 0.92) !important;
        color: #efece6 !important;
        padding: 4px 8px !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 9px !important;
        letter-spacing: 0.1em !important;
        border-radius: 3px !important;
        white-space: nowrap !important;
        border: 1px solid rgba(250, 54, 0, 0.35) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
      }

      /* === INNOVATION 3: ARTISAN WOOD LOUPE (MAGNIFIER) === */
      .teak-loupe {
        position: fixed !important;
        width: 140px !important;
        height: 140px !important;
        border-radius: 50% !important;
        border: 3px solid #d97706 !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4), inset 0 0 20px rgba(217, 119, 6, 0.3) !important;
        pointer-events: none !important;
        z-index: 9990 !important;
        overflow: hidden !important;
        display: none;
        transform: translate(-50%, -50%) !important;
        background-repeat: no-repeat !important;
        background-size: 800px 1200px !important;
        background-color: #1c1815 !important;
      }
      .teak-loupe-reticle {
        position: absolute !important;
        inset: 0 !important;
        pointer-events: none !important;
      }
      .teak-loupe-hud {
        position: absolute !important;
        bottom: -68px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        background: rgba(28, 24, 21, 0.94) !important;
        border: 1px solid #d97706 !important;
        border-radius: 6px !important;
        padding: 6px 10px !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 9px !important;
        color: #fdfbf7 !important;
        white-space: nowrap !important;
        text-align: center !important;
        line-height: 1.35 !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.35) !important;
      }
      .teak-loupe-hud span {
        color: #d97706 !important;
        font-weight: bold !important;
      }

      /* === HERO ACCORDION SPRINGS & CAD HUD === */
      .hero-rewipe-btn {
        position: absolute !important;
        top: 1.2rem !important;
        right: 1.2rem !important;
        z-index: 12 !important;
        background: rgba(28, 24, 21, 0.88) !important;
        backdrop-filter: blur(8px) !important;
        color: #efece6 !important;
        border: 1px solid rgba(250, 54, 0, 0.4) !important;
        border-radius: 4px !important;
        padding: 0.35rem 0.65rem !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 0.75rem !important;
        letter-spacing: 0.08em !important;
        cursor: pointer !important;
        opacity: 0 !important;
        transform: translateY(-4px) !important;
        transition: all 0.25s ease !important;
      }
      .home-hero-img-col:hover .hero-rewipe-btn {
        opacity: 1 !important;
        transform: translateY(0) !important;
      }
      .hero-rewipe-btn:hover {
        background: var(--content--brand) !important;
        color: #fff !important;
      }
      .hero-cad-hud {
        position: absolute !important;
        bottom: 4.4rem !important;
        left: 1.2rem !important;
        right: 1.2rem !important;
        z-index: 11 !important;
        background: rgba(28, 24, 21, 0.92) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(250, 54, 0, 0.35) !important;
        border-radius: 6px !important;
        padding: 0.65rem 0.9rem !important;
        opacity: 0 !important;
        transform: translateY(8px) !important;
        transition: all 0.35s cubic-bezier(0.25, 1, 0.5, 1) !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        pointer-events: none !important;
      }
      .home-hero-img-col:hover .hero-cad-hud {
        opacity: 1 !important;
        transform: translateY(0) !important;
      }
      .cad-specs {
        font-family: 'Geistmono', monospace !important;
        font-size: 0.78rem !important;
        color: #efece6 !important;
        line-height: 1.4 !important;
      }
      .cad-specs strong {
        color: var(--content--brand) !important;
      }
      .cad-corner-marks {
        font-family: 'Geistmono', monospace !important;
        font-size: 0.7rem !important;
        color: #a89f91 !important;
        text-align: right !important;
      }

      /* === INTRO COURTYARD CALIPER MODE === */
      .intro-caliper-toggle-btn {
        position: absolute !important;
        top: 1.2rem !important;
        right: 1.2rem !important;
        z-index: 20 !important;
        background: rgba(28, 24, 21, 0.9) !important;
        backdrop-filter: blur(8px) !important;
        color: #efece6 !important;
        border: 1px solid rgba(217, 119, 6, 0.5) !important;
        border-radius: 4px !important;
        padding: 0.45rem 0.85rem !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 0.78rem !important;
        letter-spacing: 0.08em !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        gap: 0.5rem !important;
        transition: all 0.25s ease !important;
      }
      .intro-caliper-toggle-btn:hover,
      .intro-caliper-toggle-btn.active {
        background: var(--content--brand) !important;
        color: #fff !important;
        border-color: var(--content--brand) !important;
      }
      .intro-caliper-handle {
        position: absolute !important;
        top: 0 !important;
        bottom: 0 !important;
        left: 50% !important;
        width: 32px !important;
        margin-left: -16px !important;
        z-index: 25 !important;
        cursor: ew-resize !important;
        touch-action: none !important;
      }
      .caliper-line {
        position: absolute !important;
        top: 0 !important;
        bottom: 0 !important;
        left: 15px !important;
        width: 2px !important;
        background: var(--content--brand) !important;
        box-shadow: 0 0 10px rgba(250, 54, 0, 0.8) !important;
      }
      .caliper-grip {
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        width: 38px !important;
        height: 38px !important;
        border-radius: 50% !important;
        background: #efece6 !important;
        border: 2px solid var(--content--brand) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
      }

      /* === CHRONOS 100-YEAR PATINA SECTION === */
      .home-patina-wrap {
        width: 100% !important;
        position: relative !important;
        background: var(--bg--sandstone) !important;
        padding: 5rem 0 !important;
        border-top: var(--size--border) solid var(--content--border) !important;
        border-bottom: var(--size--border) solid var(--content--border) !important;
      }
      .patina-container {
        max-width: 1300px !important;
        margin: 0 auto !important;
        padding: 3rem !important;
        background: #1c1815 !important;
        color: #fdfbf7 !important;
        border-radius: 16px !important;
        border: 1px solid rgba(217, 119, 6, 0.3) !important;
        box-shadow: 0 25px 60px rgba(0,0,0,0.35) !important;
        position: relative !important;
        overflow: hidden !important;
      }
      .patina-head {
        display: flex !important;
        justify-content: space-between !important;
        align-items: flex-end !important;
        margin-bottom: 2.5rem !important;
        position: relative !important;
        z-index: 2 !important;
      }
      .patina-tag {
        font-family: 'Geistmono', monospace !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.2em !important;
        color: #d97706 !important;
        text-transform: uppercase !important;
        margin-bottom: 0.4rem !important;
      }
      .patina-title {
        font-size: 2.4rem !important;
        font-weight: 400 !important;
        letter-spacing: -0.02em !important;
        color: #fdfbf7 !important;
        margin: 0 0 0.6rem 0 !important;
      }
      .patina-subtitle {
        font-size: 1rem !important;
        line-height: 1.5 !important;
        color: #a89f91 !important;
        max-width: 650px !important;
        margin: 0 !important;
      }
      .gi-seal-wrap {
        perspective: 800px !important;
        display: inline-block !important;
      }
      .gi-seal-coin {
        width: 100px !important;
        height: 100px !important;
        border-radius: 50% !important;
        background: radial-gradient(circle at 35% 35%, #f59e0b, #b45309 60%, #78350f 100%) !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3), inset 0 2px 4px rgba(255,255,255,0.4), inset 0 -3px 6px rgba(0,0,0,0.6) !important;
        border: 2px solid rgba(253, 251, 247, 0.25) !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        color: #fff !important;
        font-family: 'Geistmono', monospace !important;
        transition: transform 0.15s ease-out !important;
        cursor: pointer !important;
      }
      .gi-seal-coin .small { font-size: 8px !important; letter-spacing: 0.15em !important; opacity: 0.85 !important; }
      .gi-seal-coin .big { font-size: 16px !important; font-weight: bold !important; color: #fef08a !important; margin: 1px 0 !important; }
      .patina-grid {
        display: grid !important;
        grid-template-columns: 1fr 1.25fr !important;
        gap: 3rem !important;
        align-items: center !important;
        position: relative !important;
        z-index: 2 !important;
      }
      @media screen and (max-width: 991px) {
        .patina-grid {
          grid-template-columns: 1fr !important;
        }
      }
      .patina-visual {
        position: relative !important;
        height: 380px !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid rgba(217, 119, 6, 0.3) !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.5) !important;
      }
      .patina-img {
        width: 100% !important;
        height: 100% !important;
        object-fit: cover !important;
        transition: filter 0.5s ease !important;
      }
      .patina-overlay-rings {
        position: absolute !important;
        inset: 0 !important;
        background: radial-gradient(circle at center, transparent 30%, rgba(28,24,21,0.55) 100%) !important;
        pointer-events: none !important;
      }
      .patina-era-badge {
        position: absolute !important;
        top: 1rem !important;
        left: 1rem !important;
        background: rgba(28, 24, 21, 0.9) !important;
        border: 1px solid #d97706 !important;
        border-radius: 4px !important;
        padding: 0.4rem 0.8rem !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.1em !important;
        color: #f59e0b !important;
      }
      .patina-wood-grain-hud {
        position: absolute !important;
        bottom: 1rem !important;
        left: 1rem !important;
        right: 1rem !important;
        background: rgba(28, 24, 21, 0.88) !important;
        border: 1px solid rgba(200, 191, 178, 0.25) !important;
        border-radius: 4px !important;
        padding: 0.45rem 0.8rem !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 0.75rem !important;
        color: #d6d3d1 !important;
        display: flex !important;
        justify-content: space-between !important;
      }
      .patina-controls {
        display: flex !important;
        flex-direction: column !important;
        gap: 1.8rem !important;
      }
      .patina-slider {
        -webkit-appearance: none !important;
        appearance: none !important;
        width: 100% !important;
        height: 6px !important;
        border-radius: 3px !important;
        background: #38312b !important;
        outline: none !important;
        cursor: pointer !important;
      }
      .patina-slider::-webkit-slider-thumb {
        -webkit-appearance: none !important;
        appearance: none !important;
        width: 26px !important;
        height: 26px !important;
        border-radius: 50% !important;
        background: var(--content--brand) !important;
        border: 2px solid #fff !important;
        box-shadow: 0 0 15px rgba(250, 54, 0, 0.7) !important;
        cursor: pointer !important;
        transition: transform 0.15s ease !important;
      }
      .patina-slider::-webkit-slider-thumb:hover {
        transform: scale(1.2) !important;
      }
      .patina-ticks {
        display: flex !important;
        justify-content: space-between !important;
        margin-top: 0.8rem !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.08em !important;
        color: #a89f91 !important;
      }
      .patina-ticks span {
        cursor: pointer !important;
        text-align: center !important;
        transition: color 0.2s ease !important;
      }
      .patina-ticks span.active {
        color: var(--content--brand) !important;
        font-weight: bold !important;
      }
      .patina-metrics-grid {
        display: grid !important;
        grid-template-columns: repeat(3, 1fr) !important;
        gap: 1rem !important;
      }
      .patina-metric-box {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(217, 119, 6, 0.25) !important;
        border-radius: 8px !important;
        padding: 0.9rem !important;
        text-align: center !important;
      }
      .metric-val {
        font-size: 1.8rem !important;
        font-weight: 300 !important;
        color: #f59e0b !important;
        font-family: 'Geistmono', monospace !important;
        margin-bottom: 0.3rem !important;
      }
      .metric-lbl {
        font-family: 'Geistmono', monospace !important;
        font-size: 0.72rem !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
        color: #a89f91 !important;
      }
      .patina-desc {
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
        color: #d6d3d1 !important;
        padding: 1rem 1.2rem !important;
        background: rgba(255, 255, 255, 0.02) !important;
        border-left: 3px solid #d97706 !important;
        border-radius: 0 6px 6px 0 !important;
      }
"""

# Update .home-hero-img-grid in CSS to flex layout
old_grid_css = """.home-hero-img-grid {
        display: grid !important;
        grid-template-columns: repeat(3, 1fr) !important;
        width: 100% !important;
        height: 100% !important;
        position: absolute !important;
        inset: 0 !important;
        pointer-events: auto !important;
        mix-blend-mode: normal !important;
      }
      .home-hero-img-col {
        position: relative !important;
        height: 100% !important;
        width: 100% !important;
        overflow: hidden !important;
        border-right: var(--size--border) solid var(--content--border) !important;
        mix-blend-mode: normal !important;
        cursor: pointer !important;
      }"""

new_grid_css = """.home-hero-img-grid {
        display: flex !important;
        flex-direction: row !important;
        width: 100% !important;
        height: 100% !important;
        position: absolute !important;
        inset: 0 !important;
        pointer-events: auto !important;
        mix-blend-mode: normal !important;
      }
      .home-hero-img-col {
        flex: 1 1 0 !important;
        min-width: 0 !important;
        position: relative !important;
        height: 100% !important;
        overflow: hidden !important;
        border-right: var(--size--border) solid var(--content--border) !important;
        mix-blend-mode: normal !important;
        cursor: crosshair !important;
        transition: flex 0.55s cubic-bezier(0.25, 1, 0.5, 1), box-shadow 0.3s ease !important;
      }
      .home-hero-img-col.active,
      .home-hero-img-col:hover {
        flex: 1.45 1 0 !important;
        box-shadow: 0 10px 30px rgba(250, 54, 0, 0.12) !important;
      }"""

assert old_grid_css in content, "old_grid_css not found"
content = content.replace(old_grid_css, new_grid_css, 1)

# Add the new innovation CSS before </style>
style_end = content.find('</style>')
assert style_end != -1, "</style> not found"
content = content[:style_end] + innovations_css + "\n    " + content[style_end:]

# ==============================================================================
# 2. UPDATE HERO TRIPTYCH HTML WITH REWIPE BTN & CAD HUD
# ==============================================================================
old_triptych = """hero_triptych_html = '''
            <div class="home-hero-img-grid">
              <!-- Panel 01: Heritage Living Room Suite -->
              <div class="home-hero-img-col">
                <div class="home-hero-col-badge">
                  <span class="home-hero-col-num">[01]</span>
                  <span class="home-hero-col-name">HERITAGE LIVING SUITE</span>
                </div>
                <div class="pixel-wipe-wrap">
                  <div class="pixel-wipe-base">
                    <img class="img-basic img-abs" src="/images/living-grand-sketch.webp" alt="Nilambur Teak Living Room Suite Architectural Sketch" />
                  </div>
                  <div class="pixel-wipe-reveal">
                    <img class="img-basic img-abs pixel-reveal-img" src="/images/living-grand-real.jpg" alt="Nilambur Teak Living Room Suite Real Photograph" />
                  </div>
                </div>
              </div>

              <!-- Panel 02: Handcrafted Solid Teak Cot -->
              <div class="home-hero-img-col">
                <div class="home-hero-col-badge">
                  <span class="home-hero-col-num">[02]</span>
                  <span class="home-hero-col-name">SOLID NILAMBUR TEAK COT</span>
                </div>
                <div class="pixel-wipe-wrap">
                  <div class="pixel-wipe-base">
                    <img class="img-basic img-abs" src="/images/bed-sketch.webp" alt="Handcrafted Solid Nilambur Teak Cot Architectural Sketch" />
                  </div>
                  <div class="pixel-wipe-reveal">
                    <img class="img-basic img-abs pixel-reveal-img" src="/images/bed-real.jpg" alt="Handcrafted Solid Nilambur Teak Cot Real Photograph" />
                  </div>
                </div>
              </div>

              <!-- Panel 03: Architectural Modular Teak Kitchen -->
              <div class="home-hero-img-col">
                <div class="home-hero-col-badge">
                  <span class="home-hero-col-num">[03]</span>
                  <span class="home-hero-col-name">MODULAR TEAK KITCHEN</span>
                </div>
                <div class="pixel-wipe-wrap">
                  <div class="pixel-wipe-base">
                    <img class="img-basic img-abs" src="/images/kitchen-sketch.webp" alt="Turnkey Modular Teak Kitchen Architectural Sketch" />
                  </div>
                  <div class="pixel-wipe-reveal">
                    <img class="img-basic img-abs pixel-reveal-img" src="/images/kitchen-real.jpg" alt="Turnkey Modular Teak Kitchen Real Photograph" />
                  </div>
                </div>
              </div>
            </div>
            '''"""

new_triptych = """hero_triptych_html = '''
            <div class="home-hero-img-grid">
              <!-- Panel 01: Heritage Living Room Suite -->
              <div class="home-hero-img-col" id="heroCol0">
                <div class="home-hero-col-badge">
                  <span class="home-hero-col-num">[01]</span>
                  <span class="home-hero-col-name">HERITAGE LIVING SUITE</span>
                </div>
                <button class="hero-rewipe-btn" onclick="rewipeHeroCol(0, event)">↺ RE-WIPE</button>
                <div class="pixel-wipe-wrap">
                  <div class="pixel-wipe-base">
                    <img class="img-basic img-abs" src="/images/living-grand-sketch.webp" alt="Nilambur Teak Living Room Suite Architectural Sketch" />
                  </div>
                  <div class="pixel-wipe-reveal">
                    <img class="img-basic img-abs pixel-reveal-img" src="/images/living-grand-real.jpg" alt="Nilambur Teak Living Room Suite Real Photograph" />
                  </div>
                </div>
                <div class="hero-cad-hud">
                  <div class="cad-specs">
                    <strong>DIMENSIONS:</strong> 2800 × 1050 × 780mm<br>
                    <strong>JOINERY:</strong> Blind Mortise & Tenon • Solid Teak Frame
                  </div>
                  <div class="cad-corner-marks">SCALE 1:20<br>REV: 04-A</div>
                </div>
              </div>

              <!-- Panel 02: Handcrafted Solid Teak Cot -->
              <div class="home-hero-img-col" id="heroCol1">
                <div class="home-hero-col-badge">
                  <span class="home-hero-col-num">[02]</span>
                  <span class="home-hero-col-name">SOLID NILAMBUR TEAK COT</span>
                </div>
                <button class="hero-rewipe-btn" onclick="rewipeHeroCol(1, event)">↺ RE-WIPE</button>
                <div class="pixel-wipe-wrap">
                  <div class="pixel-wipe-base">
                    <img class="img-basic img-abs" src="/images/bed-sketch.webp" alt="Handcrafted Solid Nilambur Teak Cot Architectural Sketch" />
                  </div>
                  <div class="pixel-wipe-reveal">
                    <img class="img-basic img-abs pixel-reveal-img" src="/images/bed-real.jpg" alt="Handcrafted Solid Nilambur Teak Cot Real Photograph" />
                  </div>
                </div>
                <div class="hero-cad-hud">
                  <div class="cad-specs">
                    <strong>BED PLATFORM:</strong> 2050 × 1850 × 1100mm (King)<br>
                    <strong>HARDWARE:</strong> 100% Screwless Interlocking Teak Dowels
                  </div>
                  <div class="cad-corner-marks">SCALE 1:20<br>REV: 02-B</div>
                </div>
              </div>

              <!-- Panel 03: Architectural Modular Teak Kitchen -->
              <div class="home-hero-img-col" id="heroCol2">
                <div class="home-hero-col-badge">
                  <span class="home-hero-col-num">[03]</span>
                  <span class="home-hero-col-name">MODULAR TEAK KITCHEN</span>
                </div>
                <button class="hero-rewipe-btn" onclick="rewipeHeroCol(2, event)">↺ RE-WIPE</button>
                <div class="pixel-wipe-wrap">
                  <div class="pixel-wipe-base">
                    <img class="img-basic img-abs" src="/images/kitchen-sketch.webp" alt="Turnkey Modular Teak Kitchen Architectural Sketch" />
                  </div>
                  <div class="pixel-wipe-reveal">
                    <img class="img-basic img-abs pixel-reveal-img" src="/images/kitchen-real.jpg" alt="Turnkey Modular Teak Kitchen Real Photograph" />
                  </div>
                </div>
                <div class="hero-cad-hud">
                  <div class="cad-specs">
                    <strong>MODULAR RUN:</strong> 3600 × 2400 × 650mm<br>
                    <strong>CARCASS:</strong> Marine-Grade Nilambur Core • Blum Motion
                  </div>
                  <div class="cad-corner-marks">SCALE 1:20<br>REV: 06-C</div>
                </div>
              </div>
            </div>
            '''"""

assert old_triptych in content, "old_triptych not found"
content = content.replace(old_triptych, new_triptych, 1)

# ==============================================================================
# 3. UPDATE INTRO COURTYARD HTML WITH CALIPER TOGGLE & SLIDER
# ==============================================================================
old_intro = """intro_html = '''
            <div class="pixel-wipe-wrap">
              <div class="pixel-wipe-base">
                <img class="img-basic img-abs" src="/images/courtyard-sketch.webp" alt="Kerala Courtyard Teak Wood Architecture - Architectural Pencil Sketch" />
              </div>
              <div class="pixel-wipe-reveal">
                <img class="img-basic img-abs pixel-reveal-img" src="/images/courtyard-real.jpg" alt="Kerala Courtyard Teak Wood Architecture - Real Photograph" />
              </div>
            </div>
            '''"""

new_intro = """intro_html = '''
            <div class="pixel-wipe-wrap" id="introPixelWrap">
              <div class="pixel-wipe-base">
                <img class="img-basic img-abs" src="/images/courtyard-sketch.webp" alt="Kerala Courtyard Teak Wood Architecture - Architectural Pencil Sketch" />
              </div>
              <div class="pixel-wipe-reveal" id="introRevealWrap">
                <img class="img-basic img-abs pixel-reveal-img" src="/images/courtyard-real.jpg" alt="Kerala Courtyard Teak Wood Architecture - Real Photograph" />
              </div>
            </div>
            <button class="intro-caliper-toggle-btn" id="introCaliperBtn" onclick="toggleCaliperMode(event)">
              <span>↔ ARCHITECTURAL CALIPER</span>
            </button>
            <div class="intro-caliper-handle" id="introCaliperHandle" style="display: none;">
              <div class="caliper-line"></div>
              <div class="caliper-grip">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M8 7L3 12L8 17M16 7L21 12L16 17" stroke="#1c1815" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
            </div>
            '''"""

assert old_intro in content, "old_intro not found"
content = content.replace(old_intro, new_intro, 1)

# ==============================================================================
# 4. INSERT CHRONOS PATINA SECTION IN build()
# ==============================================================================
# Find where intro_wrap is finished and before platform_wrap
patina_injection_code = """
    # 6b. Insert Chronos 100-Year Timber Patina Interactive Engine
    intro_component = soup.find('home-intro-wrap')
    if intro_component:
        patina_section_html = '''
        <div class="home-patina-wrap web-component">
          <section class="home-patina-section">
            <div class="patina-container">
              <div class="patina-head">
                <div>
                  <div class="patina-tag">CHRONOS • TIMBER MATURATION ENGINE</div>
                  <h2 class="patina-title">The 100-Year Nilambur Teak Patina</h2>
                  <p class="patina-subtitle">Nilambur teak deepens and self-burnishes with generational exposure. Drag the caliper dial to observe the live color transformation, surface hardness, and natural resin maturation.</p>
                </div>
                <div class="gi-seal-wrap">
                  <div class="gi-seal-coin" id="giCoin" title="Click to spin official GI coin">
                    <div class="small">KERALA GI</div>
                    <div class="big">581</div>
                    <div class="small">CANOLI 1844</div>
                  </div>
                </div>
              </div>

              <div class="patina-grid">
                <div class="patina-visual">
                  <img class="patina-img" id="patinaImg" src="/images/bed-real.jpg" alt="Nilambur Teak Furniture Specimen">
                  <div class="patina-overlay-rings"></div>
                  <div class="patina-era-badge" id="patinaEraBadge">ERA: YEAR 0 (FRESH CANOLI HEARTWOOD)</div>
                  <div class="patina-wood-grain-hud">
                    <span>ANNUAL RINGS: 3.2mm/yr</span>
                    <span>SILICA ACOUSTIC PING: 480Hz</span>
                  </div>
                </div>

                <div class="patina-controls">
                  <div class="patina-timeline-track">
                    <input type="range" class="patina-slider" id="patinaSlider" min="0" max="3" step="1" value="0" oninput="updatePatina(this.value)">
                    <div class="patina-ticks">
                      <span class="active" onclick="setPatinaEra(0)">0 YRS<br><small>FRESH</small></span>
                      <span onclick="setPatinaEra(1)">15 YRS<br><small>AMBER</small></span>
                      <span onclick="setPatinaEra(2)">50 YRS<br><small>BRONZE</small></span>
                      <span onclick="setPatinaEra(3)">100+ YRS<br><small>ANTIQUE</small></span>
                    </div>
                  </div>

                  <div class="patina-metrics-grid">
                    <div class="patina-metric-box">
                      <div class="metric-val" id="metricHardness">1,000</div>
                      <div class="metric-lbl">Janka Hardness (lbf)</div>
                    </div>
                    <div class="patina-metric-box">
                      <div class="metric-val" id="metricResin">9.8%</div>
                      <div class="metric-lbl">Natural Resin Oil</div>
                    </div>
                    <div class="patina-metric-box">
                      <div class="metric-val" id="metricImmunity">99.2%</div>
                      <div class="metric-lbl">Moisture Barrier</div>
                    </div>
                  </div>

                  <div class="patina-desc" id="patinaDesc">
                    <strong>Year 0 (Freshly Harvested Heartwood):</strong> Radiant golden-yellow timber with fragrant natural tectoquinone essential oils. Silky silica crystals give exceptional acoustic damping and natural insect immunity.
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>
        '''
        patina_soup = BeautifulSoup(patina_section_html, 'html.parser')
        intro_component.insert_after(patina_soup)
"""

target_patina_loc = "    # Platform / Atelier Section:"
assert target_patina_loc in content, "Platform section target not found"
content = content.replace(target_patina_loc, patina_injection_code + "\n    # Platform / Atelier Section:", 1)

# ==============================================================================
# 5. APPEND FLOATING WIDGETS INTO BODY
# ==============================================================================
floating_widgets_code = """
    # Append Acoustic Sound Toggle, Crosshair Cursor, and Loupe to body
    floating_widgets_html = '''
    <!-- 1. SOUND TOGGLE BUTTON -->
    <button class="sound-toggle-btn" id="soundBtn" onclick="toggleSound()">
      <div class="sound-wave-dot" id="soundDot"></div>
      <span id="soundLabel">ACOUSTIC TEAK: ON</span>
    </button>

    <!-- 2. ARCHITECTURAL DRAFTING CROSSHAIR CURSOR -->
    <div class="arch-crosshair" id="archCrosshair">
      <div class="arch-crosshair-circle">
        <div class="arch-crosshair-h"></div>
        <div class="arch-crosshair-v"></div>
      </div>
      <div class="arch-crosshair-hud" id="archHud">X: 0mm | Y: 0mm | SCALE 1:20</div>
    </div>

    <!-- 3. ARTISAN WOOD LOUPE (MAGNIFIER) -->
    <div class="teak-loupe" id="teakLoupe">
      <div class="teak-loupe-reticle">
        <svg width="140" height="140" viewBox="0 0 140 140">
          <circle cx="70" cy="70" r="35" stroke="rgba(217, 119, 6, 0.4)" stroke-dasharray="3,3" fill="none"/>
          <circle cx="70" cy="70" r="55" stroke="rgba(217, 119, 6, 0.3)" stroke-dasharray="2,4" fill="none"/>
          <line x1="70" y1="10" x2="70" y2="30" stroke="#d97706" stroke-width="1.5"/>
          <line x1="70" y1="110" x2="70" y2="130" stroke="#d97706" stroke-width="1.5"/>
          <line x1="10" y1="70" x2="30" y2="70" stroke="#d97706" stroke-width="1.5"/>
          <line x1="110" y1="70" x2="130" y2="70" stroke="#d97706" stroke-width="1.5"/>
          <circle cx="70" cy="70" r="3" fill="#fa3600"/>
        </svg>
      </div>
      <div class="teak-loupe-hud">
        <span>NILAMBUR TEAK</span> [GI-581]<br>
        SILICA DENSITY: 685 kg/m³<br>
        TECTOQUINONE: NATURAL PROOF
      </div>
    </div>
    '''
    if soup.body:
        soup.body.append(BeautifulSoup(floating_widgets_html, 'html.parser'))
"""

target_floating_loc = "    # 9. Update Title and Metadata"
assert target_floating_loc in content, "Title metadata target not found"
content = content.replace(target_floating_loc, floating_widgets_code + "\n    # 9. Update Title and Metadata", 1)

# ==============================================================================
# 6. REPLACE JS SCRIPT IN head_injections WITH COMPREHENSIVE INNOVATIONS SUITE
# ==============================================================================
func_start = content.find('function initAiswaryaPixelWipes() {')
assert func_start != -1, "initAiswaryaPixelWipes not found"

target_after_func = "document.addEventListener('DOMContentLoaded'"
func_end = content.find(target_after_func, func_start)
assert func_end != -1, "target_after_func not found"

new_js_suite = """// === 1. ACOUSTIC WOOD TAP (WEB AUDIO SYNTHESIZER) ===
      let audioCtx = null;
      let soundEnabled = true;

      function initAudio() {
        if (!audioCtx) {
          audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }
      }

      function playWoodTap(pitch = 480) {
        if (!soundEnabled) return;
        try {
          initAudio();
          if (audioCtx.state === 'suspended') {
            audioCtx.resume();
          }
          const now = audioCtx.currentTime;

          const osc1 = audioCtx.createOscillator();
          const osc2 = audioCtx.createOscillator();
          const gainNode = audioCtx.createGain();
          const filter = audioCtx.createBiquadFilter();

          osc1.type = 'sine';
          osc1.frequency.setValueAtTime(pitch, now);
          osc1.frequency.exponentialRampToValueAtTime(pitch * 0.45, now + 0.06);

          osc2.type = 'sine';
          osc2.frequency.setValueAtTime(pitch * 2.1, now);
          osc2.frequency.exponentialRampToValueAtTime(pitch * 0.7, now + 0.04);

          filter.type = 'lowpass';
          filter.frequency.setValueAtTime(1400, now);
          filter.frequency.exponentialRampToValueAtTime(400, now + 0.06);

          gainNode.gain.setValueAtTime(0.35, now);
          gainNode.gain.exponentialRampToValueAtTime(0.001, now + 0.06);

          osc1.connect(filter);
          osc2.connect(filter);
          filter.connect(gainNode);
          gainNode.connect(audioCtx.destination);

          osc1.start(now);
          osc2.start(now);
          osc1.stop(now + 0.065);
          osc2.stop(now + 0.065);
        } catch(e) {}
      }

      function toggleSound() {
        soundEnabled = !soundEnabled;
        const dot = document.getElementById('soundDot');
        const lbl = document.getElementById('soundLabel');
        if (soundEnabled) {
          if (dot) dot.classList.remove('muted');
          if (lbl) lbl.textContent = 'ACOUSTIC TEAK: ON';
          playWoodTap(540);
        } else {
          if (dot) dot.classList.add('muted');
          if (lbl) lbl.textContent = 'ACOUSTIC TEAK: OFF';
        }
      }

      // === 2. HERO RE-WIPE INTERACTIVE HANDLER ===
      function rewipeHeroCol(colIdx, e) {
        if (e) e.stopPropagation();
        playWoodTap(620);
        const col = document.getElementById(`heroCol${colIdx}`);
        if (!col) return;
        const revealImg = col.querySelector('.pixel-reveal-img');
        if (revealImg) {
          gsap.fromTo(revealImg,
            { maskPosition: '0% 0%', webkitMaskPosition: '0% 0%' },
            { maskPosition: '0% 100%', webkitMaskPosition: '0% 100%', duration: 1.15, ease: 'steps(29)', overwrite: 'auto' }
          );
        }
      }

      // === 3. CHRONOS PATINA TIMELINE ENGINE ===
      const patinaEras = [
        {
          name: "ERA: YEAR 0 (FRESH CANOLI HEARTWOOD)",
          filter: "none",
          hardness: "1,000",
          resin: "9.8%",
          immunity: "99.2%",
          desc: "<strong>Year 0 (Freshly Harvested Heartwood):</strong> Radiant golden-yellow timber with fragrant natural tectoquinone essential oils. Silky silica crystals give exceptional acoustic damping and natural insect immunity."
        },
        {
          name: "ERA: YEAR 15 (SEASONED ESTATE TEAK)",
          filter: "sepia(0.2) saturate(1.25) contrast(1.05)",
          hardness: "1,060",
          resin: "12.2%",
          immunity: "99.6%",
          desc: "<strong>Year 15 (Matured Estate Patina):</strong> Amber warmth deepens through ambient exposure. The wood self-burnishes as microscopic resins seal the grain against seasonal monsoon humidity."
        },
        {
          name: "ERA: YEAR 50 (HERITAGE ROYAL BRONZE)",
          filter: "sepia(0.4) saturate(1.4) contrast(1.15) brightness(0.92)",
          hardness: "1,120",
          resin: "14.5%",
          immunity: "99.9%",
          desc: "<strong>Year 50 (Generational Heritage Bronze):</strong> Rich lustrous chestnut bronze with dark chocolate growth rings. Impervious to water, weathering, and insect penetration without any chemical polish."
        },
        {
          name: "ERA: YEAR 100+ (PALATIAL MALABAR ANTIQUE)",
          filter: "sepia(0.55) saturate(1.5) contrast(1.25) brightness(0.85)",
          hardness: "1,180",
          resin: "16.8%",
          immunity: "100%",
          desc: "<strong>Year 100+ (Immortal Palatial Teak):</strong> Museum-grade antique patina with an iridescent bronze sheen. As seen in 19th-century Travancore and Malabar palaces, structural hardness exceeds steel-reinforced softwood."
        }
      ];

      function setPatinaEra(val) {
        const slider = document.getElementById('patinaSlider');
        if (slider) slider.value = val;
        updatePatina(val);
      }

      function updatePatina(val) {
        val = parseInt(val);
        playWoodTap(400 + val * 70);
        const era = patinaEras[val];
        if (!era) return;

        document.querySelectorAll('.patina-ticks span').forEach((span, i) => {
          span.classList.toggle('active', i === val);
        });

        const img = document.getElementById('patinaImg');
        const badge = document.getElementById('patinaEraBadge');
        const desc = document.getElementById('patinaDesc');
        const hardness = document.getElementById('metricHardness');
        const resin = document.getElementById('metricResin');
        const immunity = document.getElementById('metricImmunity');

        if (img) img.style.filter = era.filter;
        if (badge) badge.textContent = era.name;
        if (desc) desc.innerHTML = era.desc;
        if (hardness) hardness.textContent = era.hardness;
        if (resin) resin.textContent = era.resin;
        if (immunity) immunity.textContent = era.immunity;
      }

      // === 4. INTRO ARCHITECTURAL CALIPER SPLIT SLIDER ===
      let caliperActive = false;

      function toggleCaliperMode(e) {
        if (e) e.stopPropagation();
        caliperActive = !caliperActive;
        playWoodTap(580);

        const btn = document.getElementById('introCaliperBtn');
        const handle = document.getElementById('introCaliperHandle');
        const revealWrap = document.getElementById('introRevealWrap');
        const pixelImg = revealWrap ? revealWrap.querySelector('.pixel-reveal-img') : null;

        if (btn) btn.classList.toggle('active', caliperActive);
        if (handle) handle.style.display = caliperActive ? 'block' : 'none';

        if (caliperActive) {
          // Switch reveal to horizontal split clipping
          if (pixelImg) {
            pixelImg.style.maskImage = 'none';
            pixelImg.style.webkitMaskImage = 'none';
          }
          setCaliperPosition(50);
        } else {
          // Restore pixel wipe down mask
          if (revealWrap) revealWrap.style.clipPath = 'none';
          if (pixelImg) {
            pixelImg.style.maskImage = 'url("/images/pixel-wipe-down.svg")';
            pixelImg.style.webkitMaskImage = 'url("/images/pixel-wipe-down.svg")';
            pixelImg.style.maskPosition = '0% 100%';
            pixelImg.style.webkitMaskPosition = '0% 100%';
          }
        }
      }

      function setCaliperPosition(pct) {
        pct = Math.max(0, Math.min(100, pct));
        const handle = document.getElementById('introCaliperHandle');
        const revealWrap = document.getElementById('introRevealWrap');
        if (handle) handle.style.left = pct + '%';
        if (revealWrap) revealWrap.style.clipPath = `inset(0 0 0 ${pct}%)`;
      }

      // === 5. MAIN ANIMATION PIPELINE INITIALIZER ===
      function initAiswaryaPixelWipes() {
        if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') {
          setTimeout(initAiswaryaPixelWipes, 100);
          return;
        }
        gsap.registerPlugin(ScrollTrigger);

        const scrollerEl = document.querySelector('.main-inner') ? '.main-inner' : window;

        // --- 0. HERO SECTION: AUTOMATIC PIXEL CASCADE DOWN ON OPEN (NO SCROLL REQUIRED) ---
        const heroCols = document.querySelectorAll('.home-hero-img-col');
        const heroReveals = document.querySelectorAll('.home-hero-img-col .pixel-reveal-img');
        if (heroReveals.length > 0) {
          heroReveals.forEach((img, idx) => {
            gsap.set(img, {
              maskPosition: '0% 0%',
              webkitMaskPosition: '0% 0%'
            });
            gsap.to(img, {
              maskPosition: '0% 100%',
              webkitMaskPosition: '0% 100%',
              duration: 1.25,
              delay: 0.35 + idx * 0.22,
              ease: 'steps(29)',
              overwrite: 'auto',
              onStart: () => {
                if (idx === 0) playWoodTap(440);
                if (idx === 1) setTimeout(() => playWoodTap(520), 220);
                if (idx === 2) setTimeout(() => playWoodTap(600), 440);
              }
            });
          });
        }

        // --- HERO ACCORDION & CURSOR INTERACTION ---
        const crosshair = document.getElementById('archCrosshair');
        const archHud = document.getElementById('archHud');
        const loupe = document.getElementById('teakLoupe');

        heroCols.forEach((col, idx) => {
          const realImg = col.querySelector('.pixel-reveal-img');

          col.addEventListener('mouseenter', () => {
            playWoodTap(460 + idx * 50);
            if (crosshair) crosshair.style.display = 'block';
            if (loupe && realImg) {
              loupe.style.display = 'block';
              loupe.style.backgroundImage = `url('${realImg.src}')`;
            }
          });

          col.addEventListener('mouseleave', () => {
            if (crosshair) crosshair.style.display = 'none';
            if (loupe) loupe.style.display = 'none';
          });

          col.addEventListener('mousemove', (e) => {
            const rect = col.getBoundingClientRect();
            const relX = Math.round(e.clientX - rect.left);
            const relY = Math.round(e.clientY - rect.top);

            if (crosshair && archHud) {
              crosshair.style.left = e.clientX + 'px';
              crosshair.style.top = e.clientY + 'px';
              archHud.textContent = `X: ${relX * 5}mm | Y: ${relY * 5}mm | SCALE 1:20`;
            }

            if (loupe) {
              loupe.style.left = (e.clientX + 32) + 'px';
              loupe.style.top = (e.clientY - 32) + 'px';
              const pctX = (relX / rect.width) * 100;
              const pctY = (relY / rect.height) * 100;
              loupe.style.backgroundPosition = `${pctX}% ${pctY}%`;
            }
          });
        });

        // --- 1. EXPLORE WOODCRAFT (INTRO) SCROLLTRIGGER WIPE ---
        const introReveal = document.querySelector('.home-intro-wrap .pixel-reveal-img');
        if (introReveal) {
          gsap.fromTo(introReveal,
            { maskPosition: '0% 0%', webkitMaskPosition: '0% 0%' },
            {
              maskPosition: '0% 100%',
              webkitMaskPosition: '0% 100%',
              ease: 'steps(29)',
              scrollTrigger: {
                scroller: scrollerEl,
                trigger: '.home-intro-wrap',
                start: 'top 75%',
                end: 'bottom 25%',
                scrub: 0.6
              }
            }
          );
        }

        // --- CALIPER POINTER DRAG LISTENER ---
        const caliperHandle = document.getElementById('introCaliperHandle');
        const introImgWrap = document.querySelector('.home-intro-img-wrap');
        if (caliperHandle && introImgWrap) {
          let isDraggingCaliper = false;
          caliperHandle.addEventListener('pointerdown', (e) => {
            isDraggingCaliper = true;
            caliperHandle.setPointerCapture(e.pointerId);
            playWoodTap(520);
          });
          caliperHandle.addEventListener('pointermove', (e) => {
            if (!isDraggingCaliper) return;
            const rect = introImgWrap.getBoundingClientRect();
            const pct = ((e.clientX - rect.left) / rect.width) * 100;
            setCaliperPosition(pct);
          });
          caliperHandle.addEventListener('pointerup', () => {
            isDraggingCaliper = false;
          });
          caliperHandle.addEventListener('pointercancel', () => {
            isDraggingCaliper = false;
          });
        }

        // --- 2. PLATFORM / ATELIER SECTION (ITEMS 0 AND 1) ---
        const platformReveals = document.querySelectorAll('.home-platform-img-item-inner .pixel-reveal-img');
        platformReveals.forEach((img) => {
          const trigger = img.closest('.home-platform-img-item') || img;
          gsap.fromTo(img,
            { maskPosition: '0% 0%', webkitMaskPosition: '0% 0%' },
            {
              maskPosition: '0% 100%',
              webkitMaskPosition: '0% 100%',
              ease: 'steps(29)',
              scrollTrigger: {
                scroller: scrollerEl,
                trigger: trigger,
                start: 'top 75%',
                end: 'bottom 25%',
                scrub: 0.6
              }
            }
          );
        });

        // --- 3. WHY AISWARYA SECTION: 4 CRAFTSMANSHIP STEPS ---
        const whyReveals = document.querySelectorAll('.home-why-item .pixel-reveal-img');
        whyReveals.forEach((img) => {
          const trigger = img.closest('.home-why-item') || img;
          gsap.fromTo(img,
            { maskPosition: '0% 0%', webkitMaskPosition: '0% 0%' },
            {
              maskPosition: '0% 100%',
              webkitMaskPosition: '0% 100%',
              ease: 'steps(29)',
              scrollTrigger: {
                scroller: scrollerEl,
                trigger: trigger,
                start: 'top 80%',
                end: 'center 30%',
                scrub: 0.6
              }
            }
          );
        });

        // --- 4. CTA SECTION (GRAND LIVING HALL) ---
        const ctaReveal = document.querySelector('.cta-wrap .pixel-reveal-img');
        if (ctaReveal) {
          gsap.fromTo(ctaReveal,
            { maskPosition: '0% 0%', webkitMaskPosition: '0% 0%' },
            {
              maskPosition: '0% 100%',
              webkitMaskPosition: '0% 100%',
              ease: 'steps(29)',
              scrollTrigger: {
                scroller: scrollerEl,
                trigger: '.cta-wrap',
                start: 'top 80%',
                end: 'bottom 30%',
                scrub: 0.6
              }
            }
          );
        }

        // --- 5. 3D GYRO COIN INTERACTION ---
        const coin = document.getElementById('giCoin');
        if (coin) {
          coin.addEventListener('mousemove', (e) => {
            const rect = coin.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;
            coin.style.transform = `rotateX(${-y * 0.4}deg) rotateY(${x * 0.4}deg) scale(1.08)`;
          });
          coin.addEventListener('mouseleave', () => {
            coin.style.transform = 'rotateX(0deg) rotateY(0deg) scale(1)';
          });
          coin.addEventListener('click', () => {
            playWoodTap(740);
            gsap.to(coin, { rotationY: "+=360", duration: 0.85, ease: "back.out(1.5)" });
          });
        }

        // --- 6. ATTACH WOOD TAP SOUND TO ALL BUTTONS ---
        document.querySelectorAll('.btn-basic, .btn-fill, .header-menu-btn, .footer-menu-link').forEach((el) => {
          el.addEventListener('click', () => playWoodTap(560));
        });

        setTimeout(() => {
          if (window.ScrollTrigger) ScrollTrigger.refresh();
        }, 400);
      }

      """

content = content[:func_start] + new_js_suite + content[func_end:]

with open('/home/mullainathan/projects/nilambur-teak-wood/clean_aiswarya_builder.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully updated clean_aiswarya_builder.py with the full innovations suite!")
