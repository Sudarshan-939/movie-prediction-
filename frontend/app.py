"""
CineScore — Neural Cinema Intelligence
Psychology × Developer Theme
"""
import math, time, requests
import streamlit as st

st.set_page_config(
    page_title="CineScore Neural",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Inline SVG icon library ───────────────────────────────────
def _ico(path_d, size=16, stroke="currentColor", fill="none", sw=1.8, extra=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
            f'viewBox="0 0 24 24" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" {extra}>'
            f'{path_d}</svg>')

# Star — IMDb
ICO_STAR = _ico('<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>', fill="currentColor", stroke="none")
# Film strip — TMDB
ICO_FILM = _ico('<rect x="2" y="2" width="20" height="20" rx="2.18"/><line x1="7" y1="2" x2="7" y2="22"/><line x1="17" y1="2" x2="17" y2="22"/><line x1="2" y1="12" x2="22" y2="12"/><line x1="2" y1="7" x2="7" y2="7"/><line x1="2" y1="17" x2="7" y2="17"/><line x1="17" y1="7" x2="22" y2="7"/><line x1="17" y1="17" x2="22" y2="17"/>')
# Tomato circle — RT
ICO_TOMA = _ico('<circle cx="12" cy="13" r="8" fill="currentColor" stroke="none"/><path d="M12 5 C12 5 10 2 7 3" stroke="currentColor" stroke-width="2" fill="none"/><path d="M12 5 C12 5 14 1 17 3" stroke="currentColor" stroke-width="2" fill="none"/>', fill="currentColor", stroke="none")
# CPU chip — AI
ICO_CPU  = _ico('<rect x="9" y="9" width="6" height="6"/><path d="M9 2v3M15 2v3M9 19v3M15 19v3M2 9h3M2 15h3M19 9h3M19 15h3"/><rect x="4" y="4" width="16" height="16" rx="2"/>')
# Play triangle — YouTube/trailer
ICO_PLAY = _ico('<circle cx="12" cy="12" r="10"/><polygon points="10 8 16 12 10 16" fill="currentColor"/>')
# Movie camera — section header
ICO_CAM  = _ico('<path d="M15 2H9L7 7H3a1 1 0 0 0-1 1v11a1 1 0 0 0 1 1h18a1 1 0 0 0 1-1V8a1 1 0 0 0-1-1h-4l-2-5z"/><circle cx="12" cy="13" r="3"/>')
# Database — metadata
ICO_DB   = _ico('<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>')
# Bar chart — comparison
ICO_BARS = _ico('<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>')
# Sparkle — verdict
ICO_SPARK= _ico('<path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>')
# Frame fallback poster icon
ICO_FRAME    = _ico('<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/>', size=48)
# Large play icon for empty trailer placeholder
ICO_PLAY_BIG = _ico('<circle cx="12" cy="12" r="10"/><polygon points="10 8 16 12 10 16" fill="currentColor"/>', size=52)

import os
BACKEND    = os.environ.get("BACKEND_URL", "https://movie-prediction-ufhz.onrender.com")
YT_API_KEY = "AIzaSyDUUBNeOc1TFqQeBEJick89iXBrZg3x1as"
YT_SEARCH  = "https://www.googleapis.com/youtube/v3/search"

# ══════════════════════════════════════════════════════════════
#  PSYCHOLOGY × DEVELOPER DARK THEME CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Inter:wght@300;400;500;600;700;800;900&family=Playfair+Display:ital,wght@0,700;0,800;1,700&display=swap');

/* ─── Variables ─── */
:root {
  --void:     #02020a;
  --deep:     #060612;
  --surface:  #0a0a1a;
  --card:     #0d0d20;
  --card2:    #101024;
  --lift:     #13132a;
  --border:   rgba(99,110,255,.14);
  --border2:  rgba(99,110,255,.28);
  --cyan:     #00d4ff;
  --neural:   #636eff;
  --violet:   #9f6eff;
  --green:    #00ff88;
  --amber:    #ffb800;
  --red:      #ff4466;
  --imdb:     #f5c518;
  --tmdb:     #00b4e4;
  --rt:       #ff4444;
  --text:     #e8e8ff;
  --text2:    #9090c0;
  --muted:    #4a4a78;
  --mono:     'JetBrains Mono', monospace;
  --sans:     'Inter', sans-serif;
  --serif:    'Playfair Display', serif;
  --r:        12px;
  --r-lg:     20px;
}

/* ─── Base ─── */
html, body, [class*="st-"] { font-family: var(--sans) !important; }
.main, [data-testid="stApp"] { background: var(--void) !important; }
.block-container { padding: 0 2.4rem 6rem !important; max-width: 1420px !important; margin: auto !important; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebar"] { display: none; }

/* ─── Background neural grid ─── */
[data-testid="stApp"]::before {
  content: '';
  position: fixed; inset: 0; z-index: 0; pointer-events: none;
  background-image:
    linear-gradient(rgba(99,110,255,.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(99,110,255,.04) 1px, transparent 1px);
  background-size: 44px 44px;
}
[data-testid="stApp"]::after {
  content: '';
  position: fixed; top: 0; left: 0; right: 0; height: 340px;
  background: radial-gradient(ellipse 80% 50% at 50% -5%,
    rgba(99,110,255,.18) 0%, transparent 70%);
  z-index: 0; pointer-events: none;
}
.block-container { position: relative; z-index: 1; }

/* ─── Animations ─── */
@keyframes fadeUp   { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }
@keyframes fadeIn   { from{opacity:0} to{opacity:1} }
@keyframes scanline { from{transform:translateY(-100%)} to{transform:translateY(200vh)} }
@keyframes pulse    { 0%,100%{opacity:.6} 50%{opacity:1} }
@keyframes glow-c   { 0%,100%{box-shadow:0 0 16px rgba(0,212,255,.2)} 50%{box-shadow:0 0 32px rgba(0,212,255,.45)} }
@keyframes dash-c   { from{stroke-dasharray:0 1000} }
@keyframes blink    { 0%,100%{opacity:1} 50%{opacity:0} }
@keyframes slide-r  { from{opacity:0;transform:translateX(14px)} to{opacity:1;transform:translateX(0)} }

.anim-up   { animation: fadeUp .5s cubic-bezier(.22,.68,0,1.15) both; }
.anim-in   { animation: fadeIn .4s ease both; }
.s1{animation-delay:.05s} .s2{animation-delay:.12s}
.s3{animation-delay:.20s} .s4{animation-delay:.28s}
.s5{animation-delay:.36s}

/* ─── Scrollbar ─── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--surface); }
::-webkit-scrollbar-thumb { background: var(--neural); border-radius: 99px; opacity: .4; }

/* ══════ APP HEADER ══════ */
.nn-header {
  position: relative;
  text-align: center;
  padding: 3.8rem 1rem 2.4rem;
  overflow: hidden;
}
.nn-header .scanline {
  position: absolute; top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(to right, transparent, var(--cyan), transparent);
  animation: scanline 4s linear infinite;
  opacity: .5; pointer-events: none;
}
.nn-badge {
  display: inline-flex; align-items: center; gap: .5rem;
  background: rgba(99,110,255,.1);
  border: 1px solid rgba(99,110,255,.3);
  border-radius: 6px;
  padding: .3rem .9rem;
  font-family: var(--mono);
  font-size: .68rem; font-weight: 500;
  color: var(--neural); letter-spacing: .12em;
  text-transform: uppercase; margin-bottom: 1.2rem;
}
.nn-badge .dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--green); animation: pulse 2s ease infinite;
}
.nn-title {
  font-family: var(--serif);
  font-size: clamp(2.8rem, 5.5vw, 4.6rem);
  font-weight: 800; line-height: 1.05; margin: 0 0 .6rem;
  background: linear-gradient(125deg, var(--cyan) 0%, var(--neural) 40%, var(--violet) 80%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
}
.nn-sub {
  font-family: var(--mono);
  color: var(--muted); font-size: .83rem; letter-spacing: .06em;
  margin-bottom: 1.4rem;
}
.nn-sub em { color: var(--neural); font-style: normal; }
.platform-row {
  display: flex; gap: .5rem; justify-content: center;
  flex-wrap: wrap; margin: 0 0 .4rem;
}
.plat-pill {
  display: inline-flex; align-items: center; gap: .35rem;
  padding: .28rem .8rem; border-radius: 6px;
  font-family: var(--mono); font-size: .67rem; font-weight: 500;
  letter-spacing: .08em; border: 1px solid;
  transition: transform .2s, box-shadow .2s;
}
.plat-pill:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,.4); }

