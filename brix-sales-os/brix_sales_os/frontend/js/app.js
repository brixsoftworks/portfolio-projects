/**
 * Brix Sales OS — Master Client Engine Frontend Controller
 */

const API_BASE = "/api";

async function fetchJSON(url, options = {}) {
  try {
    const res = await fetch(url, options);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || res.statusText);
    }
    return await res.json();
  } catch (e) {
    console.error(`API Error on ${url}:`, e);
    throw e;
  }
}

// ─── Tab Navigation ────────────────────────────────────────────────────────

function switchTab(tabId) {
  document.querySelectorAll(".nav-item").forEach(el => el.classList.remove("active"));
  document.querySelectorAll(".view-container").forEach(el => el.classList.remove("active"));

  const navEl = document.querySelector(`.nav-item[data-tab="${tabId}"]`);
  const viewEl = document.getElementById(`view-${tabId}`);
  if (navEl) navEl.classList.add("active");
  if (viewEl) viewEl.classList.add("active");

  const titleMap = {
    overview: "Commercial Overview",
    leads: "B2B Lead Explorer",
    agents: "AI Agent Control Center",
    campaigns: "Campaign Review Queue",
    inbox: "Unified Communications Inbox",
    deals: "Deal Pipeline (Kanban)",
    proposals: "Proposal Studio & Statements of Work",
    workflows: "Workflow Capability Registry (60 Agents)",
    settings: "System & Compliance Settings"
  };
  document.getElementById("page-title-text").innerText = titleMap[tabId] || "Brix Sales OS";

  // Load view-specific data
  if (tabId === "overview") loadTelemetry();
  if (tabId === "leads") loadLeads();
  if (tabId === "agents") loadAgents();
  if (tabId === "campaigns") loadCampaignQueue();
  if (tabId === "inbox") loadInbox();
  if (tabId === "deals") loadDeals();
  if (tabId === "workflows") loadWorkflows();
  if (tabId === "settings") loadSettings();
}

// ─── Telemetry & Overview ──────────────────────────────────────────────────

async function loadTelemetry() {
  try {
    const data = await fetchJSON(`${API_BASE}/telemetry`);
    document.getElementById("kpi-prospects").innerText = data.prospects_discovered;
    document.getElementById("kpi-qualified").innerText = data.qualified_leads;
    document.getElementById("kpi-drafts").innerText = data.drafts_awaiting_approval;
    document.getElementById("kpi-sent").innerText = data.messages_sent;
    document.getElementById("kpi-meetings").innerText = data.meetings_booked;
    document.getElementById("kpi-won").innerText = data.deals_won;
    document.getElementById("kpi-revenue").innerText = `$${data.verified_revenue_usd.toLocaleString()}`;
    document.getElementById("kpi-pipeline").innerText = `$${data.pipeline_value_usd.toLocaleString()}`;

    // Emergency pill
    const emPill = document.getElementById("emergency-pill");
    if (data.emergency_stop) {
      emPill.style.display = "inline-flex";
      emPill.innerText = "🛑 EMERGENCY STOP ACTIVE";
      emPill.className = "status-pill btn-danger";
    } else {
      emPill.style.display = "none";
    }

    // Mode indicator
    document.getElementById("mode-indicator").innerText = data.operating_mode;
  } catch (e) {
    console.error("Telemetry failed", e);
  }
}

// ─── Lead Explorer ─────────────────────────────────────────────────────────

async function loadLeads() {
  const container = document.getElementById("leads-table-body");
  container.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:24px;">Loading prospects...</td></tr>`;

  try {
    const leads = await fetchJSON(`${API_BASE}/leads`);
    if (!leads.length) {
      container.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:24px; color:#64748b;">No leads ingested yet. Click "Discover Leads" above.</td></tr>`;
      return;
    }

    container.innerHTML = leads.map(l => {
      const badgeClass = l.priority === "HIGH" ? "badge-high" : (l.priority === "MEDIUM" ? "badge-medium" : "badge-low");
      const matchedStr = l.matched_workflows && l.matched_workflows.length ? l.matched_workflows.slice(0, 2).join(", ") : "None";
      return `
        <tr>
          <td>
            <strong>${l.company_name}</strong><br/>
            <span style="font-size:11px; color:#64748b;"><a href="${l.website}" target="_blank" style="color:#38bdf8; text-decoration:none;">${l.domain}</a> &bull; ${l.country}</span>
          </td>
          <td>${l.industry || "General"}</td>
          <td>
            ${l.contact_name}<br/>
            <span style="font-size:11px; color:#64748b;">${l.contact_email}</span>
          </td>
          <td>
            <span class="badge ${badgeClass}">${l.lead_score !== null ? l.lead_score + '/100' : 'Unscored'} (${l.priority})</span>
          </td>
          <td>
            <span style="color:#a855f7; font-weight:600;">${l.recommended_offer || 'TBD'}</span><br/>
            <span style="font-size:11px; color:#64748b;">${matchedStr}</span>
          </td>
          <td>
            <span style="color:#22c55e; font-weight:700;">$${l.deal_amount}</span><br/>
            <span style="font-size:11px; color:#94a3b8;">${l.deal_stage}</span>
          </td>
          <td>
            <button class="btn btn-primary" style="padding:4px 10px; font-size:11px;" onclick="runPipelineForLead('${l.id}')">⚡ Run AI Pipeline</button>
          </td>
        </tr>
      `;
    }).join("");
  } catch (e) {
    container.innerHTML = `<tr><td colspan="7" style="color:#ef4444; padding:24px;">Failed to load leads: ${e.message}</td></tr>`;
  }
}

