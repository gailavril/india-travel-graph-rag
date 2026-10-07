"""
BHARAT ATLAS — India Tourism Graph RAG
Explore India through connected knowledge.
"""

# ═══════════════════════════════════════════════════════════
# SETUP
# ═══════════════════════════════════════════════════════════

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import re
import traceback
import streamlit as st
import pandas as pd

from src.graph_rag import graph_rag

st.set_page_config(
    page_title="Bharat Atlas — Explore India",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ═══════════════════════════════════════════════════════════
# SVG ICONS  (Lucide-style, stroke=currentColor)
# ═══════════════════════════════════════════════════════════

_A = ('xmlns="http://www.w3.org/2000/svg" fill="none" '
      'stroke="currentColor" stroke-width="1.5" '
      'stroke-linecap="round" stroke-linejoin="round"')

def icon(name, size=18):
    d = {
        "compass":       f'<svg {_A} width="{size}" height="{size}" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/></svg>',
        "map":           f'<svg {_A} width="{size}" height="{size}" viewBox="0 0 24 24"><polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/><line x1="8" y1="2" x2="8" y2="18"/><line x1="16" y1="6" x2="16" y2="22"/></svg>',
        "map-pin":       f'<svg {_A} width="{size}" height="{size}" viewBox="0 0 24 24"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>',
        "mountain":      f'<svg {_A} width="{size}" height="{size}" viewBox="0 0 24 24"><path d="m8 3 4 8 5-5 5 15H2L8 3z"/></svg>',
        "globe":         f'<svg {_A} width="{size}" height="{size}" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>',
        "route":         f'<svg {_A} width="{size}" height="{size}" viewBox="0 0 24 24"><circle cx="6" cy="19" r="3"/><path d="M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 0-7H15"/><circle cx="18" cy="5" r="3"/></svg>',
        "network":       f'<svg {_A} width="{size}" height="{size}" viewBox="0 0 24 24"><rect x="16" y="16" width="6" height="6" rx="1"/><rect x="2" y="16" width="6" height="6" rx="1"/><rect x="9" y="2" width="6" height="6" rx="1"/><path d="M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3"/><path d="M12 12V8"/></svg>',
        "search":        f'<svg {_A} width="{size}" height="{size}" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
        "calendar":      f'<svg {_A} width="{size}" height="{size}" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
        "camera":        f'<svg {_A} width="{size}" height="{size}" viewBox="0 0 24 24"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>',
        "utensils":      f'<svg {_A} width="{size}" height="{size}" viewBox="0 0 24 24"><path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><path d="M7 2v20"/><path d="M21 15V2a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3zm0 0v7"/></svg>',
        "users":         f'<svg {_A} width="{size}" height="{size}" viewBox="0 0 24 24"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
        "arrow-right":   f'<svg {_A} width="{size}" height="{size}" viewBox="0 0 24 24"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>',
        "arrow-left":    f'<svg {_A} width="{size}" height="{size}" viewBox="0 0 24 24"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>',
        "chevron-right": f'<svg {_A} width="{size}" height="{size}" viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"/></svg>',
        "book-open":     f'<svg {_A} width="{size}" height="{size}" viewBox="0 0 24 24"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>',
    }
    return d.get(name, "")


COMPASS_LOGO = '''<svg viewBox="0 0 32 32" width="26" height="26" fill="none"
  xmlns="http://www.w3.org/2000/svg">
  <circle cx="16" cy="16" r="14" stroke="#C65D3A" stroke-width="1"/>
  <circle cx="16" cy="16" r="11" stroke="#C65D3A" stroke-width="0.3" opacity="0.35"/>
  <polygon points="16,4 17.8,14.5 16,12.8 14.2,14.5" fill="#C65D3A"/>
  <polygon points="16,28 17.8,17.5 16,19.2 14.2,17.5" fill="#D99A32" opacity="0.75"/>
  <circle cx="16" cy="16" r="1.5" fill="#C65D3A"/>
</svg>'''


# ═══════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Design Tokens ── */
:root{
  --bg:#171A17;--bg2:#20251F;--bg3:#272C26;--bg4:#2D322C;
  --parchment:#F2E9D8;
  --terra:#C65D3A;--terra-dim:rgba(198,93,58,.12);
  --saffron:#D99A32;--saffron-dim:rgba(217,154,50,.10);
  --forest:#315C4A;--forest-dim:rgba(49,92,74,.12);
  --turq:#4F8A82;--turq-dim:rgba(79,138,130,.10);
  --t1:#F4EBDD;--t2:#B8B0A2;--t3:#7A7568;--td:#24231F;
  --border:rgba(244,235,221,.07);--border-h:rgba(244,235,221,.14);
  --serif:'DM Serif Display',Georgia,serif;
  --sans:'Inter',-apple-system,BlinkMacSystemFont,sans-serif;
}

/* ── Reset / Global ── */
html,body,.stApp{background:var(--bg)!important;color:var(--t1)!important;font-family:var(--sans)!important}
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stStatusWidget"]{display:none!important;visibility:hidden!important}

/* ── Sidebar Rail ── */
section[data-testid="stSidebar"]{background:#141714!important;border-right:1px solid var(--border)!important;width:250px!important;min-width:250px!important}
section[data-testid="stSidebar"]>div{padding-top:1.5rem!important}
section[data-testid="stSidebar"] hr{border-color:var(--border)!important;margin:.8rem 0!important}
section[data-testid="stSidebar"] .stButton button{
  background:transparent!important;border:none!important;
  border-left:2px solid transparent!important;border-radius:0!important;
  color:var(--t3)!important;font-family:var(--sans)!important;
  font-size:.73rem!important;font-weight:500!important;
  letter-spacing:.05em!important;text-transform:uppercase!important;
  text-align:left!important;padding:.5rem 1rem!important;
  transition:all .2s ease!important;justify-content:flex-start!important;
}
section[data-testid="stSidebar"] .stButton button:hover{
  color:var(--t2)!important;border-left-color:var(--terra)!important;
  background:rgba(198,93,58,.04)!important;
}

/* ── Main Area ── */
.stMainBlockContainer{padding:1.2rem 2rem!important;max-width:100%!important}

/* ── Form ── */
[data-testid="stForm"]{border:none!important;padding:0!important;background:transparent!important}

/* ── Search Input ── */
.stTextInput input{
  background:var(--bg2)!important;border:1px solid var(--border)!important;
  border-radius:6px!important;color:var(--t1)!important;
  font-family:var(--sans)!important;font-size:.92rem!important;
  padding:.8rem 1.1rem!important;transition:all .25s ease!important;
}
.stTextInput input:focus{
  border-color:var(--terra)!important;
  box-shadow:0 0 0 1px rgba(198,93,58,.15)!important;
  background:var(--bg3)!important;
}
.stTextInput input::placeholder{color:var(--t3)!important;font-style:italic!important}
.stTextInput label{display:none!important}

/* ── Form Submit ── */
[data-testid="stFormSubmitButton"] button{
  background:var(--terra)!important;color:var(--t1)!important;
  border:none!important;border-radius:6px!important;
  padding:.8rem 1.1rem!important;font-family:var(--sans)!important;
  font-weight:600!important;font-size:.8rem!important;
  letter-spacing:.08em!important;transition:all .2s ease!important;
}
[data-testid="stFormSubmitButton"] button:hover{
  background:#B5522F!important;transform:translateY(-1px)!important;
}

/* ── Chip Buttons (main area) ── */
.stMainBlockContainer .stButton button{
  background:transparent!important;
  border:1px solid var(--border)!important;
  border-radius:20px!important;color:var(--t3)!important;
  font-family:var(--sans)!important;font-size:.72rem!important;
  font-weight:400!important;padding:.32rem .8rem!important;
  letter-spacing:.02em!important;transition:all .2s ease!important;
  white-space:nowrap!important;
}
.stMainBlockContainer .stButton button:hover{
  border-color:var(--terra)!important;color:var(--terra)!important;
  background:var(--terra-dim)!important;
}

/* ── Expander ── */
.stExpander{border:1px solid var(--border)!important;border-radius:6px!important;background:var(--bg2)!important}
.stExpander [data-testid="stExpanderDetails"]{background:var(--bg2)!important}
details summary span{color:var(--t3)!important;font-size:.72rem!important;font-weight:600!important;letter-spacing:.08em!important;text-transform:uppercase!important}

/* ── Code ── */
pre{background:var(--bg)!important;border:1px solid var(--border)!important;border-radius:6px!important}

/* ── Scrollbar ── */
::-webkit-scrollbar{width:5px}::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--bg3);border-radius:3px}

