import os
import re

builder_path = '/home/mullainathan/projects/nilambur-teak-wood/clean_aiswarya_builder.py'
with open(builder_path, 'r', encoding='utf-8') as f:
    content = f.read()

css_start = "      /* Ambient Architectural Telemetry Watermarks */"
css_end = "      /* === ADVANCED ELEMENT ANIMATIONS === */"

new_card_css = """      /* Ambient Architectural Telemetry Watermarks */
      .rr-watermark {
        position: absolute !important;
        font-family: 'Geistmono', monospace !important;
        font-size: 0.7rem !important;
        letter-spacing: 0.14em !important;
        color: var(--content--primary) !important;
        background: rgba(235, 228, 219, 0.92) !important;
        border: 1px solid var(--content--border) !important;
        border-radius: 999px !important;
        padding: 5px 14px !important;
        text-transform: uppercase !important;
        font-weight: 700 !important;
        z-index: 4 !important;
        pointer-events: none !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 8px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08) !important;
      }
      .rr-watermark.top-left { top: 28px; left: 40px; }
      .rr-watermark.top-right { top: 28px; right: 40px; }
      .rr-watermark.bottom-right { bottom: 28px; right: 40px; }
      .rr-dot-pulse {
        width: 6px !important;
        height: 6px !important;
        border-radius: 50% !important;
        background: #10b981 !important;
        box-shadow: 0 0 8px #10b981 !important;
        animation: heroPulse 1.8s infinite !important;
      }

      /* Act Narrative Cards - Unified with Site Warm Sandstone Linen & Fraktion Sans */
      .rr-act-card {
        position: absolute !important;
        top: 50% !important;
        left: 64px !important;
        transform: translateY(-50%) !important;
        max-width: 520px !important;
        z-index: 5 !important;
        background: var(--content--white) !important;
        color: var(--content--primary) !important;
        border: var(--size--border) solid var(--content--border) !important;
        border-radius: 14px !important;
        padding: 2.4rem !important;
        box-shadow: 0 20px 50px rgba(28, 24, 21, 0.16), inset 0 1px 0 rgba(255, 255, 255, 0.8) !important;
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
        color: var(--content--brand) !important;
        background: rgba(250, 54, 0, 0.08) !important;
        border: 1px solid rgba(250, 54, 0, 0.25) !important;
        padding: 4px 12px !important;
        border-radius: 999px !important;
        text-transform: uppercase !important;
        margin-bottom: 0.9rem !important;
      }
      .rr-tag-icon {
        font-size: 0.9rem !important;
      }
      .rr-act-title {
        font-family: 'Fraktion Sans', sans-serif !important;
        font-size: 2.4rem !important;
        font-weight: 600 !important;
        line-height: 1.15 !important;
        letter-spacing: -0.03em !important;
        color: var(--content--primary) !important;
        margin: 0 0 1rem 0 !important;
      }
      .rr-act-desc {
        font-size: 0.98rem !important;
        line-height: 1.65 !important;
        color: var(--content--secondary) !important;
        margin: 0 0 1.4rem 0 !important;
      }
      .rr-act-desc strong {
        color: var(--content--primary) !important;
        font-weight: 700 !important;
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
        color: var(--content--secondary) !important;
        border-top: 1px solid var(--content--border) !important;
        padding-top: 1.1rem !important;
        width: 100% !important;
      }
      .rr-scroll-mouse {
        width: 14px !important;
        height: 22px !important;
        border: 1.5px solid var(--content--brand) !important;
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
        background: var(--content--brand) !important;
        border-radius: 1px !important;
        animation: mouseScroll 1.4s infinite !important;
      }

      /* Metrics in Act 2 */
      .rr-metric-row {
        display: flex !important;
        gap: 12px !important;
        border-top: 1px solid var(--content--border) !important;
        padding-top: 1.1rem !important;
      }
      .rr-metric-pill {
        flex: 1 !important;
        background: #f4efe8 !important;
        border: 1px solid var(--content--border) !important;
        border-radius: 10px !important;
        padding: 12px 14px !important;
        text-align: center !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03) !important;
      }
      .p-num {
        font-family: 'Geistmono', monospace !important;
        font-size: 1.35rem !important;
        font-weight: 800 !important;
        color: var(--content--brand) !important;
        line-height: 1.1 !important;
        margin-bottom: 3px !important;
      }
      .p-lbl {
        font-family: 'Geistmono', monospace !important;
        font-size: 9px !important;
        letter-spacing: 0.14em !important;
        text-transform: uppercase !important;
        color: var(--content--primary) !important;
        font-weight: 700 !important;
      }

      /* Badges in Act 3 */
      .rr-badge-row {
        display: grid !important;
        grid-template-columns: repeat(3, 1fr) !important;
        gap: 10px !important;
        border-top: 1px solid var(--content--border) !important;
        padding-top: 1.1rem !important;
      }
      .rr-spec-item {
        background: #f4efe8 !important;
        border: 1px solid var(--content--border) !important;
        border-radius: 10px !important;
        padding: 12px 8px !important;
        text-align: center !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03) !important;
      }
      .rr-spec-num {
        font-family: 'Geistmono', monospace !important;
        font-size: 1.35rem !important;
        font-weight: 800 !important;
        color: var(--content--brand) !important;
        line-height: 1.1 !important;
        margin-bottom: 3px !important;
      }
      .rr-spec-label {
        font-family: 'Geistmono', monospace !important;
        font-size: 9px !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
        color: var(--content--primary) !important;
        font-weight: 700 !important;
        line-height: 1.25 !important;
      }

"""

pattern_css = re.escape(css_start) + r".*?" + re.escape(css_end)
assert re.search(pattern_css, content, re.DOTALL), "CSS pattern not found"
content = re.sub(pattern_css, new_card_css + "      " + css_end, content, flags=re.DOTALL)

with open(builder_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated clean_aiswarya_builder.py card styling successfully!")
