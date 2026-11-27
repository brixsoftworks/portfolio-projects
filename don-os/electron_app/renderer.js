// ==========================================================================
// DON OS - Native Linux Workstation Copilot Controller
// Pure Minimalist Chat Interface & High-Speed Voice Engine
// ==========================================================================

const BACKEND_URL = (window.api && window.api.backendUrl) ? window.api.backendUrl : 'http://127.0.0.1:8765';

let voiceEnabled = true;

// Header Controls
const voiceToggleBtn = document.getElementById('voiceToggleBtn');
const voiceIconOn = document.getElementById('voiceIconOn');
const voiceIconOff = document.getElementById('voiceIconOff');
const voiceLabel = document.getElementById('voiceLabel');
const handsFreeBtn = document.getElementById('handsFreeBtn');
const handsFreeLabel = document.getElementById('handsFreeLabel');
const clearChatBtn = document.getElementById('clearChatBtn');

// Chat Viewport Elements
const chatLayoutWrapper = document.getElementById('chatLayoutWrapper');
const chatWelcomeBanner = document.getElementById('chatWelcomeBanner');
const desktopChatStream = document.getElementById('desktopChatStream');
const desktopPromptInput = document.getElementById('desktopPromptInput');
const desktopSendBtn = document.getElementById('desktopSendBtn');
const desktopMicBtn = document.getElementById('desktopMicBtn');
const desktopFleetBtn = document.getElementById('desktopFleetBtn');
let isFleetModeActive = true;
if (desktopFleetBtn) {
  desktopFleetBtn.addEventListener('click', () => {
    isFleetModeActive = !isFleetModeActive;
    desktopFleetBtn.classList.toggle('active', isFleetModeActive);
  });
}
const mcpPickerBtn = document.getElementById('mcpPickerBtn');
const mcpPickerPanel = document.getElementById('mcpPickerPanel');
const mcpServerList = document.getElementById('mcpServerList');
const mcpAttachmentBar = document.getElementById('mcpAttachmentBar');
const mcpSelectedCount = document.getElementById('mcpSelectedCount');
const mcpPanelMessage = document.getElementById('mcpPanelMessage');
const mcpConnectorForm = document.getElementById('mcpConnectorForm');
const mcpAddConnectorBtn = document.getElementById('mcpAddConnectorBtn');
const activeModelSelect = document.getElementById('activeModelSelect');
const manageModelsBtn = document.getElementById('manageModelsBtn');
const modelProvider = document.getElementById('modelProvider');
const modelEndpoint = document.getElementById('modelEndpoint');
const modelApiKey = document.getElementById('modelApiKey');
const modelApiKeyField = document.getElementById('modelApiKeyField');
const modelProviderHint = document.getElementById('modelProviderHint');
const modelConnectorForm = document.getElementById('modelConnectorForm');
const modelList = document.getElementById('modelList');
const modelPanelMessage = document.getElementById('modelPanelMessage');
const localModelCatalogList = document.getElementById('localModelCatalogList');
const localModelRuntimeStatus = document.getElementById('localModelRuntimeStatus');
const reloadLocalModelCatalogBtn = document.getElementById('reloadLocalModelCatalog');
const localModelProgress = document.getElementById('localModelProgress');
const localModelProgressMessage = document.getElementById('localModelProgressMessage');
const localModelProgressValue = document.getElementById('localModelProgressValue');
const localModelProgressBar = document.getElementById('localModelProgressBar');
const cancelLocalModelDownloadBtn = document.getElementById('cancelLocalModelDownload');
const localModelMessage = document.getElementById('localModelMessage');
let localModelCatalog = [];
let localModelDownloadJobId = null;
let localModelDownloadPollTimer = null;
let localModelPollBusy = false;
if (mcpPickerPanel) document.body.appendChild(mcpPickerPanel);

// Voice Assistant Status & Equalizer Capsule (Google/Alexa style)
const voiceStatusCapsule = document.getElementById('voiceStatusCapsule');
const voiceStatusText = document.getElementById('voiceStatusText');
const cancelVoiceBtn = document.getElementById('cancelVoiceBtn');
const voiceWaveBars = document.querySelector('.voice-wave-bars');
const vbars = document.querySelectorAll('.vbar');

const sendIconSvg = document.getElementById('sendIconSvg');
const stopIconSvg = document.getElementById('stopIconSvg');

// Claude-Style Live Artifact Canvas Preview Drawer Elements
const artifactCanvasDrawer = document.getElementById('artifactCanvasDrawer');
const artifactOverlayBackdrop = document.getElementById('artifactOverlayBackdrop');
const artifactTitle = document.getElementById('artifactTitle');
const artifactSubtitle = document.getElementById('artifactSubtitle');
const artifactTabDesktop = document.getElementById('artifactTabDesktop');
const artifactTabMobile = document.getElementById('artifactTabMobile');
const artifactViewportContainer = document.getElementById('artifactViewportContainer');
const artifactIframe = document.getElementById('artifactIframe');
const artifactCopyCodeBtn = document.getElementById('artifactCopyCodeBtn');
const artifactRefreshBtn = document.getElementById('artifactRefreshBtn');
const artifactCloseBtn = document.getElementById('artifactCloseBtn');

let isGenerating = false;
let currentAbortController = null;
let lastUserPrompt = '';
let currentArtifactCode = '';
let currentArtifactLang = '';
let orbVideoObserver = null;
const visibleOrbVideos = new Set();
let mcpServers = [];
const selectedMcpServers = new Set();

function mcpLogo(name) {
  const normalized = name.toLowerCase();
  const craftApp = normalized.match(/(?:^|[- ])(photocraft|vectorcraft|filmcraft|lightcraft|pdfcraft|effectcraft|designcraft|gridcraft|wordcraft|deckcraft|cadcraft|soundcraft|figcraft)(?:$|[- ])/);

  if (craftApp) return { kind: 'craft', src: `assets/mcp-icons/craft-${craftApp[1]}.png` };
  if (normalized.includes('foundry')) return { kind: 'foundry', src: 'assets/mcp-icons/foundry.svg' };
  if (normalized.includes('github') || normalized.includes('git-hub')) return { kind: 'github', src: 'assets/mcp-icons/github.svg' };
  if (normalized.includes('azure')) return { kind: 'azure', src: 'assets/mcp-icons/azure.svg' };
  if (normalized.includes('blender')) return { kind: 'blender', src: 'assets/mcp-icons/blender.svg' };
  if (normalized.includes('git')) return { kind: 'git', src: 'assets/mcp-icons/git.svg' };
  if (normalized.includes('filesystem') || normalized.includes('file-system')) return { kind: 'files', src: 'assets/mcp-icons/files.svg' };
  if (normalized.includes('desktop') || normalized.includes('system')) return { kind: 'system', src: 'assets/mcp-icons/system.svg' };
  return { kind: '', src: 'assets/mcp-icons/server.svg' };
}

function createMcpLogo(name) {
  const logoData = mcpLogo(name);
  const logo = document.createElement('span');
  logo.className = `mcp-server-logo ${logoData.kind}`;
  logo.setAttribute('aria-hidden', 'true');

  const image = document.createElement('img');
  image.src = logoData.src;
  image.alt = '';
  image.draggable = false;
  logo.append(image);
  return logo;
}


// ==========================================================================
// 1. Ambient Background Motion (Hardware Composited via CSS)
// ==========================================================================
function initAmbientCanvas() {
  // Ambient gradients are now smoothly handled by GPU compositor in CSS
  // eliminating canvas clearing and CPU redraw spikes.
}

function observeOrbVideos(root = document) {
  if (!orbVideoObserver) {
    orbVideoObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        const video = entry.target;
        if (entry.isIntersecting && !document.hidden) {
          visibleOrbVideos.add(video);
          video.play().catch(error => console.warn('Could not play orb animation:', error));
        } else {
          visibleOrbVideos.delete(video);
          video.pause();
        }
      });
    }, { threshold: 0.1 });
  }

  root.querySelectorAll('video').forEach(video => {
    video.muted = true;
    orbVideoObserver.observe(video);
  });
}

document.addEventListener('visibilitychange', () => {
  visibleOrbVideos.forEach(video => {
    if (document.hidden) {
      video.pause();
    } else {
      video.play().catch(error => console.warn('Could not resume orb animation:', error));
    }
  });
});


// ==========================================================================
// 2. Chat Conversation Engine
// ==========================================================================
desktopPromptInput.addEventListener('input', () => {
  desktopPromptInput.style.height = 'auto';
  desktopPromptInput.style.height = Math.min(desktopPromptInput.scrollHeight, 140) + 'px';
});

desktopPromptInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    submitChatInput();
  }
});

desktopSendBtn.addEventListener('click', submitChatInput);

async function mcpRequest(path, options = {}) {
  const response = await fetch(`${BACKEND_URL}${path}`, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || `Connector request failed (${response.status}).`);
  }
  return data;
}

function showMcpPanelMessage(message, isError = false) {
  if (!mcpPanelMessage) return;
  mcpPanelMessage.textContent = message;
  mcpPanelMessage.classList.toggle('error', isError);
  mcpPanelMessage.classList.toggle('hidden', !message);
}

function updateMcpAttachments() {
  if (!mcpAttachmentBar || !mcpSelectedCount || !mcpPickerBtn) return;
  mcpAttachmentBar.replaceChildren();
  const selected = mcpServers.filter(server => selectedMcpServers.has(server.name));

  selected.forEach(server => {
    const chip = document.createElement('button');
    chip.type = 'button';
    chip.className = 'mcp-attachment-chip';
    chip.title = `Remove ${server.name} from this message`;
    const logo = createMcpLogo(server.name);
    const label = document.createElement('span');
    label.textContent = server.name;
    const remove = document.createElement('span');
    remove.setAttribute('aria-hidden', 'true');
    remove.textContent = '×';
    chip.append(logo, label, remove);
    chip.addEventListener('click', () => {
      selectedMcpServers.delete(server.name);
      renderMcpServerList();
    });
    mcpAttachmentBar.appendChild(chip);
  });

  mcpAttachmentBar.classList.toggle('hidden', selected.length === 0);
  mcpSelectedCount.textContent = String(selected.length);
  mcpSelectedCount.classList.toggle('hidden', selected.length === 0);
  mcpPickerBtn.setAttribute(
    'aria-label',
    selected.length ? `${selected.length} MCP connector${selected.length === 1 ? '' : 's'} attached` : 'Attach MCP connectors'
  );
}

function positionMcpPickerPanel() {
  if (!mcpPickerPanel || !mcpPickerBtn || mcpPickerPanel.classList.contains('hidden')) return;
  const anchor = mcpPickerBtn.getBoundingClientRect();
  const panel = mcpPickerPanel.getBoundingClientRect();
  const margin = 16;
  const left = Math.max(
    margin,
    Math.min(anchor.right - panel.width, window.innerWidth - panel.width - margin)
  );
  let top = anchor.top - panel.height - 12;
  if (top < margin) {
    top = Math.min(anchor.bottom + 12, window.innerHeight - panel.height - margin);
  }
  mcpPickerPanel.style.left = `${left}px`;
  mcpPickerPanel.style.top = `${Math.max(margin, top)}px`;
}

function renderMcpServerList() {
  if (!mcpServerList) return;
  mcpServerList.replaceChildren();

  if (!mcpServers.length) {
    const empty = document.createElement('p');
    empty.className = 'mcp-server-empty';
    empty.textContent = 'No connectors yet. Add an MCP server to make its tools available in chat.';
    mcpServerList.appendChild(empty);
  }

  mcpServers.forEach(server => {
    const row = document.createElement('div');
    row.className = 'mcp-server-row';

    const toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'mcp-server-toggle';
    const selected = selectedMcpServers.has(server.name);
    toggle.setAttribute('aria-pressed', String(selected));
    toggle.title = selected ? `Detach ${server.name}` : `Attach ${server.name} to this message`;

    const logo = createMcpLogo(server.name);

    const copy = document.createElement('span');
    copy.className = 'mcp-server-copy';
    const name = document.createElement('span');
    name.className = 'mcp-server-name';
    name.textContent = server.name;
    const detail = document.createElement('span');
    detail.className = 'mcp-server-detail';
    if (server.transport === 'http') {
      detail.textContent = `${server.command || 'Remote MCP'}${server.auth_configured ? '' : ' · auth may be needed'}`;
    } else {
      detail.textContent = server.command
        ? `${server.command}${server.env_keys?.length ? ` · ${server.env_keys.length} env vars` : ''}`
        : 'Local MCP server';
    }
    copy.append(name, detail);
    toggle.append(logo, copy);
    toggle.addEventListener('click', () => {
      if (selectedMcpServers.has(server.name)) {
        selectedMcpServers.delete(server.name);
      } else if (selectedMcpServers.size >= 5) {
        showMcpPanelMessage('Attach up to five connectors to one message.', true);
        return;
      } else {
        selectedMcpServers.add(server.name);
        showMcpPanelMessage('');
      }
      renderMcpServerList();
    });

    const actions = document.createElement('div');
    actions.className = 'mcp-server-actions';
    const test = document.createElement('button');
    test.type = 'button';
    test.className = 'mcp-server-action';
    test.textContent = 'Test';
    test.title = `Connect to ${server.name} and list its tools`;
    test.addEventListener('click', async () => {
      test.disabled = true;
      test.textContent = 'Testing…';
      showMcpPanelMessage(`Connecting to ${server.name}…`);
      try {
        const result = await mcpRequest(
          `/api/mcp/servers/${encodeURIComponent(server.name)}/test`,
          { method: 'POST' }
        );
        const toolCount = result.tools?.length || 0;
        showMcpPanelMessage(
          `Connected to ${server.name}. ${toolCount} ${toolCount === 1 ? 'tool' : 'tools'} discovered.`
        );
      } catch (error) {
        showMcpPanelMessage(error.message, true);
      } finally {
        test.disabled = false;
        test.textContent = 'Test';
      }
    });

    const remove = document.createElement('button');
    remove.type = 'button';
    remove.className = 'mcp-server-action remove';
    remove.textContent = 'Remove';
    remove.title = `Remove ${server.name}`;
    remove.addEventListener('click', async () => {
      if (!window.confirm(`Remove the "${server.name}" MCP connector from DON OS?`)) return;
      remove.disabled = true;
      try {
        await mcpRequest(`/api/mcp/servers/${encodeURIComponent(server.name)}`, { method: 'DELETE' });
        selectedMcpServers.delete(server.name);
        showMcpPanelMessage(`Removed ${server.name}.`);
        await loadMcpServers();
      } catch (error) {
        showMcpPanelMessage(error.message, true);
        remove.disabled = false;
      }
    });

    actions.append(test, remove);
    row.append(toggle, actions);
    mcpServerList.appendChild(row);
  });

  updateMcpAttachments();
  positionMcpPickerPanel();
}