/* ────────────────────────────────────────────────
   CUSTOM COMPONENT CLASSES
   ──────────────────────────────────────────────── */

/* Brand */
.atlas-brand{padding:0 1rem 1rem;border-bottom:1px solid var(--border);margin-bottom:.6rem}
.atlas-brand-row{display:flex;align-items:center;gap:.55rem}
.atlas-brand-title{font-family:var(--sans);font-size:.82rem;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:var(--t1)}
.atlas-brand-sub{font-size:.58rem;color:var(--t3);letter-spacing:.1em;margin-top:.15rem;margin-left:2.2rem}
.atlas-brand svg{transition:transform .4s ease}.atlas-brand:hover svg{transform:rotate(15deg)}

/* Nav Items */
.nav-item{display:flex;align-items:center;gap:.6rem;padding:.5rem 1rem;color:var(--t3);font-family:var(--sans);font-size:.72rem;font-weight:500;letter-spacing:.06em;text-transform:uppercase;border-left:2px solid transparent;transition:all .2s ease;cursor:default}
.nav-item:hover{color:var(--t2)}.nav-item.active{color:var(--terra);border-left-color:var(--terra);background:rgba(198,93,58,.04)}

/* Nav Footer */
.nav-footer{padding:.8rem 1rem;border-top:1px solid var(--border);margin-top:.6rem}
.nav-footer-label{font-size:.55rem;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--t3);margin-bottom:.4rem}
.nav-footer-row{display:flex;align-items:center;gap:.35rem;font-size:.68rem;color:var(--t2);margin-bottom:.2rem}
.dot{width:6px;height:6px;border-radius:50%;flex-shrink:0}
.dot-ok{background:var(--forest)}.dot-err{background:#8B3A3A}

/* Breadcrumb */
.bc{font-family:var(--sans);font-size:.65rem;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:var(--t3);margin-bottom:.3rem}
.bc em{font-style:normal;color:var(--terra)}

/* Headings */
.h-atlas{font-family:var(--serif);font-size:2.3rem;color:var(--t1);margin:.3rem 0 .2rem;letter-spacing:-.01em;line-height:1.1}
.h-sub{font-family:var(--sans);font-size:.88rem;color:var(--t3);font-weight:300;margin-bottom:1.6rem;line-height:1.5}
.h-ctx{font-family:var(--sans);font-size:.62rem;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:var(--terra);margin-bottom:.2rem}
.h-result{font-family:var(--serif);font-size:1.5rem;color:var(--t1);margin-bottom:1.2rem}

/* Answer Block */
.ans{padding:1.3rem;background:var(--bg2);border:1px solid var(--border);border-left:3px solid var(--terra);border-radius:0 8px 8px 0;margin:1.2rem 0}
.ans-label{font-size:.58rem;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--terra);margin-bottom:.5rem}
.ans-body{font-family:var(--sans);font-size:.88rem;color:var(--t2);line-height:1.75}

