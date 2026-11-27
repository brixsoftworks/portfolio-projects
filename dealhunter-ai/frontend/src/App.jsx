import { useState, useEffect, useRef, useCallback } from 'react';
import { motion } from 'motion/react';
import { Sparkles, Search, ArrowRight, Bot, User, ShoppingBag, Star, RotateCcw, ExternalLink, ArrowLeftRight, SearchCheck, WandSparkles, Zap, ArrowUpDown, X, Share2 } from 'lucide-react';
import './index.css';

function HexagonBackground() {
  const [grid, setGrid] = useState({ rows: 0, columns: 0 });

  useEffect(() => {
    const update = () => {
      const size = 75;
      const rowSpacing = size * 0.8;
      setGrid({
        rows: Math.ceil(window.innerHeight / rowSpacing),
        columns: Math.ceil(window.innerWidth / size) + 1,
      });
    };
    update();
    window.addEventListener('resize', update);
    return () => window.removeEventListener('resize', update);
  }, []);

  const hexSize = 75;
  const hexMargin = 3;
  const rowSpacing = hexSize * 0.8;
  const marginTop = -36 - 0.275 * (hexSize - 100) + hexMargin;

  return (
    <div className="hexagon-bg">
      {Array.from({ length: grid.rows }).map((_, rowIdx) => (
        <div
          key={`r-${rowIdx}`}
          className="hex-row"
          style={{
            marginTop,
            marginLeft: ((rowIdx + 1) % 2 === 0 ? hexMargin / 2 : -(hexSize / 2)) - 10,
          }}
        >
          {Array.from({ length: grid.columns }).map((_, colIdx) => (
            <div
              key={`h-${rowIdx}-${colIdx}`}
              className="hex-cell"
              style={{
                width: hexSize,
                height: hexSize * 1.1,
                marginLeft: hexMargin,
                marginRight: hexMargin,
                '--hue': `${((rowIdx * 37 + colIdx * 53) % 360)}`,
              }}
            />
          ))}
        </div>
      ))}
    </div>
  );
}

const heroWords = [
  { text: 'AI', size: '6rem', x: '8%', y: '15%', delay: '0s', duration: '22s' },
  { text: 'DEALS', size: '4rem', x: '75%', y: '10%', delay: '2s', duration: '28s' },
  { text: 'COMPARE', size: '3.5rem', x: '60%', y: '30%', delay: '4s', duration: '25s' },
  { text: 'SAVE', size: '5rem', x: '15%', y: '55%', delay: '1s', duration: '30s' },
  { text: 'AMAZON', size: '2.8rem', x: '80%', y: '65%', delay: '3s', duration: '26s' },
  { text: 'FLIPKART', size: '2.5rem', x: '5%', y: '78%', delay: '5s', duration: '24s' },
  { text: 'MYNTRA', size: '2.2rem', x: '50%', y: '50%', delay: '0.5s', duration: '32s' },
  { text: 'SMART', size: '3.2rem', x: '70%', y: '78%', delay: '3.5s', duration: '27s' },
  { text: 'PRICE', size: '3.8rem', x: '25%', y: '35%', delay: '1.5s', duration: '29s' },
  { text: 'SHOPPING', size: '2.8rem', x: '40%', y: '10%', delay: '6s', duration: '23s' },
  { text: 'INDIA', size: '3rem', x: '88%', y: '45%', delay: '2.5s', duration: '31s' },
  { text: 'BEST', size: '2.5rem', x: '35%', y: '70%', delay: '4.5s', duration: '26s' },
  { text: 'TRENDING', size: '2rem', x: '92%', y: '82%', delay: '7s', duration: '28s' },
  { text: 'BUDGET', size: '2.8rem', x: '45%', y: '88%', delay: '0.8s', duration: '25s' },
  { text: 'SEARCH', size: '2.2rem', x: '65%', y: '55%', delay: '5.5s', duration: '30s' },
  { text: 'DISCOUNTS', size: '2.5rem', x: '20%', y: '90%', delay: '3.2s', duration: '27s' },
];