async function loadMcpServers() {
  if (mcpServerList) {
    const loading = document.createElement('p');
    loading.className = 'mcp-server-empty';
    loading.textContent = 'Loading configured connectors…';
    mcpServerList.replaceChildren(loading);
  }
  try {
    const result = await mcpRequest('/api/mcp/servers');
    mcpServers = Array.isArray(result.servers) ? result.servers : [];
    for (const name of selectedMcpServers) {
      if (!mcpServers.some(server => server.name === name)) selectedMcpServers.delete(name);
    }
    renderMcpServerList();
  } catch (error) {
    mcpServers = [];
    renderMcpServerList();
    showMcpPanelMessage(error.message, true);
  }
}

if (mcpPickerBtn && mcpPickerPanel) {
  mcpPickerBtn.addEventListener('click', async event => {
    event.stopPropagation();
    const opening = mcpPickerPanel.classList.contains('hidden');
    mcpPickerPanel.classList.toggle('hidden', !opening);
    mcpPickerBtn.setAttribute('aria-expanded', String(opening));
    if (opening) {
      positionMcpPickerPanel();
      await loadMcpServers();
    }
  });

  mcpPickerPanel.addEventListener('click', event => event.stopPropagation());
  document.addEventListener('click', () => {
    mcpPickerPanel.classList.add('hidden');
    mcpPickerBtn.setAttribute('aria-expanded', 'false');
  });
}

window.addEventListener('resize', positionMcpPickerPanel);

document.getElementById('mcpPanelCloseBtn')?.addEventListener('click', () => {
  mcpPickerPanel?.classList.add('hidden');
  mcpPickerBtn?.setAttribute('aria-expanded', 'false');
});

mcpAddConnectorBtn?.addEventListener('click', () => {
  mcpConnectorForm?.classList.toggle('hidden');
  mcpAddConnectorBtn.classList.toggle('hidden', !mcpConnectorForm?.classList.contains('hidden'));
  showMcpPanelMessage('');
});

document.getElementById('mcpCancelAddBtn')?.addEventListener('click', () => {
  mcpConnectorForm?.reset();
  mcpConnectorForm?.classList.add('hidden');
  mcpAddConnectorBtn?.classList.remove('hidden');
});

mcpConnectorForm?.elements.transport?.addEventListener('change', event => {
  const isHttp = event.target.value === 'http';
  mcpConnectorForm.querySelectorAll('.mcp-stdio-field').forEach(field => {
    field.classList.toggle('hidden', isHttp);
  });
  mcpConnectorForm.querySelectorAll('.mcp-http-field').forEach(field => {
    field.classList.toggle('hidden', !isHttp);
  });
  mcpConnectorForm.elements.command.required = !isHttp;
  mcpConnectorForm.elements.url.required = isHttp;
});

mcpConnectorForm?.addEventListener('submit', async event => {
  event.preventDefault();
  const submit = mcpConnectorForm.querySelector('[type="submit"]');
  const formData = new FormData(mcpConnectorForm);
  const transport = String(formData.get('transport') || 'stdio');
  let args;
  let env;
  let headers;
  try {
    args = JSON.parse(String(formData.get('args') || '[]'));
    env = JSON.parse(String(formData.get('env') || '{}'));
    headers = JSON.parse(String(formData.get('headers') || '{}'));
    if (!Array.isArray(args) || !args.every(value => typeof value === 'string')) {
      throw new Error('Arguments must be a JSON array of strings.');
    }
    if (!env || Array.isArray(env) || typeof env !== 'object' ||
        Object.values(env).some(value => typeof value !== 'string')) {
      throw new Error('Environment must be a JSON object with text values.');
    }
    if (!headers || Array.isArray(headers) || typeof headers !== 'object' ||
        Object.values(headers).some(value => typeof value !== 'string')) {
      throw new Error('HTTP headers must be a JSON object with text values.');
    }
  } catch (error) {
    showMcpPanelMessage(error.message, true);
    return;
  }

  submit.disabled = true;
  showMcpPanelMessage('Saving connector…');
  try {
    await mcpRequest('/api/mcp/servers', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: formData.get('name'),
        command: formData.get('command'),
        transport,
        url: formData.get('url'),
        args,
        env,
        headers
      })
    });
    mcpConnectorForm.reset();
    mcpConnectorForm.classList.add('hidden');
    mcpAddConnectorBtn.classList.remove('hidden');
    showMcpPanelMessage('Connector saved. Test it to verify the server and discover its tools.');
    await loadMcpServers();
  } catch (error) {
    showMcpPanelMessage(error.message, true);
  } finally {
    submit.disabled = false;
  }
});

function setGeneratingState(generating) {
  isGenerating = generating;
  if (generating) {
    if (sendIconSvg) sendIconSvg.classList.add('hidden');
    if (stopIconSvg) stopIconSvg.classList.remove('hidden');
    desktopSendBtn.title = "Stop Generating";
  } else {
    if (sendIconSvg) sendIconSvg.classList.remove('hidden');
    if (stopIconSvg) stopIconSvg.classList.add('hidden');
    desktopSendBtn.title = "Send Instruction (Enter)";
  }
}

function submitChatInput() {
  if (isGenerating) {
    if (currentAbortController) {
      currentAbortController.abort();
      currentAbortController = null;
    }
    setGeneratingState(false);
    return;
  }
  const text = desktopPromptInput.value.trim();
  if (!text) return;
  desktopPromptInput.value = '';
  desktopPromptInput.style.height = 'auto';
  sendPrompt(text);
}

// Action chips in welcome banner
document.querySelectorAll('.action-chip').forEach(chip => {
  chip.addEventListener('click', () => {
    const prompt = chip.getAttribute('data-prompt');
    if (prompt) sendPrompt(prompt);
  });
});