/* Destination Card */
.dc{background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:1.3rem;margin-bottom:.8rem;transition:all .25s ease;position:relative}
.dc:hover{border-color:var(--border-h);transform:translateY(-2px);box-shadow:0 8px 20px rgba(0,0,0,.25)}
.dc-name{font-family:var(--serif);font-size:1.35rem;color:var(--t1);margin-bottom:.1rem}
.dc-state{font-family:var(--sans);font-size:.68rem;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--saffron);margin-bottom:.5rem}
.dc-desc{font-family:var(--sans);font-size:.84rem;color:var(--t2);line-height:1.55;margin-bottom:.75rem}
.dc-highlight{background:var(--saffron-dim);border-left:3px solid var(--saffron);padding:.5rem .75rem;border-radius:0 4px 4px 0;margin-bottom:.75rem;font-family:var(--sans);font-size:.78rem;color:var(--t2);line-height:1.45}
.dc-highlight strong{color:var(--saffron);font-size:.65rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;display:block;margin-bottom:.15rem}
.dc-meta{display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:.8rem;padding-top:.7rem;border-top:1px solid var(--border)}
.dc-mi{display:flex;flex-direction:column}
.dc-mv{font-family:var(--sans);font-size:.9rem;font-weight:700;color:var(--t1)}
.dc-ml{font-family:var(--sans);font-size:.55rem;font-weight:600;letter-spacing:.15em;text-transform:uppercase;color:var(--t3);margin-top:.05rem}
.dc-tags{display:flex;gap:.4rem;flex-wrap:wrap;margin-bottom:.8rem}
.dc-tag{font-family:var(--sans);font-size:.6rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--forest);background:var(--forest-dim);padding:.2rem .5rem;border-radius:3px}
.dc-link{font-family:var(--sans);font-size:.68rem;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--terra);display:inline-flex;align-items:center;gap:.35rem;transition:gap .2s ease}
.dc-link:hover{gap:.55rem}
.dc-coord{position:absolute;top:.8rem;right:.9rem;font-family:'Courier New',monospace;font-size:.55rem;color:var(--t3);opacity:.45}