async function triggerLeadDiscovery() {
  const btn = document.getElementById("btn-discover");
  btn.disabled = true;
  btn.innerText = "Discovering...";
  try {
    await fetchJSON(`${API_BASE}/leads/discover`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({})
    });
    alert("Lead Discovery successfully executed! Ingested qualified prospects.");
    loadLeads();
    loadTelemetry();
  } catch (e) {
    alert("Error discovering leads: " + e.message);
  } finally {
    btn.disabled = false;
    btn.innerText = "🔍 Discover Leads";
  }
}

async function runPipelineForLead(orgId) {
  if (!confirm("Run complete AI intelligence, scoring, solution matching, demo, and outreach drafting for this lead?")) return;
  try {
    const res = await fetchJSON(`${API_BASE}/leads/${orgId}/process-full-pipeline`, { method: "POST" });
    alert("Pipeline finished! Generated research, score, solution match, and pending outreach draft.");
    loadLeads();
    loadTelemetry();
  } catch (e) {
    alert("Pipeline error: " + e.message);
  }
}

// ─── AI Agents Control Center ──────────────────────────────────────────────

async function loadAgents() {
  const container = document.getElementById("agents-grid");
  container.innerHTML = `<div style="grid-column: 1/-1; text-align:center; padding:24px;">Loading agent telemetry...</div>`;

  try {
    const agents = await fetchJSON(`${API_BASE}/agents`);
    container.innerHTML = agents.map(a => {
      const isOk = a.last_status !== "FAILED";
      const statusColor = a.status === "RUNNING" ? "#eab308" : (isOk ? "#22c55e" : "#ef4444");
      return `
        <div style="background:#0f172a; border: 1px solid rgba(255,255,255,0.08); border-radius:12px; padding:18px;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <span style="font-family:monospace; font-size:11px; color:#38bdf8; font-weight:700;">${a.agent_id}</span>
            <span style="font-size:11px; padding:2px 8px; border-radius:12px; background:rgba(34,197,94,0.15); color:${statusColor}; font-weight:700;">${a.status}</span>
          </div>
          <h4 style="margin:0 0 8px 0; color:#fff; font-size:14px;">${a.name}</h4>
          <div style="font-size:12px; color:#94a3b8; line-height:1.6;">
            <div><strong>Runs:</strong> ${a.total_runs} &bull; <strong>Success:</strong> ${a.success_rate}%</div>
            <div><strong>Last Latency:</strong> ${a.duration_ms} ms</div>
            <div><strong>Last Run:</strong> ${a.last_executed ? new Date(a.last_executed).toLocaleTimeString() : 'Never'}</div>
          </div>
        </div>
      `;
    }).join("");
  } catch (e) {
    container.innerHTML = `<div style="color:#ef4444;">Failed to load agents: ${e.message}</div>`;
  }
}

// ─── Campaign Review Queue ─────────────────────────────────────────────────