/* ══════ SEARCH ══════ */
div[data-testid="stTextInput"] input {
  background: var(--card) !important;
  color: var(--text) !important;
  border: 1px solid var(--border2) !important;
  border-radius: var(--r) !important;
  font-family: var(--mono) !important;
  font-size: .95rem !important;
  padding: .85rem 1.2rem !important;
  transition: border-color .25s, box-shadow .25s !important;
  caret-color: var(--cyan);
}
div[data-testid="stTextInput"] input:focus {
  border-color: var(--cyan) !important;
  box-shadow: 0 0 0 3px rgba(0,212,255,.12), 0 0 20px rgba(0,212,255,.08) !important;
  background: var(--card2) !important;
}
div[data-testid="stTextInput"] input::placeholder { color: var(--muted) !important; }
div[data-testid="stButton"] > button {
  background: linear-gradient(135deg, var(--neural) 0%, var(--cyan) 100%) !important;
  color: #fff !important; font-weight: 700 !important;
  border: none !important; border-radius: var(--r) !important;
  padding: .72rem 1.5rem !important; letter-spacing: .04em !important;
  font-family: var(--mono) !important; font-size: .85rem !important;
  transition: transform .18s, box-shadow .22s, filter .2s !important;
}
div[data-testid="stButton"] > button:hover {
  transform: translateY(-3px) scale(1.02) !important;
  box-shadow: 0 8px 28px rgba(99,110,255,.45) !important;
  filter: brightness(1.1) !important;
}

