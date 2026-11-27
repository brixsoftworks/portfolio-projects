/* --- smooth-scroll.js --- */
(() => {
  "use strict";

  function throttle(fn, delay) {
    let last = 0;
    return (...args) => {
      const now = Date.now();
      if (now - last >= delay) {
        last = now;
        fn(...args);
      }
    };
  }

  const SmoothScroll = {
    init() {
      const container = document.querySelector("[data-scroll-container]");
      if (!container) return;

      document.body.style.overflow = "";
      document.documentElement.style.overflow = "";
      document.body.style.height = "";
      document.documentElement.style.height = "";
      container.style.willChange = "";

      const updateScrollbar = () => {
        const bar = document.getElementById("brix-scrollbar");
        if (!bar) return;
        const doc = document.documentElement;
        const scrollTop = window.scrollY || doc.scrollTop;
        const scrollHeight = doc.scrollHeight - window.innerHeight;
        if (scrollHeight <= 0) {
          bar.style.height = "0";
          return;
        }
        const progress = scrollTop / scrollHeight;
        const trackHeight = bar.parentElement.offsetHeight;
        const thumbHeight = Math.max(
          30,
          trackHeight * (window.innerHeight / doc.scrollHeight),
        );
        bar.style.height = thumbHeight + "px";
        bar.style.transform = `translateY(${progress * (trackHeight - thumbHeight)}px)`;
      };

      const updateScroll = () => {
        const progress =
          document.documentElement.scrollHeight > window.innerHeight
            ? window.scrollY /
              (document.documentElement.scrollHeight - window.innerHeight)
            : 0;
        window.dispatchEvent(
          new CustomEvent("brix-scroll", {
            detail: { y: window.scrollY, progress },
          }),
        );
        updateScrollbar();
      };

      window.addEventListener("scroll", throttle(updateScroll, 16), {
        passive: true,
      });

      window.__brixScroll = {
        get scrollY() {
          return window.scrollY;
        },
        get scrollProgress() {
          const doc = document.documentElement;
          return doc.scrollHeight > window.innerHeight
            ? window.scrollY / (doc.scrollHeight - window.innerHeight)
            : 0;
        },
        scrollTo: (y) => {
          window.scrollTo({ top: y, behavior: "smooth" });
        },
      };

      const track = document.createElement("div");
      track.id = "brix-scrollbar-track";
      track.style.cssText =
        "position:fixed;top:0;right:0;width:4px;height:100%;z-index:9998;pointer-events:none;";
      const bar = document.createElement("div");
      bar.id = "brix-scrollbar";
      bar.style.cssText =
        "position:absolute;top:0;left:0;width:100%;background:linear-gradient(180deg,rgba(56,189,248,0.3),rgba(168,85,247,0.3));border-radius:2px;transition:opacity 0.3s ease,height 0.1s ease;opacity:0;box-shadow:0 0 8px rgba(56,189,248,0.1);";
      track.appendChild(bar);

      let hideTimeout = null;
      const showBar = () => {
        bar.style.opacity = "1";
        if (hideTimeout) clearTimeout(hideTimeout);
        hideTimeout = setTimeout(() => {
          bar.style.opacity = "0";
        }, 1500);
      };

      window.addEventListener("scroll", showBar, { passive: true });
      window.addEventListener("wheel", showBar, { passive: true });
      document.addEventListener("touchmove", showBar, { passive: true });

      document.body.appendChild(track);
      updateScrollbar();
      updateScroll();
    },
  };

  const ready = () => {
    document.removeEventListener("DOMContentLoaded", ready);
    document.removeEventListener("load", ready);
    SmoothScroll.init();
  };

  document.addEventListener("DOMContentLoaded", ready);
  window.addEventListener("load", ready);
})();
/* --- effects.js --- */
(() => {
  "use strict";

  const mouse = { x: -1000, y: -1000, clientX: -1000, clientY: -1000 };
  let scrollProgress = 0;
  let ticking = false;

  document.addEventListener("mousemove", (e) => {
    mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
    mouse.y = (e.clientY / window.innerHeight) * 2 - 1;
    mouse.clientX = e.clientX;
    mouse.clientY = e.clientY;
  });

  document.addEventListener(
    "scroll",
    () => {
      if (!ticking) {
        requestAnimationFrame(() => {
          scrollProgress = window.__brixScroll
            ? window.__brixScroll.scrollProgress
            : window.scrollY /
              (document.documentElement.scrollHeight - window.innerHeight);
          ticking = false;
        });
        ticking = true;
      }
    },
    { passive: true },
  );

  // ── Grid Background (enhanced) ──
  class GridBackground {
    constructor(canvas) {
      this.canvas = canvas;
      this.ctx = canvas.getContext("2d");
      this.spacing = 48;
      this.dots = [];
      this.connectRadius = 180;
      this.animationId = null;

      this.resize();
      this.initDots();
      window.addEventListener("resize", () => this.resize());
    }

    resize() {
      const dpr = window.devicePixelRatio || 1;
      const w = window.innerWidth;
      const h = window.innerHeight;
      this.canvas.width = w * dpr;
      this.canvas.height = h * dpr;
      this.canvas.style.width = w + "px";
      this.canvas.style.height = h + "px";
      this.ctx.scale(dpr, dpr);
      this.cols = Math.ceil(w / this.spacing);
      this.rows = Math.ceil(h / this.spacing);
      this.initDots();
    }

    initDots() {
      this.dots = [];
      for (let y = 0; y < this.rows; y++) {
        for (let x = 0; x < this.cols; x++) {
          this.dots.push({
            ox: x * this.spacing,
            oy: y * this.spacing,
            x: x * this.spacing,
            y: y * this.spacing,
            cx: x / this.cols,
            cy: y / this.rows,
            phase: Math.random() * Math.PI * 2,
          });
        }
      }
    }

    animate(time) {
      const ctx = this.ctx;
      const w = window.innerWidth;
      const h = window.innerHeight;
      ctx.clearRect(0, 0, w, h);

      const mX = mouse.clientX;
      const mY = mouse.clientY;
      const scrollWave = scrollProgress * Math.PI * 4;
      const t = time * 0.0002;

      // First pass: update dot positions
      for (const d of this.dots) {
        const dx = d.ox - mX;
        const dy = d.oy - mY;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const influence = Math.max(0, 1 - dist / 220);
        const waveX = Math.sin(d.cx * 8 + scrollWave + t) * 4;
        const waveY = Math.cos(d.cy * 8 + scrollWave + t * 0.8) * 4;
        const pushX = influence * dx * 0.1;
        const pushY = influence * dy * 0.1;
        const pulse = Math.sin(t * 2 + d.phase) * 1.5;
        d.x = d.ox + pushX + waveX + pulse;
        d.y = d.oy + pushY + waveY + pulse * 0.5;
      }

      // Draw mouse connections
      for (const d of this.dots) {
        const dx = d.x - mX;
        const dy = d.y - mY;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < this.connectRadius) {
          const alpha = (1 - dist / this.connectRadius) * 0.35;
          ctx.beginPath();
          ctx.moveTo(d.x, d.y);
          ctx.lineTo(mX, mY);
          ctx.strokeStyle = `rgba(0, 200, 255, ${alpha})`;
          ctx.lineWidth = 0.5 + (1 - dist / this.connectRadius) * 1;
          ctx.stroke();
        }
      }

      // Draw inter-dot connections (clusters)
      const maxClusterDist = 80;
      for (let i = 0; i < this.dots.length; i += 4) {
        const a = this.dots[i];
        for (let j = i + 1; j < this.dots.length; j += 3) {
          const b = this.dots[j];
          const dx = a.x - b.x;
          const dy = a.y - b.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < maxClusterDist) {
            const alpha = (1 - dist / maxClusterDist) * 0.12;
            const hue = 200 + Math.sin(t * 0.5 + a.cx * 3 + b.cy * 3) * 30;
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.strokeStyle = `hsla(${hue}, 80%, 70%, ${alpha})`;
            ctx.lineWidth = 0.3;
            ctx.stroke();
          }
        }
      }

      // Draw dots
      const maxCenterDist = Math.sqrt((w / 2) ** 2 + (h / 2) ** 2);
      for (const d of this.dots) {
        const dx = d.x - mX;
        const dy = d.y - mY;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const influence = Math.max(0, 1 - dist / 200);
        const distFromCenter = Math.sqrt((d.x - w / 2) ** 2 + (d.y - h / 2) ** 2);
        const centerGlow = Math.max(0.15, 1 - distFromCenter / maxCenterDist);
        const baseSize = 1.2 + influence * 2 + centerGlow * 1.2 + Math.sin(t * 3 + d.phase) * 0.3;
        const alpha = Math.min(1, (0.25 + influence * 0.75) * Math.max(0.3, centerGlow));
        const hue = 200 + influence * 50 + centerGlow * 30 + Math.sin(t * 0.5 + d.phase) * 20;

        ctx.beginPath();
        ctx.arc(d.x, d.y, baseSize, 0, Math.PI * 2);
        ctx.fillStyle = `hsla(${hue}, 100%, 70%, ${alpha})`;
        ctx.fill();

        if (centerGlow > 0.4) {
          ctx.beginPath();
          ctx.arc(d.x, d.y, baseSize * 3, 0, Math.PI * 2);
          ctx.fillStyle = `hsla(${hue + 20}, 100%, 60%, ${alpha * 0.1 * centerGlow})`;
          ctx.fill();
        }
      }

      this.animationId = requestAnimationFrame((t) => this.animate(t));
    }

    start() {
      if (this.animationId) cancelAnimationFrame(this.animationId);
      this.animationId = requestAnimationFrame((t) => this.animate(t));
    }

    stop() {
      if (this.animationId) {
        cancelAnimationFrame(this.animationId);
        this.animationId = null;
      }
    }
  }

  // ── HeroMesh: Flowing 3D Gradient Mesh ──
  class HeroMesh {
    constructor(canvas) {
      this.canvas = canvas;
      this.ctx = canvas.getContext("2d");
      this.rows = 20;
      this.cols = 30;
      this.points = [];
      this.animationId = null;
      this.time = 0;

      this.resize();
      this.initMesh();
      window.addEventListener("resize", () => this.resize());
    }

    resize() {
      const dpr = window.devicePixelRatio || 1;
      const w = window.innerWidth;
      const h = window.innerHeight;
      this.canvas.width = w * dpr;
      this.canvas.height = h * dpr;
      this.canvas.style.width = w + "px";
      this.canvas.style.height = h + "px";
      this.ctx.scale(dpr, dpr);
      this.w = w;
      this.h = h;
      this.cellW = w / (this.cols - 1);
      this.cellH = h / (this.rows - 1);
    }

    initMesh() {
      this.points = [];
      for (let r = 0; r < this.rows; r++) {
        for (let c = 0; c < this.cols; c++) {
          this.points.push({
            ox: c * this.cellW,
            oy: r * this.cellH,
            x: c * this.cellW,
            y: r * this.cellH,
            cx: c / (this.cols - 1),
            cy: r / (this.rows - 1),
          });
        }
      }
    }

    animate(t) {
      const ctx = this.ctx;
      const w = this.w;
      const h = this.h;
      this.time = t * 0.00015;
      const scrollWave = scrollProgress * Math.PI * 2;

      ctx.clearRect(0, 0, w, h);

      const mX = mouse.clientX;
      const mY = mouse.clientY;

      for (const p of this.points) {
        const dx = p.ox - mX;
        const dy = p.oy - mY;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const mouseInf = Math.max(0, 1 - dist / 300);
        const wave1 = Math.sin(p.cx * 6 + p.cy * 4 + this.time * 1.5 + scrollWave) * 25;
        const wave2 = Math.cos(p.cx * 5 - p.cy * 7 + this.time * 1.2) * 20;
        const wave3 = Math.sin((p.cx + p.cy) * 8 + this.time * 2) * 15;
        const pushX = mouseInf * dx * 0.1;
        const pushY = mouseInf * dy * 0.1;
        p.x = p.ox + wave1 + wave2 * 0.5 + pushX;
        p.y = p.oy + wave3 + wave2 * 0.3 + pushY;
      }

      const palette = [220, 240, 285, 300, 15, 35];
      const hueFromPos = (cx, cy) => {
        const idx = (Math.floor(cx * 3 + cy * 2) + Math.floor(this.time * 0.3)) % palette.length;
        return palette[idx] + ((cx * 15 + cy * 10) % 20);
      };

      for (let r = 0; r < this.rows - 1; r++) {
        for (let c = 0; c < this.cols - 1; c++) {
          const idx = r * this.cols + c;
          const p00 = this.points[idx];
          const p10 = this.points[idx + 1];
          const p01 = this.points[idx + this.cols];
          const p11 = this.points[idx + this.cols + 1];

          const centerX = (p00.x + p10.x + p01.x + p11.x) / 4;
          const centerY = (p00.y + p10.y + p01.y + p11.y) / 4;

          const mDist = Math.sqrt((centerX - mX) ** 2 + (centerY - mY) ** 2);
          const mGlow = Math.max(0, 1 - mDist / 400);

          const hue = (hueFromPos(p00.cx, p00.cy) + mGlow * 20) % 360;
          const sat = 70 + mGlow * 20;
          const lig = 12 + Math.sin(centerX * 0.005 + this.time) * 5 + mGlow * 15;

          ctx.beginPath();
          ctx.moveTo(p00.x, p00.y);
          ctx.lineTo(p10.x, p10.y);
          ctx.lineTo(p11.x, p11.y);
          ctx.lineTo(p01.x, p01.y);
          ctx.closePath();

          ctx.fillStyle = `hsla(${hue}, ${sat}%, ${lig}%, 0.45)`;
          ctx.fill();

          if (mGlow > 0.3) {
            ctx.fillStyle = `hsla(${hue + 20}, ${sat}%, ${lig + 10}%, ${mGlow * 0.2})`;
            ctx.fill();
          }
        }
      }

      ctx.lineWidth = 0.5;
      for (const p of this.points) {
        const alpha = 0.08 + Math.sin(p.x * 0.01 + this.time) * 0.04;
        ctx.beginPath();
        ctx.arc(p.x, p.y, 1.5, 0, Math.PI * 2);
        const dotHue = hueFromPos(p.cx, p.cy);
        ctx.fillStyle = `hsla(${dotHue}, 60%, 80%, ${alpha})`;
        ctx.fill();
      }

      this.animationId = requestAnimationFrame((t2) => this.animate(t2));
    }

    start() {
      if (this.animationId) cancelAnimationFrame(this.animationId);
      this.animationId = requestAnimationFrame((t) => this.animate(t));
    }

    stop() {
      if (this.animationId) {
        cancelAnimationFrame(this.animationId);
        this.animationId = null;
      }
    }
  }

  // ── Tech Code Rain (full width) ──
  class TechCodeRain {
    constructor(canvas) {
      this.canvas = canvas;
      this.ctx = canvas.getContext("2d");
      this.cols = [];
      this.animationId = null;
      this.chars = [
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
        "A", "B", "C", "D", "E", "F",
        "<", ">", "{", "}", "/", "|", "=", "&",
        "λ", "∑", "√", "∞", "∆", "∇", "∫", "π",
      ];
      this.resize();
      this.initCols();
      window.addEventListener("resize", () => this.resize());
    }

    resize() {
      const dpr = window.devicePixelRatio || 1;
      const w = window.innerWidth;
      const h = window.innerHeight;
      this.canvas.width = w * dpr;
      this.canvas.height = h * dpr;
      this.canvas.style.width = w + "px";
      this.canvas.style.height = h + "px";
      this.ctx.scale(dpr, dpr);
      this.w = w;
      this.h = h;
      this.columnGap = 36;
      this.initCols();
    }

    initCols() {
      this.cols = [];
      const dropChar = () => this.chars[Math.floor(Math.random() * this.chars.length)];
      // Full-width columns with varying density
      const totalCols = Math.ceil(this.w / this.columnGap);
      for (let i = 0; i < totalCols; i++) {
        if (Math.random() > 0.35) continue; // sparse
        this.cols.push({
          x: i * this.columnGap + Math.random() * 10,
          y: Math.random() * this.h,
          speed: 0.3 + Math.random() * 1.2,
          chars: [
            dropChar(), dropChar(), dropChar(), dropChar(), dropChar(),
          ],
          opacity: 0.04 + Math.random() * 0.08,
          flicker: Math.random() * Math.PI * 2,
          trail: Math.random() > 0.5,
        });
      }
    }

    animate() {
      const ctx = this.ctx;
      const w = this.w;
      const h = this.h;
      ctx.clearRect(0, 0, w, h);

      for (const col of this.cols) {
        col.y += col.speed;
        if (col.y > h + 30) {
          col.y = -50;
          col.chars = [
            this.chars[Math.floor(Math.random() * this.chars.length)],
            this.chars[Math.floor(Math.random() * this.chars.length)],
            this.chars[Math.floor(Math.random() * this.chars.length)],
            this.chars[Math.floor(Math.random() * this.chars.length)],
            this.chars[Math.floor(Math.random() * this.chars.length)],
          ];
        }

        col.flicker += 0.03;
        const flickerAlpha = Math.sin(col.flicker) * 0.25 + 0.75;
        const alpha = col.opacity * flickerAlpha;

        ctx.font = "10px monospace";
        ctx.textAlign = "center";

        // Draw trailing glow
        if (col.trail) {
          ctx.shadowColor = `hsla(200, 80%, 70%, ${alpha * 0.3})`;
          ctx.shadowBlur = 4;
        }

        for (let i = 0; i < col.chars.length; i++) {
          const cy = col.y - i * 14;
          if (cy < -20 || cy > h + 20) continue;
          const fade = Math.max(0, 1 - Math.abs(cy - h / 2) / (h / 2));
          const isLead = i === 0;
          const brightness = isLead ? 85 : 55;
          const size = isLead ? 11 : 10;
          ctx.font = `${size}px monospace`;
          ctx.fillStyle = `hsla(${isLead ? 190 : 210}, ${isLead ? 90 : 70}%, ${brightness}%, ${alpha * fade * (isLead ? 2 : 1)})`;
          ctx.fillText(col.chars[i], col.x, cy);
        }

        ctx.shadowBlur = 0;
      }

      this.animationId = requestAnimationFrame(() => this.animate());
    }

    start() {
      if (this.animationId) cancelAnimationFrame(this.animationId);
      this.animate();
    }

    stop() {
      if (this.animationId) {
        cancelAnimationFrame(this.animationId);
        this.animationId = null;
      }
    }
  }

  // ── Orbital Tech Rings (enhanced) ──
  class OrbitalRings {
    constructor(canvas) {
      this.canvas = canvas;
      this.ctx = canvas.getContext("2d");
      this.animationId = null;
      this.time = 0;
      this.rings = [];
      this.resize();
      window.addEventListener("resize", () => this.resize());
    }

    resize() {
      const dpr = window.devicePixelRatio || 1;
      const w = window.innerWidth;
      const h = window.innerHeight;
      this.canvas.width = w * dpr;
      this.canvas.height = h * dpr;
      this.canvas.style.width = w + "px";
      this.canvas.style.height = h + "px";
      this.ctx.scale(dpr, dpr);
      this.w = w;
      this.h = h;
      this.cx = w / 2;
      this.cy = h / 2;
      this.initRings();
    }

    initRings() {
      const maxDim = Math.max(this.w, this.h);
      this.rings = [
        { rx: maxDim * 0.3, ry: maxDim * 0.12, speed: 0.15, phase: 0, hue: 220, dash: [6, 14], lw: 0.6, dots: 8 },
        { rx: maxDim * 0.42, ry: maxDim * 0.17, speed: -0.1, phase: 1.2, hue: 270, dash: [3, 18], lw: 0.5, dots: 10 },
        { rx: maxDim * 0.52, ry: maxDim * 0.21, speed: 0.07, phase: 2.5, hue: 190, dash: [10, 20], lw: 0.5, dots: 12 },
        { rx: maxDim * 0.62, ry: maxDim * 0.26, speed: -0.05, phase: 4.0, hue: 300, dash: [5, 22], lw: 0.4, dots: 14 },
        { rx: maxDim * 0.72, ry: maxDim * 0.30, speed: 0.03, phase: 5.5, hue: 160, dash: [8, 24], lw: 0.3, dots: 16 },
      ];
    }

    animate(t) {
      const ctx = this.ctx;
      const w = this.w;
      const h = this.h;
      ctx.clearRect(0, 0, w, h);

      this.time = t * 0.00004;
      const scrollWave = scrollProgress * Math.PI;

      for (const ring of this.rings) {
        const angle = this.time * ring.speed + ring.phase;

        ctx.save();
        ctx.translate(this.cx, this.cy + Math.sin(this.time * 0.2 + ring.phase) * 15);
        ctx.rotate(ring.phase * 0.08 + scrollWave * 0.015);

        // Dynamic dash offset
        const dashOffset = this.time * 20;
        ctx.setLineDash(ring.dash);
        ctx.lineDashOffset = -dashOffset;

        ctx.strokeStyle = `hsla(${ring.hue + Math.sin(this.time + ring.phase) * 20}, 70%, 65%, 0.2)`;
        ctx.lineWidth = ring.lw;

        ctx.beginPath();
        for (let a = 0; a < Math.PI * 2; a += 0.04) {
          const px = ring.rx * Math.cos(a + angle);
          const py = ring.ry * Math.sin(a + angle);
          if (a === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        }
        ctx.closePath();
        ctx.stroke();

        // Outer glow ring
        ctx.setLineDash([]);
        ctx.lineDashOffset = 0;
        ctx.strokeStyle = `hsla(${ring.hue + 10}, 70%, 60%, 0.04)`;
        ctx.lineWidth = ring.lw * 4;
        ctx.stroke();

        // Dots on ring
        const dotCount = ring.dots;
        for (let i = 0; i < dotCount; i++) {
          const a = (Math.PI * 2 * i) / dotCount + angle;
          const px = ring.rx * Math.cos(a);
          const py = ring.ry * Math.sin(a);
          const dotAlpha = 0.06 + Math.sin(this.time + i + ring.phase) * 0.04;
          ctx.beginPath();
          ctx.arc(px, py, 1.5 + Math.sin(this.time * 2 + i) * 0.5, 0, Math.PI * 2);
          ctx.fillStyle = `hsla(${ring.hue + 30}, 90%, 80%, ${Math.max(0, dotAlpha)})`;
          ctx.fill();
        }

        ctx.restore();
      }

      this.animationId = requestAnimationFrame((t2) => this.animate(t2));
    }

    start() {
      if (this.animationId) cancelAnimationFrame(this.animationId);
      this.animationId = requestAnimationFrame((t) => this.animate(t));
    }

    stop() {
      if (this.animationId) {
        cancelAnimationFrame(this.animationId);
        this.animationId = null;
      }
    }
  }

  // ── Data Flow Lines ──
  class DataFlow {
    constructor(canvas) {
      this.canvas = canvas;
      this.ctx = canvas.getContext("2d");
      this.lines = [];
      this.animationId = null;
      this.resize();
      this.initLines();
      window.addEventListener("resize", () => this.resize());
    }

    resize() {
      const dpr = window.devicePixelRatio || 1;
      const w = window.innerWidth;
      const h = window.innerHeight;
      this.canvas.width = w * dpr;
      this.canvas.height = h * dpr;
      this.canvas.style.width = w + "px";
      this.canvas.style.height = h + "px";
      this.ctx.scale(dpr, dpr);
      this.w = w;
      this.h = h;
    }

    initLines() {
      this.lines = [];
      const count = Math.floor(this.h / 60);
      for (let i = 0; i < count; i++) {
        const y = 40 + i * 60 + Math.random() * 20;
        this.lines.push({
          y,
          packets: [],
          hue: 200 + Math.random() * 60,
          lineWidth: 0.3 + Math.random() * 0.4,
        });
        const packetCount = 2 + Math.floor(Math.random() * 4);
        for (let j = 0; j < packetCount; j++) {
          this.lines[i].packets.push({
            x: Math.random() * this.w,
            speed: 0.3 + Math.random() * 0.8,
            size: 2 + Math.random() * 3,
            opacity: 0.3 + Math.random() * 0.4,
            trail: 30 + Math.random() * 40,
            dir: Math.random() > 0.5 ? 1 : -1,
          });
        }
      }
    }

    animate() {
      const ctx = this.ctx;
      const w = this.w;
      const h = this.h;
      ctx.clearRect(0, 0, w, h);

      for (const line of this.lines) {
        // Draw the line
        ctx.beginPath();
        ctx.moveTo(0, line.y);
        ctx.lineTo(w, line.y);
        ctx.strokeStyle = `hsla(${line.hue}, 50%, 60%, 0.04)`;
        ctx.lineWidth = line.lineWidth;
        ctx.stroke();

        for (const p of line.packets) {
          p.x += p.speed * p.dir;
          if (p.dir > 0 && p.x > w + p.trail) p.x = -p.trail;
          if (p.dir < 0 && p.x < -p.trail) p.x = w + p.trail;

          // Draw packet glow
          const gradient = ctx.createRadialGradient(p.x, line.y, 0, p.x, line.y, p.size * 3);
          gradient.addColorStop(0, `hsla(${line.hue}, 80%, 75%, ${p.opacity * 0.4})`);
          gradient.addColorStop(1, `hsla(${line.hue}, 80%, 75%, 0)`);
          ctx.fillStyle = gradient;
          ctx.beginPath();
          ctx.arc(p.x, line.y, p.size * 3, 0, Math.PI * 2);
          ctx.fill();

          // Draw packet core
          ctx.beginPath();
          ctx.arc(p.x, line.y, p.size, 0, Math.PI * 2);
          ctx.fillStyle = `hsla(${line.hue + 20}, 90%, 85%, ${p.opacity})`;
          ctx.fill();

          // Draw trail
          ctx.beginPath();
          ctx.moveTo(p.x - p.dir * p.trail * 0.1, line.y);
          ctx.lineTo(p.x - p.dir * p.trail, line.y);
          ctx.strokeStyle = `hsla(${line.hue}, 80%, 70%, ${p.opacity * 0.15})`;
          ctx.lineWidth = p.size * 0.8;
          ctx.stroke();
        }
      }

      this.animationId = requestAnimationFrame(() => this.animate());
    }

    start() {
      if (this.animationId) cancelAnimationFrame(this.animationId);
      this.animate();
    }

    stop() {
      if (this.animationId) {
        cancelAnimationFrame(this.animationId);
        this.animationId = null;
      }
    }
  }

  // ── Neural Network ──
  class NeuralNetwork {
    constructor(canvas) {
      this.canvas = canvas;
      this.ctx = canvas.getContext("2d");
      this.nodes = [];
      this.connections = [];
      this.signals = [];
      this.animationId = null;
      this.resize();
      this.initNetwork();
      window.addEventListener("resize", () => this.resize());
    }

    resize() {
      const dpr = window.devicePixelRatio || 1;
      const w = window.innerWidth;
      const h = window.innerHeight;
      this.canvas.width = w * dpr;
      this.canvas.height = h * dpr;
      this.canvas.style.width = w + "px";
      this.canvas.style.height = h + "px";
      this.ctx.scale(dpr, dpr);
      this.w = w;
      this.h = h;
    }

    initNetwork() {
      this.nodes = [];
      this.connections = [];
      this.signals = [];

      // Create nodes in layers
      const layers = [4, 6, 8, 6, 4];
      const layerGap = this.w / (layers.length + 1);

      for (let l = 0; l < layers.length; l++) {
        const nodeCount = layers[l];
        const nodeGap = this.h / (nodeCount + 1);
        for (let n = 0; n < nodeCount; n++) {
          this.nodes.push({
            x: layerGap * (l + 1) + (Math.random() - 0.5) * 30,
            y: nodeGap * (n + 1) + (Math.random() - 0.5) * 20,
            ox: layerGap * (l + 1),
            oy: nodeGap * (n + 1),
            layer: l,
            index: n,
            size: 2 + Math.random() * 2,
            phase: Math.random() * Math.PI * 2,
            hue: 200 + Math.random() * 60,
          });
        }
      }

      // Create connections between adjacent layers
      for (let l = 0; l < layers.length - 1; l++) {
        const currentNodes = this.nodes.filter((n) => n.layer === l);
        const nextNodes = this.nodes.filter((n) => n.layer === l + 1);
        for (const a of currentNodes) {
          for (const b of nextNodes) {
            if (Math.random() > 0.4) continue;
            const signal = {
              a,
              b,
              progress: Math.random(),
              speed: 0.002 + Math.random() * 0.004,
              hue: (a.hue + b.hue) / 2,
              active: Math.random() > 0.5,
              cooldown: Math.random() * 200,
              timer: 0,
            };
            this.connections.push(signal);
          }
        }
      }
    }

    animate(t) {
      const ctx = this.ctx;
      const w = this.w;
      const h = this.h;
      ctx.clearRect(0, 0, w, h);

      const time = (t || 0) * 0.0001;

      // Draw connections
      for (const c of this.connections) {
        const ax = c.a.x + Math.sin(time + c.a.phase) * 5;
        const ay = c.a.y + Math.cos(time + c.a.phase) * 5;
        const bx = c.b.x + Math.sin(time + c.b.phase) * 5;
        const by = c.b.y + Math.cos(time + c.b.phase) * 5;

        ctx.beginPath();
        ctx.moveTo(ax, ay);
        ctx.lineTo(bx, by);
        ctx.strokeStyle = `hsla(${c.hue}, 50%, 60%, 0.06)`;
        ctx.lineWidth = 0.3;
        ctx.stroke();

        // Advance signal
        if (c.active) {
          c.progress += c.speed;
          if (c.progress >= 1) {
            c.active = false;
            c.timer = 0;
          }
        } else {
          c.timer++;
          if (c.timer > c.cooldown) {
            c.active = true;
            c.progress = 0;
          }
        }

        // Draw signal dot moving along connection
        if (c.active) {
          const sx = ax + (bx - ax) * c.progress;
          const sy = ay + (by - ay) * c.progress;
          const signalAlpha = 0.3 + Math.sin(c.progress * Math.PI) * 0.5;

          ctx.beginPath();
          ctx.arc(sx, sy, 2.5, 0, Math.PI * 2);
          ctx.fillStyle = `hsla(${c.hue + 20}, 90%, 80%, ${signalAlpha})`;
          ctx.fill();
        }
      }

      // Draw nodes
      for (const n of this.nodes) {
        const nx = n.x + Math.sin(time + n.phase) * 5;
        const ny = n.y + Math.cos(time + n.phase) * 5;
        const pulse = Math.sin(time * 3 + n.phase) * 0.3 + 1;
        const size = n.size * pulse;

        ctx.beginPath();
        ctx.arc(nx, ny, size * 3, 0, Math.PI * 2);
        ctx.fillStyle = `hsla(${n.hue}, 70%, 70%, 0.06)`;
        ctx.fill();

        ctx.beginPath();
        ctx.arc(nx, ny, size, 0, Math.PI * 2);
        ctx.fillStyle = `hsla(${n.hue}, 80%, 75%, 0.25)`;
        ctx.fill();

        ctx.beginPath();
        ctx.arc(nx, ny, size * 0.4, 0, Math.PI * 2);
        ctx.fillStyle = `hsla(${n.hue + 20}, 90%, 85%, 0.5)`;
        ctx.fill();
      }

      this.animationId = requestAnimationFrame((t2) => this.animate(t2));
    }

    start() {
      if (this.animationId) cancelAnimationFrame(this.animationId);
      this.animationId = requestAnimationFrame((t) => this.animate(t));
    }

    stop() {
      if (this.animationId) {
        cancelAnimationFrame(this.animationId);
        this.animationId = null;
      }
    }
  }

  class CursorGlow {
    constructor(outerEl, innerEl) {
      this.outer = outerEl;
      this.inner = innerEl;

      const outerGlow = document.createElement("div");
      outerGlow.className = "cursor-glow-dot";
      this.outer.appendChild(outerGlow);

      const innerGlow = document.createElement("div");
      innerGlow.className = "cursor-glow-dot cursor-glow-dot--inner";
      this.inner.appendChild(innerGlow);

      this.target = { x: window.innerWidth / 2, y: window.innerHeight / 2 };
      this.current = { x: window.innerWidth / 2, y: window.innerHeight / 2 };

      document.addEventListener("mousemove", (e) => {
        this.target.x = e.clientX;
        this.target.y = e.clientY;
      });

      this.animate();
    }

    animate() {
      this.current.x += (this.target.x - this.current.x) * 0.1;
      this.current.y += (this.target.y - this.current.y) * 0.1;
      this.outer.style.transform = `translate(${this.current.x - 300}px, ${this.current.y - 300}px)`;
      this.inner.style.transform = `translate(${this.current.x - 100}px, ${this.current.y - 100}px)`;
      requestAnimationFrame(() => this.animate());
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    const gridCanvas = document.getElementById("gridCanvas");
    const cursorOuter = document.getElementById("cursorGlow");
    const cursorInner = document.getElementById("cursorTrail");
    const heroMesh = document.getElementById("heroMesh");

    const codeRainCanvas = document.getElementById("codeRainCanvas");
    const orbitalRingCanvas = document.getElementById("orbitalRingCanvas");
    const dataFlowCanvas = document.getElementById("dataFlowCanvas");
    const neuralCanvas = document.getElementById("neuralCanvas");

    const anims = [];
    if (gridCanvas) {
      const g = new GridBackground(gridCanvas);
      g.start();
      anims.push(g);
    }
    if (heroMesh) {
      const hm = new HeroMesh(heroMesh);
      hm.start();
      anims.push(hm);
    }
    if (codeRainCanvas) {
      const cr = new TechCodeRain(codeRainCanvas);
      cr.start();
      anims.push(cr);
    }
    if (orbitalRingCanvas) {
      const or = new OrbitalRings(orbitalRingCanvas);
      or.start();
      anims.push(or);
    }
    if (dataFlowCanvas) {
      const df = new DataFlow(dataFlowCanvas);
      df.start();
      anims.push(df);
    }
    if (neuralCanvas) {
      const nn = new NeuralNetwork(neuralCanvas);
      nn.start();
      anims.push(nn);
    }
    if (cursorOuter && cursorInner) new CursorGlow(cursorOuter, cursorInner);

    document.addEventListener("visibilitychange", () => {
      if (document.hidden) {
        anims.forEach((a) => a.stop?.());
      } else {
        anims.forEach((a) => a.start?.());
      }
    });
  });
})();
/* --- main.js --- */
(() => {
  "use strict";

  class ScrollAnimations {
    constructor() {
      this.observer = null;
      this.staggerObservers = [];
    }

    init() {
      const animateElements = document.querySelectorAll("[data-animate]");
      if (!animateElements.length) return;

      this.observer = new IntersectionObserver(
        (entries) => {
          for (const entry of entries) {
            if (entry.isIntersecting) {
              const el = entry.target;
              const type = el.dataset.animateType || "fade-up";
              const delay = parseFloat(el.dataset.animateDelay) || 0;
              const once = el.dataset.animateOnce !== "false";

              if (delay) el.style.animationDelay = `${delay}s`;
              el.classList.add(type);
              el.classList.add("is-visible");

              if (once) this.observer.unobserve(el);
            }
          }
        },
        {
          threshold: [0.1, 0.2],
          rootMargin: "0px 0px -50px 0px",
        },
      );

      for (const el of animateElements) {
        this.observer.observe(el);
      }

      const staggerParents = document.querySelectorAll("[data-stagger]");
      for (const parent of staggerParents) {
        const baseDelay = parseFloat(parent.dataset.staggerDelay) || 0;
        const staggerBy = parseFloat(parent.dataset.staggerBy) || 0.1;
        const children = Array.from(parent.children);

        const staggerObserver = new IntersectionObserver(
          (entries) => {
            for (const entry of entries) {
              if (entry.isIntersecting) {
                for (const [index, child] of children.entries()) {
                  const delay = baseDelay + index * staggerBy;
                  const type = child.dataset.animateType || "fade-up";
                  child.style.animationDelay = `${delay}s`;
                  child.classList.add(type);
                  child.classList.add("is-visible");
                }
                staggerObserver.unobserve(parent);
              }
            }
          },
          { threshold: 0.15 },
        );

        staggerObserver.observe(parent);
        this.staggerObservers.push(staggerObserver);
      }
    }

    destroy() {
      if (this.observer) this.observer.disconnect();
      for (const ob of this.staggerObservers) ob.disconnect();
    }
  }

  class AnimatedCounters {
    constructor() {
      this.observer = null;
    }

    init() {
      const counters = document.querySelectorAll("[data-counter]");
      if (!counters.length) return;

      this.observer = new IntersectionObserver(
        (entries) => {
          for (const entry of entries) {
            if (entry.isIntersecting) {
              const el = entry.target;
              const target = parseFloat(el.dataset.counterValue) || 0;
              const suffix = el.dataset.counterSuffix || "";
              const duration = parseFloat(el.dataset.counterDuration) || 2000;
              const prefix = el.dataset.counterPrefix || "";
              const decimals = target % 1 === 0 ? 0 : 1;

              this.animateCounter(
                el,
                target,
                suffix,
                prefix,
                duration,
                decimals,
              );
              this.observer.unobserve(el);
            }
          }
        },
        { threshold: 0.3 },
      );

      for (const el of counters) {
        this.observer.observe(el);
      }
    }

    animateCounter(el, target, suffix, prefix, duration, decimals) {
      const startTime = performance.now();

      const step = (currentTime) => {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = eased * target;

        el.textContent = prefix + current.toFixed(decimals) + suffix;

        if (progress < 1) {
          requestAnimationFrame(step);
        } else {
          el.textContent = prefix + target.toFixed(decimals) + suffix;
        }
      };

      requestAnimationFrame(step);
    }

    destroy() {
      if (this.observer) this.observer.disconnect();
    }
  }

  class ParallaxTilt {
    init() {
      const cards = document.querySelectorAll("[data-tilt]");
      for (const card of cards) {
        const maxTilt = parseFloat(card.dataset.tiltMax) || 10;
        const perspective = parseFloat(card.dataset.tiltPerspective) || 1000;
        const scale = parseFloat(card.dataset.tiltScale) || 1.02;

        card.style.transformStyle = "preserve-3d";
        card.style.transition = "transform 0.4s ease";

        card.addEventListener("mousemove", (e) => {
          const rect = card.getBoundingClientRect();
          const centerX = rect.left + rect.width / 2;
          const centerY = rect.top + rect.height / 2;
          const deltaX = (e.clientX - centerX) / (rect.width / 2);
          const deltaY = (e.clientY - centerY) / (rect.height / 2);

          card.style.transform = `perspective(${perspective}px) rotateX(${-deltaY * maxTilt}deg) rotateY(${deltaX * maxTilt}deg) scale3d(${scale}, ${scale}, ${scale})`;
        });

        card.addEventListener("mouseleave", () => {
          card.style.transition = "transform 0.6s ease";
          card.style.transform = `perspective(${perspective}px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)`;
        });
      }
    }
  }

  class FAQAccordion {
    init() {
      const items = document.querySelectorAll(".faq-item");
      if (!items.length) return;

      for (const item of items) {
        const question = item.querySelector(".faq-question");
        if (!question) continue;

        question.addEventListener("click", () => {
          const isOpen = item.classList.contains("is-open");

          for (const other of items) {
            other.classList.remove("is-open");
            const answer = other.querySelector(".faq-answer");
            if (answer) answer.style.maxHeight = "0";
          }

          if (!isOpen) {
            item.classList.add("is-open");
            const answer = item.querySelector(".faq-answer");
            if (answer) answer.style.maxHeight = answer.scrollHeight + "px";
          }
        });
      }

      window.addEventListener("resize", () => {
        for (const item of items) {
          if (item.classList.contains("is-open")) {
            const answer = item.querySelector(".faq-answer");
            if (answer) answer.style.maxHeight = answer.scrollHeight + "px";
          }
        }
      });
    }
  }

  class MouseGlow {
    init() {
      const cards = document.querySelectorAll("[data-glow]");
      for (const card of cards) {
        card.style.position = "relative";
        card.style.overflow = "hidden";

        const glow = document.createElement("div");
        glow.className = "card-glow";
        glow.style.cssText =
          "position:absolute;inset:0;pointer-events:none;z-index:1;transition:opacity 0.3s ease;opacity:0;border-radius:inherit";
        card.appendChild(glow);

        card.addEventListener("mouseenter", () => {
          glow.style.opacity = "1";
        });
        card.addEventListener("mousemove", (e) => {
          const rect = card.getBoundingClientRect();
          const x = e.clientX - rect.left;
          const y = e.clientY - rect.top;
          glow.style.background = `radial-gradient(600px circle at ${x}px ${y}px, rgba(0, 180, 255, 0.08) 0%, transparent 60%)`;
        });
        card.addEventListener("mouseleave", () => {
          glow.style.opacity = "0";
        });
      }
    }
  }

  class AnchorLinks {
    init() {
      document.addEventListener("click", (e) => {
        const link = e.target.closest('a[href^="#"]');
        if (!link) return;
        e.preventDefault();

        const targetId = link.getAttribute("href").slice(1);
        if (!targetId) return;

        const target = document.getElementById(targetId);
        if (!target) return;

        this.closeMobileNav();

        if (window.__brixScroll) {
          const y =
            target.getBoundingClientRect().top +
            window.__brixScroll.scrollY -
            80;
          if (window.__brixScroll.scrollTo) {
            window.__brixScroll.scrollTo(y);
            return;
          }
        }
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    }

    closeMobileNav() {
      const panel = document.getElementById("mobilePanel");
      const overlay = document.getElementById("mobileOverlay");
      const toggle = document.getElementById("navToggle");
      if (panel && panel.classList.contains("is-open")) {
        panel.classList.remove("is-open");
        overlay.classList.remove("is-open");
        overlay.setAttribute("inert", "");
        toggle.classList.remove("is-active");
        toggle.setAttribute("aria-expanded", "false");
        document.body.style.overflow = "";
      }
    }
  }

  class ScrollNav {
    init() {
      const navbar = document.getElementById("navbar");
      const progress = document.getElementById("scrollProgress");
      const backBtn = document.getElementById("backToTop");
      if (!navbar) return;

      const hero = document.getElementById("hero");
      const heroHeight = hero ? hero.offsetHeight : 300;

      this.update = () => {
        const scrollY = window.scrollY;

        if (scrollY > 40) {
          navbar.classList.add("is-scrolled");
        } else {
          navbar.classList.remove("is-scrolled");
        }

        if (progress) {
          const doc = document.documentElement;
          const scrollTop = scrollY;
          const scrollHeight = doc.scrollHeight - window.innerHeight;
          const pct = scrollHeight > 0 ? (scrollTop / scrollHeight) * 100 : 0;
          progress.style.width = pct + "%";
        }

        if (backBtn) {
          backBtn.classList.toggle("is-visible", scrollY > heroHeight * 0.5);
        }
      };

      window.addEventListener("scroll", this.update, { passive: true });
      this.update();
    }
  }

  class ActiveNav {
    init() {
      const navLinks = document.querySelectorAll("[data-nav]");
      const navbar = document.getElementById("navbar");
      const indicator = document.getElementById("navIndicator");
      if (!navLinks.length || !navbar) return;

      const sections = [];
      for (const link of navLinks) {
        const id = link.getAttribute("href").slice(1);
        const section = document.getElementById(id);
        if (section) sections.push({ link, section, id });
      }

      if (!sections.length) return;

      const setActive = (id) => {
        for (const { link } of sections) {
          link.classList.toggle(
            "is-active",
            link.getAttribute("href") === "#" + id,
          );
        }

        if (indicator && id) {
          const activeLink = document.querySelector(
            `[data-nav][href="#${id}"]`,
          );
          if (activeLink) {
            const rect = activeLink.getBoundingClientRect();
            const navRect = navbar.getBoundingClientRect();
            indicator.style.left = rect.left - navRect.left + "px";
            indicator.style.width = rect.width + "px";
            navbar.classList.add("has-active");
          }
        } else if (indicator) {
          navbar.classList.remove("has-active");
        }
      };

      const navObserver = new IntersectionObserver(
        (entries) => {
          let maxRatio = 0;
          let activeId = null;

          for (const entry of entries) {
            if (entry.isIntersecting && entry.intersectionRatio > maxRatio) {
              maxRatio = entry.intersectionRatio;
              activeId = entry.target.id;
            }
          }

          if (activeId) setActive(activeId);
        },
        {
          threshold: [0, 0.25, 0.5, 0.75, 1],
          rootMargin: "-80px 0px -40% 0px",
        },
      );

      for (const { section } of sections) {
        navObserver.observe(section);
      }

      setActive(sections[0].id);
    }
  }

  class MobileNav {
    init() {
      const toggle = document.getElementById("navToggle");
      const panel = document.getElementById("mobilePanel");
      const overlay = document.getElementById("mobileOverlay");
      const links = document.querySelectorAll("[data-mobile-nav]");
      if (!toggle || !panel || !overlay) return;

      const open = () => {
        panel.classList.add("is-open");
        overlay.classList.add("is-open");
        overlay.removeAttribute("inert");
        toggle.classList.add("is-active");
        toggle.setAttribute("aria-expanded", "true");
        document.body.style.overflow = "hidden";
      };

      const close = () => {
        panel.classList.remove("is-open");
        overlay.classList.remove("is-open");
        overlay.setAttribute("inert", "");
        toggle.classList.remove("is-active");
        toggle.setAttribute("aria-expanded", "false");
        document.body.style.overflow = "";
      };

      toggle.addEventListener("click", () => {
        panel.classList.contains("is-open") ? close() : open();
      });

      overlay.addEventListener("click", close);

      for (const link of links) {
        link.addEventListener("click", close);
      }

      document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && panel.classList.contains("is-open")) {
          close();
          toggle.focus();
        }
      });

      window.addEventListener("resize", () => {
        if (window.innerWidth > 768 && panel.classList.contains("is-open")) {
          close();
        }
      });
    }
  }

  class ImageLoader {
    init() {
      const images = document.querySelectorAll('img[loading="lazy"]');
      if (!images.length) return;

      for (const img of images) {
        if (img.complete) {
          img.classList.add("loaded");
          continue;
        }
        img.addEventListener("load", () => img.classList.add("loaded"), {
          once: true,
        });
        img.addEventListener("error", () => img.classList.add("loaded"), {
          once: true,
        });
      }
    }
  }

  // ── Hero: Text Splitter ──
  class HeroTextSplit {
    init() {
      const title = document.getElementById("heroTitle");
      if (title) this.splitWords(title, 0.06);
      const subtitle = document.getElementById("heroSubtitle");
      if (subtitle) this.splitWords(subtitle, 0.015);
    }

    splitWords(el, staggerBy) {
      const hasGradient = el.querySelector(":scope > .text-gradient") !== null;
      let rawHTML = el.innerHTML;
      rawHTML = rawHTML.replace(/<br\s*\/?>/gi, ' _BR_ ');
      const dummy = document.createElement('div');
      dummy.innerHTML = rawHTML;
      const text = dummy.textContent || dummy.innerText;
      const words = text.split(/\s+/).filter(w => w.trim() !== "");
      
      el.innerHTML = "";
      let delay = 0;
      for (const [i, word] of words.entries()) {
        if (word === "_BR_") {
          el.appendChild(document.createElement("br"));
          continue;
        }
        const span = document.createElement("span");
        span.className = hasGradient ? "word text-gradient" : "word";
        span.textContent = word;
        span.style.animationDelay = `${delay}s`;
        el.appendChild(span);
        if (i < words.length - 1 && words[i + 1] !== "_BR_") {
          const space = document.createElement("span");
          space.className = "word-space";
          el.appendChild(space);
        }
        delay += word.length > 6 ? staggerBy * 1.2 : staggerBy;
      }
    }
  }

  // ── Hero: 3D Parallax Tilt ──
  class HeroTilt {
    init() {
      const container = document.querySelector("[data-hero-tilt]");
      if (!container) return;

      const isTouch = "ontouchstart" in window || navigator.maxTouchPoints > 0;
      if (isTouch) return;

      const maxTilt = 6;
      const perspective = 800;

      container.addEventListener("mousemove", (e) => {
        const rect = container.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        const deltaX = (e.clientX - centerX) / (rect.width / 2);
        const deltaY = (e.clientY - centerY) / (rect.height / 2);

        const rotateX = -deltaY * maxTilt;
        const rotateY = deltaX * maxTilt;

        container.style.transform = `
          perspective(${perspective}px)
          rotateX(${rotateX}deg)
          rotateY(${rotateY}deg)
          translateZ(0)
        `;

        const children = container.querySelectorAll(
          ".hero-title, .hero-subtitle, .hero-cta",
        );
        for (const child of children) {
          const depth = child.dataset.tiltDepth || 20;
          const x = deltaX * depth;
          const y = deltaY * depth;
          child.style.transform = `translateZ(0) translateX(${-x}px) translateY(${-y}px)`;
        }
      });

      container.addEventListener("mouseleave", () => {
        container.style.transform =
          "perspective(800px) rotateX(0deg) rotateY(0deg) translateZ(0)";
        const children = container.querySelectorAll(
          ".hero-title, .hero-subtitle, .hero-cta",
        );
        for (const child of children) {
          child.style.transform = "translateZ(0) translateX(0) translateY(0)";
          child.style.transition = "transform 0.6s ease";
          setTimeout(() => {
            child.style.transition = "";
          }, 600);
        }
      });
    }
  }

  // ── Hero: Spotlight ──
  class HeroSpotlight {
    init() {
      const spotlight = document.getElementById("heroSpotlight");
      if (!spotlight) return;

      const isTouch = "ontouchstart" in window || navigator.maxTouchPoints > 0;
      if (isTouch) {
        spotlight.style.display = "none";
        return;
      }

      const hero = document.getElementById("hero");
      if (!hero) return;

      let rafId = null;
      const updateSpot = (e) => {
        if (rafId) cancelAnimationFrame(rafId);
        rafId = requestAnimationFrame(() => {
          const rect = hero.getBoundingClientRect();
          const x = ((e.clientX - rect.left) / rect.width) * 100;
          const y = ((e.clientY - rect.top) / rect.height) * 100;
          spotlight.style.background = `radial-gradient(600px circle at ${x}% ${y}%, rgba(56, 189, 248, 0.22), rgba(139, 92, 246, 0.12) 18%, rgba(236, 72, 153, 0.08) 35%, rgba(251, 146, 60, 0.05) 50%, rgba(34, 211, 238, 0.03) 65%, transparent 75%)`;
        });
      };

      hero.addEventListener("mousemove", updateSpot, { passive: true });
    }
  }

  // ── Hero: Orb Mouse-Follow ──
  class HeroOrbs {
    init() {
      const orbs = document.querySelectorAll("[data-hero-orb]");
      if (!orbs.length) return;

      const isTouch = "ontouchstart" in window || navigator.maxTouchPoints > 0;
      if (isTouch) return;

      const hero = document.getElementById("hero");
      if (!hero) return;

      let rafId = null;
      let mouseInside = false;

      const moveOrbs = (e) => {
        if (rafId) cancelAnimationFrame(rafId);
        rafId = requestAnimationFrame(() => {
          const rect = hero.getBoundingClientRect();
          const x = (e.clientX - rect.left) / rect.width;
          const y = (e.clientY - rect.top) / rect.height;
          for (const [i, orb] of orbs.entries()) {
            const factor = 10 + i * 5;
            const tx = (x - 0.5) * factor;
            const ty = (y - 0.5) * factor;
            if (!mouseInside) {
              mouseInside = true;
              orb.style.animation = "none";
              orb.style.transform = "";
              void orb.offsetHeight;
            }
            orb.style.transform = `translate(${tx}px, ${ty}px)`;
          }
        });
      };

      const resetOrbs = () => {
        mouseInside = false;
        for (const orb of orbs) {
          orb.style.animation = "";
          orb.style.transform = "";
          orb.style.transition = "transform 0.8s ease";
          setTimeout(() => {
            orb.style.transition = "";
          }, 800);
        }
      };

      hero.addEventListener("mousemove", moveOrbs, { passive: true });
      hero.addEventListener("mouseleave", resetOrbs, { passive: true });
    }
  }

  // ── Hero: Magnetic Buttons ──
  class HeroMagnetic {
    init() {
      const btns = document.querySelectorAll(".btn-glow");
      if (!btns.length) return;

      const isTouch = "ontouchstart" in window || navigator.maxTouchPoints > 0;
      if (isTouch) return;

      for (const btn of btns) {
        btn.addEventListener("mousemove", (e) => {
          const rect = btn.getBoundingClientRect();
          const x = e.clientX - rect.left - rect.width / 2;
          const y = e.clientY - rect.top - rect.height / 2;
          const dist = Math.sqrt(x * x + y * y);
          const maxDist = Math.max(rect.width, rect.height);
          const strength = Math.max(0, 1 - dist / maxDist) * 8;
          const angle = Math.atan2(y, x);
          const tx = Math.cos(angle) * strength;
          const ty = Math.sin(angle) * strength;
          btn.style.transform = `translate(${tx}px, ${ty}px)`;
        });

        btn.addEventListener("mouseleave", () => {
          btn.style.transform = "";
          btn.style.transition = "transform 0.4s ease";
          setTimeout(() => {
            btn.style.transition = "";
          }, 400);
        });
      }
    }
  }

  // ── Hero: Scroll-Driven Effects ──
  class HeroScrollDrive {
    init() {
      const hero = document.getElementById("hero");
      const content = document.querySelector(".hero-content");
      if (!hero) return;

      let willChangeTimer;

      const setWillChange = (active) => {
        if (!content) return;
        if (active) {
          content.style.willChange = "transform, opacity";
        } else {
          content.style.willChange = "auto";
        }
      };

      const update = () => {
        const rect = hero.getBoundingClientRect();
        const viewH = window.innerHeight;
        const progress = Math.max(0, Math.min(1, (viewH - rect.top) / viewH));

        if (content) {
          const scale = 1 - progress * 0.08;
          const opacity = 1 - progress * 0.5;
          const y = progress * 40;
          content.style.transform = `scale(${scale}) translateY(${y}px)`;
          content.style.opacity = opacity;
          setWillChange(true);
          clearTimeout(willChangeTimer);
          willChangeTimer = setTimeout(() => setWillChange(false), 200);
        }

      };

      window.addEventListener("scroll", update, { passive: true });
    }
  }

  // ── Loading Screen ──
  class LoadingScreen {
    init() {
      const screen = document.getElementById("loadingScreen");
      const fill = document.querySelector(".loading-bar-fill");
      const pctEl = document.getElementById("loadingPercent");
      if (!screen) return;

      const setProgress = (pct) => {
        if (fill) fill.style.width = Math.min(pct, 100) + "%";
        if (pctEl) pctEl.textContent = Math.round(Math.min(pct, 100)) + "%";
      };

      // Milestones: DOMContentLoaded ~ 50%, window.load ~ 85%, then 100%
      const atDomReady = () => setProgress(55);
      const atFullyLoaded = () => {
        setProgress(85);
        setTimeout(() => {
          setProgress(100);
          if (pctEl) pctEl.textContent = "100%";
          setTimeout(() => {
            screen.classList.add("is-hidden");
            setTimeout(() => screen.remove(), 900);
          }, 400);
        }, 200);
      };
      const atTimeout = () => {
        setProgress(100);
        if (pctEl) pctEl.textContent = "100%";
        setTimeout(() => {
          screen.classList.add("is-hidden");
          setTimeout(() => screen.remove(), 900);
        }, 300);
      };

      setProgress(10);
      setTimeout(() => setProgress(25), 100);
      setTimeout(() => setProgress(35), 250);

      if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", atDomReady, {
          once: true,
        });
      } else {
        atDomReady();
      }

      if (document.readyState === "complete") {
        atFullyLoaded();
      } else {
        window.addEventListener("load", atFullyLoaded, { once: true });
      }

      setTimeout(atTimeout, 5000);
    }
  }

  // ── Custom Card Handler (UI-only animation) ──
  class CustomCardHandler {
    init() {
      const btn = document.querySelector(".custom-card-btn");
      const input = document.querySelector(".custom-card-input");
      if (!btn || !input) return;

      const submit = () => {
        if (
          btn.classList.contains("is-loading") ||
          btn.classList.contains("is-success")
        )
          return;

        btn.classList.add("is-loading");
        input.classList.add("is-disabled");

        setTimeout(() => {
          btn.classList.remove("is-loading");
          btn.classList.add("is-success");

          setTimeout(() => {
            btn.classList.remove("is-success");
            input.classList.remove("is-disabled");
            input.value = "";
          }, 2500);
        }, 1400);
      };

      btn.addEventListener("click", submit);

      input.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          submit();
        }
      });
    }
  }

  // ── Process Timeline Fill ──
  class TimelineFill {
    init() {
      const fill = document.getElementById("timelineFill");
      const timeline = document.querySelector(".process-timeline");
      if (!fill || !timeline) return;

      const update = () => {
        const rect = timeline.getBoundingClientRect();
        const viewH = window.innerHeight;
        const totalH = rect.height;
        const top = rect.top;
        const bottom = rect.bottom;

        if (bottom < 0 || top > viewH) return;

        const visibleStart = Math.max(0, -top);
        const visibleEnd = Math.min(totalH, viewH - top);
        const visible = visibleEnd - visibleStart;
        const progress = Math.max(
          0,
          Math.min(1, (viewH - top) / (totalH + viewH)),
        );
        fill.style.height = progress * 100 + "%";
      };

      window.addEventListener("scroll", update, { passive: true });
      update();
    }
  }

  // ── Enhanced Cursor (glow color on interactive) ──
  class EnhancedCursor {
    init() {
      const outer = document.getElementById("cursorGlow");
      const inner = document.getElementById("cursorTrail");
      if (!outer || !inner) return;

      const interactive = document.querySelectorAll(
        "a, button, .service-card, .project-card, .tech-item a, .footer-social-link, .nav-link, .mobile-nav-link",
      );

      const glowDot = outer.querySelector(".cursor-glow-dot");
      const innerDot = inner.querySelector(".cursor-glow-dot--inner");

      for (const el of interactive) {
        el.addEventListener("mouseenter", () => {
          if (glowDot)
            glowDot.style.background =
              "radial-gradient(circle, rgba(251, 146, 60, 0.18) 0%, rgba(168, 85, 247, 0.08) 40%, transparent 70%)";
          if (innerDot)
            innerDot.style.background =
              "radial-gradient(circle, rgba(255, 255, 255, 0.3) 0%, transparent 70%)";
        });

        el.addEventListener("mouseleave", () => {
          if (glowDot)
            glowDot.style.background =
              "radial-gradient(circle, rgba(59, 130, 246, 0.12) 0%, rgba(168, 85, 247, 0.06) 30%, transparent 70%)";
          if (innerDot)
            innerDot.style.background =
              "radial-gradient(circle, rgba(251, 146, 60, 0.15) 0%, rgba(139, 92, 246, 0.15) 40%, transparent 70%)";
        });
      }
    }
  }

  // ── Hero: Scroll Indicator Hide ──
  class ScrollIndicator {
    init() {
      const indicator = document.querySelector(".scroll-indicator");
      if (!indicator) return;

      let lastScrollY = window.scrollY;
      const check = () => {
        const scrollY = window.scrollY;
        if (scrollY > 100 && scrollY > lastScrollY) {
          indicator.classList.add("is-hidden");
        } else if (scrollY < 50) {
          indicator.classList.remove("is-hidden");
        }
        lastScrollY = scrollY;
      };

      window.addEventListener("scroll", check, { passive: true });
    }
  }

  // ── Magnetic Buttons ──
  class MagneticButtons {
    init() {
      const buttons = document.querySelectorAll(
        ".btn-primary, .btn-secondary, .nav-link, .project-card-link, .custom-card-btn, .cta-btn-primary, .cta-btn-secondary"
      );

      for (const btn of buttons) {
        const wrap = document.createElement("span");
        wrap.className = "magnetic-wrap";
        btn.parentNode.insertBefore(wrap, btn);
        wrap.appendChild(btn);

        let rafId = null;
        let boundX = 0, boundY = 0, boundW = 0, boundH = 0;

        const updateBounds = () => {
          const r = wrap.getBoundingClientRect();
          boundX = r.left; boundY = r.top; boundW = r.width; boundH = r.height;
        };

        const onMove = (e) => {
          if (!rafId) {
            rafId = requestAnimationFrame(() => {
              const cx = boundX + boundW / 2;
              const cy = boundY + boundH / 2;
              const dx = e.clientX - cx;
              const dy = e.clientY - cy;
              const dist = Math.sqrt(dx * dx + dy * dy);
              const maxDist = 120;
              const pull = Math.max(0, 1 - dist / maxDist);
              const strength = 8;
              wrap.style.transform = `translate(${dx * pull * 0.15}px, ${dy * pull * 0.15}px)`;
              rafId = null;
            });
          }
        };

        const onLeave = () => {
          if (rafId) { cancelAnimationFrame(rafId); rafId = null; }
          wrap.style.transform = "";
        };

        wrap.addEventListener("mouseenter", () => {
          updateBounds();
          document.addEventListener("mousemove", onMove);
        });

        wrap.addEventListener("mouseleave", () => {
          document.removeEventListener("mousemove", onMove);
          onLeave();
        });
      }
    }
  }

  // ── Form Enhancer ──
  class FormEnhancer {
    init() {
      const inputs = document.querySelectorAll(".form-group input");
      for (const input of inputs) {
        const group = input.closest(".form-group");
        if (!group) continue;
        const label = group.querySelector("label");
        if (!label) continue;

        const check = () => {
          group.classList.toggle("has-value", input.value.length > 0);
          group.classList.toggle("is-focused", document.activeElement === input);
        };

        input.addEventListener("focus", check);
        input.addEventListener("blur", check);
        input.addEventListener("input", check);
        check();
      }
    }
  }

  // ── Terminal Typer (animated running code) ──
  class TerminalTyper {
    constructor(terminalId, bodyId) {
      this.terminal = document.getElementById(terminalId);
      this.body = document.getElementById(bodyId);
      if (!this.terminal || !this.body) return;

      this.scenarios = [
        {
          lines: [
            { type: "cmd", text: "deploy --model=neural-v2 --env=prod" },
            { type: "out", text: "▸ Initializing neural engine..." },
            { type: "out", text: "▸ Loading weights  [████████░░] 87%" },
            { type: "out", text: "▸ Optimizing inference pipeline..." },
            { type: "out", text: "▸ Quantizing: fp16 → int8  [OK]" },
            { type: "out", text: "▸ Kernel fusion: 12 layers merged" },
            { type: "out", text: "▸ API gateway: 3.2k req/s @ p99=14ms" },
            { type: "out", text: "▸ Deployment complete [OK]" },
          ],
        },
        {
          lines: [
            { type: "cmd", text: "infer --input=test/batch_04 --model=v2" },
            { type: "out", text: "▸ Loading model weights..." },
            { type: "out", text: "▸ Processing batch of 128 samples" },
            { type: "out", text: "▸ Inference: 247ms / sample" },
            { type: "out", text: "▸ Accuracy: 98.7% @ threshold=0.5" },
            { type: "out", text: "▸ Results written to /out/batch_04.json" },
          ],
        },
        {
          lines: [
            { type: "cmd", text: "train --config=experiment_12 --lr=5e-5" },
            { type: "out", text: "▸ Initializing trainer..." },
            { type: "out", text: "▸ Epoch 128/200 | loss: 0.018" },
            { type: "out", text: "▸ Val acc: 97.3% | F1: 0.962" },
            { type: "out", text: "▸ LR schedule: cosine -> 1e-5" },
            { type: "out", text: "▸ Checkpoint saved @ epoch 128" },
          ],
        },
      ];

      this.scenarioIdx = 0;
      this.lineIdx = 0;
      this.charIdx = 0;
      this.running = false;
    }

    start() {
      if (!this.body) return;
      this.running = true;
      this.body.innerHTML = "";
      this.scenarioIdx = 0;
      this.lineIdx = 0;
      this.typeNextChar();
    }

    typeNextChar() {
      if (!this.running) return;
      const scenario = this.scenarios[this.scenarioIdx];
      if (!scenario) { this.start(); return; }

      if (this.lineIdx >= scenario.lines.length) {
        this.lineIdx = 0;
        this.scenarioIdx = (this.scenarioIdx + 1) % this.scenarios.length;
        setTimeout(() => {
          this.body.innerHTML = "";
          this.typeNextChar();
        }, 2000);
        return;
      }

      const line = scenario.lines[this.lineIdx];
      const text = line.text;
      const prefix = line.type === "cmd" ? '<span class="prompt">$</span> ' : '<span class="output">';
      const suffix = line.type === "cmd" ? "" : "</span>";

      if (this.charIdx === 0) {
        const div = document.createElement("div");
        div.className = "terminal-line";
        div.innerHTML = prefix + suffix;
        if (line.type === "cmd") {
          div.innerHTML = prefix + '<span class="cmd"></span>';
        }
        this.body.appendChild(div);
      }

      const lastDiv = this.body.lastElementChild;
      if (line.type === "cmd") {
        const cmdSpan = lastDiv.querySelector(".cmd");
        if (cmdSpan) {
          cmdSpan.textContent = text.slice(0, this.charIdx + 1);
        }
      } else {
        lastDiv.innerHTML = prefix + text.slice(0, this.charIdx + 1) + '<span class="cursor-blink">_</span>' + suffix;
      }

      this.charIdx++;

      if (this.charIdx >= text.length) {
        this.charIdx = 0;
        this.lineIdx++;
        // Add the trailing cursor to last line
        if (line.type === "cmd") {
          const cmdSpan = lastDiv.querySelector(".cmd");
          if (cmdSpan) cmdSpan.textContent = text;
        } else {
          lastDiv.innerHTML = prefix + text + suffix;
        }
        const delay = line.type === "cmd" ? 400 : 200 + Math.random() * 300;
        setTimeout(() => this.typeNextChar(), delay);
      } else {
        const speed = line.type === "cmd" ? 25 + Math.random() * 15 : 12 + Math.random() * 20;
        setTimeout(() => this.typeNextChar(), speed);
      }
    }
  }

  // ── Scroll Parallax ──
  class ScrollParallax {
    init() {
      const els = document.querySelectorAll("[data-parallax]");
      if (!els.length) return;

      const isMobile = window.innerWidth < 768;

      const update = () => {
        const st = window.scrollY;
        const vh = window.innerHeight;
        for (const el of els) {
          const speed = parseFloat(el.getAttribute("data-parallax")) || 0.05;
          const rect = el.getBoundingClientRect();
          const center = rect.top + rect.height / 2;
          const distFromViewportCenter = center - vh / 2;
          const offset = distFromViewportCenter * speed;
          el.style.transform = `translateY(${offset * -1}px)`;
        }
      };

      if (!isMobile) {
        window.addEventListener("scroll", update, { passive: true });
        update();
      }
    }
  }

  // ── Project Rotator ──
  class ProjectRotator {
    init() {
      this.cards = document.querySelectorAll(".project-card");
      if (this.cards.length <= 1) return;

      this.idx = 0;
      this.playing = true;
      this.interval = null;

      this._buildDots();
      this._highlight(0);
      this._startAuto();
    }

    _buildDots() {
      this.nav = document.createElement("div");
      this.nav.className = "project-rotator-nav";
      for (let i = 0; i < this.cards.length; i++) {
        const dot = document.createElement("button");
        dot.className = "rotator-dot" + (i === 0 ? " is-active" : "");
        dot.setAttribute("aria-label", `Show project ${i + 1}`);
        dot.dataset.idx = i;
        dot.addEventListener("click", (e) => {
          this.playing = false;
          this._highlight(parseInt(e.currentTarget.dataset.idx));
          clearTimeout(this._pauseTimeout);
          this._pauseTimeout = setTimeout(() => { this.playing = true; this._startAuto(); }, 8000);
        });
        this.nav.appendChild(dot);
      }
      // Insert after the projects-grid
      const grid = document.querySelector(".projects-grid");
      grid.parentNode.insertBefore(this.nav, grid.nextSibling);
    }

    _highlight(i) {
      if (i === this.idx && this.interval) return;
      this.idx = i;
      for (let j = 0; j < this.cards.length; j++) {
        this.cards[j].classList.toggle("is-highlighted", j === i);
      }
      const dots = this.nav.querySelectorAll(".rotator-dot");
      dots.forEach((d, j) => d.classList.toggle("is-active", j === i));
    }

    _startAuto() {
      clearInterval(this.interval);
      if (!this.playing) return;
      this.interval = setInterval(() => {
        const next = (this.idx + 1) % this.cards.length;
        this._highlight(next);
      }, 4000);
    }
  }

  // ── Hex Clock ──
  class HexClock {
    init() {
      const el = document.getElementById("hexClock");
      if (!el) return;
      const update = () => {
        const now = new Date();
        const h = now.getHours().toString(16).padStart(2, "0").toUpperCase();
        const m = now.getMinutes().toString(16).padStart(2, "0").toUpperCase();
        const s = now.getSeconds().toString(16).padStart(2, "0").toUpperCase();
        const ms = now.getMilliseconds().toString(16).padStart(3, "0").toUpperCase();
        el.textContent = `0x${h}${m}${s}${ms}`;
      };
      update();
      setInterval(update, 50);
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    new ScrollAnimations().init();
    new AnimatedCounters().init();
    new ParallaxTilt().init();
    new FAQAccordion().init();
    new MouseGlow().init();
    new AnchorLinks().init();
    new ScrollNav().init();
    new ActiveNav().init();
    new MobileNav().init();
    new ImageLoader().init();
    new HeroTextSplit().init();
    new HeroTilt().init();
    new HeroSpotlight().init();
    new HeroOrbs().init();
    new HeroMagnetic().init();
    new HeroScrollDrive().init();
    new LoadingScreen().init();
    new CustomCardHandler().init();
    new TimelineFill().init();
    new EnhancedCursor().init();
    new ScrollIndicator().init();
    new MagneticButtons().init();
    new ScrollParallax().init();
    new ProjectRotator().init();
    new FormEnhancer().init();
    new HexClock().init();
    new TerminalTyper("heroTerminal", "terminalBody").start();
  });
})();
/* --- contact-form.js --- */
(() => {
  "use strict";

  const FORM = document.getElementById("contactForm");
  const STATUS = document.getElementById("formStatus");
  const SUBMIT_BTN = document.getElementById("formSubmit");
  if (!FORM || !STATUS || !SUBMIT_BTN) return;

  emailjs.init("BlAsb_uUrdfjZ2E62");

  const btnText = SUBMIT_BTN.querySelector(".btn-text");

  let lastSubmitAt = 0;

  FORM.addEventListener("submit", async (e) => {
    e.preventDefault();
    STATUS.className = "form-status";
    STATUS.textContent = "";

    for (const el of [FORM.formName, FORM.formPhone, FORM.formEmail]) {
      el.closest(".form-group").classList.remove("error");
    }

    const name = FORM.formName.value.trim();
    const phone = FORM.formPhone.value.trim();
    const email = FORM.formEmail.value.trim();

    // Honeypot: bots fill the hidden "website" field; silently ignore them
    if (FORM.formWebsite && FORM.formWebsite.value.trim()) {
      FORM.reset();
      return;
    }

    // Rate limit: at least 60s between submissions from this browser
    const now = Date.now();
    if (now - lastSubmitAt < 60000) {
      STATUS.className = "form-status error";
      STATUS.textContent = "Please wait a moment before submitting again.";
      return;
    }

    let valid = true;
    for (const el of [FORM.formName, FORM.formPhone, FORM.formEmail]) {
      el.closest(".form-group").classList.toggle("error", !el.value.trim());
      if (!el.value.trim()) valid = false;
    }

    if (!valid) {
      STATUS.className = "form-status error";
      STATUS.textContent = "Please fill in all fields.";
      return;
    }

    if (!/^[\d\s\-+()]{7,20}$/.test(phone)) {
      FORM.formPhone.closest(".form-group").classList.add("error");
      STATUS.className = "form-status error";
      STATUS.textContent = "Please enter a valid phone number.";
      return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      FORM.formEmail.closest(".form-group").classList.add("error");
      STATUS.className = "form-status error";
      STATUS.textContent = "Please enter a valid email address.";
      return;
    }

    SUBMIT_BTN.disabled = true;
    if (btnText) btnText.textContent = "Sending...";

    try {
      const data = { name, phone, email, createdAt: new Date().toISOString() };

      // Write to Firestore via Firebase SDK
      await firebase.firestore().collection("contacts").add(data);
      lastSubmitAt = Date.now();

      // Send email notification via EmailJS (non-blocking: Firestore is the
      // source of truth, so the submitter still gets confirmation)
      try {
        await emailjs.send(
          "service_ss7duub",
          "template_3gk88us",
          {
            name,
            phone,
            email,
            createdAt: data.createdAt,
          }
        );
      } catch (mailErr) {
        console.error("Email notification failed:", mailErr);
      }

      STATUS.className = "form-status success";
      STATUS.textContent = "Thank you! We'll contact you within 24 hours.";
      FORM.reset();
    } catch {
      STATUS.className = "form-status error";
      STATUS.textContent =
        "Something went wrong. Please try again or email us directly.";
    } finally {
      SUBMIT_BTN.disabled = false;
      if (btnText) btnText.textContent = "Submit";
    }
  });
})();