async function loadCampaignQueue() {
  const container = document.getElementById("campaign-queue-body");
  container.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:24px;">Loading review queue...</td></tr>`;

  try {
    const queue = await fetchJSON(`${API_BASE}/campaigns/review-queue`);
    if (!queue.length) {
      container.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:24px; color:#64748b;">No messages awaiting review. Run AI pipeline on leads to create drafts.</td></tr>`;
      return;
    }

    container.innerHTML = queue.map(m => `
      <tr>
        <td>
          <strong>${m.company_name}</strong><br/>
          <span style="font-size:11px; color:#64748b;">${m.contact_name} &bull; ${m.contact_email}</span>
        </td>
        <td><strong style="color:#38bdf8;">${m.subject}</strong></td>
        <td style="max-width:380px; font-size:12px; color:#cbd5e1; white-space:pre-wrap; font-family:monospace;">${m.body_text}</td>
        <td><span class="badge badge-medium">PENDING APPROVAL</span></td>
        <td>
          <div style="display:flex; gap:6px;">
            <button class="btn btn-success" style="padding:4px 10px; font-size:11px;" onclick="reviewMessage('${m.message_id}', true)">✓ Approve</button>
            <button class="btn btn-danger" style="padding:4px 10px; font-size:11px;" onclick="reviewMessage('${m.message_id}', false)">✕ Reject</button>
          </div>
        </td>
      </tr>
    `).join("");
  } catch (e) {
    container.innerHTML = `<tr><td colspan="5" style="color:#ef4444; padding:24px;">Failed to load queue: ${e.message}</td></tr>`;
  }
}

async function reviewMessage(messageId, approved) {
  try {
    await fetchJSON(`${API_BASE}/campaigns/review`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message_id: messageId, approved: approved })
    });
    loadCampaignQueue();
    loadTelemetry();
  } catch (e) {
    alert("Error reviewing message: " + e.message);
  }
}

async function dispatchApprovedQueue() {
  if (!confirm("Dispatch all approved messages in the queue?")) return;
  try {
    const res = await fetchJSON(`${API_BASE}/campaigns/dispatch`, { method: "POST" });
    alert(`Dispatched ${res.dispatched_count} messages safely.`);
    loadCampaignQueue();
    loadTelemetry();
  } catch (e) {
    alert("Dispatch error: " + e.message);
  }
}

// ─── Unified Inbox ─────────────────────────────────────────────────────────

async function loadInbox() {
  const container = document.getElementById("inbox-list");
  container.innerHTML = `<div style="text-align:center; padding:24px;">Loading messages...</div>`;

  try {
    const convs = await fetchJSON(`${API_BASE}/inbox`);
    if (!convs.length) {
      container.innerHTML = `<div style="text-align:center; padding:24px; color:#64748b;">No incoming communications recorded yet.</div>`;
      return;
    }

    container.innerHTML = convs.map(c => `
      <div style="background:#0f172a; border:1px solid rgba(255,255,255,0.08); border-radius:10px; padding:18px; margin-bottom:14px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
          <div>
            <strong>${c.contact_name}</strong> (${c.company_name}) &bull; <span style="font-size:12px; color:#64748b;">${c.contact_email}</span>
          </div>
          <span class="badge ${c.intent === 'UNSUBSCRIBE' ? 'badge-low' : 'badge-high'}">${c.intent}</span>
        </div>
        <p style="background:#090d16; padding:12px; border-radius:6px; font-size:13px; color:#cbd5e1; margin-bottom:12px;">"${c.incoming_message}"</p>
        ${c.suggested_reply ? `
          <div style="border-top:1px solid rgba(255,255,255,0.06); padding-top:10px;">
            <div style="font-size:11px; text-transform:uppercase; color:#38bdf8; font-weight:700; margin-bottom:4px;">AI Suggested Reply (Requires Approval):</div>
            <div style="font-size:12px; color:#94a3b8; white-space:pre-wrap; background:#1e293b; padding:10px; border-radius:6px;">${c.suggested_reply}</div>
          </div>
        ` : ''}
      </div>
    `).join("");
  } catch (e) {
    container.innerHTML = `<div style="color:#ef4444;">Failed to load inbox: ${e.message}</div>`;
  }
}

// ─── Deal Pipeline (Kanban) ────────────────────────────────────────────────

async function loadDeals() {
  try {
    const deals = await fetchJSON(`${API_BASE}/deals`);
    const stages = ["NEW_LEAD", "QUALIFIED", "INTERESTED", "MEETING", "PROPOSAL", "WON"];
    
    stages.forEach(s => {
      const col = document.getElementById(`kanban-${s}`);
      if (!col) return;
      const matched = deals.filter(d => d.stage === s);
      col.innerHTML = matched.map(d => `
        <div class="deal-card">
          <div class="deal-title">${d.title}</div>
          <div style="font-size:12px; color:#94a3b8; margin-bottom:8px;">${d.company_name}</div>
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <span class="deal-val">$${d.amount}</span>
            <span class="badge badge-purple">${d.matched_offer}</span>
          </div>
        </div>
      `).join("");
    });
  } catch (e) {
    console.error("Failed to load deals", e);
  }
}