/* ══════ RESULT CARDS ══════ */
.res-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: .95rem;
  cursor: pointer;
  transition: border-color .22s, transform .22s, box-shadow .22s;
  animation: fadeUp .4s ease both;
  position: relative; overflow: hidden;
}
.res-card::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(to right, var(--neural), var(--cyan));
  opacity: 0; transition: opacity .25s;
}
.res-card:hover { border-color: var(--border2); transform: translateY(-5px);
  box-shadow: 0 16px 40px rgba(0,0,0,.5); }
.res-card:hover::before { opacity: 1; }
.res-card img { width:100%; border-radius:8px; margin-bottom:.6rem; display:block; }
.res-noimg {
  width:100%; height:145px; border-radius:8px;
  background: var(--surface);
  display:flex; align-items:center; justify-content:center;
  font-size:2.5rem; margin-bottom:.6rem;
  border: 1px dashed var(--border);
}
.res-title {
  font-weight: 700; font-size: .93rem; color: var(--text);
  margin: 0 0 .2rem; font-family: var(--sans);
}
.res-meta { font-family: var(--mono); font-size: .72rem; color: var(--muted); margin-bottom: .28rem; }
.res-over {
  font-size: .75rem; color: #38386a; line-height: 1.55;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}

/* ══════ MOVIE HERO ══════ */
.mhero {
  position: relative; border-radius: var(--r-lg);
  overflow: hidden; margin-bottom: 1.4rem;
  background: var(--card); min-height: 270px;
  border: 1px solid var(--border);
  animation: fadeIn .5s ease;
}
.mhero-bd {
  position: absolute; inset: 0;
  width:100%; height:100%; object-fit:cover;
  opacity: .1; filter: blur(3px) saturate(1.3);
}
.mhero-grad {
  position: absolute; inset: 0;
  background: linear-gradient(105deg,
    rgba(2,2,10,.98) 0%,
    rgba(6,6,18,.92) 45%,
    rgba(6,6,18,.6) 75%,
    rgba(6,6,18,.25) 100%);
}
/* neural circuit lines overlay */
.mhero-circuits {
  position: absolute; inset: 0; pointer-events: none;
  background-image:
    linear-gradient(rgba(99,110,255,.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(99,110,255,.06) 1px, transparent 1px);
  background-size: 36px 36px; opacity: .6;
}
.mhero-inner {
  position: relative; z-index: 2;
  display: flex; align-items: center;
  gap: 2.2rem; padding: 2.2rem 2.6rem;
}
.mhero-poster {
  flex-shrink: 0; width: 152px;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0,0,0,.85), 0 0 0 1px rgba(99,110,255,.25);
  display: block; align-self: center;
  animation: fadeUp .5s .1s ease both;
  transition: transform .3s, box-shadow .3s;
}
.mhero-poster:hover {
  transform: scale(1.04) translateY(-4px);
  box-shadow: 0 28px 70px rgba(0,0,0,.9), 0 0 0 1px var(--neural), 0 0 20px rgba(99,110,255,.25);
}
.mhero-noimg {
  flex-shrink: 0; width: 152px; height: 228px;
  border-radius: 12px; background: var(--surface);
  display: flex; align-items: center; justify-content: center;
  font-size: 4rem;
  border: 1px dashed var(--border);
}
.mhero-details {
  flex: 1; display: flex; flex-direction: column;
  justify-content: center; gap: .55rem; padding: .3rem 0;
  animation: fadeUp .55s .15s ease both;
}
.mhero-id {
  font-family: var(--mono); font-size: .65rem;
  color: var(--muted); letter-spacing: .1em;
  display: flex; align-items: center; gap: .5rem;
}
.mhero-id-line { flex:1; height:1px; background: var(--border); }
.mhero-rated {
  display: inline-flex; align-items: center;
  background: rgba(255,184,0,.12);
  border: 1px solid rgba(255,184,0,.3);
  border-radius: 6px; padding: .15rem .6rem;
  font-family: var(--mono); font-size: .65rem; font-weight: 700;
  color: var(--amber); letter-spacing: .1em;
  text-transform: uppercase; width: fit-content;
}
.mhero-title {
  font-family: var(--serif);
  font-size: clamp(1.6rem, 2.8vw, 2.7rem);
  font-weight: 800; color: var(--text); line-height: 1.12; margin: 0;
}
.mhero-meta {
  font-family: var(--mono); color: var(--text2);
  font-size: .78rem; display: flex; align-items: center;
  gap: .45rem; flex-wrap: wrap;
}
.mhero-dot { color: var(--border2); }
.mhero-tag { color: #6060a0; font-size: .82rem; font-style: italic; line-height: 1.55; max-width: 580px; }
.mhero-genres { display: flex; gap: .35rem; flex-wrap: wrap; }
.mhero-genre {
  background: rgba(99,110,255,.1); border: 1px solid rgba(99,110,255,.22);
  border-radius: 5px; padding: .2rem .7rem;
  font-family: var(--mono); font-size: .68rem; color: var(--neural);
  transition: background .2s;
}
.mhero-genre:hover { background: rgba(99,110,255,.22); }
.mhero-verdict {
  display: inline-flex; align-items: center; gap: .5rem;
  background: rgba(0,255,136,.08); border: 1px solid rgba(0,255,136,.25);
  border-radius: 6px; padding: .3rem 1rem;
  font-family: var(--mono); font-size: .78rem; font-weight: 600;
  color: var(--green); width: fit-content;
  animation: glow-c 3s ease infinite;
}
.mhero-verdict svg { width:14px; height:14px; flex-shrink:0; }
@media(max-width:640px){
  .mhero-inner{flex-direction:column;align-items:flex-start;padding:1.5rem 1.6rem;}
  .mhero-poster{width:110px;}
}

/* ══════ RATING CARDS ══════ */
.r-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--r); padding: 1.3rem 1rem;
  text-align: center; position: relative; overflow: hidden;
  transition: transform .22s, box-shadow .22s, border-color .22s;
  animation: fadeUp .45s ease both;
}
.r-card:hover { transform: translateY(-4px); box-shadow: 0 16px 40px rgba(0,0,0,.6); }
.r-card::after {
  content:''; position:absolute; bottom:0; left:0; right:0; height:1px;
  background: linear-gradient(to right, transparent, var(--neural), transparent);
  opacity: 0; transition: opacity .3s;
}
.r-card:hover::after { opacity: .6; }
.r-card-ai {
  background: linear-gradient(155deg, #10082a 0%, #0d0d20 100%);
  border-color: rgba(159,110,255,.35);
  box-shadow: 0 0 30px rgba(159,110,255,.1), inset 0 1px 0 rgba(159,110,255,.15);
}
.r-logo {
  display:flex; align-items:center; justify-content:center;
  height:36px; margin-bottom:.5rem;
}
.r-logo svg { width:28px; height:28px; }
.r-platform {
  font-family: var(--mono); font-size: .85rem;
  text-transform: uppercase; letter-spacing: .12em;
  margin-bottom: .6rem; font-weight: 700;
}
.r-ring { position:relative; display:inline-flex; align-items:center; justify-content:center; margin:.6rem 0; }
.r-ring svg circle:last-child { animation: dash-c .9s ease both; }
.r-score { position:absolute; font-weight:900; font-family:var(--mono); line-height:1; text-shadow: 0 2px 8px rgba(0,0,0,0.6); }
.r-sub { font-family: var(--mono); font-size: .95rem; font-weight: 700; color: #fff; margin-top: .6rem; line-height: 1.3; }

/* ══════ CONTENT ZONE ══════ */
.trailer-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--r); overflow: hidden;
}
.zone-header {
  display: flex; align-items: center; gap: .55rem;
  padding: .85rem 1.2rem;
  font-family: var(--mono); font-size: .7rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: .1em;
  color: var(--muted); border-bottom: 1px solid var(--border);
}
.zone-header .zh-icon { color: var(--cyan); }
.trailer-embed { position:relative; padding-bottom:56.25%; height:0; overflow:hidden; }
.trailer-embed iframe { position:absolute;top:0;left:0;width:100%;height:100%;border:none; }
.trailer-none {
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  padding:3rem 2rem; color:var(--muted); font-family:var(--mono); font-size:.78rem; gap:.6rem;
}
.trailer-none .yt-big { font-size:2.6rem; opacity:.2; }