function sanitizeText(raw) {
  if (typeof raw !== 'string') return String(raw);
  const trimmed = raw.trim();
  if (trimmed.startsWith('[') && trimmed.includes("'text':")) {
    const match = trimmed.match(/'text':\s*['"]([\s\S]*?)['"]\s*}/);
    if (match && match[1]) {
      return match[1].replace(/\\n/g, '\n');
    }
  }
  return raw;
}

// ==========================================================================
// Claude-Style Live Artifact Canvas Preview Drawer Controller
// ==========================================================================
function injectIntoIframe(iframe, code, lang = 'html') {
  let content = code;
  if (lang === 'svg' || (code.trim().startsWith('<svg') && code.trim().endsWith('</svg>'))) {
    content = `<!DOCTYPE html><html><head><style>body{margin:0;display:flex;align-items:center;justify-content:center;min-height:100vh;background:#ffffff;}</style></head><body>${code}</body></html>`;
  } else if (!code.includes('<html') && !code.includes('<!DOCTYPE')) {
    content = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 16px; color: #1e293b; }
  </style>
</head>
<body>
  ${code}
</body>
</html>`;
  }
  iframe.srcdoc = content;
}

function openArtifactCanvas(code, lang = 'html', title = 'Component Artifact') {
  currentArtifactCode = code;
  currentArtifactLang = lang;
  if (artifactTitle) artifactTitle.textContent = title;
  if (artifactSubtitle) artifactSubtitle.textContent = `${lang.toUpperCase()} Interactive Sandbox`;
  
  if (artifactIframe) {
    injectIntoIframe(artifactIframe, code, lang);
  }
  
  if (artifactCanvasDrawer) artifactCanvasDrawer.classList.add('open');
  if (artifactOverlayBackdrop) artifactOverlayBackdrop.classList.add('active');
}

function closeArtifactCanvas() {
  if (artifactCanvasDrawer) artifactCanvasDrawer.classList.remove('open');
  if (artifactOverlayBackdrop) artifactOverlayBackdrop.classList.remove('active');
}

if (artifactCloseBtn) artifactCloseBtn.addEventListener('click', closeArtifactCanvas);
if (artifactOverlayBackdrop) artifactOverlayBackdrop.addEventListener('click', closeArtifactCanvas);
window.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    closeArtifactCanvas();
    mcpPickerPanel?.classList.add('hidden');
    mcpPickerBtn?.setAttribute('aria-expanded', 'false');
  }
});

if (artifactRefreshBtn && artifactIframe) {
  artifactRefreshBtn.addEventListener('click', () => {
    if (currentArtifactCode) {
      injectIntoIframe(artifactIframe, currentArtifactCode, currentArtifactLang);
    }
  });
}

if (artifactCopyCodeBtn) {
  artifactCopyCodeBtn.addEventListener('click', async () => {
    if (currentArtifactCode) {
      try {
        await navigator.clipboard.writeText(currentArtifactCode);
        const span = artifactCopyCodeBtn.querySelector('span');
        if (span) span.textContent = 'Copied!';
        setTimeout(() => { if (span) span.textContent = 'Copy'; }, 2000);
      } catch (e) {
        console.error('Failed to copy artifact code:', e);
      }
    }
  });
}

if (artifactTabDesktop && artifactTabMobile && artifactViewportContainer) {
  artifactTabDesktop.addEventListener('click', () => {
    artifactTabDesktop.classList.add('active');
    artifactTabMobile.classList.remove('active');
    artifactViewportContainer.classList.remove('mobile-mode');
  });
  artifactTabMobile.addEventListener('click', () => {
    artifactTabMobile.classList.add('active');
    artifactTabDesktop.classList.remove('active');
    artifactViewportContainer.classList.add('mobile-mode');
  });
}

// ==========================================================================
// Code Card Transformation Engine (ChatGPT & Claude Code View + Preview)
// ==========================================================================
function enhanceCodeBlocks(container) {
  const preElements = container.querySelectorAll('pre');
  preElements.forEach((pre) => {
    const codeEl = pre.querySelector('code');
    if (!codeEl) return;

    const rawCode = codeEl.textContent;
    let lang = '';
    const classList = Array.from(codeEl.classList);
    for (const c of classList) {
      if (c.startsWith('language-')) {
        lang = c.replace('language-', '').toLowerCase();
        break;
      }
    }

    if (!lang) {
      if (rawCode.includes('<!DOCTYPE') || rawCode.includes('<html') || rawCode.includes('<div')) lang = 'html';
      else if (rawCode.includes('import ') || rawCode.includes('def ')) lang = 'python';
      else if (rawCode.includes('function ') || rawCode.includes('const ') || rawCode.includes('let ')) lang = 'javascript';
      else if (rawCode.trim().startsWith('<svg')) lang = 'svg';
      else lang = 'text';
    }

    const isPreviewable = ['html', 'svg', 'xml'].includes(lang) ||
      (rawCode.includes('<html') || rawCode.includes('<!DOCTYPE') || rawCode.includes('<svg') || (rawCode.includes('<div') && rawCode.includes('</')));

    let highlighted = rawCode;
    if (window.hljs) {
      try {
        if (lang && hljs.getLanguage(lang)) {
          highlighted = hljs.highlight(rawCode, { language: lang, ignoreIllegals: true }).value;
        } else {
          highlighted = hljs.highlightAuto(rawCode).value;
        }
      } catch (e) {
        highlighted = rawCode;
      }
    }

    const card = document.createElement('div');
    card.className = 'chat-code-card';

    card.innerHTML = `
      <div class="chat-code-header">
        <div class="code-header-left">
          <span class="code-lang-label">${lang}</span>
        </div>
        <div class="code-header-actions">
          ${isPreviewable ? `
            <div class="code-tab-pills">
              <button class="code-tab-btn active" data-tab="code">
                <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>
                <span>Code</span>
              </button>
              <button class="code-tab-btn" data-tab="preview">
                <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                <span>Preview</span>
              </button>
            </div>
            <button class="code-action-btn open-canvas-btn" title="Open in Canvas Drawer">
              <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 3 21 3 21 9"></polyline><polyline points="9 21 3 21 3 15"></polyline><line x1="21" y1="3" x2="14" y2="10"></line><line x1="3" y1="21" x2="10" y2="14"></line></svg>
              <span>Canvas</span>
            </button>
          ` : ''}
          <button class="code-action-btn copy-code-btn" title="Copy code">
            <svg class="copy-icon" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
            <span class="copy-text">Copy</span>
          </button>
        </div>
      </div>
      <div class="chat-code-body">
        <div class="code-pane-view">
          <pre><code class="hljs ${lang}">${highlighted}</code></pre>
        </div>
        ${isPreviewable ? `
          <div class="code-pane-preview hidden">
            <div class="inline-preview-toolbar">
              <span class="inline-preview-badge">Live Interactive Component</span>
              <button class="inline-refresh-btn" title="Reload Component">
                <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/></svg>
              </button>
            </div>
            <iframe class="inline-preview-frame" sandbox="allow-scripts allow-modals"></iframe>
          </div>
        ` : ''}
      </div>
    `;

    const copyBtn = card.querySelector('.copy-code-btn');
    if (copyBtn) {
      copyBtn.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText(rawCode);
          copyBtn.classList.add('copied');
          const lbl = copyBtn.querySelector('.copy-text');
          if (lbl) lbl.textContent = 'Copied!';
          setTimeout(() => {
            copyBtn.classList.remove('copied');
            if (lbl) lbl.textContent = 'Copy';
          }, 2000);
        } catch (e) {
          console.error('Failed to copy code:', e);
        }
      });
    }

    if (isPreviewable) {
      const codePane = card.querySelector('.code-pane-view');
      const previewPane = card.querySelector('.code-pane-preview');
      const inlineIframe = card.querySelector('.inline-preview-frame');
      const tabBtns = card.querySelectorAll('.code-tab-btn');
      const refreshBtn = card.querySelector('.inline-refresh-btn');
      const canvasBtn = card.querySelector('.open-canvas-btn');

      let iframeLoaded = false;
      function loadInlinePreview() {
        if (!iframeLoaded && inlineIframe) {
          injectIntoIframe(inlineIframe, rawCode, lang);
          iframeLoaded = true;
        }
      }

      tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
          tabBtns.forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          const tab = btn.getAttribute('data-tab');
          if (tab === 'preview') {
            codePane.classList.add('hidden');
            previewPane.classList.remove('hidden');
            loadInlinePreview();
          } else {
            codePane.classList.remove('hidden');
            previewPane.classList.add('hidden');
          }
        });
      });

      if (refreshBtn && inlineIframe) {
        refreshBtn.addEventListener('click', () => {
          injectIntoIframe(inlineIframe, rawCode, lang);
        });
      }

      if (canvasBtn) {
        canvasBtn.addEventListener('click', () => {
          openArtifactCanvas(rawCode, lang, `${lang.toUpperCase()} Component`);
        });
      }
    }

    pre.replaceWith(card);
  });
}

// ==========================================================================
// Assistant Message Action Bar & Micro-Interactions
// ==========================================================================
function wireMessageActions(row, cleanText) {
  const copyBtn = row.querySelector('.copy-msg-btn');
  if (copyBtn) {
    copyBtn.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(cleanText);
        const lbl = copyBtn.querySelector('.btn-lbl');
        if (lbl) lbl.textContent = 'Copied!';
        setTimeout(() => { if (lbl) lbl.textContent = 'Copy'; }, 2000);
      } catch (e) {
        console.error('Copy message failed:', e);
      }
    });
  }

  const speakBtn = row.querySelector('.speak-msg-btn');
  if (speakBtn) {
    speakBtn.addEventListener('click', async () => {
      const isSpeaking = speakBtn.classList.contains('speaking');
      if (isSpeaking) {
        try {
          await fetch(`${BACKEND_URL}/api/stop_speech`, { method: 'POST' });
        } catch (e) {}
        speakBtn.classList.remove('speaking');
        const lbl = speakBtn.querySelector('.btn-lbl');
        if (lbl) lbl.textContent = 'Listen';
      } else {
        document.querySelectorAll('.speak-msg-btn.speaking').forEach(b => {
          b.classList.remove('speaking');
          const l = b.querySelector('.btn-lbl');
          if (l) l.textContent = 'Listen';
        });
        speakBtn.classList.add('speaking');
        const lbl = speakBtn.querySelector('.btn-lbl');
        if (lbl) lbl.textContent = 'Speaking...';
        try {
          await fetch(`${BACKEND_URL}/api/speak`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: cleanText })
          });
        } catch (e) {
          console.error('Speak failed:', e);
        }
        setTimeout(() => {
          speakBtn.classList.remove('speaking');
          if (lbl) lbl.textContent = 'Listen';
        }, Math.max(4000, Math.min(cleanText.length * 60, 25000)));
      }
    });
  }

  const retryBtn = row.querySelector('.retry-msg-btn');
  if (retryBtn) {
    retryBtn.addEventListener('click', () => {
      if (lastUserPrompt) {
        sendPrompt(lastUserPrompt);
      }
    });
  }

  const likeBtn = row.querySelector('.like-btn');
  const dislikeBtn = row.querySelector('.dislike-btn');
  if (likeBtn) {
    likeBtn.addEventListener('click', () => {
      likeBtn.style.color = '#10b981';
      if (dislikeBtn) dislikeBtn.style.color = '';
      if (window.confetti) {
        confetti({ particleCount: 25, spread: 45, origin: { y: 0.85 } });
      }
    });
  }
  if (dislikeBtn) {
    dislikeBtn.addEventListener('click', () => {
      dislikeBtn.style.color = '#ef4444';
      if (likeBtn) likeBtn.style.color = '';
    });
  }
}

function appendUserMessage(text) {
  if (chatLayoutWrapper && chatLayoutWrapper.classList.contains('empty-state')) {
    chatLayoutWrapper.classList.remove('empty-state');
  }

  if (chatWelcomeBanner && chatWelcomeBanner.style.display !== 'none') {
    if (window.gsap) {
      gsap.to(chatWelcomeBanner, {
        opacity: 0,
        duration: 0.25,
        ease: "power2.inOut",
        onComplete: () => {
          chatWelcomeBanner.style.display = 'none';
          chatWelcomeBanner.style.opacity = '1';
        }
      });
    } else {
      chatWelcomeBanner.style.display = 'none';
    }
  }

  // Ensure dock is visible and reset in standard layout
  const dock = document.querySelector('.desktop-input-dock');
  if (dock && window.gsap) {
    gsap.set(dock, { opacity: 1, y: 0 });
  }

  const row = document.createElement('div');
  row.className = 'desktop-msg-row user';
  row.innerHTML = `<div class="user-capsule-message">${text}</div>`;
  desktopChatStream.appendChild(row);

  if (window.gsap) {
    gsap.fromTo(row, { opacity: 0, y: 12, scale: 0.98 }, { opacity: 1, y: 0, scale: 1, duration: 0.28, ease: "power2.out" });
  }

  scrollChatToBottom();
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, character => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  }[character]));
}

function appendAssistantMessage(content, toolCalls = [], progressEvents = [], elapsedSec = null, fleetSummary = null) {
  const cleanContent = sanitizeText(content);
  const row = document.createElement('div');
  row.className = 'desktop-msg-row assistant';

  let fleetCardHtml = '';
  if (fleetSummary && fleetSummary.agent_details && fleetSummary.agent_details.length > 0) {
    fleetCardHtml = `
      <div class="fleet-mission-card">
        <div class="fleet-card-header">
          <span> Multi-Agent Swarm (${fleetSummary.agents_deployed} Specialists Deployed)</span>
          <span>${fleetSummary.elapsed_seconds}s</span>
        </div>
        <div class="fleet-agents-list">
          ${fleetSummary.agent_details.map(a => `
            <div class="fleet-agent-pill completed">
              <span>[OK]</span>
              <span>${escapeHtml(a.role)}</span>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }

  let reasoningHtml = '';
  if ((toolCalls && toolCalls.length > 0) || progressEvents.length > 0) {
    const toolSvg = `<svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path></svg>`;
    const tagList = toolCalls.map(tc => `<span class="tool-tag">${toolSvg}<code>${escapeHtml(tc.tool)}</code></span>`).join(' ');
    const progressList = progressEvents.map((message, i) => `<li class="reasoning-step-item"><span class="step-num">${i + 1}</span><span class="step-desc">${escapeHtml(message)}</span></li>`).join('');
    const timeLabel = elapsedSec ? `${elapsedSec}s` : 'a few seconds';
    reasoningHtml = `
      <details class="reasoning-disclosure deepseek-disclosure">
        <summary class="reasoning-summary">
          <div class="reasoning-summary-left">
            <span class="reasoning-sparkle">*</span>
            <span class="reasoning-title">Thought for ${timeLabel}</span>
            <span class="reasoning-badge">${progressEvents.length + toolCalls.length} steps</span>
          </div>
          <svg class="reasoning-chevron" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
        </summary>
        <div class="reasoning-body">
          ${progressList ? `<ol class="progress-event-list">${progressList}</ol>` : ''}
          ${tagList ? `<div class="tool-execution-tags">${tagList}</div>` : ''}
        </div>
      </details>
    `;
  }

  const parsedHtml = (window.marked && typeof marked.parse === 'function')
    ? marked.parse(cleanContent)
    : cleanContent;

  row.innerHTML = `
    <div class="assistant-avatar-orb-wrap" title="DON OS">
      <video class="assistant-avatar-video" loop muted playsinline preload="none">
        <source src="orb_loop.webm" type="video/webm">
        <source src="orb_loop.mp4" type="video/mp4">
      </video>
    </div>
    <div class="assistant-content-column" style="flex: 1; max-width: 88%;">
      <div class="assistant-card-bubble">
        ${fleetCardHtml}
        ${reasoningHtml}
        <div class="markdown-body">${parsedHtml}</div>
      </div>
      <div class="assistant-msg-actions-bar">
        <div class="msg-actions-left">
          <button class="msg-action-btn copy-msg-btn" title="Copy response">
            <svg class="copy-svg" viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
            <span class="btn-lbl">Copy</span>
          </button>
          <button class="msg-action-btn speak-msg-btn" title="Read aloud">
            <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>
            <span class="btn-lbl">Listen</span>
          </button>
          <button class="msg-action-btn retry-msg-btn" title="Regenerate response">
            <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/></svg>
            <span class="btn-lbl">Retry</span>
          </button>
          <div class="msg-action-divider"></div>
          <button class="msg-action-btn icon-only like-btn" title="Good response">
            <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path></svg>
          </button>
          <button class="msg-action-btn icon-only dislike-btn" title="Poor response">
            <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h3a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-3"></path></svg>
          </button>
        </div>
        <div class="msg-actions-right">
          <span class="msg-stat-tag">DON OS Brain</span>
        </div>
      </div>
    </div>
  `;

  const markdownBody = row.querySelector('.markdown-body');
  if (markdownBody) {
    enhanceCodeBlocks(markdownBody);
  }

  wireMessageActions(row, cleanContent);

  desktopChatStream.appendChild(row);
  observeOrbVideos(row);

  if (window.gsap) {
    gsap.fromTo(row, { opacity: 0, y: 14, scale: 0.98 }, { opacity: 1, y: 0, scale: 1, duration: 0.32, ease: "power2.out" });
  }

  scrollChatToBottom();
}

function appendThinking() {
  const row = document.createElement('div');
  row.className = 'desktop-msg-row assistant thinking';
  row.innerHTML = `
    <div class="assistant-avatar-orb-wrap" title="DON OS">
      <video class="assistant-avatar-video" loop muted playsinline preload="none">
        <source src="orb_loop.webm" type="video/webm">
        <source src="orb_loop.mp4" type="video/mp4">
      </video>
    </div>
    <div class="thinking-bubble deepseek-thinking-bubble">
      <div class="thinking-status-row">
        <div class="thinking-pulse-ring"></div>
        <div class="thinking-header-left">
          <span class="thinking-title">Thinking Process</span>
          <span class="thinking-badge">DeepSeek Mode</span>
        </div>
        <span class="thinking-elapsed">0s</span>
      </div>
      <div class="thinking-active-step">
        <span class="thinking-sparkle">*</span>
        <span class="thinking-text">Analyzing your request...</span>
      </div>
      <ol class="thinking-activity-list" aria-live="polite"></ol>
    </div>
  `;
  desktopChatStream.appendChild(row);
  observeOrbVideos(row);

  if (window.gsap) {
    gsap.fromTo(row, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.25, ease: "power2.out" });
  }

  scrollChatToBottom();
  return row;
}

function scrollChatToBottom() {
  setTimeout(() => {
    desktopChatStream.scrollTop = desktopChatStream.scrollHeight;
  }, 40);
}

async function sendPrompt(
  promptText,
  {
    voiceMode = false,
    onProgress = null,
    mcpServers = Array.from(selectedMcpServers)
  } = {}
) {
  const text = promptText.trim();
  if (!text) return;

  lastUserPrompt = text;
  appendUserMessage(text);
  const thinkingNode = appendThinking();
  const progressEvents = [];
  let responseData = null;
  const requestStartedAt = performance.now();
  const elapsedLabel = thinkingNode.querySelector('.thinking-elapsed');
  const updateProgress = message => {
    if (progressEvents[progressEvents.length - 1] === message) return;

    progressEvents.push(message);
    const activityList = thinkingNode.querySelector('.thinking-activity-list');
    if (activityList) {
      const activity = document.createElement('li');
      activity.className = 'thinking-activity-item';
      activity.innerHTML = `<span class="step-num">${progressEvents.length}</span><span class="step-desc">${escapeHtml(message)}</span>`;
      activityList.appendChild(activity);
    }

    const status = thinkingNode.querySelector('.thinking-text');
    if (status) status.textContent = message;
    if (onProgress) onProgress(message);
    scrollChatToBottom();
  };
  const elapsedTimer = window.setInterval(() => {
    if (elapsedLabel) {
      const elapsedSeconds = Math.floor((performance.now() - requestStartedAt) / 1000);
      elapsedLabel.textContent = `${elapsedSeconds}s`;
    }
  }, 1000);

  setGeneratingState(true);
  const requestController = new AbortController();
  currentAbortController = requestController;
  updateProgress('Thinking: Initializing background processing pipeline...');

  try {
    const requestBody = JSON.stringify({
      prompt: text,
      speak: voiceEnabled && !voiceMode,
      session_id: currentSessionId,
      voice_mode: voiceMode,
      mcp_servers: mcpServers,
      model_id: activeModelSelect?.value || 'default'
    });
    const isFleetRequested = (typeof isFleetModeActive !== 'undefined' ? isFleetModeActive : true) || text.startsWith('/fleet') || text.startsWith('/swarm');
    const targetEndpoint = isFleetRequested
      ? `${BACKEND_URL}/api/fleet/stream`
      : `${BACKEND_URL}/api/chat/stream`;

    let res = await fetch(targetEndpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: requestBody,
      signal: requestController.signal
    });

    if (res.status === 404) {
      updateProgress('Waiting for the assistant to process your request...');
      res = await fetch(`${BACKEND_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: requestBody,
        signal: requestController.signal
      });
    }

    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.detail || `Request failed (${res.status} ${res.statusText}).`);
    }

    let data = null;
    if (res.headers.get('content-type')?.includes('application/x-ndjson')) {
      if (!res.body) throw new Error('The server did not provide a response stream.');

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      const handleEvent = line => {
        if (!line.trim()) return;
        const event = JSON.parse(line);
        if (event.type === 'status') {
          updateProgress(event.message);
        } else if (event.type === 'result') {
          data = event.data;
        } else if (event.type !== 'keepalive') {
          throw new Error(`Unexpected response event: ${event.type}`);
        }
      };

      while (true) {
        const { done, value } = await reader.read();
        buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
        const lines = buffer.split('\n');
        buffer = lines.pop();
        lines.forEach(handleEvent);
        if (done) break;
      }
      if (buffer.trim()) handleEvent(buffer);
    } else {
      data = await res.json();
    }
    if (!data) throw new Error('The response stream ended before the assistant returned a result.');
    responseData = data;

    const totalElapsedSec = Math.max(1, Math.round((performance.now() - requestStartedAt) / 1000));
    thinkingNode.remove();

    if (data.status === 'success') {
      appendAssistantMessage(data.response, data.tool_calls_executed, progressEvents, totalElapsedSec, data.fleet_summary);
      setTimeout(() => { if (typeof loadSessions === 'function') loadSessions(); }, 300);
    } else {
      appendAssistantMessage(`**Execution Error:** ${data.response || 'Could not process request.'}`, data.tool_calls_executed, progressEvents, totalElapsedSec, data.fleet_summary);
    }
  } catch (err) {
    const totalElapsedSec = Math.max(1, Math.round((performance.now() - requestStartedAt) / 1000));
    thinkingNode.remove();
    if (err.name === 'AbortError') {
      appendAssistantMessage(`*Generation stopped by Boss Munna.*`, [], progressEvents, totalElapsedSec);
    } else {
      appendAssistantMessage(`**Server Communication Error:** ${err.message}`, [], progressEvents, totalElapsedSec);
    }
  } finally {
    window.clearInterval(elapsedTimer);
    if (currentAbortController === requestController) {
      setGeneratingState(false);
      currentAbortController = null;
    }
  }

  scrollChatToBottom();
  return responseData;
}