/* Knowledge Trail (right panel) */
.kp{background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:1.3rem;min-height:280px}
.kp-title{font-family:var(--sans);font-size:.62rem;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:var(--t3);margin-bottom:1.2rem;padding-bottom:.4rem;border-bottom:1px solid var(--border)}
.kp-empty{font-family:var(--sans);font-size:.8rem;color:var(--t3);font-style:italic;line-height:1.6}
.tn{display:flex;align-items:flex-start;gap:.65rem;padding:.1rem 0}
.td{width:10px;height:10px;border-radius:50%;margin-top:4px;flex-shrink:0}
.td-q{background:var(--t1)}.td-s{background:var(--saffron)}.td-d{background:var(--terra)}
.td-a{background:var(--forest)}.td-t{background:var(--turq)}.td-sn{background:var(--saffron)}
.tl{font-family:var(--sans);font-size:.52rem;font-weight:700;letter-spacing:.15em;text-transform:uppercase;color:var(--t3);margin-bottom:.05rem}
.tv{font-family:var(--sans);font-size:.82rem;font-weight:500;color:var(--t1)}
.tc{width:1px;height:18px;background:var(--border-h);margin-left:4.5px}
.k-sum{font-family:var(--sans);font-size:.6rem;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--t3);margin-top:1.2rem;padding-top:.6rem;border-top:1px solid var(--border)}
.k-rels{margin-top:.6rem}.k-rel{font-size:.72rem;color:var(--t2);padding:.2rem 0;display:flex;gap:.4rem}
.k-rt{color:var(--t3);font-size:.6rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;min-width:65px}

/* Suggestion Cards */
.sg{background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:1.1rem;transition:all .25s ease;height:100%}
.sg:hover{border-color:var(--terra);transform:translateY(-2px);box-shadow:0 6px 16px rgba(0,0,0,.2)}
.sg-t{font-family:var(--sans);font-size:.6rem;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--terra);margin-bottom:.35rem}
.sg-d{font-family:var(--sans);font-size:.78rem;color:var(--t2);font-style:italic;line-height:1.4}

/* Loading */
@keyframes spin{from{transform:rotate(0)}to{transform:rotate(360deg)}}
.ld{display:flex;flex-direction:column;align-items:center;justify-content:center;padding:3.5rem 2rem;text-align:center}
.ld-c{animation:spin 2.5s linear infinite;margin-bottom:1.2rem;color:var(--terra)}
.ld-t{font-family:var(--sans);font-size:.82rem;color:var(--t3);font-style:italic}

/* Error */
.err{padding:2rem;text-align:center}
.err-h{font-family:var(--serif);font-size:1.25rem;color:var(--t1);margin-bottom:.35rem}
.err-t{font-family:var(--sans);font-size:.82rem;color:var(--t3)}

/* Section divider label */
.sdl{font-family:var(--sans);font-size:.6rem;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--t3);padding:0 1rem;margin-bottom:.35rem}

/* ── Responsive ── */
@media(max-width:768px){
  .h-atlas{font-size:1.5rem}.dc-name{font-size:1.1rem}.dc-meta{gap:.6rem}
  .kp{min-height:auto}
}
</style>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════