.info-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--r); overflow: hidden;
}
.info-body { padding: 1.1rem 1.3rem; }
.ir { display:flex; gap:.6rem; margin:.42rem 0; font-size:.82rem; align-items:flex-start; }
.ir-k {
  font-family: var(--mono); color: var(--muted); min-width: 78px;
  flex-shrink:0; font-size:.68rem; text-transform:uppercase;
  letter-spacing:.08em; padding-top:.14rem; font-weight:600;
}
.ir-v { color: var(--text); font-weight: 500; line-height: 1.5; }
.plot-box {
  background: rgba(99,110,255,.07); border-left: 2px solid var(--neural);
  border-radius: 0 8px 8px 0; padding: .8rem 1rem;
  color: #6060a0; font-size: .8rem; line-height: 1.7;
  font-style: italic; margin-top: .8rem;
}
.hdiv { height:1px; background:var(--border); margin:1rem 0; border:none; }
.pb-wrap { margin:.4rem 0; }
.pb-label {
  display:flex; justify-content:space-between;
  font-family:var(--mono); font-size:.7rem;
  color:var(--muted); margin-bottom:.28rem;
}
.pb-track { height:6px; background:rgba(255,255,255,.05); border-radius:99px; overflow:hidden; }
.pb-fill  { height:100%; border-radius:99px; transition:width .8s cubic-bezier(.22,.68,0,1.2); }
.chip {
  display:inline-flex; align-items:center; gap:.3rem;
  background: rgba(99,110,255,.08); border: 1px solid rgba(99,110,255,.22);
  border-radius:6px; padding:.26rem .7rem;
  font-family:var(--mono); font-size:.67rem; color:var(--text2);
}

