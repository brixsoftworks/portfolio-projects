from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path='/home/mullainathan/.local/bin/google-chrome',
        headless=True,
        args=['--no-sandbox', '--disable-setuid-sandbox']
    )
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    page.on('pageerror', lambda err: print('PAGE ERROR:', err))
    
    print('Navigating to http://localhost:3005/ ...')
    page.goto('http://localhost:3005/', wait_until='load')
    time.sleep(1)
    page.evaluate('window.skipPreloader()')
    time.sleep(1)
    
    # Check 1: Is THE FURNITURE DILEMMA visible?
    dilemma_check = page.evaluate('''() => {
        const text = document.body.innerText;
        const problemEl = document.querySelector('home-problem-wrap, .home-problem');
        const intelEls = document.querySelectorAll('.home-intel-inner');
        return {
            hasFurnitureDilemma: text.includes('THE FURNITURE DILEMMA'),
            hasCommercialComposite: text.includes('Commercial composite furniture sags'),
            hasSwellingWarping: text.includes('Swelling & Warping'),
            hasToxicChemical: text.includes('Toxic Chemical Resins'),
            hasRigidStore: text.includes('Rigid Store Sizes'),
            hasDisposable: text.includes('Disposable Lifespans'),
            hasMasterWoodcraftDetails: text.includes('Master Woodcraft Details'),
            hasRightThereWithYou: text.includes('Right there with you'),
            hasForWholeDesign: text.includes('For the whole design'),
            problemElDisplay: problemEl ? window.getComputedStyle(problemEl).display : 'none',
            intelElsCount: intelEls.length
        };
    }''')
    print('Removal check results:', dilemma_check)
    
    # Capture scrolled transition from intro directly into blueprint
    page.mouse.move(720, 500)
    page.mouse.wheel(0, 1000)
    time.sleep(2)
    page.screenshot(path='/home/mullainathan/projects/nilambur-teak-wood/public/verified-intro-scroll.png')
    
    page.mouse.wheel(0, 1500)
    time.sleep(2)
    page.screenshot(path='/home/mullainathan/projects/nilambur-teak-wood/public/verified-blueprint-clean.png')
    
    # Scroll directly to footer to inspect the big animated Aiswarya graphic
    page.evaluate('''() => {
        const footer = document.querySelector('footer');
        if (footer) footer.scrollIntoView();
    }''')
    time.sleep(2)
    page.screenshot(path='/home/mullainathan/projects/nilambur-teak-wood/public/verified-footer-graphic.png')
    
    footer_check = page.evaluate('''() => {
        const footer = document.querySelector('footer');
        const img = document.querySelector('.footer-img-wrap img');
        const svgImg = document.querySelector('.footer-img-wrap image');
        return {
            footerImgSrc: img ? img.src : null,
            footerSvgImgHref: svgImg ? svgImg.getAttribute('href') : null,
            hasHeronInFooter: footer ? footer.innerText.toLowerCase().includes('heron') : false,
            footerTextSnippet: footer ? footer.innerText.slice(0, 300) : null
        };
    }''')
    print('Footer check results:', footer_check)
    
    browser.close()