def extract_knowledge_trail(result):
    """Parse Cypher + results to build Knowledge Trail nodes & relationships."""
    cypher  = result.get("cypher", "")
    records = result.get("results", [])
    nodes, rels = [], []

    # State
    m = re.search(r"toLower\(s\.name\)\s*=\s*'([^']+)'", cypher, re.I)
    if not m:
        m = re.search(r"\{?\s*name:\s*'([^']+)'\s*\}?", cypher, re.I)
    if m:
        nodes.append(("s", "STATE", m.group(1).title()))
        rels.append(("State", m.group(1).title()))
    elif records and records[0].get("state"):
        nodes.append(("s", "STATE", records[0]["state"]))
        rels.append(("State", records[0]["state"]))

    # Destinations from results
    seen = set()
    for r in records[:5]:
        n = r.get("destination")
        if n and n not in seen:
            nodes.append(("d", "DESTINATION", n)); seen.add(n)

    # Activity
    m = re.search(r"toLower\(a\.name\)\s*CONTAINS\s*'([^']+)'", cypher, re.I)
    if m:
        v = m.group(1).title()
        nodes.append(("a", "ACTIVITY", v)); rels.append(("Activity", v))

    # Traveler type
    m = re.search(r"toLower\(t\.name\)\s*CONTAINS\s*'([^']+)'", cypher, re.I)
    if m:
        v = m.group(1).title()
        nodes.append(("t", "TRAVELER TYPE", v)); rels.append(("Traveler", v))

    # Cuisine
    m = re.search(r"toLower\(c\.name\)\s*CONTAINS\s*'([^']+)'", cypher, re.I)
    if m:
        v = m.group(1).title()
        nodes.append(("c", "CUISINE", v)); rels.append(("Cuisine", v))

    # Attraction
    m = re.search(r"toLower\(att\.name\)\s*CONTAINS\s*'([^']+)'", cypher, re.I)
    if m:
        v = m.group(1).title()
        nodes.append(("att", "ATTRACTION", v)); rels.append(("Attraction", v))

    # Season
    m = re.search(r"toLower\(\w+\.name\)\s*CONTAINS\s*'(monsoon|summer|winter|autumn|spring|post.monsoon|pre.monsoon)[^']*'", cypher, re.I)
    if m:
        v = m.group(1).title()
        nodes.append(("sn", "SEASON", v)); rels.append(("Season", v))

    rel_count = len(re.findall(r'\[:[A-Z_]+\]', cypher))
    return nodes, rels, rel_count


def build_trail_html(result):
    """Render Knowledge Trail panel HTML."""
    if not result:
        return (
            '<div class="kp-title">Knowledge Trail</div>'
            '<div class="kp-empty">Begin exploring to see<br>your knowledge trail.</div>'
        )

    nodes, rels, rc = extract_knowledge_trail(result)
    if not nodes:
        return (
            '<div class="kp-title">Knowledge Trail</div>'
            '<div class="kp-empty">No trail data for this query.</div>'
        )

    q = result.get("question", "").strip()
    if len(q) > 55:
        q = q[:52] + "..."

    dot_map = {"s": "td-s", "d": "td-d", "a": "td-a", "t": "td-t", "sn": "td-sn", "c": "td-s", "att": "td-a"}
    parts = ['<div class="kp-title">Knowledge Trail</div>']

    # Question node
    parts.append(f'''<div class="tn"><div class="td td-q"></div><div>
<div class="tl">QUESTION</div>
<div class="tv" style="font-style:italic;font-size:.78rem;color:var(--t2);">{q}</div>
</div></div><div class="tc"></div>''')

    for i, (ntype, label, value) in enumerate(nodes):
        dot_cls = dot_map.get(ntype, "td-d")
        parts.append(f'''<div class="tn"><div class="td {dot_cls}"></div><div>
<div class="tl">{label}</div>
<div class="tv">{value}</div>
</div></div>''')
        if i < len(nodes) - 1:
            parts.append('<div class="tc"></div>')

    if rc:
        parts.append(f'<div class="k-sum">Connected through {rc} relationship{"s" if rc != 1 else ""}</div>')

    if rels:
        parts.append('<div class="k-rels">')
        for rt, rv in rels:
            parts.append(f'<div class="k-rel"><span class="k-rt">{rt}</span><span>→ {rv}</span></div>')
        parts.append('</div>')

    return "\n".join(parts)


