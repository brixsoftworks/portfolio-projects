import re
from bs4 import BeautifulSoup, NavigableString

def build():
    with open('/home/mullainathan/projects/nilambur-teak-wood/public/test-heron.html', 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    # 1. Ensure CSS link points to local /css/heronai.css
    for link in soup.find_all('link', rel='stylesheet'):
        link['href'] = '/css/heronai.css'

    # 2. Decompose broken cookie banner completely
    cookie = soup.find(class_='cookie')
    if cookie:
        cookie.decompose()

    # 3. Clean out Netlify tracking scripts
    for s in list(soup.find_all('script')):
        src = s.get('src', '')
        sid = s.get('id', '')
        if 'googletagmanager' in src or 'rum' in src or sid == 'netlify-rum-container':
            s.decompose()

    # 4. Remove the two floating title cards in Blueprint/Map ("Master Woodcraft Details" / "Right there with you" and "For the whole design")
    # Keep container DOM nodes intact for Webflow main.js controller, clear text nodes
    for intel in soup.find_all(class_='home-intel-inner'):
        for h in intel.find_all(class_='heading'):
            h.string = ""
        for s in list(intel.find_all(string=True)):
            if isinstance(s, NavigableString):
                s.replace_with("")

    # Decompose old introduction card that referenced manual modelling
    intro = soup.find(class_='home-map-intro')
    if intro:
        intro.decompose()
    for in_el in soup.find_all(class_='home-map-intro'):
        in_el.decompose()

    # 5. Completely remove "THE FURNITURE DILEMMA" / Problems section
    prob = soup.find('home-problem-wrap')
    if prob:
        prob.decompose()
    for p_el in soup.find_all(class_='home-problem-wrap'):
        p_el.decompose()

    # 6. Completely remove Awwwards "Site of the Day" side ribbon
    awwwards = soup.find(class_='awwwards')
    if awwwards:
        awwwards.decompose()
    for aw in soup.find_all(lambda tag: tag.get('class') and any('awwwards' in c for c in tag.get('class', []))):
        aw.decompose()

    # 7. Replace big animated footer graphic with Aiswarya CAD line drawing and animated ink reveal
    footer_img_wrap = soup.find(class_='footer-img-wrap')
    if footer_img_wrap:
        # Mobile/tablet image
        for item in footer_img_wrap.find_all(class_='footer-img-item'):
            for img in item.find_all('img'):
                img['src'] = '/images/aiswarya-footer-filled.png'
        # Desktop unmasked base outline
        for main_div in footer_img_wrap.find_all(class_='ink-mask-img'):
            if 'main' in main_div.get('class', []):
                for img in main_div.find_all('img'):
                    img['src'] = '/images/aiswarya-footer-outline.png'
        # Desktop animated ink reveal layer
        for svg_img in footer_img_wrap.find_all('image'):
            if svg_img.get('href') or svg_img.get('xlink:href'):
                svg_img['href'] = '/images/aiswarya-footer-filled.png'
                svg_img['xlink:href'] = '/images/aiswarya-footer-filled.png'

    # 8. Retain footer-logo-svg in DOM so Webflow P0 parallax initialization does not fail,
    # but hide it visually and display the gold Aiswarya J Monogram inside footer-logo
    footer_logo = soup.find(class_='footer-logo')
    if footer_logo:
        svg_el = footer_logo.find('svg', class_='footer-logo-svg')
        if svg_el:
            svg_el['style'] = "display: none !important; opacity: 0 !important; pointer-events: none !important;"
        sketch = footer_logo.find(class_='sketch')
        if sketch:
            sketch.clear()
            sketch.append(BeautifulSoup("""
            <div style="display: flex; align-items: center; justify-content: center; width: 100%; height: 100%;">
              <img src="/images/aiswarya-j-gold.png" alt="Aiswarya J Logo" style="max-height: 140px; width: auto; object-fit: contain; filter: drop-shadow(0 4px 12px rgba(0,0,0,0.15));" />
            </div>
            """, 'html.parser'))

    # 8b. Replace generic site images with Aiswarya Industries custom real photos and Gemini architectural sketches
    # PIXEL-BY-PIXEL SWIPE DOWN REVEAL SYSTEM

    # Hero Section: 3-Image Architectural Drafting Grid with Pixel-by-Pixel Reveal
    hero_wrap = soup.find(class_='home-hero-wrap')
    if hero_wrap:
        # A. Prepend Live Terroir Telemetry HUD to Hero
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

        hero_img_inner = hero_wrap.find(class_='home-hero-img-inner')
        if hero_img_inner:
            hero_img_inner.clear()
            hero_triptych_html = '''
            <div class="home-hero-img-grid">
              <!-- Panel 01: Heritage Living Room Suite -->
              <div class="home-hero-img-col" id="heroCol0">
                <div class="home-hero-col-badge">
                  <span class="home-hero-col-num">[01]</span>
                  <span class="home-hero-col-name">HERITAGE LIVING SUITE</span>
                </div>
                <button class="hero-rewipe-btn" onclick="rewipeHeroCol(0, event)">↺ RE-WIPE</button>
                <div class="pixel-wipe-wrap">
                  <div class="pixel-wipe-laser-beam"></div>
                  <div class="hero-wood-sheen"></div>
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
                  <div class="pixel-wipe-laser-beam"></div>
                  <div class="hero-wood-sheen"></div>
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
                  <div class="pixel-wipe-laser-beam"></div>
                  <div class="hero-wood-sheen"></div>
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
            '''
            hero_img_inner.append(BeautifulSoup(hero_triptych_html, 'html.parser'))

    # Intro Section: Residential Courtyard (Explore Woodcraft)
    intro_wrap = soup.find(class_='home-intro-wrap')
    if intro_wrap:
        intro_img_el = intro_wrap.find(class_='home-intro-img')
        if intro_img_el:
            intro_img_el.clear()
            intro_html = '''
            <div class="pixel-wipe-wrap" id="introPixelWrap">
              <div class="pixel-wipe-laser-beam"></div>
              <div class="pixel-matrix-grid"></div>
              <div class="hero-wood-sheen"></div>
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
            '''
            intro_img_el.append(BeautifulSoup(intro_html, 'html.parser'))

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
            intro_partner_inner.append(BeautifulSoup(metrics_html, 'html.parser'))


    # 6b. Insert Rolls-Royce Nilambur Teak 3D Exploded Fullscreen Canvas Engine (Pure Frame-by-Frame Architecture)
    intro_component = soup.find('home-intro-wrap')
    if intro_component:
        rr_section_html = '''
        <div class="home-rr-wrap web-component" id="rrRollsRoyceSection">
          <div class="rr-fullscreen-stage">
            <!-- Hardware-Accelerated Canvas for Frame-by-Frame Scrub (Zero Video Chrome) -->
            <canvas id="rrCanvas" class="rr-fullscreen-canvas"></canvas>

            <!-- Cinematic Vignette & Ambient Darkness -->
            <div class="rr-cinematic-vignette"></div>

            <!-- Architectural CAD Grid & Crosshair Markings -->
            <div class="rr-cad-grid"></div>
            <div class="rr-cad-mark tl">+</div>
            <div class="rr-cad-mark tr">+</div>
            <div class="rr-cad-mark bl">+</div>
            <div class="rr-cad-mark br">+</div>

            <!-- Ambient Architectural Telemetry Watermarks -->
            <div class="rr-watermark top-left">
              <span class="rr-dot-pulse"></span>
              <span>11°16′N 76°13′E // NILAMBUR TERROIR</span>
            </div>
            <div class="rr-watermark top-right">
              <span>CANOLI PLOT 1844 • KERALA GI REG. NO. 581</span>
            </div>
            <div class="rr-watermark bottom-right">
              <span>ROLLS-ROYCE COACHBUILD SPECIFICATION // SOLID TEAK VENEER</span>
            </div>

            <!-- Interactive Holographic Cursor Reticle -->
            <div class="rr-cursor-reticle" id="rrReticle">
              <div class="rr-reticle-hud" id="rrReticleHud">CAD 1:1 // PING 340Hz</div>
            </div>

            <!-- Act 1: Initial Chassis Matrix -->
            <div class="rr-act-card" id="rrAct1">
              <div class="rr-act-tag">
                <span>AUTOMOTIVE MARQUE BENCHMARK</span>
              </div>
              <h2 class="rr-act-title">The Wood of<br>Rolls-Royce</h2>
              <p class="rr-act-desc">
                For over a century, when the world's most prestigious automotive marque demands perfection for its bespoke interiors, only authentic <strong>Nilambur Teak</strong> from Malabar suffices.
              </p>
              <div class="rr-scroll-indicator">
                <div class="rr-scroll-mouse">
                  <div class="rr-scroll-wheel"></div>
                </div>
                <span>SCROLL DOWN TO ADVANCE ARCHITECTURE</span>
              </div>
            </div>

            <!-- Act 2: Orbital Flight & Bookmatched Symmetry -->
            <div class="rr-act-card right" id="rrAct2" style="opacity: 0; pointer-events: none; transform: translateY(30px);">
              <div class="rr-act-tag">
                <span>100% BOOKMATCHED SYMMETRY</span>
              </div>
              <h2 class="rr-act-title">Dual-Leaf<br>Mirror-Grain Fascia</h2>
              <p class="rr-act-desc">
                Every dashboard, cascading center console, and rear executive picnic table is sliced from consecutive leaves of a single seasoned Nilambur teak log—hand-laid to create seamless mirror-symmetry across the entire cabin.
              </p>
              <div class="rr-metric-row">
                <div class="rr-metric-pill">
                  <div class="p-num">1:1</div>
                  <div class="p-lbl">FLITCH SYMMETRY</div>
                </div>
                <div class="rr-metric-pill">
                  <div class="p-num">3.2mm</div>
                  <div class="p-lbl">GROWTH RING PITCH</div>
                </div>
              </div>
            </div>

            <!-- Act 3: Cabin Reveal & Climate Immunity -->
            <div class="rr-act-card" id="rrAct3" style="opacity: 0; pointer-events: none; transform: translateY(30px);">
              <div class="rr-act-tag">
                <span>TECTOQUINONE RESIN IMMUNITY</span>
              </div>
              <h2 class="rr-act-title">Zero Warping.<br>Immortal Bronze.</h2>
              <p class="rr-act-desc">
                Enriched with 16.8% natural preservative oils and a dense silica crystal lattice, genuine Nilambur Teak is impervious to desert heat and alpine freezes. It never shrinks, splits, or dulls—deepening over decades into an immortal royal bronze luster.
              </p>
              <div class="rr-badge-row">
                <div class="rr-spec-item">
                  <div class="rr-spec-num">16.8%</div>
                  <div class="rr-spec-label">NATURAL RESIN OIL</div>
                </div>
                <div class="rr-spec-item">
                  <div class="rr-spec-num">0.72%</div>
                  <div class="rr-spec-label">SILICA HEARTWOOD</div>
                </div>
                <div class="rr-spec-item">
                  <div class="rr-spec-num">18-COAT</div>
                  <div class="rr-spec-label">FRENCH SATIN POLISH</div>
                </div>
              </div>
            </div>
          </div>
        </div>'''
        rr_soup = BeautifulSoup(rr_section_html, 'html.parser')
        intro_component.insert_after(rr_soup)

        # Platform / Atelier Section:
    platform_wrap = soup.find(class_='home-platform-wrap')
    if platform_wrap:
        # 1. Update thumbnails in content area
        p_content_imgs = platform_wrap.find_all(class_='home-platform-content-img')
        if len(p_content_imgs) >= 1:
            for img in p_content_imgs[0].find_all('img'):
                img['src'] = '/images/sofa-fluted-sketch.webp'
        if len(p_content_imgs) >= 2:
            for img in p_content_imgs[1].find_all('img'):
                img['src'] = '/images/kitchen-sketch.webp'

        # 2. Update the layers in .home-platform-img-item-inner with Advanced Pixel Reveal & Spatial 3D Systems
        p_img_inners = platform_wrap.find_all(class_='home-platform-img-item-inner')
        plat_data = [
            {
                'sketch': '/images/sofa-fluted-sketch.webp',
                'real': '/images/sofa-fluted-real.jpg',
                'alt': 'Living Room Teak Sofa & Fluted Panelling',
                'code': 'SOFA & FLUTED PANELLING',
                'specs': 'SOLID NILAMBUR FRAME • ACOUSTIC FLUTING'
            },
            {
                'sketch': '/images/kitchen-sketch.webp',
                'real': '/images/kitchen-real.jpg',
                'alt': 'Turnkey Modular Teak Kitchen',
                'code': 'MODULAR TEAK KITCHEN',
                'specs': 'MARINE-GRADE TEAK CARCASS • BLUM HARDWARE'
            }
        ]
        for idx, inner in enumerate(p_img_inners):
            if idx < len(plat_data):
                pdata = plat_data[idx]
                inner.clear()
                p_html = f'''
                <div class="platform-side-img-card" id="platCard{idx}">
                  <div class="platform-col-badge">
                    <span class="platform-col-num">[0{idx+1}]</span>
                    <span class="platform-col-name">{pdata['code']}</span>
                  </div>
                  <button class="platform-rewipe-btn" onclick="rewipePlatItem({idx}, event)">↺ RE-WIPE</button>
                  <div class="pixel-wipe-wrap">
                    <div class="pixel-wipe-laser-beam"></div>
                    <div class="pixel-matrix-grid"></div>
                    <div class="hero-wood-sheen"></div>
                    <div class="pixel-wipe-base">
                      <img class="img-basic img-abs" src="{pdata['sketch']}" alt="{pdata['alt']} - Architectural Sketch" />
                    </div>
                    <div class="pixel-wipe-reveal">
                      <img class="img-basic img-abs pixel-reveal-img" src="{pdata['real']}" alt="{pdata['alt']} - Real Photograph" />
                    </div>
                  </div>
                  <div class="platform-cad-hud">
                    <div class="cad-specs">
                      <strong>ATELIER:</strong> {pdata['specs']}
                    </div>
                    <div class="cad-corner-marks">SCALE 1:20 • SPEC: 0{idx+1}-P</div>
                  </div>
                </div>
                '''
                inner.append(BeautifulSoup(p_html, 'html.parser'))

    # Why Us Section: 4 Craftsmanship Steps with Advanced Pixel-by-Pixel Reveal & Spatial 3D Systems
    why_wrap = soup.find(class_='home-why-wrap')
    if why_wrap:
        why_step_data = [
            {
                'sketch': '/images/courtyard-sketch.webp',
                'real': '/images/courtyard-real.jpg',
                'alt': 'Architectural Consultation & Space Planning',
                'step': '01',
                'code': 'TERROIR CONSULTATION',
                'meta': '11.2710°N 76.2235°E // KERALA GI 581 // 1:20 SCALE',
                'specs': 'CANOLI SEEDLINE 1844 • PALATIAL ARCHIVE'
            },
            {
                'sketch': '/images/dining-sketch.webp',
                'real': '/images/dining-real.jpg',
                'alt': 'Sustainable Nilambur Teak Selection',
                'step': '02',
                'code': 'TIMBER SELECTION',
                'meta': '100-YR HEARTWOOD // 16.8% TECTO RESIN // 760 kg/m³',
                'specs': 'ZERO DRY ROT • SELF-LUBRICATING DENSITY'
            },
            {
                'sketch': '/images/bed-sketch.webp',
                'real': '/images/bed-real.jpg',
                'alt': 'Handcrafted Solid Teak Cot - Master Artisan Joinery',
                'step': '03',
                'code': 'ARTISAN JOINERY',
                'meta': 'BLIND MORTISE & TENON // 14.2 kN TENSILE LOAD',
                'specs': 'INTERLOCKING TEAK DOWELS • SCREWLESS CORE'
            },
            {
                'sketch': '/images/wardrobe-sketch.webp',
                'real': '/images/wardrobe-real.jpg',
                'alt': 'Heritage Natural Oil Polishing',
                'step': '04',
                'code': 'FINISHING & POLISH',
                'meta': '18-COAT FRENCH SATIN // 0.72% SILICA // 340Hz PING',
                'specs': 'ORGANIC BEESWAX • IMMORTAL ROYAL BRONZE'
            }
        ]
        why_img_inners = why_wrap.find_all(class_='home-why-item-img-inner')
        for idx, inner in enumerate(why_img_inners):
            if idx < len(why_step_data):
                data = why_step_data[idx]
                inner.clear()
                wipe_html = f'''
                <div class="why-side-img-card" id="whyCard{idx}">
                  <div class="why-col-badge">
                    <span class="why-col-num">[{data['step']}]</span>
                    <span class="why-col-name">{data['code']}</span>
                  </div>
                  <button class="why-rewipe-btn" onclick="rewipeWhyStep({idx}, event)">↺ RE-WIPE</button>
                  <div class="pixel-wipe-wrap">
                    <div class="pixel-wipe-laser-beam"></div>
                    <div class="pixel-matrix-grid"></div>
                    <div class="hero-wood-sheen"></div>
                    <div class="pixel-wipe-base">
                      <img class="img-basic img-abs" src="{data['sketch']}" alt="{data['alt']} Sketch" />
                    </div>
                    <div class="pixel-wipe-reveal">
                      <img class="img-basic img-abs pixel-reveal-img" src="{data['real']}" alt="{data['alt']} Real Photograph" />
                    </div>
                  </div>
                  <div class="why-cad-hud">
                    <div class="cad-specs">
                      <strong>SPEC:</strong> {data['specs']}<br>
                      <strong>DATA:</strong> {data['meta']}
                    </div>
                    <div class="cad-corner-marks">CAD 1:20 • SEC: {data['step']}-W</div>
                  </div>
                </div>
                '''
                inner.append(BeautifulSoup(wipe_html, 'html.parser'))

    # Portfolio Section: 8 Categories
    usecase_wrap = soup.find(class_='home-usecase-wrap')
    if usecase_wrap:
        portfolio_imgs = [
            '/images/living-grand-real.jpg',  # 1. Living Room Furniture
            '/images/kitchen-real.jpg',       # 2. Solid Wood Modular Kitchens
            '/images/bed-real.jpg',           # 3. Luxury Bedroom Suites
            '/images/wardrobe-real.jpg',      # 4. Custom Wardrobes & Walk-Ins
            '/images/courtyard-real.jpg',     # 5. Architectural Doors & Windows
            '/images/dining-real.jpg',        # 6. Dining Sets & Chairs
            '/images/sofa-fluted-real.jpg',   # 7. Wooden Wall Panelling & Ceilings
            '/images/dining-real.jpg'         # 8. Custom Staircases & Railings
        ]
        usecase_items = usecase_wrap.find_all(class_='home-usecase-img-item')
        for idx, item in enumerate(usecase_items):
            if idx < len(portfolio_imgs):
                for img in item.find_all('img'):
                    img['src'] = portfolio_imgs[idx]

    # 7b. Insert Interactive 3D Exploded Joinery Schematic in Technical Map Section
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
            <svg class="joinery-svg" viewBox="0 0 600 240" id="mortiseJointSvg">
              <defs>
                <pattern id="gridPat" width="20" height="20" patternUnits="userSpaceOnUse">
                  <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(200, 191, 178, 0.4)" stroke-width="0.5"/>
                </pattern>
                <filter id="tenonGlow" x="-20%" y="-20%" width="140%" height="140%">
                  <feGaussianBlur stdDeviation="3" result="blur" />
                  <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
              </defs>
              <rect width="100%" height="100%" fill="url(#gridPat)" />

              <!-- Acoustic Ping Waves -->
              <circle id="acousticWave1" cx="242" cy="70" r="8" stroke="#fa3600" stroke-width="2" fill="none" opacity="0"/>
              <circle id="acousticWave2" cx="242" cy="70" r="8" stroke="#f59e0b" stroke-width="1.5" fill="none" opacity="0"/>

              <!-- Stress-Strain FEA Heatmap Contour -->
              <polygon id="stressHeatmap" points="160,85 242,55 315,90 235,120" fill="none" stroke="#fa3600" stroke-width="3" filter="url(#tenonGlow)" opacity="0"/>

              <!-- Component A: Mortise Block (Left) -->
              <g id="mortiseBlock" transform="translate(140, 60)">
                <polygon points="0,40 60,10 140,45 80,75" fill="#dfd7c7" stroke="#1c1815" stroke-width="1.5"/>
                <polygon points="0,40 80,75 80,140 0,105" fill="#c4b8a3" stroke="#1c1815" stroke-width="1.5"/>
                <polygon points="80,75 140,45 140,110 80,140" fill="#ad9f88" stroke="#1c1815" stroke-width="1.5"/>
                <polygon points="40,55 70,40 100,55 70,70" fill="#3a3026" stroke="#fa3600" stroke-width="1.5"/>
                <text x="30" y="30" font-family="'Geistmono', monospace" font-size="9" fill="#fa3600" font-weight="bold">MORTISE CAVITY (90×42mm)</text>
              </g>

              <!-- Component B: Tenon Tongue (Right) -->
              <g id="tenonBlock" transform="translate(340, 60)" style="cursor: grab;">
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
                <line id="dimLine" x1="200" y1="120" x2="330" y2="120" stroke="#fa3600" stroke-width="1" stroke-dasharray="3,3"/>
                <circle cx="200" cy="120" r="2.5" fill="#fa3600"/>
                <circle id="dimDotRight" cx="330" cy="120" r="2.5" fill="#fa3600"/>
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

    # CTA Section: Double-Height Grand Living Room
    cta_wrap = soup.find(class_='cta-wrap')
    if cta_wrap:
        cta_deco = cta_wrap.find(class_='cta-deco-item-img-inner')
        if cta_deco:
            cta_deco.clear()
            cta_html = '''
            <div class="pixel-wipe-wrap">
              <div class="pixel-wipe-laser-beam"></div>
              <div class="pixel-matrix-grid"></div>
              <div class="hero-wood-sheen"></div>
              <div class="pixel-wipe-base">
                <img class="img-basic img-abs" src="/images/living-grand-sketch.webp" alt="Double-Height Grand Living Hall - Sketch" />
              </div>
              <div class="pixel-wipe-reveal">
                <img class="img-basic img-abs pixel-reveal-img" src="/images/living-grand-real.jpg" alt="Double-Height Grand Living Hall - Real Photograph" />
              </div>
            </div>
            '''
            cta_deco.append(BeautifulSoup(cta_html, 'html.parser'))

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
                    <span class="phone-icon">📞</span>
                    <span>JANARDHANAN: +91 94476 31731</span>
                  </a>
                  <a href="tel:+919656663063" class="cta-phone-pill magnetic-btn">
                    <span class="phone-icon">📞</span>
                    <span>JITHESH: +91 96566 63063</span>
                  </a>
                </div>
                '''
                cta_sub.append(BeautifulSoup(phone_html, 'html.parser'))


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

    # 9. Update Title and Metadata
    if soup.title:
        soup.title.string = "Aiswarya Industries | Dealers in Wooden Furniture & Interior Designing | Nilambur, Kerala"

    for meta in soup.find_all('meta'):
        prop = meta.get('property', '')
        name = meta.get('name', '')
        if prop in ['og:title', 'twitter:title']:
            meta['content'] = "Aiswarya Industries | Wooden Furniture & Interior Designing, Nilambur"
        elif prop in ['og:description', 'twitter:description'] or name == 'description':
            meta['content'] = "Aiswarya Industries, Nilambur — Handcrafted wooden furniture, custom solid teak living sets, modular kitchens, bedroom suites, wooden wardrobes, and turnkey architectural interior designing. Contact: Janardhanan: +91 9447631731, Jithesh: +91 9656663063."

    # 10. Header Logo with 'J' Monogram and Aiswarya Industries brand
    logo_inner = soup.find(class_='header-logo-inner')
    if logo_inner:
        logo_inner.clear()
        new_logo_html = """
        <a href="/" class="header-logo-item bg-global w-inline-block w--current" style="display: flex; align-items: center; justify-content: center; width: 36px; height: 36px; text-decoration: none;">
          <img src="/images/aiswarya-j-gold.png" alt="Aiswarya J Logo" style="height: 26px; width: auto; object-fit: contain; display: block;" />
        </a>
        <a href="/" class="header-logo-item item-txt w-inline-block w--current" style="display: flex; flex-direction: column; justify-content: center; width: auto; max-width: 260px; padding-left: 8px; text-decoration: none; line-height: 1.15;">
          <span style="font-family: 'BT Grotesk', -apple-system, BlinkMacSystemFont, sans-serif; font-weight: 800; font-size: 13px; letter-spacing: 0.08em; color: var(--content--primary); text-transform: uppercase;">AISWARYA INDUSTRIES</span>
          <span style="font-family: 'Geistmono', monospace; font-size: 8px; letter-spacing: 0.04em; color: var(--content--secondary); text-transform: uppercase; white-space: nowrap;">WOODEN FURNITURE &amp; INTERIORS</span>
        </a>
        """
        logo_inner.append(BeautifulSoup(new_logo_html, 'html.parser'))

    # 11. Safe Text Replacements (strictly inside DOM Text Nodes)
    text_replacements = [
        # Floating titles to remove completely
        ('Master Woodcraft Details', ''),
        ('Right there with you', ''),
        ('Precision Joinery & Natural Teak Grain', ''),
        ('For the whole design', ''),

        # Preloader
        ('WELCOME TO HERON AI', 'WELCOME TO AISWARYA INDUSTRIES'),
        ('Technology/AI Software Company', 'Dealers in Wooden Furniture & Interior Designing'),
        ('TECHNOLOGY/AI SOFTWARE COMPANY', 'DEALERS IN WOODEN FURNITURE & INTERIOR DESIGNING'),
        ('FOUNDED:2026', 'FOUNDED:NILAMBUR WOODCRAFT'),
        ('AI-powered building code compliance for architects', 'Custom Solid Wood Furniture & Turnkey Luxury Interior Designing'),
        ('AI-POWERED BUILDING CODE COMPLIANCE FOR ARCHITECTS', 'CUSTOM SOLID WOOD FURNITURE & TURNKEY LUXURY INTERIOR DESIGNING'),
        ('(BIM / Revit integration)', '(Nilambur Teak & Hardwood Specialists)'),
        ('(BIM / REVIT INTEGRATION)', '(NILAMBUR TEAK & HARDWOOD SPECIALISTS)'),
        ('1801 California St. Suite 2400 Denver, CO 80202', 'Mannuppadam, Eranhimangad P.O., Nilambur, Malappuram, Kerala - 679329'),
        ('1801 CALIFORNIA ST. SUITE 2400 DENVER, CO 80202', 'MANNUPPADAM, ERANHIMANGAD P.O., NILAMBUR, KERALA - 679329 (PH: +91 9447 631 731 / +91 9656 663 063)'),
        ('BY BEARPLUS,', 'BY AISWARYA INDUSTRIES,'),
        ('THE AWARD-WINNING', 'DEALERS IN WOODEN FURNITURE'),
        ('DESIGN AGENCY', '& INTERIOR DESIGNING'),

        # Preloader 10 Steps
        ('001 INITIALIZE CORE SYSTEM', '001 HARVEST SEASONED NILAMBUR TEAK'),
        ('002 LOAD AI MODELS', '002 ARCHITECTURAL INTERIOR SPACE PLANNING'),
        ('003 CONFIGURE DATA PIPELINES', '003 CUSTOM FURNITURE 3D CAD MODELING'),
        ('004 SYNC DISTRIBUTED NODES', '004 ACCURATE ON-SITE ROOM MEASUREMENTS'),
        ('005 VALIDATE INPUT STREAMS', '005 SELECT PREMIUM GRAIN HARDWOODS'),
        ('006 OPTIMIZE INFERENCE ENGINE', '006 PRECISION MORTISE & TENON JOINERY'),
        ('007 DEPLOY TEST ENVIRONMENT', '007 MULTI-TIER SURFACE MICRO-SANDING'),
        ('008 ENABLE REAL-TIME PROCESSING', '008 NATURAL WOOD POLISH & PU SEALING'),
        ('009 RUN DIAGNOSTICS', '009 EXPERT ON-SITE INSTALLATION & FIT'),
        ('010 START EXECUTION', '010 DELIVER HEIRLOOM INTERIOR SANCTUARY'),

        # Navigation
        ('Product', 'Furniture Collections'),
        ('Heron Chat Widget', 'Living & Dining Furniture'),
        ('Heron Dashboard', 'Modular Kitchens & Wardrobes'),
        ('Pricing', 'Interior Design Packages'),
        ('Resources', 'Woodcraft Portfolio'),
        ('Insights', 'Nilambur Teak Craft'),
        ('AI Practices', 'Seasoning & Joinery'),
        ('Design Workflows', 'Turnkey Process'),
        ('About us', 'About Aiswarya'),
        ('About', 'About Aiswarya'),
        ('Contact us', 'Contact Atelier'),
        ('contact us', 'Call: +91 9447 631 731'),

        # Buttons
        ('Learn more', 'Explore Woodcraft'),
        ('Learn More', 'Explore Woodcraft'),
        ('LEARN MORE', 'EXPLORE WOODCRAFT'),
        ('Discover more', 'Explore Furniture'),

        # Hero
        ('Click and drag your mouse to see violations', 'Drag cursor to inspect artisan wood joinery & furniture proportions'),
        ('IBC 1015.3', 'AISWARYA INDUSTRIES'),
        ('Guardrail required for fall protection', 'Dealers in Wooden Furniture & Interior Designing'),
        ('IBC 1011.11', 'NILAMBUR, KERALA'),
        ('Handrails required.', 'Mannuppadam, Eranhimangad P.O. - 679329'),
        ('An AI agent that works inside your design tools', 'Handcrafted Wooden Furniture & Luxury Interior Designing'),
        ('Heron reviews your model, identifies issues, and proposes solutions. Upon approval, it edits automatically. This concept crafted by',
         'Aiswarya Industries brings master woodcraft and turnkey interior designing to life. We manufacture custom solid teak furniture, modular kitchens, and architectural woodwork tailored to your home.'),
        ('Bearplus agency', 'Aiswarya Industries, Nilambur'),
        ('the award-winning design agency.', 'dealers in wooden furniture & interior designing.'),
        ('Faster iterations', '100% Solid Teak'),
        ('Fewer mistakes', 'Master Joinery'),
        ('Less busywork', 'Turnkey Interiors'),

        # Intro
        ("THE REPETITIVE PARTS OF MODELLING SHOULDN'T EAT YOUR DAY. HERON HANDLES THE FIDDLY, MANUAL WORK SO YOU CAN STAY FOCUSED ON THE DESIGN, NOT THE SOFTWARE.",
         "YOUR HOME DESERVES LIFETIME SOLID WOOD, NOT FRAGILE VENEERS. AISWARYA INDUSTRIES CRAFTS BESPOKE WOODEN FURNITURE AND ENDURING INTERIORS FROM SEASONED NILAMBUR TEAK."),
        ('clients', 'Specialities'),
        ('Works natively inside the tools you already use, including Revit, Rhino, ArchiCAD and SketchUp.',
         'Delivering handcrafted wooden furniture, custom cabinetry, and turnkey interior designing across Nilambur, Malappuram, and all over Kerala.'),

        # Blueprint / Map details
        ('IBC 1017.2', 'SOLID NILAMBUR TEAK'),
        ('Exit Access Travel Distance', 'Natural Termite & Moisture Resistance'),
        ('Assembly occupancies without sprinklers are limited to 75 ft of exit travel distance. This layout exceeds the maximum allowable path length.',
         'Nilambur teak heartwood contains high natural tectoquinone oil concentrations, making our furniture naturally immune to termites, fungal rot, and monsoonal humidity without chemical baths.'),
        ('IBC 1010.1.2.1', 'TRADITIONAL MORTISE & TENON'),
        ('Door Swing Direction', 'Generational Structural Load Strength'),
        ('ICC A117.1 §604.3.1', 'ORGANIC HAND-RUBBED FINISH'),
        ('Accessible Toilet Clearance', 'Silky Satin Polish & Rich Chatoyancy'),
        ('Accessible restrooms require a 60” turning radius. This layout does not provide sufficient maneuvering space.',
         'Every wooden surface undergoes multi-grade sanding and hand-rubbed natural oil sealant, preserving the natural golden teak glow and authentic growth rings.'),

        # Blueprint / Map Content & Features
        ('Your model. Your tools. Connected.', 'Solid Teak. Master Joinery. Timeless Interiors.'),
        ('YOUR MODEL. YOUR TOOLS. CONNECTED.', 'SOLID TEAK. MASTER JOINERY. TIMELESS INTERIORS.'),
        ('RUN AN AGENT NATIVELY IN YOUR MODEL', 'BESPOKE FURNITURE & TURNKEY INTERIOR DESIGN'),
        ("Heron runs inside the design software you already use. It reads your model, understands what you're working on, and can make changes directly, with every action shown to you first so nothing happens without your say-so.",
         "Aiswarya Industries builds heirloom teak furniture and turnkey bespoke interiors. From architectural CAD floor space planning to timber selection, mortise-and-tenon joinery, and on-site hand installation, we craft pieces tailored to your home."),
        ('Works with Revit, Rhino, ArchiCAD, SketchUp.', 'Handcrafted from 100% seasoned genuine Nilambur teak.'),
        ('Understands your geometry and intent.', 'Custom tailored to your exact room dimensions and layout.'),
        ('Suggests fixes while you work.', 'Natural termite-proof oil richness and lifetime durability.'),
        ('Edits automatically after your approval.', 'Expert white-glove on-site assembly and satin finishing.'),

        # Platform
        ('Heron Chat widget', 'Custom Wooden Furniture Atelier'),
        ('A chat that floats over your design tool. Ask it about your model or tell it what to change, and it acts inside the software on your approval.',
         'Handcrafted living room sofa sets, solid wood dining tables, royal king beds, ergonomic office furniture, TV credenzas, and handcrafted accent pieces built to your exact specifications.'),
        ('Heron Dashboard', 'Turnkey Architectural Interior Designing'),
        ('Ask code questions about your building and get answers that reflect how the code applies to your layout, occupancy, and conditions, not just what the requirements say in isolation.',
         'Complete residential interior execution: modular solid teak kitchens, floor-to-ceiling wardrobes, wooden false ceilings, wall claddings, pooja units, and grand entrance doors with 3D space planning.'),

        # Why Us
        ('WHY US', 'WHY AISWARYA INDUSTRIES'),
        ('BUILT TO WORK THE WAY YOU DO', 'CRAFTED WITH HEREDITARY PASSION & RIGOR'),
        ('Heron fits into your process instead of replacing it. It watches quietly, speaks up when something needs attention, and only acts when you say so, so you stay in control the whole way through.',
         'From our workshop in Mannuppadam, Nilambur, our team combines traditional Kerala wood craftsmanship with modern architectural interior designing. We oversee every step from timber selection to on-site assembly.'),
        ('Observe', 'Consultation'),
        ('Heron watches your model as you design',
         'Janardhanan, Jithesh, and our design team conduct in-depth on-site room measurements and 3D layout planning.'),
        ('Advise', 'Timber Selection'),
        ('It flags issues and suggests fixes in plain language',
         'We hand-select 100% seasoned genuine Nilambur teak and premium hardwoods with uniform grain and zero sapwood.'),
        ('Act', 'Artisan Joinery'),
        ('With your approval, it makes the edit directly in the model',
         'Master carpenters hand-craft precision mortise-and-tenon joints, fluted panels, and custom architectural carvings.'),
        ('Learn', 'Finishing & Polish'),
        ("It picks up your firm's standards and gets more useful over time",
         'White-glove delivery, seamless installation in your home, and hand-applied multi-coat protective finishes.'),

        # Portfolio / Use Cases
        ('USE CASES', 'INTERIOR PORTFOLIO'),
        ('MADE FOR THE PEOPLE IN THE MODEL', 'BESPOKE WOODWORK FOR EVERY LIVING SPACE'),
        ('Architects', 'Living Room Furniture'),
        ('Hand the repetitive modelling to Heron and keep your focus on design.',
         'Solid teak sofa sets, sculptural coffee tables, TV wall consoles, and accent display shelving.'),
        ('Interior Designers', 'Solid Wood Modular Kitchens'),
        ('Get quick help with layouts, fixtures, and clearances without leaving your model.',
         'Teak wood shaker cabinetry, soft-close hardware, pull-out spice racks, and durable breakfast counters.'),
        ('Landscape Architects', 'Luxury Bedroom Suites'),
        ('Sort grading, site elements, and layouts without the manual grind.',
         'Solid hardwood king and queen beds, hydraulic storage, custom bedside tables, and vanity dressers.'),
        ('Engineers', 'Custom Wardrobes & Walk-Ins'),
        ('Run discipline-specific checks and edits in the model, so coordination issues surface earlier.',
         'Floor-to-ceiling wooden wardrobes, glass-and-teak displays, internal organizers, and walk-in dressing suites.'),
        ('BIM MANAGERS', 'Architectural Doors & Windows'),
        ("Keep models clean and on-standard with an agent that knows your firm's rules.",
         'Massive solid teak pivot entrance doors, intricately carved pooja mandapam doors, and casement windows.'),
        ('DRAFTERS', 'Dining Sets & Chairs'),
        ('Skip the tedious drawing cleanup and let Heron handle the repeatable parts.',
         'Heavy 6 to 12-seater solid teak dining tables with handcrafted ergonomic chairs and bench seating.'),
        ('DESIGN LEADS', 'Wooden Wall Panelling & Ceilings'),
        ("Keep quality and standards consistent across everyone's work.",
         'Acoustic wooden fluted wall panels, coffered ceiling beams, and decorative partition screens.'),
        ('SMALL FIRMS', 'Custom Staircases & Railings'),
        ('Get the output of a bigger team without adding headcount.',
         'Solid teak floating stair treads, turned balusters, and continuous ergonomic wooden handrails.'),

        # CTA
        ('SEE WHAT HERON CAN DO IN YOUR MODEL', 'TRANSFORM YOUR HOME WITH AISWARYA INDUSTRIES'),
        ("Book a demo and we'll show Heron working inside one of your own projects.",
         "Get in touch with Janardhanan (+91 9447 631 731) or Jithesh (+91 9656 663 063) for a personalized wooden furniture and interior designing consultation for your home or project."),

        # Footer
        ('An AI agent that works inside your design tools', 'Aiswarya Industries — Dealers in Wooden Furniture & Interior Designing, Nilambur'),
        ('Want to see more cool websites like this?', 'Looking to furnish your home with custom wooden interiors?'),
        ('Sign up for occasional updates from Bearplus.',
         'Contact Janardhanan: +91 9447 631 731 or Jithesh: +91 9656 663 063 for custom commissions.'),
        ('Subscribe', 'Contact Atelier'),
        ('Company', 'Aiswarya Industries'),
        ('Address', 'Workshop & Location'),
        ('60 Martin Pl, Sydney,', 'Mannuppadam, Eranhimangad P.O.,'),
        ('NSW 2000, Australia', 'Nilambur, Malappuram, Kerala - 679329'),
        ('Direction', 'Janardhanan: +91 9447 631 731'),
        ('New business', 'Key Contacts'),
        ('business@bear.plus', 'Janardhanan: +91 9447 631 731'),
        ('General inquiries', 'Jithesh / Office'),
        ('hello@heronaiapp.com', '+91 9656 663 063 | +91 9961 858 798'),
        ('©2026 HERON AI. All rights reserved.', '©2026 AISWARYA INDUSTRIES. All rights reserved. Dealers in Wooden Furniture & Interior Designing, Nilambur.'),
        ('Bearplus', 'Aiswarya Industries, Nilambur'),
        ('Heron AI', 'Aiswarya Industries'),
        ('HERON AI', 'AISWARYA INDUSTRIES'),
        ('Heron', 'Aiswarya Industries'),
    ]

    # Replace safely in DOM visible text nodes
    for text_node in list(soup.find_all(string=True)):
        if isinstance(text_node, NavigableString):
            if text_node.parent and text_node.parent.name in ['script', 'style', 'noscript', 'meta', 'title']:
                continue
            orig_text = str(text_node)
            new_text = orig_text
            for old, new in text_replacements:
                if old in new_text:
                    new_text = new_text.replace(old, new)
            if new_text != orig_text:
                text_node.replace_with(NavigableString(new_text))

    # 12. Programmatic SVG Color Modernization (harmonize all SVG paths with the new palette)
    for el in soup.find_all(True):
        for attr in ['stroke', 'fill', 'color']:
            val = el.get(attr)
            if val:
                v_up = val.upper()
                if v_up in ['#137547', '#FA3600', '#F15534', '#E15C46', '#FF3B00', '#FA3600B8'] or '250, 54, 0' in val or '241, 85, 52' in val:
                    el[attr] = '#fa3600'
                elif v_up in ['#282828', '#11221B']:
                    el[attr] = '#1c1815'
                elif v_up in ['#B3B3AF', '#B8C7BF']:
                    el[attr] = '#c8bfb2'
                elif v_up in ['#72726F', '#4A6358', '#3D544A']:
                    el[attr] = '#685d53'

    html_str = str(soup)

    # 13. CSS Injections & Preloader Skip Script
    head_injections = """
    <script>
      // Immediately register that the page is loaded so Lenis and Webflow unlock scrolling immediately
      try { sessionStorage.setItem("isLoaded", "true"); } catch(e){}
    </script>
    <style>
      /* === PALETTE TRANSFORMATION: Heritage Vibrant Orange & Warm Architectural Sandstone/Linen === */
      :root, body {
        --content--brand: #fa3600 !important;        /* Signature Vibrant Heritage Orange */
        --content--primary: #1c1815 !important;      /* Deep Architectural Charcoal Ink */
        --content--secondary: #483f36 !important;    /* Warm Muted Slate Charcoal */
        --content--terriary: rgba(28, 24, 21, 0.68) !important;
        --content--border: #c8bfb2 !important;       /* Architectural Drafting Border */
        --content--white: #dfd7c7 !important;        /* Warm Architectural Sandstone Card Surface (Replaces White) */
        --content--disable: #b8af9f !important;
        --content--surface: #685d53 !important;
        --content--granite-gray: #4d443c !important;
      }

      home-hero-wrap, home-intro-wrap, .home-rr-wrap { display: block !important; }
      /* Global canvas and typography color mapping: Replaces all white background colors with Warm Sandstone */
      html, body, .body, .body-inner, .main-inner, .main-content {
        background-color: #e9e2d4 !important;
        color: #1c1815 !important;
      }

      /* Cursor dot: vibrant orange */
      .cursor-inner {
        background-color: #fa3600 !important;
      }

      /* Primary buttons & highlight elements: vibrant orange */
      .btn.btn-primary, .home-hero-btn, .btn-fill-bg {
        background-color: #fa3600 !important;
        border-color: #fa3600 !important;
        color: #ffffff !important;
      }
      .btn.btn-outline:hover {
        border-color: #fa3600 !important;
        color: #fa3600 !important;
      }

      /* Grid lines and structural borders */
      .line, .bg-border, .bg-border-plus, .bg-border-plus svg path {
        border-color: #c8bfb2 !important;
        color: #c8bfb2 !important;
      }
      .line-brand {
        border-color: #fa3600 !important;
      }

      /* Card panels and global background containers: No white backgrounds */
      .bg-global {
        border-color: #c8bfb2 !important;
        background-color: #dfd7c7 !important;
      }
      .footer-img-inner.bg-global {
        background-color: transparent !important;
      }

      /* Form inputs and controls */
      .w-input, .w-select, .footer-form-input {
        background-color: #dfd7c7 !important;
        color: #1c1815 !important;
        border-color: #c8bfb2 !important;
      }

      /* Hardcoded SVG orange strokes and fills */
      svg [stroke="#137547"], svg [stroke="#FA3600"], svg [stroke="#fa3600"], svg [stroke="#F15534"], svg [stroke="#f15534"], svg [stroke="#E15C46"], svg [stroke="#e15c46"] {
        stroke: #fa3600 !important;
      }
      svg [fill="#137547"], svg [fill="#FA3600"], svg [fill="#fa3600"], svg [fill="#F15534"], svg [fill="#f15534"], svg [fill="#E15C46"], svg [fill="#e15c46"] {
        fill: #fa3600 !important;
      }

      /* Architectural imagery color harmony: restore original vibrant warm illustrations */
      img[src*="solution"], img[src*="cta"], .cta-sketch, .cta-img-wrap img {
        filter: none !important;
      }

      /* Completely remove Awwwards side ribbon */
      .awwwards, [class*="awwwards"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
        height: 0 !important;
        width: 0 !important;
        overflow: hidden !important;
      }

      /* Quick non-blocking preloader: fades out in 0.4s and never traps scroll */
      .loading {
        opacity: 0 !important;
        pointer-events: none !important;
        display: none !important;
        visibility: hidden !important;
      }

      /* Ensure proper header logo visibility */
      .header-logo-inner {
        overflow: visible !important;
        width: auto !important;
        display: flex !important;
        align-items: center !important;
      }
      .header-logo-item.item-txt {
        width: auto !important;
        max-width: 280px !important;
        opacity: 1 !important;
        transform: none !important;
      }
      
      /* Completely remove problems section */
      home-problem-wrap, .home-problem-wrap, .home-problem {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        max-height: 0 !important;
        overflow: hidden !important;
        pointer-events: none !important;
        margin: 0 !important;
        padding: 0 !important;
      }

      /* Remove the 2 floating title texts in Blueprint/Map */
      .home-intel-inner, .home-intel-item {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        max-height: 0 !important;
        overflow: hidden !important;
        pointer-events: none !important;
        opacity: 0 !important;
      }

      /* Compact Blueprint section: perfectly balanced side-by-side layout with zero empty scrolling */
      .home-map-main {
        height: 105vh !important;
        min-height: 720px !important;
      }
      .home-map-inner {
        display: flex !important;
        height: 100% !important;
        align-items: center !important;
      }
      .home-map-main-stick {
        position: relative !important;
        height: 100% !important;
        top: 0 !important;
        flex: 1 1 56% !important;
        width: 56% !important;
      }
      .home-map-content-wrap {
        position: relative !important;
        flex: 1 1 44% !important;
        width: 44% !important;
        max-width: 48vw !important;
        height: 100% !important;
        opacity: 1 !important;
        visibility: visible !important;
        display: flex !important;
        transform: none !important;
        overflow: visible !important;
      }
      .home-map-content {
        width: 100% !important;
        opacity: 1 !important;
        visibility: visible !important;
        display: flex !important;
        transform: none !important;
      }
      .home-map-content-wrap *, .home-map-content *, .home-map-content-title *, .home-map-content-sub * {
        opacity: 1 !important;
        visibility: visible !important;
      }
      .home-map-content-wrap .bp-line > div,
      .home-map-content-title .bp-line > div,
      .home-map-content-sub div,
      .home-map-content-sub .txt,
      .home-map-content-item-title .txt {
        transform: none !important;
        translate: none !important;
        opacity: 1 !important;
        visibility: visible !important;
      }
      .home-map-intro {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
      }
      .home-map-main-img {
        opacity: 1 !important;
        pointer-events: auto !important;
        display: block !important;
      }
      .home-map-main-img-inner {
        opacity: 1 !important;
        visibility: visible !important;
      }
      .home-map-main-img .home-map-img-svg path {
        opacity: 1 !important;
        transform: none !important;
      }

      @media screen and (max-width: 991px) {
        .home-map-main {
          height: auto !important;
          min-height: 100vh !important;
        }
        .home-map-inner {
          flex-direction: column !important;
          height: auto !important;
        }
        .home-map-main-stick {
          width: 100% !important;
          height: 60vh !important;
          min-height: 380px !important;
        }
        .home-map-content-wrap {
          width: 100% !important;
          max-width: 100% !important;
          height: auto !important;
        }
      }

      /* Prevent any unstyled cookie elements */
      .cookie, .cookie-banner, [data-cookie-banner], .cookie-banner-reject, .cookie-banner-accept {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
        height: 0 !important;
        width: 0 !important;
        overflow: hidden !important;
      }

      /* Hero title & text visibility guarantee */
      .home-hero-title,
      .home-hero-title *,
      .home-hero-title .bp-line > div,
      .home-hero-title div,
      .home-hero-title h1,
      .home-hero-sub,
      .home-hero-sub *,
      .home-hero-sub div,
      .home-hero-sub .txt,
      .home-hero-sub a,
      .home-hero-btn {
        visibility: visible !important;
        opacity: 1 !important;
        transform: none !important;
        translate: none !important;
      }

      /* === PIXEL-BY-PIXEL SWIPE DOWN REVEAL SYSTEM === */
      .pixel-wipe-wrap {
        width: 100% !important;
        height: 100% !important;
        position: absolute !important;
        inset: 0 !important;
        overflow: hidden !important;
        mix-blend-mode: normal !important;
      }
      .pixel-wipe-base,
      .pixel-wipe-reveal {
        position: absolute !important;
        inset: 0 !important;
        width: 100% !important;
        height: 100% !important;
        mix-blend-mode: normal !important;
      }
      .pixel-wipe-base {
        z-index: 1 !important;
      }
      .pixel-wipe-reveal {
        z-index: 2 !important;
      }
      .pixel-wipe-base img {
        width: 100% !important;
        height: 100% !important;
        object-fit: cover !important;
        object-position: center !important;
        display: block !important;
      }
      .pixel-reveal-img {
        width: 100% !important;
        height: 100% !important;
        object-fit: cover !important;
        object-position: center !important;
        display: block !important;
        -webkit-mask-image: url("/images/pixel-wipe-down.svg") !important;
        mask-image: url("/images/pixel-wipe-down.svg") !important;
        -webkit-mask-size: 100% 3000% !important;
        mask-size: 100% 3000% !important;
        -webkit-mask-repeat: no-repeat !important;
        mask-repeat: no-repeat !important;
        -webkit-mask-position: 0% 0%;
        mask-position: 0% 0%;
        will-change: mask-position, -webkit-mask-position;
      }

      /* === HERO SECTION 3-IMAGE ARCHITECTURAL TRIPTYCH === */
      .home-hero-ruler {
        pointer-events: none !important;
      }
      .home-hero-img-wrap {
        position: relative !important;
        overflow: hidden !important;
      }
      .home-hero-img {
        position: relative !important;
        width: 100% !important;
        height: 100% !important;
        mix-blend-mode: normal !important;
      }
      .home-hero-img-inner {
        position: absolute !important;
        inset: 0 !important;
        width: 100% !important;
        height: 100% !important;
        mix-blend-mode: normal !important;
        pointer-events: auto !important;
        display: block !important;
        z-index: 1 !important;
      }
      .home-hero-img-grid {
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
      }
      .home-hero-img-col:last-child {
        border-right: none !important;
      }
      .home-hero-col-badge {
        position: absolute !important;
        bottom: 1.4rem !important;
        left: 1.4rem !important;
        z-index: 10 !important;
        pointer-events: none !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 0.6rem !important;
        background: rgba(235, 228, 219, 0.92) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        padding: 0.4rem 0.8rem !important;
        border: var(--size--border) solid var(--content--border) !important;
        border-radius: 2px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
      }
      .home-hero-col-num {
        font-family: 'Geistmono', monospace !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        color: var(--content--brand) !important;
        letter-spacing: 0.04em !important;
      }
      .home-hero-col-name {
        font-family: 'Geistmono', monospace !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: var(--content--primary) !important;
        letter-spacing: 0.06em !important;
        text-transform: uppercase !important;
      }
      .home-hero-img-interact-wrap {
        z-index: 5 !important;
        pointer-events: none !important;
      }
      .bg-border {
        z-index: 4 !important;
        pointer-events: none !important;
      }
      @media screen and (max-width: 767px) {
        .home-hero-img-grid {
          grid-template-columns: 1fr !important;
        }
        .home-hero-img-col:not(:first-child) {
          display: none !important;
        }
      }

      /* === ARCHITECTURAL SKETCH & INK MASK PIXEL REVEAL STYLES === */
      .home-why-item.grid {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: space-between !important;
        gap: 3.2rem !important;
        min-height: 440px !important;
        margin-bottom: 6rem !important;
        position: relative !important;
        width: 100% !important;
      }
      .home-why-item:nth-child(even) {
        flex-direction: row-reverse !important;
      }
      .home-why-item-img {
        flex: 1 1 55% !important;
        max-width: 58% !important;
        position: relative !important;
        aspect-ratio: 16 / 11 !important;
        min-height: 380px !important;
        display: block !important;
        overflow: hidden !important;
        mix-blend-mode: normal !important;
        border: var(--size--border) solid var(--content--border) !important;
        border-radius: 4px !important;
        visibility: visible !important;
        opacity: 1 !important;
      }
      .home-why-item-sticky {
        flex: 1 1 40% !important;
        max-width: 42% !important;
        position: relative !important;
        top: auto !important;
        left: auto !important;
        right: auto !important;
        width: auto !important;
        opacity: 1 !important;
        display: flex !important;
        pointer-events: auto !important;
        visibility: visible !important;
      }
      .home-why-item-sticky-content {
        background-color: var(--content--white) !important;
        border: var(--size--border) solid var(--content--border) !important;
        padding: 2.4rem !important;
        width: 100% !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06) !important;
        border-radius: 4px !important;
        opacity: 1 !important;
        pointer-events: auto !important;
        visibility: visible !important;
      }
      .home-why-sticky-item-title .heading {
        color: var(--content--primary) !important;
        font-size: 2rem !important;
        line-height: 1.2 !important;
        margin-bottom: 0.8rem !important;
        font-weight: 700 !important;
      }
      .home-why-sticky-item-sub .txt {
        color: var(--content--secondary) !important;
        font-size: 1.1rem !important;
        line-height: 1.6 !important;
      }
      .home-why-item-img-inner {
        position: absolute !important;
        inset: 0% !important;
        width: 100% !important;
        height: 100% !important;
        opacity: 1 !important;
        visibility: visible !important;
        display: block !important;
        mix-blend-mode: normal !important;
        overflow: hidden !important;
        pointer-events: auto !important;
      }
      .home-why-item-img-inner .ink-mask {
        width: 100% !important;
        height: 100% !important;
        position: absolute !important;
        inset: 0% !important;
      }
      .home-why-item-img-inner .ink-mask-img.main img {
        width: 100% !important;
        height: 100% !important;
        object-fit: cover !important;
        display: block !important;
      }
      .home-why-item-img-inner .ink-mask-img.sub svg {
        width: 100% !important;
        height: 100% !important;
        display: block !important;
      }
      .home-why-item-img-box,
      .home-why-item-img-point,
      .home-why-item-img-line,
      .home-why-item-card,
      .home-why-item-img-deco,
      .home-why-item-img-deco-main {
        display: none !important;
        opacity: 0 !important;
        visibility: hidden !important;
        pointer-events: none !important;
      }
      .home-platform-img-item,
      .home-platform-img-item-inner,
      .home-intro-img,
      .cta-wrap,
      .home-usecase-img-item {
        mix-blend-mode: normal !important;
      }
    
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

      /* === ROLLS-ROYCE FULL-SCREEN 3D EXPLODED ARCHITECTURE (CANVAS ENGINE) === */
      .home-rr-wrap {
        display: block !important;
        width: 100% !important;
        height: 100vh !important;
        max-width: 100vw !important;
        position: relative !important;
        background: #0d0c0a !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
        border-top: var(--size--border) solid rgba(255, 255, 255, 0.12) !important;
        border-bottom: var(--size--border) solid rgba(255, 255, 255, 0.12) !important;
      }
      .rr-fullscreen-stage {
        position: relative !important;
        width: 100% !important;
        height: 100% !important;
        overflow: hidden !important;
        background: #0d0c0a !important;
      }
      .rr-fullscreen-canvas {
        position: absolute !important;
        inset: 0 !important;
        width: 100% !important;
        height: 100% !important;
        display: block !important;
        pointer-events: none !important;
        z-index: 1 !important;
      }
      .rr-cinematic-vignette {
        position: absolute !important;
        inset: 0 !important;
        background: 
          radial-gradient(circle at 65% 50%, transparent 35%, rgba(13, 12, 10, 0.72) 88%),
          linear-gradient(to top, rgba(13, 12, 10, 0.88) 0%, transparent 22%),
          linear-gradient(to bottom, rgba(13, 12, 10, 0.88) 0%, transparent 22%) !important;
        pointer-events: none !important;
        z-index: 2 !important;
      }
      .rr-cad-grid {
        position: absolute !important;
        inset: 0 !important;
        background-size: 60px 60px !important;
        background-image: 
          linear-gradient(to right, rgba(255, 255, 255, 0.035) 1px, transparent 1px),
          linear-gradient(to bottom, rgba(255, 255, 255, 0.035) 1px, transparent 1px) !important;
        pointer-events: none !important;
        z-index: 2 !important;
      }
      .rr-cad-mark {
        position: absolute !important;
        color: rgba(250, 54, 0, 0.6) !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 16px !important;
        font-weight: 300 !important;
        line-height: 1 !important;
        z-index: 3 !important;
        pointer-events: none !important;
      }
      .rr-cad-mark.tl { top: 28px; left: 28px; }
      .rr-cad-mark.tr { top: 28px; right: 28px; }
      .rr-cad-mark.bl { bottom: 28px; left: 28px; }
      .rr-cad-mark.br { bottom: 28px; right: 28px; }

      .rr-watermark {
        position: absolute !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 11px !important;
        letter-spacing: 0.14em !important;
        color: rgba(255, 255, 255, 0.85) !important;
        background: rgba(18, 16, 14, 0.5) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        border-radius: 4px !important;
        padding: 5px 12px !important;
        text-shadow: 0 1px 4px rgba(0, 0, 0, 0.8) !important;
        text-transform: uppercase !important;
        font-weight: 600 !important;
        z-index: 4 !important;
        pointer-events: none !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 8px !important;
      }
      .rr-watermark.top-left { top: 28px; left: 40px; }
      .rr-watermark.top-right { top: 28px; right: 40px; }
      .rr-watermark.bottom-right { bottom: 28px; right: 40px; }
      .rr-dot-pulse {
        width: 7px !important;
        height: 7px !important;
        border-radius: 50% !important;
        background: var(--content--brand) !important;
        box-shadow: 0 0 8px var(--content--brand) !important;
        animation: heroPulse 1.8s infinite !important;
      }

      /* Pure Typography Floating Narrative - No Cards, Full Car Visibility */
      .rr-act-card {
        position: absolute !important;
        top: 50% !important;
        left: 80px !important;
        transform: translateY(-50%) !important;
        max-width: 580px !important;
        width: calc(100% - 160px) !important;
        z-index: 5 !important;
        background: transparent !important;
        backdrop-filter: none !important;
        -webkit-backdrop-filter: none !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 0 !important;
        box-shadow: none !important;
        color: #ffffff !important;
        pointer-events: auto !important;
        transition: opacity 0.35s ease, transform 0.35s ease !important;
      }
      .rr-act-card.right {
        left: auto !important;
        right: 80px !important;
      }
      .rr-act-tag {
        display: inline-flex !important;
        align-items: center !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        letter-spacing: 0.18em !important;
        color: #fa3600 !important;
        text-transform: uppercase !important;
        margin-bottom: 16px !important;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.9) !important;
      }
      .rr-act-title {
        font-family: 'BT Grotesk', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-size: 44px !important;
        font-weight: 700 !important;
        line-height: 1.08 !important;
        letter-spacing: -0.02em !important;
        text-transform: uppercase !important;
        color: #ffffff !important;
        text-shadow: 0 4px 28px rgba(0, 0, 0, 0.95), 0 2px 8px rgba(0, 0, 0, 0.95) !important;
        margin: 0 0 18px 0 !important;
      }
      .rr-act-desc {
        font-family: 'BT Grotesk', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-size: 15px !important;
        line-height: 1.7 !important;
        font-weight: 400 !important;
        color: rgba(255, 255, 255, 0.92) !important;
        text-shadow: 0 2px 14px rgba(0, 0, 0, 0.95), 0 1px 4px rgba(0, 0, 0, 0.95) !important;
        margin: 0 0 26px 0 !important;
        max-width: 540px !important;
      }
      .rr-act-desc strong {
        color: #ffffff !important;
        font-weight: 700 !important;
      }

      /* Scroll Indicator in Act 1 */
      .rr-scroll-indicator {
        display: inline-flex !important;
        align-items: center !important;
        gap: 12px !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        letter-spacing: 0.14em !important;
        color: rgba(255, 255, 255, 0.8) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.22) !important;
        padding-top: 20px !important;
        width: 100% !important;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.9) !important;
      }
      .rr-scroll-mouse {
        width: 14px !important;
        height: 22px !important;
        border: 1.5px solid #fa3600 !important;
        border-radius: 999px !important;
        position: relative !important;
      }
      .rr-scroll-wheel {
        position: absolute !important;
        top: 3px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 2px !important;
        height: 4px !important;
        background: #fa3600 !important;
        border-radius: 1px !important;
        animation: mouseScroll 1.4s infinite !important;
      }

      /* Minimalist Text Metrics in Act 2 - No Card */
      .rr-metric-row {
        display: flex !important;
        gap: 40px !important;
        border-top: 1px solid rgba(255, 255, 255, 0.22) !important;
        padding-top: 20px !important;
      }
      .rr-metric-pill {
        flex: none !important;
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 0 !important;
        box-shadow: none !important;
      }
      .p-num {
        font-family: 'BT Grotesk', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-size: 32px !important;
        font-weight: 800 !important;
        color: #fa3600 !important;
        line-height: 1.1 !important;
        text-shadow: 0 2px 16px rgba(0, 0, 0, 0.95) !important;
      }
      .p-lbl {
        font-family: 'Geistmono', monospace !important;
        font-size: 11px !important;
        letter-spacing: 0.12em !important;
        color: rgba(255, 255, 255, 0.85) !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        margin-top: 4px !important;
        text-shadow: 0 1px 6px rgba(0, 0, 0, 0.9) !important;
      }

      /* Minimalist Text Metrics in Act 3 - No Card */
      .rr-badge-row {
        display: flex !important;
        gap: 36px !important;
        border-top: 1px solid rgba(255, 255, 255, 0.22) !important;
        padding-top: 20px !important;
      }
      .rr-spec-item {
        flex: none !important;
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 0 !important;
        text-align: left !important;
        box-shadow: none !important;
      }
      .rr-spec-item:hover {
        border-color: transparent !important;
        transform: none !important;
      }
      .rr-spec-num {
        font-family: 'BT Grotesk', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-size: 30px !important;
        font-weight: 800 !important;
        color: #fa3600 !important;
        line-height: 1.1 !important;
        text-shadow: 0 2px 16px rgba(0, 0, 0, 0.95) !important;
      }
      .rr-spec-label {
        font-family: 'Geistmono', monospace !important;
        font-size: 10px !important;
        letter-spacing: 0.12em !important;
        color: rgba(255, 255, 255, 0.85) !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        margin-top: 4px !important;
        text-shadow: 0 1px 6px rgba(0, 0, 0, 0.9) !important;
      }

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

      /* 7. Hero 3D Spatial Tilt, Laser Beam & Wood Sheen */
      .home-hero-img-col {
        transform-style: preserve-3d !important;
        will-change: transform !important;
        transition: box-shadow 0.35s ease !important;
      }
      .home-hero-img-col:hover {
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.15) !important;
      }
      .pixel-wipe-wrap {
        position: relative !important;
        overflow: hidden !important;
      }
      .pixel-wipe-laser-beam {
        position: absolute !important;
        left: 0 !important;
        right: 0 !important;
        height: 2px !important;
        background: #fa3600 !important;
        box-shadow: 0 0 12px #fa3600, 0 0 4px #ffffff !important;
        z-index: 10 !important;
        pointer-events: none !important;
        opacity: 0;
        top: 0;
      }
      .hero-wood-sheen {
        position: absolute !important;
        top: -60% !important;
        left: -120% !important;
        width: 60% !important;
        height: 220% !important;
        background: linear-gradient(
          105deg,
          transparent 30%,
          rgba(255, 255, 255, 0.38) 50%,
          transparent 70%
        ) !important;
        transform: rotate(25deg) !important;
        pointer-events: none !important;
        z-index: 7 !important;
        opacity: 0;
      }

      /* 8. Rolls-Royce Holographic Cursor Reticle */
      .rr-cursor-reticle {
        position: absolute !important;
        width: 44px !important;
        height: 44px !important;
        border: 1px dashed rgba(250, 54, 0, 0.75) !important;
        border-radius: 50% !important;
        pointer-events: none !important;
        z-index: 6 !important;
        transform: translate(-50%, -50%) !important;
        display: none;
        transition: border-color 0.2s ease !important;
      }
      .rr-cursor-reticle::before {
        content: '' !important;
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        width: 4px !important;
        height: 4px !important;
        background: #fa3600 !important;
        border-radius: 50% !important;
        transform: translate(-50%, -50%) !important;
        box-shadow: 0 0 8px #fa3600 !important;
      }
      .rr-reticle-hud {
        position: absolute !important;
        top: 48px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        white-space: nowrap !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 9px !important;
        letter-spacing: 0.12em !important;
        color: #fa3600 !important;
        background: rgba(18, 16, 14, 0.85) !important;
        padding: 2px 7px !important;
        border-radius: 3px !important;
        border: 1px solid rgba(250, 54, 0, 0.4) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.4) !important;
      }

      /* 9. Caliper Measurement Real-Time Tooltip */
      .intro-caliper-measure-hud {
        position: absolute !important;
        top: -34px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        background: var(--content--primary) !important;
        color: #fff !important;
        border: 1px solid var(--content--brand) !important;
        padding: 3px 9px !important;
        border-radius: 4px !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 9px !important;
        letter-spacing: 0.1em !important;
        white-space: nowrap !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
        pointer-events: none !important;
      }

      /* 10. 3D Floating Coin */
      #giCoin {
        will-change: transform !important;
        transform-style: preserve-3d !important;
      }

      /* 11. Lower Side Images Advanced Pixel Reveal & Spatial 3D Systems */
      .why-side-img-card,
      .platform-side-img-card {
        position: relative !important;
        width: 100% !important;
        height: 100% !important;
        overflow: hidden !important;
        transform-style: preserve-3d !important;
        will-change: transform !important;
        transition: box-shadow 0.35s ease !important;
        cursor: crosshair !important;
        border-radius: 4px !important;
      }
      .why-side-img-card:hover,
      .platform-side-img-card:hover {
        box-shadow: 0 16px 44px rgba(0, 0, 0, 0.16) !important;
      }
      .pixel-matrix-grid {
        position: absolute !important;
        inset: 0 !important;
        pointer-events: none !important;
        z-index: 8 !important;
        opacity: 0.16 !important;
        background-size: 20px 20px !important;
        background-image: 
          linear-gradient(to right, rgba(250, 54, 0, 0.18) 1px, transparent 1px),
          linear-gradient(to bottom, rgba(250, 54, 0, 0.18) 1px, transparent 1px) !important;
        mix-blend-mode: overlay !important;
        transition: opacity 0.3s ease !important;
      }
      .why-col-badge,
      .platform-col-badge {
        position: absolute !important;
        bottom: 1.2rem !important;
        left: 1.2rem !important;
        z-index: 12 !important;
        pointer-events: none !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 0.6rem !important;
        background: rgba(235, 228, 219, 0.94) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        padding: 0.35rem 0.75rem !important;
        border: var(--size--border) solid var(--content--border) !important;
        border-radius: 2px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
      }
      .why-col-num,
      .platform-col-num {
        font-family: 'Geistmono', monospace !important;
        font-size: 0.9rem !important;
        font-weight: 700 !important;
        color: var(--content--brand) !important;
        letter-spacing: 0.04em !important;
      }
      .why-col-name,
      .platform-col-name {
        font-family: 'Geistmono', monospace !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        color: var(--content--primary) !important;
        letter-spacing: 0.06em !important;
        text-transform: uppercase !important;
      }
      .why-rewipe-btn,
      .platform-rewipe-btn {
        position: absolute !important;
        top: 1.2rem !important;
        right: 1.2rem !important;
        z-index: 15 !important;
        background: rgba(28, 24, 21, 0.88) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(250, 54, 0, 0.6) !important;
        color: #ffd166 !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.08em !important;
        padding: 0.38rem 0.78rem !important;
        border-radius: 3px !important;
        cursor: pointer !important;
        transition: all 0.25s ease !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 0.35rem !important;
      }
      .why-rewipe-btn:hover,
      .platform-rewipe-btn:hover {
        background: #fa3600 !important;
        color: #ffffff !important;
        transform: scale(1.04) !important;
        box-shadow: 0 4px 14px rgba(250, 54, 0, 0.4) !important;
      }
      .why-cad-hud,
      .platform-cad-hud {
        position: absolute !important;
        bottom: 1.2rem !important;
        right: 1.2rem !important;
        z-index: 12 !important;
        pointer-events: none !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 0.72rem !important;
        color: var(--content--secondary) !important;
        background: rgba(235, 228, 219, 0.88) !important;
        backdrop-filter: blur(6px) !important;
        -webkit-backdrop-filter: blur(6px) !important;
        padding: 0.35rem 0.65rem !important;
        border: var(--size--border) solid var(--content--border) !important;
        border-radius: 2px !important;
        line-height: 1.35 !important;
        text-align: right !important;
      }
      .why-cad-hud strong,
      .platform-cad-hud strong {
        color: var(--content--primary) !important;
      }
      .why-cad-hud .cad-corner-marks,
      .platform-cad-hud .cad-corner-marks {
        color: var(--content--brand) !important;
        font-weight: 700 !important;
        margin-top: 0.2rem !important;
      }

    </style>

    </style>
    <script>
      function unlockPage() {
        const loading = document.querySelector('.loading');
        if (loading) {
          loading.style.display = 'none';
          loading.style.opacity = '0';
          loading.style.pointerEvents = 'none';
        }
        
        document.querySelectorAll('.home-hero-title [style*="translate"], .home-hero-title .bp-line > div, .home-hero-title div, .home-hero-sub [style*="translate"], .home-hero-sub div, .home-hero-sub a, .home-map-content-wrap [style*="translate"], .home-map-content-wrap .bp-line > div, .home-map-content-wrap div, .home-map-content-title div, .home-map-content-sub div').forEach(el => {
          el.style.transform = 'translate(0%, 0%)';
          el.style.opacity = '1';
          el.style.visibility = 'visible';
        });

        // Ensure Lenis scroll is active and refreshed
        if (window.ScrollTrigger) {
          window.ScrollTrigger.refresh();
        }
      }

      // Architectural Blueprint Sketch to Real Teak Photo - Organic Ink/Displacement Pixel Reveal on Scroll
      // === 1. ACOUSTIC WOOD TAP (WEB AUDIO SYNTHESIZER) ===
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
        const laser = col.querySelector('.pixel-wipe-laser-beam');
        const sheen = col.querySelector('.hero-wood-sheen');
        const hud = col.querySelector('.hero-cad-hud');

        if (revealImg) {
          gsap.fromTo(revealImg,
            { maskPosition: '0% 0%', webkitMaskPosition: '0% 0%' },
            { maskPosition: '0% 100%', webkitMaskPosition: '0% 100%', duration: 1.15, ease: 'steps(29)', overwrite: 'auto' }
          );
        }
        if (laser) {
          gsap.fromTo(laser,
            { top: '0%', opacity: 1 },
            { top: '100%', opacity: 0, duration: 1.15, ease: 'steps(29)' }
          );
        }
        if (sheen) {
          gsap.fromTo(sheen,
            { left: '-120%', opacity: 0 },
            { left: '200%', opacity: 0.65, duration: 0.95, delay: 0.35, ease: 'power2.inOut' }
          );
        }
        if (hud) {
          gsap.fromTo(hud, { filter: 'brightness(1.6)' }, { filter: 'brightness(1)', duration: 0.6 });
        }
      }

      // === 2B. WHY US LOWER SIDE IMAGES RE-WIPE HANDLER ===
      function rewipeWhyStep(idx, e) {
        if (e) e.stopPropagation();
        playWoodTap(540 + idx * 35);
        const card = document.getElementById(`whyCard${idx}`);
        if (!card) return;
        const revealImg = card.querySelector('.pixel-reveal-img');
        const laser = card.querySelector('.pixel-wipe-laser-beam');
        const sheen = card.querySelector('.hero-wood-sheen');
        const grid = card.querySelector('.pixel-matrix-grid');
        const hud = card.querySelector('.why-cad-hud');

        if (revealImg) {
          gsap.fromTo(revealImg,
            { maskPosition: '0% 0%', webkitMaskPosition: '0% 0%' },
            { maskPosition: '0% 100%', webkitMaskPosition: '0% 100%', duration: 1.2, ease: 'steps(29)', overwrite: 'auto' }
          );
        }
        if (laser) {
          gsap.fromTo(laser,
            { top: '0%', opacity: 1 },
            { top: '100%', opacity: 0, duration: 1.2, ease: 'steps(29)', overwrite: 'auto' }
          );
        }
        if (grid) {
          gsap.fromTo(grid,
            { opacity: 0.45 },
            { opacity: 0.16, duration: 1.2, ease: 'power2.out', overwrite: 'auto' }
          );
        }
        if (sheen) {
          gsap.fromTo(sheen,
            { left: '-120%', opacity: 0 },
            { left: '200%', opacity: 0.72, duration: 0.95, delay: 0.35, ease: 'power2.inOut', overwrite: 'auto' }
          );
        }
        if (hud) {
          gsap.fromTo(hud, { filter: 'brightness(1.5)' }, { filter: 'brightness(1)', duration: 0.6 });
        }
      }

      // === 2C. PLATFORM LOWER SIDE IMAGES RE-WIPE HANDLER ===
      function rewipePlatItem(idx, e) {
        if (e) e.stopPropagation();
        playWoodTap(560 + idx * 40);
        const card = document.getElementById(`platCard${idx}`);
        if (!card) return;
        const revealImg = card.querySelector('.pixel-reveal-img');
        const laser = card.querySelector('.pixel-wipe-laser-beam');
        const sheen = card.querySelector('.hero-wood-sheen');
        const grid = card.querySelector('.pixel-matrix-grid');
        const hud = card.querySelector('.platform-cad-hud');

        if (revealImg) {
          gsap.fromTo(revealImg,
            { maskPosition: '0% 0%', webkitMaskPosition: '0% 0%' },
            { maskPosition: '0% 100%', webkitMaskPosition: '0% 100%', duration: 1.2, ease: 'steps(29)', overwrite: 'auto' }
          );
        }
        if (laser) {
          gsap.fromTo(laser,
            { top: '0%', opacity: 1 },
            { top: '100%', opacity: 0, duration: 1.2, ease: 'steps(29)', overwrite: 'auto' }
          );
        }
        if (grid) {
          gsap.fromTo(grid,
            { opacity: 0.45 },
            { opacity: 0.16, duration: 1.2, ease: 'power2.out', overwrite: 'auto' }
          );
        }
        if (sheen) {
          gsap.fromTo(sheen,
            { left: '-120%', opacity: 0 },
            { left: '200%', opacity: 0.72, duration: 0.95, delay: 0.35, ease: 'power2.inOut', overwrite: 'auto' }
          );
        }
        if (hud) {
          gsap.fromTo(hud, { filter: 'brightness(1.5)' }, { filter: 'brightness(1)', duration: 0.6 });
        }
      }

      // === 3. CHRONOS PATINA TIMELINE ENGINE (ADVANCED ENGINE) ===
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

      // === ROLLS-ROYCE FULL-SCREEN 3D EXPLODED CANVAS ENGINE ===
      function initRollsRoyceCanvasScrub() {
        const rrWrap = document.getElementById('rrRollsRoyceSection');
        const canvas = document.getElementById('rrCanvas');
        if (!rrWrap || !canvas || typeof ScrollTrigger === 'undefined') return;

        const ctx = canvas.getContext('2d', { alpha: false });
        const frameCount = 240;
        const frameUrl = (idx) => `/rr_frames_webp/f_${String(idx + 1).padStart(4, '0')}.webp`;

        let lastRenderedIndex = 0;
        const images = [];

        function drawImageCover(img) {
          if (!img || !img.complete) return;
          const cw = canvas.width;
          const ch = canvas.height;
          const iw = img.naturalWidth || 1920;
          const ih = img.naturalHeight || 1080;
          const ratio = Math.max(cw / iw, ch / ih);
          const nw = iw * ratio;
          const nh = ih * ratio;
          const cx = (cw - nw) / 2;
          const cy = (ch - nh) / 2;
          ctx.drawImage(img, cx, cy, nw, nh);
        }

        function resizeCanvas() {
          const rect = rrWrap.getBoundingClientRect();
          const dpr = Math.min(window.devicePixelRatio || 1, 2);
          canvas.width = Math.round((rect.width || window.innerWidth) * dpr);
          canvas.height = Math.round((rect.height || window.innerHeight) * dpr);
          drawFrame(lastRenderedIndex);
        }

        function drawFrame(idx) {
          lastRenderedIndex = Math.min(frameCount - 1, Math.max(0, idx));
          const targetImg = images[lastRenderedIndex];
          if (targetImg && targetImg.complete) {
            drawImageCover(targetImg);
          } else if (targetImg) {
            targetImg.onload = () => {
              if (lastRenderedIndex === idx) drawImageCover(targetImg);
            };
          }
        }

        // Preload frames progressively
        for (let i = 0; i < frameCount; i++) {
          const img = new Image();
          if (i === 0) {
            img.src = frameUrl(0);
            img.onload = () => {
              resizeCanvas();
              drawImageCover(img);
            };
          } else {
            img.src = frameUrl(i);
          }
          images.push(img);
        }

        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);

        const act1 = document.getElementById('rrAct1');
        const act2 = document.getElementById('rrAct2');
        const act3 = document.getElementById('rrAct3');
        const scrollerEl = document.querySelector('.main-inner') ? '.main-inner' : window;

        const wmTopLeft = rrWrap.querySelector('.rr-watermark.top-left span:last-child');
        const wmBottomRight = rrWrap.querySelector('.rr-watermark.bottom-right span');
        let act2Animated = false;
        let act3Animated = false;

        // Interactive Holographic Reticle Follower
        const reticle = document.getElementById('rrReticle');
        const reticleHud = document.getElementById('rrReticleHud');
        if (reticle) {
          rrWrap.addEventListener('pointerenter', () => { reticle.style.display = 'block'; });
          rrWrap.addEventListener('pointerleave', () => { reticle.style.display = 'none'; });
          rrWrap.addEventListener('pointermove', (e) => {
            const rect = rrWrap.getBoundingClientRect();
            const rx = e.clientX - rect.left;
            const ry = e.clientY - rect.top;
            reticle.style.left = rx + 'px';
            reticle.style.top = ry + 'px';
            if (reticleHud) {
              const currentFrame = Math.min(frameCount - 1, Math.max(0, Math.round((window.rrScrollTriggerInstance ? window.rrScrollTriggerInstance.progress : 0) * (frameCount - 1))));
              reticleHud.textContent = `CAD 1:1 // X:${Math.round(rx)} Y:${Math.round(ry)} // F:${String(currentFrame + 1).padStart(3, '0')}`;
            }
          });
        }

        // Pinned exact frame-by-frame bi-directional scrub
        window.rrScrollTriggerInstance = ScrollTrigger.create({
          scroller: scrollerEl,
          trigger: rrWrap,
          start: 'top top',
          end: '+=2800',
          pin: true,
          scrub: 0.1, // immediate, crisp tracking: zero jump!
          onUpdate: (self) => {
            // EXACT frame calculation: progress from 0.0 to 1.0 maps to frames 0 to 239
            const frameIndex = Math.min(frameCount - 1, Math.max(0, Math.round(self.progress * (frameCount - 1))));
            drawFrame(frameIndex);

            // Dynamic Real-Time Telemetry HUD Tickers
            const p = self.progress;
            const deg = (11.2667 + p * 0.005).toFixed(4);
            const lon = (76.2167 + p * 0.008).toFixed(4);
            if (wmTopLeft) {
              wmTopLeft.textContent = `${deg}°N ${lon}°E // FRAME ${String(frameIndex + 1).padStart(3, '0')}/240 // MALABAR TERROIR`;
            }
            if (wmBottomRight) {
              if (p < 0.33) {
                wmBottomRight.textContent = 'ROLLS-ROYCE COACHBUILD // 01 PHANTOM CHASSIS FRAMEWORK [ACTIVE]';
              } else if (p >= 0.33 && p < 0.68) {
                wmBottomRight.textContent = 'ROLLS-ROYCE COACHBUILD // 02 DUAL-FLITCH MIRROR-GRAIN FASCIA [1:1 SYMMETRY]';
              } else {
                wmBottomRight.textContent = 'ROLLS-ROYCE COACHBUILD // 03 TECTOQUINONE RESIN IMMUNITY LOCK [340Hz ACOUSTIC]';
              }
            }

            // Scroll Velocity Kinetic Inertia
            const vel = self.getVelocity ? self.getVelocity() : 0;
            const skew = Math.max(-2.5, Math.min(2.5, vel / 450));

            // Cinematic text transitions across 3 Acts with velocity skew
            if (p < 0.33) {
              const exit = p > 0.23 ? Math.max(0, 1 - (p - 0.23) / 0.1) : 1;
              if (act1) {
                act1.style.opacity = String(exit);
                act1.style.transform = `translateY(${-50 - (p * 40)}%) skewY(${skew}deg)`;
                act1.style.pointerEvents = exit > 0.3 ? 'auto' : 'none';
              }
              if (act2) {
                act2.style.opacity = '0';
                act2.style.transform = 'translateY(-20%)';
                act2.style.pointerEvents = 'none';
              }
              if (act3) {
                act3.style.opacity = '0';
                act3.style.transform = 'translateY(-20%)';
                act3.style.pointerEvents = 'none';
              }
              act2Animated = false;
              act3Animated = false;
            } else if (p >= 0.33 && p < 0.68) {
              const enter = Math.min(1, (p - 0.33) / 0.08);
              const exit = p > 0.58 ? Math.max(0, 1 - (p - 0.58) / 0.1) : 1;
              const op = Math.min(enter, exit);
              if (act1) {
                act1.style.opacity = '0';
                act1.style.transform = 'translateY(-80%)';
                act1.style.pointerEvents = 'none';
              }
              if (act2) {
                act2.style.opacity = String(op);
                act2.style.transform = `translateY(${-50 + (1 - enter) * 20}%) skewY(${skew}deg)`;
                act2.style.pointerEvents = op > 0.3 ? 'auto' : 'none';
              }
              if (act3) {
                act3.style.opacity = '0';
                act3.style.transform = 'translateY(-20%)';
                act3.style.pointerEvents = 'none';
              }
              if (!act2Animated && op > 0.5) {
                act2Animated = true;
                playWoodTap(540);
                const pitchEl = act2 ? act2.querySelector('.p-num:last-child') : null;
                if (pitchEl) {
                  gsap.fromTo({ val: 0.8 }, { val: 3.2 }, {
                    duration: 1.2,
                    ease: 'power2.out',
                    onUpdate: function() {
                      pitchEl.textContent = this.targets()[0].val.toFixed(1) + 'mm';
                    }
                  });
                }
              }
              act3Animated = false;
            } else {
              const enter = Math.min(1, (p - 0.68) / 0.08);
              if (act1) {
                act1.style.opacity = '0';
                act1.style.transform = 'translateY(-80%)';
                act1.style.pointerEvents = 'none';
              }
              if (act2) {
                act2.style.opacity = '0';
                act2.style.transform = 'translateY(-80%)';
                act2.style.pointerEvents = 'none';
              }
              if (act3) {
                act3.style.opacity = String(enter);
                act3.style.transform = `translateY(${-50 + (1 - enter) * 20}%) skewY(${skew}deg)`;
                act3.style.pointerEvents = enter > 0.3 ? 'auto' : 'none';
              }
              if (!act3Animated && enter > 0.5) {
                act3Animated = true;
                playWoodTap(620);
                const specNums = act3 ? act3.querySelectorAll('.rr-spec-num') : [];
                if (specNums.length >= 3) {
                  gsap.fromTo({ val: 0 }, { val: 16.8 }, {
                    duration: 1.5,
                    ease: 'power3.out',
                    onUpdate: function() { specNums[0].textContent = this.targets()[0].val.toFixed(1) + '%'; }
                  });
                  gsap.fromTo({ val: 0 }, { val: 0.72 }, {
                    duration: 1.7,
                    ease: 'power3.out',
                    onUpdate: function() { specNums[1].textContent = this.targets()[0].val.toFixed(2) + '%'; }
                  });
                  gsap.fromTo({ val: 1 }, { val: 18 }, {
                    duration: 1.3,
                    ease: 'power2.out',
                    onUpdate: function() { specNums[2].textContent = Math.round(this.targets()[0].val) + '-COAT'; }
                  });
                }
              }
            }
          }
        });
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
        if (handle) {
          handle.style.left = pct + '%';
          let badge = handle.querySelector('.intro-caliper-measure-hud');
          if (!badge) {
            badge = document.createElement('div');
            badge.className = 'intro-caliper-measure-hud';
            handle.appendChild(badge);
          }
          const mm = Math.round(pct * 14.5);
          badge.textContent = `${mm}mm // SPLIT ${Math.round(pct)}% : ${Math.round(100 - pct)}%`;
        }
        if (revealWrap) revealWrap.style.clipPath = `inset(0 0 0 ${pct}%)`;
      }

      // === 5. MAIN ANIMATION PIPELINE INITIALIZER ===
      
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
        const dimLine = document.getElementById('dimLine');
        const dimDot = document.getElementById('dimDotRight');

        if (typeof gsap !== 'undefined') {
          if (joineryLocked) {
            gsap.to(tenon, { x: 230, duration: 0.85, ease: 'power3.inOut' });
            if (dimLine) gsap.to(dimLine, { attr: { x2: 220 }, duration: 0.85, ease: 'power3.inOut' });
            if (dimDot) gsap.to(dimDot, { attr: { cx: 220 }, duration: 0.85, ease: 'power3.inOut' });
            gsap.to({ v: 130 }, {
              v: 0,
              duration: 0.85,
              ease: 'power3.inOut',
              onUpdate: function() {
                if (dimReadout) dimReadout.textContent = "INTERLOCKED: " + Math.round(this.targets()[0].v) + "mm";
              }
            });
            gsap.to(pin, {
              y: 65,
              duration: 0.5,
              delay: 0.7,
              ease: 'bounce.out',
              onComplete: () => {
                playWoodTap(740);
                gsap.fromTo('#acousticWave1',
                  { attr: { r: 8 }, opacity: 0.9, strokeWidth: 2.5 },
                  { attr: { r: 55 }, opacity: 0, strokeWidth: 0.5, duration: 0.85, ease: 'power2.out' }
                );
                gsap.fromTo('#acousticWave2',
                  { attr: { r: 8 }, opacity: 0.8, strokeWidth: 2 },
                  { attr: { r: 85 }, opacity: 0, strokeWidth: 0.3, duration: 1.1, delay: 0.08, ease: 'power2.out' }
                );
                gsap.fromTo('#stressHeatmap',
                  { opacity: 0 },
                  { opacity: 0.9, duration: 0.35, yoyo: true, repeat: 1, ease: 'power2.inOut' }
                );
              }
            });
          } else {
            gsap.to(pin, { y: 10, duration: 0.4, ease: 'power2.in' });
            gsap.to(tenon, { x: 340, duration: 0.85, delay: 0.2, ease: 'power3.out' });
            if (dimLine) gsap.to(dimLine, { attr: { x2: 330 }, duration: 0.85, delay: 0.2, ease: 'power3.out' });
            if (dimDot) gsap.to(dimDot, { attr: { cx: 330 }, duration: 0.85, delay: 0.2, ease: 'power3.out' });
            gsap.to({ v: 0 }, {
              v: 130,
              duration: 0.85,
              delay: 0.2,
              ease: 'power3.out',
              onUpdate: function() {
                if (dimReadout) dimReadout.textContent = "EXPAND: " + Math.round(this.targets()[0].v) + "mm";
              }
            });
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

      // === 11. MAGNETIC CURSOR ATTRACTION (DUAL-LAYER LIQUID PULL) ===
      function initMagneticButtons() {
        document.querySelectorAll('.magnetic-btn, .btn-basic, .btn-fill, .hero-rewipe-btn, .sound-toggle-btn, .intro-caliper-toggle-btn, .specimen-tab, .joinery-btn').forEach(btn => {
          const innerSpan = btn.querySelector('span') || btn.querySelector('.txt') || btn.querySelector('div');
          btn.addEventListener('mousemove', (e) => {
            const rect = btn.getBoundingClientRect();
            const dx = e.clientX - (rect.left + rect.width / 2);
            const dy = e.clientY - (rect.top + rect.height / 2);
            if (typeof gsap !== 'undefined') {
              gsap.to(btn, { x: dx * 0.28, y: dy * 0.28, duration: 0.3, ease: 'power2.out' });
              if (innerSpan) {
                gsap.to(innerSpan, { x: dx * 0.16, y: dy * 0.16, duration: 0.25, ease: 'power2.out' });
              }
            }
          });
          btn.addEventListener('mouseleave', () => {
            if (typeof gsap !== 'undefined') {
              gsap.to(btn, { x: 0, y: 0, duration: 0.5, ease: 'elastic.out(1, 0.3)' });
              if (innerSpan) {
                gsap.to(innerSpan, { x: 0, y: 0, duration: 0.6, ease: 'elastic.out(1, 0.4)' });
              }
            }
          });
        });
      }

      let pixelWipesInitialized = false;
      function initAiswaryaPixelWipes() {
        if (pixelWipesInitialized) return;
        if (typeof gsap === "undefined" || typeof ScrollTrigger === "undefined") {
          setTimeout(initAiswaryaPixelWipes, 100);
          return;
        }
        pixelWipesInitialized = true;
        gsap.registerPlugin(ScrollTrigger);

        const scrollerEl = document.querySelector('.main-inner') ? '.main-inner' : window;

        // --- 0. HERO SECTION: AUTOMATIC PIXEL CASCADE DOWN ON OPEN WITH LASER & SHEEN ---
        const heroCols = document.querySelectorAll('.home-hero-img-col');
        const heroReveals = document.querySelectorAll('.home-hero-img-col .pixel-reveal-img');
        if (heroReveals.length > 0) {
          heroCols.forEach((col, idx) => {
            const img = col.querySelector('.pixel-reveal-img');
            const laser = col.querySelector('.pixel-wipe-laser-beam');
            const sheen = col.querySelector('.hero-wood-sheen');

            if (img) {
              gsap.set(img, { maskPosition: '0% 0%', webkitMaskPosition: '0% 0%' });
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
            }
            if (laser) {
              gsap.fromTo(laser,
                { top: '0%', opacity: 1 },
                { top: '100%', opacity: 0, duration: 1.25, delay: 0.35 + idx * 0.22, ease: 'steps(29)' }
              );
            }
            if (sheen) {
              gsap.fromTo(sheen,
                { left: '-120%', opacity: 0 },
                { left: '200%', opacity: 0.65, duration: 0.95, delay: 0.75 + idx * 0.22, ease: 'power2.inOut' }
              );
            }
          });
        }

        // --- HERO 3D PERSPECTIVE TILT & INTERACTION ---
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
            gsap.to(col, { rotationY: 0, rotationX: 0, duration: 0.6, ease: 'elastic.out(1, 0.4)' });
            if (realImg) {
              gsap.to(realImg, { x: 0, y: 0, duration: 0.6, ease: 'power2.out' });
            }
          });

          col.addEventListener('mousemove', (e) => {
            const rect = col.getBoundingClientRect();
            const relX = Math.round(e.clientX - rect.left);
            const relY = Math.round(e.clientY - rect.top);

            // 3D Spatial Tilt Physics
            const normX = (relX / rect.width) - 0.5;
            const normY = (relY / rect.height) - 0.5;
            gsap.to(col, {
              rotationY: normX * 10,
              rotationX: -normY * 10,
              transformPerspective: 900,
              duration: 0.3,
              ease: 'power2.out'
            });
            if (realImg) {
              gsap.to(realImg, {
                x: -normX * 8,
                y: -normY * 8,
                duration: 0.3,
                ease: 'power2.out'
              });
            }

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

        // --- 1. EXPLORE WOODCRAFT (INTRO) SCROLLTRIGGER WIPE WITH LASER & SHEEN ---
        const introReveal = document.querySelector('.home-intro-wrap .pixel-reveal-img');
        const introLaser = document.querySelector('#introPixelWrap .pixel-wipe-laser-beam');
        const introSheen = document.querySelector('#introPixelWrap .hero-wood-sheen');
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
                scrub: 0.6,
                onUpdate: (self) => {
                  if (introLaser) {
                    const p = self.progress;
                    introLaser.style.top = (p * 100) + '%';
                    introLaser.style.opacity = (p > 0.01 && p < 0.99) ? 1 : 0;
                  }
                },
                onEnter: () => {
                  playWoodTap(500);
                  if (introSheen) {
                    gsap.fromTo(introSheen,
                      { left: '-120%', opacity: 0 },
                      { left: '200%', opacity: 0.65, duration: 1.0, ease: 'power2.inOut' }
                    );
                  }
                }
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

        // --- EXPLORE WOODCRAFT ODOMETER SCROLLTRIGGER ---
        const introMetrics = document.querySelector('.intro-metrics-grid');
        if (introMetrics && typeof ScrollTrigger !== 'undefined') {
          ScrollTrigger.create({
            scroller: scrollerEl,
            trigger: introMetrics,
            start: 'top 85%',
            onEnter: () => animateOdometerCounters()
          });
        }

        // --- 2. ROLLS-ROYCE FULL-SCREEN 3D EXPLODED CANVAS ENGINE (PINNED +=2800) ---
        // MUST BE INITIALIZED HERE IN DOM SEQUENCE SO LOWER SECTIONS ACCOUNT FOR THE 2800px PIN-SPACER
        initRollsRoyceCanvasScrub();

        // --- 3. TECHNICAL MAP JOINERY SCHEMATIC SCROLLTRIGGER ---
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

        // --- 4. PLATFORM / ATELIER SECTION (LOWER SIDE IMAGES 0 AND 1) WITH LASER, MATRIX & 3D TILT ---
        const platformCards = document.querySelectorAll('.platform-side-img-card');
        platformCards.forEach((card, idx) => {
          const img = card.querySelector('.pixel-reveal-img');
          const laser = card.querySelector('.pixel-wipe-laser-beam');
          const sheen = card.querySelector('.hero-wood-sheen');
          const grid = card.querySelector('.pixel-matrix-grid');
          const trigger = card.closest('.home-platform-img-item') || card;

          if (img) {
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
                  scrub: 0.6,
                  onUpdate: (self) => {
                    const p = self.progress;
                    if (laser) {
                      laser.style.top = (p * 100) + '%';
                      laser.style.opacity = (p > 0.01 && p < 0.99) ? 1 : 0;
                    }
                    if (grid) {
                      grid.style.opacity = (p > 0.05 && p < 0.95) ? 0.35 : 0.16;
                    }
                  },
                  onEnter: () => {
                    playWoodTap(520 + idx * 40);
                    if (sheen) {
                      gsap.fromTo(sheen,
                        { left: '-120%', opacity: 0 },
                        { left: '200%', opacity: 0.72, duration: 1.0, ease: 'power2.inOut' }
                      );
                    }
                  }
                }
              }
            );
          }

          // 3D Spatial Perspective Tilt on Mousemove
          card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const relX = Math.round(e.clientX - rect.left);
            const relY = Math.round(e.clientY - rect.top);
            const normX = (relX / rect.width) - 0.5;
            const normY = (relY / rect.height) - 0.5;
            gsap.to(card, {
              rotationY: normX * 8,
              rotationX: -normY * 8,
              transformPerspective: 900,
              scale: 1.015,
              duration: 0.3,
              ease: 'power2.out'
            });

            if (crosshair && archHud) {
              crosshair.style.display = 'block';
              crosshair.style.left = e.clientX + 'px';
              crosshair.style.top = e.clientY + 'px';
              archHud.textContent = `ATELIER 0${idx+1} // X: ${relX * 4}mm | Y: ${relY * 4}mm // 1:20 SCALE`;
            }
          });

          card.addEventListener('mouseleave', () => {
            gsap.to(card, {
              rotationY: 0,
              rotationX: 0,
              scale: 1,
              duration: 0.6,
              ease: 'elastic.out(1, 0.4)'
            });
            if (crosshair) crosshair.style.display = 'none';
          });
        });

        // --- 5. WHY AISWARYA SECTION: 4 CRAFTSMANSHIP LOWER SIDE IMAGES WITH ADVANCED LASER, MATRIX, SHEEN & 3D TILT ---
        const whyItems = document.querySelectorAll('.home-why-item');
        whyItems.forEach((item, idx) => {
          const card = item.querySelector('.why-side-img-card');
          const img = item.querySelector('.pixel-reveal-img');
          const laser = item.querySelector('.pixel-wipe-laser-beam');
          const sheen = item.querySelector('.hero-wood-sheen');
          const grid = item.querySelector('.pixel-matrix-grid');
          const trigger = card || item;

          if (img) {
            gsap.fromTo(img,
              { maskPosition: '0% 0%', webkitMaskPosition: '0% 0%' },
              {
                maskPosition: '0% 100%',
                webkitMaskPosition: '0% 100%',
                ease: 'steps(29)',
                scrollTrigger: {
                  scroller: scrollerEl,
                  trigger: trigger,
                  start: 'top 85%',
                  end: 'center 35%',
                  scrub: 0.6,
                  onUpdate: (self) => {
                    const p = self.progress;
                    if (laser) {
                      laser.style.top = (p * 100) + '%';
                      laser.style.opacity = (p > 0.01 && p < 0.99) ? 1 : 0;
                    }
                    if (grid) {
                      grid.style.opacity = (p > 0.05 && p < 0.95) ? 0.38 : 0.16;
                    }
                  },
                  onEnter: () => {
                    playWoodTap(460 + idx * 40);
                    if (sheen) {
                      gsap.fromTo(sheen,
                        { left: '-120%', opacity: 0 },
                        { left: '200%', opacity: 0.75, duration: 1.1, ease: 'power2.inOut' }
                      );
                    }
                  }
                }
              }
            );
          }

          // 3D Spatial Perspective Tilt on Mousemove for Why side image cards
          if (card) {
            card.addEventListener('mousemove', (e) => {
              const rect = card.getBoundingClientRect();
              const relX = Math.round(e.clientX - rect.left);
              const relY = Math.round(e.clientY - rect.top);
              const normX = (relX / rect.width) - 0.5;
              const normY = (relY / rect.height) - 0.5;

              gsap.to(card, {
                rotationY: normX * 8,
                rotationX: -normY * 8,
                transformPerspective: 900,
                scale: 1.015,
                duration: 0.3,
                ease: 'power2.out'
              });

              if (crosshair && archHud) {
                crosshair.style.display = 'block';
                crosshair.style.left = e.clientX + 'px';
                crosshair.style.top = e.clientY + 'px';
                archHud.textContent = `CRAFT 0${idx+1} // X: ${relX * 3}mm | Y: ${relY * 3}mm // NILAMBUR TEAK 760kg/m³`;
              }
            });

            card.addEventListener('mouseleave', () => {
              gsap.to(card, {
                rotationY: 0,
                rotationX: 0,
                scale: 1,
                duration: 0.6,
                ease: 'elastic.out(1, 0.4)'
              });
              if (crosshair) crosshair.style.display = 'none';
            });
          }
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

        // --- 5. 3D GYRO COIN LEVITATION & FLIP INTERACTION ---
        const coin = document.getElementById('giCoin');
        if (coin) {
          gsap.to(coin, {
            y: -7,
            rotationZ: 1.5,
            duration: 2.8,
            yoyo: true,
            repeat: -1,
            ease: 'sine.inOut'
          });
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

        // --- 8. ATTACH WOOD TAP SOUND TO ALL BUTTONS ---
        document.querySelectorAll('.btn-basic, .btn-fill, .header-menu-btn, .footer-menu-link').forEach((el) => {
          el.addEventListener('click', () => playWoodTap(560));
        });

        // --- 9. INITIALIZE MAGNETIC CURSOR ---
        initMagneticButtons();

        setTimeout(() => {
          if (window.ScrollTrigger) ScrollTrigger.refresh();
        }, 250);
      }

      document.addEventListener('DOMContentLoaded', () => {
        unlockPage();
        setTimeout(unlockPage, 200);
        initAiswaryaPixelWipes();
      });
      window.addEventListener('load', () => {
        unlockPage();
        setTimeout(unlockPage, 300);
        if (window.ScrollTrigger) {
          setTimeout(() => window.ScrollTrigger.refresh(), 200);
        }
      });
    </script>
    """

    if '</head>' in html_str:
        html_str = html_str.replace('</head>', head_injections + '\n</head>')

    with open('/home/mullainathan/projects/nilambur-teak-wood/public/nilambur.html', 'w', encoding='utf-8') as f:
        f.write(html_str)
    with open('/home/mullainathan/projects/nilambur-teak-wood/public/index.html', 'w', encoding='utf-8') as f:
        f.write(html_str)

    print(f"Generated clean Aiswarya Industries site! Size: {len(html_str)}")

if __name__ == '__main__':
    build()
