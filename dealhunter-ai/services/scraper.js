import * as cheerio from 'cheerio';

const UA_DESKTOP = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36';
const UA_MOBILE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1';
const UA_GOOGLEBOT = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)';

async function fetchPage(url, opts = {}) {
  const { timeout = 20000, mobile = false, googlebot = false, retries = 1 } = opts;
  for (let attempt = 0; attempt <= retries; attempt++) {
    if (attempt > 0) await new Promise(r => setTimeout(r, 1000 * attempt));
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeout);
    const ua = googlebot ? UA_GOOGLEBOT : (mobile ? UA_MOBILE : UA_DESKTOP);
    try {
      const resp = await fetch(url, {
        signal: controller.signal,
        headers: {
          'User-Agent': ua,
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'Accept-Language': 'en-US,en;q=0.9',
          'Cache-Control': 'no-cache',
        },
        redirect: 'follow',
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      return await resp.text();
    } catch (e) {
      clearTimeout(timer);
      if (attempt === retries) throw e;
    }
  }
}

function parsePrice(text) {
  const n = parseInt((text || '').replace(/[₹,]/g, ''), 10);
  return isNaN(n) ? 0 : n;
}

function cleanUrl(href) {
  if (!href) return '';
  if (!href.startsWith('http')) return '';
  return href.split('?')[0];
}

const RETAILERS = [
  {
    name: 'Amazon',
    searchUrl: q => `https://www.amazon.in/s?k=${encodeURIComponent(q)}`,
    approaches: [
      { mobile: true, googlebot: false },
      { mobile: false, googlebot: false },
      { mobile: false, googlebot: true },
    ],
    fetchOptions: { retries: 2, timeout: 25000 },
    productSelector: '[data-component-type="s-search-result"], .s-result-item',
    extract($, el) {
      const $el = $(el);
      const name = $el.find('h2').text().trim() || $el.find('h2 a span').text().trim();
      if (!name || name.length <= 3) return null;
      const href = $el.find('h2 a').attr('href') || $el.find('a').first().attr('href') || '';
      const ratingText = $el.find('i.a-icon-star-small span.a-icon-alt, i[class*="star"] span').first().text();
      const reviewText = $el.find('span.a-size-base.s-underline-text, span[data-a-size="base"]').first().text();
      return {
        name: name.substring(0, 100),
        price: parsePrice($el.find('span.a-price .a-offscreen').first().text()),
        originalPrice: parsePrice($el.find('span.a-price.a-text-price span.a-offscreen').first().text()),
        description: $el.find('div.a-color-secondary .a-size-base-plus, div.a-color-secondary .a-size-base').first().text().trim().substring(0, 200) || null,
        image: $el.find('img.s-image').attr('src') || $el.find('img').first().attr('src') || '',
        url: cleanUrl(href.startsWith('http') ? href : `https://www.amazon.in${href}`),
        rating: parseFloat((ratingText.match(/[\d.]+/) || [])[0]) || null,
        reviews: parseInt((reviewText.match(/\d[\d,]*/) || [''])[0].replace(/,/g, '')) || null,
      };
    },
  },
  {
    name: 'Flipkart',
    searchUrl: q => `https://www.flipkart.com/search?q=${encodeURIComponent(q)}`,
    approaches: [
      { mobile: false, googlebot: false },
      { mobile: true, googlebot: false },
    ],
    productSelector: 'div[data-id], div._75nlfW, div.tUxRFu, div.cPHDOP',
    extract($, el) {
      const $el = $(el);
      const brand = $el.find('div.Fo1I0b, [class*=brand]').first().text().trim();
      const name = $el.find('a.atJtCj, a[class*=title], a').first().text().trim();
      const fullName = brand ? `${brand} ${name}` : name;
      if (!fullName || fullName.length <= 3) return null;
      const href = $el.find('a').first().attr('href') || '';
      const ratingEl = $el.find('[class*=rating], div.gUuXy- span, span._2_R_DZ').first().text();
      return {
        name: fullName.substring(0, 100),
        price: parsePrice($el.find('div.hZ3P6w, [class*=price]').first().text()),
        originalPrice: parsePrice($el.find('div.yRaY8j, [class*=old-price], [class*=original]').first().text()),
        description: $el.find('div._2ZkDZ-').first().text().trim().substring(0, 200) || null,
        image: $el.find('img.MZeksS, img').first().attr('src') || '',
        url: cleanUrl(href.startsWith('http') ? href : `https://www.flipkart.com${href}`),
        rating: parseFloat((ratingEl.match(/[\d.]+/) || [])[0]) || null,
        reviews: null,
      };
    },
  },
  {
    name: 'Myntra',
    searchUrl: q => `https://www.myntra.com/${encodeURIComponent(q)}`,
    approaches: [
      { mobile: false, googlebot: false },
      { mobile: true, googlebot: false },
    ],
    parseHtml(html) {
      const names = [...html.matchAll(/"productName":"([^"]+)"/g)].map(m => m[1]);
      const prices = [...html.matchAll(/"price":([0-9.]+)/g)].map(m => parseFloat(m[1]));
      const mrps = [...html.matchAll(/"mrp":([0-9.]+)/g)].map(m => parseFloat(m[1]));
      const imgs = [...html.matchAll(/"searchImage":"([^"]+)"/g)].map(m => m[1].replace(/\\u002F/g, '/'));
      const uris = [...html.matchAll(/"landingPageUrl":"([^"]+)"/g)].map(m => m[1].replace(/\\u002F/g, '/'));
      const ratings = [...html.matchAll(/"rating":([\d.]+)/g)].map(m => parseFloat(m[1]));
      const reviews = [...html.matchAll(/"ratingCount":(\d+)/g)].map(m => parseInt(m[1]));
      const descs = [...html.matchAll(/"productDescription":"([^"]+)"/g)].map(m => m[1]);
      const items = [];
      for (let i = 0; i < Math.min(names.length, 20); i++) {
        const name = names[i];
        if (!name) continue;
        items.push({
          name: name.substring(0, 100),
          price: prices[i] ? Math.round(prices[i]) : 0,
          originalPrice: mrps[i] ? Math.round(mrps[i]) : 0,
          description: descs[i] ? descs[i].substring(0, 200) : null,
          image: imgs[i] || '',
          url: uris[i] ? `https://www.myntra.com/${uris[i]}` : '',
          rating: ratings[i] || null,
          reviews: reviews[i] || null,
        });
      }
      return items;
    },
  },
  {
    name: 'Ajio',
    searchUrl: q => `https://www.ajio.com/search/?text=${encodeURIComponent(q)}`,
    approaches: [
      { mobile: true, googlebot: false },
      { mobile: false, googlebot: false },
    ],
    parseHtml(html) {
      const $ = cheerio.load(html);
      const items = [];
      $('script[type="application/ld+json"]').each((_, s) => {
        try {
          const data = JSON.parse($(s).html());
          const elements = data['@type'] === 'ItemList' ? data.itemListElement
            : data['@graph'] ? data['@graph'].filter(g => g['@type'] === 'Product') : null;
          if (elements) {
            elements.forEach(item => {
              const name = item.name;
              const url = item.url;
              if (!name || !url || items.some(i => i.name === name)) return;
              let price = 0;
              let originalPrice = 0;
              if (item.offers) {
                const offer = Array.isArray(item.offers) ? item.offers[0] : item.offers;
                price = parsePrice(offer.price);
                if (offer.priceSpecification?.price) {
                  originalPrice = parsePrice(offer.priceSpecification.price);
                }
              }
              if (price === 0 && item.price) price = parsePrice(item.price);
              const image = item.image || '';
              const imageUrl = Array.isArray(image) ? image[0] : (typeof image === 'string' ? image : '');
              const agg = item.aggregateRating || {};
              items.push({
                name: name.substring(0, 100),
                price,
                originalPrice,
                description: item.description ? item.description.substring(0, 200) : null,
                image: imageUrl,
                url,
                rating: parseFloat(agg.ratingValue) || null,
                reviews: parseInt(agg.reviewCount) || null,
              });
            });
          }
        } catch (e) {}
      });
      if (items.length === 0) {
        $('[class*=product], [class*=item], article').each((_, el) => {
          const $el = $(el);
          const name = $el.find('[class*=name], [class*=title], h3, h2').first().text().trim();
          if (!name || name.length <= 3 || items.some(i => i.name === name)) return;
          const href = $el.find('a').first().attr('href') || '';
          items.push({
            name: name.substring(0, 100),
            price: parsePrice($el.find('[class*=price], .price, span:contains(₹)').first().text()),
            image: $el.find('img').first().attr('src') || '',
            url: href.startsWith('http') ? href : `https://www.ajio.com${href}`,
            rating: null,
            reviews: null,
          });
        });
      }
      return items;
    },
  },
  {
    name: 'TataCliq',
    searchUrl: q => `https://www.tatacliq.com/search/?searchCategory=all&text=${encodeURIComponent(q)}`,
    approaches: [
      { mobile: true, googlebot: false },
      { mobile: false, googlebot: false },
    ],
    productSelector: '.plpGridItem',
    extract($, el) {
      const $el = $(el);
      const brand = $el.find('.prdDesrpHed h3').first().text().trim();
      const name = $el.find('.prdInfoDesc h2').first().text().trim();
      const fullName = brand ? `${brand} ${name}` : name;
      if (!fullName || fullName.length <= 3) return null;
      const href = $el.find('a').first().attr('href') || '';
      return {
        name: fullName.substring(0, 100),
        price: parsePrice($el.find('.prdPrice').first().text()),
        originalPrice: parsePrice($el.find('.oldPricee').first().text()),
        description: null,
        image: $el.find('img').first().attr('src') || '',
        url: cleanUrl(href.startsWith('http') ? href : `https://www.tatacliq.com${href}`),
        rating: parseFloat(($el.find('.rating-value').first().text().match(/[\d.]+/) || [])[0]) || null,
        reviews: parseInt(($el.find('.ratingCount').text().match(/\d+/) || [])[0]) || null,
      };
    },
  },
  {
    name: 'Nykaa',
    searchUrl: q => `https://www.nykaa.com/search/result/?q=${encodeURIComponent(q)}`,
    approaches: [
      { mobile: true, googlebot: false },
      { mobile: false, googlebot: false },
    ],
    fetchOptions: { timeout: 30000 },
    productSelector: '[class*=product], [class*=css], div[data-testid*="product"], [class*=ProductContainer]',
    extract($, el) {
      const $el = $(el);
      const name = $el.find('[class*=name], [class*=title], a').first().text().trim();
      if (!name || name.length <= 3) return null;
      const href = $el.find('a').first().attr('href') || '';
      return {
        name: name.substring(0, 100),
        price: parsePrice($el.find('[class*=price], .price, span:contains(₹)').first().text()),
        image: $el.find('img').first().attr('src') || '',
        url: cleanUrl(href.startsWith('http') ? href : `https://www.nykaa.com${href}`),
        rating: null,
        reviews: null,
      };
    },
  },
];

async function scrapeRetailer(config, query) {
  for (const approach of config.approaches) {
    try {
      const html = await fetchPage(config.searchUrl(query), { ...config.fetchOptions, ...approach });
      let items = [];
      if (config.parseHtml) {
        items = config.parseHtml(html);
      } else if (config.extract) {
        const $ = cheerio.load(html);
        const selectors = (config.productSelector || '').split(',').map(s => s.trim());
        for (const sel of selectors) {
          $(sel).each((_, el) => {
            const product = config.extract($, el);
            if (product) items.push(product);
          });
          if (items.length > 0) break;
        }
      }
      if (items.length > 0) {
        const seen = new Set();
        items = items.filter(i => {
          if (!i.name || seen.has(i.name) || i.price >= 100000) return false;
          seen.add(i.name);
          return true;
        });
        const priced = items.filter(i => i.price > 0);
        const unpriced = items.filter(i => i.price <= 0);
        const result = [...priced, ...unpriced].slice(0, 10).map(p => ({ ...p, retailer: config.name }));
        const label = approach.googlebot ? 'googlebot' : (approach.mobile ? 'mobile' : 'desktop');
        console.log(`[Scraper] ${config.name} (${label}): found ${result.length} items`);
        return result;
      }
    } catch (e) {
      const label = approach.googlebot ? 'googlebot' : (approach.mobile ? 'mobile' : 'desktop');
      console.error(`[Scraper] ${config.name} (${label}) failed: ${e.message}`);
    }
  }
  return [];
}

function guessRetailer(url) {
  const u = url.toLowerCase();
  if (u.includes('amazon')) return 'Amazon';
  if (u.includes('flipkart')) return 'Flipkart';
  if (u.includes('myntra')) return 'Myntra';
  if (u.includes('ajio')) return 'Ajio';
  if (u.includes('tatacliq') || u.includes('tata')) return 'TataCliq';
  if (u.includes('nykaa')) return 'Nykaa';
  if (u.includes('nike')) return 'Nike';
  if (u.includes('adidas')) return 'Adidas';
  if (u.includes('puma')) return 'Puma';
  if (u.includes('croma')) return 'Croma';
  if (u.includes('reliance')) return 'Reliance Digital';
  if (u.includes('shopclues')) return 'ShopClues';
  if (u.includes('snapdeal')) return 'Snapdeal';
  if (u.includes('paytm')) return 'Paytm Mall';
  if (u.includes('meesho')) return 'Meesho';
  if (u.includes('lifestyle')) return 'Lifestyle';
  if (u.includes('shoppersstop')) return 'Shoppers Stop';
  return 'Online Store';
}

function roundRobinSelect(items, max) {
  const byRetailer = {};
  for (const r of items) {
    if (!byRetailer[r.retailer]) byRetailer[r.retailer] = [];
    byRetailer[r.retailer].push(r);
  }
  for (const key in byRetailer) {
    byRetailer[key].sort((a, b) => (a.price || 0) - (b.price || 0));
  }
  const keys = Object.keys(byRetailer);
  const selected = [];
  let exhausted = false;
  while (selected.length < max && !exhausted) {
    exhausted = true;
    for (const key of keys) {
      if (byRetailer[key].length > 0 && selected.length < max) {
        selected.push(byRetailer[key].shift());
        exhausted = false;
      }
    }
  }
  return selected;
}

export class ScraperService {
  static async scrapeTop10Sites(query) {
    console.log(`[Scraper] Starting scrape for: "${query}"`);
    console.log(`[Scraper] Targeting: ${RETAILERS.map(r => r.name).join(', ')}`);

    // Scrape all retailers in parallel; a failing source degrades gracefully
    // instead of slowing or blocking the others. Scrapers are inherently
    // fragile against anti-bot changes — by design we never fail the whole
    // request because one retailer broke.
    const settled = await Promise.allSettled(
      RETAILERS.map(config => scrapeRetailer(config, query))
    );

    const results = [];
    const failed = [];
    settled.forEach((outcome, i) => {
      if (outcome.status === 'fulfilled') {
        if (outcome.value.length > 0) results.push(...outcome.value);
      } else {
        failed.push(RETAILERS[i].name);
      }
    });
    if (failed.length > 0) {
      console.warn(`[Scraper] Sources unavailable this run: ${failed.join(', ')}`);
    }

    if (results.length > 0) {
      const selected = roundRobinSelect(results, 30);
      const retailers = [...new Set(selected.map(r => r.retailer))];
      console.log(`[Scraper] Total: ${results.length} products, returning ${selected.length} from ${retailers.join(', ')}`);
      return this.enrichWithIds(selected);
    }

    console.log('[Scraper] All methods failed, generating smart fallback');
    return this.generateSmartFallback(query);
  }

  static enrichWithIds(items) {
    return items.map((item, i) => ({
      id: `${item.retailer.substring(0, 3)}_${Date.now()}_${i}`,
      name: item.name,
      retailer: item.retailer,
      price: item.price,
      originalPrice: item.originalPrice || (item.price > 0 ? Math.round(item.price * 1.2) : 0),
      description: item.description || null,
      rating: item.rating || null,
      reviews: item.reviews || null,
      category: item.category || 'Search Result',
      image: item.image || `https://placehold.co/400x500/1a1a2e/e0e0e0?text=${encodeURIComponent(item.name.split(' ')[0])}`,
      url: item.url,
    }));
  }

  static generateSmartFallback(query) {
    const retailers = {
      'Amazon': `https://www.amazon.in/s?k=${encodeURIComponent(query)}`,
      'Flipkart': `https://www.flipkart.com/search?q=${encodeURIComponent(query)}`,
      'Myntra': `https://www.myntra.com/${encodeURIComponent(query)}`,
      'Ajio': `https://www.ajio.com/search/?text=${encodeURIComponent(query)}`,
    };
    return Object.entries(retailers).map(([name, url], i) => ({
      id: `fb_${i}_${Date.now()}`,
      name: `Browse "${query}" on ${name}`,
      retailer: name,
      price: 0,
      originalPrice: 0,
      rating: null,
      reviews: null,
      category: 'Search Result',
      image: `https://placehold.co/400x500/1a1a2e/e0e0e0?text=${encodeURIComponent(name)}`,
      url,
    }));
  }
}
