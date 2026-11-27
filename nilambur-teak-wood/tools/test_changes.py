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
    page.goto('http://localhost:3005/nilambur.html', wait_until='load')
    time.sleep(1)
    page.evaluate('window.skipPreloader()')
    time.sleep(1)
    
    # Hide with CSS
    page.evaluate('''() => {
        const style = document.createElement('style');
        style.textContent = "home-problem-wrap, .home-problem-wrap, .home-problem { display: none !important; } .home-intel-inner { display: none !important; }";
        document.head.appendChild(style);
        if (window.ScrollTrigger) window.ScrollTrigger.refresh();
    }''')
    time.sleep(1)
    
    # Wheel scroll
    page.mouse.move(720, 500)
    page.mouse.wheel(0, 1000)
    time.sleep(2)
    
    status = page.evaluate('''() => {
        return {
            mainScroll: document.querySelector('.main-inner') ? document.querySelector('.main-inner').scrollTop : null,
            bodyScroll: document.body.scrollTop
        };
    }''')
    print('Status after CSS hide:', status)
    page.screenshot(path='/home/mullainathan/projects/nilambur-teak-wood/public/test-hide-problem.png')
    
    # Scroll further down to blueprint / map
    page.mouse.wheel(0, 1500)
    time.sleep(2)
    page.screenshot(path='/home/mullainathan/projects/nilambur-teak-wood/public/test-hide-blueprint.png')
    
    browser.close()
