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
      const text = el.textContent;
      const words = text.split(/\s+/);
      el.innerHTML = "";
      let delay = 0;
      for (const [i, word] of words.entries()) {
        const span = document.createElement("span");
        span.className = hasGradient ? "word text-gradient" : "word";
        span.textContent = word;
        span.style.animationDelay = `${delay}s`;
        el.appendChild(span);
        if (i < words.length - 1) {
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
            { type: "out", text: "▸ Quantizing: fp16 → int8  ✓" },
            { type: "out", text: "▸ Kernel fusion: 12 layers merged" },
            { type: "out", text: "▸ API gateway: 3.2k req/s @ p99=14ms" },
            { type: "out", text: "▸ Deployment complete ✓" },
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