// ─── Workflows Registry ────────────────────────────────────────────────────

async function loadWorkflows() {
  const container = document.getElementById("workflows-table-body");
  container.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:24px;">Loading 60 workflows...</td></tr>`;

  try {
    const items = await fetchJSON(`${API_BASE}/workflows`);
    container.innerHTML = items.map(w => `
      <tr>
        <td><strong style="color:#38bdf8; font-family:monospace;">${w.id}</strong></td>
        <td><strong>${w.name}</strong></td>
        <td><span class="badge badge-purple">${w.department}</span></td>
        <td>${w.node_count} nodes (${w.trigger_type})</td>
        <td>
          <span style="color:#22c55e; font-weight:700;">$${w.suggested_setup_usd} setup</span><br/>
          <span style="font-size:11px; color:#64748b;">$${w.suggested_monthly_usd}/mo</span>
        </td>
        <td><span class="badge badge-high">${w.operational_status}</span></td>
      </tr>
    `).join("");
  } catch (e) {
    container.innerHTML = `<tr><td colspan="6" style="color:#ef4444; padding:24px;">Failed to load workflows: ${e.message}</td></tr>`;
  }
}

// ─── Emergency & Mode Controls ─────────────────────────────────────────────

async function toggleEmergencyStop() {
  const confirmed = confirm("Are you sure you want to toggle the Global Emergency Stop switch?");
  if (!confirmed) return;

  const current = document.getElementById("emergency-pill").style.display !== "none";
  try {
    await fetchJSON(`${API_BASE}/emergency-stop`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ active: !current })
    });
    loadTelemetry();
  } catch (e) {
    alert("Error setting emergency stop: " + e.message);
  }
}

async function setMode(mode) {
  try {
    await fetchJSON(`${API_BASE}/mode`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode: mode })
    });
    alert(`Switched operating mode to: ${mode}`);
    loadTelemetry();
  } catch (e) {
    alert("Error changing mode: " + e.message);
  }
}

async function loadSettings() {
  try {
    const res = await fetchJSON(`${API_BASE}/mailer/status`);
    const statusBox = document.getElementById("mailer-status-box");
    if (res.configured && res.success) {
      statusBox.innerHTML = `<span style="color:#22c55e;">✓ Connected as ${res.email} (SMTP: OK &bull; IMAP: OK)</span>`;
    } else if (res.configured) {
      statusBox.innerHTML = `<span style="color:#ef4444;">✕ Failed: ${res.smtp_status}</span>`;
    } else {
      statusBox.innerText = "Status: Not configured";
    }
  } catch (e) {
    console.error("Failed to load mailer status", e);
  }
}

async function saveMailerCredentials() {
  const emailAddr = document.getElementById("mailer-email").value.trim();
  const appKey = document.getElementById("mailer-key").value.trim();
  if (!emailAddr || !appKey) {
    alert("Please provide both your sender email address and App Password.");
    return;
  }

  const statusBox = document.getElementById("mailer-status-box");
  statusBox.innerText = "Testing SMTP & IMAP connection...";

  try {
    const res = await fetchJSON(`${API_BASE}/mailer/configure`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email_address: emailAddr, app_password: appKey, provider: "gmail" })
    });

    if (res.success) {
      statusBox.innerHTML = `<span style="color:#22c55e; font-weight:700;">✓ Successfully connected! Inbound & Outbound ready.</span>`;
      alert("App Key verified! Inbound reply detection and automated follow-up sequences are now active.");
    } else {
      statusBox.innerHTML = `<span style="color:#ef4444; font-weight:700;">✕ Connection Failed. ${res.smtp_status} | ${res.imap_status}</span>`;
      alert("Connection check failed. Please verify your App Password.");
    }
  } catch (e) {
    statusBox.innerText = "Error: " + e.message;
    alert("Error configuring mailer: " + e.message);
  }
}

async function checkMailerReplies() {
  try {
    const res = await fetchJSON(`${API_BASE}/mailer/check-replies`, { method: "POST" });
    alert(`Scanned inbox: Detected ${res.replies_detected} prospect replies.`);
    loadInbox();
    loadTelemetry();
  } catch (e) {
    alert("Error checking inbox: " + e.message);
  }
}

// Initialize on DOM load
document.addEventListener("DOMContentLoaded", () => {
  switchTab("overview");
  // Auto refresh telemetry every 15s
  setInterval(loadTelemetry, 15000);
});
