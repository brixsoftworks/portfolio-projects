import os
import re

builder_path = '/home/mullainathan/projects/nilambur-teak-wood/clean_aiswarya_builder.py'
with open(builder_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. HTML REPLACEMENT: Replace video element with Canvas element
html_start = "    # 6b. Insert Rolls-Royce Nilambur Teak 3D Exploded Fullscreen Showcase"
html_end = "    # Platform / Atelier Section:"

new_html_block = '''    # 6b. Insert Rolls-Royce Nilambur Teak 3D Exploded Fullscreen Canvas Engine (Pure Frame-by-Frame Architecture)
    intro_component = soup.find('home-intro-wrap')
    if intro_component:
        rr_section_html = \'\'\'
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

            <!-- Act 1: Initial Chassis Matrix -->
            <div class="rr-act-card" id="rrAct1">
              <div class="rr-act-tag">
                <span class="rr-tag-icon"></span>
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
                <span class="rr-tag-icon">*</span>
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
                <span class="rr-tag-icon"></span>
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
        </div>\'\'\'
        rr_soup = BeautifulSoup(rr_section_html, 'html.parser')
        intro_component.insert_after(rr_soup)

'''

pattern_html = re.escape(html_start) + r".*?" + re.escape(html_end)
assert re.search(pattern_html, content, re.DOTALL), "HTML pattern not found"
content = re.sub(pattern_html, new_html_block + "    " + html_end, content, flags=re.DOTALL)
print("1. HTML successfully updated to Canvas Engine.")

# 2. CSS REPLACEMENT: Canvas element styling
css_start = "      /* === ROLLS-ROYCE FULL-SCREEN 3D EXPLODED ARCHITECTURE === */"
css_end = "      /* === ADVANCED ELEMENT ANIMATIONS === */"

new_css = """      /* === ROLLS-ROYCE FULL-SCREEN 3D EXPLODED ARCHITECTURE (CANVAS ENGINE) === */
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
        font-size: 0.7rem !important;
        letter-spacing: 0.16em !important;
        color: rgba(239, 236, 230, 0.6) !important;
        text-transform: uppercase !important;
        font-weight: 600 !important;
        z-index: 4 !important;
        pointer-events: none !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 8px !important;
      }
      .rr-watermark.top-left { top: 32px; left: 56px; }
      .rr-watermark.top-right { top: 32px; right: 56px; }
      .rr-watermark.bottom-right { bottom: 32px; right: 56px; }
      .rr-dot-pulse {
        width: 6px !important;
        height: 6px !important;
        border-radius: 50% !important;
        background: #10b981 !important;
        box-shadow: 0 0 8px #10b981 !important;
        animation: heroPulse 1.8s infinite !important;
      }

      /* Act Narrative Cards */
      .rr-act-card {
        position: absolute !important;
        top: 50% !important;
        left: 64px !important;
        transform: translateY(-50%) !important;
        max-width: 540px !important;
        z-index: 5 !important;
        background: rgba(18, 16, 14, 0.84) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(217, 119, 6, 0.35) !important;
        border-radius: 14px !important;
        padding: 2.5rem !important;
        color: #efece6 !important;
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.6) !important;
        transition: opacity 0.35s ease, transform 0.35s ease !important;
      }
      .rr-act-card.right {
        left: auto !important;
        right: 64px !important;
      }
      .rr-act-tag {
        display: inline-flex !important;
        align-items: center !important;
        gap: 7px !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.14em !important;
        color: #f59e0b !important;
        text-transform: uppercase !important;
        margin-bottom: 0.85rem !important;
      }
      .rr-tag-icon {
        font-size: 0.9rem !important;
      }
      .rr-act-title {
        font-family: 'Fraktion Sans', sans-serif !important;
        font-size: 2.75rem !important;
        font-weight: 600 !important;
        line-height: 1.1 !important;
        letter-spacing: -0.03em !important;
        color: #ffffff !important;
        margin: 0 0 1.1rem 0 !important;
      }
      .rr-act-desc {
        font-size: 1.05rem !important;
        line-height: 1.65 !important;
        color: rgba(239, 236, 230, 0.85) !important;
        margin: 0 0 1.5rem 0 !important;
      }
      .rr-act-desc strong {
        color: #f59e0b !important;
      }

      /* Scroll Indicator in Act 1 */
      .rr-scroll-indicator {
        display: inline-flex !important;
        align-items: center !important;
        gap: 12px !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.12em !important;
        color: rgba(239, 236, 230, 0.65) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.12) !important;
        padding-top: 1.2rem !important;
        width: 100% !important;
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

      /* Metrics in Act 2 */
      .rr-metric-row {
        display: flex !important;
        gap: 12px !important;
        border-top: 1px solid rgba(255, 255, 255, 0.12) !important;
        padding-top: 1.2rem !important;
      }
      .rr-metric-pill {
        flex: 1 !important;
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
      }
      .p-num {
        font-family: 'Geistmono', monospace !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        color: #fa3600 !important;
      }
      .p-lbl {
        font-family: 'Geistmono', monospace !important;
        font-size: 0.62rem !important;
        letter-spacing: 0.06em !important;
        color: rgba(239, 236, 230, 0.7) !important;
        margin-top: 2px !important;
      }

      /* Badges in Act 3 */
      .rr-badge-row {
        display: grid !important;
        grid-template-columns: repeat(3, 1fr) !important;
        gap: 10px !important;
        border-top: 1px solid rgba(255, 255, 255, 0.12) !important;
        padding-top: 1.2rem !important;
      }
      .rr-spec-item {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
        padding: 8px !important;
        text-align: center !important;
      }
      .rr-spec-num {
        font-family: 'Geistmono', monospace !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        color: #fa3600 !important;
      }
      .rr-spec-label {
        font-family: 'Geistmono', monospace !important;
        font-size: 0.58rem !important;
        letter-spacing: 0.05em !important;
        color: rgba(239, 236, 230, 0.7) !important;
        margin-top: 3px !important;
      }

"""

pattern_css = re.escape(css_start) + r".*?" + re.escape(css_end)
assert re.search(pattern_css, content, re.DOTALL), "CSS pattern not found"
content = re.sub(pattern_css, new_css + "      " + css_end, content, flags=re.DOTALL)
print("2. CSS successfully updated to Canvas Engine.")

# 3. JS REPLACEMENT: Hardware-Accelerated Canvas Frame-by-Frame Scrubbing Engine
js_start = "      // === ROLLS-ROYCE FULL-SCREEN 3D EXPLODED SCROLL ENGINE ==="
js_end = "      // === 4. INTRO ARCHITECTURAL CALIPER SPLIT SLIDER ==="

new_js = """      // === ROLLS-ROYCE FULL-SCREEN 3D EXPLODED CANVAS ENGINE ===
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

            // Cinematic text transitions across 3 Acts
            const p = self.progress;
            if (p < 0.33) {
              const exit = p > 0.23 ? Math.max(0, 1 - (p - 0.23) / 0.1) : 1;
              if (act1) {
                act1.style.opacity = String(exit);
                act1.style.transform = `translateY(${-50 - (p * 40)}%)`;
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
                act2.style.transform = `translateY(${-50 + (1 - enter) * 20}%)`;
                act2.style.pointerEvents = op > 0.3 ? 'auto' : 'none';
              }
              if (act3) {
                act3.style.opacity = '0';
                act3.style.transform = 'translateY(-20%)';
                act3.style.pointerEvents = 'none';
              }
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
                act3.style.transform = `translateY(${-50 + (1 - enter) * 20}%)`;
                act3.style.pointerEvents = enter > 0.3 ? 'auto' : 'none';
              }
            }
          }
        });
      }

"""

pattern_js = re.escape(js_start) + r".*?" + re.escape(js_end)
assert re.search(pattern_js, content, re.DOTALL), "JS pattern not found"
content = re.sub(pattern_js, new_js + "      " + js_end, content, flags=re.DOTALL)
print("3. JS successfully updated to Canvas Engine.")

# 4. SCROLLTRIGGER INITIALIZER REPLACEMENT
st_start = "        // --- ROLLS-ROYCE FULL-SCREEN 3D EXPLODED PINNED SCROLL SCRUB ---"
st_end = "        setTimeout(() => {"

new_st = """        // --- ROLLS-ROYCE FULL-SCREEN 3D EXPLODED CANVAS ENGINE ---
        initRollsRoyceCanvasScrub();
"""

pattern_st = re.escape(st_start) + r".*?" + re.escape(st_end)
assert re.search(pattern_st, content, re.DOTALL), "ScrollTrigger initializer pattern not found"
content = re.sub(pattern_st, new_st + "        " + st_end, content, flags=re.DOTALL)
print("4. ScrollTrigger initializer successfully updated.")

with open(builder_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated clean_aiswarya_builder.py to Canvas Engine successfully!")
