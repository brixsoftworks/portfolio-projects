import re
from bs4 import BeautifulSoup

def build_clone():
    with open('/tmp/heron.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Fix relative CDN paths
    html = html.replace('../cdn.prod.website-files.com/', 'https://cdn.prod.website-files.com/')

    # 2. Parse HTML
    soup = BeautifulSoup(html, 'html.parser')

    # Update Title & Meta
    if soup.title:
        soup.title.string = "Nilambur Teak Wood | The Gold Standard of Architectural Timber (GI Tag 581)"
    
    for meta in soup.find_all('meta'):
        if meta.get('property') in ['og:title', 'twitter:title']:
            meta['content'] = "Nilambur Teak Wood | The Gold Standard of Architectural Timber (GI Tag 581)"
        elif meta.get('property') in ['og:description', 'twitter:description'] or meta.get('name') == 'description':
            meta['content'] = "Handcrafted luxury teak interiors, bespoke cabinetry, and architectural woodwork from Kerala's legendary GI-tagged Nilambur forests."

    html_str = str(soup)

    # Clean out external tracking scripts and Netlify rum
    html_str = re.sub(r'<script[^>]*googletagmanager[^>]*>.*?</script>', '', html_str, flags=re.DOTALL)
    html_str = re.sub(r'https://www.googletagmanager.com/gtag/js\?id=G-N1KKXK6ZR5', '', html_str)
    html_str = re.sub(r'<script[^>]*clarity\.ms[^>]*>.*?</script>', '', html_str, flags=re.DOTALL)
    html_str = re.sub(r'<script[^>]*mixpanel[^>]*>.*?</script>', '', html_str, flags=re.DOTALL)
    html_str = re.sub(r'<script[^>]*id="netlify-rum-container"[^>]*>.*?</script>', '', html_str, flags=re.DOTALL)
    html_str = re.sub(r'<script[^>]*src="/\.netlify/scripts/rum"[^>]*>.*?</script>', '', html_str, flags=re.DOTALL)

    # 3. Systematic text replacements dictionary
    replacements = [
        # Logo / Brand
        ('Heron AI | Works inside your design tools', 'Nilambur Teak Wood | The Gold Standard of Architectural Timber'),
        ('WELCOME TO HERON AI', 'WELCOME TO NILAMBUR TEAK WOOD'),
        ('TYPE :Technology/AI Software Company', 'TYPE :Rare Architectural Hardwood & Bespoke Atelier'),
        ('TYPE\n:\nTechnology/AI Software Company', 'TYPE\n:\nRare Architectural Hardwood & Bespoke Atelier'),
        ('TYPE\n:\nTECHNOLOGY/AI SOFTWARE COMPANY', 'TYPE\n:\nRARE ARCHITECTURAL HARDWOOD & BESPOKE ATELIER'),
        ('TYPE\n:\nTECHNOLOGY/AI SOFTWARE ATELIER', 'TYPE\n:\nRARE ARCHITECTURAL HARDWOOD & BESPOKE ATELIER'),
        ('FOUNDED:2026', 'FOUNDED:1844 (CANOLI HISTORIC RESERVE)'),
        ('FOUNDED\n:\n2026', 'FOUNDED\n:\n1844 (CANOLI HISTORIC RESERVE)'),
        ('FOCUS      :AI-powered building code compliance for architects', 'FOCUS      :GI-Tagged Generational Teak Wood For Luxury Estates & Sanctuaries'),
        ('FOCUS\xa0\xa0\xa0\xa0\xa0\xa0:AI-powered building code compliance for architects\n(BIM / REVIT INTEGRATION)', 'FOCUS\xa0\xa0\xa0\xa0\xa0\xa0:GI-Tagged Generational Teak Wood For Luxury Estates & Sanctuaries\n(CANOLI PLOT GI TAG NO. 581)'),
        ('FOCUS\xa0\xa0\xa0\xa0\xa0\xa0:\nAI-POWERED BUILDING CODE COMPLIANCE FOR ARCHITECTS\n(BIM / REVIT INTEGRATION)', 'FOCUS\xa0\xa0\xa0\xa0\xa0\xa0:\nGI-TAGGED GENERATIONAL TEAK WOOD FOR LUXURY ESTATES & SANCTUARIES\n(CANOLI PLOT GI TAG NO. 581)'),
        ('LOCATION:1801 CALIFORNIA ST. SUITE 2400 DENVER, CO 80202', 'LOCATION:CHALIYAR RIVER BASIN, NILAMBUR, MALAPPURAM, KERALA 679329'),
        ('LOCATION\n:\n1801 CALIFORNIA ST. SUITE 2400 DENVER, CO 80202', 'LOCATION\n:\nCHALIYAR RIVER BASIN, NILAMBUR, MALAPPURAM, KERALA 679329'),
        ('LOCATION\n:\n1801 CALIFORNIA ST. SUITE 2400 DENVER,', 'LOCATION\n:\nCHALIYAR RIVER BASIN, NILAMBUR, MALAPPURAM, KERALA,'),
        
        # Preloader steps
        ('001 INITIALIZE CORE SYSTEM', '001 VERIFY CHALIYAR ALLUVIAL HEARTWOOD'),
        ('002 LOAD AI MODELS', '002 TEST TECTOQUINONE ESSENTIAL OIL DENSITY'),
        ('003 CONFIGURE DATA PIPELINES', '003 INSPECT MONSOONAL GROWTH RING TIGHTNESS'),
        ('004 SYNC DISTRIBUTED NODES', '004 VALIDATE GOVERNMENT GI REGISTRATION NO. 581'),
        ('005 VALIDATE INPUT STREAMS', '005 EXECUTE SOLAR KILN EQUILIBRIUM STABILIZATION'),
        ('006 OPTIMIZE INFERENCE ENGINE', '006 CALIBRATE 10-12% INTERIOR MOISTURE TARGET'),
        ('007 DEPLOY TEST ENVIRONMENT', '007 ARTISAN MORTISE-AND-TENON JOINERY FIT'),
        ('008 ENABLE REAL-TIME PROCESSING', '008 SURFACE MICRO-PLANING & SILICA POLISH'),
        ('009 RUN DIAGNOSTICS', '009 APPLY COLD-PRESSED LINSEED & BEESWAX'),
        ('010 START EXECUTION', '010 RELEASE GENERATIONAL HEIRLOOM TIMBER'),

        # Header menu items
        ('>Product<', '>Atelier<'),
        ('>Heron Chat Widget<', '>Bespoke Millwork<'),
        ('>Heron Dashboard<', '>Timber Reserve Archive<'),
        ('>Pricing<', '>Provenance & Rates<'),
        ('>Resources<', '>Timber Dossier<'),
        ('>Insights<', '>GI Tag 581 Insights<'),
        ('>AI Practices<', '>Sustainable Forestry<'),
        ('>Design Workflows<', '>Atelier Process<'),
        ('>About<', '>Heritage<'),
        ('>Contact us<', '>Commission<'),
        ('>contact us<', '>commission<'),

        # Hero
        ('Click and drag your mouse to see violations', 'Drag cursor to inspect timber fiber density & joinery specifications'),
        ('IBC 1015.3', 'GI CERT 581'),
        ('Guardrail required for fall protection', 'Geographical Indication certified Nilambur provenance'),
        ('IBC 1011.11', 'CANOLI 1844'),
        ('Handrails required.', "World's oldest planted teak forest heartwood."),
        ('An AI agent that works inside your design tools', 'An Architectural Masterpiece Handcrafted from Nilambur Teak'),
        ('Heron reviews your model, identifies issues, and proposes solutions. Upon approval, it edits automatically. This concept crafted by', 'Harvested from Kerala’s historic river banks, seasoned for generations, and master-crafted into bespoke estates, cabinetry, and heirloom sanctuaries.'),
        ('Bearplus agency', 'Nilambur Atelier'),

        # Intro
        ("THE REPETITIVE PARTS OF MODELLING SHOULDN'T EAT YOUR DAY. HERON HANDLES THE FIDDLY, MANUAL WORK SO YOU CAN STAY FOCUSED ON THE DESIGN, NOT THE SOFTWARE.",
         "THE RAPID DEGRADATION OF COMMERCIAL TIMBER SHOULD NEVER COMPROMISE YOUR ESTATE. NILAMBUR TEAK IS NATURALLY IMPERVIOUS TO TERMITES, TIME, AND TROPICAL HUMIDITY."),
        ("Works natively inside the tools you already use, including Revit, Rhino, ArchiCAD and SketchUp.",
         "Naturally harvested along the nutrient-rich Chaliyar River, boasting world-record tectoquinone resin and silica density."),

        # Problem section
        ('PROBLEMS', 'THE TIMBER PARADOX'),
        ('Your design tools do what you tell them, nothing more', 'Commercial timber warps, rots, and decays. Nilambur endures for centuries.'),
        ("Design software is powerful but passive. It waits for every instruction, gives no advice, and can't act on its own, so all the repetitive work stays on you.",
         "Mass-market timber is fast-grown and chemically treated. It decays when exposed to humidity, lacks natural essential oils, and requires repetitive replacement every few years."),
        ('>Manual<', '>Commercial Softness<'),
        ('>Slow<', '>Toxic Chemical Treatments<'),
        ('>Unreliable<', '>Disposable Lifespans<'),
        ('>Linear<', '>Synthetic Veneers<'),

        # Map / Model Section
        ('Right there with you', 'In Every Grain'),
        ('For the whole design', 'Botanical Superiority in Every Fiber'),
        ('IBC 1017.2', 'TECTOQUINONE 98.4%'),
        ('Exit Access Travel Distance', 'Natural Termite & Marine Borer Resistance'),
        ('Assembly occupancies without sprinklers are limited to 75 ft of exit travel distance. This layout exceeds the maximum allowable path length.',
         'Nilambur teak synthesizes high concentrations of tectoquinone oils that naturally repel termites, fungal rot, and borers without a single drop of synthetic chemicals.'),
        ('IBC 1010.1.2.1', 'SILICA 650 KG/M³'),
        ('Door Swing Direction', 'Diamond-Hard Alluvial Hardness'),
        ('ICC A117.1 §604.3.1', 'MONSOON RINGS 1.2 MM'),
        ('Accessible Toilet Clearance', 'Century-Tight Ring Density'),
        ('Accessible restrooms require a 60” turning radius. This layout does not provide sufficient maneuvering space.',
         'Centuries of slow monsoonal growth produce razor-tight annual rings and golden chatoyant luster that never shrink or split over generations.'),

        # Platform Section
        ('Heron Chat widget', 'Bespoke Architectural Living & Cabinetry Atelier'),
        ('A chat that floats over your design tool. Ask it about your model or tell it what to change, and it acts inside the software on your approval.',
         'Custom architectural millwork tailored to your estate. From floor-to-ceiling wainscoting to hidden pivot doors, our hereditary artisans craft living timber spaces that age into family heirlooms.'),
        ('Heron Dashboard', 'Generational Timber Archive & GI Tag 581'),
        ('Ask code questions about your building and get answers that reflect how the code applies to your layout, occupancy, and conditions, not just what the requirements say in isolation.',
         'Every commission comes with government-registered GI Tag No. 581 certification, harvest coordinates, and a digital provenance passport validating century-old heartwood.'),

        # Why Us Section
        ('WHY US', 'WHY NILAMBUR TEAK'),
        ('BUILT TO WORK THE WAY YOU DO', 'BUILT TO ENDURE BEYOND LIFETIMES'),
        ('Heron fits into your process instead of replacing it. It watches quietly, speaks up when something needs attention, and only acts when you say so, so you stay in control the whole way through.',
         'Nilambur teak integrates into your architectural vision as living heritage. It matures gracefully, deepening into rich golden-brown hues with natural self-healing oils.'),
        ('Observe', 'Harvest'),
        ('Heron watches your model as you design', 'Ethically sourced from certified Kerala Forest Department mature conservation reserves.'),
        ('Advise', 'Season'),
        ('It flags issues and suggests fixes in plain language', '18-month open-air seasoning followed by computer-calibrated solar kilns to 10–12% moisture.'),
        ('Act', 'Shape'),
        ('With your approval, it makes the edit directly in the model', 'Sub-millimeter mortise-and-tenon joinery hand-cut by hereditary master craftsmen.'),
        ('Learn', 'Finish'),
        ("It picks up your firm's standards and gets more useful over time", 'Organic botanical oil and beeswax finishes that enrich natural chatoyancy and grain depth.'),

        # Use Cases
        ('Architects', 'Private Luxury Estates'),
        ('Hand the repetitive modelling to Heron and keep your focus on design.',
         'Palatial timber ceilings, grand entryways, and custom wainscoting engineered for coastal and tropical estates.'),
        ('Interior Designers', 'Bespoke Kitchens & Pantries'),
        ('Get quick help with layouts, fixtures, and clearances without leaving your model.',
         'Solid heartwood cabinetry, butcher blocks, and concealed joinery immune to cooking moisture and steam.'),
        ('Landscape Architects', 'Heirloom Libraries & Studies'),
        ('Sort grading, site elements, and layouts without the manual grind.',
         'Bespoke book sanctuaries, executive desks, and wall-to-wall coffered woodwork.'),
        ('Engineers', 'Architectural Portals & Staircases'),
        ('Run discipline-specific checks and edits in the model, so coordination issues surface earlier.',
         'Massive solid teak pivot portals and floating sculptural stairs engineered for high pedestrian load.'),

        # CTA
        ('SEE WHAT HERON CAN DO IN YOUR MODEL', 'SEE WHAT NILAMBUR TEAK CAN DO IN YOUR ESTATE'),
        ("Book a demo and we'll show Heron working inside one of your own projects.",
         "Request a consultation with our master timber curator. Commission bespoke architectural woodwork tailored to your residence."),

        # Footer
        ('Want to see more cool websites like this?', 'Interested in commissioning Nilambur Teak for your estate?'),
        ('Sign up for occasional updates from Bearplus.', 'Receive our Private Reserve Timber Catalog and Architectural Portfolio.'),
        ('Subscribe', 'Request Dossier'),
        ('Company', 'Atelier'),
        ('About us', 'Heritage'),
    ]

    for old, new in replacements:
        html_str = html_str.replace(old, new)

    head_script = """
    <script>
      window.skipPreloader = function() {
        const loading = document.querySelector('.loading');
        if (loading) {
          loading.style.opacity = '0';
          loading.style.pointerEvents = 'none';
          setTimeout(() => { loading.style.display = 'none'; }, 400);
        }
        const skipBtn = document.getElementById('skip-preloader-btn');
        if (skipBtn) skipBtn.style.display = 'none';
      };

      const copyData = {
        teak: {
          title: "An Architectural Masterpiece Handcrafted from Nilambur Teak",
          sub: "Harvested from Kerala’s historic river banks, seasoned for generations, and master-crafted into bespoke estates, cabinetry, and heirloom sanctuaries.",
          intro: "THE RAPID DEGRADATION OF COMMERCIAL TIMBER SHOULD NEVER COMPROMISE YOUR ESTATE. NILAMBUR TEAK IS NATURALLY IMPERVIOUS TO TERMITES, TIME, AND TROPICAL HUMIDITY.",
          cta: "SEE WHAT NILAMBUR TEAK CAN DO IN YOUR ESTATE"
        },
        heron: {
          title: "An AI agent that works inside your design tools",
          sub: "Heron reviews your model, identifies issues, and proposes solutions. Upon approval, it edits automatically. This concept crafted by",
          intro: "THE REPETITIVE PARTS OF MODELLING SHOULDN'T EAT YOUR DAY. HERON HANDLES THE FIDDLY, MANUAL WORK SO YOU CAN STAY FOCUSED ON THE DESIGN, NOT THE SOFTWARE.",
          cta: "SEE WHAT HERON CAN DO IN YOUR MODEL"
        }
      };

      window.toggleCopyMode = function(mode) {
        const btnTeak = document.getElementById('btn-mode-teak');
        const btnHeron = document.getElementById('btn-mode-heron');
        if (mode === 'teak') {
          if (btnTeak) { btnTeak.style.background = '#e15c46'; btnTeak.style.color = '#fff'; }
          if (btnHeron) { btnHeron.style.background = 'transparent'; btnHeron.style.color = '#a0a0a0'; }
          updateCopy(copyData.teak);
        } else {
          if (btnHeron) { btnHeron.style.background = '#e15c46'; btnHeron.style.color = '#fff'; }
          if (btnTeak) { btnTeak.style.background = 'transparent'; btnTeak.style.color = '#a0a0a0'; }
          updateCopy(copyData.heron);
        }
      };

      function updateCopy(data) {
        const heroH1 = document.querySelector('.home-hero-title h1');
        if (heroH1) {
          heroH1.setAttribute('aria-label', data.title);
          const lines = heroH1.querySelectorAll('.bp-line');
          if (lines.length > 0) {
            lines[0].innerText = data.title;
            for (let i = 1; i < lines.length; i++) lines[i].style.display = 'none';
          } else {
            heroH1.innerText = data.title;
          }
        }
        const introH2 = document.querySelector('.home-intro-content-title h2');
        if (introH2) introH2.innerText = data.intro;
        const ctaH2 = document.querySelector('.home-cta-title h2');
        if (ctaH2) ctaH2.innerText = data.cta;
      }
    </script>
    """

    floating_controls = """
    <!-- Floating Mode Switcher & Skip Intro HUD -->
    <div id="nilambur-hud-control" style="position: fixed; bottom: 24px; right: 24px; z-index: 999999; display: flex; align-items: center; gap: 10px; font-family: 'Geistmono', monospace; font-size: 11px;">
      <button id="skip-preloader-btn" onclick="window.skipPreloader()" style="background: rgba(18, 18, 18, 0.9); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border: 1px solid rgba(225, 92, 70, 0.5); color: #e15c46; padding: 8px 14px; border-radius: 6px; cursor: pointer; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; box-shadow: 0 4px 20px rgba(0,0,0,0.5);">
         Skip Intro
      </button>
      <div style="background: rgba(18, 18, 18, 0.9); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.15); padding: 4px; border-radius: 6px; display: flex; gap: 4px; box-shadow: 0 4px 20px rgba(0,0,0,0.5);">
        <button id="btn-mode-teak" onclick="window.toggleCopyMode('teak')" style="background: #e15c46; color: #ffffff; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">
          Nilambur Teak Copy
        </button>
        <button id="btn-mode-heron" onclick="window.toggleCopyMode('heron')" style="background: transparent; color: #a0a0a0; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; text-transform: uppercase; letter-spacing: 0.05em;">
          Original Heron AI Copy
        </button>
      </div>
    </div>
    """

    if '</head>' in html_str:
        html_str = html_str.replace('</head>', head_script + '\n</head>')
    if '</body>' in html_str:
        html_str = html_str.replace('</body>', floating_controls + '\n</body>')
    else:
        html_str += floating_controls

    with open('/home/mullainathan/projects/nilambur-teak-wood/public/nilambur.html', 'w', encoding='utf-8') as f:
        f.write(html_str)

    with open('/home/mullainathan/projects/nilambur-teak-wood/public/index.html', 'w', encoding='utf-8') as f:
        f.write(html_str)

    print(f"Generated /public/nilambur.html and /public/index.html, length: {len(html_str)}")

if __name__ == '__main__':
    build_clone()