function AnimatedBlobs() {
  const colors = [
    'rgba(99,102,241,0.15)',
    'rgba(168,85,247,0.12)',
    'rgba(34,211,238,0.1)',
    'rgba(244,114,182,0.1)',
    'rgba(251,191,36,0.08)',
    'rgba(52,211,153,0.08)',
  ];
  return (
    <div className="animated-blobs">
      <svg className="blob-svg">
        <defs>
          <filter id="blob-goo">
            <feGaussianBlur in="SourceGraphic" stdDeviation="40" result="blur" />
            <feColorMatrix in="blur" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 25 -10" result="goo" />
          </filter>
        </defs>
      </svg>
      <div className="blob-container" style={{ filter: 'url(#blob-goo)' }}>
        {colors.map((color, i) => (
          <motion.div
            key={i}
            className="blob"
            style={{
              background: `radial-gradient(circle at 30% 30%, ${color}, transparent 70%)`,
              width: `${30 + i * 8}%`,
              height: `${30 + i * 8}%`,
              top: `${10 + (i * 7) % 60}%`,
              left: `${10 + (i * 13) % 70}%`,
            }}
            animate={{
              x: [0, 60, -40, 30, 0],
              y: [0, -50, 30, -20, 0],
              scale: [1, 1.2, 0.9, 1.1, 1],
              rotate: [0, 10, -5, 8, 0],
            }}
            transition={{
              duration: 20 + i * 4,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: i * 0.5,
            }}
          />
        ))}
      </div>
    </div>
  );
}

const features = [
  { icon: WandSparkles, title: 'AI-Powered Search', desc: 'Describe what you want naturally and let AI refine your query for the best results.' },
  { icon: SearchCheck, title: 'Multi-Store Scanning', desc: 'Scans Amazon, Flipkart, Myntra, Ajio & more simultaneously in real-time.' },
  { icon: ArrowLeftRight, title: 'Smart Comparison', desc: 'Compare prices, ratings, and reviews across retailers to find the perfect deal.' },
  { icon: Zap, title: 'Lightning Fast', desc: 'Results appear seconds after your query. No endless scrolling through pages.' },
];

function FeatureCards() {
  return (
    <div className="feature-section">
      {features.map((f, i) => (
        <motion.div
          key={i}
          className="feature-card glass-panel"
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 + i * 0.12, duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
          whileHover={{ scale: 1.02, y: -4 }}
        >
          <div className="feature-icon-wrap">
            <div className="feature-icon-glow" />
            <div className="feature-icon">
              <f.icon size={22} />
            </div>
          </div>
          <div className="feature-title">{f.title}</div>
          <div className="feature-desc">{f.desc}</div>
        </motion.div>
      ))}
    </div>
  );
}

