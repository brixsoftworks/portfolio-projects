import re

with open('/home/mullainathan/projects/nilambur-teak-wood/clean_aiswarya_builder.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ==============================================================================
# 1. ADVANCED ELEMENT CSS
# ==============================================================================
advanced_element_css = """
      /* === ADVANCED ELEMENT ANIMATIONS === */

      /* 1. Hero Terroir Telemetry HUD */
      .hero-terroir-hud {
        display: inline-flex !important;
        align-items: center !important;
        gap: 10px !important;
        background: rgba(28, 24, 21, 0.9) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        padding: 6px 14px !important;
        border-radius: 999px !important;
        border: 1px solid rgba(217, 119, 6, 0.45) !important;
        color: #efece6 !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 11px !important;
        letter-spacing: 0.1em !important;
        margin-bottom: 16px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15) !important;
      }
      .terroir-pulse-dot {
        width: 7px !important;
        height: 7px !important;
        border-radius: 50% !important;
        background: #10b981 !important;
        box-shadow: 0 0 8px #10b981 !important;
        animation: pulseGreen 1.8s infinite ease-in-out !important;
      }
      @keyframes pulseGreen {
        0% { opacity: 0.6; transform: scale(0.9); }
        50% { opacity: 1; transform: scale(1.3); }
        100% { opacity: 0.6; transform: scale(0.9); }
      }
      .terroir-time {
        color: #f59e0b !important;
        font-weight: 700 !important;
      }

      /* 2. Explore Woodcraft Live Odometer Metrics */
      .intro-metrics-grid {
        display: grid !important;
        grid-template-columns: repeat(4, 1fr) !important;
        gap: 16px !important;
        width: 100% !important;
        margin-top: 14px !important;
      }
      @media screen and (max-width: 767px) {
        .intro-metrics-grid {
          grid-template-columns: repeat(2, 1fr) !important;
        }
      }
      .intro-metric-card {
        background: var(--content--white) !important;
        border: 1px solid var(--content--border) !important;
        border-radius: 10px !important;
        padding: 16px 12px !important;
        text-align: center !important;
        transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease !important;
      }
      .intro-metric-card:hover {
        transform: translateY(-3px) !important;
        border-color: var(--content--brand) !important;
        box-shadow: 0 6px 20px rgba(250, 54, 0, 0.12) !important;
      }
      .intro-metric-num {
        font-size: 30px !important;
        font-weight: 800 !important;
        color: var(--content--brand) !important;
        font-family: 'Geistmono', monospace !important;
        line-height: 1.1 !important;
        margin-bottom: 4px !important;
      }
      .intro-metric-lbl {
        font-family: 'Geistmono', monospace !important;
        font-size: 10px !important;
        letter-spacing: 0.15em !important;
        text-transform: uppercase !important;
        color: var(--content--primary) !important;
        font-weight: 700 !important;
        margin-bottom: 2px !important;
      }
      .intro-metric-sub {
        font-size: 11px !important;
        color: var(--content--secondary) !important;
        line-height: 1.3 !important;
      }

      /* 3. Chronos Specimen Switcher */
      .specimen-switcher {
        display: inline-flex !important;
        gap: 8px !important;
        background: rgba(28, 24, 21, 0.06) !important;
        padding: 4px !important;
        border-radius: 8px !important;
        margin-bottom: 16px !important;
        border: 1px solid var(--content--border) !important;
      }
      .specimen-tab {
        background: transparent !important;
        border: none !important;
        padding: 6px 14px !important;
        border-radius: 6px !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 11px !important;
        letter-spacing: 0.08em !important;
        color: var(--content--secondary) !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
      }
      .specimen-tab.active {
        background: var(--content--brand) !important;
        color: #fff !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 8px rgba(250, 54, 0, 0.3) !important;
      }

      /* 4. 3D Exploded Mortise & Tenon Joinery Schematic */
      .joinery-schematic-card {
        background: var(--content--white) !important;
        border: 1px solid var(--content--border) !important;
        border-radius: 12px !important;
        padding: 20px !important;
        width: 100% !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.06) !important;
        position: relative !important;
        overflow: hidden !important;
      }
      .joinery-head {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        margin-bottom: 14px !important;
      }
      .joinery-title {
        font-family: 'Geistmono', monospace !important;
        font-size: 12px !important;
        letter-spacing: 0.15em !important;
        color: var(--content--brand) !important;
        text-transform: uppercase !important;
        font-weight: 700 !important;
      }
      .joinery-meta {
        font-family: 'Geistmono', monospace !important;
        font-size: 10px !important;
        color: var(--content--secondary) !important;
        letter-spacing: 0.08em !important;
      }
      .joinery-stage {
        position: relative !important;
        height: 250px !important;
        background: #f4efe8 !important;
        border: 1px dashed var(--content--border) !important;
        border-radius: 8px !important;
        overflow: hidden !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
      }
      .joinery-svg {
        width: 100% !important;
        height: 100% !important;
      }
      .joinery-controls {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        margin-top: 14px !important;
      }
      .joinery-btn {
        background: var(--content--primary) !important;
        color: #efece6 !important;
        border: 1px solid rgba(250, 54, 0, 0.4) !important;
        padding: 8px 14px !important;
        border-radius: 6px !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 11px !important;
        letter-spacing: 0.08em !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
      }
      .joinery-btn:hover {
        background: var(--content--brand) !important;
        color: #fff !important;
      }
      .joinery-load-badge {
        font-family: 'Geistmono', monospace !important;
        font-size: 11px !important;
        color: var(--content--secondary) !important;
      }
      .joinery-load-badge strong {
        color: var(--content--brand) !important;
      }

      /* 5. CTA Corner Brackets & Phone Dialers */
      .cta-main {
        position: relative !important;
      }
      .cta-bracket {
        position: absolute !important;
        width: 22px !important;
        height: 22px !important;
        border: 2px solid var(--content--brand) !important;
        pointer-events: none !important;
        transition: transform 0.4s cubic-bezier(0.25, 1, 0.5, 1) !important;
        z-index: 10 !important;
      }
      .cta-bracket.tl { top: 12px !important; left: 12px !important; border-right: none !important; border-bottom: none !important; }
      .cta-bracket.tr { top: 12px !important; right: 12px !important; border-left: none !important; border-bottom: none !important; }
      .cta-bracket.bl { bottom: 12px !important; left: 12px !important; border-right: none !important; border-top: none !important; }
      .cta-bracket.br { bottom: 12px !important; right: 12px !important; border-left: none !important; border-top: none !important; }
      .cta-main:hover .cta-bracket.tl { transform: translate(-4px, -4px) !important; }
      .cta-main:hover .cta-bracket.tr { transform: translate(4px, -4px) !important; }
      .cta-main:hover .cta-bracket.bl { transform: translate(-4px, 4px) !important; }
      .cta-main:hover .cta-bracket.br { transform: translate(4px, 4px) !important; }

      .cta-phone-grid {
        display: flex !important;
        gap: 16px !important;
        margin-top: 24px !important;
        flex-wrap: wrap !important;
      }
      .cta-phone-pill {
        display: inline-flex !important;
        align-items: center !important;
        gap: 10px !important;
        background: var(--content--primary) !important;
        color: #efece6 !important;
        border: 1px solid rgba(217, 119, 6, 0.4) !important;
        padding: 10px 18px !important;
        border-radius: 999px !important;
        text-decoration: none !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 12px !important;
        letter-spacing: 0.08em !important;
        transition: all 0.25s ease !important;
        cursor: pointer !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
      }
      .cta-phone-pill:hover {
        background: var(--content--brand) !important;
        color: #fff !important;
        transform: scale(1.03) !important;
        border-color: var(--content--brand) !important;
        box-shadow: 0 6px 20px rgba(250, 54, 0, 0.3) !important;
      }
      .cta-phone-pill .phone-icon {
        font-size: 14px !important;
      }

      /* 6. Magnetic Elements */
      .magnetic-btn {
        will-change: transform;
      }
"""

# Insert advanced CSS before </style>
style_end = content.find('</style>')
assert style_end != -1, "</style> not found"
content = content[:style_end] + advanced_element_css + "\n    " + content[style_end:]

# ==============================================================================
# 2. DOM MODIFICATIONS IN build()
# ==============================================================================

# A. Insert Hero Terroir Telemetry HUD
hero_sub_target = "hero_img_inner = hero_wrap.find(class_='home-hero-img-inner')"
assert hero_sub_target in content, "hero_img_inner target not found"

hero_hud_code = """# A. Prepend Live Terroir Telemetry HUD to Hero
        hero_sub_wrap = hero_wrap.find(class_='home-hero-sub-wrap')
        if hero_sub_wrap:
            hud_html = '''
            <div class="hero-terroir-hud" id="terroirHud">
              <div class="terroir-pulse-dot"></div>
              <span class="terroir-location">NILAMBUR, KERALA [11°16′N 76°13′E]</span>
              <span class="terroir-sep">•</span>
              <span class="terroir-reserve">CANOLI PLOT 1844</span>
              <span class="terroir-sep">•</span>
              <span class="terroir-time" id="heroLiveTime">LIVE IST --:--:--</span>
            </div>
            '''
            hero_sub_wrap.insert(0, BeautifulSoup(hud_html, 'html.parser'))

        """
content = content.replace(hero_sub_target, hero_hud_code + hero_sub_target, 1)

# B. Insert Odometer Metrics in Explore Woodcraft (.home-intro-partner-inner)
intro_code_target = "intro_img_el.append(BeautifulSoup(intro_html, 'html.parser'))"
assert intro_code_target in content, "intro_html append target not found"

odometer_code = """intro_img_el.append(BeautifulSoup(intro_html, 'html.parser'))

        # B. Insert Live Odometer Metrics Grid into Explore Woodcraft
        intro_partner_inner = intro_wrap.find(class_='home-intro-partner-inner')
        if intro_partner_inner:
            intro_partner_inner.clear()
            metrics_html = '''
            <div class="intro-metrics-grid">
              <div class="intro-metric-card">
                <div class="intro-metric-num" data-target="1844">0</div>
                <div class="intro-metric-lbl">CANOLI'S PLOT HERITAGE</div>
                <div class="intro-metric-sub">World's Oldest Teak Reserve</div>
              </div>
              <div class="intro-metric-card">
                <div class="intro-metric-num" data-target="581">0</div>
                <div class="intro-metric-lbl">GEOGRAPHICAL INDICATION</div>
                <div class="intro-metric-sub">Kerala GI Reg. No. 581</div>
              </div>
              <div class="intro-metric-card">
                <div class="intro-metric-num" data-target="100" data-suffix="%">0%</div>
                <div class="intro-metric-lbl">SOLID NILAMBUR HEARTWOOD</div>
                <div class="intro-metric-sub">0% Particle Board / MDF</div>
              </div>
              <div class="intro-metric-card">
                <div class="intro-metric-num" data-target="40" data-suffix="+">0+</div>
                <div class="intro-metric-lbl">HERITAGE ARTISANS</div>
                <div class="intro-metric-sub">Generational Wood Carvers</div>
              </div>
            </div>
            '''
            intro_partner_inner.append(BeautifulSoup(metrics_html, 'html.parser'))"""

content = content.replace(intro_code_target, odometer_code, 1)

# C. Insert Specimen Switcher above .patina-visual in Chronos
patina_grid_target = """<div class="patina-grid">
              <!-- 3D Specimen Card -->
              <div class="patina-visual-wrap" id="visualWrap">"""

patina_switcher_replacement = """<div class="patina-grid">
              <!-- 3D Specimen Card -->
              <div class="patina-visual-wrap" id="visualWrap">
                <div class="specimen-switcher">
                  <button class="specimen-tab active magnetic-btn" onclick="switchChronosSpecimen(0)">[01 BED PLATFORM]</button>
                  <button class="specimen-tab magnetic-btn" onclick="switchChronosSpecimen(1)">[02 LIVING SOFA]</button>
                  <button class="specimen-tab magnetic-btn" onclick="switchChronosSpecimen(2)">[03 MODULAR KITCHEN]</button>
                </div>"""

assert patina_grid_target in content, "patina_grid_target not found"
content = content.replace(patina_grid_target, patina_switcher_replacement, 1)

# D. Insert Interactive 3D Exploded Joinery Schematic in Technical Map (.home-map-main-img-inner)
map_target = "# CTA Section: Double-Height Grand Living Room"
assert map_target in content, "CTA section target not found"

joinery_insertion_code = """# 7b. Insert Interactive 3D Exploded Joinery Schematic in Technical Map Section
    map_main_img_inner = soup.find(class_='home-map-main-img-inner')
    if map_main_img_inner:
        map_main_img_inner.clear()
        joinery_html = '''
        <div class="joinery-schematic-card">
          <div class="joinery-head">
            <div class="joinery-title">ISOMETRIC CAD: BLIND MORTISE &amp; TENON ASSEMBLY</div>
            <div class="joinery-meta">SCALE 1:5 • TECTONA GRANDIS</div>
          </div>
          <div class="joinery-stage">
            <svg class="joinery-svg" viewBox="0 0 600 240">
              <defs>
                <pattern id="gridPat" width="20" height="20" patternUnits="userSpaceOnUse">
                  <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(200, 191, 178, 0.4)" stroke-width="0.5"/>
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#gridPat)" />

              <!-- Component A: Mortise Block (Left) -->
              <g id="mortiseBlock" transform="translate(140, 60)">
                <polygon points="0,40 60,10 140,45 80,75" fill="#dfd7c7" stroke="#1c1815" stroke-width="1.5"/>
                <polygon points="0,40 80,75 80,140 0,105" fill="#c4b8a3" stroke="#1c1815" stroke-width="1.5"/>
                <polygon points="80,75 140,45 140,110 80,140" fill="#ad9f88" stroke="#1c1815" stroke-width="1.5"/>
                <polygon points="40,55 70,40 100,55 70,70" fill="#3a3026" stroke="#fa3600" stroke-width="1.5"/>
                <text x="30" y="30" font-family="'Geistmono', monospace" font-size="9" fill="#fa3600" font-weight="bold">MORTISE CAVITY (90×42mm)</text>
              </g>

              <!-- Component B: Tenon Tongue (Right) -->
              <g id="tenonBlock" transform="translate(340, 60)">
                <polygon points="-50,55 -20,40 10,55 -20,70" fill="#e69d45" stroke="#fa3600" stroke-width="1.5"/>
                <polygon points="-50,55 -20,70 -20,95 -50,80" fill="#c97d26" stroke="#fa3600" stroke-width="1.5"/>
                <polygon points="0,40 60,10 140,45 80,75" fill="#dfd7c7" stroke="#1c1815" stroke-width="1.5"/>
                <polygon points="0,40 80,75 80,140 0,105" fill="#c4b8a3" stroke="#1c1815" stroke-width="1.5"/>
                <polygon points="80,75 140,45 140,110 80,140" fill="#ad9f88" stroke="#1c1815" stroke-width="1.5"/>
                <text x="60" y="30" font-family="'Geistmono', monospace" font-size="9" fill="#d97706" font-weight="bold">SOLID TENON TONGUE</text>
              </g>

              <!-- Component C: Teak Locking Pin (Top) -->
              <g id="lockingPin" transform="translate(230, 10)">
                <polygon points="0,0 12,-5 24,0 12,5" fill="#fa3600" stroke="#1c1815" stroke-width="1.2"/>
                <polygon points="0,0 12,5 12,45 0,40" fill="#b91c1c" stroke="#1c1815" stroke-width="1.2"/>
                <polygon points="12,5 24,0 24,40 12,45" fill="#991b1b" stroke="#1c1815" stroke-width="1.2"/>
                <text x="32" y="25" font-family="'Geistmono', monospace" font-size="8" fill="#fa3600" font-weight="bold">12mm TEAK PIN</text>
              </g>

              <!-- Dynamic dimension leader lines -->
              <g id="dimensionLines">
                <line x1="200" y1="120" x2="330" y2="120" stroke="#fa3600" stroke-width="1" stroke-dasharray="3,3"/>
                <circle cx="200" cy="120" r="2.5" fill="#fa3600"/>
                <circle cx="330" cy="120" r="2.5" fill="#fa3600"/>
                <text x="240" y="115" font-family="'Geistmono', monospace" font-size="9" fill="#fa3600" font-weight="bold" id="dimReadout">EXPAND: 130mm</text>
              </g>
            </svg>
          </div>
          <div class="joinery-controls">
            <button class="joinery-btn magnetic-btn" onclick="toggleJoineryLock(event)">
              <span>INTERLOCK JOINT ↔ EXPLODE VIEW</span>
            </button>
            <div class="joinery-load-badge">
              TENSILE CAPACITY: <strong>14.2 kN SCREWLESS</strong>
            </div>
          </div>
        </div>
        '''
        map_main_img_inner.append(BeautifulSoup(joinery_html, 'html.parser'))

    """

content = content.replace(map_target, joinery_insertion_code + map_target, 1)

# E. Insert CTA Drafting Corner Brackets & Phone Dialers
cta_code_target = "cta_deco.append(BeautifulSoup(cta_html, 'html.parser'))"
assert cta_code_target in content, "cta_html append target not found"

cta_brackets_code = """cta_deco.append(BeautifulSoup(cta_html, 'html.parser'))

        # E. Add animated drafting corner brackets and phone dialers to CTA
        cta_main = cta_wrap.find(class_='cta-main')
        if cta_main:
            brackets_html = '''
            <div class="cta-bracket tl"></div>
            <div class="cta-bracket tr"></div>
            <div class="cta-bracket bl"></div>
            <div class="cta-bracket br"></div>
            '''
            cta_main.insert(0, BeautifulSoup(brackets_html, 'html.parser'))

            cta_sub = cta_main.find(class_='cta-main-item-sub')
            if cta_sub:
                phone_html = '''
                <div class="cta-phone-grid">
                  <a href="tel:+919447631731" class="cta-phone-pill magnetic-btn">
                    <span class="phone-icon">Tel: </span>
                    <span>JANARDHANAN: +91 94476 31731</span>
                  </a>
                  <a href="tel:+919656663063" class="cta-phone-pill magnetic-btn">
                    <span class="phone-icon">Tel: </span>
                    <span>JITHESH: +91 96566 63063</span>
                  </a>
                </div>
                '''
                cta_sub.append(BeautifulSoup(phone_html, 'html.parser'))"""

content = content.replace(cta_code_target, cta_brackets_code, 1)

# ==============================================================================
# 3. ADVANCED JAVASCRIPT ANIMATION ROUTINES
# ==============================================================================
advanced_js_code = """
      // === 7. LIVE TERROIR CLOCK ===
      function updateTerroirTime() {
        const now = new Date();
        const istStr = now.toLocaleTimeString('en-US', { timeZone: 'Asia/Kolkata', hour12: false });
        const el = document.getElementById('heroLiveTime');
        if (el) el.textContent = `LIVE IST ${istStr}`;
      }
      setInterval(updateTerroirTime, 1000);
      updateTerroirTime();

      // === 8. LIVE ODOMETER COUNTERS ===
      let odometerRan = false;
      function animateOdometerCounters() {
        if (odometerRan) return;
        odometerRan = true;
        document.querySelectorAll('.intro-metric-num').forEach(el => {
          const target = parseInt(el.getAttribute('data-target'));
          const suffix = el.getAttribute('data-suffix') || '';
          if (typeof gsap !== 'undefined') {
            gsap.fromTo({ val: 0 }, { val: target }, {
              duration: 2.0,
              ease: 'power3.out',
              onUpdate: function() {
                el.textContent = Math.round(this.targets()[0].val).toLocaleString() + suffix;
              }
            });
          }
        });
        playWoodTap(520);
      }

      // === 9. 3D EXPLODED MORTISE & TENON JOINERY INTERLOCK ===
      let joineryLocked = false;
      function toggleJoineryLock(e) {
        if (e) e.stopPropagation();
        joineryLocked = !joineryLocked;
        playWoodTap(joineryLocked ? 680 : 440);

        const tenon = document.getElementById('tenonBlock');
        const pin = document.getElementById('lockingPin');
        const dimReadout = document.getElementById('dimReadout');

        if (typeof gsap !== 'undefined') {
          if (joineryLocked) {
            gsap.to(tenon, { x: 230, duration: 0.85, ease: 'power3.inOut' });
            gsap.to(pin, { y: 65, duration: 0.5, delay: 0.7, ease: 'bounce.out', onComplete: () => playWoodTap(720) });
            if (dimReadout) dimReadout.textContent = "INTERLOCKED: 0mm";
          } else {
            gsap.to(pin, { y: 10, duration: 0.4, ease: 'power2.in' });
            gsap.to(tenon, { x: 340, duration: 0.85, delay: 0.2, ease: 'power3.out' });
            if (dimReadout) dimReadout.textContent = "EXPAND: 130mm";
          }
        }
      }

      // === 10. CHRONOS SPECIMEN SWITCHER ===
      const chronosSpecimens = [
        { src: '/images/bed-real.jpg', alt: 'Solid Nilambur Teak Bed' },
        { src: '/images/sofa-fluted-real.jpg', alt: 'Nilambur Teak Living Room Sofa' },
        { src: '/images/kitchen-real.jpg', alt: 'Modular Teak Kitchen Suite' }
      ];

      function switchChronosSpecimen(idx) {
        playWoodTap(540 + idx * 40);
        document.querySelectorAll('.specimen-tab').forEach((tab, i) => {
          tab.classList.toggle('active', i === idx);
        });
        const img = document.getElementById('patinaImg');
        if (img && chronosSpecimens[idx] && typeof gsap !== 'undefined') {
          gsap.to(img, {
            opacity: 0.3,
            duration: 0.2,
            onComplete: () => {
              img.src = chronosSpecimens[idx].src;
              gsap.to(img, { opacity: 1, duration: 0.3 });
              triggerScanline();
            }
          });
        }
      }

      // === 11. MAGNETIC CURSOR ATTRACTION ===
      function initMagneticButtons() {
        document.querySelectorAll('.magnetic-btn, .btn-basic, .btn-fill, .hero-rewipe-btn, .sound-toggle-btn, .intro-caliper-toggle-btn').forEach(btn => {
          btn.addEventListener('mousemove', (e) => {
            const rect = btn.getBoundingClientRect();
            const dx = e.clientX - (rect.left + rect.width / 2);
            const dy = e.clientY - (rect.top + rect.height / 2);
            if (typeof gsap !== 'undefined') {
              gsap.to(btn, { x: dx * 0.28, y: dy * 0.28, duration: 0.3, ease: 'power2.out' });
            }
          });
          btn.addEventListener('mouseleave', () => {
            if (typeof gsap !== 'undefined') {
              gsap.to(btn, { x: 0, y: 0, duration: 0.5, ease: 'elastic.out(1, 0.3)' });
            }
          });
        });
      }
"""

# Insert JS code before initAiswaryaPixelWipes
init_target = "function initAiswaryaPixelWipes() {"
assert init_target in content, "initAiswaryaPixelWipes not found"
content = content.replace(init_target, advanced_js_code + "\n      " + init_target, 1)

# In initAiswaryaPixelWipes, add ScrollTriggers for Odometer and Joinery
st_chronos_target = "// --- CHRONOS 100-YEAR MATURATION SCROLLTRIGGER SCRUB ---"
assert st_chronos_target in content, "st_chronos_target not found"

st_advanced_triggers = """// --- EXPLORE WOODCRAFT ODOMETER SCROLLTRIGGER ---
        const introMetrics = document.querySelector('.intro-metrics-grid');
        if (introMetrics && typeof ScrollTrigger !== 'undefined') {
          ScrollTrigger.create({
            scroller: scrollerEl,
            trigger: introMetrics,
            start: 'top 85%',
            onEnter: () => animateOdometerCounters()
          });
        }

        // --- TECHNICAL MAP JOINERY SCHEMATIC SCROLLTRIGGER ---
        const joineryCard = document.querySelector('.joinery-schematic-card');
        if (joineryCard && typeof ScrollTrigger !== 'undefined') {
          ScrollTrigger.create({
            scroller: scrollerEl,
            trigger: joineryCard,
            start: 'top 75%',
            onEnter: () => {
              if (!joineryLocked) toggleJoineryLock();
            }
          });
        }

        // --- INITIALIZE MAGNETIC CURSOR ---
        initMagneticButtons();

        // --- CHRONOS 100-YEAR MATURATION SCROLLTRIGGER SCRUB ---"""

content = content.replace(st_chronos_target, st_advanced_triggers, 1)

with open('/home/mullainathan/projects/nilambur-teak-wood/clean_aiswarya_builder.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("clean_aiswarya_builder.py successfully updated with advanced element animations!")
