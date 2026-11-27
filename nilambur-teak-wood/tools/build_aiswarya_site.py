import re
from bs4 import BeautifulSoup

def generate_site():
    with open('/home/mullainathan/projects/nilambur-teak-wood/public/test-heron.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # Fix relative CDN paths
    html = html.replace('../cdn.prod.website-files.com/', 'https://cdn.prod.website-files.com/')

    soup = BeautifulSoup(html, 'html.parser')

    # Update Title & Meta
    if soup.title:
        soup.title.string = "Aiswarya Industries | Dealers in Wooden Furniture & Interior Designing | Nilambur, Kerala"
    
    for meta in soup.find_all('meta'):
        if meta.get('property') in ['og:title', 'twitter:title']:
            meta['content'] = "Aiswarya Industries | Wooden Furniture & Interior Designing, Nilambur"
        elif meta.get('property') in ['og:description', 'twitter:description'] or meta.get('name') == 'description':
            meta['content'] = "Aiswarya Industries, Nilambur — Dealers in handcrafted wooden furniture, bespoke solid teak living sets, modular kitchens, bedroom suites, custom wardrobes, and turnkey interior designing. Contact Janardhanan: +91 9447631731, Jithesh: +91 9656663063."

    html_str = str(soup)

    # Clean out tracking scripts and Netlify rum
    html_str = re.sub(r'<script[^>]*googletagmanager[^>]*>.*?</script>', '', html_str, flags=re.DOTALL)
    html_str = re.sub(r'https://www.googletagmanager.com/gtag/js\?id=G-N1KKXK6ZR5', '', html_str)
    html_str = re.sub(r'<script[^>]*clarity\.ms[^>]*>.*?</script>', '', html_str, flags=re.DOTALL)
    html_str = re.sub(r'<script[^>]*mixpanel[^>]*>.*?</script>', '', html_str, flags=re.DOTALL)
    html_str = re.sub(r'<script[^>]*id="netlify-rum-container"[^>]*>.*?</script>', '', html_str, flags=re.DOTALL)
    html_str = re.sub(r'<script[^>]*src="/\.netlify/scripts/rum"[^>]*>.*?</script>', '', html_str, flags=re.DOTALL)

    # Clean out Schema.org SoftwareApplication and replace with Furniture & Interior Business
    new_schema = """{
  "@context": "https://schema.org",
  "@type": "HomeGoodsStore",
  "name": "Aiswarya Industries",
  "description": "Dealers in Wooden Furniture & Interior Designing in Nilambur, Kerala. Manufacturing custom solid wood furniture, modular kitchens, and architectural interiors.",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "Mannuppadam, Eranhimangad P.O.",
    "addressLocality": "Nilambur",
    "addressRegion": "Kerala",
    "postalCode": "679329",
    "addressCountry": "IN"
  },
  "telephone": "+919447631731"
}"""
    html_str = re.sub(r'{\s*"@context":\s*"https://schema.org",\s*"@type":\s*"SoftwareApplication".*?}', new_schema, html_str, flags=re.DOTALL)

    # Systematic Replacements for Aiswarya Industries & Wooden Furniture / Interior Designing
    replacements = [
        # 1. Branding & Header
        ('Heron AI | Works inside your design tools', 'Aiswarya Industries | Dealers in Wooden Furniture & Interior Designing'),
        ('Heron AI', 'Aiswarya Industries'),
        ('heronai', 'aiswarya-industries'),
        ('Heron', 'Aiswarya'),
        ('heron', 'aiswarya'),

        # Header Navigation Items
        ('>Product<', '>Furniture Collections<'),
        ('>Heron Chat Widget<', '>Living & Dining Furniture<'),
        ('>Heron Dashboard<', '>Modular Kitchens & Wardrobes<'),
        ('>Pricing<', '>Interior Design Packages<'),
        ('>Resources<', '>Woodcraft Portfolio<'),
        ('>Insights<', '>Nilambur Teak Craft<'),
        ('>AI Practices<', '>Seasoning & Joinery<'),
        ('>Design Workflows<', '>Turnkey Process<'),
        ('>About<', '>About Aiswarya<'),
        ('>Contact us<', '>Contact & Inquiries<'),
        ('>contact us<', '>Call: +91 9447 631 731<'),

        # Preloader / Loading Screen
        ('WELCOME TO HERON AI', 'WELCOME TO AISWARYA INDUSTRIES'),
        ('Technology/AI Software Company', 'Dealers in Wooden Furniture & Interior Designing'),
        ('TECHNOLOGY/AI SOFTWARE COMPANY', 'DEALERS IN WOODEN FURNITURE & INTERIOR DESIGNING'),
        ('FOUNDED:2026', 'FOUNDED:NILAMBUR WOODCRAFT ATELIER'),
        ('FOUNDED\n:\n2026', 'FOUNDED\n:\nNILAMBUR WOODCRAFT ATELIER'),
        ('2026', 'NILAMBUR'),
        ('AI-powered building code compliance for architects', 'Custom Solid Wood Furniture & Turnkey Luxury Interior Designing'),
        ('AI-POWERED BUILDING CODE COMPLIANCE FOR ARCHITECTS', 'CUSTOM SOLID WOOD FURNITURE & TURNKEY LUXURY INTERIOR DESIGNING'),
        ('(BIM / Revit integration)', '(Nilambur Teak & Hardwood Specialists)'),
        ('(BIM / REVIT INTEGRATION)', '(NILAMBUR TEAK & HARDWOOD SPECIALISTS)'),
        ('1801 California St. Suite 2400 Denver, CO 80202', 'Mannuppadam, Eranhimangad P.O., Nilambur, Malappuram, Kerala - 679329 (Janardhanan: +91 9447 631 731 | Jithesh: +91 9656 663 063)'),
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

        # Hero Section
        ('Click and drag your mouse to see violations', 'Drag cursor to inspect artisan wood joinery & furniture proportions'),
        ('IBC 1015.3', 'AISWARYA INDUSTRIES'),
        ('Guardrail required for fall protection', 'Dealers in Wooden Furniture & Interior Designing'),
        ('IBC 1011.11', 'NILAMBUR, KERALA'),
        ('Handrails required.', 'Mannuppadam, Eranhimangad P.O. - 679329'),
        ('An AI agent that works inside your design tools', 'Handcrafted Wooden Furniture & Luxury Interior Designing'),
        ('Heron reviews your model, identifies issues, and proposes solutions. Upon approval, it edits automatically. This concept crafted by',
         'Aiswarya Industries brings master woodcraft and turnkey interior designing to life. We manufacture custom solid teak furniture, modular kitchens, and architectural woodwork tailored to your home.'),
        ('Bearplus agency', 'Aiswarya Industries, Nilambur'),
        ('Discover more', 'Explore Furniture'),
        ('Faster iterations', '100% Solid Teak'),
        ('Fewer mistakes', 'Master Joinery'),
        ('Less busywork', 'Turnkey Interiors'),

        # Intro Section
        ("THE REPETITIVE PARTS OF MODELLING SHOULDN'T EAT YOUR DAY. HERON HANDLES THE FIDDLY, MANUAL WORK SO YOU CAN STAY FOCUSED ON THE DESIGN, NOT THE SOFTWARE.",
         "YOUR HOME DESERVES LIFETIME SOLID WOOD, NOT FRAGILE VENEERS. AISWARYA INDUSTRIES CRAFTS BESPOKE WOODEN FURNITURE AND ENDURING INTERIORS FROM SEASONED NILAMBUR TEAK."),
        ('clients', 'Specialities'),
        ('Works natively inside the tools you already use, including Revit, Rhino, ArchiCAD and SketchUp.',
         'Delivering handcrafted wooden furniture, custom cabinetry, and turnkey interior designing across Nilambur, Malappuram, and all over Kerala.'),

        # Problem Section
        ('PROBLEMS', 'THE FURNITURE DILEMMA'),
        ('Your design tools do what you tell them, nothing more',
         'Commercial composite furniture sags, peels, and wears out. Solid wood endures for lifetimes.'),
        ("Design software is powerful but passive. It waits for every instruction, gives no advice, and can't act on its own, so all the repetitive work stays on you.",
         "Modern particle board and flat-pack MDF furniture fail under tropical moisture, bubbling at the edges within 3 to 5 years. Aiswarya Industries builds heirloom furniture and bespoke interiors with generational strength."),
        ('>Manual<', '>Swelling & Warping<'),
        ("You make each edit by hand, one at a time, even the ones you've done a hundred times before.",
         "Commercial modular boards absorb humidity, expand, and crumble around hinge screws, leaving costly damage."),
        ('>Disjointed<', '>Toxic Chemical Resins<'),
        ("Generic AI tools can't see your project, so you keep copying, pasting, and re-explaining the same context.",
         "Industrial engineered boards off-gas harmful VOCs and synthetic formaldehydes, degrading your family's indoor air quality."),
        ('>BLIND<', '>Rigid Store Sizes<'),
        ('Issues sit quietly in your model until you happen to spot them, if you spot them at all.',
         "Store-bought modular units never fit your home's exact room proportions, leaving awkward gaps, unaligned joints, and wasted space."),
        ('>SLOW<', '>Disposable Lifespans<'),
        ('The fiddly work that fills your week is exactly the work software should be doing for you.',
         "Cheap composite veneers force repetitive replacements. Real Nilambur hardwood from Aiswarya Industries lasts for generations."),

        # Blueprint / Map Section
        ('Right there with you', 'Master Woodcraft Details'),
        ('For the whole design', 'Precision Joinery & Natural Teak Grain'),
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

        # Platform Section
        ('RUN AN AGENT NATIVELY IN YOUR MODEL', 'BESPOKE FURNITURE & TURNKEY INTERIOR DESIGN'),
        ('Heron Chat widget', 'Custom Wooden Furniture Atelier'),
        ('A chat that floats over your design tool. Ask it about your model or tell it what to change, and it acts inside the software on your approval.',
         'Handcrafted living room sofa sets, solid wood dining tables, royal king beds, ergonomic office furniture, TV credenzas, and handcrafted accent pieces built to your exact specifications.'),
        ('Heron Dashboard', 'Turnkey Architectural Interior Designing'),
        ('Ask code questions about your building and get answers that reflect how the code applies to your layout, occupancy, and conditions, not just what the requirements say in isolation.',
         'Complete residential interior execution: modular solid teak kitchens, floor-to-ceiling wardrobes, wooden false ceilings, wall claddings, pooja units, and grand entrance doors with 3D space planning.'),

        # Why Us Section
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
        ('Learn', 'Installation & Polish'),
        ("It picks up your firm's standards and gets more useful over time",
         'White-glove delivery, seamless installation in your home, and hand-applied multi-coat protective finishes.'),

        # Use Cases
        ('USE CASES', 'INTERIOR PORTFOLIO'),
        ('MADE FOR THE PEOPLE IN THE MODEL', 'BESPOKE WOODWORK FOR EVERY LIVING SPACE'),
        ('MADE FOR', 'BESPOKE FOR'),
        ('THE PEOPLE IN', 'EVERY CORNER OF'),
        ('THE MODEL', 'YOUR HOME'),
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

        # CTA Section
        ('SEE WHAT HERON CAN DO IN YOUR MODEL', 'TRANSFORM YOUR HOME WITH AISWARYA INDUSTRIES'),
        ("Book a demo and we'll show Heron working inside one of your own projects.",
         "Get in touch with Janardhanan (+91 9447 631 731) or Jithesh (+91 9656 663 063) for a personalized wooden furniture and interior designing consultation for your home or project."),
        ('Contact us', 'Call: +91 9447 631 731'),

        # Footer Section
        ('An AI agent that works inside your design tools', 'Aiswarya Industries — Dealers in Wooden Furniture & Interior Designing, Nilambur'),
        ('Want to see more cool websites like this?', 'Looking to furnish your home with custom wooden interiors?'),
        ('Sign up for occasional updates from Bearplus.',
         'Contact Janardhanan: +91 9447 631 731 or Jithesh: +91 9656 663 063 for custom commissions.'),
        ('Subscribe', 'Contact Atelier'),
        ('Company', 'Aiswarya Industries'),
        ('About us', 'About Our Woodcraft'),
        ('Address', 'Workshop & Location'),
        ('Direction', 'Mannuppadam, Eranhimangad P.O., Nilambur, Malappuram, Kerala - 679329'),
        ('New business', 'Key Contacts'),
        ('business@bear.plus', 'Janardhanan: +91 9447 631 731'),
        ('General inquiries', 'Jithesh / Office'),
        ('hello@heronaiapp.com', '+91 9656 663 063 | +91 9961 858 798'),
        ('Bearplus', 'Aiswarya Industries, Nilambur'),
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
        aiswarya: {
          title: "Handcrafted Wooden Furniture & Luxury Interior Designing",
          sub: "Aiswarya Industries brings master woodcraft and turnkey interior designing to life. We manufacture custom solid teak furniture, modular kitchens, and architectural woodwork tailored to your home.",
          intro: "YOUR HOME DESERVES LIFETIME SOLID WOOD, NOT FRAGILE VENEERS. AISWARYA INDUSTRIES CRAFTS BESPOKE WOODEN FURNITURE AND ENDURING INTERIORS FROM SEASONED NILAMBUR TEAK.",
          cta: "TRANSFORM YOUR HOME WITH AISWARYA INDUSTRIES"
        },
        heron: {
          title: "An AI agent that works inside your design tools",
          sub: "Heron reviews your model, identifies issues, and proposes solutions. Upon approval, it edits automatically. This concept crafted by",
          intro: "THE REPETITIVE PARTS OF MODELLING SHOULDN'T EAT YOUR DAY. HERON HANDLES THE FIDDLY, MANUAL WORK SO YOU CAN STAY FOCUSED ON THE DESIGN, NOT THE SOFTWARE.",
          cta: "SEE WHAT HERON CAN DO IN YOUR MODEL"
        }
      };

      window.toggleCopyMode = function(mode) {
        const btnAiswarya = document.getElementById('btn-mode-aiswarya');
        const btnHeron = document.getElementById('btn-mode-heron');
        if (mode === 'aiswarya') {
          if (btnAiswarya) { btnAiswarya.style.background = '#e15c46'; btnAiswarya.style.color = '#fff'; }
          if (btnHeron) { btnHeron.style.background = 'transparent'; btnHeron.style.color = '#a0a0a0'; }
          updateCopy(copyData.aiswarya);
        } else {
          if (btnHeron) { btnHeron.style.background = '#e15c46'; btnHeron.style.color = '#fff'; }
          if (btnAiswarya) { btnAiswarya.style.background = 'transparent'; btnAiswarya.style.color = '#a0a0a0'; }
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
    <div id="aiswarya-hud-control" style="position: fixed; bottom: 24px; right: 24px; z-index: 999999; display: flex; align-items: center; gap: 10px; font-family: 'Geistmono', monospace; font-size: 11px;">
      <a href="tel:+919447631731" style="background: rgba(34, 197, 94, 0.9); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.2); color: #ffffff; padding: 8px 14px; border-radius: 6px; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; text-decoration: none; display: flex; align-items: center; gap: 6px; box-shadow: 0 4px 20px rgba(0,0,0,0.5);">
        Tel:  Call Janardhanan: +91 9447631731
      </a>
      <button id="skip-preloader-btn" onclick="window.skipPreloader()" style="background: rgba(18, 18, 18, 0.9); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border: 1px solid rgba(225, 92, 70, 0.5); color: #e15c46; padding: 8px 14px; border-radius: 6px; cursor: pointer; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; box-shadow: 0 4px 20px rgba(0,0,0,0.5);">
         Skip Intro
      </button>
      <div style="background: rgba(18, 18, 18, 0.9); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.15); padding: 4px; border-radius: 6px; display: flex; gap: 4px; box-shadow: 0 4px 20px rgba(0,0,0,0.5);">
        <button id="btn-mode-aiswarya" onclick="window.toggleCopyMode('aiswarya')" style="background: #e15c46; color: #ffffff; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">
          Aiswarya Industries
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

    print(f"Generated /public/nilambur.html and /public/index.html for Aiswarya Industries, length: {len(html_str)}")

if __name__ == '__main__':
    generate_site()