function HeroWords() {
  return (
    <div className="hero-words">
      {heroWords.map((w, i) => (
        <span
          key={i}
          className="hero-word"
          style={{
            '--x': w.x,
            '--y': w.y,
            '--size': w.size,
            '--delay': w.delay,
            '--duration': w.duration,
          }}
        >
          {w.text}
        </span>
      ))}
    </div>
  );
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001';

const RETAILER_CLASSES = {
  amazon: 'badge-amazon',
  flipkart: 'badge-flipkart',
  myntra: 'badge-myntra',
  ajio: 'badge-ajio'
};

const quickReplies = [
  "Show me the cheapest option",
  "What has the best ratings?",
  "Filter by Amazon only",
  "Sort by price low to high"
];

const SkeletonGrid = () => (
  <div className="skeleton-grid">
    {[1,2,3,4,5,6].map(i => (
      <div key={i} className="skeleton-card">
        <div className="skeleton-img" />
        <div className="skeleton-text" />
        <div className="skeleton-text short" />
        <div className="skeleton-text price" />
      </div>
    ))}
  </div>
);

function App() {
  const [sessionId] = useState(() => Math.random().toString(36).substring(7));
  const [chatMessages, setChatMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isScraping, setIsScraping] = useState(false);
  const [searchResults, setSearchResults] = useState(null);
  const [aiSummary, setAiSummary] = useState('');
  const [selectedRetailers, setSelectedRetailers] = useState([]);
  const [maxPrice, setMaxPrice] = useState(20000);
  const [sortBy, setSortBy] = useState('default');
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [isWaiting, setIsWaiting] = useState(false);
  const [mousePos, setMousePos] = useState({ x: -200, y: -200 });

  const chatEndRef = useRef(null);
  const cursorRef = useRef(null);

  const handleMouseMove = useCallback((e) => {
    setMousePos({ x: e.clientX, y: e.clientY });
    if (cursorRef.current) {
      cursorRef.current.style.transform = `translate(${e.clientX - 150}px, ${e.clientY - 150}px)`;
    }
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const handleSend = async (text) => {
    const msg = text || inputValue;
    if (!msg?.trim()) return;
    setInputValue('');
    setIsWaiting(true);
    setChatMessages(prev => [...prev, { role: 'user', content: msg }]);

    try {
      const res = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sessionId, message: msg })
      });
      const data = await res.json();

      setChatMessages(prev => [...prev, { role: 'ai', content: data.reply }]);

      if (data.isSearchReady) {
        handleScrape(data.searchQuery);
      }
    } catch (err) {
      console.error('Chat error', err);
      setChatMessages(prev => [...prev, { role: 'ai', content: "Sorry, I ran into an issue. Could you try again?" }]);
    } finally {
      setIsWaiting(false);
    }
  };

  const handleScrape = async (query) => {
    setIsScraping(true);
    setSearchResults(null);
    try {
      const res = await fetch(`${API_URL}/api/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      const data = await res.json();
      if (data.success) {
        setTimeout(() => {
          setSearchResults(data.results);
          setAiSummary(data.summary);
          setIsScraping(false);
        }, 800);
      }
    } catch (err) {
      console.error('Scrape error', err);
      setIsScraping(false);
    }
  };

  const handleNewSearch = () => {
    setChatMessages([]);
    setSearchResults(null);
    setAiSummary('');
    setSelectedRetailers([]);
    setMaxPrice(20000);
    setSortBy('default');
    setInputValue('');
  };

  const toggleRetailer = (retailer) => {
    setSelectedRetailers(prev =>
      prev.includes(retailer) ? prev.filter(r => r !== retailer) : [...prev, retailer]
    );
  };

  const filteredResults = searchResults?.filter(item => {
    if (selectedRetailers.length > 0 && !selectedRetailers.includes(item.retailer)) return false;
    if (item.price > maxPrice) return false;
    return true;
  }).sort((a, b) => {
    if (sortBy === 'price-asc') return (a.price || 999999) - (b.price || 999999);
    if (sortBy === 'price-desc') return (b.price || 0) - (a.price || 0);
    if (sortBy === 'rating') return (b.rating || 0) - (a.rating || 0);
    return 0;
  });

  const allRetailers = searchResults ? [...new Set(searchResults.map(r => r.retailer))] : [];

  const getBadgeClass = (retailer) => {
    const key = retailer?.toLowerCase();
    return RETAILER_CLASSES[key] || 'badge-nbt';
  };

  const closeDetailPanel = useCallback(() => setSelectedProduct(null), []);

  useEffect(() => {
    if (!selectedProduct) return;
    const onKey = (e) => { if (e.key === 'Escape') closeDetailPanel(); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [selectedProduct, closeDetailPanel]);

  const handleShare = async (product) => {
    const text = `Check out ${product.name} at ₹${product.price.toLocaleString()} on ${product.retailer}!`;
    if (navigator.share) {
      try { await navigator.share({ title: product.name, text, url: product.url }); } catch {}
    } else {
      try { await navigator.clipboard.writeText(text + ' ' + product.url); } catch {}
    }
  };

  const discount = selectedProduct && selectedProduct.originalPrice > selectedProduct.price
    ? Math.round((1 - selectedProduct.price / selectedProduct.originalPrice) * 100)
    : 0;

  return (
    <div className="app-container" onMouseMove={handleMouseMove}>
      <HexagonBackground />
      <AnimatedBlobs />
      <HeroWords />
      <div className="color-blend" />
      <div className="orb orb-1" />
      <div className="orb orb-2" />
      <div className="stars" />
      <div className="dust-layer" />
      <div className="aurora" />
      <div className="cursor-glow" ref={cursorRef} style={{ transform: `translate(${mousePos.x - 150}px, ${mousePos.y - 150}px)` }} />

      <header className="header">
        <div className="logo">
          <span className="logo-icon"><Sparkles size={18} /></span>
          DealHunter AI
        </div>
        <div className="status-badge">
          <span className="status-dot" />
          {searchResults ? `${filteredResults.length} deals` : 'Ready'}
        </div>
      </header>

      <main className={`search-container ${searchResults || isScraping ? 'active-mode' : ''}`}>
        {!searchResults && !isScraping && chatMessages.length === 0 && (
          <>
            <h1 className="hero-title">Discover the perfect deal.</h1>
            <div className="hero-rotator">
              <span className="hero-tagline">AI-Powered Price Comparison</span>
              <span className="hero-tagline">Amazon &bull; Flipkart &bull; Myntra &bull; Ajio</span>
              <span className="hero-tagline">Real-Time Deal Scanning</span>
              <span className="hero-tagline">Smart Shopping, Zero Effort</span>
            </div>
            <p className="hero-subtitle">Describe what you want — I'll refine your search and instantly fetch the best options from India's top e-commerce sites.</p>
            <FeatureCards />
          </>
        )}

        <div className="glass-panel chat-box">
          {chatMessages.length > 0 && (
            <div className="chat-history">
              {chatMessages.map((msg, idx) => (
                <div key={idx} className={`chat-msg ${msg.role}`}>
                  <div className="chat-sender">
                    {msg.role === 'ai' ? <><Bot size={13} /> AI Assistant</> : <><User size={13} /> You</>}
                  </div>
                  {msg.content}
                </div>
              ))}
              {isWaiting && (
                <div className="chat-msg ai">
                  <div className="chat-sender"><Bot size={13} /> AI Assistant</div>
                  <div className="typing-indicator">
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>
          )}

          {!isScraping && !searchResults && (
            <>
              <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="chat-input-wrapper">
                <Search className="chat-icon-left" size={20} />
                <input
                  type="text"
                  className="chat-input"
                  placeholder="What are you looking to buy today?"
                  value={inputValue}
                  onChange={e => setInputValue(e.target.value)}
                  autoFocus
                />
                <button type="submit" className="chat-submit" disabled={!inputValue.trim() || isWaiting}>
                  <ArrowRight size={18} />
                </button>
              </form>
              {chatMessages.length > 0 && (
                <div className="quick-chips">
                  {quickReplies.map((chip, i) => (
                    <button key={i} className="chip" onClick={() => handleSend(chip)}>
                      {chip}
                    </button>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </main>

      {isScraping && (
        <div className="loading-overlay">
          <div className="scraping-status">
            <div className="spinner" />
            Dispatching Scraping Fleet...
          </div>
          <p className="scraping-sub">Scanning Amazon, Flipkart, Myntra, Ajio, and more...</p>
          <SkeletonGrid />
        </div>
      )}

      {searchResults && !isScraping && (
        <div className="dashboard">
          <aside className="sidebar glass-panel">
            <div className="filter-section">
              <div className="filter-title">
                Retailers
                <span className="filter-count">{selectedRetailers.length || 'All'}</span>
              </div>
              <div className="filter-group">
                {allRetailers.map(ret => (
                  <label key={ret} className="filter-label">
                    <input
                      type="checkbox"
                      className="filter-checkbox"
                      checked={selectedRetailers.includes(ret)}
                      onChange={() => toggleRetailer(ret)}
                    />
                    {ret}
                  </label>
                ))}
              </div>
            </div>

            <div className="filter-section">
              <div className="filter-title">Max Price</div>
              <div className="slider-header">
                <span className="slider-value">₹{maxPrice.toLocaleString()}</span>
                {maxPrice >= 50000 && <span style={{fontSize: '0.75rem', color: 'var(--text-secondary)'}}>No limit</span>}
              </div>
              <input
                type="range"
                min="500"
                max="50000"
                step="500"
                value={maxPrice}
                onChange={e => setMaxPrice(Number(e.target.value))}
              />
            </div>

            <div className="filter-section">
              <div className="filter-title"><ArrowUpDown size={14} /> Sort By</div>
              <div className="sort-group">
                {[
                  { value: 'default', label: 'Default' },
                  { value: 'price-asc', label: 'Price Low' },
                  { value: 'price-desc', label: 'Price High' },
                  { value: 'rating', label: 'Rating' },
                ].map(opt => (
                  <button
                    key={opt.value}
                    className={`sort-btn ${sortBy === opt.value ? 'active' : ''}`}
                    onClick={() => setSortBy(opt.value)}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            <button className="btn-new-search" onClick={handleNewSearch} style={{marginTop: 'auto', width: '100%', justifyContent: 'center'}}>
              <RotateCcw size={14} /> New Search
            </button>
          </aside>

          <section className="results-area">
            <div className="ai-summary">
              <div className="ai-summary-header">
                <Sparkles size={18} /> AI Shopping Insights
              </div>
              <p>{aiSummary}</p>
            </div>

            <div className="results-header">
              <h2 className="results-title">Top Picks for You</h2>
              <div className="deals-count">
                <ShoppingBag size={14} />
                {filteredResults.length} deal{filteredResults.length !== 1 ? 's' : ''} found
              </div>
            </div>

            {filteredResults.length === 0 ? (
              <div className="glass-panel empty-state">
                <div className="empty-state-icon">
                  <Search size={24} />
                </div>
                <p className="empty-state-text">No products match your filters</p>
                <p className="empty-state-hint">Try adjusting your price range or selecting different retailers</p>
              </div>
            ) : (
              <div className="product-grid">
                {filteredResults.map((product, idx) => (
                  <div
                    key={product.id}
                    className="glass-panel product-card"
                    style={{ animationDelay: `${idx * 0.06}s` }}
                    onClick={() => setSelectedProduct(product)}
                  >
                    <span className={`product-retailer-badge ${getBadgeClass(product.retailer)}`}>
                      {product.retailer}
                    </span>
                    <div className="product-image-container">
                      <img src={product.image} alt={product.name} className="product-image" loading="lazy" />
                      <div className="product-image-overlay">
                        <a href={product.url} target="_blank" rel="noreferrer" className="overlay-btn" onClick={e => e.stopPropagation()}>
                          <ExternalLink size={14} /> View Deal
                        </a>
                      </div>
                    </div>
                    <div className="product-details">
                      <div className="product-meta">
                        <span className="category-tag">{product.category}</span>
                        {product.rating && (
                          <div className="product-rating">
                            <Star size={13} className="star-icon" /> {product.rating}
                          </div>
                        )}
                      </div>
                      <h3 className="product-name" title={product.name}>{product.name}</h3>
                      {product.reviews && <div className="product-reviews">{product.reviews.toLocaleString()} reviews</div>}

                      <div className="product-price-row">
                        <div className="price-block">
                          {product.price > 0 ? (
                            <>
                              <div className="product-price">₹{product.price.toLocaleString()}</div>
                              {product.originalPrice > product.price && (
                                <div className="product-original-price">₹{product.originalPrice.toLocaleString()}</div>
                              )}
                            </>
                          ) : (
                            <div className="product-price" style={{fontSize: '1rem', opacity: 0.6}}>Price N/A</div>
                          )}
                        </div>
                        <a href={product.url} target="_blank" rel="noreferrer" className="btn-buy">
                          <ShoppingBag size={15} /> Buy
                        </a>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>
      )}

      {selectedProduct && (
        <div className="detail-overlay" onClick={closeDetailPanel}>
          <div className="detail-panel" onClick={e => e.stopPropagation()}>
            <div className="detail-header">
              <span className={`product-retailer-badge ${getBadgeClass(selectedProduct.retailer)}`}>
                {selectedProduct.retailer}
              </span>
              <button className="detail-close" onClick={closeDetailPanel}>
                <X size={20} />
              </button>
            </div>
            <div className="detail-image-container">
              <img src={selectedProduct.image} alt={selectedProduct.name} className="detail-image" />
            </div>
            <div className="detail-body">
              <h2 className="detail-name">{selectedProduct.name}</h2>

              <div className="detail-price-row">
                <span className="detail-price">₹{selectedProduct.price.toLocaleString()}</span>
                {selectedProduct.originalPrice > selectedProduct.price && (
                  <>
                    <span className="detail-original-price">₹{selectedProduct.originalPrice.toLocaleString()}</span>
                    <span className="detail-discount">-{discount}%</span>
                  </>
                )}
              </div>

              {selectedProduct.rating && (
                <div className="detail-rating">
                  <Star size={16} className="star-icon" /> {selectedProduct.rating}
                  {selectedProduct.reviews && <span className="detail-reviews"> &middot; {selectedProduct.reviews.toLocaleString()} reviews</span>}
                </div>
              )}

              <div className="detail-category">{selectedProduct.category}</div>

              {selectedProduct.description && (
                <div className="detail-description">{selectedProduct.description}</div>
              )}

              <div className="detail-actions">
                <a href={selectedProduct.url} target="_blank" rel="noreferrer" className="btn-buy detail-buy">
                  <ExternalLink size={16} /> View on {selectedProduct.retailer}
                </a>
                <button className="btn-share" onClick={() => handleShare(selectedProduct)}>
                  <Share2 size={16} /> Share
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