/* ══════ HOME FEAT CARDS ══════ */
.feat-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--r); padding: 1.7rem 1.2rem; text-align: center;
  transition: border-color .22s, transform .22s, box-shadow .22s;
  animation: fadeUp .4s ease both; position: relative; overflow:hidden;
}
.feat-card::before {
  content:''; position:absolute; top:0; left:0; right:0; height:2px;
  background: linear-gradient(to right, var(--neural), var(--cyan));
  opacity: 0; transition: opacity .25s;
}
.feat-card:hover { border-color:var(--border2); transform:translateY(-4px);
  box-shadow:0 12px 35px rgba(0,0,0,.5); }
.feat-card:hover::before { opacity: 1; }
.feat-ico {
  display:flex; align-items:center; justify-content:center;
  height:36px; margin-bottom:.65rem;
}
.feat-ico svg { width:26px; height:26px; }
.feat-name { font-family:var(--mono); font-weight:700; font-size:.85rem; margin-bottom:.4rem; }
.feat-desc { color:var(--muted); font-size:.76rem; line-height:1.65; }
.quick-label {
  text-align:center; font-family:var(--mono);
  color:var(--muted); font-size:.75rem; margin:.6rem 0 .9rem;
  letter-spacing:.06em;
}

/* ══════ FOOTER ══════ */
.nn-footer {
  text-align:center; font-family:var(--mono);
  color:var(--muted); font-size:.7rem; margin-top:3.5rem;
  padding-top:1.2rem; border-top:1px solid var(--border);
  letter-spacing:.04em;
}
.nn-footer b { color:var(--text2); font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──
for k, v in [("results", []), ("movie", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── API helpers ──
def api_search(q):
    try:
        return requests.get(f"{BACKEND}/api/search", params={"title": q}, timeout=12).json()
    except Exception as e:
        return {"error": str(e)}

def api_predict(imdb_id):
    try:
        return requests.get(f"{BACKEND}/api/predict", params={"imdb_id": imdb_id}, timeout=15).json()
    except Exception as e:
        return {"error": str(e)}

def get_yt_trailer(title: str, year: str = "") -> str | None:
    try:
        q = f"{title} {year} official trailer".strip()
        r = requests.get(YT_SEARCH, params={
            "part": "snippet", "q": q, "type": "video",
            "maxResults": 1, "videoEmbeddable": "true", "key": YT_API_KEY,
        }, timeout=8)
        items = r.json().get("items", [])
        return items[0]["id"]["videoId"] if items else None
    except:
        return None

def score_color(v):
    if v is None: return "#4a4a6a"
    v = float(v)
    if v >= 8.0: return "#00ff88"
    if v >= 6.5: return "#ffb800"
    if v >= 5.0: return "#ff9a00"
    return "#ff4466"

def ring_html(score, max_v=10, size=92, stroke=9, color="#636eff"):
    r_ = (size - stroke) / 2
    circ = 2 * math.pi * r_
    frac = min(max(float(score or 0) / max_v, 0), 1) if score else 0
    dash = frac * circ; gap = circ - dash
    cx = cy = size / 2
    val = f"{score:.1f}" if score is not None else "N/A"
    return f"""
<div class="r-ring">
  <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" style="transform:rotate(-90deg)">
    <circle cx="{cx}" cy="{cy}" r="{r_}" fill="none" stroke="rgba(99,110,255,.1)" stroke-width="{stroke}"/>
    <circle cx="{cx}" cy="{cy}" r="{r_}" fill="none" stroke="{color}" stroke-width="{stroke}"
            stroke-linecap="round" stroke-dasharray="{dash:.2f} {gap:.2f}"/>
  </svg>
  <div class="r-score" style="font-size:2.2rem;color:{color};">{val}</div>
</div>"""

def prog_bar(label, val, max_v, color, disp):
    if val is None: return ""
    pct = min(max(float(val) / max_v * 100, 0), 100)
    return f"""
<div class="pb-wrap">
  <div class="pb-label"><span>{label}</span><span>{disp}</span></div>
  <div class="pb-track"><div class="pb-fill" style="width:{pct:.1f}%;background:{color};"></div></div>
</div>"""

def fmt_money(v):
    if not v: return None
    v = int(v)
    if v >= 1_000_000_000: return f"${v/1e9:.2f}B"
    if v >= 1_000_000:     return f"${v/1e6:.1f}M"
    return f"${v:,}"

# ══════════════════════════════════════════════════════════════
#  APP HEADER
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div class="nn-header anim-up">
  <div class="scanline"></div>
  <div class="nn-badge"><div class="dot"></div>NEURAL CINEMA INTELLIGENCE // v2.0</div>
  <div class="nn-title">CineScore</div>
  <div class="nn-sub">AI prediction engine · <em>IMDb</em> · <em>TMDB</em> · <em>Rotten Tomatoes</em> · <em>YouTube</em></div>
  <div class="platform-row">
    <span class="plat-pill" style="background:rgba(245,197,24,.1);border-color:rgba(245,197,24,.3);color:#f5c518;">{ico_star} IMDb</span>
    <span class="plat-pill" style="background:rgba(0,180,228,.1);border-color:rgba(0,180,228,.3);color:#00b4e4;">{ico_film} TMDB</span>
    <span class="plat-pill" style="background:rgba(255,68,68,.1);border-color:rgba(255,68,68,.3);color:#ff4444;">{ico_toma} RT</span>
    <span class="plat-pill" style="background:rgba(159,110,255,.1);border-color:rgba(159,110,255,.3);color:#9f6eff;">{ico_cpu} AI Pred</span>
    <span class="plat-pill" style="background:rgba(255,0,0,.08);border-color:rgba(255,60,60,.3);color:#ff5555;">{ico_play} Trailer</span>
  </div>
</div>
""".format(
    ico_star=ICO_STAR, ico_film=ICO_FILM,
    ico_toma=ICO_TOMA, ico_cpu=ICO_CPU, ico_play=ICO_PLAY,
), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  SEARCH
# ══════════════════════════════════════════════════════════════
sc1, sc2 = st.columns([6, 1], gap="small")
with sc1:
    query = st.text_input("", placeholder="// search movie title — typos are fine, e.g. 'incepsion', 'opnheimer'…",
                          label_visibility="collapsed", key="q")
with sc2:
    st.markdown("<div style='margin-top:.12rem'></div>", unsafe_allow_html=True)
    go = st.button("run →", use_container_width=True)

if go and query.strip():
    with st.spinner("querying…"):
        res = api_search(query.strip())
    if "error" in res:
        st.error(f"[ ERR ] backend offline: {res['error']}")
    elif not res.get("results"):
        st.warning("[ 0 results ] — try a different title")
    else:
        st.session_state.results = res["results"]
        st.session_state.movie   = None

# ══════════════════════════════════════════════════════════════
#  SEARCH RESULTS
# ══════════════════════════════════════════════════════════════
if st.session_state.results and not st.session_state.movie:
    cnt = len(st.session_state.results)
    st.markdown(
        f"<p style='font-family:var(--mono);color:var(--muted);font-size:.7rem;"
        f"margin:.5rem 0 .9rem;letter-spacing:.06em;'>"
        f"<span style='color:var(--cyan)'>›</span> {cnt} matches found — select to run prediction</p>",
        unsafe_allow_html=True)
    cols = st.columns(3, gap="medium")
    for i, m in enumerate(st.session_state.results[:9]):
        with cols[i % 3]:
            poster = m.get("poster","") or ""
            img_html = (f'<img src="{poster}">' if poster and poster != "N/A"
                        else f'<div class="res-noimg">{ICO_FRAME}</div>')
            tr = m.get("tmdb_rating")
            tr_str = (f'<span style="color:var(--tmdb);font-family:var(--mono);font-size:.7rem;">tmdb:{tr:.1f}</span>'
                      if tr else "")
            ov = m.get("overview","") or ""
            st.markdown(f"""
<div class="res-card anim-up s{min(i%3+1,5)}">
  {img_html}
  <div class="res-title">{m['title']}</div>
  <div class="res-meta">{m.get('year','—')} &nbsp; {tr_str}</div>
  <div class="res-over">{ov}</div>
</div>""", unsafe_allow_html=True)
            if st.button("→ predict", key=f"p_{m['imdb_id'] or i}", use_container_width=True):
                st.session_state.movie = m
                st.rerun()

# ══════════════════════════════════════════════════════════════
#  PREDICTION PAGE
# ══════════════════════════════════════════════════════════════
if st.session_state.movie:
    m = st.session_state.movie
    with st.spinner("loading neural analysis…"):
        data  = api_predict(m["imdb_id"])
        yt_id = get_yt_trailer(m.get("title",""), m.get("year",""))

    if "error" in data:
        st.error(f"[ ERR ] {data['error']}")
    else:
        pred    = data["predicted_rating"]
        ratings = data.get("ratings", {})
        imdb_v  = ratings.get("imdb")
        tmdb_v  = ratings.get("tmdb")
        rt_raw  = ratings.get("rotten_tomatoes")
        rt_v    = float(rt_raw.replace("%",""))/10 if rt_raw else None
        rt_txt  = rt_raw or "N/A"
        backdrop= data.get("backdrop","")
        poster  = data.get("poster","")
        p_color = score_color(pred)
        senti   = data.get("sentiment","—")
        r2      = data.get("model_r2", 0)
        rmse    = data.get("model_rmse", 0)

        # genre chips
        genre_str   = data.get("genre","") or ""
        genre_chips = "".join(
            f'<span class="mhero-genre">{g.strip()}</span>'
            for g in genre_str.split(",") if g.strip()
        )

        # hero banner
        bd_el    = f'<img class="mhero-bd" src="{backdrop}">' if backdrop else ""
        rated    = data.get("rated","") or ""
        rated_html = (f'<div class="mhero-rated">{rated}</div>'
                      if rated and rated != "N/A" else "")
        tag_html = (f'<div class="mhero-tag">"{data["tagline"]}"</div>'
                    if data.get("tagline") else "")
        poster_el = (f'<img class="mhero-poster" src="{poster}" alt="{data["title"]}">'
                     if poster and poster != "N/A"
                     else f'<div class="mhero-noimg">{ICO_FRAME}</div>')
        imdb_id_label = data.get("imdb_id","—")

        st.markdown(f"""
<div class="mhero">
{bd_el}
<div class="mhero-grad"></div>
<div class="mhero-circuits"></div>
<div class="mhero-inner">
{poster_el}
<div class="mhero-details">
<div class="mhero-id">
<span style="color:var(--cyan)">›</span> imdb:{imdb_id_label}
<div class="mhero-id-line"></div>
</div>
{rated_html}
<div class="mhero-title">{data['title']}</div>
<div class="mhero-meta">
<span>{data.get('year','—')}</span><span class="mhero-dot">·</span>
<span>{data.get('runtime','—')}</span><span class="mhero-dot">·</span>
<span>{data.get('language','—')}</span><span class="mhero-dot">·</span>
<span>{data.get('country','—')}</span>
</div>
{tag_html}
<div class="mhero-genres">{genre_chips}</div>
<div class="mhero-verdict">{ICO_SPARK} {senti}</div>
</div>
</div>
</div>""", unsafe_allow_html=True)

        # ── Rating cards (4 cols) ──
        r1, r2c, r3, r4 = st.columns(4, gap="small")

        def rcard(col, logo, platform, score, sub, color, delay, ai=False):
            cls = "r-card-ai" if ai else ""
            top = "var(--violet)" if ai else color
            plat_html = (f'<span style="color:var(--violet)">{platform}</span>' if ai
                         else platform)
            with col:
                st.markdown(f"""
<div class="r-card {cls} anim-up s{delay}" style="border-top:2px solid {top};">
  <div class="r-logo" style="color:{top};">{logo}</div>
  <div class="r-platform" style="color:{top};">{plat_html}</div>
  {ring_html(score, color=color)}
  <div class="r-sub">{sub}</div>
</div>""", unsafe_allow_html=True)

        rcard(r1,  ICO_STAR, "// IMDb",   imdb_v, f"{ratings.get('imdb_votes','—')} votes", "#f5c518", 1)
        rcard(r2c, ICO_FILM, "// TMDB",   tmdb_v, f"{ratings.get('tmdb_votes','—')} votes", "#00b4e4", 2)
        rcard(r3,  ICO_TOMA, "// RT",     rt_v,   rt_txt,                                   "#ff4444",  3)
        rcard(r4,  ICO_CPU,  "// AI pred", pred,  senti,                                    p_color,   4, ai=True)

        st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)

        # ── Trailer | Info+Bars ──
        tc, ic = st.columns([1.2, 1], gap="medium")

        with tc:
            header = f'<div class="zone-header"><span class="zh-icon">{ICO_PLAY}</span> official_trailer.mp4</div>'
            if yt_id:
                embed = f"https://www.youtube.com/embed/{yt_id}?rel=0&modestbranding=1&color=white"
                st.markdown(f"""
<div class="trailer-card anim-up s3">
  {header}
  <div class="trailer-embed">
    <iframe src="{embed}"
      allow="accelerometer;autoplay;clipboard-write;encrypted-media;gyroscope;picture-in-picture"
      allowfullscreen title="{data['title']} trailer"></iframe>
  </div>
</div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
<div class="trailer-card anim-up s3">
  {header}
  <div class="trailer-none">
    <div class="yt-big" style="opacity:.25;">{ICO_PLAY_BIG}</div><span>// trailer not found</span>
  </div>
</div>""", unsafe_allow_html=True)

        with ic:
            b   = fmt_money(data.get("budget"))
            rev = fmt_money(data.get("revenue"))
            info_rows = [
                ("director", data.get("director")),
                ("cast",     data.get("actors")),
                ("awards",   data.get("awards")),
                ("budget",   b),
                ("revenue",  rev),
            ]
            info_html = "".join(
                f'<div class="ir"><span class="ir-k">{k}</span><span class="ir-v">{v}</span></div>'
                for k, v in info_rows if v and v != "N/A"
            )
            plot = data.get("plot","")
            plot_html = f'<div class="plot-box">"{plot}"</div>' if plot and plot != "N/A" else ""

            bars  = prog_bar(f"{ICO_STAR} IMDb",   imdb_v, 10, "#f5c518", f"{imdb_v:.1f}/10" if imdb_v else "N/A")
            bars += prog_bar(f"{ICO_FILM} TMDB",   tmdb_v, 10, "#00b4e4", f"{tmdb_v:.1f}/10" if tmdb_v else "N/A")
            bars += prog_bar(f"{ICO_TOMA} RT",     rt_v,   10, "#ff4444",  rt_txt)
            bars += prog_bar(f"{ICO_CPU} AI pred", pred,   10, p_color,   f"{pred:.2f}/10")

            r2_val = data.get("model_r2", 0)
            rmse_val = data.get("model_rmse", 0)

            ico_db   = ICO_DB
            ico_bars = ICO_BARS
            ico_cpu2 = ICO_CPU
            st.markdown(f"""
<div class="info-card anim-up s4">
  <div class="zone-header"><span class="zh-icon">{ico_db}</span> movie_metadata.json</div>
  <div class="info-body">
    {info_html}
    {plot_html}
    <hr class="hdiv">
    <div class="zone-header" style="border:none;padding:.2rem 0 .7rem;">
      <span class="zh-icon">{ico_bars}</span> rating_comparison[]
    </div>
    {bars}
    <hr class="hdiv">
    <div style="display:flex;gap:.4rem;flex-wrap:wrap;">
      <span class="chip" style="color:var(--violet);">{ico_cpu2} model: GBR+RF+Ridge</span>
      <span class="chip" style="color:var(--green);">r²={r2_val}</span>
      <span class="chip" style="color:var(--amber);">rmse={rmse_val}</span>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)
        if st.button("← back to search", key="back"):
            st.session_state.movie   = None
            st.session_state.results = []
            st.rerun()

# ══════════════════════════════════════════════════════════════
#  HOME STATE
# ══════════════════════════════════════════════════════════════
if not st.session_state.results and not st.session_state.movie:
    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

    feats = [
        (ICO_STAR, "#f5c518", "// imdb_api",  "Real-time ratings & vote counts. 250K+ movie index via OMDB."),
        (ICO_FILM, "#00b4e4", "// tmdb_api",  "Popularity metrics, budget, revenue & community vote data."),
        (ICO_TOMA, "#ff4444", "// rt_scores", "Critics' Tomatometer. Fetched live from OMDB ratings array."),
        (ICO_PLAY, "#ff5555", "// yt_embed",  "Official trailer auto-fetched via YouTube Data API v3."),
    ]
    fc = st.columns(4, gap="medium")
    for i, (col, (ico, color, name, desc)) in enumerate(zip(fc, feats)):
        with col:
            st.markdown(f"""
<div class="feat-card anim-up s{i+1}">
  <div class="feat-ico">{ico}</div>
  <div class="feat-name" style="color:{color};">{name}</div>
  <div class="feat-desc">{desc}</div>
</div>""", unsafe_allow_html=True)

    st.markdown(
        "<p class='quick-label'>// quick_search[] — click to analyse</p>",
        unsafe_allow_html=True)
    picks = ["Oppenheimer", "Dune", "Parasite", "The Dark Knight", "Inception", "Barbie"]
    pc = st.columns(len(picks), gap="small")
    for i, t in enumerate(picks):
        with pc[i]:
            if st.button(t, use_container_width=True, key=f"qp_{i}"):
                with st.spinner("…"):
                    res = api_search(t)
                if res.get("results"):
                    st.session_state.results = res["results"]
                    st.rerun()

# ══════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div class="nn-footer">
  <b>OMDB API</b> · <b>TMDB API</b> · <b>YouTube Data API v3</b> ·
  ensemble: <b>GradientBoosting + RandomForest + Ridge</b>
</div>""", unsafe_allow_html=True)