def build_dest_card(dest, idx):
    """Build editorial HTML for one destination card."""
    name   = dest.get("destination") or dest.get("destination_name") or dest.get("name") or "Unknown"
    state  = dest.get("state", "")
    safety = dest.get("safety_rating")
    pop    = dest.get("popularity_score")
    days   = dest.get("ideal_days")
    lat    = dest.get("latitude")
    lon    = dest.get("longitude")
    desc   = dest.get("description") or dest.get("user_reviews_summary") or ""

    coord = ""
    if lat and lon:
        try: coord = f'<div class="dc-coord">{float(lat):.1f}°N, {float(lon):.1f}°E</div>'
        except (TypeError, ValueError): pass

    state_html = f'<div class="dc-state">{state}</div>' if state else ""

    # Short description
    desc_html = f'<div class="dc-desc">{desc}</div>' if desc else ""

    # Question-specific contextual highlights
    highlights = []
    if dest.get("food_scene"):
        highlights.append(f'<div class="dc-highlight"><strong>Food Scene</strong>{dest["food_scene"]}</div>')
    elif dest.get("local_culture"):
        highlights.append(f'<div class="dc-highlight"><strong>Culture & Heritage</strong>{dest["local_culture"]}</div>')
    elif dest.get("safety_notes"):
        highlights.append(f'<div class="dc-highlight"><strong>Safety Advice</strong>{dest["safety_notes"]}</div>')
    elif dest.get("special_considerations"):
        highlights.append(f'<div class="dc-highlight"><strong>Travel Note</strong>{dest["special_considerations"]}</div>')
    highlight_html = "".join(highlights[:1])

    metas = []
    if days:   metas.append(f'<div class="dc-mi"><div class="dc-mv">{days} days</div><div class="dc-ml">Ideal Stay</div></div>')
    if safety: metas.append(f'<div class="dc-mi"><div class="dc-mv">{safety}/10</div><div class="dc-ml">Safety</div></div>')
    if pop:    metas.append(f'<div class="dc-mi"><div class="dc-mv">{pop}/10</div><div class="dc-ml">Popularity</div></div>')
    meta_html = f'<div class="dc-meta">{"".join(metas)}</div>' if metas else ""

    # Tags (Activities, Cuisines, Attractions, Seasons, etc.)
    tags = []
    for k in ("activities", "activity", "cuisines", "cuisine", "attractions", "attraction", "best_seasons", "traveler_type", "trip_type"):
        v = dest.get(k)
        if not v:
            continue
        if isinstance(v, list):
            for item in v:
                if item and str(item) not in tags:
                    tags.append(str(item))
        elif isinstance(v, str):
            if v not in tags:
                tags.append(v)

    tags_html = ""
    if tags:
        tags_html = '<div class="dc-tags">' + "".join(f'<span class="dc-tag">{t}</span>' for t in tags[:4]) + '</div>'

    arr = icon("arrow-right", 13)
    return f'''<div class="dc">{coord}
        <div class="dc-name">{name}</div>{state_html}{desc_html}{highlight_html}{tags_html}{meta_html}
        <span class="dc-link">Explore destination {arr}</span></div>'''


def answer_to_html(text):
    """Minimal markdown → HTML for the answer block."""
    h = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    h = h.replace("\n", "<br>")
    h = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', h)
    h = re.sub(r'(?m)^\* ', '• ', h)
    h = re.sub(r'(?m)^- ', '• ', h)
    return h


# ═══════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════

st.session_state.setdefault("current_result", None)
st.session_state.setdefault("current_query", "")
st.session_state.setdefault("current_error", None)


# ═══════════════════════════════════════════════════════════
# SIDEBAR — LEFT NAVIGATION RAIL
# ═══════════════════════════════════════════════════════════

