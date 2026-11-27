import re

with open('/home/mullainathan/projects/nilambur-teak-wood/clean_aiswarya_builder.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ==============================================================================
# 1. UPDATE CSS FOR CHRONOS SECTION (SANDSTONE ARCHITECTURAL THEME & ADVANCED ANIMATIONS)
# ==============================================================================
css_start = content.find('/* === CHRONOS 100-YEAR PATINA SECTION === */')
assert css_start != -1, "Chronos CSS start not found"

# Find end of Chronos CSS block (before </style>)
css_end = content.find('</style>', css_start)
assert css_end != -1, "Chronos CSS end not found"

new_chronos_css = """/* === CHRONOS 100-YEAR PATINA SECTION (ARCHITECTURAL SANDSTONE & ADVANCED ANIMATIONS) === */
      .home-patina-wrap {
        width: 100% !important;
        position: relative !important;
        background: transparent !important;
        padding: 4.5rem 0 !important;
        border-top: var(--size--border) solid var(--content--border) !important;
        border-bottom: var(--size--border) solid var(--content--border) !important;
      }
      .patina-container {
        max-width: 1300px !important;
        margin: 0 auto !important;
        padding: 3rem !important;
        background: var(--content--white) !important;
        color: var(--content--primary) !important;
        border-radius: 16px !important;
        border: var(--size--border) solid var(--content--border) !important;
        box-shadow: 0 10px 40px rgba(28, 24, 21, 0.06), inset 0 1px 0 rgba(255, 255, 255, 0.6) !important;
        position: relative !important;
        overflow: hidden !important;
      }
      .patina-bg-grid {
        position: absolute !important;
        inset: 0 !important;
        background-size: 40px 40px !important;
        background-image: 
          linear-gradient(to right, rgba(200, 191, 178, 0.22) 1px, transparent 1px),
          linear-gradient(to bottom, rgba(200, 191, 178, 0.22) 1px, transparent 1px) !important;
        pointer-events: none !important;
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
        letter-spacing: 0.22em !important;
        color: var(--content--brand) !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        margin-bottom: 0.4rem !important;
      }
      .patina-title {
        font-size: 2.4rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
        color: var(--content--primary) !important;
        margin: 0 0 0.6rem 0 !important;
      }
      .patina-subtitle {
        font-size: 1rem !important;
        line-height: 1.55 !important;
        color: var(--content--secondary) !important;
        max-width: 660px !important;
        margin: 0 !important;
      }
      .gi-seal-wrap {
        perspective: 800px !important;
        display: inline-block !important;
      }
      .gi-seal-coin {
        width: 105px !important;
        height: 105px !important;
        border-radius: 50% !important;
        background: radial-gradient(circle at 35% 35%, #f59e0b, #b45309 60%, #78350f 100%) !important;
        box-shadow: 0 8px 25px rgba(217, 119, 6, 0.35), inset 0 2px 4px rgba(255,255,255,0.4), inset 0 -3px 6px rgba(0,0,0,0.5) !important;
        border: 2px solid rgba(253, 251, 247, 0.3) !important;
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
      .gi-seal-coin .small { font-size: 8px !important; letter-spacing: 0.15em !important; opacity: 0.9 !important; }
      .gi-seal-coin .big { font-size: 17px !important; font-weight: bold !important; color: #fef08a !important; margin: 1px 0 !important; }
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

      /* 3D Visual Card with Glare, Particles & Scanline */
      .patina-visual-wrap {
        perspective: 1000px !important;
      }
      .patina-visual {
        position: relative !important;
        height: 420px !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid var(--content--border) !important;
        background: #1c1815 !important;
        box-shadow: 0 16px 40px rgba(28, 24, 21, 0.18) !important;
        transform-style: preserve-3d !important;
        transition: transform 0.15s ease-out !important;
      }
      .patina-img {
        width: 100% !important;
        height: 100% !important;
        object-fit: cover !important;
        display: block !important;
        transition: filter 0.35s ease !important;
      }
      .patina-glare {
        position: absolute !important;
        inset: 0 !important;
        background: radial-gradient(circle at 50% 50%, rgba(255,255,255,0.25), transparent 60%) !important;
        opacity: 0 !important;
        pointer-events: none !important;
        mix-blend-mode: overlay !important;
        transition: opacity 0.3s ease !important;
        z-index: 3 !important;
      }
      .patina-particles-canvas {
        position: absolute !important;
        inset: 0 !important;
        pointer-events: none !important;
        z-index: 4 !important;
      }
      .patina-scanline {
        position: absolute !important;
        left: 0 !important;
        right: 0 !important;
        height: 3px !important;
        background: linear-gradient(90deg, transparent, #fa3600, #f59e0b, transparent) !important;
        box-shadow: 0 0 15px #fa3600 !important;
        opacity: 0 !important;
        z-index: 5 !important;
        pointer-events: none !important;
      }
      .patina-era-badge {
        position: absolute !important;
        top: 1rem !important;
        left: 1rem !important;
        background: rgba(28, 24, 21, 0.88) !important;
        backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(217, 119, 6, 0.45) !important;
        border-radius: 4px !important;
        padding: 0.45rem 0.85rem !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.1em !important;
        color: #f59e0b !important;
        z-index: 6 !important;
      }
      .patina-wood-grain-hud {
        position: absolute !important;
        bottom: 1rem !important;
        left: 1rem !important;
        right: 1rem !important;
        background: rgba(28, 24, 21, 0.9) !important;
        backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(200, 191, 178, 0.3) !important;
        border-radius: 6px !important;
        padding: 0.5rem 0.85rem !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 0.75rem !important;
        color: #efece6 !important;
        display: flex !important;
        justify-content: space-between !important;
        z-index: 6 !important;
      }
      .patina-wood-grain-hud span strong {
        color: var(--content--brand) !important;
      }

      /* Interactive Hotspots */
      .anatomy-hotspot {
        position: absolute !important;
        z-index: 7 !important;
        cursor: pointer !important;
        transform: translate(-50%, -50%) !important;
      }
      .hotspot-ring {
        width: 22px !important;
        height: 22px !important;
        border-radius: 50% !important;
        border: 2px solid var(--content--brand) !important;
        background: rgba(250, 54, 0, 0.25) !important;
        box-shadow: 0 0 12px var(--content--brand) !important;
        animation: pulseHotspot 2s infinite ease-in-out !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
      }
      .hotspot-dot {
        width: 6px !important;
        height: 6px !important;
        border-radius: 50% !important;
        background: #fff !important;
      }
      .hotspot-tooltip {
        position: absolute !important;
        bottom: 28px !important;
        left: 50% !important;
        transform: translateX(-50%) translateY(6px) !important;
        background: rgba(28, 24, 21, 0.94) !important;
        color: #efece6 !important;
        border: 1px solid var(--content--brand) !important;
        border-radius: 6px !important;
        padding: 6px 10px !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 10px !important;
        white-space: nowrap !important;
        opacity: 0 !important;
        pointer-events: none !important;
        transition: all 0.25s cubic-bezier(0.25, 1, 0.5, 1) !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3) !important;
      }
      .anatomy-hotspot:hover .hotspot-tooltip {
        opacity: 1 !important;
        transform: translateX(-50%) translateY(0) !important;
      }
      @keyframes pulseHotspot {
        0% { transform: scale(0.9); opacity: 0.8; }
        50% { transform: scale(1.25); opacity: 1; }
        100% { transform: scale(0.9); opacity: 0.8; }
      }

      /* Controls (Sandstone Theme) */
      .patina-controls {
        display: flex !important;
        flex-direction: column !important;
        gap: 1.5rem !important;
      }
      .patina-timeline-track {
        background: var(--bg--sandstone) !important;
        border: 1px solid var(--content--border) !important;
        border-radius: 12px !important;
        padding: 1.25rem 1.5rem 1rem !important;
      }
      .patina-timeline-head {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        margin-bottom: 0.8rem !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 0.82rem !important;
      }
      .timeline-title {
        color: var(--content--secondary) !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        font-weight: 700 !important;
      }
      .timeline-year-readout {
        color: var(--content--brand) !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
      }
      .patina-slider {
        -webkit-appearance: none !important;
        appearance: none !important;
        width: 100% !important;
        height: 8px !important;
        border-radius: 4px !important;
        background: #cfc7bc !important;
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
        border: 3px solid #fff !important;
        box-shadow: 0 2px 10px rgba(250, 54, 0, 0.5) !important;
        cursor: ew-resize !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
      }
      .patina-slider::-webkit-slider-thumb:hover {
        transform: scale(1.2) !important;
        box-shadow: 0 0 16px var(--content--brand) !important;
      }
      .patina-ticks {
        display: flex !important;
        justify-content: space-between !important;
        margin-top: 0.75rem !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 0.78rem !important;
        letter-spacing: 0.05em !important;
        color: var(--content--secondary) !important;
      }
      .patina-ticks span {
        cursor: pointer !important;
        padding: 4px 6px !important;
        border-radius: 4px !important;
        transition: all 0.2s ease !important;
        text-align: center !important;
      }
      .patina-ticks span:hover {
        background: rgba(250, 54, 0, 0.08) !important;
        color: var(--content--brand) !important;
      }
      .patina-ticks span.active {
        background: var(--content--brand) !important;
        color: #fff !important;
        font-weight: 700 !important;
      }
      .patina-metrics-grid {
        display: grid !important;
        grid-template-columns: repeat(3, 1fr) !important;
        gap: 1rem !important;
      }
      .patina-metric-box {
        background: var(--bg--sandstone) !important;
        border: 1px solid var(--content--border) !important;
        border-radius: 10px !important;
        padding: 1.1rem 0.8rem !important;
        text-align: center !important;
        transition: transform 0.2s ease, border-color 0.2s ease !important;
      }
      .patina-metric-box:hover {
        transform: translateY(-2px) !important;
        border-color: var(--content--brand) !important;
      }
      .metric-val {
        font-size: 1.9rem !important;
        font-weight: 700 !important;
        color: var(--content--brand) !important;
        font-family: 'Geistmono', monospace !important;
        margin-bottom: 0.2rem !important;
      }
      .metric-lbl {
        font-family: 'Geistmono', monospace !important;
        font-size: 0.72rem !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        color: var(--content--secondary) !important;
      }
      .patina-desc {
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
        color: var(--content--primary) !important;
        padding: 1.1rem 1.3rem !important;
        background: var(--bg--sandstone) !important;
        border-left: 3px solid var(--content--brand) !important;
        border-top: 1px solid var(--content--border) !important;
        border-right: 1px solid var(--content--border) !important;
        border-bottom: 1px solid var(--content--border) !important;
        border-radius: 0 8px 8px 0 !important;
      }
      .patina-desc strong {
        color: var(--content--brand) !important;
      }
"""

content = content[:css_start] + new_chronos_css + content[css_end:]

# ==============================================================================
# 2. UPDATE CHRONOS HTML IN build()
# ==============================================================================
html_start = content.find("patina_section_html = '''")
assert html_start != -1, "patina_section_html not found"
html_end = content.find("'''\n        patina_soup = BeautifulSoup(patina_section_html, 'html.parser')", html_start)
assert html_end != -1, "patina_section_html end not found"

new_chronos_html = """patina_section_html = '''
        <div class="home-patina-wrap web-component">
          <section class="patina-container">
            <div class="patina-bg-grid"></div>

            <div class="patina-head">
              <div>
                <div class="patina-tag">CHRONOS • TIMBER MATURATION ENGINE</div>
                <h2 class="patina-title">The 100-Year Nilambur Teak Patina</h2>
                <p class="patina-subtitle">
                  Unlike softwoods that rot, authentic Nilambur teak oxidises with air and sunlight, self-lubricating with natural tectoquinone oils to deepen from radiant golden honey to immortal royal bronze.
                </p>
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
              <!-- 3D Specimen Card -->
              <div class="patina-visual-wrap" id="visualWrap">
                <div class="patina-visual" id="patinaVisual">
                  <img class="patina-img" id="patinaImg" src="/images/bed-real.jpg" alt="Nilambur Teak Furniture Specimen">
                  <div class="patina-glare" id="patinaGlare"></div>
                  <canvas class="patina-particles-canvas" id="particlesCanvas"></canvas>
                  <div class="patina-scanline" id="patinaScanline"></div>
                  <div class="patina-era-badge" id="patinaEraBadge">ERA: YEAR 0 (FRESH CANOLI HEARTWOOD)</div>

                  <!-- Interactive Hotspots -->
                  <div class="anatomy-hotspot" style="top: 35%; left: 30%;" onclick="showHotspotInfo('heartwood')">
                    <div class="hotspot-ring"><div class="hotspot-dot"></div></div>
                    <div class="hotspot-tooltip">SILICA HEARTWOOD: 0.72% ACOUSTIC PING</div>
                  </div>
                  <div class="anatomy-hotspot" style="top: 55%; left: 72%;" onclick="showHotspotInfo('resin')">
                    <div class="hotspot-ring"><div class="hotspot-dot"></div></div>
                    <div class="hotspot-tooltip">TECTOQUINONE POCKET: ANTI-TERMITE RESIN</div>
                  </div>
                  <div class="anatomy-hotspot" style="top: 75%; left: 45%;" onclick="showHotspotInfo('joint')">
                    <div class="hotspot-ring"><div class="hotspot-dot"></div></div>
                    <div class="hotspot-tooltip">MORTISE & TENON: 14.2 kN TENSILE LOAD</div>
                  </div>

                  <div class="patina-wood-grain-hud">
                    <span>ANNUAL RINGS: <strong id="hudRings">3.2mm/yr</strong></span>
                    <span>DENSITY: <strong id="hudDensity">650 kg/m³</strong></span>
                    <span>ACOUSTIC PING: <strong id="hudPing">580 Hz</strong></span>
                  </div>
                </div>
              </div>

              <!-- Controls -->
              <div class="patina-controls">
                <div class="patina-timeline-track">
                  <div class="patina-timeline-head">
                    <span class="timeline-title">TIMBER AGE &amp; MATURATION SCRUB</span>
                    <span class="timeline-year-readout" id="yearReadout">YEAR 0 (FRESH CANOLI HEARTWOOD)</span>
                  </div>
                  <input type="range" class="patina-slider" id="patinaSlider" min="0" max="100" step="1" value="0" oninput="onContinuousScrub(this.value)">
                  <div class="patina-ticks">
                    <span class="active" onclick="snapToYear(0)">YEAR 0<br><small>FRESH</small></span>
                    <span onclick="snapToYear(15)">YEAR 15<br><small>AMBER</small></span>
                    <span onclick="snapToYear(50)">YEAR 50<br><small>BRONZE</small></span>
                    <span onclick="snapToYear(100)">YEAR 100+<br><small>ANTIQUE</small></span>
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
          </section>
        </div>"""

content = content[:html_start] + new_chronos_html + content[html_end:]

# ==============================================================================
# 3. UPDATE CHRONOS JS IN head_injections
# ==============================================================================
js_start = content.find('// === 3. CHRONOS PATINA TIMELINE ENGINE ===')
assert js_start != -1, "Chronos JS start not found"
js_end = content.find('// === 4. INTRO ARCHITECTURAL CALIPER SPLIT SLIDER ===', js_start)
assert js_end != -1, "Chronos JS end not found"

new_chronos_js = """// === 3. CHRONOS PATINA TIMELINE ENGINE (ADVANCED ENGINE) ===
      let lastPlayedYear = 0;
      let isUserDraggingSlider = false;

      function triggerScanline() {
        const scan = document.getElementById('patinaScanline');
        if (scan && typeof gsap !== 'undefined') {
          gsap.fromTo(scan, 
            { top: '0%', opacity: 0.9 }, 
            { top: '100%', opacity: 0, duration: 0.65, ease: 'power2.out' }
          );
        }
      }

      function snapToYear(year) {
        const slider = document.getElementById('patinaSlider');
        if (slider) slider.value = year;
        onContinuousScrub(year, true);
      }

      function onContinuousScrub(year, isSnap = false) {
        year = parseFloat(year);
        const ratio = Math.max(0, Math.min(1, year / 100));

        // Pitch modulated acoustic wood tap
        if (Math.abs(year - lastPlayedYear) >= 10 || isSnap) {
          const pitch = 580 - (ratio * 240); // 580Hz down to 340Hz as timber hardens!
          playWoodTap(pitch);
          lastPlayedYear = year;
          triggerScanline();
        }

        // Update Year Readout
        const yrLabel = document.getElementById('yearReadout');
        if (yrLabel) {
          if (year === 0) yrLabel.textContent = "YEAR 0 (FRESH CANOLI HEARTWOOD)";
          else if (year < 25) yrLabel.textContent = `YEAR ${Math.round(year)} (HONEY AMBER)`;
          else if (year < 60) yrLabel.textContent = `YEAR ${Math.round(year)} (HERITAGE ROYAL BRONZE)`;
          else yrLabel.textContent = `YEAR ${Math.round(year)}+ (PALATIAL MALABAR ANTIQUE)`;
        }

        // Update Ticks highlight
        document.querySelectorAll('.patina-ticks span').forEach((span, idx) => {
          const tickYears = [0, 15, 50, 100];
          const isActive = Math.abs(year - tickYears[idx]) < 12;
          span.classList.toggle('active', isActive);
        });

        // Continuous Color Grading Interpolation
        const sepia = (ratio * 0.58).toFixed(2);
        const saturate = (1.0 + ratio * 0.55).toFixed(2);
        const contrast = (1.0 + ratio * 0.25).toFixed(2);
        const brightness = (1.0 - ratio * 0.16).toFixed(2);

        const img = document.getElementById('patinaImg');
        if (img) {
          img.style.filter = `sepia(${sepia}) saturate(${saturate}) contrast(${contrast}) brightness(${brightness})`;
        }

        // Particle intensity scaling
        if (window.setPatinaParticleIntensity) {
          window.setPatinaParticleIntensity(0.2 + ratio * 0.8);
        }

        // Odometer Metrics
        const hardness = Math.round(1000 + ratio * 180);
        const resin = (9.8 + ratio * 7.0).toFixed(1);
        const immunity = (99.2 + ratio * 0.8).toFixed(1);
        const density = Math.round(650 + ratio * 110);
        const ping = Math.round(580 - ratio * 240);

        const mHardness = document.getElementById('metricHardness');
        const mResin = document.getElementById('metricResin');
        const mImmunity = document.getElementById('metricImmunity');
        const mDensity = document.getElementById('hudDensity');
        const mPing = document.getElementById('hudPing');

        if (mHardness) mHardness.textContent = hardness.toLocaleString();
        if (mResin) mResin.textContent = resin + '%';
        if (mImmunity) mImmunity.textContent = immunity + '%';
        if (mDensity) mDensity.textContent = density + ' kg/m³';
        if (mPing) mPing.textContent = ping + ' Hz';

        // Era Badge & Narrative
        const badge = document.getElementById('patinaEraBadge');
        const desc = document.getElementById('patinaDesc');

        if (badge && desc) {
          if (year < 15) {
            badge.textContent = `ERA: YEAR ${Math.round(year)} (FRESH CANOLI HEARTWOOD)`;
            desc.innerHTML = "<strong>Freshly Sawn Nilambur Heartwood:</strong> Radiant golden-yellow timber with fragrant natural tectoquinone essential oils. Silky silica crystals give exceptional acoustic damping and natural insect immunity.";
          } else if (year < 50) {
            badge.textContent = `ERA: YEAR ${Math.round(year)} (SEASONED ESTATE AMBER)`;
            desc.innerHTML = "<strong>Seasoned Estate Patina:</strong> Amber warmth deepens through ambient exposure. The wood self-burnishes as microscopic resins seal the grain against seasonal monsoon humidity.";
          } else if (year < 85) {
            badge.textContent = `ERA: YEAR ${Math.round(year)} (HERITAGE ROYAL BRONZE)`;
            desc.innerHTML = "<strong>Generational Heritage Bronze:</strong> Rich lustrous chestnut bronze with dark chocolate growth rings. Impervious to water, weathering, and insect penetration without any chemical polish.";
          } else {
            badge.textContent = `ERA: YEAR ${Math.round(year)}+ (PALATIAL MALABAR ANTIQUE)`;
            desc.innerHTML = "<strong>Immortal Palatial Teak:</strong> Museum-grade antique patina with an iridescent bronze sheen. As seen in 19th-century Travancore and Malabar palaces, structural hardness exceeds steel-reinforced softwood.";
          }
        }
      }

      function showHotspotInfo(type) {
        playWoodTap(620);
        triggerScanline();
      }

      // Initialize Particles & 3D Tilt for Chronos
      function initChronosAdvanced() {
        // 1. Resin Particle Engine
        const canvas = document.getElementById('particlesCanvas');
        if (canvas) {
          const ctx = canvas.getContext('2d');
          let particles = [];
          let currentIntensity = 0.2;

          window.setPatinaParticleIntensity = (val) => { currentIntensity = val; };

          function resizeCanvas() {
            const rect = canvas.getBoundingClientRect();
            canvas.width = rect.width;
            canvas.height = rect.height;
          }
          resizeCanvas();
          window.addEventListener('resize', resizeCanvas);

          class ResinParticle {
            constructor() { this.reset(); }
            reset() {
              this.x = Math.random() * (canvas.width || 300);
              this.y = Math.random() * (canvas.height || 300);
              this.vx = (Math.random() - 0.5) * 0.4;
              this.vy = -Math.random() * 0.6 - 0.2;
              this.size = Math.random() * 2 + 1;
              this.alpha = Math.random() * 0.6 + 0.2;
              this.color = Math.random() > 0.4 ? '#f59e0b' : '#fa3600';
            }
            update() {
              this.x += this.vx;
              this.y += this.vy;
              if (this.y < 0) this.y = canvas.height;
              if (this.x < 0) this.x = canvas.width;
              if (this.x > canvas.width) this.x = 0;
            }
            draw() {
              ctx.save();
              ctx.globalAlpha = this.alpha * currentIntensity;
              ctx.fillStyle = this.color;
              ctx.shadowBlur = 6;
              ctx.shadowColor = this.color;
              ctx.beginPath();
              ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
              ctx.fill();
              ctx.restore();
            }
          }

          for (let i = 0; i < 40; i++) particles.push(new ResinParticle());

          function loop() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            particles.forEach(p => { p.update(); p.draw(); });
            requestAnimationFrame(loop);
          }
          loop();
        }

        // 2. 3D Gyro Tilt with Specular Glare
        const visualWrap = document.getElementById('visualWrap');
        const visual = document.getElementById('patinaVisual');
        const glare = document.getElementById('patinaGlare');

        if (visualWrap && visual && glare) {
          visualWrap.addEventListener('mousemove', (e) => {
            const rect = visual.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;

            const rotX = (-y / (rect.height / 2)) * 8;
            const rotY = (x / (rect.width / 2)) * 8;

            visual.style.transform = `rotateX(${rotX}deg) rotateY(${rotY}deg) scale(1.02)`;
            glare.style.opacity = '1';
            glare.style.background = `radial-gradient(circle at ${(x / rect.width + 0.5) * 100}% ${(y / rect.height + 0.5) * 100}%, rgba(255,255,255,0.28), transparent 60%)`;
          });

          visualWrap.addEventListener('mouseleave', () => {
            visual.style.transform = 'rotateX(0deg) rotateY(0deg) scale(1)';
            glare.style.opacity = '0';
          });
        }

        // 3. User drag flag on slider
        const slider = document.getElementById('patinaSlider');
        if (slider) {
          slider.addEventListener('pointerdown', () => { isUserDraggingSlider = true; });
          window.addEventListener('pointerup', () => { isUserDraggingSlider = false; });
        }
      }

      """

content = content[:js_start] + new_chronos_js + content[js_end:]

# Add ScrollTrigger for Chronos in initAiswaryaPixelWipes
st_target = "setTimeout(() => {\n          if (window.ScrollTrigger) ScrollTrigger.refresh();\n        }, 400);"
assert st_target in content, "ScrollTrigger target not found in initAiswaryaPixelWipes"

chronos_st = """// --- CHRONOS 100-YEAR MATURATION SCROLLTRIGGER SCRUB ---
        initChronosAdvanced();
        const patinaWrap = document.querySelector('.home-patina-wrap');
        if (patinaWrap && typeof ScrollTrigger !== 'undefined') {
          gsap.to({ p: 0 }, {
            p: 100,
            ease: "none",
            scrollTrigger: {
              scroller: scrollerEl,
              trigger: '.home-patina-wrap',
              start: 'top 70%',
              end: 'bottom 40%',
              scrub: 0.5,
              onUpdate: (self) => {
                if (!isUserDraggingSlider) {
                  const yr = Math.round(self.progress * 100);
                  const slider = document.getElementById('patinaSlider');
                  if (slider) slider.value = yr;
                  onContinuousScrub(yr);
                }
              }
            }
          });
        }

        setTimeout(() => {
          if (window.ScrollTrigger) ScrollTrigger.refresh();
        }, 400);"""

content = content.replace(st_target, chronos_st, 1)

with open('/home/mullainathan/projects/nilambur-teak-wood/clean_aiswarya_builder.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated clean_aiswarya_builder.py with advanced Chronos engine and sandstone background!")