// ==========================================================================
// 3. Google Assistant & Alexa Style Voice Engine (VAD + Silence Endpointing)
// ==========================================================================

let handsFreeActive = false;
let isVoiceEngineActive = false;
let audioContext = null;
let micMediaStream = null;
let mediaRecorder = null;
let audioAnalyser = null;
let vadLoopId = null;

let isRecordingUtterance = false;
let currentRecordedChunks = [];
let silenceTimerStart = null;
let speechTimerStart = null;
let isAssistantSpeaking = false;
let isVoiceTurnProcessing = false;
let voiceTurnId = 0;

// Voice Activity Detection (VAD) Tuning Parameters
const VAD_ENERGY_THRESHOLD = 0.032;   // Minimum microphone volume to trigger speech
const VAD_SILENCE_TIMEOUT_MS = 850;   // Silence duration before cutting recording (Google/Alexa endpoint)
const VAD_MIN_SPEECH_MS = 350;        // Minimum speech duration to discard accidental clicks/coughs

async function initVoiceAudio() {
  if (micMediaStream && audioContext) return true;

  try {
    micMediaStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true
      }
    });

    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const sourceNode = audioContext.createMediaStreamSource(micMediaStream);
    audioAnalyser = audioContext.createAnalyser();
    audioAnalyser.fftSize = 256;
    audioAnalyser.smoothingTimeConstant = 0.3;
    sourceNode.connect(audioAnalyser);

    return true;
  } catch (err) {
    console.error('[Voice Engine Error]: Microphone access failed:', err);
    alert('Microphone permission required for Google/Alexa voice recognition: ' + err.message);
    return false;
  }
}

function calculateMicVolume() {
  if (!audioAnalyser) return 0;
  const buffer = new Uint8Array(audioAnalyser.frequencyBinCount);
  audioAnalyser.getByteTimeDomainData(buffer);

  let sumSquares = 0;
  for (let i = 0; i < buffer.length; i++) {
    const normalized = (buffer[i] - 128) / 128;
    sumSquares += normalized * normalized;
  }
  return Math.sqrt(sumSquares / buffer.length);
}

function updateVisualizerBars(volume, isSpeaking) {
  if (!vbars || vbars.length === 0) return;

  const baseHeight = isSpeaking ? Math.min(22, Math.max(6, volume * 140)) : 6;
  vbars.forEach((bar, idx) => {
    const jitter = isSpeaking ? (Math.sin(Date.now() * 0.015 + idx) * 4) : 0;
    const h = Math.max(5, Math.min(24, baseHeight + jitter));
    bar.style.height = `${h}px`;
  });
}

function setVoiceStateUI(state, customText) {
  if (!voiceStatusCapsule) return;

  voiceStatusCapsule.classList.remove('hidden', 'listening', 'hearing', 'thinking');
  if (voiceWaveBars) voiceWaveBars.classList.remove('active');

  if (state === 'hidden') {
    voiceStatusCapsule.classList.add('hidden');
    return;
  }

  if (state === 'listening') {
    voiceStatusCapsule.classList.add('listening');
    voiceStatusText.textContent = customText || 'Listening for Boss Munna...';
  } else if (state === 'hearing') {
    voiceStatusCapsule.classList.add('hearing');
    if (voiceWaveBars) voiceWaveBars.classList.add('active');
    voiceStatusText.textContent = customText || 'Hearing Boss Munna...';
  } else if (state === 'thinking') {
    voiceStatusCapsule.classList.add('thinking');
    voiceStatusText.textContent = customText || 'Transcribing speech with Whisper...';
  }
}

function startVADLoop() {
  if (vadLoopId) cancelAnimationFrame(vadLoopId);

  function checkVAD() {
    if (!isVoiceEngineActive) return;

    // Acoustic Echo Protection: Do NOT record while assistant is speaking or processing speech
    if (isAssistantSpeaking || isVoiceTurnProcessing) {
      if (isRecordingUtterance) {
        isRecordingUtterance = false;
        currentRecordedChunks = [];
        if (mediaRecorder && mediaRecorder.state === 'recording') {
          try { mediaRecorder.stop(); } catch (e) {}
        }
      }
      updateVisualizerBars(0, false);
      vadLoopId = requestAnimationFrame(checkVAD);
      return;
    }

    const volume = calculateMicVolume();
    const now = Date.now();

    // 2. User Speaking Detection
    if (volume > VAD_ENERGY_THRESHOLD) {
      silenceTimerStart = null;

      if (!isRecordingUtterance) {
        // Begin recording utterance
        isRecordingUtterance = true;
        speechTimerStart = now;
        currentRecordedChunks = [];

        try {
          mediaRecorder = new MediaRecorder(micMediaStream, {
            mimeType: MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
              ? 'audio/webm;codecs=opus'
              : 'audio/webm'
          });

          mediaRecorder.ondataavailable = (e) => {
            if (e.data && e.data.size > 0) currentRecordedChunks.push(e.data);
          };

          mediaRecorder.onstop = handleUtteranceRecorded;
          mediaRecorder.start(100);
        } catch (e) {
          console.error('[MediaRecorder start error]:', e);
        }

        setVoiceStateUI('hearing', 'Hearing Boss Munna...');
      }

      updateVisualizerBars(volume, true);
    } else {
      // 3. User Silence Detection (Endpointing)
      if (isRecordingUtterance) {
        if (!silenceTimerStart) {
          silenceTimerStart = now;
        } else if (now - silenceTimerStart > VAD_SILENCE_TIMEOUT_MS) {
          // Silence duration threshold met -> Endpoint reached!
          const speechDuration = now - (speechTimerStart || now);
          silenceTimerStart = null;
          isRecordingUtterance = false;

          if (speechDuration >= VAD_MIN_SPEECH_MS && mediaRecorder && mediaRecorder.state === 'recording') {
            setVoiceStateUI('thinking', 'Transcribing speech with Whisper...');
            mediaRecorder.stop();
          } else {
            // Discard too short noises
            if (mediaRecorder && mediaRecorder.state === 'recording') {
              mediaRecorder.stop();
            }
            setVoiceStateUI('listening', 'Listening for Boss Munna...');
          }
        }
      }

      updateVisualizerBars(0, false);
    }

    vadLoopId = requestAnimationFrame(checkVAD);
  }

  vadLoopId = requestAnimationFrame(checkVAD);
}

async function handleUtteranceRecorded() {
  if (!isVoiceEngineActive) return;
  if (isVoiceTurnProcessing) return;

  if (currentRecordedChunks.length === 0) {
    if (handsFreeActive) setVoiceStateUI('listening', 'Listening for Boss Munna...');
    else stopVoiceEngine();
    return;
  }

  const audioBlob = new Blob(currentRecordedChunks, { type: 'audio/webm' });
  currentRecordedChunks = [];
  isVoiceTurnProcessing = true;
  const currentTurnId = ++voiceTurnId;

  try {
    const formData = new FormData();
    formData.append('file', audioBlob, 'speech.webm');

    const res = await fetch(`${BACKEND_URL}/api/transcribe`, {
      method: 'POST',
      body: formData
    });

    if (res.ok) {
      const data = await res.json();
      const transcribedText = (data.text || '').trim();

      if (transcribedText) {
        console.log(`[Google/Alexa ASR]: "${transcribedText}"`);
        setVoiceStateUI('thinking', `Recognized: "${transcribedText}"`);

        const response = await sendPrompt(transcribedText, {
          voiceMode: handsFreeActive,
          onProgress: message => {
            if (handsFreeActive && isVoiceEngineActive) setVoiceStateUI('thinking', message);
          }
        });

        if (!handsFreeActive || !isVoiceEngineActive || currentTurnId !== voiceTurnId) {
          isVoiceTurnProcessing = false;
          if (!handsFreeActive || !isVoiceEngineActive) stopVoiceEngine();
        } else if (voiceEnabled && response?.status === 'success' && response.response) {
          setVoiceStateUI('thinking', 'Starting your spoken response...');
          const speechResponse = await fetch(`${BACKEND_URL}/api/speak`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: response.response })
          });
          if (!speechResponse.ok) {
            throw new Error(`Speech playback could not start (${speechResponse.status}).`);
          }

          if (!handsFreeActive || !isVoiceEngineActive || currentTurnId !== voiceTurnId) {
            fetch(`${BACKEND_URL}/api/stop_speech`, { method: 'POST' }).catch(error => {
              console.warn('Could not stop speech playback:', error);
            });
            isVoiceTurnProcessing = false;
            return;
          }

          isAssistantSpeaking = true;
          isVoiceTurnProcessing = true;
          setVoiceStateUI('thinking', 'Speaking your response...');
          await waitForSpeechCompletion(response.response, currentTurnId);
          await delay(700);
          if (currentTurnId === voiceTurnId) {
            isAssistantSpeaking = false;
            isVoiceTurnProcessing = false;
          }
        } else {
          isVoiceTurnProcessing = false;
        }

        if (currentTurnId === voiceTurnId && handsFreeActive && isVoiceEngineActive) {
          isAssistantSpeaking = false;
          isVoiceTurnProcessing = false;
          setVoiceStateUI('listening', 'Listening for you...');
        } else if (!handsFreeActive || !isVoiceEngineActive) {
          stopVoiceEngine();
        }
      } else {
        if (handsFreeActive) setVoiceStateUI('listening', 'Listening for Boss Munna...');
        else stopVoiceEngine();
      }
    } else {
      if (handsFreeActive) setVoiceStateUI('listening', 'Listening for Boss Munna...');
      else stopVoiceEngine();
    }
  } catch (err) {
    console.error('[Voice Turn Error]:', err);
    if (handsFreeActive) setVoiceStateUI('listening', 'Listening for Boss Munna...');
    else stopVoiceEngine();
  } finally {
    if (currentTurnId === voiceTurnId) {
      isVoiceTurnProcessing = false;
      isAssistantSpeaking = false;
    }
  }
}

function delay(ms) {
  return new Promise(resolve => window.setTimeout(resolve, ms));
}

function stopHandsFreeSession() {
  const hadPendingVoiceTurn = isVoiceTurnProcessing;
  handsFreeActive = false;
  voiceTurnId += 1;
  isVoiceTurnProcessing = false;
  isAssistantSpeaking = false;

  if (hadPendingVoiceTurn && currentAbortController) {
    currentAbortController.abort();
  }

  fetch(`${BACKEND_URL}/api/stop_speech`, { method: 'POST' }).catch(error => {
    console.warn('Could not stop speech playback:', error);
  });
  stopVoiceEngine();
}

async function waitForSpeechCompletion(responseText, turnId) {
  const startedAt = Date.now();
  const estimatedDuration = Math.max(
    1200,
    (responseText.trim().split(/\s+/).length / 2.7) * 1000
  );
  let useEstimate = false;

  while (
    handsFreeActive &&
    isVoiceEngineActive &&
    isAssistantSpeaking &&
    turnId === voiceTurnId
  ) {
    try {
      const response = await fetch(`${BACKEND_URL}/api/speech/status`);
      if (response.status === 404) {
        useEstimate = true;
        break;
      }
      if (!response.ok) throw new Error(`Speech status request failed (${response.status}).`);

      const statusData = await response.json();
      const isSpeaking = statusData.speaking || statusData.cooldown;
      if (!isSpeaking && Date.now() - startedAt >= 900) return;
    } catch (error) {
      console.warn('Could not check speech playback status; estimating completion time:', error);
      useEstimate = true;
      break;
    }

    await delay(250);
  }

  if (useEstimate) {
    while (
      Date.now() - startedAt < estimatedDuration &&
      handsFreeActive &&
      isVoiceEngineActive &&
      isAssistantSpeaking &&
      turnId === voiceTurnId
    ) {
      await delay(250);
    }
  }
}

async function startVoiceEngine() {
  const ready = await initVoiceAudio();
  if (!ready) return;

  if (audioContext && audioContext.state === 'suspended') {
    await audioContext.resume();
  }

  isVoiceEngineActive = true;
  desktopMicBtn.classList.add('recording');
  setVoiceStateUI('listening', 'Listening for Boss Munna...');
  startVADLoop();
}

function stopVoiceEngine() {
  isVoiceEngineActive = false;
  isRecordingUtterance = false;

  if (vadLoopId) {
    cancelAnimationFrame(vadLoopId);
    vadLoopId = null;
  }

  if (mediaRecorder && mediaRecorder.state === 'recording') {
    try { mediaRecorder.stop(); } catch (e) {}
  }

  if (desktopMicBtn) desktopMicBtn.classList.remove('recording');
  setVoiceStateUI('hidden');
}


// ==========================================================================
// 4. Global Button Controls
// ==========================================================================

// 1-Touch Mic Button
if (desktopMicBtn) {
  desktopMicBtn.addEventListener('click', () => {
    if (isVoiceEngineActive) {
      stopVoiceEngine();
    } else {
      startVoiceEngine();
    }
  });
}

// Hands-Free Mode Toggle (Continuous Alexa/Google Assistant conversation)
if (handsFreeBtn) {
  handsFreeBtn.addEventListener('click', () => {
    handsFreeActive = !handsFreeActive;
    handsFreeBtn.classList.toggle('active', handsFreeActive);
    if (handsFreeLabel) {
      handsFreeLabel.textContent = handsFreeActive ? 'Hands-Free: ON' : 'Hands-Free';
    }

    if (handsFreeActive) {
      startVoiceEngine();
    } else {
      stopHandsFreeSession();
    }
  });
}

