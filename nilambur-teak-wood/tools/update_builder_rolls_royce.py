import os
import re

builder_path = '/home/mullainathan/projects/nilambur-teak-wood/clean_aiswarya_builder.py'
with open(builder_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. HTML REPLACEMENT: Replace Chronos Patina section with Rolls-Royce Nilambur Teak Showcase
patina_html_target = '''    # 6b. Insert Chronos 100-Year Timber Patina Interactive Engine
    intro_component = soup.find('home-intro-wrap')
    if intro_component:
        patina_section_html = \'\'\'
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
                <div class="specimen-switcher">
                  <button class="specimen-tab active magnetic-btn" onclick="switchChronosSpecimen(0)">[01 BED PLATFORM]</button>
                  <button class="specimen-tab magnetic-btn" onclick="switchChronosSpecimen(1)">[02 LIVING SOFA]</button>
                  <button class="specimen-tab magnetic-btn" onclick="switchChronosSpecimen(2)">[03 MODULAR KITCHEN]</button>
                </div>
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
        </div>\'\'\'
        patina_soup = BeautifulSoup(patina_section_html, 'html.parser')
        intro_component.insert_after(patina_soup)'''

rr_html_replacement = '''    # 6b. Insert Rolls-Royce Nilambur Teak 3D Exploded Video Showcase (Scroll-Driven Scrub)
    intro_component = soup.find('home-intro-wrap')
    if intro_component:
        rr_section_html = \'\'\'
        <div class="home-rr-wrap web-component" id="rrRollsRoyceSection">
          <section class="rr-container">
            <div class="rr-bg-grid"></div>

            <div class="rr-head">
              <div class="rr-head-left">
                <div class="rr-tag">
                  <span class="rr-tag-dot"></span>
                  <span>ROYAL HERITAGE • AUTOMOTIVE MARQUE SPECIFICATION</span>
                </div>
                <h2 class="rr-title">The Wood of Rolls-Royce</h2>
                <p class="rr-subtitle">
                  Authentic <strong>Nilambur Teak</strong> from Malabar is hand-selected across the globe to craft the bespoke, bookmatched wooden interiors, dashboards, and picnic tables inside <strong>Rolls-Royce</strong> motorcars.
                </p>
              </div>
              <div class="rr-head-right">
                <div class="rr-seal-card">
                  <div class="rr-seal-crown">👑</div>
                  <div class="rr-seal-val">NILAMBUR TEAK</div>
                  <div class="rr-seal-sub">ROLLS-ROYCE CABIN VENEERS</div>
                  <div class="rr-seal-meta">KERALA GI 581 • CANOLI 1844</div>
                </div>
              </div>
            </div>

            <!-- Video Player Stage with HUD & Narrative Overlays -->
            <div class="rr-stage-wrap" id="rrStageWrap">
              <div class="rr-video-viewport" id="rrViewport">
                <video id="rrVideoEl"
                       class="rr-video-el"
                       src="/videos/rolls_royce_nilambur_exploded.mp4"
                       preload="auto"
                       muted
                       playsinline
                       webkit-playsinline></video>

                <!-- Gradient Vignettes for Readability -->
                <div class="rr-video-vignette-top"></div>
                <div class="rr-video-vignette-bottom"></div>
                <div class="rr-video-vignette-side"></div>

                <!-- Corner CAD Drafting Brackets -->
                <div class="rr-corner-bracket tl"></div>
                <div class="rr-corner-bracket tr"></div>
                <div class="rr-corner-bracket bl"></div>
                <div class="rr-corner-bracket br"></div>

                <!-- Top Telemetry HUD -->
                <div class="rr-hud-bar">
                  <div class="rr-hud-chip">
                    <span class="rr-pulse-dot"></span>
                    <span>ROLLS-ROYCE 3D EXPLODED CAD // NILAMBUR VENEER</span>
                  </div>
                  <div class="rr-hud-center">
                    <span id="rrPhaseBadge" class="rr-phase-badge">PHASE 01: CHASSIS &amp; SUSPENSION MATRIX</span>
                  </div>
                  <div class="rr-hud-chip right">
                    <span id="rrTimecode" class="rr-mono-num">00:00.00 / 00:10.00</span>
                  </div>
                </div>

                <!-- Floating Glassmorphic Narrative Card Overlay -->
                <div class="rr-narrative-overlay" id="rrNarrativeOverlay">
                  <div class="rr-glass-card">
                    <div class="rr-glass-pill">
                      <span class="rr-pill-dot"></span>
                      <span>BESPOKE COACHBUILDING HERITAGE</span>
                    </div>
                    <h3 class="rr-glass-heading">Bookmatched Teak Cabin Fascia</h3>
                    <p class="rr-glass-text">
                      Celebrated for centuries as the world’s most dimensionally stable hardwood, <strong>Nilambur Teak</strong> is sought by Goodwood coachbuilders for its rich natural tectoquinone resin and silica heartwood. Hand-sawn and bookmatched to mirror-symmetry, it forms the iconic dashboards, cascading center consoles, and rear executive picnic tables of bespoke Rolls-Royce motorcars—guaranteed never to warp, crack, or split in any climate.
                    </p>
                    <div class="rr-spec-badges">
                      <div class="rr-spec-box">
                        <div class="spec-num">100%</div>
                        <div class="spec-lbl">BOOKMATCHED SYMMETRY</div>
                        <div class="spec-sub">Dual-leaf mirror grain</div>
                      </div>
                      <div class="rr-spec-box">
                        <div class="spec-num">16.8%</div>
                        <div class="spec-lbl">NATURAL TECTOQUINONE</div>
                        <div class="spec-sub">Zero climate warping</div>
                      </div>
                      <div class="rr-spec-box">
                        <div class="spec-num">18-COAT</div>
                        <div class="spec-lbl">FRENCH SATIN POLISH</div>
                        <div class="spec-sub">Open-pore tactile grain</div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Bottom Scrubber & Chapter Bar -->
                <div class="rr-bottom-controls">
                  <div class="rr-timeline-container">
                    <div class="rr-timeline-track" id="rrTrack" onclick="handleTrackClick(event)">
                      <div class="rr-timeline-fill" id="rrTimelineFill"></div>
                      <div class="rr-timeline-handle" id="rrTimelineHandle"></div>
                    </div>
                    <div class="rr-chapter-markers">
                      <button class="rr-chapter-btn active magnetic-btn" id="btnChap0" onclick="seekRRVideo(0.05, 0)">[01 CHASSIS MATRIX]</button>
                      <button class="rr-chapter-btn magnetic-btn" id="btnChap1" onclick="seekRRVideo(4.2, 1)">[02 ORBITAL DIVE]</button>
                      <button class="rr-chapter-btn magnetic-btn" id="btnChap2" onclick="seekRRVideo(8.6, 2)">[03 TEAK INTERIOR REVEAL]</button>
                    </div>
                  </div>
                  <div class="rr-controls-row">
                    <div class="rr-scroll-prompt">
                      <span class="mouse-icon"></span>
                      <span>SCROLL DOWN TO ADVANCE VIDEO // REVEAL CABIN INTERIOR</span>
                    </div>
                    <button class="rr-play-btn magnetic-btn" id="rrPlayToggleBtn" onclick="toggleRRPlay()">
                      <span id="rrPlayIcon">▶</span> <span id="rrPlayText">PLAY AUTOMATICALLY</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>\'\'\'
        rr_soup = BeautifulSoup(rr_section_html, 'html.parser')
        intro_component.insert_after(rr_soup)'''

assert patina_html_target in content, "HTML target not found"
content = content.replace(patina_html_target, rr_html_replacement)
print("1. HTML successfully replaced.")

# 2. CSS REPLACEMENT: Replace Patina CSS with Rolls-Royce Video & HUD CSS
css_start = "      /* === CHRONOS 100-YEAR PATINA SECTION (ARCHITECTURAL SANDSTONE & ADVANCED ANIMATIONS) === */"
css_end = "      /* === ADVANCED ELEMENT ANIMATIONS === */"

rr_css = """      /* === ROLLS-ROYCE 3D EXPLODED VIDEO & SCROLL SCRUB SHOWCASE === */
      .home-rr-wrap {
        width: 100% !important;
        position: relative !important;
        background: transparent !important;
        padding: 4.5rem 0 !important;
        border-top: var(--size--border) solid var(--content--border) !important;
        border-bottom: var(--size--border) solid var(--content--border) !important;
      }
      .rr-container {
        max-width: 1320px !important;
        margin: 0 auto !important;
        padding: 2.8rem !important;
        background: var(--content--white) !important;
        color: var(--content--primary) !important;
        border-radius: 16px !important;
        border: var(--size--border) solid var(--content--border) !important;
        box-shadow: 0 10px 40px rgba(28, 24, 21, 0.06), inset 0 1px 0 rgba(255, 255, 255, 0.6) !important;
        position: relative !important;
        overflow: hidden !important;
      }
      .rr-bg-grid {
        position: absolute !important;
        inset: 0 !important;
        background-size: 40px 40px !important;
        background-image: 
          linear-gradient(to right, rgba(200, 191, 178, 0.22) 1px, transparent 1px),
          linear-gradient(to bottom, rgba(200, 191, 178, 0.22) 1px, transparent 1px) !important;
        pointer-events: none !important;
      }
      .rr-head {
        display: flex !important;
        justify-content: space-between !important;
        align-items: flex-end !important;
        margin-bottom: 2.2rem !important;
        position: relative !important;
        z-index: 2 !important;
        gap: 2rem !important;
      }
      .rr-head-left {
        max-width: 820px !important;
      }
      .rr-tag {
        display: inline-flex !important;
        align-items: center !important;
        gap: 8px !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 0.72rem !important;
        letter-spacing: 0.14em !important;
        color: var(--content--brand) !important;
        text-transform: uppercase !important;
        font-weight: 700 !important;
        margin-bottom: 0.6rem !important;
      }
      .rr-tag-dot {
        width: 7px !important;
        height: 7px !important;
        border-radius: 50% !important;
        background: var(--content--brand) !important;
        box-shadow: 0 0 8px rgba(250, 54, 0, 0.8) !important;
        animation: heroPulse 1.8s infinite !important;
      }
      .rr-title {
        font-family: 'Fraktion Sans', sans-serif !important;
        font-size: 2.35rem !important;
        font-weight: 600 !important;
        letter-spacing: -0.03em !important;
        margin: 0 0 0.75rem 0 !important;
        color: var(--content--primary) !important;
        line-height: 1.15 !important;
      }
      .rr-subtitle {
        font-size: 1.05rem !important;
        line-height: 1.6 !important;
        color: var(--content--secondary) !important;
        margin: 0 !important;
      }
      .rr-subtitle strong {
        color: var(--content--primary) !important;
      }
      .rr-head-right {
        flex-shrink: 0 !important;
      }
      .rr-seal-card {
        padding: 1rem 1.4rem !important;
        border-radius: 12px !important;
        background: #f4efe8 !important;
        border: 1px solid var(--content--border) !important;
        text-align: center !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.04) !important;
      }
      .rr-seal-crown {
        font-size: 1.4rem !important;
        margin-bottom: 2px !important;
      }
      .rr-seal-val {
        font-family: 'Geistmono', monospace !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.08em !important;
        color: #1c1815 !important;
      }
      .rr-seal-sub {
        font-family: 'Geistmono', monospace !important;
        font-size: 0.68rem !important;
        color: var(--content--brand) !important;
        letter-spacing: 0.06em !important;
        font-weight: 700 !important;
        margin-top: 2px !important;
      }
      .rr-seal-meta {
        font-family: 'Geistmono', monospace !important;
        font-size: 0.65rem !important;
        color: var(--content--secondary) !important;
        margin-top: 3px !important;
      }

      /* Viewport Stage */
      .rr-stage-wrap {
        position: relative !important;
        width: 100% !important;
        z-index: 2 !important;
      }
      .rr-video-viewport {
        position: relative !important;
        width: 100% !important;
        aspect-ratio: 16 / 9.2 !important;
        max-height: 700px !important;
        border-radius: 14px !important;
        overflow: hidden !important;
        background: #0d0c0a !important;
        border: 1px solid var(--content--border) !important;
        box-shadow: 0 24px 70px rgba(28, 24, 21, 0.16) !important;
      }
      .rr-video-el {
        width: 100% !important;
        height: 100% !important;
        object-fit: cover !important;
        display: block !important;
      }

      /* Vignette Gradients */
      .rr-video-vignette-top {
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 110px !important;
        background: linear-gradient(to bottom, rgba(13, 12, 10, 0.88), transparent) !important;
        pointer-events: none !important;
        z-index: 3 !important;
      }
      .rr-video-vignette-bottom {
        position: absolute !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 150px !important;
        background: linear-gradient(to top, rgba(13, 12, 10, 0.95), transparent) !important;
        pointer-events: none !important;
        z-index: 3 !important;
      }
      .rr-video-vignette-side {
        position: absolute !important;
        top: 0 !important;
        bottom: 0 !important;
        left: 0 !important;
        width: 50% !important;
        background: linear-gradient(to right, rgba(13, 12, 10, 0.65), transparent) !important;
        pointer-events: none !important;
        z-index: 3 !important;
      }

      /* Corner Brackets */
      .rr-corner-bracket {
        position: absolute !important;
        width: 18px !important;
        height: 18px !important;
        border-color: #fa3600 !important;
        border-style: solid !important;
        z-index: 5 !important;
        pointer-events: none !important;
      }
      .rr-corner-bracket.tl { top: 12px; left: 12px; border-width: 2px 0 0 2px; }
      .rr-corner-bracket.tr { top: 12px; right: 12px; border-width: 2px 2px 0 0; }
      .rr-corner-bracket.bl { bottom: 12px; left: 12px; border-width: 0 0 2px 2px; }
      .rr-corner-bracket.br { bottom: 12px; right: 12px; border-width: 0 2px 2px 0; }

      /* Top HUD Bar */
      .rr-hud-bar {
        position: absolute !important;
        top: 18px !important;
        left: 24px !important;
        right: 24px !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        z-index: 6 !important;
        pointer-events: none !important;
      }
      .rr-hud-chip {
        display: inline-flex !important;
        align-items: center !important;
        gap: 8px !important;
        background: rgba(28, 24, 21, 0.88) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        padding: 6px 14px !important;
        border-radius: 999px !important;
        border: 1px solid rgba(217, 119, 6, 0.45) !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 0.72rem !important;
        color: #efece6 !important;
        font-weight: 600 !important;
        letter-spacing: 0.08em !important;
      }
      .rr-pulse-dot {
        width: 6px !important;
        height: 6px !important;
        border-radius: 50% !important;
        background: #10b981 !important;
        box-shadow: 0 0 6px #10b981 !important;
        animation: heroPulse 1.5s infinite !important;
      }
      .rr-phase-badge {
        font-family: 'Geistmono', monospace !important;
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.12em !important;
        color: #fa3600 !important;
        background: rgba(250, 54, 0, 0.12) !important;
        border: 1px solid rgba(250, 54, 0, 0.4) !important;
        padding: 5px 14px !important;
        border-radius: 999px !important;
      }
      .rr-mono-num {
        color: #f59e0b !important;
      }

      /* Narrative Glass Card */
      .rr-narrative-overlay {
        position: absolute !important;
        top: 85px !important;
        left: 28px !important;
        max-width: 480px !important;
        z-index: 6 !important;
        pointer-events: auto !important;
        transition: transform 0.4s ease, opacity 0.4s ease !important;
      }
      .rr-glass-card {
        background: rgba(28, 24, 21, 0.82) !important;
        backdrop-filter: blur(14px) !important;
        -webkit-backdrop-filter: blur(14px) !important;
        border: 1px solid rgba(217, 119, 6, 0.45) !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        color: #efece6 !important;
        box-shadow: 0 16px 40px rgba(0,0,0,0.4) !important;
      }
      .rr-glass-pill {
        display: inline-flex !important;
        align-items: center !important;
        gap: 6px !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 0.68rem !important;
        font-weight: 700 !important;
        color: #f59e0b !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
        margin-bottom: 0.5rem !important;
      }
      .rr-pill-dot {
        width: 5px !important;
        height: 5px !important;
        border-radius: 50% !important;
        background: #f59e0b !important;
      }
      .rr-glass-heading {
        font-family: 'Fraktion Sans', sans-serif !important;
        font-size: 1.45rem !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
        margin: 0 0 0.65rem 0 !important;
        color: #ffffff !important;
        line-height: 1.2 !important;
      }
      .rr-glass-text {
        font-size: 0.88rem !important;
        line-height: 1.6 !important;
        color: rgba(239, 236, 230, 0.88) !important;
        margin: 0 0 1.1rem 0 !important;
      }
      .rr-glass-text strong {
        color: #f59e0b !important;
      }
      .rr-spec-badges {
        display: grid !important;
        grid-template-columns: repeat(3, 1fr) !important;
        gap: 8px !important;
        border-top: 1px solid rgba(255,255,255,0.12) !important;
        padding-top: 0.9rem !important;
      }
      .rr-spec-box {
        background: rgba(255,255,255,0.05) !important;
        padding: 6px 8px !important;
        border-radius: 6px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
      }
      .spec-num {
        font-family: 'Geistmono', monospace !important;
        font-size: 0.92rem !important;
        font-weight: 700 !important;
        color: #fa3600 !important;
      }
      .spec-lbl {
        font-family: 'Geistmono', monospace !important;
        font-size: 0.58rem !important;
        font-weight: 700 !important;
        color: #efece6 !important;
        letter-spacing: 0.05em !important;
        margin-top: 2px !important;
      }
      .spec-sub {
        font-size: 0.55rem !important;
        color: rgba(239, 236, 230, 0.65) !important;
        margin-top: 1px !important;
      }

      /* Bottom Controls */
      .rr-bottom-controls {
        position: absolute !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        padding: 14px 28px 18px 28px !important;
        z-index: 6 !important;
      }
      .rr-timeline-container {
        margin-bottom: 10px !important;
      }
      .rr-timeline-track {
        position: relative !important;
        width: 100% !important;
        height: 6px !important;
        background: rgba(255, 255, 255, 0.22) !important;
        border-radius: 999px !important;
        cursor: pointer !important;
        margin-bottom: 8px !important;
      }
      .rr-timeline-fill {
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        height: 100% !important;
        width: 0% !important;
        background: linear-gradient(90deg, #d97706, #fa3600) !important;
        border-radius: 999px !important;
        box-shadow: 0 0 10px rgba(250, 54, 0, 0.7) !important;
      }
      .rr-timeline-handle {
        position: absolute !important;
        top: 50% !important;
        left: 0% !important;
        transform: translate(-50%, -50%) !important;
        width: 14px !important;
        height: 14px !important;
        border-radius: 50% !important;
        background: #ffffff !important;
        border: 2px solid #fa3600 !important;
        box-shadow: 0 0 10px rgba(250, 54, 0, 0.9) !important;
        pointer-events: none !important;
      }
      .rr-chapter-markers {
        display: flex !important;
        justify-content: space-between !important;
        gap: 8px !important;
      }
      .rr-chapter-btn {
        background: rgba(28, 24, 21, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: rgba(239, 236, 230, 0.75) !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 0.68rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.08em !important;
        padding: 5px 12px !important;
        border-radius: 6px !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
      }
      .rr-chapter-btn:hover,
      .rr-chapter-btn.active {
        background: rgba(250, 54, 0, 0.18) !important;
        border-color: #fa3600 !important;
        color: #ffffff !important;
        box-shadow: 0 0 10px rgba(250, 54, 0, 0.3) !important;
      }
      .rr-controls-row {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
      }
      .rr-scroll-prompt {
        display: inline-flex !important;
        align-items: center !important;
        gap: 8px !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 0.7rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.08em !important;
        color: rgba(239, 236, 230, 0.75) !important;
      }
      .mouse-icon {
        width: 11px !important;
        height: 16px !important;
        border: 1.5px solid #fa3600 !important;
        border-radius: 8px !important;
        position: relative !important;
      }
      .mouse-icon::after {
        content: '' !important;
        position: absolute !important;
        top: 2px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 2px !important;
        height: 3px !important;
        background: #fa3600 !important;
        border-radius: 1px !important;
        animation: mouseScroll 1.2s infinite !important;
      }
      @keyframes mouseScroll {
        0% { transform: translate(-50%, 0); opacity: 1; }
        100% { transform: translate(-50%, 5px); opacity: 0; }
      }
      .rr-play-btn {
        background: #fa3600 !important;
        color: #ffffff !important;
        border: none !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.08em !important;
        padding: 7px 16px !important;
        border-radius: 999px !important;
        cursor: pointer !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 6px !important;
        box-shadow: 0 4px 15px rgba(250, 54, 0, 0.4) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
      }
      .rr-play-btn:hover {
        transform: scale(1.04) !important;
        box-shadow: 0 6px 20px rgba(250, 54, 0, 0.6) !important;
      }

"""

pattern_css = re.escape(css_start) + r".*?" + re.escape(css_end)
assert re.search(pattern_css, content, re.DOTALL), "CSS target pattern not found"
content = re.sub(pattern_css, rr_css + "      " + css_end, content, flags=re.DOTALL)
print("2. CSS successfully replaced.")

# 3. JAVASCRIPT REPLACEMENT: Replace Chronos JS functions with Rolls-Royce video scrub engine
js_start = "      function snapToYear(year) {"
js_end = "      // === 4. INTRO ARCHITECTURAL CALIPER SPLIT SLIDER ==="

rr_js = """      // === ROLLS-ROYCE 3D EXPLODED VIDEO SCROLL SCRUB ENGINE ===
      let isRRAutoPlaying = false;
      let rrScrollTriggerInstance = null;

      function formatTimecode(sec) {
        if (!sec || isNaN(sec)) sec = 0;
        const m = Math.floor(sec / 60);
        const s = Math.floor(sec % 60);
        const ms = Math.floor((sec % 1) * 100);
        return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}.${String(ms).padStart(2, '0')}`;
      }

      function updateRRHUD(progress, currentTime, duration) {
        const fill = document.getElementById('rrTimelineFill');
        const handle = document.getElementById('rrTimelineHandle');
        const timecode = document.getElementById('rrTimecode');
        const phaseBadge = document.getElementById('rrPhaseBadge');
        const overlay = document.getElementById('rrNarrativeOverlay');

        const pct = Math.max(0, Math.min(100, progress * 100));
        if (fill) fill.style.width = pct + '%';
        if (handle) handle.style.left = pct + '%';

        if (timecode) {
          timecode.textContent = `${formatTimecode(currentTime)} / ${formatTimecode(duration || 10)}`;
        }

        // Chapters & Phases
        const btn0 = document.getElementById('btnChap0');
        const btn1 = document.getElementById('btnChap1');
        const btn2 = document.getElementById('btnChap2');

        if (progress < 0.35) {
          if (phaseBadge) phaseBadge.textContent = "PHASE 01: CHASSIS & SUSPENSION MATRIX";
          if (btn0) btn0.classList.add('active');
          if (btn1) btn1.classList.remove('active');
          if (btn2) btn2.classList.remove('active');
          if (overlay) {
            overlay.style.opacity = '0.9';
            overlay.style.transform = 'translateY(0)';
          }
        } else if (progress < 0.70) {
          if (phaseBadge) phaseBadge.textContent = "PHASE 02: ORBITAL TRAJECTORY DIVE";
          if (btn0) btn0.classList.remove('active');
          if (btn1) btn1.classList.add('active');
          if (btn2) btn2.classList.remove('active');
          if (overlay) {
            overlay.style.opacity = '0.75';
            overlay.style.transform = 'translateY(10px)';
          }
        } else {
          if (phaseBadge) phaseBadge.textContent = "PHASE 03: BESPOKE NILAMBUR TEAK CABIN REVEAL";
          if (btn0) btn0.classList.remove('active');
          if (btn1) btn1.classList.remove('active');
          if (btn2) btn2.classList.add('active');
          if (overlay) {
            overlay.style.opacity = '1';
            overlay.style.transform = 'translateY(0) scale(1.02)';
          }
        }
      }

      function seekRRVideo(targetTime, chapterIdx) {
        playWoodTap(540 + (chapterIdx || 0) * 60);
        const video = document.getElementById('rrVideoEl');
        if (!video) return;

        if (isRRAutoPlaying) {
          video.pause();
          isRRAutoPlaying = false;
          const playText = document.getElementById('rrPlayText');
          const playIcon = document.getElementById('rrPlayIcon');
          if (playText) playText.textContent = "PLAY AUTOMATICALLY";
          if (playIcon) playIcon.textContent = "▶";
        }

        const dur = video.duration || 10;
        targetTime = Math.max(0, Math.min(dur - 0.05, targetTime));
        video.currentTime = targetTime;

        const progress = targetTime / dur;
        updateRRHUD(progress, targetTime, dur);

        // Scroll the main-inner scroller to the corresponding scroll position
        if (rrScrollTriggerInstance) {
          const scroller = document.querySelector('.main-inner') || window;
          const targetScroll = rrScrollTriggerInstance.start + (progress * (rrScrollTriggerInstance.end - rrScrollTriggerInstance.start));
          if (scroller.scrollTo) {
            scroller.scrollTo({ top: targetScroll, behavior: 'smooth' });
          } else {
            scroller.scrollTop = targetScroll;
          }
        }
      }

      function handleTrackClick(e) {
        const track = document.getElementById('rrTrack');
        const video = document.getElementById('rrVideoEl');
        if (!track || !video) return;
        const rect = track.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const ratio = Math.max(0, Math.min(1, clickX / rect.width));
        const dur = video.duration || 10;
        seekRRVideo(ratio * dur);
      }

      function toggleRRPlay() {
        const video = document.getElementById('rrVideoEl');
        const playText = document.getElementById('rrPlayText');
        const playIcon = document.getElementById('rrPlayIcon');
        if (!video) return;

        isRRAutoPlaying = !isRRAutoPlaying;
        playWoodTap(isRRAutoPlaying ? 660 : 440);

        if (isRRAutoPlaying) {
          video.play().then(() => {
            if (playText) playText.textContent = "PAUSE & SCRUB";
            if (playIcon) playIcon.textContent = "⏸";
          }).catch(err => {
            console.warn('Video auto-play prevented:', err);
            isRRAutoPlaying = false;
          });
        } else {
          video.pause();
          if (playText) playText.textContent = "PLAY AUTOMATICALLY";
          if (playIcon) playIcon.textContent = "▶";
        }
      }

      function initRollsRoyceVideo() {
        const video = document.getElementById('rrVideoEl');
        if (!video) return;

        video.addEventListener('loadedmetadata', () => {
          video.currentTime = 0.05;
          updateRRHUD(0, 0.05, video.duration);
        });

        video.addEventListener('timeupdate', () => {
          if (isRRAutoPlaying && video.duration) {
            const prog = video.currentTime / video.duration;
            updateRRHUD(prog, video.currentTime, video.duration);
            if (prog >= 0.98) {
              video.pause();
              isRRAutoPlaying = false;
              const playText = document.getElementById('rrPlayText');
              const playIcon = document.getElementById('rrPlayIcon');
              if (playText) playText.textContent = "REPLAY SHOWCASE";
              if (playIcon) playIcon.textContent = "↺";
            }
          }
        });
      }

"""

pattern_js = re.escape(js_start) + r".*?" + re.escape(js_end)
assert re.search(pattern_js, content, re.DOTALL), "JS target pattern not found"
content = re.sub(pattern_js, rr_js + "      " + js_end, content, flags=re.DOTALL)
print("3. JS functions successfully replaced.")

# 4. SCROLLTRIGGER INITIALIZER REPLACEMENT: Replace Chronos ScrollTrigger with Rolls-Royce ScrollTrigger
st_target = """        // --- CHRONOS 100-YEAR MATURATION SCROLLTRIGGER SCRUB ---
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
        }"""

rr_st_replacement = """        // --- ROLLS-ROYCE 3D EXPLODED VIDEO PINNED SCROLLTRIGGER SCRUB ---
        initRollsRoyceVideo();
        const rrWrap = document.getElementById('rrRollsRoyceSection');
        const rrVideo = document.getElementById('rrVideoEl');
        if (rrWrap && rrVideo && typeof ScrollTrigger !== 'undefined') {
          rrScrollTriggerInstance = ScrollTrigger.create({
            scroller: scrollerEl,
            trigger: rrWrap,
            start: 'top top',
            end: '+=2400',
            pin: true,
            scrub: 0.4,
            onUpdate: (self) => {
              if (!isRRAutoPlaying && rrVideo.duration) {
                const targetTime = self.progress * (rrVideo.duration - 0.05);
                rrVideo.currentTime = targetTime;
                updateRRHUD(self.progress, targetTime, rrVideo.duration);
              }
            }
          });
        }"""

assert st_target in content, "ScrollTrigger target not found"
content = content.replace(st_target, rr_st_replacement)
print("4. ScrollTrigger successfully replaced.")

with open(builder_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated clean_aiswarya_builder.py successfully!")
