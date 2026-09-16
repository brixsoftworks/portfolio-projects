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