// Cancel Voice Capsule Button
if (cancelVoiceBtn) {
  cancelVoiceBtn.addEventListener('click', () => {
    stopHandsFreeSession();
    if (handsFreeBtn) handsFreeBtn.classList.remove('active');
    if (handsFreeLabel) handsFreeLabel.textContent = 'Hands-Free';
    stopVoiceEngine();
  });
}

// Voice audio playback toggle
voiceToggleBtn.addEventListener('click', () => {
  voiceEnabled = !voiceEnabled;
  voiceToggleBtn.classList.toggle('active', voiceEnabled);
  if (voiceIconOn && voiceIconOff) {
    voiceIconOn.classList.toggle('hidden', !voiceEnabled);
    voiceIconOff.classList.toggle('hidden', voiceEnabled);
  }
  voiceLabel.textContent = voiceEnabled ? 'Voice Audio' : 'Voice Muted';
});

// Clear chat
clearChatBtn.addEventListener('click', async () => {
  try {
    await fetch(`${BACKEND_URL}/api/clear`, { method: 'POST' });
    desktopChatStream.innerHTML = '';
    if (chatLayoutWrapper) chatLayoutWrapper.classList.add('empty-state');
    if (chatWelcomeBanner) {
      chatWelcomeBanner.style.display = 'flex';
      chatWelcomeBanner.style.opacity = '1';
      chatWelcomeBanner.style.height = '';
      chatWelcomeBanner.style.marginBottom = '';
      chatWelcomeBanner.style.paddingTop = '';
      chatWelcomeBanner.style.paddingBottom = '';
      playDonOsIntro();
    }
  } catch (e) {
    console.error('Error clearing conversation:', e);
  }
});

// Initialize ambient motion canvas
initAmbientCanvas();

// ==========================================================================
// Motion Graphics Controller for "DON OS"
// ==========================================================================
function playDonOsIntro() {
  if (!window.gsap) return;
  const orbWrap = document.getElementById('heroOrbVideoWrap');
  const chars = document.querySelectorAll('.don-char');
  const sub = document.getElementById('donOsMotionSub');
  const dock = document.querySelector('.desktop-input-dock');

  // Cancel any running animations to avoid overlaps
  gsap.killTweensOf([orbWrap, chars, sub, dock]);

  // Initial cinematic staging: floating 3D orb with bounce, 3D tilted characters with blur
  if (orbWrap) gsap.set(orbWrap, { scale: 0.6, opacity: 0, y: -24 });
  if (chars.length > 0) gsap.set(chars, { opacity: 0, y: 38, scale: 0.72, filter: 'blur(14px)', rotateX: -35 });
  if (sub) gsap.set(sub, { opacity: 0, y: 16, filter: 'blur(8px)' });
  if (dock) gsap.set(dock, { opacity: 0, y: 22 });

  const tl = gsap.timeline();

  if (orbWrap) {
    tl.to(orbWrap, {
      scale: 1,
      opacity: 1,
      y: 0,
      duration: 0.85,
      ease: 'elastic.out(1, 0.75)'
    });
  }

  if (chars.length > 0) {
    tl.to(chars, {
      opacity: 1,
      y: 0,
      scale: 1,
      filter: 'blur(0px)',
      rotateX: 0,
      duration: 0.8,
      stagger: 0.065,
      ease: 'back.out(2.2)'
    }, orbWrap ? '-=0.5' : 0);
  }

  if (sub) {
    tl.to(sub, {
      opacity: 1,
      y: 0,
      filter: 'blur(0px)',
      duration: 0.65,
      ease: 'power2.out'
    }, '-=0.35');
  }

  if (dock) {
    tl.to(dock, {
      opacity: 1,
      y: 0,
      duration: 0.55,
      ease: 'power2.out'
    }, '-=0.4');
  }
}

// Only decode animations that are actually on screen.
observeOrbVideos();

// ==========================================================================
// 4. Claude & ChatGPT Style Sidebar & Agent Feature Suite Controller
// ==========================================================================
let currentSessionId = localStorage.getItem('don_os_session_id') || ('session_' + Date.now());
localStorage.setItem('don_os_session_id', currentSessionId);

const desktopSidebar = document.getElementById('desktopSidebar');
const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');
const sidebarCollapseBtn = document.getElementById('sidebarCollapseBtn');
const newChatBtn = document.getElementById('newChatBtn');

const sidebarNavTabs = document.querySelectorAll('.sidebar-nav-tab');
const sidebarPanels = document.querySelectorAll('.sidebar-panel');

const sidebarChatsList = document.getElementById('sidebarChatsList');
const sidebarMemoriesList = document.getElementById('sidebarMemoriesList');
const sidebarNotesList = document.getElementById('sidebarNotesList');
const sidebarRemindersList = document.getElementById('sidebarRemindersList');
const sidebarMcpList = document.getElementById('sidebarMcpList');

const addMemoryBtn = document.getElementById('addMemoryBtn');
const addNoteBtn = document.getElementById('addNoteBtn');
const addReminderBtn = document.getElementById('addReminderBtn');

const brightnessSlider = document.getElementById('brightnessSlider');
const brightnessValBadge = document.getElementById('brightnessValBadge');
const volumeSlider = document.getElementById('volumeSlider');
const volumeValBadge = document.getElementById('volumeValBadge');
const lockScreenBtn = document.getElementById('lockScreenBtn');
const hwBatteryStatus = document.getElementById('hwBatteryStatus');
const hwCpuStatus = document.getElementById('hwCpuStatus');

const voiceSelectDropdown = document.getElementById('voiceSelectDropdown');
const speechRateSlider = document.getElementById('speechRateSlider');
const speechRateBadge = document.getElementById('speechRateBadge');
const testVoiceBtn = document.getElementById('testVoiceBtn');

const editorModal = document.getElementById('editorModal');
const editorModalTitle = document.getElementById('editorModalTitle');
const editorModalBody = document.getElementById('editorModalBody');
const editorModalCloseBtn = document.getElementById('editorModalCloseBtn');
const editorModalCancelBtn = document.getElementById('editorModalCancelBtn');
const editorModalSaveBtn = document.getElementById('editorModalSaveBtn');

// --------------------------------------------------------------------------
// Sidebar Toggle & Hotkeys
// --------------------------------------------------------------------------
function toggleSidebar(e) {
  if (e) {
    e.preventDefault();
    e.stopPropagation();
  }
  const sidebar = document.getElementById('desktopSidebar');
  if (!sidebar) {
    console.error('[DON OS]: desktopSidebar element not found in DOM!');
    return;
  }
  const isCollapsed = sidebar.classList.toggle('collapsed');
  localStorage.setItem('don_os_sidebar_collapsed', isCollapsed ? 'true' : 'false');
  console.log('[DON OS]: Sidebar toggled -> isCollapsed:', isCollapsed);

  const toggleBtn = document.getElementById('sidebarToggleBtn');
  if (toggleBtn) {
    toggleBtn.classList.toggle('active', !isCollapsed);
    toggleBtn.setAttribute('title', isCollapsed ? 'Expand Sidebar (Ctrl+B)' : 'Collapse Sidebar (Ctrl+B)');
  }
}

if (sidebarToggleBtn) {
  sidebarToggleBtn.addEventListener('click', toggleSidebar);
}
if (sidebarCollapseBtn) {
  sidebarCollapseBtn.addEventListener('click', toggleSidebar);
}

// Global click delegate for any sidebar toggle trigger
document.addEventListener('click', (e) => {
  const btn = e.target.closest('#sidebarToggleBtn, #sidebarCollapseBtn');
  if (btn) {
    toggleSidebar(e);
  }
});

// Always ensure the sidebar is visible and expanded on boot
const sidebar = document.getElementById('desktopSidebar');
if (sidebar) {
  sidebar.classList.remove('collapsed');
}
localStorage.setItem('don_os_sidebar_collapsed', 'false');
if (sidebarToggleBtn) {
  sidebarToggleBtn.classList.add('active');
  sidebarToggleBtn.setAttribute('title', 'Collapse Sidebar (Ctrl+B)');
}

window.addEventListener('keydown', (e) => {
  if ((e.ctrlKey || e.metaKey) && (e.key === 'b' || e.key === 'B')) {
    e.preventDefault();
    toggleSidebar(e);
  }
  if ((e.ctrlKey || e.metaKey) && (e.key === 'n' || e.key === 'N')) {
    e.preventDefault();
    startNewChat();
  }
});

// --------------------------------------------------------------------------
// Feature Cards Deck & Detail Navigation Controller
// --------------------------------------------------------------------------
const sidebarCardsHub = document.getElementById('sidebarCardsHub');
const sidebarFeatureDetail = document.getElementById('sidebarFeatureDetail');
const featureDetailBackBtn = document.getElementById('featureDetailBackBtn');
const featureDetailTitle = document.getElementById('featureDetailTitle');

const featurePanelsMap = {
  codeReview: document.getElementById('panelCodeReview'),
  hardware: document.getElementById('panelHardware'),
  memories: document.getElementById('panelMemories'),
  notes: document.getElementById('panelNotes'),
  reminders: document.getElementById('panelReminders'),
  voice: document.getElementById('panelVoice'),
  chats: document.getElementById('panelChats'),
  mcp: document.getElementById('panelMcp'),
  models: document.getElementById('panelModels')
};

const featureTitlesMap = {
  codeReview: 'Code Review & Diff Studio',
  hardware: 'Workstation Hardware',
  memories: 'Memory & Knowledge',
  notes: 'Saved Notes',
  reminders: 'Reminders & Alarms',
  voice: 'Voice Studio',
  chats: 'Conversations History',
  mcp: 'MCP Creative Toolchains',
  models: 'AI Models'
};

function openFeaturePanel(featureId) {
  if (!sidebarCardsHub || !sidebarFeatureDetail) return;

  // Hide all panels
  Object.values(featurePanelsMap).forEach(p => {
    if (p) p.classList.add('hidden');
  });

  const activePanel = featurePanelsMap[featureId];
  if (!activePanel) return;

  activePanel.classList.remove('hidden');
  sidebarCardsHub.classList.add('hidden');
  sidebarFeatureDetail.classList.remove('hidden');

  if (featureDetailTitle) {
    featureDetailTitle.textContent = featureTitlesMap[featureId] || 'Feature Details';
  }

  // Reload fresh data for active panel
  if (featureId === 'hardware') loadHardwareStatus();
  if (featureId === 'memories') loadMemories();
  if (featureId === 'notes') loadNotes();
  if (featureId === 'reminders') loadReminders();
  if (featureId === 'voice') loadVoiceConfig();
  if (featureId === 'chats') loadSessions();
  if (featureId === 'models') {
    loadModels();
    loadLocalModelCatalog();
  }
}

function closeFeaturePanel() {
  if (!sidebarCardsHub || !sidebarFeatureDetail) return;
  sidebarFeatureDetail.classList.add('hidden');
  sidebarCardsHub.classList.remove('hidden');
}

document.querySelectorAll('.feature-hub-card').forEach(card => {
  card.addEventListener('click', () => {
    const fId = card.getAttribute('data-feature');
    if (fId) openFeaturePanel(fId);
  });
});

if (featureDetailBackBtn) {
  featureDetailBackBtn.addEventListener('click', closeFeaturePanel);
}

function showModelPanelMessage(message, isError = false) {
  if (!modelPanelMessage) return;
  modelPanelMessage.textContent = message;
  modelPanelMessage.classList.toggle('error', isError);
  modelPanelMessage.classList.remove('hidden');
}

function showLocalModelMessage(message, isError = false) {
  if (!localModelMessage) return;
  localModelMessage.textContent = message;
  localModelMessage.classList.toggle('error', isError);
  localModelMessage.classList.remove('hidden');
}

async function modelRequest(path, options = {}, timeoutMs = 0) {
  let timeoutId;
  const requestOptions = { ...options };
  if (timeoutMs) {
    const controller = new AbortController();
    timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);
    requestOptions.signal = controller.signal;
  }
  let response;
  try {
    response = await fetch(`${BACKEND_URL}${path}`, requestOptions);
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('The request took too long. Check that DON OS is running, then try again.');
    }
    throw error;
  } finally {
    if (timeoutId) window.clearTimeout(timeoutId);
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || `Model request failed (${response.status}).`);
  return data;
}

function renderLocalModelCatalog() {
  if (!localModelCatalogList) return;
  localModelCatalogList.replaceChildren();
  if (!localModelCatalog.length) {
    localModelCatalogList.textContent = 'No local models are available right now.';
    return;
  }
  localModelCatalog.forEach(model => {
    const item = document.createElement('article');
    item.className = 'local-model-item';
    const details = document.createElement('div');
    details.className = 'local-model-item-details';
    const name = document.createElement('h4');
    name.textContent = model.name;
    const summary = document.createElement('p');
    summary.textContent = model.description;
    const specs = document.createElement('span');
    specs.textContent = `${model.parameters} parameters · ${model.download_gb} GB download · about ${model.required_disk_gb} GB free storage · up to ${model.memory_gb} GB memory`;
    const source = document.createElement('span');
    source.className = 'local-model-hardware';
    source.textContent = 'Hugging Face model · installs on this computer';
    details.append(name, summary, specs, source);

    const action = document.createElement('button');
    action.className = 'model-row-action local-model-download-action';
    action.type = 'button';
    action.textContent = model.installed
      ? 'Use model'
      : `Install & use · ${model.download_gb} GB`;
    action.disabled = Boolean(localModelDownloadJobId);
    action.addEventListener('click', () => downloadCatalogModel(model, action));
    item.append(details, action);
    localModelCatalogList.appendChild(item);
  });
}

