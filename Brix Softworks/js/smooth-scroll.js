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
