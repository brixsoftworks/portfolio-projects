/**
 * BRIX SOFTWORKS — 60 AI AGENTS & WORKFLOWS INTERACTIVE CONTROLLER
 * Supports both Homepage Teaser and Full Categorized Directory Page (agents.html)
 */
(function () {
  "use strict";

  const CATEGORY_META = [
    {
      id: "sales",
      name: "Sales & RevOps",
      badge: "Revenue Growth",
      icon: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>`,
      desc: "Autonomous inbound lead qualification, enrichment, deal pipeline acceleration, and automated proposal negotiation."
    },
    {
      id: "support",
      name: "Customer Support & CX",
      badge: "Client Retention",
      icon: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>`,
      desc: "Omnichannel customer ticket auto-triage, real-time sentiment telemetry, proactive retention playbooks, and onboarding."
    },
    {
      id: "finance",
      name: "Finance & Accounting",
      badge: "Zero Discrepancy",
      icon: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="5" width="20" height="14" rx="2"></rect><line x1="2" y1="10" x2="22" y2="10"></line></svg>`,
      desc: "Autonomous 3-way invoice matching, accounts receivable recovery, SaaS seat waste audit, and runway forecasting."
    },
    {
      id: "security",
      name: "Security, Legal & Compliance",
      badge: "Zero-Trust",
      icon: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>`,
      desc: "Real-time secrets & PII hunting, automated SOC2/ISO audit evidence collection, IT access deprovisioning, and contract insight."
    },
    {
      id: "data",
      name: "Data & Analytics",
      badge: "Data Integrity",
      icon: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>`,
      desc: "Automated dataset sanitization, anomaly detection, spreadsheet intelligence, and duplicate resolution across CRMs."
    },
    {
      id: "operations",
      name: "Operations & Governance",
      badge: "Process Automation",
      icon: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>`,
      desc: "Predictive inventory reorder, recurring tasks, deadline guardians, smart file sorting, and automated backup pipelines."
    },
    {
      id: "marketing",
      name: "Content & Marketing",
      badge: "Brand Velocity",
      icon: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>`,
      desc: "Multi-channel content repurposing, automated social publishing, editorial calendar planning, and review sentiment monitoring."
    },
    {
      id: "hr",
      name: "HR & Talent Management",
      badge: "Workforce",
      icon: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>`,
      desc: "Resume screening & candidate matching, automated employee onboarding orchestration, and PTO coverage coordination."
    },
    {
      id: "knowledge",
      name: "Executive & Intelligence",
      badge: "Decision Support",
      icon: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 14 14"></polyline></svg>`,
      desc: "Executive Monday morning briefings, competitor price war intelligence, web research agents, and company-wide Q&A."
    }
  ];

  let catalog = null;
  let activeCategory = "all";
  let activeType = "all";
  let searchKeyword = "";
  let simulationTimer = null;
  const isDedicatedPage = Boolean(document.getElementById("agentsCatalogPage"));

  function init() {
    if (!window.BRIX_AGENTS_CATALOG) {
      setTimeout(init, 50);
      return;
    }
    catalog = window.BRIX_AGENTS_CATALOG;

    // Check for hash on load
    if (window.location.hash) {
      const hashCat = window.location.hash.replace("#", "").toLowerCase();
      const match = CATEGORY_META.find((c) => c.id === hashCat);
      if (match) {
        activeCategory = match.id;
      }
    }

    renderStats();

    if (isDedicatedPage) {
      renderCategoryPills();
      renderQuickJumpBar();
      setupEventListeners();
      renderCatalogPage();
    } else {
      renderHomepageTeaser();
      setupEventListeners();
    }
  }

  function renderStats() {
    const statsContainer = document.getElementById("agentsStatsBar");
    if (!statsContainer) return;

    statsContainer.innerHTML = `
      <div class="agents-stat-card">
        <span class="agents-stat-val">60</span>
        <span class="agents-stat-label">Production Modules</span>
      </div>
      <div class="agents-stat-card">
        <span class="agents-stat-val">45</span>
        <span class="agents-stat-label">Autonomous AI Agents</span>
      </div>
      <div class="agents-stat-card">
        <span class="agents-stat-val">15</span>
        <span class="agents-stat-label">Zero-Loss Workflows</span>
      </div>
      <div class="agents-stat-card">
        <span class="agents-stat-val">99.4%</span>
        <span class="agents-stat-label">Benchmark Accuracy</span>
      </div>
    `;
  }

  // --- HOMEPAGE TEASER MODE ---
  function renderHomepageTeaser() {
    const grid = document.getElementById("agentsGrid");
    if (!grid) return;

    // Render 9 category overview cards
    const categoryCardsHTML = CATEGORY_META.map((cat) => {
      const items = catalog.items.filter((i) => i.group === cat.id);
      return `
        <a href="agents.html#${cat.id}" class="agents-category-card">
          <div>
            <div class="agents-cat-icon">${cat.icon}</div>
            <div class="agents-cat-title">
              <span>${cat.name}</span>
              <span class="agents-cat-count">${items.length} Modules</span>
            </div>
            <p class="agents-cat-desc">${cat.desc}</p>
          </div>
          <div class="agents-cat-footer">
            <span>Explore ${cat.name}</span>
            <span>→</span>
          </div>
        </a>
      `;
    }).join("");

    // Featured 4 Flagship Modules
    const featuredIds = ["agent_60", "agent_46", "agent_53", "agent_48"];
    const featuredItems = featuredIds
      .map((id) => catalog.items.find((i) => i.id === id))
      .filter(Boolean);

    const featuredHTML = featuredItems.map((item) => renderCardHTML(item)).join("");

    grid.innerHTML = `
      <div style="grid-column: 1 / -1;">
        <div class="agents-teaser-card-grid">
          ${categoryCardsHTML}
        </div>

        <div class="agents-category-banner" style="margin-top: 3.5rem;">
          <div class="agents-category-banner-left">
            <span class="agents-category-tag">Featured Flagship Modules</span>
            <h3 class="agents-category-name">High-Impact Cognitive Agents</h3>
            <p class="agents-category-desc">Try live interactive simulation on our benchmark flagship enterprise agents.</p>
          </div>
          <a href="agents.html" class="agents-primary-btn" style="padding: 0.6rem 1.25rem; font-size: 0.8125rem;">
            View All 60 Agents →
          </a>
        </div>

        <div class="agents-grid" style="margin-bottom: 2rem;">
          ${featuredHTML}
        </div>

        <!-- Sleek CTA Box -->
        <div class="agents-cta-banner">
          <h3 class="agents-cta-title">Looking for the Complete 60-Module Workforce?</h3>
          <p class="agents-cta-desc">
            Explore our dedicated catalog with all 45 goal-oriented AI agents and 15 deterministic workflows cleanly categorized by business function.
          </p>
          <a href="agents.html" class="agents-primary-btn">
            <span>Open 60-Agent Interactive Catalog</span>
            <span>→</span>
          </a>
        </div>
      </div>
    `;

    attachCardHandlers(grid);
  }

  // --- DEDICATED CATALOG PAGE (agents.html) ---
  function renderQuickJumpBar() {
    const nav = document.getElementById("agentsQuickJump");
    if (!nav) return;

    nav.innerHTML = `
      <a href="#all" class="agents-quickjump-item ${activeCategory === "all" ? "active" : ""}" data-jump="all">All Modules (60)</a>
      ${CATEGORY_META.map(
        (c) => `
        <a href="#${c.id}" class="agents-quickjump-item ${activeCategory === c.id ? "active" : ""}" data-jump="${c.id}">
          ${c.name} (${catalog.items.filter((i) => i.group === c.id).length})
        </a>
      `
      ).join("")}
    `;

    nav.querySelectorAll(".agents-quickjump-item").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        const target = btn.dataset.jump;
        activeCategory = target;
        window.location.hash = target === "all" ? "" : target;

        nav.querySelectorAll(".agents-quickjump-item").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");

        const pills = document.getElementById("agentsFilterPills");
        if (pills) {
          pills.querySelectorAll(".agents-pill").forEach((p) => {
            p.classList.toggle("active", p.dataset.categoryId === target);
          });
        }

        renderCatalogPage();
      });
    });
  }

  function renderCategoryPills() {
    const pillsContainer = document.getElementById("agentsFilterPills");
    if (!pillsContainer) return;

    pillsContainer.innerHTML = catalog.categories
      .map((cat) => {
        const isActive = cat.id === activeCategory ? "active" : "";
        return `
          <button type="button" class="agents-pill ${isActive}" data-category-id="${cat.id}">
            <span>${cat.label}</span>
            <span class="agents-pill-count">${cat.count}</span>
          </button>
        `;
      })
      .join("");

    pillsContainer.querySelectorAll(".agents-pill").forEach((btn) => {
      btn.addEventListener("click", () => {
        pillsContainer.querySelectorAll(".agents-pill").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        activeCategory = btn.dataset.categoryId;
        window.location.hash = activeCategory === "all" ? "" : activeCategory;

        const nav = document.getElementById("agentsQuickJump");
        if (nav) {
          nav.querySelectorAll(".agents-quickjump-item").forEach((b) => {
            b.classList.toggle("active", b.dataset.jump === activeCategory);
          });
        }

        renderCatalogPage();
      });
    });
  }

  function renderCatalogPage() {
    const grid = document.getElementById("agentsGrid");
    const counter = document.getElementById("agentsCountDisplay");
    if (!grid) return;

    const filtered = getFilteredItems();

    if (counter) {
      counter.innerHTML = `Showing <span>${filtered.length}</span> of ${catalog.items.length} Modules`;
    }

    if (filtered.length === 0) {
      grid.innerHTML = `
        <div class="agents-empty-state">
          <svg class="agents-empty-icon" viewBox="0 0 24 24" fill="none" stroke-width="1.5">
            <circle cx="11" cy="11" r="8"></circle>
            <path d="M21 21l-4.35-4.35"></path>
          </svg>
          <div class="agents-empty-title">No matching modules found</div>
          <div class="agents-empty-desc">Try clearing your search query or switching to another category.</div>
          <button type="button" class="agents-btn-simulate" id="agentsResetFilter">Reset All Filters</button>
        </div>
      `;
      const resetBtn = document.getElementById("agentsResetFilter");
      if (resetBtn) {
        resetBtn.addEventListener("click", () => {
          activeCategory = "all";
          activeType = "all";
          searchKeyword = "";
          const searchInput = document.getElementById("agentsSearchInput");
          if (searchInput) searchInput.value = "";
          renderCatalogPage();
        });
      }
      return;
    }

    // If searching or filtering by a specific category/type:
    if (searchKeyword || activeCategory !== "all" || activeType !== "all") {
      grid.innerHTML = `
        <div class="agents-grid" style="grid-column: 1 / -1;">
          ${filtered.map((item) => renderCardHTML(item)).join("")}
        </div>
      `;
    } else {
      // "All" view: RENDER BY CATEGORIES!
      let categorizedHTML = "";
      CATEGORY_META.forEach((cat) => {
        const catItems = filtered.filter((i) => i.group === cat.id);
        if (catItems.length === 0) return;

        categorizedHTML += `
          <div class="agents-category-group" id="cat-${cat.id}">
            <div class="agents-category-banner">
              <div class="agents-category-banner-left">
                <span class="agents-category-tag">${cat.badge}</span>
                <h3 class="agents-category-name">
                  <span>${cat.name}</span>
                  <span class="agents-category-count-badge">${catItems.length}</span>
                </h3>
                <p class="agents-category-desc">${cat.desc}</p>
              </div>
            </div>
            <div class="agents-grid">
              ${catItems.map((item) => renderCardHTML(item)).join("")}
            </div>
          </div>
        `;
      });
      grid.innerHTML = `<div style="grid-column: 1 / -1;">${categorizedHTML}</div>`;
    }

    attachCardHandlers(grid);
  }

  function renderCardHTML(item) {
    const isAgent = item.type === "agent";
    const typeBadge = isAgent
      ? `<span class="agent-type-badge badge-agent">
           <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
             <path d="M12 2a4 4 0 0 1 4 4c0 1.1-.9 2-2 2h-4c-1.1 0-2-.9-2-2a4 4 0 0 1 4-4z"></path>
             <path d="M6 10v4c0 3.3 2.7 6 6 6s6-2.7 6-6v-4"></path>
           </svg>
           AI Agent
         </span>`
      : `<span class="agent-type-badge badge-workflow">
           <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
             <polyline points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polyline>
           </svg>
           Workflow
         </span>`;

    const modelName = (item.model || "").includes("gemini")
      ? "Gemini 3.5 Flash"
      : (item.model || "").includes("Deterministic")
      ? "Rules Engine"
      : item.model;

    const governanceBadge = item.requiresApproval
      ? `<span class="agent-gate-chip gate-hitl" title="Human Review Guardrail Enabled">
           <span class="gate-dot hitl-dot"></span>HITL Gate
         </span>`
      : `<span class="agent-gate-chip gate-auto" title="Autonomous Guardrail Boundaries">
           <span class="gate-dot auto-dot"></span>Autonomous
         </span>`;

    const toolsHTML = (item.tools || [])
      .slice(0, 3)
      .map((t) => `<span class="agent-tool-tag">${t}</span>`)
      .join("");

    return `
      <div class="agent-card" data-agent-id="${item.id}">
        <div class="agent-card-inner">
          <div class="agent-card-header">
            <div class="agent-card-badges">
              <span class="agent-code-badge">${item.code}</span>
              ${typeBadge}
              <span class="agent-model-chip">${modelName}</span>
            </div>
            <div class="agent-card-header-right">
              ${governanceBadge}
            </div>
          </div>

          <h3 class="agent-card-title">${item.name}</h3>

          <div class="agent-card-meta-strip">
            <span class="agent-meta-chip">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
              </svg>
              ${item.groupLabel}
            </span>
            <span class="agent-meta-chip">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
              </svg>
              ${item.trigger}
            </span>
          </div>

          <p class="agent-card-desc">${item.description}</p>
        </div>

        <div class="agent-card-footer-group">
          <div class="agent-metrics-row">
            <div class="agent-metric-item">
              <span class="agent-metric-label">Latency</span>
              <span class="agent-metric-val val-latency">${item.avgDurationMs}ms</span>
            </div>
            <div class="agent-metric-item">
              <span class="agent-metric-label">Accuracy</span>
              <span class="agent-metric-val val-success">${item.successRate.toFixed(1)}%</span>
            </div>
            <div class="agent-metric-item">
              <span class="agent-metric-label">Saved</span>
              <span class="agent-metric-val val-saved">${Math.round(item.timeSavedHours)}h/mo</span>
            </div>
          </div>

          <div class="agent-tools-row">
            <span class="agent-tools-label">Stack:</span>
            <div class="agent-tools-container">
              ${toolsHTML}
              ${(item.tools || []).length > 3 ? `<span class="agent-tool-tag tag-more">+${item.tools.length - 3}</span>` : ""}
            </div>
          </div>

          <div class="agent-card-actions">
            <button type="button" class="agent-btn-simulate" data-action="simulate" data-id="${item.id}" aria-label="Simulate ${item.name}">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
                <polygon points="5 3 19 12 5 21 5 3"></polygon>
              </svg>
              <span>Simulate</span>
            </button>
            <button type="button" class="agent-btn-details" data-action="details" data-id="${item.id}" aria-label="Inspect ${item.name} Architecture" title="View Technical Architecture &amp; Schemas">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="16 18 22 12 16 6"></polyline>
                <polyline points="8 6 2 12 8 18"></polyline>
              </svg>
              <span>Specs</span>
            </button>
          </div>
        </div>
      </div>
    `;
  }

  function attachCardHandlers(container) {
    container.querySelectorAll(".agent-card").forEach((card) => {
      card.addEventListener("mousemove", (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        card.style.setProperty("--mouse-x", `${x}px`);
        card.style.setProperty("--mouse-y", `${y}px`);
      });
    });

    container.querySelectorAll("[data-action='simulate']").forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = btn.dataset.id;
        const item = catalog.items.find((i) => i.id === id);
        if (item) openSimulationModal(item);
      });
    });

    container.querySelectorAll("[data-action='details']").forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = btn.dataset.id;
        const item = catalog.items.find((i) => i.id === id);
        if (item) openDetailsModal(item);
      });
    });
  }

  function getFilteredItems() {
    return catalog.items.filter((item) => {
      // Type Filter
      if (activeType === "agents" && item.type !== "agent") return false;
      if (activeType === "workflows" && item.type !== "workflow") return false;

      // Category Filter
      if (activeCategory === "type-agent" && item.type !== "agent") return false;
      if (activeCategory === "type-workflow" && item.type !== "workflow") return false;
      if (
        activeCategory !== "all" &&
        activeCategory !== "type-agent" &&
        activeCategory !== "type-workflow" &&
        item.group !== activeCategory
      ) {
        return false;
      }

      // Keyword Search
      if (searchKeyword) {
        const searchable = [
          item.name,
          item.code,
          item.description,
          item.category,
          item.groupLabel,
          item.model,
          item.trigger,
          ...(item.tools || []),
        ]
          .join(" ")
          .toLowerCase();

        if (!searchable.includes(searchKeyword)) {
          return false;
        }
      }

      return true;
    });
  }

  function setupEventListeners() {
    const searchInput = document.getElementById("agentsSearchInput");
    const clearBtn = document.getElementById("agentsSearchClear");
    const typeButtons = document.querySelectorAll(".agents-type-btn");
    const modalBackdrop = document.getElementById("agentSimModal");
    const modalCloseBtn = document.getElementById("agentModalClose");

    if (searchInput) {
      searchInput.addEventListener("input", (e) => {
        searchKeyword = e.target.value.trim().toLowerCase();
        if (clearBtn) clearBtn.style.display = searchKeyword.length > 0 ? "flex" : "none";
        if (isDedicatedPage) renderCatalogPage();
      });
    }

    if (clearBtn && searchInput) {
      clearBtn.addEventListener("click", () => {
        searchInput.value = "";
        searchKeyword = "";
        clearBtn.style.display = "none";
        searchInput.focus();
        if (isDedicatedPage) renderCatalogPage();
      });
    }

    typeButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        typeButtons.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        activeType = btn.dataset.typeFilter || "all";
        if (isDedicatedPage) renderCatalogPage();
      });
    });

    if (modalCloseBtn && modalBackdrop) {
      modalCloseBtn.addEventListener("click", () => closeModal());
    }

    if (modalBackdrop) {
      modalBackdrop.addEventListener("click", (e) => {
        if (e.target === modalBackdrop) closeModal();
      });
    }

    if (typeof window !== "undefined" && window.addEventListener) {
      window.addEventListener("keydown", (e) => {
        if (e.key === "Escape") closeModal();
        if (e.key === "/" && document.activeElement !== searchInput) {
          if (searchInput) {
            e.preventDefault();
            searchInput.focus();
          }
        }
      });
    }
  }

  // --- MODAL LOGIC ---
  function openSimulationModal(item) {
    const modal = document.getElementById("agentSimModal");
    if (!modal) return;

    const titleEl = document.getElementById("agentModalTitle");
    const subtitleEl = document.getElementById("agentModalSubtitle");
    const telemetryEl = document.getElementById("agentModalTelemetry");
    const payloadInputEl = document.getElementById("agentPayloadInput");
    const runBtn = document.getElementById("agentModalRunBtn");

    if (titleEl) titleEl.textContent = `${item.code} — ${item.name}`;
    if (subtitleEl) subtitleEl.textContent = `${item.typeLabel} • Backbone: ${item.model}`;

    if (telemetryEl) {
      telemetryEl.innerHTML = `
        <div class="agent-sim-telemetry-item">
          <span>Target SLA:</span>
          <strong>${item.avgDurationMs}ms</strong>
        </div>
        <div class="agent-sim-telemetry-item">
          <span>Success Rate:</span>
          <strong style="color: #10b981">${item.successRate.toFixed(1)}%</strong>
        </div>
        <div class="agent-sim-telemetry-item">
          <span>Safety Policy:</span>
          <strong>${item.requiresApproval ? "Approval Gate Active" : "Self-Governed Guardrails"}</strong>
        </div>
        <div class="agent-sim-telemetry-item">
          <span>Total Executions:</span>
          <strong>${item.runsCount.toLocaleString()}</strong>
        </div>
      `;
    }

    if (payloadInputEl) {
      payloadInputEl.textContent = item.simulation.inputSample;
    }

    if (runBtn) {
      runBtn.onclick = () => runLiveSimulation(item);
    }

    modal.classList.add("active");
    document.body.style.overflow = "hidden";
    runLiveSimulation(item);
  }

  function runLiveSimulation(item) {
    const terminalLogsEl = document.getElementById("agentTerminalLogs");
    const runBtn = document.getElementById("agentModalRunBtn");
    if (!terminalLogsEl) return;

    if (simulationTimer) {
      clearTimeout(simulationTimer);
      simulationTimer = null;
    }

    if (runBtn) {
      runBtn.disabled = true;
      runBtn.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin">
          <circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-linecap="round"></circle>
        </svg>
        Executing Phases...
      `;
    }

    terminalLogsEl.innerHTML = `
      <div class="terminal-line" style="opacity: 1;">
        <span class="terminal-time">[00:00.00]</span>
        <span class="terminal-phase">[INIT]</span>
        <span class="terminal-msg">Initializing runtime session for ${item.code} (${item.key})...</span>
      </div>
    `;

    const phases = item.simulation.phases || [];
    let stepIndex = 0;

    function nextStep() {
      if (stepIndex >= phases.length) {
        const doneLine = document.createElement("div");
        doneLine.className = "terminal-line";
        doneLine.innerHTML = `
          <span class="terminal-time">[00:0${stepIndex + 1}.20]</span>
          <span class="terminal-phase" style="color: #10b981;">[RESULT]</span>
          <span class="terminal-success">${item.simulation.outputSample}</span>
        `;
        terminalLogsEl.appendChild(doneLine);
        terminalLogsEl.scrollTop = terminalLogsEl.scrollHeight;

        if (runBtn) {
          runBtn.disabled = false;
          runBtn.innerHTML = `
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
              <polygon points="5 3 19 12 5 21 5 3"></polygon>
            </svg>
            Re-run Simulation
          `;
        }
        return;
      }

      const p = phases[stepIndex];
      const line = document.createElement("div");
      line.className = "terminal-line";
      line.innerHTML = `
        <span class="terminal-time">[00:0${stepIndex + 1}.05]</span>
        <span class="terminal-phase">[${p.name || p.phase}]</span>
        <span class="terminal-msg">${p.desc || p.label} <span style="color:#71717a">(${p.time || p.latency})</span></span>
      `;
      terminalLogsEl.appendChild(line);
      terminalLogsEl.scrollTop = terminalLogsEl.scrollHeight;

      stepIndex++;
      simulationTimer = setTimeout(nextStep, 260);
    }

    simulationTimer = setTimeout(nextStep, 150);
  }

  function openDetailsModal(item) {
    const modal = document.getElementById("agentSimModal");
    if (!modal) return;

    const titleEl = document.getElementById("agentModalTitle");
    const subtitleEl = document.getElementById("agentModalSubtitle");
    const telemetryEl = document.getElementById("agentModalTelemetry");
    const terminalLogsEl = document.getElementById("agentTerminalLogs");
    const payloadInputEl = document.getElementById("agentPayloadInput");
    const runBtn = document.getElementById("agentModalRunBtn");

    if (titleEl) titleEl.textContent = `${item.code} Architecture — ${item.name}`;
    if (subtitleEl) subtitleEl.textContent = `Technical Specifications & Guardrails`;

    if (telemetryEl) {
      telemetryEl.innerHTML = `
        <div class="agent-sim-telemetry-item">
          <span>Type:</span>
          <strong>${item.typeLabel}</strong>
        </div>
        <div class="agent-sim-telemetry-item">
          <span>Category:</span>
          <strong>${item.groupLabel}</strong>
        </div>
        <div class="agent-sim-telemetry-item">
          <span>Model Engine:</span>
          <strong>${item.model}</strong>
        </div>
      `;
    }

    if (payloadInputEl) {
      payloadInputEl.textContent = JSON.stringify(
        {
          module_id: item.id,
          trigger: item.trigger,
          tools: item.tools,
          governance: item.requiresApproval ? "Admin Approval Gate" : "Autonomous Guardrails",
          architecture_spec: item.spec || {},
        },
        null,
        2
      );
    }

    if (terminalLogsEl) {
      terminalLogsEl.innerHTML = `
        <div class="terminal-line" style="opacity: 1;">
          <span class="terminal-phase">[OBJECTIVE]</span>
          <span class="terminal-msg">${item.goal}</span>
        </div>
        <div class="terminal-line" style="opacity: 1;">
          <span class="terminal-phase">[INTEGRATIONS]</span>
          <span class="terminal-msg">${(item.tools || []).join(", ")}</span>
        </div>
        <div class="terminal-line" style="opacity: 1;">
          <span class="terminal-phase">[EXECUTION SLA]</span>
          <span class="terminal-msg">P95 Latency: ${item.avgDurationMs}ms | Success Rate: ${item.successRate.toFixed(1)}% | Monthly Runs: ${item.runsCount}</span>
        </div>
        <div class="terminal-line" style="opacity: 1;">
          <span class="terminal-phase">[GUARDRAILS]</span>
          <span class="terminal-msg">${item.requiresApproval ? "Human Approval Checkpoint Enabled before committing external actions." : "Automated policy validation and rate limiting enabled."}</span>
        </div>
      `;
    }

    if (runBtn) {
      runBtn.onclick = () => runLiveSimulation(item);
      runBtn.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
          <polygon points="5 3 19 12 5 21 5 3"></polygon>
        </svg>
        Run Test Simulation
      `;
    }

    modal.classList.add("active");
    document.body.style.overflow = "hidden";
  }

  function closeModal() {
    const modal = document.getElementById("agentSimModal");
    if (!modal) return;
    modal.classList.remove("active");
    document.body.style.overflow = "";
    if (simulationTimer) {
      clearTimeout(simulationTimer);
      simulationTimer = null;
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