async function loadLocalModelCatalog() {
  reloadLocalModelCatalogBtn.disabled = true;
  localModelCatalogList.replaceChildren();
  const loading = document.createElement('p');
  loading.className = 'local-model-hardware';
  loading.textContent = 'Loading local models…';
  localModelCatalogList.appendChild(loading);
  try {
    const data = await modelRequest('/api/models/local/catalog', {}, 3000);
    localModelCatalog = data.models || [];
    const runtime = localModelCatalog[0];
    if (localModelRuntimeStatus && runtime) {
      localModelRuntimeStatus.textContent = runtime.runtime_running
        ? 'Local runtime is ready.'
        : runtime.runtime_installed
          ? 'Local runtime is installed; DON OS will start it when you use a model.'
          : 'DON OS will install the local runtime when you choose a model.';
    }
    renderLocalModelCatalog();
    showLocalModelMessage('Choose a model to install the local runtime, download the model, and select it for your chats.');
  } catch (error) {
    localModelCatalog = [];
    localModelCatalogList.replaceChildren();
    if (localModelRuntimeStatus) {
      localModelRuntimeStatus.textContent = 'Could not check the local runtime. Refresh the list or restart DON OS.';
    }
    const failure = document.createElement('p');
    failure.className = 'local-model-hardware';
    failure.textContent = 'Could not load the local model list.';
    localModelCatalogList.appendChild(failure);
    showLocalModelMessage(error.message, true);
  } finally {
    reloadLocalModelCatalogBtn.disabled = false;
  }
}

function finishLocalModelDownloadPolling() {
  if (localModelDownloadPollTimer) window.clearInterval(localModelDownloadPollTimer);
  localModelDownloadPollTimer = null;
  localModelDownloadJobId = null;
  cancelLocalModelDownloadBtn.hidden = true;
  renderLocalModelCatalog();
}

async function pollLocalModelDownload() {
  if (!localModelDownloadJobId || localModelPollBusy) return;
  localModelPollBusy = true;
  try {
    const job = await modelRequest(`/api/models/local/download/${encodeURIComponent(localModelDownloadJobId)}`);
    localModelProgressMessage.textContent = job.message || 'Setting up your local model…';
    localModelProgressValue.textContent = job.progress_label || `${job.progress || 0}%`;
    localModelProgressBar.value = job.progress || 0;
    if (job.status === 'completed') {
      finishLocalModelDownloadPolling();
      await loadModels();
      localModelCatalog = localModelCatalog.map(model => model.id === job.catalog_id ? { ...model, installed: true } : model);
      renderLocalModelCatalog();
      showLocalModelMessage(`${job.connected_model?.name || 'Your model'} is downloaded, connected, and selected for your chats.`);
    } else if (job.status === 'failed' || job.status === 'cancelled') {
      finishLocalModelDownloadPolling();
      showLocalModelMessage(job.error || job.message || 'The download stopped. You can try again.', job.status === 'failed');
    }
  } catch (error) {
    finishLocalModelDownloadPolling();
    showLocalModelMessage(error.message, true);
  } finally {
    localModelPollBusy = false;
  }
}

async function downloadCatalogModel(model, action) {
  action.disabled = true;
  showLocalModelMessage('');
  try {
    const started = await modelRequest('/api/models/local/download', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ catalog_id: model.id })
    });
    localModelProgress.classList.remove('hidden');
    cancelLocalModelDownloadBtn.hidden = true;
    localModelProgressMessage.textContent = started.message || 'Preparing the local runtime and model…';
    localModelProgressValue.textContent = started.progress_label || `${started.progress || 0}%`;
    localModelProgressBar.value = started.progress || 0;
    if (started.status === 'completed') {
      await loadModels();
      localModelCatalog = localModelCatalog.map(item => item.id === model.id ? { ...item, installed: true } : item);
      renderLocalModelCatalog();
      showLocalModelMessage(`${started.connected_model?.name || 'Your model'} is already downloaded, connected, and selected for your chats.`);
      return;
    }
    localModelDownloadJobId = started.job_id;
    cancelLocalModelDownloadBtn.hidden = false;
    renderLocalModelCatalog();
    localModelDownloadPollTimer = window.setInterval(pollLocalModelDownload, 1000);
    pollLocalModelDownload();
  } catch (error) {
    action.disabled = false;
    showLocalModelMessage(error.message, true);
  }
}

if (reloadLocalModelCatalogBtn) {
  reloadLocalModelCatalogBtn.addEventListener('click', loadLocalModelCatalog);
}

if (cancelLocalModelDownloadBtn) {
  cancelLocalModelDownloadBtn.addEventListener('click', async () => {
    if (!localModelDownloadJobId) return;
    cancelLocalModelDownloadBtn.disabled = true;
    try {
      await modelRequest(`/api/models/local/download/${encodeURIComponent(localModelDownloadJobId)}`, { method: 'DELETE' });
      finishLocalModelDownloadPolling();
      showLocalModelMessage('Download stopped. You can start it again whenever you are ready.');
    } catch (error) {
      showLocalModelMessage(error.message, true);
    } finally {
      cancelLocalModelDownloadBtn.disabled = false;
    }
  });
}

function renderModelList(models, activeId) {
  if (!modelList) return;
  modelList.replaceChildren();
  models.forEach(model => {
    const row = document.createElement('article');
    row.className = 'model-list-row';
    const copy = document.createElement('div');
    copy.className = 'model-list-copy';
    const title = document.createElement('strong');
    title.textContent = model.name;
    const detail = document.createElement('span');
    detail.textContent = model.provider === 'gemini'
      ? (model.available ? 'Gemini · automatic fallback' : 'Add GEMINI_API_KEY to enable')
      : `${model.provider === 'ollama' ? 'Local Ollama' : 'Hosted API'} · ${model.model}`;
    copy.append(title, detail);

    const actions = document.createElement('div');
    actions.className = 'model-list-actions';
    if (model.id !== 'default') {
      const test = document.createElement('button');
      test.type = 'button';
      test.className = 'model-row-action';
      test.textContent = 'Test';
      test.addEventListener('click', async () => {
        test.disabled = true;
        test.textContent = 'Testing…';
        try {
          await modelRequest(`/api/models/${encodeURIComponent(model.id)}/test`, { method: 'POST' });
          showModelPanelMessage(`${model.name} connected successfully.`);
        } catch (error) {
          showModelPanelMessage(error.message, true);
        } finally {
          test.disabled = false;
          test.textContent = 'Test';
        }
      });
      actions.appendChild(test);

      const remove = document.createElement('button');
      remove.type = 'button';
      remove.className = 'model-row-action remove';
      remove.textContent = 'Remove';
      remove.addEventListener('click', async () => {
        remove.disabled = true;
        try {
          await modelRequest(`/api/models/${encodeURIComponent(model.id)}`, { method: 'DELETE' });
          await loadModels();
          showModelPanelMessage(`${model.name} removed.`);
        } catch (error) {
          remove.disabled = false;
          showModelPanelMessage(error.message, true);
        }
      });
      actions.appendChild(remove);
    }

    const selected = document.createElement('span');
    selected.className = 'model-active-badge';
    selected.textContent = activeId === model.id ? 'Active' : '';
    row.append(copy, actions, selected);
    modelList.appendChild(row);
  });
}

async function loadModels() {
  try {
    const data = await modelRequest('/api/models');
    const { models, active_model_id: activeId } = data;
    if (activeModelSelect) {
      activeModelSelect.replaceChildren();
      models.forEach(model => {
        const option = document.createElement('option');
        option.value = model.id;
        option.textContent = model.id === 'default'
          ? 'Gemini · automatic fallback'
          : `${model.name} · ${model.model}`;
        option.disabled = model.id === 'default' && !model.available;
        activeModelSelect.appendChild(option);
      });
      activeModelSelect.value = activeId;
    }
    renderModelList(models, activeId);
  } catch (error) {
    showModelPanelMessage(error.message, true);
  }
}

if (activeModelSelect) {
  activeModelSelect.addEventListener('change', async () => {
    activeModelSelect.disabled = true;
    try {
      await modelRequest('/api/models/active', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_id: activeModelSelect.value })
      });
      await loadModels();
    } catch (error) {
      showModelPanelMessage(error.message, true);
      await loadModels();
    } finally {
      activeModelSelect.disabled = false;
    }
  });
}

if (manageModelsBtn) {
  manageModelsBtn.addEventListener('click', () => openFeaturePanel('models'));
}

if (modelProvider) {
  modelProvider.addEventListener('change', () => {
    const isOllama = modelProvider.value === 'ollama';
    modelEndpoint.value = isOllama ? 'http://127.0.0.1:11434/v1' : 'https://api.openai.com/v1';
    modelApiKey.required = !isOllama;
    modelApiKeyField.classList.toggle('hidden', isOllama);
    modelProviderHint.textContent = isOllama
      ? 'Start Ollama locally and enter the exact model name shown by `ollama list`.'
      : 'Use the provider’s OpenAI-compatible API endpoint and model ID.';
  });
}

if (modelConnectorForm) {
  modelConnectorForm.addEventListener('submit', async event => {
    event.preventDefault();
    const submit = modelConnectorForm.querySelector('[type="submit"]');
    submit.disabled = true;
    try {
      await modelRequest('/api/models', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: document.getElementById('modelDisplayName').value,
          provider: modelProvider.value,
          model: document.getElementById('modelIdentifier').value,
          base_url: modelEndpoint.value,
          api_key: modelApiKey.value || null
        })
      });
      modelConnectorForm.reset();
      modelApiKey.value = '';
      modelProvider.dispatchEvent(new Event('change'));
      await loadModels();
      showModelPanelMessage('Model added. Select it in the chat composer, then test the connection.');
    } catch (error) {
      showModelPanelMessage(error.message, true);
    } finally {
      submit.disabled = false;
    }
  });
}

loadModels();

// --------------------------------------------------------------------------
// Primary Action: New Chat (ChatGPT & Claude Style)
// --------------------------------------------------------------------------
function startNewChat() {
  currentSessionId = 'session_' + Date.now();
  localStorage.setItem('don_os_session_id', currentSessionId);
  desktopChatStream.innerHTML = '';
  if (chatLayoutWrapper) chatLayoutWrapper.classList.add('empty-state');
  if (chatWelcomeBanner) {
    chatWelcomeBanner.style.display = 'flex';
    chatWelcomeBanner.style.opacity = '1';
    chatWelcomeBanner.style.height = '';
    chatWelcomeBanner.style.marginBottom = '';
    chatWelcomeBanner.style.paddingTop = '';
    chatWelcomeBanner.style.paddingBottom = '';
    playDonOsIntro();
  }
  desktopPromptInput.value = '';
  desktopPromptInput.focus();
  loadSessions();
  // Return to cards view if in a detail panel
  closeFeaturePanel();
}

if (newChatBtn) newChatBtn.addEventListener('click', startNewChat);

// --------------------------------------------------------------------------
// Chat Sessions: Load, Switch, Rename, Delete
// --------------------------------------------------------------------------
async function loadSessions() {
  if (!sidebarChatsList) return;
  try {
    const res = await fetch(`${BACKEND_URL}/api/sessions`);
    const data = await res.json();
    const sessions = data.sessions || [];
    sidebarChatsList.innerHTML = '';

    const chatCountBadge = document.getElementById('chatCountBadge');
    if (chatCountBadge) chatCountBadge.textContent = sessions.length;
    const cardChatBadge = document.getElementById('cardChatBadge');
    if (cardChatBadge) cardChatBadge.textContent = `${sessions.length} Chats`;

    if (sessions.length === 0) {
      sidebarChatsList.innerHTML = `<div style="font-size: 11.5px; color: var(--text-muted); padding: 8px 4px;">No previous conversations.</div>`;
      return;
    }

    sessions.forEach(sess => {
      const item = document.createElement('div');
      item.className = 'chat-session-item' + (sess.id === currentSessionId ? ' active' : '');
      item.innerHTML = `
        <span class="chat-item-title" title="${sess.title}">${sess.title}</span>
        <div class="chat-item-actions">
          <button class="chat-item-action-btn rename" title="Rename Chat">
            <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
          </button>
          <button class="chat-item-action-btn delete" title="Delete Chat">
            <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
          </button>
        </div>
      `;

      item.addEventListener('click', (e) => {
        if (e.target.closest('.chat-item-action-btn')) return;
        switchToSession(sess.id);
      });

      const renameBtn = item.querySelector('.chat-item-action-btn.rename');
      const titleSpan = item.querySelector('.chat-item-title');
      if (renameBtn && titleSpan) {
        renameBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          const input = document.createElement('input');
          input.type = 'text';
          input.className = 'chat-item-rename-input';
          input.value = sess.title;
          titleSpan.replaceWith(input);
          input.focus();
          input.select();

          const saveRename = async () => {
            const newTitle = input.value.trim() || sess.title;
            try {
              await fetch(`${BACKEND_URL}/api/sessions/rename`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: sess.id, title: newTitle })
              });
            } catch (err) {}
            loadSessions();
          };

          input.addEventListener('keydown', (ev) => {
            if (ev.key === 'Enter') saveRename();
            if (ev.key === 'Escape') loadSessions();
          });
          input.addEventListener('blur', saveRename);
        });
      }

      const deleteBtn = item.querySelector('.chat-item-action-btn.delete');
      if (deleteBtn) {
        deleteBtn.addEventListener('click', async (e) => {
          e.stopPropagation();
          try {
            await fetch(`${BACKEND_URL}/api/sessions/${sess.id}`, { method: 'DELETE' });
            if (currentSessionId === sess.id) {
              startNewChat();
            } else {
              loadSessions();
            }
          } catch (err) {
            console.error('Delete chat error:', err);
          }
        });
      }

      sidebarChatsList.appendChild(item);
    });
  } catch (e) {
    console.error('Error loading sessions:', e);
  }
}

async function switchToSession(sessionId) {
  currentSessionId = sessionId;
  localStorage.setItem('don_os_session_id', currentSessionId);
  desktopChatStream.innerHTML = '';
  if (chatWelcomeBanner) chatWelcomeBanner.style.display = 'none';

  try {
    const res = await fetch(`${BACKEND_URL}/api/sessions/${sessionId}/messages`);
    const data = await res.json();
    const messages = data.messages || [];

    if (messages.length === 0) {
      if (chatLayoutWrapper) chatLayoutWrapper.classList.add('empty-state');
      if (chatWelcomeBanner) {
        chatWelcomeBanner.style.display = 'flex';
        chatWelcomeBanner.style.opacity = '1';
        chatWelcomeBanner.style.height = '';
        chatWelcomeBanner.style.marginBottom = '';
        chatWelcomeBanner.style.paddingTop = '';
        chatWelcomeBanner.style.paddingBottom = '';
        playDonOsIntro();
      }
    } else {
      if (chatLayoutWrapper) chatLayoutWrapper.classList.remove('empty-state');
      if (chatWelcomeBanner) chatWelcomeBanner.style.display = 'none';
      messages.forEach(msg => {
        if (msg.role === 'user') {
          appendUserMessage(msg.content);
        } else {
          appendAssistantMessage(msg.content);
        }
      });
    }
  } catch (e) {
    console.error('Error switching session:', e);
  }
  loadSessions();
}