with st.sidebar:
    # Brand
    st.markdown(f'''
    <div class="atlas-brand">
        <div class="atlas-brand-row">{COMPASS_LOGO}
            <span class="atlas-brand-title">BHARAT ATLAS</span></div>
        <div class="atlas-brand-sub">India Tourism · Graph RAG</div>
    </div>''', unsafe_allow_html=True)

    # Navigation (visual rail — only Explore is active)
    nav = [
        ("compass",  "Explore",        True),
        ("map-pin",  "Destinations",   False),
        ("mountain", "Activities",     False),
        ("globe",    "Regions",        False),
        ("route",    "Trip Planner",   False),
        ("network",  "Graph Explorer", False),
    ]
    nav_html = ""
    for ico, label, active in nav:
        cls = "nav-item active" if active else "nav-item"
        nav_html += f'<div class="{cls}"><span style="color:inherit">{icon(ico, 15)}</span>{label}</div>'
    st.markdown(nav_html, unsafe_allow_html=True)

    st.markdown("---")

    # Suggested journeys
    st.markdown('<div class="sdl">Suggested Journeys</div>', unsafe_allow_html=True)

    examples = [
        "Trekking destinations in Karnataka",
        "Best hill stations for families in Kerala",
        "Offbeat places for photographers",
        "Where can I go scuba diving?",
        "Heritage destinations near Delhi",
        "Beach destinations with good safety",
        "Solo backpacker spots in Northeast",
        "Best monsoon destinations for nature lovers",
    ]
    for ex in examples:
        if st.button(f"→  {ex}", key=f"ex_{hash(ex)}", use_container_width=True):
            st.session_state.pending_query = ex
            st.rerun()

    st.markdown("---")

    # Footer — engine status
    neo_ok = gem_ok = False
    try:
        from src.neo4j_connection import driver
        driver.verify_connectivity(); neo_ok = True
    except Exception: pass
    try:
        from src.config import GEMINI_API_KEY
        gem_ok = bool(GEMINI_API_KEY)
    except Exception: pass

    nd = "dot-ok" if neo_ok else "dot-err"
    gd = "dot-ok" if gem_ok else "dot-err"
    st.markdown(f'''
    <div class="nav-footer">
        <div class="nav-footer-label">Graph RAG Engine</div>
        <div class="nav-footer-row"><div class="dot {nd}"></div>Neo4j {"connected" if neo_ok else "disconnected"}</div>
        <div class="nav-footer-row"><div class="dot {gd}"></div>Gemini {"ready" if gem_ok else "unavailable"}</div>
    </div>''', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# MAIN LAYOUT  —  Center + Right Knowledge Panel
# ═══════════════════════════════════════════════════════════

center_col, right_col = st.columns([3, 1.2])
pending = st.session_state.pop("pending_query", None)

with center_col:
    # ── Breadcrumb ──
    if st.session_state.current_result:
        st.markdown(
            '<div class="bc">INDIA <em>/</em> EXPLORE <em>/</em> RESULTS</div>',
            unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="bc">INDIA <em>/</em> EXPLORE</div>',
            unsafe_allow_html=True)

    # ── Atlas heading (only when no results) ──
    if not st.session_state.current_result and not st.session_state.current_error:
        st.markdown('<h1 class="h-atlas">Where will you go next?</h1>', unsafe_allow_html=True)
        st.markdown(
            '<p class="h-sub">Explore India through places, experiences, seasons and connections.</p>',
            unsafe_allow_html=True)

    # ── Search Form ──
    with st.form("atlas_search"):
        sc = st.columns([6, 1])
        with sc[0]:
            query = st.text_input(
                "search", placeholder="Ask the atlas anything about India...",
                label_visibility="collapsed", key="search_input")
        with sc[1]:
            submitted = st.form_submit_button("SEARCH")

    # ── Determine active query ──
    active_query = None
    if submitted and query and query.strip():
        active_query = query.strip()
    elif pending:
        active_query = pending

    # ── Process ──
    if active_query:
        ph = st.empty()
        ph.markdown(f'''
            <div class="ld">
                <div class="ld-c">{icon("compass", 34)}</div>
                <div class="ld-t">Tracing your journey through the atlas…</div>
            </div>''', unsafe_allow_html=True)
        try:
            result = graph_rag(active_query)
            st.session_state.current_result = result
            st.session_state.current_query  = active_query
            st.session_state.current_error  = None
        except Exception as e:
            st.session_state.current_error  = str(e)
            st.session_state.current_result = None
        ph.empty()

    # ──────────────────────────────────────────────
    # RENDER CONTENT
    # ──────────────────────────────────────────────

    if st.session_state.current_error:
        # ── Error State ──
        st.markdown('''
            <div class="err">
                <div class="err-h">That route wasn't found.</div>
                <div class="err-t">Try asking about a destination, activity, season or region.</div>
            </div>''', unsafe_allow_html=True)
        with st.expander("Technical details"):
            st.code(st.session_state.current_error)
        if st.button("← New journey", key="err_back"):
            st.session_state.current_result = None
            st.session_state.current_error  = None
            st.rerun()

    elif st.session_state.current_result:
        # ── Results State ──
        res     = st.session_state.current_result
        records = res.get("results", [])
        answer  = res.get("answer", "")
        cypher  = res.get("cypher", "")

        st.markdown(
            '<div class="h-ctx">RESULTS</div>'
            '<div class="h-result">Places that match your journey</div>',
            unsafe_allow_html=True)

        # Answer block
        if answer:
            st.markdown(f'''
                <div class="ans">
                    <div class="ans-label">Travel Intelligence</div>
                    <div class="ans-body">{answer_to_html(answer)}</div>
                </div>''', unsafe_allow_html=True)

        # Destination cards (2 per row)
        if records:
            for row in range(0, len(records), 2):
                chunk = records[row:row + 2]
                cols = st.columns(len(chunk))
                for i, dest in enumerate(chunk):
                    with cols[i]:
                        st.markdown(build_dest_card(dest, row + i), unsafe_allow_html=True)

        # Technical view
        with st.expander("Technical view"):
            if cypher:
                st.markdown(
                    '<div style="font-size:.6rem;font-weight:700;letter-spacing:.16em;'
                    'text-transform:uppercase;color:var(--t3);margin-bottom:.4rem">'
                    'Generated Cypher Query</div>', unsafe_allow_html=True)
                st.code(cypher, language="cypher")
            if records:
                st.markdown(
                    f'<div style="font-size:.6rem;font-weight:700;letter-spacing:.16em;'
                    f'text-transform:uppercase;color:var(--t3);margin:.8rem 0 .4rem">'
                    f'Retrieved Graph Entities ({len(records)} records)</div>',
                    unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(records), use_container_width=True)

        if st.button("← New journey", key="res_back"):
            st.session_state.current_result = None
            st.session_state.current_query  = ""
            st.rerun()

    else:
        # ── Empty State ──
        st.markdown("---")

        # Chips
        chips = [
            "3-day trekking destinations",
            "Quiet places in Goa",
            "Best for photographers",
            "Family-friendly spots",
            "Kerala in monsoon",
        ]
        cc = st.columns(len(chips))
        for i, c in enumerate(chips):
            with cc[i]:
                if st.button(c, key=f"chip_{i}"):
                    st.session_state.pending_query = c
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # Begin your journey
        st.markdown('''
            <div style="text-align:center;margin:1.5rem 0 .3rem">
                <div style="font-family:var(--serif);font-size:1.35rem;color:var(--t1)">
                    Begin your journey.</div>
                <div style="font-family:var(--sans);font-size:.82rem;color:var(--t3);margin-top:.25rem">
                    Ask about places, seasons, experiences or travel styles.</div>
            </div>''', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 4 Suggestion cards
        sug = [
            ("FIND ADVENTURE",  "Where can I go trekking?",               "mountain"),
            ("SLOW TRAVEL",     "Quiet destinations away from crowds",    "route"),
            ("FOOD & CULTURE",  "Places known for local cuisine",         "utensils"),
            ("PHOTOGRAPHY",     "Destinations for landscape photography", "camera"),
        ]
        scols = st.columns(4)
        for i, (title, desc, ico) in enumerate(sug):
            with scols[i]:
                st.markdown(f'''
                    <div class="sg">
                        <div style="color:var(--terra);margin-bottom:.5rem">{icon(ico, 20)}</div>
                        <div class="sg-t">{title}</div>
                        <div class="sg-d">"{desc}"</div>
                    </div>''', unsafe_allow_html=True)


# ── RIGHT PANEL — Knowledge Trail ──
with right_col:
    st.markdown(
        f'<div class="kp">{build_trail_html(st.session_state.current_result)}</div>',
        unsafe_allow_html=True)