// --------------------------------------------------------------------------
// Universal Item Editor Modal
// --------------------------------------------------------------------------
let activeModalSaveHandler = null;

function openEditorModal(title, htmlFields, onSave) {
  if (!editorModal) return;
  editorModalTitle.textContent = title;
  editorModalBody.innerHTML = htmlFields;
  activeModalSaveHandler = onSave;
  editorModal.classList.add('active');
}

function closeEditorModal() {
  if (!editorModal) return;
  editorModal.classList.remove('active');
  activeModalSaveHandler = null;
}

if (editorModalCloseBtn) editorModalCloseBtn.addEventListener('click', closeEditorModal);
if (editorModalCancelBtn) editorModalCancelBtn.addEventListener('click', closeEditorModal);
if (editorModalSaveBtn) {
  editorModalSaveBtn.addEventListener('click', async () => {
    if (typeof activeModalSaveHandler === 'function') {
      const ok = await activeModalSaveHandler();
      if (ok !== false) closeEditorModal();
    }
  });
}

// --------------------------------------------------------------------------
// Editable Knowledge Base (Memories)
// --------------------------------------------------------------------------
async function loadMemories() {
  if (!sidebarMemoriesList) return;
  try {
    const res = await fetch(`${BACKEND_URL}/api/memories/raw`);
    const data = await res.json();
    const memories = data.memories || [];
    sidebarMemoriesList.innerHTML = '';

    const memCountBadge = document.getElementById('memCountBadge');
    if (memCountBadge) memCountBadge.textContent = memories.length;
    const cardMemBadge = document.getElementById('cardMemBadge');
    if (cardMemBadge) cardMemBadge.textContent = `${memories.length} Facts`;

    if (memories.length === 0) {
      sidebarMemoriesList.innerHTML = `<div style="font-size: 11.5px; color: var(--text-muted); padding: 8px 4px;">No stored memories yet. Click + Add to store a fact.</div>`;
      return;
    }

    memories.forEach(mem => {
      const card = document.createElement('div');
      card.className = 'sidebar-entity-card';
      card.innerHTML = `
        <div class="entity-card-header">
          <span class="entity-key-badge">${mem.key}</span>
          <div class="entity-card-actions">
            <button class="entity-btn edit">Edit</button>
            <button class="entity-btn delete">Delete</button>
          </div>
        </div>
        <div class="entity-card-body">${mem.information}</div>
        <div class="entity-category-tag">Category: ${mem.category || 'general'}</div>
      `;

      card.querySelector('.entity-btn.edit').addEventListener('click', () => {
        openEditorModal('Edit Memory', `
          <div class="editor-form-group">
            <label>Memory Key (Identifier)</label>
            <input type="text" id="editMemKey" class="editor-input" value="${mem.key}">
          </div>
          <div class="editor-form-group">
            <label>Category</label>
            <input type="text" id="editMemCat" class="editor-input" value="${mem.category || 'general'}">
          </div>
          <div class="editor-form-group">
            <label>Information / Fact / Preference</label>
            <textarea id="editMemInfo" class="editor-textarea">${mem.information}</textarea>
          </div>
        `, async () => {
          const key = document.getElementById('editMemKey').value.trim();
          const category = document.getElementById('editMemCat').value.trim() || 'general';
          const information = document.getElementById('editMemInfo').value.trim();
          if (!key || !information) return false;
          await fetch(`${BACKEND_URL}/api/memories/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ key, information, category })
          });
          loadMemories();
        });
      });

      card.querySelector('.entity-btn.delete').addEventListener('click', async () => {
        await fetch(`${BACKEND_URL}/api/memories/delete`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ key: mem.key })
        });
        loadMemories();
      });

      sidebarMemoriesList.appendChild(card);
    });
  } catch (e) {
    console.error('Error loading memories:', e);
  }
}

if (addMemoryBtn) {
  addMemoryBtn.addEventListener('click', () => {
    openEditorModal('Add New Memory', `
      <div class="editor-form-group">
        <label>Memory Key (Identifier)</label>
        <input type="text" id="newMemKey" class="editor-input" placeholder="e.g. favorite_browser">
      </div>
      <div class="editor-form-group">
        <label>Category</label>
        <input type="text" id="newMemCat" class="editor-input" value="preference">
      </div>
      <div class="editor-form-group">
        <label>Information / Fact</label>
        <textarea id="newMemInfo" class="editor-textarea" placeholder="Detail for DON OS to remember..."></textarea>
      </div>
    `, async () => {
      const key = document.getElementById('newMemKey').value.trim();
      const category = document.getElementById('newMemCat').value.trim() || 'general';
      const information = document.getElementById('newMemInfo').value.trim();
      if (!key || !information) return false;
      await fetch(`${BACKEND_URL}/api/memories/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key, information, category })
      });
      loadMemories();
    });
  });
}

// --------------------------------------------------------------------------
// Editable Rich Notes
// --------------------------------------------------------------------------
async function loadNotes() {
  if (!sidebarNotesList) return;
  try {
    const res = await fetch(`${BACKEND_URL}/api/notes/raw`);
    const data = await res.json();
    const notes = data.notes || [];
    sidebarNotesList.innerHTML = '';

    const noteCountBadge = document.getElementById('noteCountBadge');
    if (noteCountBadge) noteCountBadge.textContent = notes.length;
    const cardNoteBadge = document.getElementById('cardNoteBadge');
    if (cardNoteBadge) cardNoteBadge.textContent = `${notes.length} Notes`;

    if (notes.length === 0) {
      sidebarNotesList.innerHTML = `<div style="font-size: 11.5px; color: var(--text-muted); padding: 8px 4px;">No saved notes. Click + New to create one.</div>`;
      return;
    }

    notes.forEach(note => {
      const card = document.createElement('div');
      card.className = 'sidebar-entity-card';
      card.innerHTML = `
        <div class="entity-card-header">
          <span class="entity-key-badge">${note.title}</span>
          <div class="entity-card-actions">
            <button class="entity-btn edit">Edit</button>
            <button class="entity-btn delete">Delete</button>
          </div>
        </div>
        <div class="entity-card-body">${note.content}</div>
        <div class="entity-category-tag">Tags: ${note.tags || 'general'}</div>
      `;

      card.querySelector('.entity-btn.edit').addEventListener('click', () => {
        openEditorModal('Edit Note', `
          <div class="editor-form-group">
            <label>Title</label>
            <input type="text" id="editNoteTitle" class="editor-input" value="${note.title}">
          </div>
          <div class="editor-form-group">
            <label>Tags</label>
            <input type="text" id="editNoteTags" class="editor-input" value="${note.tags || ''}">
          </div>
          <div class="editor-form-group">
            <label>Content</label>
            <textarea id="editNoteContent" class="editor-textarea" style="min-height: 120px;">${note.content}</textarea>
          </div>
        `, async () => {
          const title = document.getElementById('editNoteTitle').value.trim();
          const tags = document.getElementById('editNoteTags').value.trim();
          const content = document.getElementById('editNoteContent').value.trim();
          if (!title || !content) return false;
          await fetch(`${BACKEND_URL}/api/notes/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, content, tags })
          });
          loadNotes();
        });
      });

      card.querySelector('.entity-btn.delete').addEventListener('click', async () => {
        await fetch(`${BACKEND_URL}/api/notes/delete`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title: note.title })
        });
        loadNotes();
      });

      sidebarNotesList.appendChild(card);
    });
  } catch (e) {
    console.error('Error loading notes:', e);
  }
}

if (addNoteBtn) {
  addNoteBtn.addEventListener('click', () => {
    openEditorModal('Create New Note', `
      <div class="editor-form-group">
        <label>Title</label>
        <input type="text" id="newNoteTitle" class="editor-input" placeholder="e.g. Project Roadmap">
      </div>
      <div class="editor-form-group">
        <label>Tags</label>
        <input type="text" id="newNoteTags" class="editor-input" placeholder="e.g. dev, tasks, ai">
      </div>
      <div class="editor-form-group">
        <label>Content</label>
        <textarea id="newNoteContent" class="editor-textarea" style="min-height: 120px;" placeholder="Write your note or markdown snippet..."></textarea>
      </div>
    `, async () => {
      const title = document.getElementById('newNoteTitle').value.trim();
      const tags = document.getElementById('newNoteTags').value.trim();
      const content = document.getElementById('newNoteContent').value.trim();
      if (!title || !content) return false;
      await fetch(`${BACKEND_URL}/api/notes/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content, tags })
      });
      loadNotes();
    });
  });
}

// --------------------------------------------------------------------------
// Editable Reminders & Alarms
// --------------------------------------------------------------------------
async function loadReminders() {
  if (!sidebarRemindersList) return;
  try {
    const res = await fetch(`${BACKEND_URL}/api/reminders/raw`);
    const data = await res.json();
    const reminders = data.reminders || [];
    sidebarRemindersList.innerHTML = '';

    const remCountBadge = document.getElementById('remCountBadge');
    if (remCountBadge) remCountBadge.textContent = reminders.length;
    const cardRemBadge = document.getElementById('cardRemBadge');
    if (cardRemBadge) cardRemBadge.textContent = `${reminders.length} Active`;

    if (reminders.length === 0) {
      sidebarRemindersList.innerHTML = `<div style="font-size: 11.5px; color: var(--text-muted); padding: 8px 4px;">No active alarms or reminders.</div>`;
      return;
    }

    reminders.forEach(rem => {
      const card = document.createElement('div');
      card.className = 'sidebar-entity-card';
      card.innerHTML = `
        <div class="entity-card-header">
          <span class="entity-key-badge">Due: ${rem.due_time}</span>
          <div class="entity-card-actions">
            <button class="entity-btn delete">Cancel</button>
          </div>
        </div>
        <div class="entity-card-body">${rem.message}</div>
        <div class="entity-category-tag">Status: ${rem.status}</div>
      `;

      card.querySelector('.entity-btn.delete').addEventListener('click', async () => {
        await fetch(`${BACKEND_URL}/api/reminders/delete`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id: rem.id })
        });
        loadReminders();
      });

      sidebarRemindersList.appendChild(card);
    });
  } catch (e) {
    console.error('Error loading reminders:', e);
  }
}

if (addReminderBtn) {
  addReminderBtn.addEventListener('click', () => {
    openEditorModal('Add Scheduled Reminder', `
      <div class="editor-form-group">
        <label>Time / Delay Specification</label>
        <input type="text" id="newRemTime" class="editor-input" placeholder="e.g. in 20 minutes, tomorrow at 9am">
      </div>
      <div class="editor-form-group">
        <label>Reminder Message</label>
        <textarea id="newRemMsg" class="editor-textarea" placeholder="e.g. Push git branch, drink water..."></textarea>
      </div>
    `, async () => {
      const time_spec = document.getElementById('newRemTime').value.trim();
      const message = document.getElementById('newRemMsg').value.trim();
      if (!time_spec || !message) return false;
      await fetch(`${BACKEND_URL}/api/reminders/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ time_spec, message })
      });
      loadReminders();
    });
  });
}

// --------------------------------------------------------------------------
// Hardware Sliders & Controls (Brightness, Volume, Telemetry)
// --------------------------------------------------------------------------
async function loadHardwareStatus() {
  try {
    const res = await fetch(`${BACKEND_URL}/api/hardware/status`);
    const data = await res.json();
    if (brightnessSlider && data.brightness !== undefined) {
      brightnessSlider.value = data.brightness;
      if (brightnessValBadge) brightnessValBadge.textContent = `${data.brightness}%`;
    }
    if (volumeSlider && data.volume !== undefined) {
      volumeSlider.value = data.volume;
      if (volumeValBadge) volumeValBadge.textContent = `${data.volume}%`;
    }
    if (hwBatteryStatus && data.battery) {
      hwBatteryStatus.textContent = data.battery.split('\n')[0].replace('• Battery Status: ', '');
    }
    if (hwCpuStatus && data.cpu) {
      hwCpuStatus.textContent = 'Active';
    }
    const cardHwBadge = document.getElementById('cardHwBadge');
    if (cardHwBadge) {
      const b = (brightnessSlider ? brightnessSlider.value : (data.brightness || 100));
      cardHwBadge.textContent = `Bri ${b}%`;
    }
  } catch (e) {}
}

function updateHwCardBadge() {
  const cardHwBadge = document.getElementById('cardHwBadge');
  if (cardHwBadge && brightnessSlider) {
    cardHwBadge.textContent = `Bri ${brightnessSlider.value}%`;
  }
}

if (brightnessSlider) {
  brightnessSlider.addEventListener('input', () => {
    const val = brightnessSlider.value;
    if (brightnessValBadge) brightnessValBadge.textContent = `${val}%`;
    updateHwCardBadge();
  });
  brightnessSlider.addEventListener('change', async () => {
    const val = parseInt(brightnessSlider.value, 10);
    try {
      await fetch(`${BACKEND_URL}/api/hardware/brightness`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ percentage: val })
      });
    } catch (e) {}
  });
}

if (volumeSlider) {
  volumeSlider.addEventListener('input', () => {
    const val = volumeSlider.value;
    if (volumeValBadge) volumeValBadge.textContent = `${val}%`;
  });
  volumeSlider.addEventListener('change', async () => {
    const val = parseInt(volumeSlider.value, 10);
    try {
      await fetch(`${BACKEND_URL}/api/hardware/volume`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ percentage: val })
      });
    } catch (e) {}
  });
}

if (lockScreenBtn) {
  lockScreenBtn.addEventListener('click', async () => {
    try {
      await fetch(`${BACKEND_URL}/api/lock`, { method: 'POST' });
    } catch (e) {}
  });
}

// --------------------------------------------------------------------------
// Voice Profile & Speech Settings
// --------------------------------------------------------------------------
async function loadVoiceConfig() {
  try {
    const res = await fetch(`${BACKEND_URL}/api/voice/config`);
    const data = await res.json();
    if (voiceSelectDropdown && data.voice) {
      voiceSelectDropdown.value = data.voice;
    }
    if (speechRateSlider && data.rate) {
      const num = parseInt(data.rate.replace('%', ''), 10) || 0;
      speechRateSlider.value = num;
      if (speechRateBadge) speechRateBadge.textContent = (num >= 0 ? `+${num}%` : `${num}%`);
    }
    const cardVoiceBadge = document.getElementById('cardVoiceBadge');
    if (cardVoiceBadge && voiceSelectDropdown) {
      const opt = voiceSelectDropdown.options[voiceSelectDropdown.selectedIndex];
      const name = opt ? opt.text.split(' ')[0] : 'Ava';
      cardVoiceBadge.textContent = `${name} (25y)`;
    }
  } catch (e) {}
}

if (voiceSelectDropdown) {
  voiceSelectDropdown.addEventListener('change', async () => {
    const voice = voiceSelectDropdown.value;
    const rate = (parseInt(speechRateSlider.value, 10) >= 0 ? `+${speechRateSlider.value}%` : `${speechRateSlider.value}%`);
    const cardVoiceBadge = document.getElementById('cardVoiceBadge');
    if (cardVoiceBadge) {
      const opt = voiceSelectDropdown.options[voiceSelectDropdown.selectedIndex];
      const name = opt ? opt.text.split(' ')[0] : 'Ava';
      cardVoiceBadge.textContent = `${name} (25y)`;
    }
    await fetch(`${BACKEND_URL}/api/voice/config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ voice, rate })
    });
  });
}

if (speechRateSlider) {
  speechRateSlider.addEventListener('input', () => {
    const num = parseInt(speechRateSlider.value, 10);
    if (speechRateBadge) speechRateBadge.textContent = (num >= 0 ? `+${num}%` : `${num}%`);
  });
  speechRateSlider.addEventListener('change', async () => {
    const voice = voiceSelectDropdown.value;
    const rate = (parseInt(speechRateSlider.value, 10) >= 0 ? `+${speechRateSlider.value}%` : `${speechRateSlider.value}%`);
    await fetch(`${BACKEND_URL}/api/voice/config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ voice, rate })
    });
  });
}

if (testVoiceBtn) {
  testVoiceBtn.addEventListener('click', async () => {
    await fetch(`${BACKEND_URL}/api/speak`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: "Hello Boss Munna, my speech synthesis engine is calibrated and running at peak performance." })
    });
  });
}

// --------------------------------------------------------------------------
// MCP Creative Suites List
// --------------------------------------------------------------------------
async function loadMcpSuites() {
  if (!sidebarMcpList) return;
  try {
    const res = await fetch(`${BACKEND_URL}/api/acp/servers`);
    const data = await res.json();
    const servers = data.servers || {};
    const serverNames = Object.keys(servers);
    sidebarMcpList.innerHTML = '';

    const suites = serverNames.length > 0 ? serverNames : [
      'Blender 3D Modeling', 'Figma UX/UI', 'Adobe Photoshop', 'Adobe Illustrator',
      'AutoCAD Drafting', 'Premiere Pro Editing', 'After Effects Motion', 'Ableton Audio Synth',
      'Lightroom RAW', 'Acrobat PDF Tool', 'MS Word DOCX', 'MS Excel Analytics',
      'PowerPoint Decks', 'Chrome DevTools', 'Firebase Cloud', 'Flutter Interop', 'Science Engine'
    ];

    suites.forEach(name => {
      const chip = document.createElement('div');
      chip.className = 'mcp-chip';
      chip.innerHTML = `
        <span class="mcp-chip-name">${name}</span>
        <span class="mcp-chip-status">Connected</span>
      `;
      sidebarMcpList.appendChild(chip);
    });
  } catch (e) {
    console.error('Error loading MCP servers:', e);
  }
}

// --------------------------------------------------------------------------
// Initial Boot Sync for All Unified Sidebar Sections
// --------------------------------------------------------------------------
loadSessions();
loadHardwareStatus();
loadMemories();
loadNotes();
loadReminders();
loadVoiceConfig();
loadMcpSuites();

// ==============================================================================
// 10. Professional Code Review & Git Diff Studio
// ==============================================================================

let crCurrentSelectedFile = null;
let crSplitMode = false;

const crFilesList = document.getElementById('crFilesList');
const crChangedCountBadge = document.getElementById('crChangedCountBadge');
const crDiffContainer = document.getElementById('crDiffContainer');
const crCurrentDiffFileName = document.getElementById('crCurrentDiffFileName');
const crDiffStatsBadge = document.getElementById('crDiffStatsBadge');
const crRefreshBtn = document.getElementById('crRefreshBtn');
const crAnalyzeAiBtn = document.getElementById('crAnalyzeAiBtn');
const crTabDiffBtn = document.getElementById('crTabDiffBtn');
const crTabAuditBtn = document.getElementById('crTabAuditBtn');
const crTabTestsBtn = document.getElementById('crTabTestsBtn');
const crDiffViewSection = document.getElementById('crDiffViewSection');
const crAuditSection = document.getElementById('crAuditSection');
const crTestsSection = document.getElementById('crTestsSection');
const crAuditFindingsList = document.getElementById('crAuditFindingsList');
const crAuditStatusBadge = document.getElementById('crAuditStatusBadge');
const crRunPytestBtn = document.getElementById('crRunPytestBtn');
const crTestsOutput = document.getElementById('crTestsOutput');
const crToggleSideBySideBtn = document.getElementById('crToggleSideBySideBtn');

async function loadReviewStatus() {
  if (!crFilesList) return;
  try {
    const res = await fetch(`${API_BASE}/api/review/status`);
    const data = await res.json();
    if (data.files) {
      if (crChangedCountBadge) crChangedCountBadge.textContent = `${data.count} changed`;
      crFilesList.innerHTML = '';
      if (data.files.length === 0) {
        crFilesList.innerHTML = '<div style="color:#94a3b8; font-size:11px; padding:6px;">Working tree clean. No uncommitted diffs.</div>';
        return;
      }

      data.files.forEach(f => {
        const item = document.createElement('div');
        item.className = `cr-file-item ${crCurrentSelectedFile === f.path ? 'active' : ''}`;
        const tagClass = f.status.includes('M') ? 'mod' : (f.status.includes('?') ? 'untracked' : 'added');
        item.innerHTML = `
          <span class="cr-file-status-badge ${tagClass}">${f.status}</span>
          <span class="cr-file-path" title="${f.path}">${f.path}</span>
        `;
        item.onclick = () => {
          crCurrentSelectedFile = f.path;
          document.querySelectorAll('.cr-file-item').forEach(el => el.classList.remove('active'));
          item.classList.add('active');
          loadReviewDiff(f.path);
        };
        crFilesList.appendChild(item);
      });

      // Auto-select first file if none selected
      if (!crCurrentSelectedFile && data.files.length > 0) {
        crCurrentSelectedFile = data.files[0].path;
        const first = crFilesList.querySelector('.cr-file-item');
        if (first) first.classList.add('active');
        loadReviewDiff(crCurrentSelectedFile);
      }
    }
  } catch (err) {
    console.error('Error loading review status:', err);
  }
}

async function loadReviewDiff(filepath) {
  if (!crDiffContainer) return;
  crDiffContainer.innerHTML = '<div class="cr-empty-placeholder">Computing git diff...</div>';
  try {
    const res = await fetch(`${API_BASE}/api/review/diff`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filepath })
    });
    const data = await res.json();
    if (crCurrentDiffFileName) crCurrentDiffFileName.textContent = filepath.split('/').pop();
    if (crDiffStatsBadge) crDiffStatsBadge.textContent = `+${data.additions} / -${data.deletions}`;

    if (!data.diff) {
      crDiffContainer.innerHTML = '<div class="cr-empty-placeholder">No diff changes detected for this file.</div>';
      return;
    }

    renderDiffLines(data.diff);
  } catch (err) {
    crDiffContainer.innerHTML = `<div class="cr-empty-placeholder" style="color:#ef4444;">Error fetching diff: ${err.message}</div>`;
  }
}

function renderDiffLines(diffText) {
  const lines = diffText.split('\n');
  crDiffContainer.innerHTML = '';
  
  let oldLine = 0;
  let newLine = 0;

  lines.forEach(line => {
    const row = document.createElement('div');
    row.className = 'cr-diff-row';

    if (line.startsWith('@@')) {
      row.classList.add('chunk-header');
      row.innerHTML = `<span class="cr-line-gutter">...</span><span class="cr-line-code">${escapeHtml(line)}</span>`;
      const match = line.match(/@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@/);
      if (match) {
        oldLine = parseInt(match[1], 10);
        newLine = parseInt(match[2], 10);
      }
    } else if (line.startsWith('+') && !line.startsWith('+++')) {
      row.classList.add('addition');
      row.innerHTML = `<span class="cr-line-gutter">+${newLine}</span><span class="cr-line-code">${escapeHtml(line.substring(1))}</span>`;
      newLine++;
    } else if (line.startsWith('-') && !line.startsWith('---')) {
      row.classList.add('deletion');
      row.innerHTML = `<span class="cr-line-gutter">-${oldLine}</span><span class="cr-line-code">${escapeHtml(line.substring(1))}</span>`;
      oldLine++;
    } else if (line.startsWith('diff --git') || line.startsWith('index ') || line.startsWith('---') || line.startsWith('+++')) {
      row.classList.add('meta-header');
      row.innerHTML = `<span class="cr-line-gutter">#</span><span class="cr-line-code">${escapeHtml(line)}</span>`;
    } else {
      row.classList.add('context');
      row.innerHTML = `<span class="cr-line-gutter">${newLine || ''}</span><span class="cr-line-code">${escapeHtml(line.startsWith(' ') ? line.substring(1) : line)}</span>`;
      if (oldLine) oldLine++;
      if (newLine) newLine++;
    }
    crDiffContainer.appendChild(row);
  });
}

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

async function runAiReview() {
  if (!crAuditFindingsList) return;
  switchReviewTab('audit');
  if (crAuditStatusBadge) {
    crAuditStatusBadge.textContent = 'Auditing...';
    crAuditStatusBadge.className = 'cr-audit-badge running';
  }
  crAuditFindingsList.innerHTML = '<div class="cr-empty-placeholder">Running AI Senior Engineer Review on changed files...</div>';

  try {
    const res = await fetch(`${API_BASE}/api/review/audit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filepath: crCurrentSelectedFile })
    });
    const data = await res.json();
    if (crAuditStatusBadge) {
      crAuditStatusBadge.textContent = 'Completed';
      crAuditStatusBadge.className = 'cr-audit-badge ready';
    }

    crAuditFindingsList.innerHTML = '';

    // Summary Card
    const summaryCard = document.createElement('div');
    summaryCard.className = 'cr-finding-card summary';
    summaryCard.innerHTML = `
      <div class="cr-finding-header">
        <span class="cr-sev-pill info">AI Review Summary</span>
      </div>
      <div class="cr-finding-body">${marked ? marked.parse(data.ai_review || '') : escapeHtml(data.ai_review || '')}</div>
    `;
    crAuditFindingsList.appendChild(summaryCard);

    // Findings
    if (data.findings && data.findings.length > 0) {
      data.findings.forEach(f => {
        const card = document.createElement('div');
        card.className = `cr-finding-card ${f.severity}`;
        card.innerHTML = `
          <div class="cr-finding-header">
            <span class="cr-sev-pill ${f.severity}">${f.severity.toUpperCase()}</span>
            <strong>${f.title}</strong>
          </div>
          <div class="cr-finding-desc">${f.description}</div>
          <div class="cr-finding-suggestion"> <em>Recommendation:</em> ${f.suggestion}</div>
        `;
        crAuditFindingsList.appendChild(card);
      });
    }
  } catch (err) {
    if (crAuditStatusBadge) {
      crAuditStatusBadge.textContent = 'Error';
      crAuditStatusBadge.className = 'cr-audit-badge error';
    }
    crAuditFindingsList.innerHTML = `<div class="cr-empty-placeholder" style="color:#ef4444;">Audit failed: ${err.message}</div>`;
  }
}

async function runTestSuite() {
  if (!crTestsOutput) return;
  crTestsOutput.textContent = '$ pytest --color=no -q\nRunning test suites across all project modules...';
  try {
    const res = await fetch(`${API_BASE}/api/review/test`, { method: 'POST' });
    const data = await res.json();
    crTestsOutput.textContent = `$ pytest output (Exit Code: ${data.exit_code}):\n\n` + data.output;
  } catch (err) {
    crTestsOutput.textContent = `Test runner error: ${err.message}`;
  }
}

function switchReviewTab(tab) {
  if (crTabDiffBtn) crTabDiffBtn.classList.toggle('active', tab === 'diff');
  if (crTabAuditBtn) crTabAuditBtn.classList.toggle('active', tab === 'audit');
  if (crTabTestsBtn) crTabTestsBtn.classList.toggle('active', tab === 'tests');

  if (crDiffViewSection) crDiffViewSection.classList.toggle('hidden', tab !== 'diff');
  if (crAuditSection) crAuditSection.classList.toggle('hidden', tab !== 'audit');
  if (crTestsSection) crTestsSection.classList.toggle('hidden', tab !== 'tests');
}

// Event Listeners for Code Review Studio
if (crTabDiffBtn) crTabDiffBtn.addEventListener('click', () => switchReviewTab('diff'));
if (crTabAuditBtn) crTabAuditBtn.addEventListener('click', () => switchReviewTab('audit'));
if (crTabTestsBtn) crTabTestsBtn.addEventListener('click', () => switchReviewTab('tests'));
if (crRefreshBtn) crRefreshBtn.addEventListener('click', loadReviewStatus);
if (crAnalyzeAiBtn) crAnalyzeAiBtn.addEventListener('click', runAiReview);
if (crRunPytestBtn) crRunPytestBtn.addEventListener('click', runTestSuite);

if (crToggleSideBySideBtn) {
  crToggleSideBySideBtn.addEventListener('click', () => {
    crSplitMode = !crSplitMode;
    crToggleSideBySideBtn.textContent = crSplitMode ? 'Split' : 'Unified';
    crToggleSideBySideBtn.classList.toggle('active', crSplitMode);
    if (crDiffContainer) crDiffContainer.classList.toggle('split-view', crSplitMode);
  });
}

// Initial Boot Sync for Code Review
loadReviewStatus();

// Trigger the cinematic DON OS motion graphics intro on initial boot
if (chatLayoutWrapper && chatLayoutWrapper.classList.contains('empty-state')) {
  setTimeout(() => {
    playDonOsIntro();
  }, 100);
}
