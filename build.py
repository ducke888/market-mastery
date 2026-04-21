#!/usr/bin/env python3
"""Assemble the final Market Mastery HTML with embedded real data."""
import json, sys

# ============================================================
# MAINTENANCE MODE  (edit here, or use command-line args)
# python3 build.py close          → maintenance page
# python3 build.py close "msg"    → maintenance page with custom message
# python3 build.py open           → normal site
# python3 build.py                → uses whatever is set below
# ============================================================
MAINTENANCE_MODE = False
MAINTENANCE_MESSAGE = "We're making some improvements. Check back soon!"
# ============================================================

# Override from command line
if len(sys.argv) >= 2:
    cmd = sys.argv[1].lower()
    if cmd == 'close':
        MAINTENANCE_MODE = True
        if len(sys.argv) >= 3:
            MAINTENANCE_MESSAGE = sys.argv[2]
    elif cmd == 'open':
        MAINTENANCE_MODE = False

with open("real_data_min.json") as f:
    real_data = f.read()

DISPLAY_CANDLES = 120

if MAINTENANCE_MODE:
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Market Mastery | Under Maintenance</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap" rel="stylesheet"/>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{min-height:100vh;background:#0a0b10;color:#e5e7eb;font-family:'Inter',sans-serif;display:flex;align-items:center;justify-content:center;text-align:center;padding:20px}}
.wrap{{max-width:480px}}
.icon{{font-size:72px;margin-bottom:24px;animation:spin 8s linear infinite}}
@keyframes spin{{0%,100%{{transform:rotate(-5deg)}}50%{{transform:rotate(5deg)}}}}
h1{{font-size:36px;font-weight:900;color:#fff;margin-bottom:12px;letter-spacing:-0.03em}}
h1 span{{background:linear-gradient(135deg,#26a69a,#2dd4bf);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}
p{{font-size:16px;color:#9ca3af;line-height:1.7;margin-bottom:32px}}
.badge{{display:inline-flex;align-items:center;gap:8px;font-size:12px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#26a69a;border:1px solid rgba(38,166,154,0.3);border-radius:100px;padding:8px 20px;background:rgba(38,166,154,0.07)}}
.dot{{width:8px;height:8px;border-radius:50%;background:#26a69a;animation:pulse 1.5s ease infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:0.4}}}}
</style>
</head>
<body>
<div class="wrap">
  <div class="icon">🔧</div>
  <h1>Market<span> Mastery</span></h1>
  <p>{MAINTENANCE_MESSAGE}</p>
  <div class="badge"><span class="dot"></span>Under Maintenance</div>
</div>
</body>
</html>'''
    with open("index.html", "w") as f:
        f.write(html)
    print(f"Built index.html: MAINTENANCE MODE ({len(html)/1024:.1f} KB)")
    exit()

html = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Market Mastery | Learn Technical Analysis</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet"/>
<script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
<script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
<!-- Firebase -->
<script src="https://www.gstatic.com/firebasejs/10.12.0/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.12.0/firebase-firestore-compat.js"></script>

<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#0a0b10;--bg2:#111318;--bg3:#171a24;--bg4:#1c2030;--border:#232840;--border2:#2a3050;--text:#e5e7eb;--text2:#9ca3af;--text3:#6b7280;--green:#26a69a;--red:#ef5350;--blue:#2962ff;--orange:#ff9800;--purple:#9b59b6;--accent:#3b82f6;--radius:12px;--radius-sm:8px}
html,body{height:100%;background:var(--bg);color:var(--text);font-family:'Inter',system-ui,sans-serif;font-size:15px;line-height:1.6;-webkit-font-smoothing:antialiased;overflow-x:hidden}
#root{min-height:100vh}
.app{min-height:100vh;background:var(--bg)}

/* ======== ANIMATIONS ======== */
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
@keyframes fadeInUp{from{opacity:0;transform:translateY(24px)}to{opacity:1;transform:translateY(0)}}
@keyframes fadeInDown{from{opacity:0;transform:translateY(-16px)}to{opacity:1;transform:translateY(0)}}
@keyframes fadeInScale{from{opacity:0;transform:scale(0.92)}to{opacity:1;transform:scale(1)}}
@keyframes slideInLeft{from{opacity:0;transform:translateX(-30px)}to{opacity:1;transform:translateX(0)}}
@keyframes slideInRight{from{opacity:0;transform:translateX(30px)}to{opacity:1;transform:translateX(0)}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.5}}
@keyframes shimmer{0%{background-position:-200% 0}100%{background-position:200% 0}}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-12px)}}
@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}
@keyframes tickerScroll{from{transform:translateX(0)}to{transform:translateX(-50%)}}
@keyframes candleGrow{from{transform:scaleY(0);transform-origin:bottom}to{transform:scaleY(1);transform-origin:bottom}}
@keyframes glowPulse{0%,100%{box-shadow:0 0 20px rgba(38,166,154,0.3)}50%{box-shadow:0 0 40px rgba(38,166,154,0.6)}}
@keyframes borderGlow{0%,100%{border-color:rgba(38,166,154,0.2)}50%{border-color:rgba(38,166,154,0.5)}}
@keyframes gradientShift{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
@keyframes morphBlob{0%{border-radius:40% 60% 70% 30%/50% 40% 60% 50%}33%{border-radius:70% 30% 50% 50%/30% 60% 40% 70%}66%{border-radius:50% 50% 30% 70%/60% 40% 50% 50%}100%{border-radius:30% 70% 60% 40%/50% 60% 30% 70%}}

.anim-fadeIn{animation:fadeIn 0.5s ease forwards}
.anim-fadeInUp{animation:fadeInUp 0.6s cubic-bezier(0.22,1,0.36,1) forwards}
.anim-fadeInScale{animation:fadeInScale 0.5s cubic-bezier(0.22,1,0.36,1) forwards}

/* ======== FLUID GLASS INTRO ======== */
.intro-overlay{position:fixed;inset:0;z-index:200;display:flex;align-items:center;justify-content:center;background:#050508;overflow:hidden}
.intro-overlay.phase-exit{animation:introFadeOut 0.8s ease forwards}
@keyframes introFadeOut{to{opacity:0;visibility:hidden;pointer-events:none}}

/* Animated background: finance-themed */
.intro-bg{position:absolute;inset:0;overflow:hidden}
.intro-bg::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at 30% 40%,rgba(41,98,255,0.15),transparent 60%),radial-gradient(ellipse at 70% 60%,rgba(38,166,154,0.12),transparent 50%);z-index:1}

/* Fluid glass morphing shapes */
.fluid-shape{position:absolute;filter:blur(100px);opacity:0.4;animation:morphBlob 12s ease-in-out infinite alternate}
.fluid-1{width:600px;height:600px;background:linear-gradient(135deg,#2962ff,#9b59b6);top:-15%;left:-10%;animation-delay:0s}
.fluid-2{width:500px;height:500px;background:linear-gradient(135deg,#26a69a,#2962ff);bottom:-15%;right:-10%;animation-delay:-4s}
.fluid-3{width:400px;height:400px;background:linear-gradient(45deg,#ef5350,#ff9800);top:40%;left:45%;animation-delay:-8s}

/* Animated candlestick bars in background */
.intro-candles{position:absolute;bottom:0;left:0;right:0;height:40%;z-index:1;opacity:0.08;display:flex;align-items:flex-end;gap:3px;padding:0 5%}
.intro-candle{width:4px;background:var(--green);border-radius:2px;animation:candleGrow 1.5s ease forwards;opacity:0}
.intro-candle.red{background:var(--red)}

/* Grid lines in background */
.intro-grid{position:absolute;inset:0;z-index:1;opacity:0.04;
background-image:linear-gradient(rgba(255,255,255,0.1) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,0.1) 1px,transparent 1px);
background-size:60px 60px}

/* Floating particles */
.intro-particles{position:absolute;inset:0;z-index:2}
.intro-particle{position:absolute;border-radius:50%;animation:particleDrift linear infinite}
@keyframes particleDrift{0%{transform:translateY(0) translateX(0);opacity:0.2}50%{opacity:0.6}100%{transform:translateY(-100vh) translateX(40px);opacity:0}}

/* Center content */
.intro-center{position:relative;z-index:10;display:flex;flex-direction:column;align-items:center;text-align:center}

/* Logo animation: spins in then settles */
.intro-logo-wrap{opacity:0;transform:scale(0) rotate(-180deg);animation:logoSpin 1s cubic-bezier(0.22,1,0.36,1) 0.3s forwards}
@keyframes logoSpin{to{opacity:1;transform:scale(1) rotate(0deg)}}
.intro-logo{width:80px;height:80px;border-radius:22px;background:linear-gradient(135deg,var(--green),var(--blue));display:flex;align-items:center;justify-content:center;box-shadow:0 8px 40px rgba(38,166,154,0.4);animation:glowPulse 3s ease-in-out infinite 1.3s}
.intro-logo svg{width:40px;height:40px}

/* Title types in */
.intro-title{font-size:clamp(36px,6vw,56px);font-weight:900;color:#fff;letter-spacing:-0.03em;margin-top:28px;opacity:0;animation:fadeInUp 0.7s cubic-bezier(0.22,1,0.36,1) 0.9s forwards}
.intro-title .accent{background:linear-gradient(135deg,var(--green),#2dd4bf);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}

.intro-tagline{font-size:16px;color:var(--text2);margin-top:12px;opacity:0;animation:fadeInUp 0.6s cubic-bezier(0.22,1,0.36,1) 1.15s forwards}

/* Glass card behind CTA */
.intro-glass-card{margin-top:36px;padding:28px 40px;background:rgba(255,255,255,0.03);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,0.06);border-radius:20px;opacity:0;animation:fadeInScale 0.7s cubic-bezier(0.22,1,0.36,1) 1.4s forwards}

.intro-start-btn{background:linear-gradient(135deg,var(--green),#2dd4bf);color:#fff;border:none;padding:16px 40px;border-radius:14px;font-size:17px;font-weight:700;cursor:pointer;transition:all 0.3s;font-family:'Inter',sans-serif;letter-spacing:-0.01em}
.intro-start-btn:hover{transform:translateY(-3px);box-shadow:0 12px 40px rgba(38,166,154,0.5)}

.intro-features{display:flex;gap:24px;margin-top:20px;opacity:0;animation:fadeIn 0.6s ease 1.7s forwards}
.intro-feat{font-size:12px;color:var(--text3);display:flex;align-items:center;gap:6px}
.intro-feat-dot{width:4px;height:4px;border-radius:50%;background:var(--green)}

/* Ticker tape at bottom */
.intro-ticker{position:absolute;bottom:24px;left:0;right:0;z-index:5;overflow:hidden;opacity:0;animation:fadeIn 0.5s ease 2s forwards}
.ticker-track{display:flex;gap:40px;animation:tickerScroll 30s linear infinite;white-space:nowrap}
.ticker-item{font-size:11px;font-family:'JetBrains Mono',monospace;color:var(--text3);display:flex;align-items:center;gap:6px}
.ticker-item .up{color:var(--green)}
.ticker-item .down{color:var(--red)}

/* ======== NAVIGATION TABS ======== */
.nav-bar{position:sticky;top:0;z-index:50;display:flex;align-items:center;justify-content:space-between;padding:0 24px;height:56px;background:rgba(10,11,16,0.85);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border-bottom:1px solid var(--border);transition:all 0.3s}
.nav-left{display:flex;align-items:center;gap:20px}
.nav-logo{font-size:16px;font-weight:800;display:flex;align-items:center;gap:8px;cursor:pointer}
.nav-logo-icon{width:28px;height:28px;border-radius:8px;background:linear-gradient(135deg,var(--green),var(--blue));display:flex;align-items:center;justify-content:center;flex-shrink:0}
.nav-logo-icon svg{width:14px;height:14px}
.nav-logo-text{color:#fff;letter-spacing:-0.01em}
.nav-logo-text .accent{color:var(--green)}
.nav-tabs{display:flex;gap:4px;margin-left:20px}
.nav-tab{padding:8px 16px;border-radius:8px;font-size:13px;font-weight:600;color:var(--text3);cursor:pointer;transition:all 0.2s;border:none;background:transparent;font-family:'Inter',sans-serif}
.nav-tab:hover{color:var(--text);background:var(--bg3)}
.nav-tab.active{color:var(--green);background:rgba(38,166,154,0.1)}
.nav-right{display:flex;align-items:center;gap:12px}
.nav-user{display:flex;align-items:center;gap:8px;padding:6px 12px;border-radius:8px;border:1px solid var(--border);background:var(--bg3);cursor:pointer;transition:all 0.2s;font-family:'Inter',sans-serif;color:var(--text2);font-size:13px}
.nav-user:hover{border-color:var(--border2);background:var(--bg4)}
.nav-user-avatar{width:24px;height:24px;border-radius:50%;background:linear-gradient(135deg,var(--green),var(--blue));display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:#fff}
.nav-login-btn{padding:8px 16px;border-radius:8px;font-size:13px;font-weight:600;color:#fff;background:var(--green);border:none;cursor:pointer;transition:all 0.2s;font-family:'Inter',sans-serif}
.nav-login-btn:hover{background:#2bb5a8;transform:translateY(-1px)}

/* Mode toggle */
.mode-toggle{display:flex;align-items:center;gap:8px;padding:4px;border-radius:10px;background:var(--bg3);border:1px solid var(--border)}
.mode-opt{padding:6px 14px;border-radius:7px;font-size:12px;font-weight:600;color:var(--text3);cursor:pointer;transition:all 0.2s;border:none;background:transparent;font-family:'Inter',sans-serif}
.mode-opt.active{color:#fff;background:var(--green);box-shadow:0 2px 8px rgba(38,166,154,0.3)}

/* ======== AUTH MODAL ======== */
.modal-overlay{position:fixed;inset:0;z-index:100;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.7);backdrop-filter:blur(8px);animation:fadeIn 0.2s ease}
.modal-card{background:var(--bg2);border:1px solid var(--border);border-radius:20px;padding:36px;max-width:420px;width:90%;animation:fadeInScale 0.3s cubic-bezier(0.22,1,0.36,1)}
.modal-close{position:absolute;top:16px;right:16px;background:none;border:none;color:var(--text3);cursor:pointer;font-size:20px;font-family:'Inter',sans-serif}
.modal-title{font-size:24px;font-weight:800;color:#fff;margin-bottom:6px}
.modal-sub{font-size:14px;color:var(--text2);margin-bottom:24px}
.modal-google{width:100%;padding:14px;border-radius:10px;border:1px solid var(--border);background:var(--bg3);color:var(--text);font-size:14px;font-weight:600;cursor:pointer;transition:all 0.2s;display:flex;align-items:center;justify-content:center;gap:10px;font-family:'Inter',sans-serif}
.modal-google:hover{background:var(--bg4);border-color:var(--border2)}
.modal-divider{display:flex;align-items:center;gap:12px;margin:20px 0;font-size:12px;color:var(--text3)}
.modal-divider::before,.modal-divider::after{content:'';flex:1;height:1px;background:var(--border)}
.modal-input{width:100%;padding:12px 14px;border-radius:10px;border:1px solid var(--border);background:var(--bg3);color:var(--text);font-size:14px;margin-bottom:12px;font-family:'Inter',sans-serif;outline:none;transition:border-color 0.2s}
.modal-input:focus{border-color:var(--accent)}
.modal-input::placeholder{color:var(--text3)}
.modal-submit{width:100%;padding:14px;border-radius:10px;background:var(--green);color:#fff;font-size:14px;font-weight:700;border:none;cursor:pointer;transition:all 0.2s;font-family:'Inter',sans-serif;margin-top:4px}
.modal-submit:hover{background:#2bb5a8}
.modal-submit:disabled{opacity:0.5;cursor:default}
.modal-switch{text-align:center;margin-top:16px;font-size:13px;color:var(--text3)}
.modal-switch a{color:var(--accent);cursor:pointer;text-decoration:none;font-weight:600}
.modal-switch a:hover{text-decoration:underline}
.modal-error{color:var(--red);font-size:13px;margin-bottom:12px;padding:8px 12px;background:rgba(239,83,80,0.1);border-radius:8px}

/* ======== LANDING HOME ======== */
.landing{min-height:calc(100vh - 56px);position:relative;overflow:hidden;background:var(--bg);isolation:isolate}

/* Grid overlay */
.landing::before{content:'';position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,0.03) 1px,transparent 1px);background-size:80px 80px;pointer-events:none}
.landing::after{content:'';position:absolute;top:-200px;right:-200px;width:600px;height:600px;border-radius:50%;background:radial-gradient(circle,rgba(38,166,154,0.08),transparent 70%);pointer-events:none;animation:float 8s ease-in-out infinite}

/* Hero section */
.land-hero{max-width:1200px;margin:0 auto;padding:80px 32px 0;display:grid;grid-template-columns:1fr 1fr;gap:60px;align-items:center;position:relative;z-index:2}
@media(max-width:860px){.land-hero{grid-template-columns:1fr;gap:32px;padding:48px 20px 0;text-align:center}}

.land-hero-left{animation:fadeInUp 0.7s ease both}
.land-tag{display:inline-flex;align-items:center;gap:8px;font-size:11px;font-weight:700;letter-spacing:0.14em;color:var(--green);border:1px solid rgba(38,166,154,0.25);border-radius:100px;padding:7px 18px;margin-bottom:28px;text-transform:uppercase;background:rgba(38,166,154,0.06)}
.land-tag .dot{width:6px;height:6px;border-radius:50%;background:var(--green);animation:pulse 2s ease infinite}
.land-title{font-size:clamp(42px,6vw,72px);font-weight:900;line-height:1.0;letter-spacing:-0.04em;color:#fff;margin-bottom:24px}
.land-title .accent{background:linear-gradient(135deg,var(--green),#2dd4bf);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.land-desc{font-size:17px;color:var(--text2);line-height:1.7;max-width:480px;margin-bottom:36px}
@media(max-width:860px){.land-desc{margin:0 auto 36px}}
.land-cta{display:inline-flex;align-items:center;gap:12px;background:linear-gradient(135deg,var(--green),#2dd4bf);color:#fff;font-size:16px;font-weight:700;padding:16px 36px;border:none;border-radius:var(--radius);cursor:pointer;transition:all 0.3s;font-family:'Inter',sans-serif}
.land-cta:hover{transform:translateY(-2px);box-shadow:0 12px 32px rgba(38,166,154,0.4)}
/* ======== GET STARTED BUTTON ======== */
.gs-btn{position:relative;overflow:hidden;display:inline-flex;align-items:center;justify-content:center;height:48px;padding:0 32px;background:linear-gradient(135deg,var(--green),#2dd4bf);color:#fff;font-size:16px;font-weight:700;border:none;border-radius:12px;cursor:pointer;font-family:'Inter',sans-serif;transition:box-shadow 0.3s,transform 0.3s;min-width:180px}
.gs-btn:hover{box-shadow:0 12px 32px rgba(38,166,154,0.45);transform:translateY(-2px)}
.gs-btn:active{transform:translateY(0) scale(0.98)}
.gs-btn-label{margin-right:36px;transition:opacity 0.4s;white-space:nowrap;position:relative;z-index:1}
.gs-btn:hover .gs-btn-label{opacity:0}
.gs-btn-arrow{position:absolute;right:4px;top:4px;bottom:4px;border-radius:8px;background:rgba(255,255,255,0.18);display:grid;place-items:center;width:25%;transition:width 0.45s cubic-bezier(0.22,1,0.36,1);z-index:2;overflow:hidden}
.gs-btn:hover .gs-btn-arrow{width:calc(100% - 8px)}
.gs-btn:active .gs-btn-arrow{transform:scale(0.96)}
.land-stats{display:flex;gap:32px;margin-top:40px}
@media(max-width:860px){.land-stats{justify-content:center}}
.land-stat{display:flex;flex-direction:column}
.land-stat-num{font-size:28px;font-weight:800;color:#fff;font-family:'JetBrains Mono',monospace}
.land-stat-label{font-size:12px;color:var(--text3);font-weight:500}

/* Hero right - floating card */
.land-hero-right{position:relative;display:flex;justify-content:center;animation:fadeInUp 0.8s ease 0.2s both}
.land-card{width:100%;max-width:420px;background:var(--bg2);border:1px solid var(--border);border-radius:16px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,0.5);animation:float 6s ease-in-out infinite}
.land-card-header{padding:16px 20px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between}
.land-card-ticker{font-size:18px;font-weight:800;color:#fff;font-family:'JetBrains Mono',monospace}
.land-card-badge{font-size:10px;font-weight:700;letter-spacing:0.08em;padding:4px 10px;border-radius:100px;border:1px solid;text-transform:uppercase}
.land-card-chart{padding:20px;height:180px;display:flex;align-items:flex-end;gap:3px}
.land-bar{width:100%;border-radius:3px 3px 0 0;animation:candleGrow 0.8s ease both}
.land-card-footer{padding:14px 20px;border-top:1px solid var(--border);display:flex;justify-content:space-between;align-items:center}
.land-card-q{font-size:13px;color:var(--text2);font-weight:500}
.land-card-btns{display:flex;gap:6px}
.land-card-btn{padding:6px 14px;border-radius:6px;font-size:12px;font-weight:700;border:1px solid;cursor:default;font-family:'Inter',sans-serif}

/* Features grid */
.land-features{max-width:1200px;margin:0 auto;padding:80px 32px 0;position:relative;z-index:3}
@media(max-width:860px){.land-features{padding:48px 20px 0}}
.land-features-title{font-size:13px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:var(--text3);margin-bottom:24px;text-align:center}
.land-features-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
@media(max-width:860px){.land-features-grid{grid-template-columns:1fr}}
.land-feat{padding:28px 24px;background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius);transition:all 0.3s;animation:fadeInUp 0.6s ease both}
.land-feat:nth-child(1){animation-delay:0.1s}.land-feat:nth-child(2){animation-delay:0.2s}.land-feat:nth-child(3){animation-delay:0.3s}
.land-feat:nth-child(4){animation-delay:0.15s}.land-feat:nth-child(5){animation-delay:0.25s}.land-feat:nth-child(6){animation-delay:0.35s}
.land-feat:hover{border-color:var(--border2);transform:translateY(-4px);box-shadow:0 12px 32px rgba(0,0,0,0.3)}
.land-feat-icon{width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;margin-bottom:14px}
.land-feat-name{font-size:15px;font-weight:700;color:#fff;margin-bottom:6px}
.land-feat-desc{font-size:13px;color:var(--text2);line-height:1.6}

/* Indicators strip */
.land-indicators{max-width:1200px;margin:0 auto;padding:60px 32px;position:relative;z-index:2}
@media(max-width:860px){.land-indicators{padding:40px 20px}}
.land-ind-grid{display:flex;gap:16px;flex-wrap:wrap}
.land-ind{flex:1;min-width:200px;padding:20px;border-radius:var(--radius-sm);border:1px solid var(--border);background:var(--bg2);transition:all 0.3s}
.land-ind:hover{transform:translateY(-3px);box-shadow:0 8px 24px rgba(0,0,0,0.3)}
.land-ind strong{display:block;font-size:14px;margin-bottom:4px}
.land-ind span{font-size:12px;color:var(--text2)}

/* Bottom CTA */
.land-bottom{max-width:1200px;margin:0 auto;padding:0 32px 80px;text-align:center;position:relative;z-index:2}
@media(max-width:860px){.land-bottom{padding:0 20px 60px}}
.land-bottom-box{padding:48px 32px;background:var(--bg2);border:1px solid var(--border);border-radius:16px;position:relative;overflow:hidden}
.land-bottom-box::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at 50% 100%,rgba(38,166,154,0.06),transparent 60%);pointer-events:none}
.land-bottom h2{font-size:28px;font-weight:800;color:#fff;margin-bottom:10px;position:relative}
.land-bottom p{font-size:15px;color:var(--text2);margin-bottom:28px;position:relative}
.land-bottom .land-cta{position:relative}

/* ======== PLAY SCREEN (difficulty + start) ======== */
.play-screen{min-height:calc(100vh - 56px);padding:60px 20px 80px;position:relative;overflow:hidden}
.play-screen::before{content:'';position:absolute;top:0;left:0;right:0;height:500px;background:radial-gradient(ellipse at 50% 0%,rgba(38,166,154,0.08),transparent 60%);pointer-events:none}
.play-content{max-width:800px;margin:0 auto;position:relative;z-index:2}
.play-title{font-size:clamp(32px,5vw,48px);font-weight:900;color:#fff;margin-bottom:8px;letter-spacing:-0.03em;animation:fadeInUp 0.6s ease both}
.play-title .accent{background:linear-gradient(135deg,var(--green),#2dd4bf);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.play-sub{font-size:15px;color:var(--text2);margin-bottom:40px;animation:fadeInUp 0.6s ease 0.1s both}
.how-it-works{margin-bottom:40px;animation:fadeInUp 0.6s ease 0.2s both}
.how-it-works h2,.indicator-intro h2{font-size:13px;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;color:var(--text3);margin-bottom:16px}
.steps{display:flex;flex-direction:column;gap:12px}
.step{display:flex;align-items:flex-start;gap:16px;padding:16px 18px;background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius-sm);transition:all 0.3s;cursor:default}
.step:hover{border-color:var(--border2);transform:translateX(4px);background:var(--bg4)}
.step-num{font-size:11px;font-weight:700;color:var(--green);font-family:'JetBrains Mono',monospace;min-width:24px;padding-top:1px}
.step-text{display:flex;flex-direction:column;gap:3px}
.step-text strong{font-size:14px;color:var(--text)}
.step-text span{font-size:13px;color:var(--text2)}
.indicator-intro{margin-bottom:32px;animation:fadeInUp 0.6s ease 0.3s both}
.indicator-pills{display:flex;gap:12px;flex-wrap:wrap}
.ind-pill{flex:1;min-width:180px;padding:14px 16px;border-radius:var(--radius-sm);border:1px solid var(--border);background:var(--bg3);display:flex;flex-direction:column;gap:5px;transition:all 0.3s}
.ind-pill:hover{transform:translateY(-3px);box-shadow:0 8px 24px rgba(0,0,0,0.3)}
.ind-pill strong{font-size:13px;font-weight:700}
.ind-pill span{font-size:12px;color:var(--text2)}
.ind-pill.rsi strong{color:var(--purple)}
.ind-pill.rsi:hover{border-color:rgba(155,89,182,0.3)}
.ind-pill.macd strong{color:#26c6da}
.ind-pill.macd:hover{border-color:rgba(38,198,218,0.3)}
.ind-pill.sma strong{color:var(--orange)}
.ind-pill.sma:hover{border-color:rgba(255,152,0,0.3)}
.scoring-note{display:flex;align-items:flex-start;gap:10px;padding:14px 16px;background:rgba(59,130,246,0.07);border:1px solid rgba(59,130,246,0.2);border-radius:var(--radius-sm);font-size:13px;color:var(--text2);margin-bottom:32px;animation:fadeInUp 0.6s ease 0.4s both}
.difficulty-picker{margin-bottom:24px;animation:fadeInUp 0.5s ease 0.35s both}
.difficulty-picker h2{font-size:16px;font-weight:700;color:var(--text1);margin-bottom:12px}
.diff-options{display:flex;flex-wrap:wrap;gap:8px}
.diff-btn{display:flex;align-items:center;gap:8px;padding:10px 18px;border-radius:var(--radius-sm);border:1px solid var(--border);background:var(--bg2);color:var(--text2);font-size:14px;font-weight:600;cursor:pointer;transition:all 0.2s;font-family:Inter,sans-serif}
.diff-btn:hover{border-color:var(--border2);background:var(--bg3)}
.diff-btn.active{font-weight:700}
.diff-count{font-size:11px;font-weight:500;opacity:0.6;background:var(--bg3);border-radius:10px;padding:2px 7px}
.note-icon{font-size:16px;flex-shrink:0}
.start-btn{display:inline-flex;align-items:center;gap:10px;background:linear-gradient(135deg,var(--green),#2dd4bf);color:#fff;font-size:16px;font-weight:700;padding:16px 32px;border:none;border-radius:var(--radius);cursor:pointer;transition:all 0.3s;margin-bottom:20px;font-family:'Inter',sans-serif;animation:fadeInUp 0.6s ease 0.5s both}
.start-btn:hover{transform:translateY(-2px);box-shadow:0 12px 32px rgba(38,166,154,0.4)}
.play-footer{font-size:12px;color:var(--text3);animation:fadeInUp 0.5s ease 0.6s both}

/* ======== LIVE CHALLENGE ======== */
.live-screen{min-height:calc(100vh - 56px);padding:40px 20px 80px;position:relative}
.live-screen::before{content:'';position:absolute;top:0;left:0;right:0;height:400px;background:radial-gradient(ellipse at 50% 0%,rgba(239,83,80,0.06),transparent 60%);pointer-events:none}
.live-content{max-width:900px;margin:0 auto;position:relative;z-index:2}
.live-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:24px;flex-wrap:wrap;gap:12px}
.live-title{font-size:clamp(24px,4vw,36px);font-weight:900;color:#fff;letter-spacing:-0.03em}
.live-title .accent{background:linear-gradient(135deg,#ef5350,#ff9800);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.live-badge{display:inline-flex;align-items:center;gap:6px;font-size:11px;font-weight:700;letter-spacing:0.1em;color:#ef5350;border:1px solid rgba(239,83,80,0.3);border-radius:100px;padding:5px 14px;text-transform:uppercase;background:rgba(239,83,80,0.08)}
.live-dot{width:8px;height:8px;border-radius:50%;background:#ef5350;animation:pulse 1.5s ease infinite}

/* Ticker picker */
.live-picker{margin-bottom:28px;animation:fadeInUp 0.5s ease 0.1s both}
.live-picker-label{font-size:13px;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;color:var(--text3);margin-bottom:12px}
.live-picker-row{display:flex;gap:10px;align-items:stretch}
.live-search{flex:1;position:relative}
.live-search input{width:100%;padding:12px 16px;border-radius:var(--radius-sm);border:1px solid var(--border);background:var(--bg3);color:var(--text);font-size:15px;font-weight:600;font-family:'JetBrains Mono',monospace;outline:none;transition:border-color 0.2s;text-transform:uppercase}
.live-search input:focus{border-color:var(--accent)}
.live-search input::placeholder{color:var(--text3);text-transform:none;font-family:'Inter',sans-serif;font-weight:400}
.live-search-results{position:absolute;top:100%;left:0;right:0;background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius-sm);margin-top:4px;max-height:240px;overflow-y:auto;z-index:10;box-shadow:0 12px 32px rgba(0,0,0,0.5)}
.live-search-item{padding:10px 16px;cursor:pointer;display:flex;justify-content:space-between;align-items:center;transition:background 0.15s;border-bottom:1px solid var(--border)}
.live-search-item:last-child{border-bottom:none}
.live-search-item:hover{background:var(--bg3)}
.live-search-item strong{font-size:14px;color:#fff;font-family:'JetBrains Mono',monospace}
.live-search-item span{font-size:12px;color:var(--text3)}
.live-go-btn{padding:12px 24px;border-radius:var(--radius-sm);border:none;background:linear-gradient(135deg,#ef5350,#ff9800);color:#fff;font-size:14px;font-weight:700;cursor:pointer;transition:all 0.2s;font-family:'Inter',sans-serif;white-space:nowrap}
.live-go-btn:hover{transform:translateY(-1px);box-shadow:0 8px 20px rgba(239,83,80,0.3)}
.live-go-btn:disabled{opacity:0.5;cursor:default;transform:none;box-shadow:none}

/* Popular stocks */
.live-popular{display:flex;flex-wrap:wrap;gap:6px;margin-top:12px}
.live-pop-btn{padding:6px 14px;border-radius:20px;border:1px solid var(--border);background:var(--bg2);color:var(--text2);font-size:12px;font-weight:600;cursor:pointer;transition:all 0.2s;font-family:'JetBrains Mono',monospace}
.live-pop-btn:hover{border-color:var(--border2);background:var(--bg3);color:#fff}

/* How it works banner */
.live-how{padding:16px 20px;background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius);margin-bottom:28px;animation:fadeInUp 0.5s ease 0.2s both}
.live-how-title{font-size:13px;font-weight:700;color:var(--text);margin-bottom:8px}
.live-how-steps{display:flex;gap:24px;flex-wrap:wrap}
.live-how-step{display:flex;align-items:center;gap:8px;font-size:12px;color:var(--text2)}
.live-how-num{width:22px;height:22px;border-radius:50%;background:rgba(239,83,80,0.15);color:#ef5350;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;flex-shrink:0}

/* Loading state */
.live-loading{text-align:center;padding:60px 20px}
.live-loading-spinner{width:40px;height:40px;border:3px solid var(--border);border-top-color:var(--accent);border-radius:50%;animation:spin 0.8s linear infinite;margin:0 auto 16px}
.live-loading-text{font-size:14px;color:var(--text2)}

/* Scenario card */
.live-scenario{animation:fadeInUp 0.5s ease both}
.live-scenario-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;flex-wrap:wrap;gap:8px}
.live-ticker-display{display:flex;align-items:center;gap:12px}
.live-ticker-name{font-size:24px;font-weight:800;color:#fff;font-family:'JetBrains Mono',monospace}
.live-ticker-price{font-size:18px;font-weight:600;color:var(--text2)}
.live-ticker-time{font-size:13px;color:var(--text3)}

/* Live chart */
.live-chart-wrap{background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius);padding:16px;margin-bottom:20px}

/* Indicators display */
.live-indicators{display:flex;gap:10px;margin-bottom:20px;flex-wrap:wrap}
.live-ind-card{flex:1;min-width:180px;padding:14px 16px;background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius-sm)}
.live-ind-label{font-size:11px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:4px}
.live-ind-value{font-size:14px;font-weight:600;color:#fff;margin-bottom:2px}
.live-ind-desc{font-size:12px;color:var(--text2)}

/* Prediction buttons */
.live-predict{text-align:center;padding:24px;background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius);margin-bottom:20px}
.live-predict-q{font-size:16px;font-weight:700;color:#fff;margin-bottom:16px}
.live-predict-btns{display:flex;gap:12px;justify-content:center}
.live-predict-btn{padding:14px 36px;border-radius:var(--radius-sm);border:2px solid;font-size:16px;font-weight:700;cursor:pointer;transition:all 0.2s;font-family:'Inter',sans-serif;display:flex;align-items:center;gap:8px;background:transparent}
.live-predict-btn.up{border-color:var(--green);color:var(--green)}
.live-predict-btn.up:hover{background:rgba(38,166,154,0.15);transform:translateY(-2px)}
.live-predict-btn.down{border-color:var(--red);color:var(--red)}
.live-predict-btn.down:hover{background:rgba(239,83,80,0.15);transform:translateY(-2px)}

/* Result display */
.live-result{text-align:center;padding:32px;background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius);animation:fadeInScale 0.4s ease both}
.live-result.correct{border-color:rgba(38,166,154,0.4);background:linear-gradient(180deg,rgba(38,166,154,0.08),var(--bg2))}
.live-result.wrong{border-color:rgba(239,83,80,0.4);background:linear-gradient(180deg,rgba(239,83,80,0.08),var(--bg2))}
.live-result-icon{font-size:48px;margin-bottom:8px}
.live-result-text{font-size:20px;font-weight:800;margin-bottom:4px}
.live-result-detail{font-size:14px;color:var(--text2);margin-bottom:16px}
.live-result-price{display:flex;justify-content:center;gap:24px;margin-bottom:20px}
.live-result-price-item{display:flex;flex-direction:column;align-items:center}
.live-result-price-label{font-size:11px;color:var(--text3);text-transform:uppercase;letter-spacing:0.08em}
.live-result-price-val{font-size:20px;font-weight:700;font-family:'JetBrains Mono',monospace}
.live-again-btn{padding:12px 28px;border-radius:var(--radius-sm);border:none;background:linear-gradient(135deg,#ef5350,#ff9800);color:#fff;font-size:14px;font-weight:700;cursor:pointer;transition:all 0.2s;font-family:'Inter',sans-serif}
.live-again-btn:hover{transform:translateY(-1px);box-shadow:0 8px 20px rgba(239,83,80,0.3)}

/* Live stats bar */
.live-stats-bar{display:flex;gap:16px;margin-bottom:24px;flex-wrap:wrap}
.live-stat-item{padding:12px 18px;background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius-sm);display:flex;flex-direction:column;align-items:center;min-width:80px}
.live-stat-num{font-size:18px;font-weight:800;font-family:'JetBrains Mono',monospace}
.live-stat-label{font-size:11px;color:var(--text3);text-transform:uppercase;letter-spacing:0.06em}

/* ======== GAME ======== */
.game-screen{min-height:calc(100vh - 56px);display:flex;flex-direction:column}
.game-subheader{display:flex;align-items:center;justify-content:space-between;padding:12px 24px;background:var(--bg2);border-bottom:1px solid var(--border)}
.scenario-progress{display:flex;align-items:center;gap:10px}
.progress-label{font-size:12px;color:var(--text3);font-weight:500}
.progress-dots{display:flex;gap:5px}
.progress-dot{width:8px;height:8px;border-radius:50%;background:var(--border2);transition:all 0.3s}
.progress-dot.done{background:var(--green);opacity:0.5}
.progress-dot.current{background:var(--green);box-shadow:0 0 8px var(--green)}
.progress-fraction{font-size:12px;color:var(--text3);font-family:'JetBrains Mono',monospace}
.score-display{display:flex;flex-direction:column;align-items:flex-end}
.score-label{font-size:10px;color:var(--text3);text-transform:uppercase;letter-spacing:0.08em}
.score-value{font-size:18px;font-weight:800;color:var(--green);font-family:'JetBrains Mono',monospace}
.game-body{flex:1;max-width:900px;width:100%;margin:0 auto;padding:24px 20px 40px;display:flex;flex-direction:column;gap:18px}
.scenario-meta{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;animation:fadeInUp 0.5s ease both}
.meta-left{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
.ticker{font-size:22px;font-weight:800;color:#fff;font-family:'JetBrains Mono',monospace}
.stock-name{font-size:15px;color:var(--text2)}
.stock-date{font-size:13px;color:var(--text3)}
.difficulty-badge{font-size:11px;font-weight:700;padding:4px 12px;border-radius:100px;border:1px solid;text-transform:uppercase;letter-spacing:0.06em}
.question-box{background:var(--bg3);border:1px solid var(--border);border-left:3px solid var(--accent);border-radius:var(--radius-sm);padding:14px 18px;font-size:15px;color:var(--text);line-height:1.6;animation:fadeInUp 0.5s ease 0.1s both}
.chart-container{border-radius:var(--radius);overflow:hidden;animation:fadeInScale 0.6s ease 0.2s both}
.decision-section{display:flex;flex-direction:column;gap:14px;animation:fadeInUp 0.5s ease 0.3s both}
.decision-label{font-size:13px;font-weight:600;color:var(--text2);text-transform:uppercase;letter-spacing:0.08em}
.decision-buttons{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.decision-btn{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;padding:20px 16px;background:var(--bg3);border:2px solid var(--border);border-radius:var(--radius);cursor:pointer;transition:all 0.25s;color:var(--text2);font-family:'Inter',sans-serif}
.decision-btn:hover:not(:disabled){transform:translateY(-3px)}
.decision-btn.buy-btn:hover:not(:disabled),.decision-btn.buy-btn.selected{background:rgba(38,166,154,0.1);border-color:var(--green);color:var(--green);box-shadow:0 6px 24px rgba(38,166,154,0.25)}
.decision-btn.sell-btn:hover:not(:disabled),.decision-btn.sell-btn.selected{background:rgba(239,83,80,0.1);border-color:var(--red);color:var(--red);box-shadow:0 6px 24px rgba(239,83,80,0.25)}
.decision-btn:disabled{opacity:0.5;cursor:default}
.btn-arrow{font-size:22px}
.btn-main{font-size:20px;font-weight:800;letter-spacing:0.05em}
.btn-sub{font-size:12px;opacity:0.8}

/* Reasoning textarea */
.reasoning-section{animation:fadeInUp 0.5s ease 0.35s both}
.reasoning-label{font-size:13px;font-weight:600;color:var(--text2);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px}
.reasoning-textarea{width:100%;min-height:80px;padding:14px;border-radius:var(--radius-sm);border:1px solid var(--border);background:var(--bg3);color:var(--text);font-size:14px;font-family:'Inter',sans-serif;resize:vertical;outline:none;transition:border-color 0.2s;line-height:1.5}
.reasoning-textarea:focus{border-color:var(--accent)}
.reasoning-textarea::placeholder{color:var(--text3)}
.reasoning-hint{font-size:12px;color:var(--text3);margin-top:6px}

.confirm-btn{width:100%;padding:16px;background:var(--border2);border:1px solid var(--border);border-radius:var(--radius);font-size:15px;font-weight:700;color:var(--text3);cursor:default;transition:all 0.25s;font-family:'Inter',sans-serif}
.confirm-btn.active{background:linear-gradient(135deg,var(--accent),#2563eb);border-color:transparent;color:#fff;cursor:pointer}
.confirm-btn.active:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(59,130,246,0.3)}
.confirm-btn.submitting{opacity:0.7}

/* ======== INDICATOR READINGS (shown post-prediction) ======== */
.indicator-readings{background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius);padding:14px 16px;animation:fadeInUp 0.5s ease both}
.readings-header{display:flex;align-items:center;gap:7px;font-size:12px;font-weight:600;color:var(--purple);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px}
.readings-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px}
.reading-card{background:var(--bg4);border:1px solid var(--border2);border-radius:var(--radius-sm);padding:11px 13px;transition:all 0.3s}
.reading-card:hover{border-color:var(--border);transform:translateY(-2px)}
.reading-name{font-size:11px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.07em;margin-bottom:5px;font-family:'JetBrains Mono',monospace}
.reading-note{font-size:13px;color:var(--text);line-height:1.4}

/* ======== RESULT ======== */
.result-screen{min-height:calc(100vh - 56px);background:var(--bg);padding:24px 20px 60px}
.result-content{max-width:960px;margin:0 auto;display:flex;flex-direction:column;gap:20px}
.verdict-banner{display:flex;align-items:center;gap:20px;padding:20px 24px;border-radius:var(--radius);border:1px solid;animation:fadeInScale 0.5s ease both}
.verdict-banner.correct{background:rgba(38,166,154,0.08);border-color:rgba(38,166,154,0.3)}
.verdict-banner.incorrect{background:rgba(239,83,80,0.08);border-color:rgba(239,83,80,0.3)}
.verdict-icon{font-size:32px;font-weight:800;line-height:1}
.verdict-banner.correct .verdict-icon{color:var(--green)}
.verdict-banner.incorrect .verdict-icon{color:var(--red)}
.verdict-text{flex:1}
.verdict-main{font-size:24px;font-weight:800;color:#fff}
.verdict-sub{font-size:14px;color:var(--text2);margin-top:3px}
.verdict-points{display:flex;flex-direction:column;align-items:center}
.pts-num{font-size:32px;font-weight:800;color:var(--green);font-family:'JetBrains Mono',monospace}
.pts-label{font-size:12px;color:var(--text3);text-transform:uppercase}

/* AI Reasoning feedback */
.ai-feedback-card{background:rgba(155,89,182,0.06);border:1px solid rgba(155,89,182,0.2);border-radius:var(--radius);padding:18px;animation:fadeInUp 0.5s ease 0.1s both}
.ai-feedback-header{display:flex;align-items:center;gap:8px;font-size:12px;font-weight:700;color:var(--purple);text-transform:uppercase;letter-spacing:0.07em;margin-bottom:10px}
.ai-feedback-score{font-size:28px;font-weight:800;color:var(--purple);font-family:'JetBrains Mono',monospace}
.ai-feedback-text{font-size:14px;color:var(--text);line-height:1.6;margin-top:8px}

.result-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;animation:fadeInUp 0.5s ease 0.15s both}
@media(max-width:720px){.result-grid{grid-template-columns:1fr}}
.result-left,.result-right{display:flex;flex-direction:column;gap:14px}
.quality-card{background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius);padding:18px}
.quality-top{display:flex;gap:10px;margin-bottom:12px;flex-wrap:wrap}
.quality-badge,.signal-tag{font-size:11px;font-weight:700;padding:4px 12px;border-radius:100px;border:1px solid;text-transform:uppercase;letter-spacing:0.06em}
.quality-feedback{font-size:14px;color:var(--text);line-height:1.6;margin-bottom:8px}
.signal-desc{font-size:12px;font-weight:500}
.explanation-card{background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius);padding:18px;flex:1}
.expl-header{margin-bottom:10px}
.expl-verdict{font-size:13px;font-weight:700;color:var(--accent);text-transform:uppercase;letter-spacing:0.06em}
.expl-summary{font-size:14px;font-weight:600;color:var(--text);margin-bottom:12px;line-height:1.6}
.expl-details{font-size:13px;color:var(--text2);line-height:1.7}
.breakdown-card{background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius);padding:18px}
.breakdown-title{font-size:13px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:14px}
.breakdown-item{padding:12px 14px;border-radius:var(--radius-sm);margin-bottom:8px;border:1px solid var(--border2);transition:all 0.3s}
.breakdown-item:hover{transform:translateX(4px)}
.breakdown-item.bullish{background:rgba(38,166,154,0.06);border-color:rgba(38,166,154,0.2)}
.breakdown-item.bearish{background:rgba(239,83,80,0.06);border-color:rgba(239,83,80,0.2)}
.breakdown-item.neutral{background:rgba(107,114,128,0.06)}
.breakdown-indicator{display:flex;align-items:center;gap:8px;margin-bottom:6px}
.signal-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.signal-dot.bullish{background:var(--green);box-shadow:0 0 5px var(--green)}
.signal-dot.bearish{background:var(--red);box-shadow:0 0 5px var(--red)}
.signal-dot.neutral{background:var(--text3)}
.breakdown-indicator strong{font-size:13px;color:var(--text)}
.breakdown-item p{font-size:13px;color:var(--text2);line-height:1.55;padding-left:16px}
.outcome-card{background:rgba(38,166,154,0.06);border:1px solid rgba(38,166,154,0.2);border-radius:var(--radius);padding:16px 18px}
.outcome-header{display:flex;align-items:center;gap:8px;font-size:12px;font-weight:700;color:var(--green);text-transform:uppercase;letter-spacing:0.07em;margin-bottom:8px}
.outcome-text{font-size:14px;color:var(--text);line-height:1.6}
.lesson-card{background:rgba(59,130,246,0.06);border:1px solid rgba(59,130,246,0.2);border-radius:var(--radius);padding:16px 18px}
.lesson-header{display:flex;align-items:center;gap:8px;font-size:12px;font-weight:700;color:var(--accent);text-transform:uppercase;letter-spacing:0.07em;margin-bottom:8px}
.lesson-text{font-size:14px;color:var(--text);line-height:1.6}
.result-footer{display:flex;align-items:center;gap:20px;flex-wrap:wrap;animation:fadeInUp 0.5s ease 0.3s both}
.next-btn{display:inline-flex;align-items:center;gap:10px;background:linear-gradient(135deg,var(--accent),#2563eb);color:#fff;font-size:15px;font-weight:700;padding:14px 28px;border:none;border-radius:var(--radius);cursor:pointer;transition:all 0.3s;font-family:'Inter',sans-serif}
.next-btn:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(59,130,246,0.4)}
.result-progress{font-size:13px;color:var(--text3)}

/* ======== SUMMARY ======== */
.summary-screen{min-height:calc(100vh - 56px);background:var(--bg);padding:40px 20px 80px}
.summary-content{max-width:760px;margin:0 auto;display:flex;flex-direction:column;gap:24px}
.summary-title{font-size:clamp(28px,5vw,44px);font-weight:800;color:#fff;letter-spacing:-0.02em;animation:fadeInUp 0.6s ease both}
.score-card{display:flex;align-items:center;gap:30px;background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius);padding:28px 32px;flex-wrap:wrap;animation:fadeInScale 0.6s ease 0.1s both}
.score-circle{position:relative;width:120px;height:120px;flex-shrink:0}
.score-ring{width:100%;height:100%}
.score-inner{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center}
.score-big{font-size:26px;font-weight:800;color:#fff;font-family:'JetBrains Mono',monospace}
.score-pts{font-size:12px;color:var(--text3)}
.rank-info{flex:1}
.rank-badge{display:inline-block;font-size:14px;font-weight:700;padding:6px 18px;border-radius:100px;border:1px solid;margin-bottom:10px}
.rank-desc{font-size:14px;color:var(--text2);line-height:1.6}
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;animation:fadeInUp 0.5s ease 0.2s both}
.stat-card{background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius);padding:18px 16px;display:flex;flex-direction:column;align-items:center;gap:4px;text-align:center;transition:all 0.3s}
.stat-card:hover{transform:translateY(-4px);border-color:var(--border2)}
.stat-num{font-size:32px;font-weight:800;font-family:'JetBrains Mono',monospace}
.stat-label{font-size:13px;color:var(--text2);font-weight:600}
.stat-sublabel{font-size:11px;color:var(--text3)}
.scenario-review{background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius);padding:20px;animation:fadeInUp 0.5s ease 0.3s both}
.review-title{font-size:13px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:14px}
.review-list{display:flex;flex-direction:column;gap:8px}
.review-item{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;border-radius:var(--radius-sm);border:1px solid var(--border2);gap:12px;transition:all 0.2s}
.review-item:hover{background:var(--bg4)}
.review-item.review-correct{background:rgba(38,166,154,0.05)}
.review-item.review-wrong{background:rgba(239,83,80,0.04)}
.review-left{display:flex;align-items:center;gap:12px}
.review-icon{width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:800;flex-shrink:0}
.review-icon.correct{background:rgba(38,166,154,0.2);color:var(--green)}
.review-icon.wrong{background:rgba(239,83,80,0.2);color:var(--red)}
.review-info{display:flex;flex-direction:column}
.review-info strong{font-size:13px;color:var(--text)}
.review-info span{font-size:12px;color:var(--text3)}
.review-badge{font-size:11px;font-weight:700;padding:3px 10px;border-radius:100px;border:1px solid;text-transform:uppercase;letter-spacing:0.05em}
.review-pts{font-size:14px;font-weight:700;color:var(--green);font-family:'JetBrains Mono',monospace;min-width:55px;text-align:right}
.takeaways{background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius);padding:20px;animation:fadeInUp 0.5s ease 0.4s both}
.takeaways-title{font-size:13px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:14px}
.takeaway-list{display:flex;flex-direction:column;gap:10px}
.takeaway{display:flex;align-items:flex-start;gap:12px;font-size:14px;color:var(--text2);line-height:1.5}
.t-icon{font-size:16px;flex-shrink:0;margin-top:1px}
.takeaway strong{color:var(--text)}
.restart-btn{display:inline-flex;align-items:center;gap:10px;background:var(--bg4);border:1px solid var(--border2);color:var(--text);font-size:15px;font-weight:700;padding:14px 28px;border-radius:var(--radius);cursor:pointer;transition:all 0.3s;font-family:'Inter',sans-serif;animation:fadeInUp 0.5s ease 0.5s both}
.restart-btn:hover{background:var(--border2);transform:translateY(-2px)}

/* ======== STATISTICS PAGE ======== */
.stats-screen{min-height:calc(100vh - 56px);padding:40px 20px 80px}
.stats-content{max-width:800px;margin:0 auto}
.stats-title{font-size:28px;font-weight:800;color:#fff;margin-bottom:8px;animation:fadeInUp 0.5s ease both}
.stats-sub{font-size:14px;color:var(--text2);margin-bottom:32px;animation:fadeInUp 0.5s ease 0.1s both}
.stats-overview{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:14px;margin-bottom:32px;animation:fadeInUp 0.5s ease 0.2s both}
.stats-overview .stat-card{border:1px solid var(--border);animation:borderGlow 3s ease-in-out infinite}
.stats-history{background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius);padding:20px;animation:fadeInUp 0.5s ease 0.3s both}
.stats-history-title{font-size:13px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:16px}
.stats-empty{text-align:center;padding:40px 20px;color:var(--text3)}
.stats-empty p{margin-bottom:16px;font-size:15px}
.stats-play-btn{background:var(--green);color:#fff;border:none;padding:12px 24px;border-radius:var(--radius-sm);font-size:14px;font-weight:700;cursor:pointer;font-family:'Inter',sans-serif;transition:all 0.2s}
.stats-play-btn:hover{background:#2bb5a8}
.stats-session{padding:14px;border-radius:var(--radius-sm);border:1px solid var(--border2);margin-bottom:10px;background:var(--bg4);transition:all 0.2s}
.stats-session:hover{border-color:var(--border)}
.stats-session-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}
.stats-session-date{font-size:13px;color:var(--text2);font-weight:600}
.stats-session-score{font-size:15px;font-weight:800;color:var(--green);font-family:'JetBrains Mono',monospace}
.stats-session-details{display:flex;gap:16px;font-size:12px;color:var(--text3)}

/* ======== SETTINGS / API KEY ======== */
.settings-section{background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius);padding:20px;margin-top:24px;animation:fadeInUp 0.5s ease 0.4s both}
.settings-title{font-size:13px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:14px}
.settings-row{display:flex;align-items:center;gap:12px;margin-bottom:12px}
.settings-row label{font-size:13px;color:var(--text2);min-width:120px}
.settings-input{flex:1;padding:10px 12px;border-radius:var(--radius-sm);border:1px solid var(--border);background:var(--bg4);color:var(--text);font-size:13px;font-family:'JetBrains Mono',monospace;outline:none}
.settings-input:focus{border-color:var(--accent)}
.settings-save{padding:8px 16px;border-radius:var(--radius-sm);background:var(--green);color:#fff;border:none;font-size:13px;font-weight:600;cursor:pointer;font-family:'Inter',sans-serif;transition:all 0.2s}
.settings-save:hover{background:#2bb5a8}
.settings-note{font-size:12px;color:var(--text3);margin-top:8px}

/* ======== ACHIEVEMENTS ======== */
.achievements-section{background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius);padding:20px;margin-bottom:24px;animation:fadeInUp 0.5s ease 0.35s both}
.achievements-title{font-size:13px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:16px;display:flex;align-items:center;gap:8px}
.achievements-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:10px}
.badge-card{padding:14px 16px;border-radius:var(--radius-sm);border:1px solid var(--border2);display:flex;align-items:flex-start;gap:12px;transition:all 0.3s;background:var(--bg4)}
.badge-card.unlocked{border-color:rgba(38,166,154,0.3);background:rgba(38,166,154,0.06)}
.badge-card.locked{opacity:0.5}
.badge-card:hover{transform:translateY(-2px)}
.badge-icon{font-size:28px;flex-shrink:0;line-height:1}
.badge-info{display:flex;flex-direction:column;gap:2px}
.badge-name{font-size:13px;font-weight:700;color:#fff}
.badge-desc{font-size:11px;color:var(--text2);line-height:1.4}
.badge-date{font-size:10px;color:var(--green);font-weight:600;margin-top:2px}
.badge-progress{font-size:10px;color:var(--text3);margin-top:2px}
.badge-progress-bar{width:100%;height:4px;background:var(--border);border-radius:2px;margin-top:3px;overflow:hidden}
.badge-progress-fill{height:100%;background:var(--green);border-radius:2px;transition:width 0.4s ease}

/* ======== LEADERBOARD ======== */
.leaderboard-section{background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius);padding:20px;margin-bottom:24px;animation:fadeInUp 0.5s ease 0.4s both}
.leaderboard-title{font-size:13px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:16px;display:flex;align-items:center;gap:8px}
.lb-tabs{display:flex;gap:4px;margin-bottom:16px}
.lb-tab{padding:6px 14px;border-radius:6px;font-size:12px;font-weight:600;color:var(--text3);cursor:pointer;transition:all 0.2s;border:none;background:transparent;font-family:'Inter',sans-serif}
.lb-tab:hover{color:var(--text);background:var(--bg4)}
.lb-tab.active{color:var(--green);background:rgba(38,166,154,0.1)}
.lb-table{width:100%;border-collapse:collapse}
.lb-table th{font-size:11px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.06em;text-align:left;padding:8px 10px;border-bottom:1px solid var(--border)}
.lb-table td{font-size:13px;padding:10px;border-bottom:1px solid var(--border2)}
.lb-rank{font-weight:800;font-family:'JetBrains Mono',monospace;width:32px}
.lb-rank.gold{color:#ffd700}.lb-rank.silver{color:#c0c0c0}.lb-rank.bronze{color:#cd7f32}
.lb-name{font-weight:600;color:var(--text)}
.lb-you{color:var(--green);font-weight:700}
.lb-score{font-weight:700;font-family:'JetBrains Mono',monospace;color:var(--accent)}
.lb-acc{font-weight:600;color:var(--text2)}
.lb-empty{text-align:center;padding:24px;color:var(--text3);font-size:13px}

/* ======== MARKET STATUS BANNER ======== */
.market-status{padding:10px 16px;border-radius:var(--radius-sm);margin-bottom:16px;display:flex;align-items:center;gap:10px;font-size:13px;font-weight:500;animation:fadeInUp 0.3s ease both}
.market-status.open{background:rgba(38,166,154,0.08);border:1px solid rgba(38,166,154,0.2);color:var(--green)}
.market-status.closed{background:rgba(255,152,0,0.08);border:1px solid rgba(255,152,0,0.2);color:var(--orange)}
.market-status-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.market-status.open .market-status-dot{background:var(--green);animation:pulse 1.5s ease infinite}
.market-status.closed .market-status-dot{background:var(--orange)}

/* ======== BADGE NOTIFICATION TOAST ======== */
.badge-toast{position:fixed;top:72px;right:24px;z-index:300;background:var(--bg2);border:1px solid rgba(38,166,154,0.5);border-radius:16px;padding:16px 20px 16px 16px;display:flex;align-items:center;gap:14px;box-shadow:0 8px 40px rgba(0,0,0,0.6),0 0 0 1px rgba(38,166,154,0.15);max-width:320px;animation:toastSlideIn 0.5s cubic-bezier(0.22,1,0.36,1) both}
.badge-toast.exit{animation:toastSlideOut 0.4s ease forwards}
@keyframes toastSlideIn{from{opacity:0;transform:translateX(140%)}to{opacity:1;transform:translateX(0)}}
@keyframes toastSlideOut{to{opacity:0;transform:translateX(140%)}}
.badge-toast-icon{font-size:38px;flex-shrink:0;animation:badgeBounce 0.7s cubic-bezier(0.22,1,0.36,1) 0.1s both}
@keyframes badgeBounce{0%{transform:scale(0) rotate(-30deg)}65%{transform:scale(1.25) rotate(8deg)}100%{transform:scale(1) rotate(0deg)}}
.badge-toast-text{display:flex;flex-direction:column;gap:3px;flex:1;min-width:0}
.badge-toast-label{font-size:10px;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:var(--green);margin-bottom:1px}
.badge-toast-name{font-size:15px;font-weight:800;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.badge-toast-desc{font-size:12px;color:var(--text2);line-height:1.4}
.badge-toast-close{background:none;border:none;color:var(--text3);font-size:16px;cursor:pointer;font-family:'Inter',sans-serif;line-height:1;padding:2px;align-self:flex-start;flex-shrink:0;transition:color 0.2s}.badge-toast-close:hover{color:var(--text)}
/* ======== SOUND TOGGLE ======== */
.sound-toggle{display:flex;align-items:center;gap:5px;padding:5px 10px;border-radius:7px;border:1px solid var(--border);background:var(--bg3);cursor:pointer;font-size:12px;font-weight:600;color:var(--text3);transition:all 0.2s;font-family:'Inter',sans-serif;user-select:none}
.sound-toggle:hover{border-color:var(--border2);color:var(--text)}
.sound-toggle.on{border-color:rgba(38,166,154,0.35);color:var(--green);background:rgba(38,166,154,0.08)}
/* ======== DIFFICULTY MULTIPLIER BADGE ======== */
.diff-mult-badge{display:inline-flex;align-items:center;gap:4px;font-size:11px;font-weight:700;padding:3px 9px;border-radius:100px;border:1px solid rgba(59,130,246,0.35);background:rgba(59,130,246,0.08);color:var(--accent);margin-left:8px}
/* ======== FRIEND LEADERBOARD ======== */
.friend-section{background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius);padding:20px;margin-bottom:20px;animation:fadeInUp 0.4s ease both}
.friend-title{font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:var(--text3);margin-bottom:14px;display:flex;align-items:center;gap:8px}
.friend-code-display{font-family:'JetBrains Mono',monospace;font-size:20px;font-weight:700;letter-spacing:0.22em;color:var(--green);background:rgba(38,166,154,0.08);border:1px solid rgba(38,166,154,0.28);border-radius:10px;padding:10px 20px;display:inline-block}
.friend-actions{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:10px}
.friend-copy-btn,.friend-gen-btn{padding:7px 14px;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;transition:all 0.2s;font-family:'Inter',sans-serif;border:1px solid var(--border2);background:var(--bg4);color:var(--text)}
.friend-copy-btn:hover{border-color:rgba(38,166,154,0.5);color:var(--green)}
.friend-gen-btn:hover{border-color:rgba(59,130,246,0.5);color:var(--accent)}
.friend-join-row{display:flex;gap:8px;margin-top:12px}
.friend-join-input{flex:1;padding:9px 12px;border-radius:8px;border:1px solid var(--border);background:var(--bg4);color:var(--text);font-size:14px;font-family:'JetBrains Mono',monospace;letter-spacing:0.14em;text-transform:uppercase;outline:none;transition:border-color 0.2s;min-width:0}
.friend-join-input:focus{border-color:var(--accent)}
.friend-join-input::placeholder{text-transform:none;font-family:'Inter',sans-serif;font-weight:400;letter-spacing:0}
.friend-join-btn{padding:9px 18px;border-radius:8px;border:none;background:var(--accent);color:#fff;font-size:13px;font-weight:700;cursor:pointer;font-family:'Inter',sans-serif;transition:background 0.2s}
.friend-join-btn:hover{background:#2563eb}
.friend-lb-list{display:flex;flex-direction:column;gap:6px;margin-top:14px}
.friend-lb-item{display:flex;align-items:center;gap:10px;padding:9px 12px;background:var(--bg4);border-radius:var(--radius-sm);border:1px solid var(--border)}
.friend-lb-item.me{border-color:rgba(38,166,154,0.35);background:rgba(38,166,154,0.05)}
.friend-lb-rank{font-size:12px;font-weight:700;color:var(--text3);min-width:22px;font-family:'JetBrains Mono',monospace}
.friend-lb-name{flex:1;font-size:13px;font-weight:600;color:var(--text)}
.friend-lb-score{font-size:13px;font-weight:700;color:var(--green);font-family:'JetBrains Mono',monospace}
/* ======== MARKET NEWS ======== */
.live-news{margin-top:20px;animation:fadeInUp 0.4s ease 0.1s both}
.live-news-header{font-size:11px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--text3);margin-bottom:10px;display:flex;align-items:center;gap:8px}
.live-news-list{display:flex;flex-direction:column;gap:8px}
.live-news-item{padding:10px 14px;background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius-sm);transition:all 0.2s;cursor:pointer}
.live-news-item:hover{border-color:var(--border2);background:var(--bg3)}.live-news-headline{font-size:13px;color:var(--text);line-height:1.5;margin-bottom:3px}
.live-news-source{font-size:11px;color:var(--text3)}

/* ======== ADMIN PANEL ======== */
.admin-overlay{position:fixed;inset:0;z-index:500;background:rgba(0,0,0,0.8);backdrop-filter:blur(8px);display:flex;align-items:center;justify-content:center;animation:fadeIn 0.2s ease}
.admin-modal{background:var(--bg2);border:1px solid rgba(239,83,80,0.4);border-radius:20px;padding:32px;max-width:680px;width:92%;max-height:85vh;display:flex;flex-direction:column;gap:0;animation:fadeInScale 0.3s cubic-bezier(0.22,1,0.36,1)}
.admin-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;gap:12px;flex-shrink:0}
.admin-title{font-size:18px;font-weight:800;color:'#fff';display:flex;align-items:center;gap:10px}
.admin-badge{font-size:10px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;padding:3px 10px;border-radius:100px;background:rgba(239,83,80,0.12);border:1px solid rgba(239,83,80,0.35);color:var(--red)}
.admin-close{background:none;border:none;color:var(--text3);font-size:20px;cursor:pointer;font-family:'Inter',sans-serif;line-height:1;padding:4px;transition:color 0.2s}.admin-close:hover{color:var(--red)}
.admin-search{padding:9px 14px;border-radius:8px;border:1px solid var(--border);background:var(--bg3);color:var(--text);font-size:13px;font-family:'Inter',sans-serif;outline:none;transition:border-color 0.2s;width:100%;margin-bottom:12px;flex-shrink:0}.admin-search:focus{border-color:var(--red)}
.admin-list{display:flex;flex-direction:column;gap:6px;overflow-y:auto;flex:1;padding-right:4px}
.admin-list::-webkit-scrollbar{width:4px}.admin-list::-webkit-scrollbar-track{background:transparent}.admin-list::-webkit-scrollbar-thumb{background:var(--border2);border-radius:4px}
.admin-entry{display:flex;align-items:center;gap:12px;padding:10px 14px;background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius-sm);transition:all 0.2s}
.admin-entry:hover{border-color:rgba(239,83,80,0.25);background:var(--bg4)}
.admin-entry-info{flex:1;min-width:0}
.admin-entry-name{font-size:14px;font-weight:700;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.admin-entry-meta{font-size:11px;color:var(--text3);margin-top:1px}
.admin-del-btn{padding:5px 12px;border-radius:6px;border:1px solid rgba(239,83,80,0.35);background:rgba(239,83,80,0.08);color:var(--red);font-size:12px;font-weight:700;cursor:pointer;transition:all 0.2s;font-family:'Inter',sans-serif;flex-shrink:0}
.admin-del-btn:hover{background:rgba(239,83,80,0.2);border-color:var(--red)}
.admin-del-btn.deleted{border-color:var(--border);color:var(--text3);background:transparent;cursor:default;opacity:0.5}
.admin-stats{font-size:12px;color:var(--text3);margin-top:10px;text-align:right;flex-shrink:0}
/* admin trigger */
.admin-trigger{font-size:11px;color:var(--text3);cursor:pointer;user-select:none;margin-top:16px;text-align:center;opacity:0.4;transition:opacity 0.2s;display:inline-flex;align-items:center;gap:5px;font-family:'Inter',sans-serif}
.admin-trigger:hover{opacity:1}

/* ======== RESPONSIVE ======== */
@media(max-width:640px){
  .nav-tabs{display:none}
  .nav-bar{padding:0 16px}
  .intro-glass-card{padding:20px 24px}
  .intro-features{flex-direction:column;gap:8px}
  .game-body{padding:16px 12px 32px}
  .result-grid{grid-template-columns:1fr}
  .achievements-grid{grid-template-columns:1fr}
}
</style>
</head>
<body>
<div id="root"></div>

<script>
// REAL HISTORICAL DATA
const REAL_DATA = ''' + real_data + r''';
const DISPLAY_CANDLES = ''' + str(DISPLAY_CANDLES) + r''';
</script>

<script>
// ======== FIREBASE INIT ========
// Replace these with YOUR Firebase project config (see setup instructions)
const FIREBASE_CONFIG = {
  apiKey: "AIzaSyCuHLqJEcKfshFjW73VgkqkRKO9UPxnu9U",
  authDomain: "market-mastery-4022a.firebaseapp.com",
  projectId: "market-mastery-4022a",
  storageBucket: "market-mastery-4022a.firebasestorage.app",
  messagingSenderId: "970969419640",
  appId: "1:970969419640:web:00a9ea485c758c051cc28d"
};

let db = null;
let firebaseReady = false;
try {
  if(FIREBASE_CONFIG.projectId !== "YOUR_PROJECT_ID" && typeof firebase !== 'undefined') {
    firebase.initializeApp(FIREBASE_CONFIG);
    db = firebase.firestore();
    firebaseReady = true;
    console.log("Firebase connected — global leaderboard active");
  } else {
    console.log("Firebase not configured — using local leaderboard. See setup instructions.");
  }
} catch(e) {
  console.log("Firebase init failed, using local leaderboard:", e.message);
}
</script>

<script type="text/babel">
const {useState,useMemo,useEffect,useCallback,useRef,createContext,useContext} = React;

/* ======== LOCAL PROFILE (no backend needed) ======== */
const AuthContext = createContext({user:null,setProfile:()=>{},logout:()=>{}});

function AuthProvider({children}) {
  const [user,setUser] = useState(()=>{
    try { return JSON.parse(localStorage.getItem('mm_user')||'null'); } catch(e){return null;}
  });

  const setProfile = (name) => {
    const u = {uid:'local_'+name.toLowerCase().replace(/\s+/g,'_'), name};
    setUser(u);
    localStorage.setItem('mm_user', JSON.stringify(u));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('mm_user');
  };

  return <AuthContext.Provider value={{user,setProfile,logout}}>{children}</AuthContext.Provider>;
}

function useAuth() { return useContext(AuthContext); }

/* ======== DATA PERSISTENCE (localStorage only) ======== */
// Save a completed game session (called at end of all scenarios in a run)
function saveGameSession(userId, sessionData) {
  const key = `mm_sessions_${userId}`;
  const existing = JSON.parse(localStorage.getItem(key) || '[]');
  existing.push({...sessionData, date: new Date().toISOString()});
  localStorage.setItem(key, JSON.stringify(existing));
}

// Save individual scenario result immediately (for mid-game stats tracking)
function saveScenarioResult(userId, scenarioId, result) {
  const key = `mm_results_${userId}`;
  const existing = JSON.parse(localStorage.getItem(key) || '{}');
  existing[scenarioId] = {...result, date: new Date().toISOString()};
  localStorage.setItem(key, JSON.stringify(existing));
}

// Get all individual scenario results
function getScenarioResults(userId) {
  return JSON.parse(localStorage.getItem(`mm_results_${userId}`) || '{}');
}

// Get completed scenario IDs
function getCompletedScenarioIds(userId) {
  const results = getScenarioResults(userId);
  return Object.keys(results).map(Number);
}

// Get next incomplete scenario index within a filtered set
function getNextScenarioIndex(userId, filteredScenarios) {
  const completed = getCompletedScenarioIds(userId);
  for(let i=0;i<filteredScenarios.length;i++) {
    if(!completed.includes(filteredScenarios[i].id)) return i;
  }
  return 0; // all done, restart from beginning
}

function getGameSessions(userId) {
  return JSON.parse(localStorage.getItem(`mm_sessions_${userId}`) || '[]');
}

function getAllStats(userId) {
  const sessions = getGameSessions(userId);
  const results = getScenarioResults(userId);
  const resultArr = Object.values(results);

  // If no sessions saved yet but individual results exist, compute from those
  const totalFromResults = resultArr.length;
  const pointsFromResults = resultArr.reduce((s,r)=>s+(r.points||0),0);
  const correctFromResults = resultArr.filter(r=>r.isCorrect).length;

  const totalGames = sessions.length;
  const totalPoints = totalGames > 0 ? sessions.reduce((s,g)=>s+g.totalScore,0) : pointsFromResults;
  const totalCorrect = totalGames > 0 ? sessions.reduce((s,g)=>s+g.correct,0) : correctFromResults;
  const totalScenarios = totalGames > 0 ? sessions.reduce((s,g)=>s+g.total,0) : totalFromResults;
  const bestScore = sessions.length ? Math.max(...sessions.map(g=>g.totalScore)) : pointsFromResults;
  const avgScore = totalGames > 0 ? Math.round(sessions.reduce((s,g)=>s+g.totalScore,0)/totalGames) : pointsFromResults;

  return {totalGames: Math.max(totalGames, totalFromResults > 0 ? 1 : 0), totalPoints, totalCorrect, totalScenarios, bestScore, avgScore, sessions, scenarioResults: results};
}

/* ======== DEMO ACCESS PASSWORD — change to whatever you want ======== */
const DEMO_PASSWORD = 'ISMDemo2025';

/* ======== ADMIN CONFIG — change this password to whatever you want ======== */
const ADMIN_PASSWORD = 'MarketMastery2025';

/* ======== DIFFICULTY MULTIPLIERS ======== */
const DIFF_MULTIPLIERS = {Beginner:1.0, Intermediate:1.25, Advanced:1.5, Expert:2.0};
const DIFF_MULT_LABELS = {Beginner:'1x', Intermediate:'1.25x', Advanced:'1.5x', Expert:'2x'};

/* ======== SOUND SYSTEM (Web Audio API — no files needed) ======== */
const SoundSystem = (() => {
  let ctx = null;
  let enabled = (() => { try { return localStorage.getItem('mm_sound') !== 'off'; } catch(e){return true;} })();
  const init = () => {
    if(!ctx) { try { ctx = new (window.AudioContext || window.webkitAudioContext)(); } catch(e){} }
    if(ctx && ctx.state === 'suspended') ctx.resume();
  };
  const tone = (freq, delay, dur, type='sine', vol=0.18) => {
    if(!ctx) return;
    const now = ctx.currentTime;
    const o = ctx.createOscillator(), g = ctx.createGain();
    o.connect(g); g.connect(ctx.destination);
    o.type = type; o.frequency.value = freq;
    g.gain.setValueAtTime(0, now+delay);
    g.gain.linearRampToValueAtTime(vol, now+delay+0.02);
    g.gain.exponentialRampToValueAtTime(0.001, now+delay+dur);
    o.start(now+delay); o.stop(now+delay+dur+0.06);
  };
  return {
    get enabled() { return enabled; },
    toggle() { enabled = !enabled; try { localStorage.setItem('mm_sound', enabled ? 'on' : 'off'); } catch(e){} return enabled; },
    play(type) {
      if(!enabled) return;
      init();
      if(!ctx) return;
      if(type==='correct') {
        tone(523.25, 0, 0.12); tone(659.25, 0.13, 0.18);
      } else if(type==='wrong') {
        tone(220, 0, 0.09, 'sawtooth', 0.12); tone(196, 0.06, 0.14, 'sawtooth', 0.10);
      } else if(type==='badge') {
        tone(523.25,0,0.12); tone(659.25,0.1,0.12); tone(783.99,0.2,0.14); tone(1046.5,0.3,0.28,undefined,0.22);
      } else if(type==='streak') {
        tone(659.25,0,0.09,'triangle'); tone(783.99,0.1,0.09,'triangle'); tone(987.77,0.2,0.09,'triangle'); tone(1174.66,0.3,0.18,'triangle',0.22);
      }
    }
  };
})();

/* ======== ACHIEVEMENTS SYSTEM ======== */
const BADGES = [
  {id:'first_trade',name:'First Trade',icon:'\u{1F331}',desc:'Complete your first scenario',check:(r,s)=>Object.keys(r).length>=1},
  {id:'ten_trades',name:'Seasoned Trader',icon:'\u{1F4CA}',desc:'Complete 10 scenarios',check:(r,s)=>Object.keys(r).length>=10},
  {id:'fifty_trades',name:'Market Veteran',icon:'\u{1F3C6}',desc:'Complete all 50 scenarios',check:(r,s)=>Object.keys(r).length>=50},
  {id:'perfect_5',name:'Hot Streak',icon:'\u{1F525}',desc:'Get 5 correct predictions in a row',check:(r,s)=>{const arr=Object.values(r).sort((a,b)=>new Date(a.date)-new Date(b.date));let streak=0;for(const x of arr){if(x.isCorrect)streak++;else streak=0;if(streak>=5)return true;}return false;}},
  {id:'perfect_score',name:'Perfect Score',icon:'\u{2B50}',desc:'Score 100% on a full game run (5+ scenarios)',check:(r,s)=>s.some(g=>g.correct===g.total&&g.total>=5)},
  {id:'rsi_master',name:'RSI Master',icon:'\u{1F52E}',desc:'Get 10 correct calls on scenarios where RSI was the key signal',check:(r,s)=>{let c=0;for(const[id,res]of Object.entries(r)){if(res.isCorrect){const sc=scenarios.find(x=>x.id===Number(id));if(sc&&sc.indicators&&sc.indicators.rsi&&(sc.indicators.rsi.note.includes('oversold')||sc.indicators.rsi.note.includes('overbought')))c++;}};return c>=10;}},
  {id:'false_spotter',name:'False Signal Spotter',icon:'\u{1F575}',desc:'Beat 5 tricky scenarios (moderate/mixed signal quality)',check:(r,s)=>{let c=0;for(const[id,res]of Object.entries(r)){if(res.isCorrect){const sc=scenarios.find(x=>x.id===Number(id));if(sc&&(sc.signalQuality==='moderate'||sc.signalQuality==='mixed'))c++;}};return c>=5;}},
  {id:'expert_clear',name:'Expert Analyst',icon:'\u{1F9E0}',desc:'Complete all Expert difficulty scenarios correctly',check:(r,s)=>{const expert=scenarios.filter(x=>x.difficulty==='Expert');return expert.length>0&&expert.every(x=>{const res=r[x.id];return res&&res.isCorrect;});}},
  {id:'speed_demon',name:'Speed Demon',icon:'\u26A1',desc:'Complete 10 scenarios in a single session',check:(r,s)=>s.some(g=>g.total>=10)},
  {id:'live_10',name:'Live Wire',icon:'\u{1F4E1}',desc:'Complete 10 live challenge predictions',check:(r,s,liveStats)=>liveStats&&liveStats.played>=10},
  {id:'live_streak_5',name:'Live Streak',icon:'\u{1F4A5}',desc:'Get 5 correct live predictions in a row',check:(r,s,liveStats)=>liveStats&&liveStats.bestStreak>=5},
  {id:'all_diff',name:'Well-Rounded',icon:'\u{1F30D}',desc:'Complete at least one scenario in every difficulty',check:(r,s)=>{const diffs=new Set();for(const[id]of Object.entries(r)){const sc=scenarios.find(x=>x.id===Number(id));if(sc)diffs.add(sc.difficulty);}return ['Beginner','Intermediate','Advanced','Expert'].every(d=>diffs.has(d));}},
];

function getUnlockedBadges(userId) {
  const results = getScenarioResults(userId);
  const sessions = getGameSessions(userId);
  let liveStats = null;
  try { liveStats = JSON.parse(localStorage.getItem(`mm_live_stats_${userId}`)); } catch(e) {}
  const saved = JSON.parse(localStorage.getItem(`mm_badges_${userId}`) || '{}');
  const unlocked = {};
  const newlyUnlocked = [];
  for(const badge of BADGES) {
    if(saved[badge.id]) {
      unlocked[badge.id] = saved[badge.id];
    } else if(badge.check(results, sessions, liveStats)) {
      unlocked[badge.id] = {date: new Date().toISOString()};
      newlyUnlocked.push(badge);
    }
  }
  if(newlyUnlocked.length > 0) {
    localStorage.setItem(`mm_badges_${userId}`, JSON.stringify(unlocked));
  }
  return {unlocked, newlyUnlocked};
}

function getBadgeProgress(userId) {
  const results = getScenarioResults(userId);
  const sessions = getGameSessions(userId);
  let liveStats = null;
  try { liveStats = JSON.parse(localStorage.getItem(`mm_live_stats_${userId}`)); } catch(e) {}
  const progress = {};
  const total = Object.keys(results).length;
  progress['first_trade'] = {current: Math.min(total, 1), target: 1};
  progress['ten_trades'] = {current: Math.min(total, 10), target: 10};
  progress['fifty_trades'] = {current: Math.min(total, 50), target: 50};
  // RSI master
  let rsiCount = 0;
  for(const [id, res] of Object.entries(results)) {
    if(res.isCorrect) {
      const sc = scenarios.find(x => x.id === Number(id));
      if(sc && sc.indicators && sc.indicators.rsi && (sc.indicators.rsi.note.includes('oversold') || sc.indicators.rsi.note.includes('overbought'))) rsiCount++;
    }
  }
  progress['rsi_master'] = {current: Math.min(rsiCount, 10), target: 10};
  // False spotter
  let falseCount = 0;
  for(const [id, res] of Object.entries(results)) {
    if(res.isCorrect) {
      const sc = scenarios.find(x => x.id === Number(id));
      if(sc && (sc.signalQuality === 'moderate' || sc.signalQuality === 'mixed')) falseCount++;
    }
  }
  progress['false_spotter'] = {current: Math.min(falseCount, 5), target: 5};
  progress['live_10'] = {current: Math.min(liveStats ? liveStats.played : 0, 10), target: 10};
  progress['live_streak_5'] = {current: Math.min(liveStats ? liveStats.bestStreak : 0, 5), target: 5};
  return progress;
}

/* ======== LEADERBOARD (Firebase + localStorage fallback) ======== */
function getLeaderboard() {
  const lb = JSON.parse(localStorage.getItem('mm_leaderboard') || '[]');
  return lb.sort((a, b) => b.score - a.score);
}

function updateLeaderboard(userId, name, stats, liveStats) {
  const lb = JSON.parse(localStorage.getItem('mm_leaderboard') || '[]');
  const existing = lb.findIndex(e => e.uid === userId);
  const entry = {
    uid: userId,
    name: name,
    score: stats.totalPoints,
    accuracy: stats.totalScenarios > 0 ? Math.round(stats.totalCorrect / stats.totalScenarios * 100) : 0,
    scenarios: stats.totalScenarios,
    bestScore: stats.bestScore,
    livePlayed: liveStats ? liveStats.played : 0,
    liveAccuracy: liveStats && liveStats.played > 0 ? Math.round(liveStats.correct / liveStats.played * 100) : 0,
    liveBestStreak: liveStats ? (liveStats.bestStreak || 0) : 0,
    lastPlayed: new Date().toISOString(),
  };
  if(existing >= 0) lb[existing] = entry;
  else lb.push(entry);
  localStorage.setItem('mm_leaderboard', JSON.stringify(lb));

  // Sync to Firebase if available
  if(firebaseReady && db) {
    db.collection('leaderboard').doc(userId).set(entry, {merge: true}).catch(e=>console.warn('Firebase write failed:', e));
  }
  return lb.sort((a, b) => b.score - a.score);
}

// Fetch global leaderboard from Firebase (async)
async function fetchGlobalLeaderboard() {
  if(!firebaseReady || !db) return null;
  try {
    const snap = await db.collection('leaderboard').orderBy('score','desc').limit(100).get();
    const entries = [];
    snap.forEach(doc => entries.push(doc.data()));
    return entries;
  } catch(e) {
    console.warn('Firebase read failed:', e);
    return null;
  }
}

/* ======== INDICATOR MATH ======== */
function computeSMA(closes,period){
  return closes.map((_,i)=>{if(i<period-1)return null;let s=0;for(let j=i-period+1;j<=i;j++)s+=closes[j];return s/period;});
}
function computeEMA(closes,period){
  const k=2/(period+1),e=[closes[0]];
  for(let i=1;i<closes.length;i++)e.push(closes[i]*k+e[i-1]*(1-k));
  return e;
}
function computeRSI(closes,period=14){
  if(closes.length<period+1)return closes.map(()=>50);
  const r=Array(period).fill(null);let ag=0,al=0;
  for(let i=1;i<=period;i++){const d=closes[i]-closes[i-1];if(d>=0)ag+=d;else al+=-d;}
  ag/=period;al/=period;r.push(100-100/(1+ag/(al||1e-9)));
  for(let i=period+1;i<closes.length;i++){const d=closes[i]-closes[i-1];ag=(ag*(period-1)+Math.max(0,d))/period;al=(al*(period-1)+Math.max(0,-d))/period;r.push(100-100/(1+ag/(al||1e-9)));}
  return r;
}
function computeMACD(closes,fast=12,slow=26,signal=9){
  const ef=computeEMA(closes,fast),es=computeEMA(closes,slow);
  const ml=ef.map((f,i)=>f-es[i]),sl=computeEMA(ml,signal),h=ml.map((m,i)=>m-sl[i]);
  return {macdLine:ml,signalLine:sl,histogram:h};
}
function lastVal(a){for(let i=a.length-1;i>=0;i--)if(a[i]!==null&&!isNaN(a[i]))return a[i];return null;}

/* ======== SCENARIOS (em dashes removed) ======== */
const scenarios = [
  {id:1,stock:'Apple Inc.',ticker:'AAPL',date:'January 2023',timeframe:'Daily',difficulty:'Beginner',
    question:'Apple has been falling for months. RSI is hitting levels rarely seen. What does the chart suggest?',
    correctAnswer:'buy',signalQuality:'strong',
    indicators:{rsi:{label:'RSI (14)',note:'Deeply oversold, below 30, signaling exhausted selling pressure'},macd:{label:'MACD (12,26,9)',note:'Bearish but histogram bars shrinking, selling momentum fading'},sma:{label:'50 & 200 SMA',note:'Price near the 200-day SMA, a key institutional support zone'}},
    explanation:{verdict:'Strong Buy Signal',summary:'RSI deeply oversold with MACD momentum fading at the 200-day SMA created a classic three-signal reversal setup.',details:"When RSI drops below 30, it signals the stock has been sold too aggressively. The MACD histogram shrinking confirmed sellers were losing energy. Price finding support at the 200-day SMA, watched by institutions, completed the alignment. This three-way confluence is a textbook reversal setup.",outcome:'AAPL rallied from ~$125 to over $180 in the following 6 months (+44%).',lesson:'When RSI hits extreme oversold AND momentum is fading AND price is at major SMA support, the probability of a meaningful bounce is significantly elevated.',indicatorBreakdown:[{name:'RSI: Oversold',signal:'bullish',reading:'Extreme oversold. Values below 30 have historically preceded sharp recoveries in large-cap stocks.'},{name:'MACD: Fading Bearish',signal:'bullish',reading:'Shrinking histogram bars = weakening selling pressure = bullish divergence forming.'},{name:'200-Day SMA Support',signal:'bullish',reading:'Price at the 200-day SMA attracts institutional buying. Many large funds add positions at this level.'}]},
    decisionFeedback:{buy:{quality:'strong',feedback:'Excellent. Oversold RSI with fading MACD at 200-SMA support is a high-conviction buy setup.'},sell:{quality:'weak',feedback:'Selling into extreme oversold conditions with multiple reversal signals is a common beginner mistake.'}}},

  {id:2,stock:'S&P 500 ETF',ticker:'SPY',date:'March 2022',timeframe:'Daily',difficulty:'Beginner',
    question:'The market has been declining. A major crossover just occurred between the 50 and 200-day moving averages. What does this signal?',
    correctAnswer:'sell',signalQuality:'strong',
    indicators:{rsi:{label:'RSI (14)',note:'Below 50, bearish territory, but not yet oversold'},macd:{label:'MACD (12,26,9)',note:'Negative and declining, sustained bearish momentum'},sma:{label:'50 & 200 SMA',note:'Death Cross: 50-day SMA crossed BELOW 200-day SMA, major bearish signal'}},
    explanation:{verdict:'Strong Sell Signal: Death Cross',summary:'A Death Cross, the 50-day SMA crossing below the 200-day SMA, is one of the most recognized bearish signals. All indicators aligned bearish.',details:"The Death Cross signals short-term momentum has turned decisively negative relative to the long-term trend. In 2022, this fired at the start of a bear market driven by Fed rate hikes. MACD being negative confirmed momentum, and RSI below 50 showed a bearish regime without being oversold enough to bounce.",outcome:'SPY fell from ~$420 to a low of ~$348 over the following 7 months (-17%).',lesson:'A Death Cross is a late but reliable signal. Combined with negative MACD, it signals high probability of continued downside.',indicatorBreakdown:[{name:'Death Cross (50/200 SMA)',signal:'bearish',reading:'50-day SMA below 200-day SMA confirms the downtrend is structural, not just a dip.'},{name:'MACD: Negative',signal:'bearish',reading:'MACD well below zero = strong sustained bearish momentum.'},{name:'RSI: ~40',signal:'bearish',reading:'Below 50 but not oversold. Room to fall before a reversal signal.'}]},
    decisionFeedback:{buy:{quality:'weak',feedback:'All indicators aligned bearish: Death Cross, negative MACD, RSI below 50. Buying here ignores the weight of evidence.'},sell:{quality:'strong',feedback:'Perfect. Death Cross + negative MACD + RSI below 50 is a textbook bearish alignment.'}}},

  {id:3,stock:'Tesla Inc.',ticker:'TSLA',date:'November 2021',timeframe:'Daily',difficulty:'Beginner',
    question:'Tesla has surged to all-time highs after months of buying. RSI is at extreme levels. What do the indicators suggest?',
    correctAnswer:'sell',signalQuality:'strong',
    indicators:{rsi:{label:'RSI (14)',note:'Extremely overbought, well above 70, rare territory'},macd:{label:'MACD (12,26,9)',note:'MACD line crossing below signal line, bearish crossover forming'},sma:{label:'50 & 200 SMA',note:'Price far above both SMAs, severely stretched from the mean'}},
    explanation:{verdict:'Strong Sell Signal: Extreme Overbought',summary:'RSI above 80 is extreme. A MACD bearish crossover at the top of an extended run with price far above SMAs is a classic topping signal.',details:"RSI above 70 signals overbought. At 80+, it represents unsustainable extremes. The MACD bearish crossover confirmed upward momentum was stalling. Price trading far above the 200-day SMA meant gravity would eventually pull it back. When MACD confirms a momentum shift at these extremes, risk increases dramatically.",outcome:'TSLA fell dramatically over the following 14 months, losing the majority of its value.',lesson:'RSI above 80 + MACD bearish crossover + extreme SMA extension is one of the strongest sell signals. Mean reversion is powerful.',indicatorBreakdown:[{name:'RSI: Extreme Overbought',signal:'bearish',reading:'Values above 80 in individual stocks often precede significant corrections.'},{name:'MACD: Bearish Crossover',signal:'bearish',reading:'MACD crossing below signal line = buying momentum shifting to selling momentum.'},{name:'Price vs 200 SMA: Extended',signal:'bearish',reading:'Extreme deviation from the 200-day mean creates powerful reversion pressure.'}]},
    decisionFeedback:{buy:{quality:'weak',feedback:'Buying into extreme RSI with a MACD bearish crossover is chasing, one of the most dangerous habits in trading.'},sell:{quality:'strong',feedback:'Excellent. Extreme overbought RSI + MACD bearish crossover = high-quality sell setup.'}}},

  {id:4,stock:'Advanced Micro Devices',ticker:'AMD',date:'January 2023',timeframe:'Daily',difficulty:'Intermediate',
    question:"AMD spent months building a base after a brutal decline. The 50 and 200-day SMAs are doing something significant. What's the signal?",
    correctAnswer:'buy',signalQuality:'strong',
    indicators:{rsi:{label:'RSI (14)',note:'Neutral-bullish around 55, room to run, not overbought'},macd:{label:'MACD (12,26,9)',note:'Recently crossed positive, new upward momentum'},sma:{label:'50 & 200 SMA',note:'Golden Cross: 50-day SMA crossed ABOVE 200-day SMA, major bullish signal'}},
    explanation:{verdict:'Strong Buy Signal: Golden Cross',summary:'A Golden Cross, 50-day SMA crossing above the 200-day, signals a new bullish trend. RSI at 55 meant room to run.',details:"The Golden Cross is the opposite of the Death Cross. After AMD crashed in 2022, this marked the shift from bearish to bullish. RSI at 55 was NOT overbought, the rally had room. MACD turning positive confirmed buyers in control. This is ideal: trend reversal + confirmation + healthy momentum.",outcome:'AMD rallied from ~$68 to over $130 in the following 5 months (+91%).',lesson:'A Golden Cross with RSI in neutral territory and positive MACD is one of the cleanest "new uptrend" signals.',indicatorBreakdown:[{name:'Golden Cross (50/200 SMA)',signal:'bullish',reading:'50-day SMA above 200-day confirms recent momentum is overtaking the longer-term trend, reversal confirmed.'},{name:'MACD: Positive',signal:'bullish',reading:'MACD above signal line and above zero = buying momentum dominant.'},{name:'RSI: ~55',signal:'bullish',reading:'Above 50 but far from overbought. Sweet spot: uptrend confirmed with room to rally.'}]},
    decisionFeedback:{buy:{quality:'strong',feedback:'Perfect. Golden Cross + positive MACD + healthy RSI = textbook new uptrend setup.'},sell:{quality:'weak',feedback:'A Golden Cross with positive MACD and neutral RSI is among the most reliable bullish signals.'}}},

  {id:5,stock:'Meta Platforms',ticker:'META',date:'October/November 2022',timeframe:'Daily',difficulty:'Intermediate',
    question:'Meta has crashed from $380 to $88. RSI is showing something extreme. Is this the bottom?',
    correctAnswer:'buy',signalQuality:'strong',
    indicators:{rsi:{label:'RSI (14)',note:'Historically extreme, near 20, one of the most oversold readings possible'},macd:{label:'MACD (12,26,9)',note:'Negative but histogram diverging: price falling while momentum slows'},sma:{label:'50 & 200 SMA',note:'Price far below 200-day SMA, extreme deviation creating snap-back pressure'}},
    explanation:{verdict:'Strong Buy Signal: Extreme Capitulation',summary:'RSI near 20 is a once-in-years reading. MACD bullish divergence (price lower lows but MACD higher lows) signaled a capitulation bottom.',details:"RSI near 20 means extreme exhaustion. The key: while price made lower lows, MACD histogram made higher lows. Sellers losing conviction even as price fell. This divergence precedes reversals. Extreme distance below the 200-day SMA created powerful mean-reversion pressure.",outcome:'META recovered from ~$88 to over $380 within 12 months (+332%).',lesson:'MACD divergence with RSI below 20 often marks major bottoms in fundamentally sound companies.',indicatorBreakdown:[{name:'RSI: ~20',signal:'bullish',reading:'Extreme oversold. RSI below 20 in major companies reliably precedes significant recoveries.'},{name:'MACD Divergence',signal:'bullish',reading:'Price making lower lows while MACD makes higher lows = most powerful bullish divergence signal.'},{name:'200 SMA Deviation',signal:'bullish',reading:'Extreme distance below the 200-day SMA creates powerful snap-back pressure.'}]},
    decisionFeedback:{buy:{quality:'strong',feedback:'Outstanding. RSI near 20 with MACD divergence is a rare, high-conviction reversal signal.'},sell:{quality:'weak',feedback:'RSI near 20 with MACD divergence signaled exhausted sellers. Selling here fights the signal.'}}},

  {id:6,stock:'NVIDIA Corporation',ticker:'NVDA',date:'December 2023',timeframe:'Daily',difficulty:'Advanced',
    question:"NVIDIA has been surging on AI demand. RSI is above 70, traditionally 'overbought.' Is this a sell signal?",
    correctAnswer:'buy',signalQuality:'false_signal',
    indicators:{rsi:{label:'RSI (14)',note:'Above 70 (overbought by standard rules), but in a powerful AI-driven uptrend'},macd:{label:'MACD (12,26,9)',note:'Strongly positive and rising, momentum still accelerating, no bearish crossover'},sma:{label:'50 & 200 SMA',note:'Both SMAs trending sharply higher, price above both, strong uptrend intact'}},
    explanation:{verdict:'False Bearish Signal: RSI Overbought in Strong Trends Is a Trap',summary:"RSI above 70 does NOT automatically mean sell. In strong momentum trends, RSI can stay overbought for months while prices keep rising.",details:"Traditional TA teaches RSI above 70 = sell. This works in range-bound markets. In strong trending markets, like NVIDIA's AI boom, RSI stays elevated for extended periods. The key: MACD showed no bearish crossover. Both SMAs were rising. An RSI overbought signal needs MACD confirmation to be actionable. Alone, it is insufficient.",outcome:'NVDA continued surging, gaining 60%+ in the following months before correcting.',lesson:'RSI above 70 alone is NOT a sell signal in strong uptrends. You need MACD bearish crossover or SMA breakdown to confirm.',indicatorBreakdown:[{name:'RSI: Overbought',signal:'neutral',reading:'Traditionally bearish, but without MACD confirmation this was a false alarm in a strong trend.'},{name:'MACD: Still Rising',signal:'bullish',reading:'No bearish crossover = momentum still intact. This overrides the RSI signal.'},{name:'Both SMAs Rising',signal:'bullish',reading:'Price above both rising SMAs confirms the uptrend is structurally sound.'}]},
    decisionFeedback:{buy:{quality:'strong',feedback:'Impressive. Recognizing RSI overbought as a false signal in a strong trend with rising MACD shows advanced understanding.'},sell:{quality:'weak',feedback:'Most common intermediate mistake: selling on RSI alone without checking MACD and trend structure.'}}},

  {id:7,stock:'Invesco QQQ ETF',ticker:'QQQ',date:'July 2023',timeframe:'Daily',difficulty:'Advanced',
    question:'QQQ has been consolidating sideways. MACD just crossed negative. Does this signal a decline?',
    correctAnswer:'buy',signalQuality:'false_signal',
    indicators:{rsi:{label:'RSI (14)',note:'Perfectly neutral around 49, no directional bias'},macd:{label:'MACD (12,26,9)',note:'Slight bearish crossover: MACD barely dipped below signal line'},sma:{label:'50 & 200 SMA',note:'Both SMAs flat and converged, textbook sideways consolidation'}},
    explanation:{verdict:'False Bearish Signal: MACD Fails in Sideways Markets',summary:'MACD generates false signals in range-bound markets. Flat SMAs + neutral RSI + weak MACD crossover = noise, not signal.',details:"MACD works best in trending markets. When sideways, it oscillates around zero creating false crossovers. Warning signs: RSI at 49 was perfectly neutral. Both SMAs were flat. The MACD crossover was barely negative. In consolidation, wait for a price breakout, not indicator signals.",outcome:'QQQ broke upward from consolidation, rallying ~8% over the following weeks.',lesson:'MACD is unreliable in sideways markets. Flat SMAs = consolidation = treat MACD signals with skepticism.',indicatorBreakdown:[{name:'MACD: Weak Cross',signal:'neutral',reading:'Barely negative in a sideways market. These micro-crossovers are mostly noise.'},{name:'RSI: 49',signal:'neutral',reading:'Perfectly neutral. No directional bias, market undecided.'},{name:'Flat SMAs',signal:'neutral',reading:'Both SMAs flat = consolidation. Indicator signals during consolidation are unreliable.'}]},
    decisionFeedback:{buy:{quality:'strong',feedback:'Advanced thinking. Recognizing weak MACD in a consolidation as a false signal separates intermediate from advanced traders.'},sell:{quality:'weak',feedback:'Classic false signal trap. MACD barely crossed negative in a sideways market, exactly when MACD is least reliable.'}}},

  {id:8,stock:'S&P 500 ETF',ticker:'SPY',date:'October 2022',timeframe:'Daily',difficulty:'Intermediate',
    question:'The S&P 500 has been in a bear market all year. RSI is oversold and MACD is shifting. Is this the bottom?',
    correctAnswer:'buy',signalQuality:'strong',
    indicators:{rsi:{label:'RSI (14)',note:'Oversold, in fear/panic territory below 30'},macd:{label:'MACD (12,26,9)',note:'Histogram turning less negative, MACD about to cross above signal line'},sma:{label:'50 & 200 SMA',note:'Price at major multi-year support, 200-day SMA slope beginning to flatten'}},
    explanation:{verdict:'Strong Buy Signal: Bear Market Bottom',summary:"RSI oversold with MACD bullish crossover forming at the year's lows marked the October 2022 bottom.",details:"RSI below 30 showed deep oversold conditions after a year of rate hikes. The MACD histogram shrinking and turning positive showed bearish momentum exhausting itself. Combined with price at major support, the risk-reward for buyers was highly favorable.",outcome:'SPY rallied from ~$348 to $450+ over the next 12 months (+29%).',lesson:"Bear markets bottom when sellers run out. RSI oversold + MACD turning positive + major support = classic bottom signal.",indicatorBreakdown:[{name:'RSI: Oversold',signal:'bullish',reading:'For broad market ETFs, RSI below 30 has historically been a reliable long-term buying signal.'},{name:'MACD: Bullish Cross Forming',signal:'bullish',reading:'MACD crossing above signal line confirms selling momentum is shifting to buying.'},{name:'Major Support Level',signal:'bullish',reading:'Price at levels that held in prior cycles, where institutional buyers typically enter.'}]},
    decisionFeedback:{buy:{quality:'strong',feedback:"Great call. RSI oversold + MACD crossover + major support = high-skill bottom identification."},sell:{quality:'weak',feedback:'RSI oversold with MACD turning positive at key support signals seller exhaustion. Selling here fights the bottom.'}}},

  {id:9,stock:'Amazon.com Inc.',ticker:'AMZN',date:'August/September 2022',timeframe:'Daily',difficulty:'Advanced',
    question:'Amazon bounced off lows and RSI recovered from oversold. Is this a real recovery or a bear market trap?',
    correctAnswer:'sell',signalQuality:'moderate',
    indicators:{rsi:{label:'RSI (14)',note:'Recovered from oversold but still below 50, not yet bullish'},macd:{label:'MACD (12,26,9)',note:'Still negative, no bullish crossover confirmed'},sma:{label:'50 & 200 SMA',note:'Both SMAs trending sharply down, price below both, downtrend intact'}},
    explanation:{verdict:'Bear Market Rally: Dead Cat Bounce',summary:"RSI recovering without crossing 50, MACD still negative, and declining SMAs all confirmed the downtrend was intact.",details:"The trap: RSI recovering from 20 to 38 LOOKS like reversal. But 38 is still bearish (below 50). No MACD bullish crossover. Both SMAs still declining sharply. Compare to Meta (Scenario 5): Meta had RSI near 20 WITH MACD divergence. Amazon had RSI 38 with NO divergence, completely different.",outcome:'AMZN fell another ~29% to $84 before finding a real bottom.',lesson:"A recovering RSI is not enough. You need RSI above 50, OR MACD crossover, AND flattening SMAs. Without these, it is a trap.",indicatorBreakdown:[{name:'RSI: ~38',signal:'bearish',reading:"Recovered but still below 50 = 'less oversold' not 'bullish.'"},{name:'MACD: Still Negative',signal:'bearish',reading:'No bullish crossover. Small bounce without a line cross is not a reversal signal.'},{name:'Declining SMAs',signal:'bearish',reading:'Both SMAs trending down = textbook downtrend. Until SMAs flatten, trend is down.'}]},
    decisionFeedback:{buy:{quality:'weak',feedback:"Dead cat bounce trap. RSI below 50, no MACD crossover, declining SMAs = downtrend intact."},sell:{quality:'strong',feedback:"Good discipline. Partial RSI recovery without MACD confirmation in a downtrend is a trap, not a reversal."}}},

  {id:10,stock:'S&P 500 ETF',ticker:'SPY',date:'March 2020 (COVID Crash)',timeframe:'Daily',difficulty:'Expert',
    question:'The market has crashed 35% in weeks. Every trend indicator says SELL. RSI shows extreme panic. What do you do?',
    correctAnswer:'buy',signalQuality:'false_signal',
    indicators:{rsi:{label:'RSI (14)',note:'Near 13, one of the most extreme oversold readings in US market history'},macd:{label:'MACD (12,26,9)',note:'Deeply negative, worst reading in years. All trend momentum is bearish.'},sma:{label:'50 & 200 SMA',note:'Death Cross confirmed. Price 25% below 200-day SMA. ALL trend signals bearish.'}},
    explanation:{verdict:'The Ultimate Lesson: When ALL Indicators Are Wrong',summary:'Every indicator screamed SELL. Yet RSI near 13 in a broad market index represents once-in-a-decade capitulation panic, historically the best time to buy.',details:"March 23, 2020 was the COVID bottom. RSI near 13 in the BROAD MARKET has historically marked major bottoms, not continued declines. The S&P 500 represents 500 companies, it does not go to zero. MACD and Death Cross were lagging indicators confirming what ALREADY happened. RSI at 13 was a LEADING indicator of the reversal.",outcome:'SPY rallied from ~$228 to $400+ by year-end (+80% in 9 months), the fastest recovery in history.',lesson:'RSI below 15 in broad market indices = capitulation panic = historically the best time to buy. Trend indicators are LAGGING at crash lows.',indicatorBreakdown:[{name:'RSI: ~13, Capitulation',signal:'bullish',reading:"At this extreme, RSI becomes a 'panic meter.' Below 15 in broad indices has preceded massive recoveries."},{name:'MACD: Deeply Negative',signal:'neutral',reading:"MACD is LAGGING. It confirms what happened, not what is next. Extreme negative at a crash low does not equal more downside."},{name:'Death Cross: Lagging',signal:'neutral',reading:'Death Crosses at CRASH LOWS (with RSI at 13) are lagging signals that the damage is already priced in.'}]},
    decisionFeedback:{buy:{quality:'strong',feedback:'Expert-level thinking. Overriding bearish trend indicators at extreme RSI lows in broad indices is the hallmark of elite reasoning.'},sell:{quality:'weak',feedback:'You followed indicators mechanically. At RSI below 15 in broad indices, trend indicators are lagging. This was the greatest buying opportunity of the decade.'}}},

  // ===== BEGINNER (11-22) =====

  {id:11,stock:'Microsoft Corp.',ticker:'MSFT',date:'January 2023',timeframe:'Daily',difficulty:'Beginner',
    question:'Microsoft has pulled back sharply after months of decline. RSI is approaching oversold territory. What do you see?',
    correctAnswer:'buy',signalQuality:'strong',
    indicators:{rsi:{label:'RSI (14)',note:'Near 30, approaching oversold, selling pressure exhausting'},macd:{label:'MACD (12,26,9)',note:'Negative but histogram shrinking, bearish momentum fading'},sma:{label:'50 & 200 SMA',note:'Price testing the 200-day SMA from above, key support level'}},
    explanation:{verdict:'Strong Buy Signal',summary:'RSI near oversold with fading MACD momentum at the 200-day SMA support created a classic reversal setup.',details:"Microsoft pulled back to key support after the 2022 tech selloff. RSI approaching 30 showed selling was overdone. The MACD histogram shrinking confirmed sellers were losing conviction. The 200-day SMA acted as a floor where institutional buyers stepped in.",outcome:'MSFT rallied from ~$220 to over $340 in the following 6 months (+55%).',lesson:'When RSI nears 30 and MACD momentum is fading at a major SMA support, the probability of a bounce is high.',indicatorBreakdown:[{name:'RSI: Near Oversold',signal:'bullish',reading:'Approaching 30 signals exhausted selling in a fundamentally strong stock.'},{name:'MACD: Fading Bearish',signal:'bullish',reading:'Shrinking histogram = sellers losing energy.'},{name:'200-Day SMA Support',signal:'bullish',reading:'Institutional buyers typically defend this level.'}]},
    decisionFeedback:{buy:{quality:'strong',feedback:'Great read. Oversold RSI with fading bearish MACD at 200-SMA support is a textbook bounce setup.'},sell:{quality:'weak',feedback:'Selling into oversold conditions at major support ignores multiple reversal signals.'}}},

  {id:12,stock:'Alphabet Inc.',ticker:'GOOGL',date:'November 2022',timeframe:'Daily',difficulty:'Beginner',
    question:'Google has fallen over 40% from its highs. RSI is deeply oversold. Is this a buying opportunity?',
    correctAnswer:'buy',signalQuality:'strong',
    indicators:{rsi:{label:'RSI (14)',note:'Below 30, deeply oversold after months of selling'},macd:{label:'MACD (12,26,9)',note:'Negative but starting to curl upward, momentum shift forming'},sma:{label:'50 & 200 SMA',note:'Price far below 200-day SMA, extreme deviation from the mean'}},
    explanation:{verdict:'Strong Buy Signal',summary:'RSI below 30 with MACD beginning to turn up and extreme distance below the 200-day SMA signaled a major bottom.',details:"Google dropped from $150 to under $90 during the 2022 tech crash. RSI below 30 in a mega-cap stock is rare and historically precedes strong recoveries. MACD starting to curl up showed the selling wave was losing force. Extreme deviation below the 200-day SMA created powerful snap-back pressure.",outcome:'GOOGL recovered from ~$86 to over $130 in the following 6 months (+51%).',lesson:'Deeply oversold RSI in mega-cap stocks with MACD turning up is a reliable reversal signal.',indicatorBreakdown:[{name:'RSI: Deeply Oversold',signal:'bullish',reading:'Below 30 in a mega-cap is a rare signal that historically precedes recoveries.'},{name:'MACD: Curling Up',signal:'bullish',reading:'The MACD line starting to rise confirms selling pressure is weakening.'},{name:'Extreme SMA Deviation',signal:'bullish',reading:'Price far below the 200-day SMA creates mean-reversion pressure.'}]},
    decisionFeedback:{buy:{quality:'strong',feedback:'Excellent. Deeply oversold mega-cap with MACD turning is a high-probability buy.'},sell:{quality:'weak',feedback:'Selling a deeply oversold mega-cap with MACD turning up fights the evidence.'}}},

  {id:13,stock:'Walt Disney Co.',ticker:'DIS',date:'September 2022',timeframe:'Daily',difficulty:'Beginner',
    question:'Disney has been in a steady decline for over a year. MACD is deeply negative. What is the trend telling you?',
    correctAnswer:'sell',signalQuality:'strong',
    indicators:{rsi:{label:'RSI (14)',note:'Around 35, weak but not yet oversold, room to fall'},macd:{label:'MACD (12,26,9)',note:'Deeply negative and declining, strong sustained bearish momentum'},sma:{label:'50 & 200 SMA',note:'50-day SMA well below 200-day SMA (Death Cross), both declining'}},
    explanation:{verdict:'Strong Sell Signal',summary:'A confirmed Death Cross with deeply negative MACD and RSI below 50 but not oversold meant the downtrend had more room to run.',details:"Disney was in a structural downtrend driven by streaming losses and park concerns. The Death Cross confirmed the trend was not just a dip. MACD deeply negative showed strong sustained selling. RSI at 35 was weak but not oversold enough to trigger a bounce.",outcome:'DIS continued falling from ~$100 to under $85 over the following 2 months (-15%).',lesson:'Death Cross + deeply negative MACD + RSI below 50 (but not oversold) = downtrend with more room to fall.',indicatorBreakdown:[{name:'Death Cross',signal:'bearish',reading:'50-day below 200-day confirms a structural downtrend.'},{name:'MACD: Deeply Negative',signal:'bearish',reading:'Sustained negative readings show persistent selling pressure.'},{name:'RSI: ~35',signal:'bearish',reading:'Below 50 but not oversold means more downside before a bounce.'}]},
    decisionFeedback:{buy:{quality:'weak',feedback:'Buying into a Death Cross with deeply negative MACD is fighting the trend.'},sell:{quality:'strong',feedback:'Correct. All indicators aligned bearish with room to fall.'}}},

  {id:14,stock:'Netflix Inc.',ticker:'NFLX',date:'May 2022',timeframe:'Daily',difficulty:'Beginner',
    question:'Netflix has crashed 75% after reporting subscriber losses. RSI recently bounced from extreme lows. Is the worst over?',
    correctAnswer:'sell',signalQuality:'moderate',
    indicators:{rsi:{label:'RSI (14)',note:'Recovered from extreme lows to ~38, still below 50'},macd:{label:'MACD (12,26,9)',note:'Deeply negative, no bullish crossover, momentum still bearish'},sma:{label:'50 & 200 SMA',note:'Both SMAs declining sharply, price far below both'}},
    explanation:{verdict:'Sell: Dead Cat Bounce',summary:'Despite the RSI bounce, MACD remained deeply negative and both SMAs were declining. The bounce was a trap, not a reversal.',details:"Netflix crashed on subscriber losses. While RSI recovered from extreme oversold levels, it only reached 38, still bearish. MACD showed no bullish crossover. Both SMAs were declining sharply. A true bottom needs MACD confirmation and SMA flattening.",outcome:'NFLX continued to struggle, trading sideways to down for several more months before eventually recovering.',lesson:'An RSI bounce from extreme lows is not enough. Without MACD crossover and SMA stabilization, it is a dead cat bounce.',indicatorBreakdown:[{name:'RSI: ~38',signal:'bearish',reading:'Recovered but below 50 means "less oversold" not "bullish."'},{name:'MACD: Deeply Negative',signal:'bearish',reading:'No bullish crossover = selling momentum still dominant.'},{name:'Declining SMAs',signal:'bearish',reading:'Both SMAs falling sharply = structural downtrend intact.'}]},
    decisionFeedback:{buy:{quality:'weak',feedback:'Classic dead cat bounce trap. RSI bouncing without MACD confirmation in a crash is unreliable.'},sell:{quality:'strong',feedback:'Good discipline. RSI recovery alone without MACD or SMA support is not a reversal.'}}},

  {id:15,stock:'JPMorgan Chase',ticker:'JPM',date:'March 2023',timeframe:'Daily',difficulty:'Beginner',
    question:'JPMorgan was steady, then suddenly dropped on banking crisis fears. RSI plunged rapidly. What do you do?',
    correctAnswer:'buy',signalQuality:'moderate',
    indicators:{rsi:{label:'RSI (14)',note:'Dropped sharply to near 30, rapid oversold reading from a sudden event'},macd:{label:'MACD (12,26,9)',note:'Just turned negative, a fresh bearish crossover'},sma:{label:'50 & 200 SMA',note:'Price dropped to the 200-day SMA, testing major long-term support'}},
    explanation:{verdict:'Moderate Buy Signal',summary:'A sudden event-driven drop to 200-day SMA support with RSI near oversold in a fundamentally sound bank created a buying opportunity, though MACD turning negative added risk.',details:"The SVB banking crisis caused panic selling across all bank stocks. JPM, as the strongest US bank, was unfairly punished. RSI dropping to 30 on panic, not fundamentals, at the 200-day SMA was a classic overreaction buy. MACD turning negative was concerning but event-driven, not trend-driven.",outcome:'JPM recovered from ~$125 to over $145 in the following 2 months (+16%).',lesson:'Event-driven drops to major support in fundamentally strong stocks often create buying opportunities, even with fresh MACD bearish signals.',indicatorBreakdown:[{name:'RSI: Near 30',signal:'bullish',reading:'Rapid drop to oversold on panic selling = overreaction.'},{name:'MACD: Fresh Bearish',signal:'bearish',reading:'Just turned negative, but event-driven, not from a deteriorating trend.'},{name:'200-Day SMA Support',signal:'bullish',reading:'Long-term support held, suggesting institutional buyers stepped in.'}]},
    decisionFeedback:{buy:{quality:'strong',feedback:'Smart. Event-driven panic at 200-SMA support in a strong name is a high-probability buy.'},sell:{quality:'weak',feedback:'Selling JPM on banking panic at 200-SMA support is selling the overreaction, not the trend.'}}},

  {id:16,stock:'Boeing Co.',ticker:'BA',date:'June 2022',timeframe:'Daily',difficulty:'Beginner',
    question:'Boeing has been trending down for months. RSI is below 40 and MACD is negative. What does the chart say?',
    correctAnswer:'sell',signalQuality:'strong',
    indicators:{rsi:{label:'RSI (14)',note:'Below 40, consistently weak, bearish regime'},macd:{label:'MACD (12,26,9)',note:'Below zero and declining, sustained bearish momentum'},sma:{label:'50 & 200 SMA',note:'Price below both SMAs, 50-day trending down toward 200-day'}},
    explanation:{verdict:'Strong Sell Signal',summary:'Consistent weakness across all indicators with no reversal signals in sight confirmed the downtrend.',details:"Boeing was under pressure from production issues and recession fears. RSI below 40 consistently showed a bearish regime. MACD declining below zero confirmed sustained selling. Price below both SMAs with the 50-day approaching a Death Cross left no room for bullish interpretation.",outcome:'BA continued falling, dropping another 15% before finding temporary support.',lesson:'When all three indicators are bearish and trending worse, the path of least resistance is down.',indicatorBreakdown:[{name:'RSI: Below 40',signal:'bearish',reading:'Consistent readings below 40 confirm a bearish regime.'},{name:'MACD: Declining Below Zero',signal:'bearish',reading:'Getting more negative = selling pressure is accelerating.'},{name:'Price Below Both SMAs',signal:'bearish',reading:'No support from either moving average.'}]},
    decisionFeedback:{buy:{quality:'weak',feedback:'All indicators bearish with no reversal signals. Buying here is catching a falling knife.'},sell:{quality:'strong',feedback:'Correct. Triple bearish alignment with no reversal signals = clear sell.'}}},

  {id:17,stock:'Visa Inc.',ticker:'V',date:'May 2023',timeframe:'Daily',difficulty:'Beginner',
    question:'Visa has been quietly climbing for months. RSI is above 60 and both SMAs are rising. What is the outlook?',
    correctAnswer:'buy',signalQuality:'strong',
    indicators:{rsi:{label:'RSI (14)',note:'Around 62, bullish territory but not overbought, healthy momentum'},macd:{label:'MACD (12,26,9)',note:'Above zero and signal line, positive momentum sustained'},sma:{label:'50 & 200 SMA',note:'Both SMAs rising, price above both, classic uptrend'}},
    explanation:{verdict:'Strong Buy Signal: Healthy Uptrend',summary:'All indicators aligned bullish with RSI in a healthy range, MACD positive, and rising SMAs. A textbook uptrend.',details:"Visa showed a picture-perfect uptrend. RSI at 62 is the sweet spot: above 50 (bullish) but below 70 (not overbought). MACD positive and above its signal line confirmed buying momentum. Both SMAs rising with price above them is the definition of an uptrend.",outcome:'V continued to climb steadily over the following months.',lesson:'RSI 55-65 with positive MACD and rising SMAs is the ideal "buy the trend" setup.',indicatorBreakdown:[{name:'RSI: ~62',signal:'bullish',reading:'Sweet spot: confirmed uptrend without being overbought.'},{name:'MACD: Positive',signal:'bullish',reading:'Above zero and signal line = sustained buying momentum.'},{name:'Rising SMAs',signal:'bullish',reading:'Both SMAs trending up with price above = textbook uptrend.'}]},
    decisionFeedback:{buy:{quality:'strong',feedback:'Perfect trend-following read. Healthy RSI + positive MACD + rising SMAs = ride the trend.'},sell:{quality:'weak',feedback:'Selling a healthy uptrend with all indicators aligned bullish is fighting the trend.'}}},

  {id:18,stock:'Exxon Mobil',ticker:'XOM',date:'June 2022',timeframe:'Daily',difficulty:'Beginner',
    question:'Exxon has surged dramatically on soaring oil prices. RSI is elevated. Should you buy the momentum or take profits?',
    correctAnswer:'sell',signalQuality:'moderate',
    indicators:{rsi:{label:'RSI (14)',note:'Above 70, overbought after a massive run'},macd:{label:'MACD (12,26,9)',note:'Very positive but starting to flatten, momentum stalling'},sma:{label:'50 & 200 SMA',note:'Price far above both SMAs, extremely stretched from the mean'}},
    explanation:{verdict:'Moderate Sell Signal',summary:'RSI overbought with MACD flattening and extreme SMA extension suggested the rally was running out of steam.',details:"XOM had an incredible run driven by high oil prices. RSI above 70 signaled overbought conditions. MACD flattening (not yet crossing down) showed momentum was stalling. The extreme distance above the 200-day SMA created mean-reversion risk. While the trend was still technically up, the risk-reward for new buys was poor.",outcome:'XOM pulled back ~20% over the following 2 months before stabilizing.',lesson:'Overbought RSI with flattening MACD and extreme SMA extension signals a pullback is likely, even in strong trends.',indicatorBreakdown:[{name:'RSI: Above 70',signal:'bearish',reading:'Overbought after a massive run increases pullback probability.'},{name:'MACD: Flattening',signal:'neutral',reading:'Not yet bearish, but momentum is no longer accelerating.'},{name:'Extreme SMA Extension',signal:'bearish',reading:'Being far above the 200-day SMA invites mean reversion.'}]},
    decisionFeedback:{buy:{quality:'weak',feedback:'Buying after a massive run with overbought RSI and flattening MACD is chasing.'},sell:{quality:'strong',feedback:'Good discipline. Taking profits when RSI is overbought and MACD is stalling is smart risk management.'}}},

  {id:19,stock:'Walmart Inc.',ticker:'WMT',date:'February 2023',timeframe:'Daily',difficulty:'Beginner',
    question:'Walmart has been range-bound for months. RSI sits near 50 and both SMAs are flat. What does this setup mean?',
    correctAnswer:'buy',signalQuality:'moderate',
    indicators:{rsi:{label:'RSI (14)',note:'Near 50, perfectly neutral, no directional bias'},macd:{label:'MACD (12,26,9)',note:'Hovering near zero, very slight positive crossover forming'},sma:{label:'50 & 200 SMA',note:'Both SMAs flat and converged, consolidation pattern'}},
    explanation:{verdict:'Moderate Buy Signal',summary:'A slight MACD positive crossover during consolidation, combined with WMT being a defensive stock in uncertain times, favored a breakout to the upside.',details:"Walmart was in a consolidation phase with no strong signals in either direction. The slight MACD positive crossover was the tiebreaker. In defensive stocks during uncertain markets, consolidation often resolves upward as investors seek safety. RSI at 50 meant room to move in either direction.",outcome:'WMT broke out of consolidation to the upside, gaining ~10% over the following 2 months.',lesson:'In consolidation, look for the MACD crossover direction as the tiebreaker. Defensive stocks often break upward in uncertain markets.',indicatorBreakdown:[{name:'RSI: ~50',signal:'neutral',reading:'Perfectly neutral, waiting for a catalyst.'},{name:'MACD: Slight Positive Cross',signal:'bullish',reading:'A fresh crossover during consolidation hints at the breakout direction.'},{name:'Flat SMAs',signal:'neutral',reading:'Consolidation pattern; wait for breakout confirmation.'}]},
    decisionFeedback:{buy:{quality:'strong',feedback:'Good read. MACD crossover in consolidation + defensive stock in uncertain times = slight bullish edge.'},sell:{quality:'weak',feedback:'The slight MACD positive crossover favored upside. Selling neutral setups in defensive stocks during uncertainty is suboptimal.'}}},

  {id:20,stock:'Coca-Cola Co.',ticker:'KO',date:'April 2022',timeframe:'Daily',difficulty:'Beginner',
    question:'Coca-Cola has been steadily climbing while the broader market sells off. RSI is around 65. Is this outperformance sustainable?',
    correctAnswer:'buy',signalQuality:'strong',
    indicators:{rsi:{label:'RSI (14)',note:'Around 65, bullish but not overbought, healthy strength'},macd:{label:'MACD (12,26,9)',note:'Positive and rising, strong sustained buying momentum'},sma:{label:'50 & 200 SMA',note:'Both SMAs rising, price above both, clear uptrend'}},
    explanation:{verdict:'Strong Buy Signal: Defensive Strength',summary:'Coca-Cola showed relative strength versus the market with all indicators aligned bullish. Defensive names outperform during selloffs.',details:"While tech stocks crashed in 2022, Coca-Cola was a flight-to-safety beneficiary. RSI at 65 was healthy, MACD was positive and rising, and both SMAs were trending up. In bear markets, defensive stocks with these indicator profiles tend to continue outperforming.",outcome:'KO continued its outperformance, reaching new all-time highs while the S&P 500 kept falling.',lesson:'Relative strength matters. A stock outperforming a falling market with healthy indicators is likely to continue.',indicatorBreakdown:[{name:'RSI: ~65',signal:'bullish',reading:'Healthy bullish reading, showing sustained buying interest.'},{name:'MACD: Rising Positive',signal:'bullish',reading:'Increasing positive values = accelerating buying momentum.'},{name:'Rising SMAs',signal:'bullish',reading:'Classic uptrend structure with price above both averages.'}]},
    decisionFeedback:{buy:{quality:'strong',feedback:'Excellent. Relative strength with aligned bullish indicators in a defensive name during a selloff is a high-probability buy.'},sell:{quality:'weak',feedback:'Selling a stock showing relative strength with bullish indicators fights the flow of capital.'}}},

  {id:21,stock:'Pfizer Inc.',ticker:'PFE',date:'December 2022',timeframe:'Daily',difficulty:'Beginner',
    question:'Pfizer has been steadily declining from its COVID highs. All indicators look weak. Is there any reason to buy?',
    correctAnswer:'sell',signalQuality:'strong',
    indicators:{rsi:{label:'RSI (14)',note:'Around 38, weak but not oversold enough for a bounce'},macd:{label:'MACD (12,26,9)',note:'Below zero and declining, sustained bearish momentum'},sma:{label:'50 & 200 SMA',note:'Price below both, Death Cross in effect, downtrend confirmed'}},
    explanation:{verdict:'Strong Sell Signal',summary:'Death Cross confirmed with declining MACD and RSI below 50 left no room for a bullish case.',details:"Pfizer was in a clear downtrend as COVID vaccine demand faded. The Death Cross confirmed the trend was structural. MACD declining below zero showed persistent selling. RSI at 38 was not oversold enough to trigger a bounce. All indicators pointed the same direction: down.",outcome:'PFE continued to decline, eventually dropping below $27 from ~$50 levels.',lesson:'When all indicators align bearish and the fundamental story is deteriorating, the trend is your friend.',indicatorBreakdown:[{name:'RSI: ~38',signal:'bearish',reading:'Below 50 but not oversold, meaning the downtrend has more room.'},{name:'MACD: Declining Below Zero',signal:'bearish',reading:'Getting more negative = selling pressure increasing.'},{name:'Death Cross Active',signal:'bearish',reading:'Structural downtrend confirmed by the 50/200 SMA crossover.'}]},
    decisionFeedback:{buy:{quality:'weak',feedback:'All indicators aligned bearish with a deteriorating fundamental story. No reason to buy.'},sell:{quality:'strong',feedback:'Correct. Triple bearish alignment in a stock with fading catalysts = clear sell.'}}},

  {id:22,stock:'Intel Corp.',ticker:'INTC',date:'January 2023',timeframe:'Daily',difficulty:'Beginner',
    question:'Intel has crashed over 60% from its highs. RSI is near oversold levels. Could this be a bottom?',
    correctAnswer:'sell',signalQuality:'moderate',
    indicators:{rsi:{label:'RSI (14)',note:'Near 32, approaching oversold but not extreme'},macd:{label:'MACD (12,26,9)',note:'Negative, no signs of a bullish crossover forming'},sma:{label:'50 & 200 SMA',note:'Both SMAs declining, Death Cross in effect, strong downtrend'}},
    explanation:{verdict:'Moderate Sell Signal',summary:'Despite approaching oversold RSI, the lack of MACD divergence and active Death Cross suggested more downside ahead.',details:"Intel was in a structural decline due to losing market share. RSI near 32 might tempt buyers, but without MACD showing any bullish divergence or crossover attempt, there was no evidence of a bottom forming. The Death Cross and declining SMAs confirmed the downtrend. Not every oversold reading is a buy.",outcome:'INTC continued to struggle, unable to mount a sustained recovery.',lesson:'An approaching oversold RSI alone is not a buy signal. You need MACD confirmation or divergence to identify a real bottom.',indicatorBreakdown:[{name:'RSI: ~32',signal:'neutral',reading:'Approaching oversold but not extreme enough to signal capitulation.'},{name:'MACD: Negative, No Cross',signal:'bearish',reading:'No bullish crossover forming means sellers are still in control.'},{name:'Death Cross Active',signal:'bearish',reading:'Structural downtrend with no signs of reversal.'}]},
    decisionFeedback:{buy:{quality:'weak',feedback:'Near-oversold RSI without MACD confirmation in a structural downtrend is not a buy signal.'},sell:{quality:'strong',feedback:'Good analysis. Recognizing that oversold RSI alone is insufficient without MACD confirmation shows discipline.'}}},

  // ===== INTERMEDIATE (23-34) =====

  {id:23,stock:'PayPal Holdings',ticker:'PYPL',date:'February 2022',timeframe:'Daily',difficulty:'Intermediate',
    question:'PayPal just crashed 25% in a single day on earnings. RSI plunged to extreme lows. Is this a panic buy opportunity?',
    correctAnswer:'sell',signalQuality:'moderate',
    indicators:{rsi:{label:'RSI (14)',note:'Crashed to below 20, extreme oversold from a gap down'},macd:{label:'MACD (12,26,9)',note:'Collapsed into deeply negative territory, extreme bearish momentum'},sma:{label:'50 & 200 SMA',note:'Price gapped far below both SMAs, trend structure destroyed'}},
    explanation:{verdict:'Sell: Earnings Gap Down Changes Everything',summary:'While RSI below 20 is extreme, an earnings gap down that breaks all support levels changes the technical landscape. This is not a normal oversold signal.',details:"PayPal gapped down 25% on terrible earnings guidance. This is different from a gradual decline to oversold. An earnings gap signals a fundamental reassessment by the market. Both SMAs are now far above, acting as resistance, not support. MACD collapsed. The old technical levels are irrelevant after such a gap.",outcome:'PYPL continued falling from ~$130 to under $70 over the following months (-46%).',lesson:'Earnings gap downs reset the technical picture. Extreme oversold RSI after a gap is different from gradual oversold. Do not catch falling knives on earnings gaps.',indicatorBreakdown:[{name:'RSI: Below 20',signal:'neutral',reading:'Extreme reading, but caused by an earnings gap, not normal selling. Different context.'},{name:'MACD: Collapsed',signal:'bearish',reading:'Extreme negative spike = fundamental reassessment, not a normal dip.'},{name:'Broken SMA Structure',signal:'bearish',reading:'Gapping below all support means SMAs become resistance overhead.'}]},
    decisionFeedback:{buy:{quality:'weak',feedback:'Catching a falling knife after an earnings gap is one of the most dangerous trades. Oversold after a gap is not the same as gradual oversold.'},sell:{quality:'strong',feedback:'Smart. Recognizing that earnings gaps reset the technical picture shows intermediate-level thinking.'}}},

  {id:24,stock:'Alibaba Group',ticker:'BABA',date:'November 2021',timeframe:'Daily',difficulty:'Intermediate',
    question:'Alibaba has been falling for months under regulatory pressure. RSI is low but MACD shows something interesting. What do you see?',
    correctAnswer:'sell',signalQuality:'moderate',
    indicators:{rsi:{label:'RSI (14)',note:'Around 35, weak but not extremely oversold'},macd:{label:'MACD (12,26,9)',note:'Below zero with no bullish divergence, each bounce makes a lower MACD peak'},sma:{label:'50 & 200 SMA',note:'Both SMAs declining sharply, Death Cross confirmed long ago'}},
    explanation:{verdict:'Sell: No Divergence, No Bottom',summary:'The key: MACD was making lower highs on each bounce attempt. Without bullish divergence, there is no evidence of a bottom forming.',details:"Alibaba faced ongoing Chinese regulatory crackdowns. Each time the stock bounced, MACD made a lower peak than the previous bounce. This is bearish continuation, not bottom formation. Compare to Meta (scenario 5) where MACD showed higher lows while price fell. That divergence was absent here.",outcome:'BABA continued declining, eventually falling below $75 from ~$150 levels.',lesson:'Without MACD bullish divergence, oversold readings in a downtrend are traps. Divergence is the key signal for bottoms.',indicatorBreakdown:[{name:'RSI: ~35',signal:'bearish',reading:'Low but without any bullish setup to confirm a bottom.'},{name:'MACD: Lower Highs',signal:'bearish',reading:'Each bounce has weaker momentum. The opposite of bullish divergence.'},{name:'Death Cross Active',signal:'bearish',reading:'Structural downtrend with no technical evidence of a reversal.'}]},
    decisionFeedback:{buy:{quality:'weak',feedback:'Without MACD divergence, buying oversold stocks in structural downtrends is a common trap.'},sell:{quality:'strong',feedback:'Good. Checking for MACD divergence before buying oversold stocks shows analytical skill.'}}},

  {id:25,stock:'Shopify Inc.',ticker:'SHOP',date:'May 2022',timeframe:'Daily',difficulty:'Intermediate',
    question:'Shopify has crashed 80% from its all-time high. RSI is very low. Does this massive decline make it a deep value buy?',
    correctAnswer:'sell',signalQuality:'moderate',
    indicators:{rsi:{label:'RSI (14)',note:'Low around 25, deeply oversold after a brutal decline'},macd:{label:'MACD (12,26,9)',note:'Deeply negative with no sign of a bullish crossover or divergence'},sma:{label:'50 & 200 SMA',note:'Both SMAs in steep decline, Death Cross long confirmed, price far below'}},
    explanation:{verdict:'Sell: Percentage Decline Is Not a Buy Signal',summary:'A stock being "down 80%" tells you nothing about the future. Without MACD divergence or SMA stabilization, further downside is likely.',details:"Many beginners see an 80% decline and think it must be a buy. But SHOP showed zero technical evidence of a bottom: no MACD divergence, no SMA flattening, no volume capitulation signal. The amount a stock has fallen is irrelevant to its future direction. Only indicators and price action matter.",outcome:'SHOP continued declining further before eventually stabilizing months later at even lower prices.',lesson:'Never buy based on how far a stock has fallen. Only buy when indicators show reversal evidence: MACD divergence, SMA flattening, or volume capitulation.',indicatorBreakdown:[{name:'RSI: ~25',signal:'neutral',reading:'Deeply oversold, but without divergence this is just a weak stock getting weaker.'},{name:'MACD: No Divergence',signal:'bearish',reading:'No higher lows in MACD = no evidence sellers are exhausting.'},{name:'Steep SMA Decline',signal:'bearish',reading:'Both SMAs falling steeply = the trend is firmly and structurally down.'}]},
    decisionFeedback:{buy:{quality:'weak',feedback:'A big decline alone is not a reason to buy. You need technical evidence of a bottom forming.'},sell:{quality:'strong',feedback:'Disciplined. Resisting the "it has fallen so much" urge without technical confirmation is a key intermediate skill.'}}},

  {id:26,stock:'Roku Inc.',ticker:'ROKU',date:'July 2021',timeframe:'Daily',difficulty:'Intermediate',
    question:'Roku has been on a massive run and is pulling back from highs. RSI is around 45. Is this a healthy dip to buy?',
    correctAnswer:'sell',signalQuality:'moderate',
    indicators:{rsi:{label:'RSI (14)',note:'Around 45, neutral, dropped from overbought levels'},macd:{label:'MACD (12,26,9)',note:'Just crossed below signal line, fresh bearish crossover'},sma:{label:'50 & 200 SMA',note:'Price recently broke below the 50-day SMA, first warning sign'}},
    explanation:{verdict:'Moderate Sell Signal',summary:'The MACD bearish crossover combined with a break below the 50-day SMA signaled the end of the rally, not a healthy dip.',details:"ROKU was a COVID darling that peaked and started rolling over. RSI dropping from overbought to 45 might look like a healthy pullback, but the MACD bearish crossover and 50-day SMA break were early warning signs that the trend was changing. In growth stocks, these breaks often accelerate.",outcome:'ROKU peaked near $490 and eventually fell to under $40, losing over 90% of its value.',lesson:'A fresh MACD bearish crossover + breaking below the 50-day SMA in a growth stock is often the beginning of a major trend change, not a dip to buy.',indicatorBreakdown:[{name:'RSI: ~45',signal:'neutral',reading:'Looks like a healthy pullback, but context matters.'},{name:'MACD: Bearish Crossover',signal:'bearish',reading:'Fresh crossover confirms momentum has shifted from buyers to sellers.'},{name:'50-Day SMA Break',signal:'bearish',reading:'First major support broken. Often the beginning of a larger decline.'}]},
    decisionFeedback:{buy:{quality:'weak',feedback:'Buying a "dip" when MACD has crossed bearish and the 50-day SMA is broken is a common mistake in growth stocks.'},sell:{quality:'strong',feedback:'Good pattern recognition. MACD bearish crossover + 50-SMA break in growth stocks often signals major trend changes.'}}},

  {id:27,stock:'Salesforce Inc.',ticker:'CRM',date:'December 2022',timeframe:'Daily',difficulty:'Intermediate',
    question:'Salesforce gapped up 10% on activist investor news. RSI jumped from neutral to overbought in one move. Buy the momentum or fade it?',
    correctAnswer:'buy',signalQuality:'moderate',
    indicators:{rsi:{label:'RSI (14)',note:'Jumped above 70, overbought, but from a catalyst event'},macd:{label:'MACD (12,26,9)',note:'Just crossed above signal line on the gap, fresh bullish crossover'},sma:{label:'50 & 200 SMA',note:'Price broke above the 200-day SMA on the gap, reclaiming major resistance'}},
    explanation:{verdict:'Moderate Buy Signal',summary:'A gap up that reclaims the 200-day SMA on a fundamental catalyst (activist investor) often signals the start of a new uptrend, despite overbought RSI.',details:"This is the opposite of the PYPL earnings gap down. A catalyst gap UP that reclaims major resistance (200-day SMA) is bullish. The MACD bullish crossover confirmed the momentum shift. Overbought RSI from a gap is different from overbought from a gradual rally. Gap-driven overbought often leads to follow-through.",outcome:'CRM continued rallying from ~$140 to over $200 in the following months (+43%).',lesson:'Gap ups that reclaim major SMAs on fundamental catalysts often lead to sustained rallies. Overbought RSI from a gap is not the same as from a gradual rise.',indicatorBreakdown:[{name:'RSI: Overbought from Gap',signal:'bullish',reading:'Gap-driven overbought often leads to continuation, not reversal.'},{name:'MACD: Fresh Bullish Cross',signal:'bullish',reading:'Momentum shifted decisively to buyers.'},{name:'200-SMA Reclaimed',signal:'bullish',reading:'Breaking above the 200-day on a catalyst signals a regime change.'}]},
    decisionFeedback:{buy:{quality:'strong',feedback:'Advanced thinking. Recognizing that catalyst gap ups above the 200-SMA often lead to continuation is a key skill.'},sell:{quality:'weak',feedback:'Fading a catalyst gap that reclaimed the 200-day SMA fights the new momentum.'}}},

  {id:28,stock:'Costco Wholesale',ticker:'COST',date:'March 2023',timeframe:'Daily',difficulty:'Intermediate',
    question:'Costco is near all-time highs. RSI is around 60 and MACD is positive. The trend is clearly up, but is it too late to buy?',
    correctAnswer:'buy',signalQuality:'strong',
    indicators:{rsi:{label:'RSI (14)',note:'Around 60, bullish but not overbought, healthy momentum'},macd:{label:'MACD (12,26,9)',note:'Above zero and above signal line, sustained positive momentum'},sma:{label:'50 & 200 SMA',note:'Both rising, price above both, textbook uptrend'}},
    explanation:{verdict:'Strong Buy Signal: Trend Following',summary:'All indicators aligned bullish in a healthy uptrend. "Too high" is not a technical signal. The trend is your friend until it ends.',details:"Costco showed a perfect uptrend with RSI at 60 (healthy), MACD positive (confirmed), and rising SMAs (structural). Many traders avoid buying near highs, but stocks in strong uptrends tend to keep making new highs. There is no technical sell signal present.",outcome:'COST continued its uptrend, making new all-time highs over the following months.',lesson:'Never avoid buying just because a stock is near highs. If indicators are healthy and the trend is intact, the trend is more likely to continue than reverse.',indicatorBreakdown:[{name:'RSI: ~60',signal:'bullish',reading:'Healthy bullish reading with room to run before overbought.'},{name:'MACD: Positive',signal:'bullish',reading:'Sustained positive momentum confirms the uptrend.'},{name:'Rising SMAs',signal:'bullish',reading:'Both averages trending up = structural bull trend.'}]},
    decisionFeedback:{buy:{quality:'strong',feedback:'Excellent trend-following discipline. Buying healthy uptrends near highs is how professional traders operate.'},sell:{quality:'weak',feedback:'Selling a healthy uptrend with aligned bullish indicators just because the price is "high" is a beginner mistake.'}}},

  {id:29,stock:'Uber Technologies',ticker:'UBER',date:'February 2023',timeframe:'Daily',difficulty:'Intermediate',
    question:'Uber has been recovering from lows and just crossed above its 200-day SMA for the first time in months. RSI is rising. What does this mean?',
    correctAnswer:'buy',signalQuality:'strong',
    indicators:{rsi:{label:'RSI (14)',note:'Around 58, rising from below 50, momentum building'},macd:{label:'MACD (12,26,9)',note:'Just crossed above zero, shifting from bearish to bullish territory'},sma:{label:'50 & 200 SMA',note:'Price broke above 200-day SMA, 50-day SMA curling up toward Golden Cross'}},
    explanation:{verdict:'Strong Buy Signal: Trend Reversal',summary:'Breaking above the 200-day SMA with rising RSI and MACD crossing into positive territory are classic signals of a new uptrend beginning.',details:"Uber had been in recovery mode after its 2022 lows. The 200-day SMA breakout was the key signal. RSI rising through 50 confirmed bullish momentum. MACD crossing above zero shifted the regime from bearish to bullish. The 50-day SMA curling up suggested a Golden Cross was forming.",outcome:'UBER rallied strongly, nearly doubling from ~$33 to over $60 in the following 10 months.',lesson:'Price crossing above the 200-day SMA + RSI rising above 50 + MACD crossing zero = triple confirmation of a new uptrend.',indicatorBreakdown:[{name:'RSI: ~58, Rising',signal:'bullish',reading:'Rising through 50 confirms shift from bearish to bullish momentum.'},{name:'MACD: Crossing Zero',signal:'bullish',reading:'Zero line cross = regime change from bearish to bullish.'},{name:'200-SMA Breakout',signal:'bullish',reading:'Most significant support/resistance level. Breaking above signals a new trend.'}]},
    decisionFeedback:{buy:{quality:'strong',feedback:'Textbook trend reversal identification. Triple confirmation (RSI, MACD, SMA) is as clear as it gets.'},sell:{quality:'weak',feedback:'Selling against a triple bullish confirmation (RSI rising, MACD crossing zero, 200-SMA breakout) fights all the evidence.'}}},

  {id:30,stock:'Nike Inc.',ticker:'NKE',date:'September 2022',timeframe:'Daily',difficulty:'Intermediate',
    question:'Nike has been declining and just reported disappointing inventory numbers. RSI is around 30. Buy the dip on a brand-name stock?',
    correctAnswer:'sell',signalQuality:'strong',
    indicators:{rsi:{label:'RSI (14)',note:'Around 30, oversold, but after a fundamental catalyst'},macd:{label:'MACD (12,26,9)',note:'Deeply negative, accelerating lower, no divergence'},sma:{label:'50 & 200 SMA',note:'Both declining, Death Cross active, structural downtrend'}},
    explanation:{verdict:'Strong Sell Signal',summary:'Oversold RSI at 30 after a negative fundamental catalyst (bad inventory data) in an existing downtrend is a continuation signal, not a reversal.',details:"Nike reported bloated inventory, a sign of weakening demand. RSI at 30 might tempt buyers, but this was caused by a fresh negative catalyst reinforcing the existing downtrend. MACD accelerating lower showed sellers gaining momentum, not losing it. Brand name does not equal buy signal.",outcome:'NKE continued declining from ~$85 to under $70 over the following months.',lesson:'Oversold RSI caused by a negative fundamental catalyst in an existing downtrend is bearish, not bullish. Do not buy the dip on bad news.',indicatorBreakdown:[{name:'RSI: ~30',signal:'neutral',reading:'Oversold, but from a catalyst that confirms the bearish thesis.'},{name:'MACD: Accelerating Lower',signal:'bearish',reading:'Getting more negative = sellers gaining strength, not exhausting.'},{name:'Death Cross Active',signal:'bearish',reading:'Structural downtrend confirmed, fundamental news reinforces it.'}]},
    decisionFeedback:{buy:{quality:'weak',feedback:'Buying oversold after a negative catalyst in a downtrend is a value trap. Brand names can keep falling.'},sell:{quality:'strong',feedback:'Good discipline. Recognizing that fresh bad news in a downtrend strengthens the sell case.'}}},

  {id:31,stock:'Airbnb Inc.',ticker:'ABNB',date:'May 2022',timeframe:'Daily',difficulty:'Intermediate',
    question:'Airbnb has dropped 50% from its highs. RSI is low and MACD shows a faint hint of divergence. Is a bottom forming?',
    correctAnswer:'sell',signalQuality:'moderate',
    indicators:{rsi:{label:'RSI (14)',note:'Around 28, deeply oversold'},macd:{label:'MACD (12,26,9)',note:'Very slightly higher low vs previous dip, faint divergence hint'},sma:{label:'50 & 200 SMA',note:'Both declining sharply, Death Cross confirmed, strong downtrend'}},
    explanation:{verdict:'Sell: Faint Divergence Is Not Enough',summary:'A very slight MACD divergence is not reliable when the Death Cross is active and SMAs are declining sharply. Strong divergence is needed for high-conviction bottoms.',details:"ABNB showed a barely perceptible MACD divergence. Compare to Meta (scenario 5) where the divergence was clear and RSI was at an extreme 20. Here, the divergence was faint, SMAs were declining sharply, and the Death Cross was fully confirmed. A faint divergence in a strong downtrend often fails.",outcome:'ABNB continued declining another 20% before eventually bottoming.',lesson:'Divergence strength matters. Faint divergence with declining SMAs and an active Death Cross is unreliable. Look for clear, obvious divergence.',indicatorBreakdown:[{name:'RSI: ~28',signal:'neutral',reading:'Deeply oversold, but not extreme enough for capitulation.'},{name:'MACD: Faint Divergence',signal:'neutral',reading:'Barely visible. Strong bottoms need clear, obvious divergence.'},{name:'Declining SMAs',signal:'bearish',reading:'Steep decline in both SMAs means the structural trend is strongly down.'}]},
    decisionFeedback:{buy:{quality:'weak',feedback:'Faint divergence in a strong downtrend with declining SMAs is unreliable. Wait for clearer signals.'},sell:{quality:'strong',feedback:'Good judgment. Recognizing that faint divergence is insufficient shows analytical maturity.'}}},

  {id:32,stock:'Snap Inc.',ticker:'SNAP',date:'July 2022',timeframe:'Daily',difficulty:'Intermediate',
    question:'Snap has been in freefall, dropping over 85% from highs. RSI is deeply oversold. Every indicator is bearish. Is it time to bottom-fish?',
    correctAnswer:'sell',signalQuality:'strong',
    indicators:{rsi:{label:'RSI (14)',note:'Below 25, extremely oversold'},macd:{label:'MACD (12,26,9)',note:'Deeply negative, no divergence, continued deterioration'},sma:{label:'50 & 200 SMA',note:'Both in steep decline, price far below both, no support anywhere'}},
    explanation:{verdict:'Strong Sell Signal',summary:'Extreme oversold in a stock with deteriorating fundamentals and zero technical reversal signals is a value trap, not a buying opportunity.',details:"Snap was losing the competition to TikTok and ad revenue was declining. Every indicator was deeply bearish with no divergence. Just because a stock has fallen 85% does not mean it cannot fall another 50%. Without any technical evidence of a bottom, buying is pure speculation.",outcome:'SNAP continued to struggle, eventually falling below $8 from the ~$12 level.',lesson:'Extreme oversold in a fundamentally challenged company without MACD divergence is not a buy signal. Some stocks deserve to be down.',indicatorBreakdown:[{name:'RSI: Below 25',signal:'neutral',reading:'Extreme, but without divergence in a challenged company, it just means weak.'},{name:'MACD: No Divergence',signal:'bearish',reading:'Continued deterioration with no bottom signal.'},{name:'No SMA Support',signal:'bearish',reading:'Price far below all moving averages with nothing to stop the decline.'}]},
    decisionFeedback:{buy:{quality:'weak',feedback:'Bottom-fishing without technical confirmation in a fundamentally challenged stock is gambling, not trading.'},sell:{quality:'strong',feedback:'Disciplined. Not every oversold stock is a buy. Fundamentals and divergence matter.'}}},

  {id:33,stock:'Coinbase Global',ticker:'COIN',date:'June 2022',timeframe:'Daily',difficulty:'Intermediate',
    question:'Coinbase has crashed alongside crypto. RSI is near extreme lows during the crypto winter. Buy the capitulation?',
    correctAnswer:'sell',signalQuality:'moderate',
    indicators:{rsi:{label:'RSI (14)',note:'Near 20, extremely oversold as crypto collapses'},macd:{label:'MACD (12,26,9)',note:'Deeply negative, accelerating down, no divergence whatsoever'},sma:{label:'50 & 200 SMA',note:'Both in steep decline, price far below, structural bear market'}},
    explanation:{verdict:'Sell: Sector Contagion',summary:'When an entire sector (crypto) is in a bear market, individual stocks within it are unlikely to bottom before the sector does. COIN was hostage to crypto prices.',details:"Coinbase is a crypto exchange. Its revenue depends on crypto trading volume and prices. With Bitcoin and Ethereum in freefall, buying COIN was betting on a crypto recovery with zero technical evidence. MACD showed no divergence, and the stock was in structural decline.",outcome:'COIN continued falling from ~$52 to under $35 as the crypto winter deepened.',lesson:'When a stock is hostage to a sector in collapse, its individual indicators are less important. The sector must bottom first.',indicatorBreakdown:[{name:'RSI: ~20',signal:'neutral',reading:'Extreme, but driven by sector collapse. Individual stock RSI is less meaningful here.'},{name:'MACD: Accelerating Down',signal:'bearish',reading:'Getting worse, not better. No evidence of a bottom.'},{name:'Sector Bear Market',signal:'bearish',reading:'Crypto in freefall means COIN has no independent catalyst to reverse.'}]},
    decisionFeedback:{buy:{quality:'weak',feedback:'Buying a stock hostage to a collapsing sector without sector-level reversal signals is premature.'},sell:{quality:'strong',feedback:'Smart sector awareness. Individual stock signals matter less when the entire sector is in a bear market.'}}},

  {id:34,stock:'Zoom Video',ticker:'ZM',date:'May 2022',timeframe:'Daily',difficulty:'Intermediate',
    question:'Zoom has fallen 80% from its pandemic highs. RSI is low and the stock seems cheap. Is this a contrarian buy?',
    correctAnswer:'sell',signalQuality:'strong',
    indicators:{rsi:{label:'RSI (14)',note:'Around 30, oversold after persistent decline'},macd:{label:'MACD (12,26,9)',note:'Negative with no bullish divergence, steady decline'},sma:{label:'50 & 200 SMA',note:'Both declining, Death Cross confirmed, price well below both'}},
    explanation:{verdict:'Strong Sell Signal',summary:'A former pandemic darling with structurally declining growth and zero reversal signals is a value trap, not a contrarian buy.',details:"Zoom saw explosive growth during COVID but was losing relevance as offices reopened. The technical picture showed no bottom signals: RSI oversold without divergence, MACD declining, Death Cross active. Contrarian buying requires technical evidence of a turn, not just a big decline.",outcome:'ZM continued declining, eventually falling below $60 from ~$100 as growth decelerated.',lesson:'Being a contrarian requires evidence, not just a gut feeling that something is cheap. Without technical reversal signals, cheap stocks get cheaper.',indicatorBreakdown:[{name:'RSI: ~30',signal:'neutral',reading:'Oversold, but without divergence in a structural decline.'},{name:'MACD: Steady Decline',signal:'bearish',reading:'No bullish divergence, no crossover attempt. Sellers in control.'},{name:'Death Cross',signal:'bearish',reading:'Structural downtrend with declining fundamentals.'}]},
    decisionFeedback:{buy:{quality:'weak',feedback:'Contrarian buying without technical confirmation is hope-based trading. The chart gives no buy signal.'},sell:{quality:'strong',feedback:'Excellent discipline. Not buying a structural decline just because it looks cheap is a key intermediate skill.'}}},

  // ===== ADVANCED (35-44) =====

  {id:35,stock:'Goldman Sachs',ticker:'GS',date:'March 2023',timeframe:'Daily',difficulty:'Advanced',
    question:'Goldman Sachs dropped sharply on banking crisis fears but shows MACD divergence. The banking sector is under stress. What do you do?',
    correctAnswer:'buy',signalQuality:'moderate',
    indicators:{rsi:{label:'RSI (14)',note:'Dropped to near 25, deeply oversold from panic selling'},macd:{label:'MACD (12,26,9)',note:'While price made new lows, MACD made a higher low, classic bullish divergence'},sma:{label:'50 & 200 SMA',note:'Price broke below 200-day SMA, but on panic, not trend deterioration'}},
    explanation:{verdict:'Moderate Buy: Divergence in Panic',summary:'MACD bullish divergence during sector panic in a fundamentally sound company is a high-conviction but high-risk buy signal.',details:"The SVB crisis caused panic in all bank stocks. Goldman Sachs, a well-capitalized investment bank, was sold off indiscriminately. The key: while price made lower lows, MACD made higher lows. This divergence in the context of panic selling signals that sellers are exhausting even as fear peaks. Compare to scenario 5 (META) for a similar divergence setup.",outcome:'GS recovered from ~$300 to over $350 in the following 3 months (+17%).',lesson:'MACD bullish divergence during sector panic in fundamentally sound companies creates excellent risk-reward opportunities.',indicatorBreakdown:[{name:'RSI: ~25',signal:'bullish',reading:'Deeply oversold from panic, not fundamental deterioration.'},{name:'MACD: Bullish Divergence',signal:'bullish',reading:'Higher MACD lows while price makes lower lows = sellers exhausting.'},{name:'200-SMA Break on Panic',signal:'neutral',reading:'Panic-driven breaks often recover. Different from trend-driven breaks.'}]},
    decisionFeedback:{buy:{quality:'strong',feedback:'Advanced pattern recognition. MACD divergence during sector panic in quality names is one of the best setups.'},sell:{quality:'weak',feedback:'Missing the MACD divergence during panic. This was sellers exhausting, not the start of a new downtrend.'}}},

  {id:36,stock:'Apple Inc.',ticker:'AAPL',date:'September 2020',timeframe:'Daily',difficulty:'Advanced',
    question:'Apple has surged 120% since the COVID low and just completed a stock split. RSI is extremely overbought at 83. Sell the news?',
    correctAnswer:'sell',signalQuality:'strong',
    indicators:{rsi:{label:'RSI (14)',note:'At 83, extremely overbought, rarely sustained at these levels'},macd:{label:'MACD (12,26,9)',note:'Very positive but showing signs of flattening, momentum peak'},sma:{label:'50 & 200 SMA',note:'Price extremely extended above both SMAs, massive deviation from mean'}},
    explanation:{verdict:'Strong Sell Signal: Sell the News',summary:'RSI at 83 after a stock split "sell the news" event with extreme SMA extension and MACD peaking is a textbook profit-taking setup.',details:"Apple surged into its stock split on retail investor excitement. RSI at 83 is unsustainable. MACD flattening at extreme levels signals the momentum peak. The massive distance above the 200-day SMA created powerful reversion pressure. Stock splits are classic 'buy the rumor, sell the news' events.",outcome:'AAPL pulled back ~20% from ~$137 to ~$110 over the following month.',lesson:'RSI above 80 + MACD peaking + extreme SMA extension + news event = high-probability sell signal.',indicatorBreakdown:[{name:'RSI: 83',signal:'bearish',reading:'Extremely overbought. Readings above 80 rarely sustain, especially after news events.'},{name:'MACD: Peaking',signal:'bearish',reading:'Flattening at extreme levels signals the momentum high.'},{name:'Extreme SMA Deviation',signal:'bearish',reading:'Massive extension above the mean creates powerful reversion pressure.'}]},
    decisionFeedback:{buy:{quality:'weak',feedback:'Buying at RSI 83 after a stock split is the textbook definition of buying the top.'},sell:{quality:'strong',feedback:'Excellent timing instinct. Recognizing the sell-the-news setup with extreme indicators is advanced pattern recognition.'}}},

  {id:37,stock:'Tesla Inc.',ticker:'TSLA',date:'January 2023',timeframe:'Daily',difficulty:'Advanced',
    question:'Tesla has crashed 70% from highs. RSI shows oversold with faint divergence forming. But MACD is still deeply negative. Bottom or trap?',
    correctAnswer:'buy',signalQuality:'moderate',
    indicators:{rsi:{label:'RSI (14)',note:'Near 25, deeply oversold after capitulation selling'},macd:{label:'MACD (12,26,9)',note:'Deeply negative, but histogram bars are starting to shrink'},sma:{label:'50 & 200 SMA',note:'Both declining, but rate of decline is slowing'}},
    explanation:{verdict:'Moderate Buy: Early Bottom',summary:'Deeply oversold RSI with MACD histogram shrinking and SMA decline rate slowing are early signs of a bottom. Not high-conviction, but the risk-reward shifts bullish.',details:"Tesla had been in freefall, losing 70% of its value. At this point, RSI was deeply oversold and MACD histogram bars were starting to shrink (less negative each day). This is an early bottom signal. The SMA decline rate slowing added confirmation. While not as clear as a full MACD divergence, the combination suggested sellers were running out of stock to sell.",outcome:'TSLA rallied from ~$108 to over $200 in the following 3 months (+85%).',lesson:'Early bottom signals: deeply oversold RSI + shrinking MACD histogram + slowing SMA decline. Not as reliable as full divergence, but the risk-reward can be excellent.',indicatorBreakdown:[{name:'RSI: ~25',signal:'bullish',reading:'Deeply oversold in a high-profile stock after capitulation selling.'},{name:'MACD: Histogram Shrinking',signal:'bullish',reading:'Each bar less negative = selling pressure diminishing.'},{name:'SMA Decline Slowing',signal:'neutral',reading:'Rate of decline decreasing is an early signal of trend exhaustion.'}]},
    decisionFeedback:{buy:{quality:'strong',feedback:'Advanced bottom identification. Recognizing early signals (shrinking histogram, slowing SMA decline) shows experienced pattern reading.'},sell:{quality:'weak',feedback:'While the downtrend was intact, the early reversal signals (shrinking MACD, slowing SMA decline) warranted a contrarian buy.'}}},

  {id:38,stock:'iShares Russell 2000',ticker:'IWM',date:'June 2022',timeframe:'Daily',difficulty:'Advanced',
    question:'Small caps have been underperforming large caps badly. IWM shows a Death Cross while SPY is only in correction mode. What does this divergence mean?',
    correctAnswer:'sell',signalQuality:'strong',
    indicators:{rsi:{label:'RSI (14)',note:'Around 33, weak and declining, approaching oversold'},macd:{label:'MACD (12,26,9)',note:'Below zero and declining, sustained bearish momentum'},sma:{label:'50 & 200 SMA',note:'Death Cross active, price below both, structural bear market in small caps'}},
    explanation:{verdict:'Strong Sell Signal: Market Breadth Deterioration',summary:'Small caps leading the decline is a bearish signal for the broader market. When IWM has a Death Cross before SPY, it signals deeper market weakness.',details:"IWM (Russell 2000) is a market breadth indicator. Small caps are more sensitive to economic conditions. When small caps are in a Death Cross while large caps are only correcting, it signals the economy is weakening and the selloff will likely spread. This is an advanced breadth analysis concept.",outcome:'IWM continued falling and the broader market selloff accelerated over the following months.',lesson:'Small cap weakness (IWM Death Cross) leading large cap weakness is a powerful bearish signal for the entire market. Market breadth matters.',indicatorBreakdown:[{name:'RSI: ~33',signal:'bearish',reading:'Weak and declining, approaching oversold but not there yet.'},{name:'MACD: Declining Below Zero',signal:'bearish',reading:'Sustained selling pressure with no reversal signals.'},{name:'Death Cross',signal:'bearish',reading:'Structural bear market in small caps signals broader economic weakness.'}]},
    decisionFeedback:{buy:{quality:'weak',feedback:'Buying small caps in a Death Cross when they are leading the market lower fights the breadth signal.'},sell:{quality:'strong',feedback:'Advanced breadth analysis. Recognizing small cap leadership in declines as a bearish market signal is expert-level thinking.'}}},

  {id:39,stock:'iShares 20+ Year Treasury',ticker:'TLT',date:'October 2022',timeframe:'Daily',difficulty:'Advanced',
    question:'Long-term Treasury bonds have had their worst year in history. TLT is in freefall with RSI showing extreme oversold. Is this the bond bottom?',
    correctAnswer:'buy',signalQuality:'moderate',
    indicators:{rsi:{label:'RSI (14)',note:'Below 20, historically extreme, once-in-a-generation reading'},macd:{label:'MACD (12,26,9)',note:'Deeply negative, but showing faint higher lows on the histogram'},sma:{label:'50 & 200 SMA',note:'Both in steep decline, but rate of decline is starting to slow'}},
    explanation:{verdict:'Moderate Buy: Extreme Capitulation in Bonds',summary:'RSI below 20 in a broad Treasury ETF is a once-in-a-generation reading. While the trend was still down, the extreme oversold condition created a high-probability mean-reversion opportunity.',details:"TLT had its worst year ever due to aggressive Fed rate hikes. RSI below 20 in government bonds is extraordinary. Unlike individual stocks, Treasury bonds cannot go to zero. MACD histogram showed faint higher lows, and the rate of SMA decline was slowing. The risk-reward for a mean-reversion trade was compelling.",outcome:'TLT bounced strongly from ~$94 to over $107 in the following 2 months (+14%).',lesson:'Extreme oversold conditions (RSI below 20) in broad, systemic instruments (government bonds, major indices) are among the most reliable mean-reversion signals in finance.',indicatorBreakdown:[{name:'RSI: Below 20',signal:'bullish',reading:'Once-in-a-generation extreme in government bonds. Mean reversion is almost certain.'},{name:'MACD: Faint Divergence',signal:'bullish',reading:'Subtle higher lows on histogram = selling exhaustion beginning.'},{name:'SMA Decline Slowing',signal:'neutral',reading:'Rate of change matters. The decline is decelerating.'}]},
    decisionFeedback:{buy:{quality:'strong',feedback:'Advanced. Recognizing that extreme oversold in systemic instruments (government bonds) is different from individual stocks shows macro awareness.'},sell:{quality:'weak',feedback:'RSI below 20 in Treasury bonds is a once-in-a-generation mean-reversion opportunity. Treasury bonds cannot go to zero.'}}},

  {id:40,stock:'SPDR Gold Shares',ticker:'GLD',date:'March 2022',timeframe:'Daily',difficulty:'Advanced',
    question:'Gold has surged to near all-time highs as inflation fears peak and war breaks out in Ukraine. RSI is overbought. Buy the safe haven or sell the spike?',
    correctAnswer:'sell',signalQuality:'moderate',
    indicators:{rsi:{label:'RSI (14)',note:'Above 75, overbought on a fear-driven spike'},macd:{label:'MACD (12,26,9)',note:'Extremely positive but showing classic divergence: higher price, lower MACD peak'},sma:{label:'50 & 200 SMA',note:'Price extended above both SMAs, but both SMAs rising (uptrend intact)'}},
    explanation:{verdict:'Moderate Sell: Fear Spike Reversal',summary:'MACD bearish divergence (higher price highs with lower MACD highs) combined with overbought RSI on a geopolitical fear spike signals a pullback.',details:"Gold spiked on Ukraine war fears and inflation concerns. While gold was in an uptrend (rising SMAs), the RSI was overbought and MACD showed bearish divergence. This is the key advanced concept: even in uptrends, MACD divergence at overbought RSI signals a pullback. Fear-driven spikes in gold often reverse once the initial panic subsides.",outcome:'GLD pulled back from ~$193 to ~$162 over the following months (-16%).',lesson:'MACD bearish divergence (price making higher highs, MACD making lower highs) at overbought RSI signals a pullback, even in uptrends. Fear spikes often reverse.',indicatorBreakdown:[{name:'RSI: ~75',signal:'bearish',reading:'Overbought on a fear spike. Fear-driven moves tend to reverse.'},{name:'MACD: Bearish Divergence',signal:'bearish',reading:'Price higher high but MACD lower high = momentum weakening despite new price highs.'},{name:'Uptrend Intact',signal:'neutral',reading:'SMAs still rising, so this is a pullback within an uptrend, not a trend reversal.'}]},
    decisionFeedback:{buy:{quality:'weak',feedback:'Buying overbought gold with MACD bearish divergence on a fear spike is buying the top of the panic trade.'},sell:{quality:'strong',feedback:'Excellent. Identifying MACD divergence at overbought levels in a fear spike is advanced technical analysis.'}}},

  {id:41,stock:'Energy Select Sector',ticker:'XLE',date:'June 2022',timeframe:'Daily',difficulty:'Advanced',
    question:'Energy stocks have been the best sector for 18 months. XLE is up 150%+. RSI recently peaked above 80. Now MACD is crossing bearish. What now?',
    correctAnswer:'sell',signalQuality:'strong',
    indicators:{rsi:{label:'RSI (14)',note:'Recently pulled back from above 80 to ~65, still elevated'},macd:{label:'MACD (12,26,9)',note:'Fresh bearish crossover: MACD line crossed below signal line'},sma:{label:'50 & 200 SMA',note:'Both rising, price above both, but momentum is shifting'}},
    explanation:{verdict:'Strong Sell Signal: MACD Confirms RSI Reversal',summary:'When RSI pulls back from extreme overbought AND MACD confirms with a bearish crossover, it is the strongest sell signal, even in an uptrend.',details:"XLE had an incredible 18-month run. RSI peaked above 80 and pulled back. Many traders dismiss this. But when MACD then crosses bearish, it confirms the momentum shift. This is different from scenario 6 (NVDA) where MACD never crossed bearish. Here, the MACD crossover was the confirmation that the rally was ending.",outcome:'XLE dropped over 25% from its highs over the following 3 months.',lesson:'RSI pulling back from 80+ is a warning. MACD bearish crossover is the confirmation. Together, they are a strong sell even in the strongest uptrends.',indicatorBreakdown:[{name:'RSI: Pulled From 80+',signal:'bearish',reading:'RSI leaving extreme overbought = momentum peak passed.'},{name:'MACD: Bearish Crossover',signal:'bearish',reading:'Confirmation. MACD crossing below signal line proves the momentum shift is real.'},{name:'Rising SMAs',signal:'neutral',reading:'Uptrend structure still intact, but momentum leading price means SMAs will eventually follow.'}]},
    decisionFeedback:{buy:{quality:'weak',feedback:'Buying after RSI pulled from 80+ with a MACD bearish crossover is ignoring two clear sell signals.'},sell:{quality:'strong',feedback:'Excellent. Using MACD crossover to confirm the RSI overbought reversal is the advanced way to time exits.'}}},

  {id:42,stock:'ARK Innovation ETF',ticker:'ARKK',date:'January 2022',timeframe:'Daily',difficulty:'Advanced',
    question:'ARK Innovation ETF has been falling from its 2021 highs. RSI briefly touched oversold and bounced. MACD shows a slight bullish crossover. Is this the reversal?',
    correctAnswer:'sell',signalQuality:'false_signal',
    indicators:{rsi:{label:'RSI (14)',note:'Bounced from 30 to about 42, brief oversold relief'},macd:{label:'MACD (12,26,9)',note:'Slight bullish crossover, but both lines still deeply negative'},sma:{label:'50 & 200 SMA',note:'Both declining sharply, Death Cross active, strong structural downtrend'}},
    explanation:{verdict:'False Signal: Bear Market Rally Trap',summary:'A slight MACD bullish crossover while BOTH MACD lines remain deeply negative is a bear market rally signal, not a trend reversal.',details:"This is a critical advanced concept: MACD can cross bullish while still being deeply negative. This means selling momentum slowed slightly, not that buying momentum has begun. Both MACD lines deep in negative territory = bear market. The crossover is just a less-negative reading. Add declining SMAs and a Death Cross, and this is clearly a trap.",outcome:'ARKK continued its collapse, eventually falling to ~$30 from ~$80 at this point (-63%).',lesson:'A MACD bullish crossover deep in negative territory is a bear rally, not a reversal. True reversals need MACD to cross the ZERO line.',indicatorBreakdown:[{name:'RSI: ~42',signal:'neutral',reading:'Bounced from oversold but stayed below 50. Not bullish.'},{name:'MACD: Cross While Negative',signal:'bearish',reading:'Both lines below zero = bear market. The crossover just means "less bearish" not "bullish."'},{name:'Death Cross Active',signal:'bearish',reading:'Structural downtrend. Bear rallies within downtrends are traps.'}]},
    decisionFeedback:{buy:{quality:'weak',feedback:'MACD crossing while both lines are deeply negative is a bear rally trap. Wait for the zero line cross.'},sell:{quality:'strong',feedback:'Advanced understanding. Distinguishing between MACD signal-line crosses (minor) and zero-line crosses (major) is crucial.'}}},

  {id:43,stock:'Meta Platforms',ticker:'META',date:'April 2023',timeframe:'Daily',difficulty:'Advanced',
    question:'Meta has recovered 150% from its $88 low. RSI is approaching 70. After such a massive recovery, is it time to take profits?',
    correctAnswer:'buy',signalQuality:'false_signal',
    indicators:{rsi:{label:'RSI (14)',note:'Around 68, approaching overbought, but in a new uptrend'},macd:{label:'MACD (12,26,9)',note:'Strongly positive, well above zero, rising momentum'},sma:{label:'50 & 200 SMA',note:'Golden Cross recently formed, both SMAs rising, new bull trend'}},
    explanation:{verdict:'False Sell Signal: New Trend, Not Overbought',summary:'RSI near 70 in a newly confirmed uptrend (Golden Cross + rising MACD) is bullish momentum, not a sell signal. The context of a new trend changes everything.',details:"Meta had recovered dramatically. RSI near 70 might seem like a sell. But a Golden Cross just formed, MACD was strongly positive and rising, and both SMAs were trending up. This was the beginning of a new bull trend, not the end of a rally. In new uptrends, RSI can stay elevated for months. See scenario 6 (NVDA) for a similar concept.",outcome:'META continued rallying from ~$240 to over $500 in the following year (+108%).',lesson:'RSI near 70 in a newly confirmed uptrend with a fresh Golden Cross is a sign of strength, not a reason to sell. New trends deserve the benefit of the doubt.',indicatorBreakdown:[{name:'RSI: ~68',signal:'bullish',reading:'Approaching overbought, but in a new uptrend this signals strength.'},{name:'MACD: Strongly Positive',signal:'bullish',reading:'Well above zero and rising = powerful buying momentum.'},{name:'Fresh Golden Cross',signal:'bullish',reading:'New bull trend confirmed. Trend changes deserve the benefit of the doubt.'}]},
    decisionFeedback:{buy:{quality:'strong',feedback:'Expert-level thinking. Trusting a new uptrend confirmed by a Golden Cross despite elevated RSI shows advanced understanding.'},sell:{quality:'weak',feedback:'Selling a fresh Golden Cross with strong MACD because RSI is near 70 is fighting the new trend.'}}},

  {id:44,stock:'NVIDIA Corporation',ticker:'NVDA',date:'March 2024',timeframe:'Daily',difficulty:'Advanced',
    question:'NVIDIA has more than tripled in a year on AI demand. RSI is elevated, MACD is extremely positive. Every indicator screams "overextended." What do you do?',
    correctAnswer:'buy',signalQuality:'false_signal',
    indicators:{rsi:{label:'RSI (14)',note:'Around 72, overbought, but has been elevated for months during the AI boom'},macd:{label:'MACD (12,26,9)',note:'Extremely positive, well above zero, no bearish crossover'},sma:{label:'50 & 200 SMA',note:'Both rising sharply, price above both, powerful uptrend'}},
    explanation:{verdict:'False Sell Signal: Paradigm Shifts Override Indicators',summary:'When a paradigm shift occurs (AI revolution), traditional overbought signals can stay extreme for far longer than normal. Without MACD bearish crossover, the trend is intact.',details:"NVIDIA was benefiting from a genuine paradigm shift in computing (AI). Traditional overbought signals assume mean reversion. But paradigm shifts create new fundamentals that can sustain elevated prices far longer than historical norms suggest. The key: NO MACD bearish crossover. Until momentum actually shifts, the trend wins.",outcome:'NVDA continued its surge, reaching new all-time highs as AI demand kept exceeding expectations.',lesson:'Paradigm shifts (internet 1999, smartphones 2007, AI 2023) can keep stocks overbought for years. Without MACD confirmation, overbought alone is not a sell signal in paradigm shifts.',indicatorBreakdown:[{name:'RSI: ~72',signal:'neutral',reading:'Traditionally overbought, but paradigm shifts sustain elevated readings.'},{name:'MACD: No Bearish Cross',signal:'bullish',reading:'Until MACD actually crosses bearish, momentum is intact.'},{name:'Rising SMAs',signal:'bullish',reading:'Both SMAs sharply rising = powerful structural uptrend.'}]},
    decisionFeedback:{buy:{quality:'strong',feedback:'Expert thinking. Recognizing paradigm shifts and trusting trend continuation until MACD actually crosses bearish.'},sell:{quality:'weak',feedback:'Selling based on overbought RSI alone without MACD confirmation during a paradigm shift is the most expensive mistake in markets.'}}},

  // ===== EXPERT (45-50) =====

  {id:45,stock:'S&P 500 ETF',ticker:'SPY',date:'December 2018',timeframe:'Daily',difficulty:'Expert',
    question:'The S&P 500 has plunged into Christmas Eve on Fed rate hike fears. A Death Cross just formed. RSI is near 20. Every indicator says sell. What do you do?',
    correctAnswer:'buy',signalQuality:'false_signal',
    indicators:{rsi:{label:'RSI (14)',note:'Near 20, extreme fear levels, near-capitulation'},macd:{label:'MACD (12,26,9)',note:'Deeply negative, Death Cross confirmed, everything technically bearish'},sma:{label:'50 & 200 SMA',note:'Death Cross active, price below both SMAs, structural bear signal'}},
    explanation:{verdict:'Expert Buy: Christmas Eve Capitulation',summary:'RSI near 20 in a broad market index on a specific catalyst (Fed policy) with sentiment at extremes marked a classic V-bottom.',details:"The Christmas Eve 2018 crash was a Fed-induced panic. RSI near 20 in the S&P 500 is a once-in-several-years event. The Death Cross was a lagging indicator confirming what already happened. The key expert insight: when the catalyst is identifiable and removable (the Fed could pivot), extreme fear creates the best buying opportunities. The Fed pivoted in January 2019.",outcome:'SPY rallied from ~$234 to over $290 in the following 4 months (+24%), one of the fastest recoveries in history.',lesson:'When broad market RSI is near 20 and the catalyst is a policy decision (which can be reversed), indicators are lagging. Extreme fear in broad indices is almost always a buy.',indicatorBreakdown:[{name:'RSI: ~20',signal:'bullish',reading:'Near-capitulation in the broad market. Historically one of the best buying signals.'},{name:'Death Cross',signal:'neutral',reading:'Lagging indicator. At crash lows, it confirms what happened, not what comes next.'},{name:'MACD: Deeply Negative',signal:'neutral',reading:'Also lagging. Extreme negative readings at crash lows precede sharp recoveries.'}]},
    decisionFeedback:{buy:{quality:'strong',feedback:'Expert-level thinking. Overriding bearish indicators at extreme broad market lows when the catalyst is a reversible policy decision.'},sell:{quality:'weak',feedback:'Following bearish indicators at extreme broad market lows is mechanical thinking. RSI near 20 in the S&P 500 is a once-in-years buying opportunity.'}}},

  {id:46,stock:'Invesco QQQ ETF',ticker:'QQQ',date:'March 2020 (COVID Crash)',timeframe:'Daily',difficulty:'Expert',
    question:'The Nasdaq has crashed 30% in three weeks. Circuit breakers are triggering daily. RSI is at historic lows. Is this the end of the tech bull market?',
    correctAnswer:'buy',signalQuality:'false_signal',
    indicators:{rsi:{label:'RSI (14)',note:'Below 15, among the most extreme readings in Nasdaq history'},macd:{label:'MACD (12,26,9)',note:'Most negative reading in years, deeply bearish'},sma:{label:'50 & 200 SMA',note:'Death Cross forming, price crashed below all support levels'}},
    explanation:{verdict:'Expert Buy: Historic Capitulation',summary:'RSI below 15 in a major index ETF is a once-in-a-decade event. Combined with circuit breakers and universal panic, this was a generational buying opportunity.',details:"The COVID crash created universal panic. RSI below 15 in QQQ had only happened a handful of times in history. Every prior instance preceded a major recovery. The expert insight: broad market indices represent entire economies. They do not go to zero. Extreme panic in diversified indices is mathematically the best time to buy.",outcome:'QQQ rallied over 100% from the March 2020 low within 12 months, the fastest recovery in Nasdaq history.',lesson:'The most profitable trades feel the most terrifying at the time. RSI below 15 in major indices has a near-perfect track record of preceding massive rallies.',indicatorBreakdown:[{name:'RSI: Below 15',signal:'bullish',reading:'Historic extreme. Every prior instance in major indices preceded a massive rally.'},{name:'All Indicators Bearish',signal:'neutral',reading:'At crash lows, all indicators are lagging. They confirm the crash, not the future.'},{name:'Circuit Breakers',signal:'bullish',reading:'Paradoxically, circuit breakers signal maximum panic, which is when bottoms form.'}]},
    decisionFeedback:{buy:{quality:'strong',feedback:'Elite-level contrarian thinking. Buying when every indicator is bearish and panic is at maximum requires understanding that indicators lag at extremes.'},sell:{quality:'weak',feedback:'RSI below 15 in QQQ has a near-perfect track record of preceding major rallies. Following indicators mechanically at extremes is the most costly mistake.'}}},

  {id:47,stock:'Tesla Inc.',ticker:'TSLA',date:'February 2020',timeframe:'Daily',difficulty:'Expert',
    question:'Tesla has surged 200% in 3 months. RSI is above 90. MACD is at the most extreme positive reading ever. This is clearly unsustainable. Sell?',
    correctAnswer:'buy',signalQuality:'false_signal',
    indicators:{rsi:{label:'RSI (14)',note:'Above 90, one of the most extreme overbought readings possible'},macd:{label:'MACD (12,26,9)',note:'Most positive reading in stock history, parabolic'},sma:{label:'50 & 200 SMA',note:'Price far above both, extreme extension, multi-standard deviation event'}},
    explanation:{verdict:'Expert Lesson: Short Squeezes Break All Rules',summary:'Tesla was experiencing a short squeeze combined with a fundamental paradigm shift. RSI above 90 in a short squeeze can persist because the buying is involuntary (forced short covering).',details:"Tesla in early 2020 was a massive short squeeze. 20%+ of the float was sold short. As price rose, shorts were forced to buy to cover losses, creating a self-reinforcing cycle. RSI above 90 in a squeeze is different from normal overbought because the buying pressure is involuntary. Shorts MUST buy regardless of price. This overrides all technical signals.",outcome:'TSLA continued surging another 50%+ before the COVID crash temporarily halted it. It later rose 10x from pre-squeeze levels.',lesson:'Short squeezes invalidate all traditional indicators. When short interest is extreme, overbought readings can persist and intensify because buying is forced, not optional.',indicatorBreakdown:[{name:'RSI: Above 90',signal:'neutral',reading:'In a short squeeze, extreme RSI can persist for weeks because buying is involuntary.'},{name:'MACD: Parabolic',signal:'neutral',reading:'Record readings in a squeeze reflect forced buying, not organic momentum.'},{name:'Extreme SMA Extension',signal:'neutral',reading:'Multi-standard deviation events happen in squeezes. Normal rules do not apply.'}]},
    decisionFeedback:{buy:{quality:'strong',feedback:'Expert thinking. Recognizing a short squeeze invalidates traditional indicator rules. The buying is forced, not voluntary.'},sell:{quality:'weak',feedback:'Selling into a short squeeze because indicators are overbought fights a mechanical force (forced covering) that overrides technical analysis.'}}},

  {id:48,stock:'GameStop Corp.',ticker:'GME',date:'January 2021',timeframe:'Daily',difficulty:'Expert',
    question:'GameStop has surged 1,700% in two weeks. RSI is off the charts. MACD is meaningless at these levels. Every rule says sell. But Reddit keeps buying. What do you do?',
    correctAnswer:'sell',signalQuality:'moderate',
    indicators:{rsi:{label:'RSI (14)',note:'Above 95, literally off the charts, unprecedented for a stock this size'},macd:{label:'MACD (12,26,9)',note:'So extreme it has lost any analytical meaning'},sma:{label:'50 & 200 SMA',note:'Price is 2,000%+ above the 200-day SMA, indicators are useless'}},
    explanation:{verdict:'Expert Sell: Distinguish Short Squeezes from Manias',summary:'Unlike TSLA (scenario 47), GME was a pure speculative mania, not a fundamental paradigm shift. Once the buying stops, the fall is immediate and devastating.',details:"This is the expert counterpart to scenario 47. Tesla had a real business transformation backing its squeeze. GME was a retail-driven speculative mania with no fundamental justification. The expert skill is distinguishing between squeezes backed by fundamentals (hold) and pure speculative manias (sell). When the ONLY reason to hold is that others are also buying, you are in a mania.",outcome:'GME crashed from ~$347 to under $50 within days, a ~85% decline. Many retail traders lost their life savings.',lesson:'The expert skill is distinguishing paradigm shifts (buy), fundamental short squeezes (hold), and speculative manias (sell). If the only thesis is "others are buying," sell.',indicatorBreakdown:[{name:'RSI: 95+',signal:'neutral',reading:'So extreme that traditional analysis is meaningless.'},{name:'MACD: Meaningless',signal:'neutral',reading:'Indicators lose analytical value in pure speculative events.'},{name:'Fundamental Analysis',signal:'bearish',reading:'No business transformation. Pure speculation = inevitable collapse.'}]},
    decisionFeedback:{buy:{quality:'weak',feedback:'Buying into a speculative mania with no fundamental backing. The expert skill is knowing the difference between a squeeze and a mania.'},sell:{quality:'strong',feedback:'Elite-level thinking. Distinguishing speculative manias from fundamental squeezes is the most advanced skill in technical analysis.'}}},

  {id:49,stock:'Amazon.com Inc.',ticker:'AMZN',date:'April 2020',timeframe:'Daily',difficulty:'Expert',
    question:'Amazon has recovered from the COVID crash while most stocks are still down. It is approaching pre-crash highs while the economy is in a recession. Buy the leader or sell the divergence?',
    correctAnswer:'buy',signalQuality:'moderate',
    indicators:{rsi:{label:'RSI (14)',note:'Around 65, bullish momentum building'},macd:{label:'MACD (12,26,9)',note:'Just crossed above zero line, shifting from bearish to bullish regime'},sma:{label:'50 & 200 SMA',note:'Price reclaimed the 200-day SMA, 50-day curling up'}},
    explanation:{verdict:'Expert Buy: Relative Strength Leadership',summary:'Stocks that recover fastest from crashes and show relative strength during recessions are the market leaders. Amazon benefiting from the shift to e-commerce made it a recession winner.',details:"The expert concept: in a recovery, buy the leaders, not the laggards. Amazon was a direct beneficiary of COVID (e-commerce boom, AWS demand). Its rapid recovery while most stocks were still down signaled institutional recognition of this. MACD crossing zero confirmed the regime change. Relative strength during adversity is the strongest signal of future outperformance.",outcome:'AMZN surged to new all-time highs, rallying from ~$2,400 to over $3,500 in the following months (+46%).',lesson:'Stocks showing relative strength during market weakness are institutional favorites. Buy the strongest, not the cheapest.',indicatorBreakdown:[{name:'RSI: ~65',signal:'bullish',reading:'Building momentum while most stocks are still recovering.'},{name:'MACD: Zero Line Cross',signal:'bullish',reading:'Regime change from bearish to bullish, a major signal.'},{name:'Relative Strength',signal:'bullish',reading:'Recovering faster than the market = institutional accumulation.'}]},
    decisionFeedback:{buy:{quality:'strong',feedback:'Expert-level thinking. Buying relative strength leaders during economic weakness is how institutions build positions.'},sell:{quality:'weak',feedback:'Selling a relative strength leader during a recession because "the economy is bad" misses the point. Markets are forward-looking.'}}},

  {id:50,stock:'Dow Jones ETF',ticker:'DIA',date:'March 2020 (COVID Crash)',timeframe:'Daily',difficulty:'Expert',
    question:'The Dow Jones has crashed 37%. The economy is shutting down. Unemployment will hit 15%. The Fed is printing trillions. Every fundamental says sell. What do you do?',
    correctAnswer:'buy',signalQuality:'false_signal',
    indicators:{rsi:{label:'RSI (14)',note:'Below 15, historic extreme, once-in-a-decade panic level'},macd:{label:'MACD (12,26,9)',note:'Most negative reading since 2008, deeply bearish'},sma:{label:'50 & 200 SMA',note:'Death Cross, price below all support, technically destroyed'}},
    explanation:{verdict:'The Ultimate Expert Lesson: Fed Policy Overrides Everything',summary:'When the Federal Reserve commits unlimited resources to preventing economic collapse, all bearish indicators become irrelevant. The Fed is the ultimate technical indicator.',details:"March 23, 2020 was when the Fed announced unlimited QE (money printing). This single policy decision invalidated every bearish signal. The expert insight: central bank policy is the most powerful force in markets. When the Fed says 'we will do whatever it takes,' they mean it. RSI at 15 + unlimited Fed support = the buy signal of the decade.",outcome:'DIA rallied from ~$185 to over $340 within 18 months (+84%).',lesson:'The most important lesson in expert-level analysis: central bank policy overrides all technical signals. When the Fed commits unlimited resources, buy.',indicatorBreakdown:[{name:'RSI: Below 15',signal:'bullish',reading:'Historic panic + Fed unlimited support = generational buying opportunity.'},{name:'All Indicators Bearish',signal:'neutral',reading:'Every indicator was lagging, reflecting the crash that already happened.'},{name:'Fed Policy',signal:'bullish',reading:'Unlimited QE = the most powerful bullish signal in existence.'}]},
    decisionFeedback:{buy:{quality:'strong',feedback:'Elite thinking. Understanding that Fed policy overrides all technical indicators at market extremes is the final lesson.'},sell:{quality:'weak',feedback:'Following bearish indicators when the Fed has committed unlimited resources to preventing collapse ignores the most powerful force in markets.'}}},
];

/* ======== CHART COMPONENT (REAL DATA) ======== */
function Chart({scenarioId}) {
  const {displayCandles,sma50,sma200,rsi,macd} = useMemo(()=>{
    const raw = REAL_DATA.find(d=>d.id===scenarioId);
    if(!raw||!raw.candles.length) return {displayCandles:[],sma50:[],sma200:[],rsi:[],macd:{macdLine:[],signalLine:[],histogram:[]}};
    const allCloses = raw.candles.map(c=>c.c);
    const fullSMA50 = computeSMA(allCloses,50);
    const fullSMA200 = computeSMA(allCloses,200);
    const fullRSI = computeRSI(allCloses,14);
    const fullMACD = computeMACD(allCloses,12,26,9);
    const n = Math.min(DISPLAY_CANDLES, raw.candles.length);
    const start = raw.candles.length - n;
    return {
      displayCandles: raw.candles.slice(start),
      sma50: fullSMA50.slice(start),
      sma200: fullSMA200.slice(start),
      rsi: fullRSI.slice(start),
      macd: {
        macdLine: fullMACD.macdLine.slice(start),
        signalLine: fullMACD.signalLine.slice(start),
        histogram: fullMACD.histogram.slice(start),
      },
    };
  },[scenarioId]);

  const candles = displayCandles;
  if(!candles.length) return <div style={{background:'#131722',borderRadius:10,padding:40,textAlign:'center',color:'#6b7280'}}>Chart data unavailable</div>;

  const W=820,mainH=280,rsiH=88,macdH=88,gap=14;
  const padL=58,padR=12,padT=18,padB=6;
  const innerW=W-padL-padR;
  const totalH=mainH+gap+rsiH+gap+macdH;

  const prices=candles.flatMap(c=>[c.h,c.l]);
  const minP=Math.min(...prices)*0.997,maxP=Math.max(...prices)*1.003,pRange=maxP-minP;
  const pToY=p=>padT+((maxP-p)/pRange)*(mainH-padT-padB);
  const iToX=i=>padL+(i+0.5)*(innerW/candles.length);
  const cw=Math.max(1.5,(innerW/candles.length)*0.6);

  const rsiTop=mainH+gap;
  const rToY=v=>rsiTop+((100-v)/100)*rsiH;

  const macdTop=mainH+gap+rsiH+gap;
  const hv=macd.histogram.filter(v=>v!==null&&!isNaN(v));
  const mm=hv.length?Math.max(Math.abs(Math.min(...hv)),Math.abs(Math.max(...hv)),0.001):1;
  const mToY=v=>macdTop+macdH/2-(v/mm)*(macdH/2-4);

  const buildPath=(vals,toY)=>{let d='';vals.forEach((v,i)=>{if(v===null||isNaN(v))return;d+=d===''?`M${iToX(i)},${toY(v)}`:`L${iToX(i)},${toY(v)}`;});return d;};

  const gridPrices=Array.from({length:5},(_,i)=>minP+(i/4)*pRange);
  const curRSI=lastVal(rsi);
  const curClose=candles[candles.length-1]?.c;

  return (
    <svg viewBox={`0 0 ${W} ${totalH}`} style={{width:'100%',height:'auto',display:'block',background:'#131722',borderRadius:'10px'}}>
      <rect width={W} height={totalH} fill="#131722" rx="10"/>
      <rect x={padL} y={padT} width={innerW} height={mainH-padT-padB} fill="#161b27" rx="4"/>
      <rect x={padL} y={rsiTop} width={innerW} height={rsiH} fill="#0f1219" rx="4"/>
      <rect x={padL} y={macdTop} width={innerW} height={macdH} fill="#0f1219" rx="4"/>
      <text x={padL+6} y={padT+14} fill="#6b7280" fontSize="10" fontFamily="Inter,sans-serif" fontWeight="600">PRICE</text>
      <text x={padL+6} y={rsiTop+14} fill="#9b59b6" fontSize="10" fontFamily="Inter,sans-serif" fontWeight="600">RSI (14)</text>
      <text x={padL+6} y={macdTop+14} fill="#26c6da" fontSize="10" fontFamily="Inter,sans-serif" fontWeight="600">MACD (12,26,9)</text>
      {gridPrices.map((p,i)=>{const y=pToY(p);return <g key={i}><line x1={padL} y1={y} x2={W-padR} y2={y} stroke="#1e2535" strokeWidth="0.5" strokeDasharray="3,4"/><text x={padL-4} y={y+3.5} textAnchor="end" fill="#4b5563" fontSize="9.5" fontFamily="JetBrains Mono,monospace">{p.toFixed(p>999?0:2)}</text></g>})}
      {candles.map((c,i)=>{const x=iToX(i),isG=c.c>=c.o,col=isG?'#26a69a':'#ef5350',bTop=pToY(Math.max(c.o,c.c)),bBot=pToY(Math.min(c.o,c.c)),bH=Math.max(1,bBot-bTop);return <g key={i}><line x1={x} y1={pToY(c.h)} x2={x} y2={pToY(c.l)} stroke={col} strokeWidth={Math.max(0.5,cw*0.15)}/><rect x={x-cw/2} y={bTop} width={cw} height={bH} fill={col}/></g>})}
      <path d={buildPath(sma50,pToY)} fill="none" stroke="#2962ff" strokeWidth="1.3"/>
      <path d={buildPath(sma200,pToY)} fill="none" stroke="#ff9800" strokeWidth="1.3"/>
      <g><rect x={W-padR-140} y={padT+4} width={10} height={3} fill="#2962ff" rx="1"/><text x={W-padR-127} y={padT+10} fill="#2962ff" fontSize="9" fontFamily="Inter,sans-serif">50-Day SMA</text><rect x={W-padR-140} y={padT+18} width={10} height={3} fill="#ff9800" rx="1"/><text x={W-padR-127} y={padT+24} fill="#ff9800" fontSize="9" fontFamily="Inter,sans-serif">200-Day SMA</text></g>
      <text x={padL+6} y={padT+30} fill="#e5e7eb" fontSize="11" fontFamily="JetBrains Mono,monospace" fontWeight="600">${curClose?.toFixed(2)}</text>
      <rect x={padL} y={rToY(70)} width={innerW} height={rToY(30)-rToY(70)} fill="rgba(100,80,160,0.06)"/>
      <line x1={padL} y1={rToY(70)} x2={W-padR} y2={rToY(70)} stroke="#ef5350" strokeWidth="0.6" strokeDasharray="3,3" opacity="0.7"/>
      <line x1={padL} y1={rToY(50)} x2={W-padR} y2={rToY(50)} stroke="#374151" strokeWidth="0.4" strokeDasharray="1,4"/>
      <line x1={padL} y1={rToY(30)} x2={W-padR} y2={rToY(30)} stroke="#26a69a" strokeWidth="0.6" strokeDasharray="3,3" opacity="0.7"/>
      <text x={padL-4} y={rToY(70)+3} textAnchor="end" fill="#ef5350" fontSize="8.5" fontFamily="JetBrains Mono,monospace">70</text>
      <text x={padL-4} y={rToY(50)+3} textAnchor="end" fill="#4b5563" fontSize="8.5" fontFamily="JetBrains Mono,monospace">50</text>
      <text x={padL-4} y={rToY(30)+3} textAnchor="end" fill="#26a69a" fontSize="8.5" fontFamily="JetBrains Mono,monospace">30</text>
      <path d={buildPath(rsi,rToY)} fill="none" stroke="#9b59b6" strokeWidth="1.5"/>
      {curRSI!==null&&<text x={W-padR-4} y={rToY(curRSI)-4} textAnchor="end" fill="#9b59b6" fontSize="10" fontFamily="JetBrains Mono,monospace" fontWeight="600">{curRSI.toFixed(1)}</text>}
      <line x1={padL} y1={macdTop+macdH/2} x2={W-padR} y2={macdTop+macdH/2} stroke="#374151" strokeWidth="0.6"/>
      {macd.histogram.map((v,i)=>{if(v===null||isNaN(v))return null;const x=iToX(i),zY=macdTop+macdH/2,bY=mToY(v),bH=Math.abs(bY-zY),top=Math.min(bY,zY),bw=Math.max(1,cw*0.5);return <rect key={i} x={x-bw/2} y={top} width={bw} height={Math.max(0.5,bH)} fill={v>=0?'#26a69a':'#ef5350'} opacity="0.75"/>})}
      <path d={buildPath(macd.macdLine,mToY)} fill="none" stroke="#26c6da" strokeWidth="1.1"/>
      <path d={buildPath(macd.signalLine,mToY)} fill="none" stroke="#ff8a65" strokeWidth="1.1"/>
      <g><line x1={W-padR-110} y1={macdTop+10} x2={W-padR-100} y2={macdTop+10} stroke="#26c6da" strokeWidth="1.5"/><text x={W-padR-97} y={macdTop+13} fill="#26c6da" fontSize="9" fontFamily="Inter,sans-serif">MACD</text><line x1={W-padR-65} y1={macdTop+10} x2={W-padR-55} y2={macdTop+10} stroke="#ff8a65" strokeWidth="1.5"/><text x={W-padR-52} y={macdTop+13} fill="#ff8a65" fontSize="9" fontFamily="Inter,sans-serif">Signal</text></g>
    </svg>
  );
}

/* ======== SPARKLES CANVAS ======== */
function SparklesCanvas({color='#ffffff', density=120, speed=0.6, starRatio=0.35}) {
  const canvasRef = useRef(null);
  useEffect(()=>{
    const canvas = canvasRef.current;
    if(!canvas) return;
    const ctx = canvas.getContext('2d');
    let animId;
    let W = 0, H = 0, particles = [];

    // Parse hex color to rgb
    const hex = color.replace('#','');
    const r = parseInt(hex.slice(0,2),16);
    const g = parseInt(hex.slice(2,4),16);
    const b = parseInt(hex.slice(4,6),16);

    const makePart = ()=>({
      x: Math.random()*W, y: Math.random()*H,
      size: Math.random()*1.6+0.4,
      opacity: Math.random(),
      opacityDir: Math.random()>0.5?1:-1,
      opacitySpeed: 0.004+Math.random()*0.012,
      vx: (Math.random()-0.5)*speed*0.4,
      vy: (Math.random()-0.5)*speed*0.4,
      isStar: Math.random()<starRatio,
    });

    const resize = ()=>{
      W = canvas.offsetWidth; H = canvas.offsetHeight;
      canvas.width = W; canvas.height = H;
      particles = Array.from({length:Math.round(density*(W*H)/(1440*900))},makePart);
    };

    const drawStar = (x,y,size,op)=>{
      ctx.save(); ctx.globalAlpha=op; ctx.fillStyle=`rgb(${r},${g},${b})`;
      ctx.translate(x,y);
      const s=size*2.2;
      ctx.beginPath();
      ctx.moveTo(0,-s); ctx.lineTo(s*0.22,-s*0.22); ctx.lineTo(s,0);
      ctx.lineTo(s*0.22,s*0.22); ctx.lineTo(0,s); ctx.lineTo(-s*0.22,s*0.22);
      ctx.lineTo(-s,0); ctx.lineTo(-s*0.22,-s*0.22);
      ctx.closePath(); ctx.fill(); ctx.restore();
    };

    const draw = ()=>{
      ctx.clearRect(0,0,W,H);
      for(const p of particles){
        p.opacity += p.opacityDir * p.opacitySpeed;
        if(p.opacity>=1){p.opacity=1;p.opacityDir=-1;}
        else if(p.opacity<=0){p.opacity=0;p.opacityDir=1;}
        p.x+=p.vx; p.y+=p.vy;
        if(p.x<-10)p.x=W+10; else if(p.x>W+10)p.x=-10;
        if(p.y<-10)p.y=H+10; else if(p.y>H+10)p.y=-10;
        if(p.isStar){
          drawStar(p.x,p.y,p.size,p.opacity);
        } else {
          ctx.beginPath(); ctx.arc(p.x,p.y,p.size,0,Math.PI*2);
          ctx.fillStyle=`rgba(${r},${g},${b},${p.opacity})`; ctx.fill();
        }
      }
      animId=requestAnimationFrame(draw);
    };

    const ro = new ResizeObserver(resize);
    ro.observe(canvas.parentElement||canvas);
    resize();
    draw();
    return ()=>{ cancelAnimationFrame(animId); ro.disconnect(); };
  },[color,density,speed,starRatio]);

  return React.createElement('canvas',{ref:canvasRef,style:{position:'absolute',inset:0,width:'100%',height:'100%',pointerEvents:'none',zIndex:1}});
}

/* ======== INTRO ANIMATION ======== */
function IntroOverlay({onDismiss}) {
  const [phase,setPhase] = useState('active');
  const candleData = useMemo(()=>{
    const bars = [];
    for(let i=0;i<60;i++){
      const h = 20 + Math.random()*60;
      const isGreen = Math.random()>0.45;
      bars.push({h, isGreen, delay: 0.5 + i*0.03});
    }
    return bars;
  },[]);

  const particles = useMemo(()=>Array.from({length:25},(_,i)=>({
    left:Math.random()*100,size:1.5+Math.random()*2.5,delay:Math.random()*8,dur:5+Math.random()*8,
  })),[]);

  const tickerItems = ['AAPL +2.4%','TSLA -1.8%','NVDA +5.2%','SPY +0.7%','AMD +3.1%','META -0.9%','QQQ +1.5%','AMZN +2.8%','MSFT -0.4%','GOOG +1.2%'];

  const handleStart = () => {
    setPhase('exit');
    setTimeout(onDismiss, 800);
  };

  return (
    <div className={`intro-overlay${phase==='exit'?' phase-exit':''}`} style={{position:'fixed',inset:0}}>
      {/* Sparkles everywhere */}
      <SparklesCanvas color="#26a69a" density={180} speed={0.5} starRatio={0.4}/>
      <SparklesCanvas color="#ffffff" density={80} speed={0.3} starRatio={0.2}/>
      <div className="intro-bg">
        <div className="fluid-shape fluid-1"/>
        <div className="fluid-shape fluid-2"/>
        <div className="fluid-shape fluid-3"/>
        <div className="intro-grid"/>

        {/* Animated candlestick bars */}
        <div className="intro-candles">
          {candleData.map((c,i)=>(
            <div key={i} className={`intro-candle${c.isGreen?'':' red'}`}
              style={{height:c.h+'%',animationDelay:c.delay+'s',opacity:0,animationFillMode:'forwards'}}/>
          ))}
        </div>
      </div>

      <div className="intro-particles">
        {particles.map((p,i)=><div key={i} className="intro-particle" style={{left:p.left+'%',bottom:'-5%',width:p.size,height:p.size,background:'rgba(38,166,154,0.3)',animationDelay:p.delay+'s',animationDuration:p.dur+'s'}}/>)}
      </div>

      <div className="intro-center">
        <div className="intro-logo-wrap">
          <div className="intro-logo">
            <svg viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>
            </svg>
          </div>
        </div>
        <h1 className="intro-title">Market<span className="accent"> Mastery</span></h1>
        <p className="intro-tagline">Learn to read the market like a professional trader</p>
        <div className="intro-glass-card">
          <button className="intro-start-btn" onClick={handleStart}>Begin Trading Challenge</button>
          <div className="intro-features">
            <span className="intro-feat"><span className="intro-feat-dot"/>50 Real Scenarios</span>
            <span className="intro-feat"><span className="intro-feat-dot"/>Yahoo Finance Data</span>
            <span className="intro-feat"><span className="intro-feat-dot"/>AI-Powered Grading</span>
          </div>
        </div>
      </div>

      {/* Scrolling ticker tape */}
      <div className="intro-ticker">
        <div className="ticker-track">
          {[...tickerItems,...tickerItems].map((t,i)=>{
            const up = t.includes('+');
            return <span key={i} className="ticker-item">{t.split(/[+-]/)[0]}<span className={up?'up':'down'}>{up?'+':'-'}{t.split(/[+-]/)[1]}</span></span>;
          })}
        </div>
      </div>
    </div>
  );
}

/* ======== PROFILE MODAL (no backend, just a display name) ======== */
function AuthModal({onClose}) {
  const {setProfile} = useAuth();
  const [name,setName] = useState('');
  const [error,setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = name.trim();
    if(!trimmed) { setError('Enter a display name to continue.'); return; }
    setProfile(trimmed);
    onClose();
  };

  return (
    <div className="modal-overlay" onClick={(e)=>e.target===e.currentTarget&&onClose()}>
      <div className="modal-card" style={{position:'relative'}}>
        <button className="modal-close" onClick={onClose}>&times;</button>
        <h2 className="modal-title">Create Profile</h2>
        <p className="modal-sub">Choose a display name to save your scores and stats locally on this device. No account or password needed.</p>
        {error && <div className="modal-error">{error}</div>}
        <form onSubmit={handleSubmit}>
          <input className="modal-input" placeholder="Your name or nickname" value={name} onChange={e=>setName(e.target.value)} autoFocus maxLength={30}/>
          <button className="modal-submit" type="submit">Save Profile</button>
        </form>
        <p style={{fontSize:12,color:'var(--text3)',marginTop:14,textAlign:'center'}}>Your profile and stats are stored only in this browser. Free, no signup required.</p>
      </div>
    </div>
  );
}

/* ======== NAVIGATION ======== */
function NavBar({activeTab,setActiveTab,score,showScore,soundOn,onSoundToggle}) {
  const {user,logout} = useAuth();
  // eslint-disable-next-line no-unused-vars
  const [showAuth,setShowAuth] = useState(false);
  const [showDropdown,setShowDropdown] = useState(false);

  return (
    <>
      <nav className="nav-bar">
        <div className="nav-left">
          <div className="nav-logo" onClick={()=>setActiveTab('home')}>
            <div className="nav-logo-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/>
              </svg>
            </div>
            <span className="nav-logo-text">Market<span className="accent"> Mastery</span></span>
          </div>
          <div className="nav-tabs">
            {[['home','Home'],['play','Play'],['live','Live'],['leaderboard','Leaderboard'],['stats','Stats']].map(([id,label])=>(
              <button key={id} className={`nav-tab${activeTab===id?' active':''}`} onClick={()=>setActiveTab(id)}>{label}</button>
            ))}
          </div>
        </div>
        <div className="nav-right">
          {onSoundToggle && (
            <button className={`sound-toggle${soundOn?' on':''}`} onClick={onSoundToggle} title={soundOn?'Mute sounds':'Enable sounds'}>
              {soundOn ? '\uD83D\uDD0A' : '\uD83D\uDD07'}{soundOn ? ' On' : ' Off'}
            </button>
          )}
          {showScore && <div className="score-display"><span className="score-label">Score</span><span className="score-value">{score}</span></div>}
          {user ? (
            <div style={{position:'relative'}}>
              <button className="nav-user" onClick={()=>setShowDropdown(!showDropdown)}>
                <div className="nav-user-avatar">{(user.name||'T')[0].toUpperCase()}</div>
                <span>{user.name||'Trader'}</span>
              </button>
              {showDropdown && (
                <div style={{position:'absolute',top:'100%',right:0,marginTop:4,background:'var(--bg3)',border:'1px solid var(--border)',borderRadius:8,padding:'4px 0',minWidth:160,zIndex:50,animation:'fadeIn 0.15s ease'}}>
                  <div style={{padding:'8px 14px',fontSize:12,color:'var(--text3)',borderBottom:'1px solid var(--border)'}}>{user.email}</div>
                  <button onClick={()=>{setActiveTab('stats');setShowDropdown(false)}} style={{width:'100%',textAlign:'left',padding:'10px 14px',background:'transparent',border:'none',color:'var(--text)',fontSize:13,cursor:'pointer',fontFamily:'Inter,sans-serif'}} onMouseOver={e=>e.target.style.background='var(--bg4)'} onMouseOut={e=>e.target.style.background='transparent'}>Statistics</button>
                  <button onClick={()=>{logout();setShowDropdown(false)}} style={{width:'100%',textAlign:'left',padding:'10px 14px',background:'transparent',border:'none',color:'var(--red)',fontSize:13,cursor:'pointer',fontFamily:'Inter,sans-serif'}} onMouseOver={e=>e.target.style.background='var(--bg4)'} onMouseOut={e=>e.target.style.background='transparent'}>Sign Out</button>
                </div>
              )}
            </div>
          ) : (
            <button className="nav-login-btn" onClick={()=>setShowAuth(true)}>Set Profile</button>
          )}
        </div>
      </nav>
      {showAuth && <AuthModal onClose={()=>setShowAuth(false)}/>}
    </>
  );
}

/* ======== HOME SCREEN (Landing) ======== */
function HomeScreen({onPlay}) {
  const bars = useMemo(()=>Array.from({length:30},(_,i)=>({h:20+Math.random()*60, green:Math.random()>0.4, delay:i*0.04})),[]);
  return (
    <div className="landing" style={{position:'relative'}}>
      {/* Sparkles background layer */}
      <SparklesCanvas color="#26a69a" density={100} speed={0.4} starRatio={0.35}/>
      <SparklesCanvas color="#ffffff" density={50} speed={0.25} starRatio={0.15}/>
      {/* Hero */}
      <div className="land-hero" style={{position:'relative',zIndex:2}}>
        <div className="land-hero-left">
          <div className="land-tag"><span className="dot"/> Live Market Education</div>
          <h1 className="land-title">Master<br/>Technical<br/><span className="accent">Analysis</span></h1>
          <p className="land-desc">Learn to read real stock charts, interpret RSI, MACD, and Moving Averages, and predict major market moves using real Yahoo Finance data.</p>
          <button className="gs-btn" onClick={onPlay}>
            <span className="gs-btn-label">Start Playing</span>
            <span className="gs-btn-arrow">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
            </span>
          </button>
          <div className="land-stats">
            <div className="land-stat"><span className="land-stat-num">50</span><span className="land-stat-label">Scenarios</span></div>
            <div className="land-stat"><span className="land-stat-num">30+</span><span className="land-stat-label">Tickers</span></div>
            <div className="land-stat"><span className="land-stat-num">4</span><span className="land-stat-label">Difficulty Levels</span></div>
          </div>
        </div>
        <div className="land-hero-right">
          <div className="land-card">
            <div className="land-card-header">
              <span className="land-card-ticker">NVDA</span>
              <span className="land-card-badge" style={{borderColor:'#ef5350',color:'#ef5350',background:'rgba(239,83,80,0.1)'}}>Advanced</span>
            </div>
            <div className="land-card-chart">
              {bars.map((b,i)=><div key={i} className="land-bar" style={{height:b.h+'%',background:b.green?'var(--green)':'var(--red)',animationDelay:b.delay+'s'}}/>)}
            </div>
            <div className="land-card-footer">
              <span className="land-card-q">RSI overbought. Sell?</span>
              <div className="land-card-btns">
                <span className="land-card-btn" style={{borderColor:'var(--green)',color:'var(--green)',background:'rgba(38,166,154,0.1)'}}>Buy</span>
                <span className="land-card-btn" style={{borderColor:'var(--red)',color:'var(--red)',background:'rgba(239,83,80,0.1)'}}>Sell</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features */}
      <div className="land-features">
        <div className="land-features-title">Why Market Mastery</div>
        <div className="land-features-grid">
          <div className="land-feat">
            <div className="land-feat-icon" style={{background:'rgba(38,166,154,0.12)',color:'var(--green)'}}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
            </div>
            <div className="land-feat-name">Real Market Data</div>
            <div className="land-feat-desc">Every chart uses real historical OHLC data from Yahoo Finance. No simulations, no fake data.</div>
          </div>
          <div className="land-feat">
            <div className="land-feat-icon" style={{background:'rgba(155,89,182,0.12)',color:'var(--purple)'}}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
            </div>
            <div className="land-feat-name">Industry Indicators</div>
            <div className="land-feat-desc">RSI (14), MACD (12,26,9), and 50/200-day SMAs. The exact same tools professionals use.</div>
          </div>
          <div className="land-feat">
            <div className="land-feat-icon" style={{background:'rgba(255,152,0,0.12)',color:'var(--orange)'}}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
            </div>
            <div className="land-feat-name">Learn From Outcomes</div>
            <div className="land-feat-desc">See what actually happened after each scenario. Detailed explanations of why indicators worked or failed.</div>
          </div>
          <div className="land-feat">
            <div className="land-feat-icon" style={{background:'rgba(41,98,255,0.12)',color:'var(--accent)'}}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 20V10"/><path d="M18 20V4"/><path d="M6 20v-4"/></svg>
            </div>
            <div className="land-feat-name">4 Difficulty Levels</div>
            <div className="land-feat-desc">From Beginner (clear signals) to Expert (paradigm shifts, short squeezes, Fed policy). Progress at your pace.</div>
          </div>
          <div className="land-feat">
            <div className="land-feat-icon" style={{background:'rgba(38,198,218,0.12)',color:'#26c6da'}}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            </div>
            <div className="land-feat-name">AI Reasoning Mode</div>
            <div className="land-feat-desc">Optional Claude AI grading. Explain your reasoning and get personalized feedback on your analysis quality.</div>
          </div>
          <div className="land-feat">
            <div className="land-feat-icon" style={{background:'rgba(239,83,80,0.12)',color:'var(--red)'}}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            </div>
            <div className="land-feat-name">False Signal Training</div>
            <div className="land-feat-desc">Learn when indicators lie. Some scenarios are designed to trick you. Because real markets do the same.</div>
          </div>
        </div>
      </div>

      {/* Indicators strip */}
      <div className="land-indicators">
        <div className="land-features-title">Indicators You Will Master</div>
        <div className="land-ind-grid">
          <div className="land-ind"><strong style={{color:'var(--purple)'}}>RSI (14)</strong><span>Relative Strength Index measures overbought/oversold conditions over 14 periods</span></div>
          <div className="land-ind"><strong style={{color:'#26c6da'}}>MACD (12,26,9)</strong><span>Moving Average Convergence Divergence reveals momentum shifts and trend changes</span></div>
          <div className="land-ind"><strong style={{color:'var(--orange)'}}>50 & 200 SMA</strong><span>The two most watched moving averages: Golden Cross and Death Cross signals</span></div>
        </div>
      </div>

      {/* Bottom CTA */}
      <div className="land-bottom">
        <div className="land-bottom-box">
          <h2>Ready to Test Your Skills?</h2>
          <p>50 real scenarios. 30+ tickers. From beginner to expert. No sign-up required.</p>
          <button className="gs-btn" onClick={onPlay}>
            <span className="gs-btn-label">Start Playing</span>
            <span className="gs-btn-arrow">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
            </span>
          </button>
        </div>
      </div>
    </div>
  );
}

/* ======== PLAY SCREEN (difficulty + start) ======== */
function PlayScreen({onStart, difficulty, onDifficultyChange, scenarioCount, gameMode, onModeChange}) {
  const diffs = ['All','Beginner','Intermediate','Advanced','Expert'];
  const dc = {All:'var(--accent)',Beginner:'#26a69a',Intermediate:'#ff9800',Advanced:'#ef5350',Expert:'#9b59b6'};
  return (
    <div className="play-screen">
      <div className="play-content">
        <h1 className="play-title">Choose Your<span className="accent"> Challenge</span></h1>
        <p className="play-sub">Select a difficulty level and game mode, then start analyzing real market scenarios.</p>
        <div className="difficulty-picker">
          <h2 style={{fontSize:13,fontWeight:600,textTransform:'uppercase',letterSpacing:'0.1em',color:'var(--text3)',marginBottom:16}}>Difficulty</h2>
          <div className="diff-options">
            {diffs.map(d=><button key={d} className={`diff-btn${difficulty===d?' active':''}`} style={difficulty===d?{borderColor:dc[d],color:dc[d],background:dc[d]+'15'}:{}} onClick={()=>onDifficultyChange(d)}>{d}<span className="diff-count">{d==='All'?scenarios.length:scenarios.filter(s=>s.difficulty===d).length}</span></button>)}
          </div>
        </div>
        <div style={{marginBottom:24,animation:'fadeInUp 0.5s ease 0.25s both'}}>
          <h2 style={{fontSize:13,fontWeight:600,textTransform:'uppercase',letterSpacing:'0.1em',color:'var(--text3)',marginBottom:12}}>Game Mode</h2>
          <div className="mode-toggle" style={{display:'inline-flex'}}>
            <button className={`mode-opt${gameMode==='prediction'?' active':''}`} onClick={()=>onModeChange('prediction')}>Prediction Mode</button>
            <button className={`mode-opt${gameMode==='reasoning'?' active':''}`} onClick={()=>onModeChange('reasoning')}>Reasoning Mode</button>
          </div>
          <p style={{fontSize:12,color:'var(--text3)',marginTop:8}}>{gameMode==='prediction'?'Make buy/sell calls based on chart analysis.':'Explain your reasoning and get AI-powered feedback on your analysis.'}</p>
        </div>
        <div className="how-it-works"><h2>How It Works</h2>
          <div className="steps">
            {[['01','Analyze the Chart','Real daily charts from US market history with 50 & 200-day SMAs, right before a big move'],['02','Read the Indicators','RSI (14), MACD (12,26,9), and 50/200-day Moving Averages on the chart'],['03','Make Your Call','Buy or Sell? Your score reflects both your answer AND your reasoning quality'],['04','Learn From Reality','See what actually happened and why, in plain language']].map(([n,t,d])=><div key={n} className="step"><div className="step-num">{n}</div><div className="step-text"><strong>{t}</strong><span>{d}</span></div></div>)}
          </div>
        </div>
        <div className="scoring-note"><span className="note-icon">*</span><span><strong>Scoring:</strong> Base points &times; difficulty multiplier. <strong>Beginner 1x &bull; Intermediate 1.25x &bull; Advanced 1.5x &bull; Expert 2x</strong>. Perfect Call on Expert = 200 pts! Charts use real Yahoo Finance data, industry-standard indicators (RSI 14, MACD 12/26/9, SMA 50/200).</span></div>
        <button className="start-btn" onClick={onStart}>Start Game: {scenarioCount} Scenarios <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg></button>
        <p className="play-footer">Real Yahoo Finance data | Industry-standard indicators | 50 scenarios from Beginner to Expert</p>
      </div>
    </div>
  );
}

/* ======== LIVE CHALLENGE SCREEN ======== */
function LiveChart({candles, sma20, sma50}) {
  if(!candles||!candles.length) return null;
  const W=800, H=220, pad={t:10,r:10,b:20,l:50};
  const cw=Math.max(2, (W-pad.l-pad.r)/candles.length - 1);

  const allPrices = candles.flatMap(c=>[c.h,c.l]);
  const smaVals = [...(sma20||[]),...(sma50||[])].filter(v=>v!=null);
  allPrices.push(...smaVals);
  const minP=Math.min(...allPrices), maxP=Math.max(...allPrices);
  const range=maxP-minP||1;
  const y=v=>pad.t+(1-(v-minP)/range)*(H-pad.t-pad.b);

  return (
    <svg viewBox={`0 0 ${W} ${H}`} style={{width:'100%',height:'auto'}}>
      {candles.map((c,i)=>{
        const x=pad.l+i*(cw+1);
        const green=c.c>=c.o;
        const color=green?'var(--green)':'var(--red)';
        const bodyTop=y(Math.max(c.o,c.c));
        const bodyBot=y(Math.min(c.o,c.c));
        const bodyH=Math.max(1,bodyBot-bodyTop);
        return <g key={i}>
          <line x1={x+cw/2} y1={y(c.h)} x2={x+cw/2} y2={y(c.l)} stroke={color} strokeWidth={1} opacity={0.6}/>
          <rect x={x} y={bodyTop} width={cw} height={bodyH} fill={color} rx={1}/>
        </g>;
      })}
      {sma20 && <polyline fill="none" stroke="#ff9800" strokeWidth={1.5} opacity={0.7} points={sma20.map((v,i)=>v!=null?`${pad.l+i*(cw+1)+cw/2},${y(v)}`:null).filter(Boolean).join(' ')}/>}
      {sma50 && <polyline fill="none" stroke="#9b59b6" strokeWidth={1.5} opacity={0.7} points={sma50.map((v,i)=>v!=null?`${pad.l+i*(cw+1)+cw/2},${y(v)}`:null).filter(Boolean).join(' ')}/>}
    </svg>
  );
}

function LiveChallengeScreen() {
  const {user} = useAuth();
  const [ticker,setTicker] = useState('');
  const [searchQuery,setSearchQuery] = useState('');
  const [searchResults,setSearchResults] = useState([]);
  const [showSearch,setShowSearch] = useState(false);
  const [loading,setLoading] = useState(false);
  const [scenario,setScenario] = useState(null);
  const [prediction,setPrediction] = useState(null);
  const [error,setError] = useState(null);
  const [news,setNews] = useState([]);

  // Live stats from localStorage
  const statsKey = user ? `mm_live_stats_${user.uid}` : null;
  const [stats,setStats] = useState(()=>{
    if(!statsKey) return {played:0,correct:0,streak:0,bestStreak:0};
    try { return JSON.parse(localStorage.getItem(statsKey)) || {played:0,correct:0,streak:0,bestStreak:0}; }
    catch(e) { return {played:0,correct:0,streak:0,bestStreak:0}; }
  });

  const saveStats = (newStats) => {
    setStats(newStats);
    if(statsKey) localStorage.setItem(statsKey, JSON.stringify(newStats));
  };

  // Search debounce
  const searchTimer = useRef(null);
  const handleSearchInput = (val) => {
    setSearchQuery(val);
    setTicker(val.toUpperCase());
    if(searchTimer.current) clearTimeout(searchTimer.current);
    if(val.length >= 1) {
      searchTimer.current = setTimeout(async()=>{
        try {
          const resp = await fetch(`/api/search?q=${encodeURIComponent(val)}`);
          const data = await resp.json();
          setSearchResults(data);
          setShowSearch(true);
        } catch(e) { setSearchResults([]); }
      }, 300);
    } else {
      setSearchResults([]);
      setShowSearch(false);
    }
  };

  const selectTicker = (t) => {
    setTicker(t);
    setSearchQuery(t);
    setShowSearch(false);
    setSearchResults([]);
  };

  const loadScenario = async (t) => {
    const target = t || ticker;
    if(!target) return;
    setLoading(true);
    setScenario(null);
    setPrediction(null);
    setError(null);
    setNews([]);
    try {
      const [scenResp, newsResp] = await Promise.allSettled([
        fetch(`/api/live-scenario?ticker=${encodeURIComponent(target)}`),
        fetch(`/api/news?ticker=${encodeURIComponent(target)}`)
      ]);
      if(scenResp.status === 'fulfilled') {
        const data = await scenResp.value.json();
        if(data.error) { setError(data.error); }
        else { setScenario(data); }
      } else {
        setError('Failed to connect to server. Make sure live_server.py is running.');
      }
      if(newsResp.status === 'fulfilled') {
        try { const nd = await newsResp.value.json(); setNews(nd||[]); } catch(e){}
      }
    } catch(e) {
      setError('Failed to connect to server. Make sure live_server.py is running.');
    }
    setLoading(false);
  };

  const handlePredict = (dir) => {
    if(!scenario || prediction) return;
    const correct = dir === scenario.correctAnswer;
    setPrediction({direction: dir, correct});
    SoundSystem.play(correct ? 'correct' : 'wrong');

    // Update stats
    const newStats = {...stats, played: stats.played + 1};
    if(correct) {
      newStats.correct = stats.correct + 1;
      newStats.streak = stats.streak + 1;
      newStats.bestStreak = Math.max(newStats.streak, stats.bestStreak);
      if(newStats.streak >= 3) SoundSystem.play('streak');
    } else {
      newStats.streak = 0;
    }
    saveStats(newStats);

    // Update global leaderboard with live stats
    if(user) {
      const gameStats = getAllStats(user.uid);
      updateLeaderboard(user.uid, user.name, gameStats, newStats);
    }
  };

  const handleNewChallenge = () => {
    setScenario(null);
    setPrediction(null);
    setError(null);
    loadScenario(ticker);
  };

  const popular = ['SPY','AAPL','NVDA','TSLA','MSFT','AMZN','META','QQQ','AMD','GOOGL'];

  return (
    <div className="live-screen">
      <div className="live-content">
        {/* Header */}
        <div className="live-header">
          <h1 className="live-title">Live<span className="accent"> Challenge</span></h1>
          <div className="live-badge"><span className="live-dot"/>Live Market Data</div>
        </div>

        {/* Stats bar */}
        {stats.played > 0 && (
          <div className="live-stats-bar" style={{animation:'fadeInUp 0.4s ease both'}}>
            <div className="live-stat-item"><span className="live-stat-num" style={{color:'var(--accent)'}}>{stats.played}</span><span className="live-stat-label">Played</span></div>
            <div className="live-stat-item"><span className="live-stat-num" style={{color:'var(--green)'}}>{stats.played>0?Math.round(stats.correct/stats.played*100):0}%</span><span className="live-stat-label">Accuracy</span></div>
            <div className="live-stat-item"><span className="live-stat-num" style={{color:'var(--orange)'}}>{stats.streak}</span><span className="live-stat-label">Streak</span></div>
            <div className="live-stat-item"><span className="live-stat-num" style={{color:'var(--purple)'}}>{stats.bestStreak}</span><span className="live-stat-label">Best Streak</span></div>
          </div>
        )}

        {/* How it works */}
        <div className="live-how">
          <div className="live-how-title">How Live Challenge Works</div>
          <div className="live-how-steps">
            <div className="live-how-step"><span className="live-how-num">1</span>Pick any stock</div>
            <div className="live-how-step"><span className="live-how-num">2</span>See chart from ~1 hour ago</div>
            <div className="live-how-step"><span className="live-how-num">3</span>Predict: Up or Down?</div>
            <div className="live-how-step"><span className="live-how-num">4</span>Instantly see the most recent price</div>
          </div>
          <div style={{fontSize:11,color:'var(--text3)',marginTop:8}}>Data is 15-min delayed via Yahoo Finance. Chart shows ~1 hour back from latest data, then reveals the most recent price. All times in US Eastern.</div>
        </div>

        {/* Ticker picker */}
        <div className="live-picker">
          <div className="live-picker-label">Choose a Stock</div>
          <div className="live-picker-row">
            <div className="live-search">
              <input
                type="text"
                placeholder="Search any stock (e.g. AAPL, Tesla, SPY...)"
                value={searchQuery}
                onChange={e=>handleSearchInput(e.target.value)}
                onFocus={()=>searchResults.length>0&&setShowSearch(true)}
                onKeyDown={e=>{if(e.key==='Enter'){setShowSearch(false);loadScenario();}}}
              />
              {showSearch && searchResults.length > 0 && (
                <div className="live-search-results">
                  {searchResults.map(r=>(
                    <div key={r.ticker} className="live-search-item" onClick={()=>{selectTicker(r.ticker);loadScenario(r.ticker);}}>
                      <strong>{r.ticker}</strong>
                      <span>{r.name}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <button className="live-go-btn" onClick={()=>loadScenario()} disabled={!ticker||loading}>
              {loading ? 'Loading...' : 'Go'}
            </button>
          </div>
          <div className="live-popular">
            {popular.map(t=><button key={t} className="live-pop-btn" onClick={()=>{selectTicker(t);loadScenario(t);}}>{t}</button>)}
          </div>
        </div>

        {/* Market status banner */}
        {scenario && scenario.marketInfo && (
          <div className={`market-status ${scenario.marketInfo.isOpen ? 'open' : 'closed'}`}>
            <span className="market-status-dot"/>
            {scenario.marketInfo.isOpen
              ? `Market Open (${scenario.marketInfo.timezone}) \u2014 Live data updating`
              : scenario.marketInfo.message || `Market Closed \u2014 Using last session data`
            }
          </div>
        )}

        {/* Error */}
        {error && (
          <div style={{padding:20,background:'rgba(239,83,80,0.1)',border:'1px solid rgba(239,83,80,0.3)',borderRadius:'var(--radius)',color:'var(--red)',fontSize:14,marginBottom:20,animation:'fadeInUp 0.3s ease both'}}>
            {error}
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="live-loading">
            <div className="live-loading-spinner"/>
            <div className="live-loading-text">Fetching live data for {ticker}...</div>
          </div>
        )}

        {/* Scenario */}
        {scenario && !loading && (
          <div className="live-scenario">
            <div className="live-scenario-header">
              <div className="live-ticker-display">
                <span className="live-ticker-name">{scenario.ticker}</span>
                <span className="live-ticker-price">${scenario.scenarioPrice.toFixed(2)}</span>
              </div>
              <span className="live-ticker-time">{scenario.scenarioDate} at {scenario.scenarioTime}</span>
            </div>

            {/* Chart */}
            <div className="live-chart-wrap">
              <LiveChart candles={scenario.displayCandles} sma20={scenario.sma20} sma50={scenario.sma50}/>
              <div style={{display:'flex',gap:16,justifyContent:'center',marginTop:8}}>
                <span style={{fontSize:11,color:'#ff9800'}}>--- SMA 20</span>
                <span style={{fontSize:11,color:'#9b59b6'}}>--- SMA 50</span>
              </div>
            </div>

            {/* Indicators */}
            <div className="live-indicators">
              {scenario.indicators.rsi && (
                <div className="live-ind-card">
                  <div className="live-ind-label" style={{color:scenario.indicators.rsi.signal==='overbought'||scenario.indicators.rsi.signal==='bearish'?'var(--red)':'var(--green)'}}>{scenario.indicators.rsi.label}</div>
                  <div className="live-ind-value">{scenario.indicators.rsi.value}</div>
                  <div className="live-ind-desc">{scenario.indicators.rsi.desc}</div>
                </div>
              )}
              {scenario.indicators.macd && (
                <div className="live-ind-card">
                  <div className="live-ind-label" style={{color:scenario.indicators.macd.signal==='bullish'?'var(--green)':'var(--red)'}}>{scenario.indicators.macd.label}</div>
                  <div className="live-ind-value">{scenario.indicators.macd.value}</div>
                  <div className="live-ind-desc">{scenario.indicators.macd.desc}</div>
                </div>
              )}
              {scenario.indicators.sma && (
                <div className="live-ind-card">
                  <div className="live-ind-label" style={{color:scenario.indicators.sma.signal.includes('bullish')?'var(--green)':'var(--red)'}}>{scenario.indicators.sma.label}</div>
                  <div className="live-ind-value">50: ${scenario.indicators.sma.sma50} | 200: ${scenario.indicators.sma.sma200}</div>
                  <div className="live-ind-desc">{scenario.indicators.sma.desc}</div>
                </div>
              )}
            </div>

            {/* Prediction or Result */}
            {/* News panel - shown before prediction (not revealing) */}
            {news.length > 0 && !prediction && (
              <div className="live-news">
                <div className="live-news-header">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"/><path d="M18 14h-8M15 18h-5M10 6h8v4h-8V6Z"/></svg>
                  Recent News for {scenario.ticker}
                </div>
                <div className="live-news-list">
                  {news.slice(0,4).map((n,i)=>(
                    <div key={i} className="live-news-item" onClick={()=>n.url&&window.open(n.url,'_blank')}>
                      <div className="live-news-headline">{n.title}</div>
                      <div className="live-news-source">{n.source}{n.age ? ' \u00B7 '+n.age : ''}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {!prediction ? (
              <div className="live-predict">
                <div className="live-predict-q">Where did the price go from here?</div>
                <div className="live-predict-btns">
                  <button className="live-predict-btn up" onClick={()=>handlePredict('up')}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M12 19V5M5 12l7-7 7 7"/></svg>
                    UP
                  </button>
                  <button className="live-predict-btn down" onClick={()=>handlePredict('down')}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M12 5v14M19 12l-7 7-7-7"/></svg>
                    DOWN
                  </button>
                </div>
              </div>
            ) : (
              <div className={`live-result ${prediction.correct?'correct':'wrong'}`}>
                <div className="live-result-icon">{prediction.correct?'✓':'✗'}</div>
                <div className="live-result-text" style={{color:prediction.correct?'var(--green)':'var(--red)'}}>
                  {prediction.correct?'Correct!':'Wrong!'}
                </div>
                <div className="live-result-detail">
                  {scenario.ticker} went {scenario.correctAnswer==='up'?'UP':'DOWN'} {Math.abs(scenario.pctChange).toFixed(2)}% over {scenario.timeGapMin||'~45'} min ({scenario.scenarioTime} to {scenario.resultTime})
                </div>
                <div className="live-result-price">
                  <div className="live-result-price-item">
                    <span className="live-result-price-label">Before</span>
                    <span className="live-result-price-val">${scenario.scenarioPrice.toFixed(2)}</span>
                  </div>
                  <div className="live-result-price-item">
                    <span className="live-result-price-label">After</span>
                    <span className="live-result-price-val" style={{color:scenario.correctAnswer==='up'?'var(--green)':'var(--red)'}}>${scenario.resultPrice.toFixed(2)}</span>
                  </div>
                  <div className="live-result-price-item">
                    <span className="live-result-price-label">Change</span>
                    <span className="live-result-price-val" style={{color:scenario.correctAnswer==='up'?'var(--green)':'var(--red)'}}>{scenario.priceChange>=0?'+':''}{scenario.priceChange.toFixed(2)}</span>
                  </div>
                </div>
                <div style={{display:'flex',gap:10,justifyContent:'center',flexWrap:'wrap'}}>
                  <button className="live-again-btn" onClick={handleNewChallenge}>New {scenario.ticker} Challenge</button>
                  <button className="live-again-btn" onClick={()=>{setScenario(null);setPrediction(null);setError(null);setTicker('');setSearchQuery('');}} style={{background:'var(--bg3)',border:'1px solid var(--border)'}}>Pick Another Stock</button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

/* ======== GAME SCREEN ======== */
function GameScreen({scenario,scenarioNum,totalScenarios,score,onAnswer,gameMode,onBack,onHome,canGoBack}) {
  const [chosen,setChosen]=useState(null);
  const [reasoning,setReasoning]=useState('');
  const [confirmed,setConfirmed]=useState(false);
  const [aiGrading,setAiGrading]=useState(false);

  const handleConfirm = async() => {
    if(!chosen) return;
    setConfirmed(true);

    if(gameMode==='reasoning' && reasoning.trim()) {
      setAiGrading(true);
      // Call Claude API for reasoning grading
      const apiKey = localStorage.getItem('mm_claude_api_key');
      if(apiKey) {
        try {
          const resp = await fetch('https://api.anthropic.com/v1/messages', {
            method:'POST',
            headers:{
              'Content-Type':'application/json',
              'x-api-key': apiKey,
              'anthropic-version':'2023-06-01',
              'anthropic-dangerous-direct-browser-access':'true'
            },
            body: JSON.stringify({
              model:'claude-haiku-4-5-20251001',
              max_tokens:300,
              messages:[{role:'user',content:`You are grading a stock market technical analysis prediction. The scenario: "${scenario.question}". The correct answer is ${scenario.correctAnswer.toUpperCase()}. The user chose ${chosen.toUpperCase()} and gave this reasoning: "${reasoning}". Rate their reasoning quality from 0-100 and provide brief feedback (2-3 sentences). Respond in JSON only: {"score":number,"feedback":"string"}`}]
            })
          });
          const data = await resp.json();
          const text = data.content?.[0]?.text || '';
          try {
            const parsed = JSON.parse(text);
            setAiGrading(false);
            onAnswer(chosen, reasoning, parsed);
            return;
          } catch(e) {
            // Try to extract JSON from response
            const match = text.match(/\{[\s\S]*\}/);
            if(match) {
              try {
                const parsed = JSON.parse(match[0]);
                setAiGrading(false);
                onAnswer(chosen, reasoning, parsed);
                return;
              } catch(e2){}
            }
          }
        } catch(e) {
          console.log('Claude API call failed:', e);
        }
      }
      setAiGrading(false);
    }

    onAnswer(chosen, reasoning, null);
  };

  const dc={Beginner:'#26a69a',Intermediate:'#ff9800',Advanced:'#ef5350',Expert:'#9b59b6'};

  return (
    <div className="game-screen">
      <div className="game-subheader">
        <div style={{display:'flex',gap:6}}>
          <button onClick={onHome} style={{display:'flex',alignItems:'center',gap:6,background:'transparent',border:'1px solid var(--border)',borderRadius:8,padding:'6px 12px',color:'var(--text2)',fontSize:13,fontWeight:600,cursor:'pointer',fontFamily:'Inter,sans-serif',transition:'all 0.2s'}} onMouseOver={e=>{e.currentTarget.style.background='var(--bg3)';e.currentTarget.style.borderColor='var(--border2)'}} onMouseOut={e=>{e.currentTarget.style.background='transparent';e.currentTarget.style.borderColor='var(--border)'}}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/></svg>
          </button>
          {canGoBack && <button onClick={onBack} style={{display:'flex',alignItems:'center',gap:6,background:'transparent',border:'1px solid var(--border)',borderRadius:8,padding:'6px 12px',color:'var(--text2)',fontSize:13,fontWeight:600,cursor:'pointer',fontFamily:'Inter,sans-serif',transition:'all 0.2s'}} onMouseOver={e=>{e.currentTarget.style.background='var(--bg3)';e.currentTarget.style.borderColor='var(--border2)'}} onMouseOut={e=>{e.currentTarget.style.background='transparent';e.currentTarget.style.borderColor='var(--border)'}}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
            Prev
          </button>}
        </div>
        <div className="scenario-progress"><span className="progress-label">Scenario</span><div className="progress-dots">{Array.from({length:totalScenarios},(_,i)=><div key={i} className={`progress-dot${i<scenarioNum-1?' done':i===scenarioNum-1?' current':''}`}/>)}</div><span className="progress-fraction">{scenarioNum}/{totalScenarios}</span></div>
      </div>
      <div className="game-body">
        <div className="scenario-meta"><div className="meta-left"><span className="ticker">{scenario.ticker}</span><span className="stock-name">{scenario.stock}</span><span className="stock-date">{scenario.date} | {scenario.timeframe}</span></div><div className="meta-right"><span className="difficulty-badge" style={{borderColor:dc[scenario.difficulty],color:dc[scenario.difficulty]}}>{scenario.difficulty}</span></div></div>
        <div className="question-box"><p>{scenario.question}</p></div>
        <div className="chart-container"><Chart scenarioId={scenario.id}/></div>

        <div className="decision-section">
          <p className="decision-label">Your prediction: what happens next?</p>
          <div className="decision-buttons">
            <button className={`decision-btn buy-btn${chosen==='buy'?' selected':''}`} onClick={()=>!confirmed&&setChosen('buy')} disabled={confirmed}><span className="btn-arrow">{'\u25B2'}</span><span className="btn-main">BUY</span><span className="btn-sub">Bullish: Price rises</span></button>
            <button className={`decision-btn sell-btn${chosen==='sell'?' selected':''}`} onClick={()=>!confirmed&&setChosen('sell')} disabled={confirmed}><span className="btn-arrow">{'\u25BC'}</span><span className="btn-main">SELL</span><span className="btn-sub">Bearish: Price falls</span></button>
          </div>

          {gameMode==='reasoning' && chosen && !confirmed && (
            <div className="reasoning-section">
              <p className="reasoning-label">Explain your reasoning (optional for bonus points)</p>
              <textarea className="reasoning-textarea" placeholder="What do you see in the indicators? Why did you choose this direction? Mention specific signals like RSI levels, MACD crossovers, or SMA positions..." value={reasoning} onChange={e=>setReasoning(e.target.value)} maxLength={500}/>
              <p className="reasoning-hint">{reasoning.length}/500 characters | AI will grade your analysis for bonus points</p>
            </div>
          )}

          <button className={`confirm-btn${chosen?' active':''}${confirmed?' submitting':''}`} onClick={handleConfirm} disabled={!chosen||confirmed}>
            {aiGrading ? 'AI is grading your reasoning...' : confirmed ? 'Analyzing...' : chosen ? `Confirm: ${chosen.toUpperCase()}` : 'Select Buy or Sell first'}
          </button>
        </div>
      </div>
    </div>
  );
}

/* ======== RESULT SCREEN ======== */
function ResultScreen({result,scenarioNum,totalScenarios,onNext}) {
  const {scenario,choice,isCorrect,points,badge,qualityFeedback,aiResult}=result;
  const isLast=scenarioNum===totalScenarios;
  const bc={'Perfect Call':'#26a69a','Good Call':'#2962ff','Lucky Call':'#ff9800','Smart Reasoning':'#9b59b6','Tough Call':'#ff9800','Missed Signal':'#ef5350'}[badge]||'#6b7280';
  const sq={strong:{text:'Clear Signal',color:'#26a69a',desc:'Indicators gave a clear, reliable signal'},moderate:{text:'Mixed Signal',color:'#ff9800',desc:'Indicators gave conflicting or ambiguous signals'},false_signal:{text:'False Signal',color:'#ef5350',desc:'Indicators were misleading, a valuable learning moment'}}[scenario.signalQuality];

  return (
    <div className="result-screen"><div className="result-content">
      <div className={`verdict-banner${isCorrect?' correct':' incorrect'}`}><div className="verdict-icon">{isCorrect?'\u2713':'\u2717'}</div><div className="verdict-text"><div className="verdict-main">{isCorrect?'Correct!':'Not quite.'}</div><div className="verdict-sub">You chose <strong>{choice.toUpperCase()}</strong>, correct was <strong>{scenario.correctAnswer.toUpperCase()}</strong></div></div><div className="verdict-points"><span className="pts-num">+{points}</span><span className="pts-label">pts{result.diffMult && result.diffMult > 1 ? ` (${DIFF_MULT_LABELS[scenario.difficulty]})` : ''}</span></div></div>

      {aiResult && (
        <div className="ai-feedback-card">
          <div className="ai-feedback-header">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#9b59b6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>
            <span>AI Reasoning Analysis</span>
            <span className="ai-feedback-score">+{aiResult.score}</span>
          </div>
          <p className="ai-feedback-text">{aiResult.feedback}</p>
        </div>
      )}

      {/* Indicator readings shown AFTER prediction */}
      <div className="indicator-readings">
        <div className="readings-header">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#9b59b6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>
          <span>What the indicators showed:</span>
        </div>
        <div className="readings-grid">
          {Object.values(scenario.indicators).map(ind=>
            <div key={ind.label} className="reading-card">
              <div className="reading-name">{ind.label}</div>
              <div className="reading-note">{ind.note}</div>
            </div>
          )}
        </div>
      </div>

      <div className="result-grid">
        <div className="result-left">
          <div className="quality-card"><div className="quality-top"><span className="quality-badge" style={{background:bc+'22',color:bc,borderColor:bc+'55'}}>{badge}</span><span className="signal-tag" style={{background:sq.color+'1a',color:sq.color,borderColor:sq.color+'44'}}>{sq.text}</span></div><p className="quality-feedback">{qualityFeedback}</p><p className="signal-desc" style={{color:sq.color}}>{sq.desc}</p></div>
          <div className="explanation-card"><div className="expl-header"><span className="expl-verdict">{scenario.explanation.verdict}</span></div><p className="expl-summary">{scenario.explanation.summary}</p><p className="expl-details">{scenario.explanation.details}</p></div>
        </div>
        <div className="result-right">
          <div className="breakdown-card"><h3 className="breakdown-title">Indicator Breakdown</h3>{scenario.explanation.indicatorBreakdown.map(ind=><div key={ind.name} className={`breakdown-item ${ind.signal}`}><div className="breakdown-indicator"><span className={`signal-dot ${ind.signal}`}/><strong>{ind.name}</strong></div><p>{ind.reading}</p></div>)}</div>
          <div className="outcome-card"><div className="outcome-header"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#26a69a" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg><span>What Actually Happened</span></div><p className="outcome-text">{scenario.explanation.outcome}</p></div>
          <div className="lesson-card"><div className="lesson-header"><span>*</span><span>Key Lesson</span></div><p className="lesson-text">{scenario.explanation.lesson}</p></div>
        </div>
      </div>
      <div className="result-footer"><button className="next-btn" onClick={onNext}>{isLast?'See Final Results':'Next Scenario'} <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg></button><p className="result-progress">Scenario {scenarioNum} of {totalScenarios}</p></div>
    </div></div>
  );
}

/* ======== SUMMARY SCREEN ======== */
function SummaryScreen({answers,totalScore,onRestart,onHome}) {
  const {user} = useAuth();
  const mx=answers.length*100,pct=Math.round(totalScore/mx*100);
  const correct=answers.filter(a=>a.isCorrect).length,pc=answers.filter(a=>a.badge==='Perfect Call').length,sr=answers.filter(a=>a.badge==='Smart Reasoning').length,lc=answers.filter(a=>a.badge==='Lucky Call').length;
  const rank=pct>=90?{r:'Expert Analyst',c:'#9b59b6',d:'Advanced indicator context understanding.'}:pct>=75?{r:'Skilled Trader',c:'#26a69a',d:'Strong pattern recognition.'}:pct>=55?{r:'Intermediate Analyst',c:'#2962ff',d:'Solid foundation. Study false signals.'}:pct>=35?{r:'Learning Investor',c:'#ff9800',d:'Good start. Review missed scenarios.'}:{r:'Market Rookie',c:'#ef5350',d:'Play again and focus on RSI + MACD context.'};
  const bcs={'Perfect Call':'#26a69a','Good Call':'#2962ff','Lucky Call':'#ff9800','Smart Reasoning':'#9b59b6','Tough Call':'#ff9800','Missed Signal':'#ef5350'};
  const circ=2*Math.PI*52;

  // Save session
  useEffect(()=>{
    if(user) {
      saveGameSession(user.uid, {
        totalScore, correct, total: answers.length,
        pct, rank: rank.r,
        answers: answers.map(a=>({ticker:a.scenario.ticker,badge:a.badge,points:a.points,correct:a.isCorrect}))
      });
    }
  },[]);

  return (
    <div className="summary-screen"><div className="summary-content">
      <h1 className="summary-title">Game Complete!</h1>
      <div className="score-card"><div className="score-circle"><svg viewBox="0 0 120 120" className="score-ring"><circle cx="60" cy="60" r="52" fill="none" stroke="#1e2535" strokeWidth="10"/><circle cx="60" cy="60" r="52" fill="none" stroke={rank.c} strokeWidth="10" strokeDasharray={`${pct/100*circ} ${circ}`} strokeLinecap="round" transform="rotate(-90 60 60)"/></svg><div className="score-inner"><span className="score-big">{pct}%</span><span className="score-pts">{totalScore} pts</span></div></div><div className="rank-info"><div className="rank-badge" style={{color:rank.c,borderColor:rank.c+'44',background:rank.c+'12'}}>{rank.r}</div><p className="rank-desc">{rank.d}</p></div></div>
      <div className="stats-grid">
        <div className="stat-card"><span className="stat-num" style={{color:'#26a69a'}}>{correct}/{answers.length}</span><span className="stat-label">Correct</span></div>
        <div className="stat-card"><span className="stat-num" style={{color:'#9b59b6'}}>{pc}</span><span className="stat-label">Perfect Calls</span></div>
        <div className="stat-card"><span className="stat-num" style={{color:'#9b59b6'}}>{sr}</span><span className="stat-label">Smart Reasoning</span></div>
        <div className="stat-card"><span className="stat-num" style={{color:'#ff9800'}}>{lc}</span><span className="stat-label">Lucky Calls</span></div>
      </div>
      <div className="scenario-review"><h2 className="review-title">Scenario Review</h2><div className="review-list">{answers.map((a,i)=><div key={i} className={`review-item${a.isCorrect?' review-correct':' review-wrong'}`}><div className="review-left"><span className={`review-icon${a.isCorrect?' correct':' wrong'}`}>{a.isCorrect?'\u2713':'\u2717'}</span><div className="review-info"><strong>{a.scenario.ticker}</strong><span>{a.scenario.date}</span></div></div><div><span className="review-badge" style={{color:bcs[a.badge],borderColor:(bcs[a.badge]||'#6b7280')+'55'}}>{a.badge}</span></div><div className="review-right"><span className="review-pts">+{a.points}</span></div></div>)}</div></div>
      <div className="takeaways"><h2 className="takeaways-title">Core Takeaways</h2><div className="takeaway-list">{[['RSI below 30',' signals oversold, historically precedes bounces'],['RSI above 70 alone',' is NOT a sell in strong trends; confirm with MACD'],['Death Cross (50/200 SMA)',' confirms downtrends in early bear markets'],['MACD is unreliable',' in sideways markets; flat SMAs = wait for breakout'],['MACD divergence',' (price down, MACD up) = powerful reversal signal'],['Indicators are tools, not rules',' : context changes everything']].map(([s,r])=><div key={s} className="takeaway"><span className="t-icon">{'>'}</span><span><strong>{s}</strong>{r}</span></div>)}</div></div>
      <div style={{display:'flex',gap:12,flexWrap:'wrap'}}>
        <button className="restart-btn" onClick={onRestart}>Play Again <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg></button>
        <button className="restart-btn" onClick={onHome} style={{background:'var(--green)',borderColor:'var(--green)',color:'#fff'}}>Back to Home</button>
      </div>
    </div></div>
  );
}

/* ======== STATISTICS SCREEN ======== */
function AchievementsPanel({userId}) {
  const {unlocked} = useMemo(()=>getUnlockedBadges(userId),[userId]);
  const progress = useMemo(()=>getBadgeProgress(userId),[userId]);
  return (
    <div className="achievements-section">
      <h2 className="achievements-title">{'\u{1F3C5}'} Achievements ({Object.keys(unlocked).length}/{BADGES.length})</h2>
      <div className="achievements-grid">
        {BADGES.map(b=>{
          const isUnlocked = !!unlocked[b.id];
          const prog = progress[b.id];
          return (
            <div key={b.id} className={`badge-card ${isUnlocked?'unlocked':'locked'}`}>
              <div className="badge-icon">{b.icon}</div>
              <div className="badge-info">
                <div className="badge-name">{b.name}</div>
                <div className="badge-desc">{b.desc}</div>
                {isUnlocked ? (
                  <div className="badge-date">Unlocked {new Date(unlocked[b.id].date).toLocaleDateString('en-US',{month:'short',day:'numeric'})}</div>
                ) : prog ? (
                  <div className="badge-progress">
                    {prog.current}/{prog.target}
                    <div className="badge-progress-bar"><div className="badge-progress-fill" style={{width:`${Math.round(prog.current/prog.target*100)}%`}}/></div>
                  </div>
                ) : null}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ======== ADMIN PANEL ======== */
function AdminPanel({onClose, globalData, localLb, onDeleted}) {
  const [entries, setEntries] = useState([]);
  const [filter, setFilter] = useState('');
  const [deleted, setDeleted] = useState(new Set());
  const [deleting, setDeleting] = useState(null);
  const [msg, setMsg] = useState('');

  // Load all entries from Firebase + local
  useEffect(()=>{
    const local = localLb || [];
    if(firebaseReady && db) {
      db.collection('leaderboard').orderBy('score','desc').limit(200).get()
        .then(snap=>{ const arr=[]; snap.forEach(d=>arr.push(d.data())); setEntries(arr.length > 0 ? arr : local); })
        .catch(()=>setEntries(local));
    } else {
      setEntries(local);
    }
  },[]);

  const handleDelete = async (entry) => {
    if(deleting) return;
    if(!confirm(`Delete "${entry.name}" from the leaderboard? This cannot be undone.`)) return;
    setDeleting(entry.uid);
    try {
      // Remove from Firebase
      if(firebaseReady && db) {
        await db.collection('leaderboard').doc(entry.uid).delete();
      }
      // Remove from localStorage leaderboard array
      const lb = JSON.parse(localStorage.getItem('mm_leaderboard')||'[]').filter(e=>e.uid!==entry.uid);
      localStorage.setItem('mm_leaderboard', JSON.stringify(lb));
      // Add to permanent admin blocklist so sync never re-adds this entry
      const blocked = JSON.parse(localStorage.getItem('mm_lb_blocked')||'[]');
      if(!blocked.includes(entry.uid)) {
        blocked.push(entry.uid);
        localStorage.setItem('mm_lb_blocked', JSON.stringify(blocked));
      }
      setDeleted(s=>new Set([...s, entry.uid]));
      setMsg(`Deleted "${entry.name}" from leaderboard.`);
      setTimeout(()=>setMsg(''), 3000);
      if(onDeleted) onDeleted(entry.uid);
    } catch(e) {
      setMsg('Error: ' + e.message);
    }
    setDeleting(null);
  };

  const filtered = entries.filter(e =>
    (e.name||'').toLowerCase().includes(filter.toLowerCase()) ||
    (e.uid||'').toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="admin-overlay" onClick={e=>e.target===e.currentTarget&&onClose()}>
      <div className="admin-modal">
        <div className="admin-header">
          <div className="admin-title">
            <span style={{fontSize:20}}>{'\uD83D\uDEE1\uFE0F'}</span>
            <span style={{color:'#fff'}}>Leaderboard Admin</span>
            <span className="admin-badge">Admin Only</span>
          </div>
          <button className="admin-close" onClick={onClose}>&#x2715;</button>
        </div>

        <input
          className="admin-search"
          placeholder="Search by name or user ID..."
          value={filter}
          onChange={e=>setFilter(e.target.value)}
        />

        {msg && (
          <div style={{padding:'8px 12px',marginBottom:8,borderRadius:8,background:'rgba(38,166,154,0.1)',border:'1px solid rgba(38,166,154,0.3)',fontSize:13,color:'var(--green)',flexShrink:0}}>
            {'\u2713'} {msg}
          </div>
        )}

        <div className="admin-list">
          {filtered.length === 0 && (
            <div style={{textAlign:'center',padding:32,color:'var(--text3)',fontSize:13}}>No entries found</div>
          )}
          {filtered.map((entry,i)=>{
            const isDel = deleted.has(entry.uid);
            const isDeleting = deleting === entry.uid;
            return (
              <div key={entry.uid||i} className="admin-entry" style={isDel?{opacity:0.4}:{}}>
                <div style={{minWidth:32,textAlign:'center',fontSize:13,fontWeight:700,color:'var(--text3)',fontFamily:"'JetBrains Mono',monospace"}}>
                  #{i+1}
                </div>
                <div className="admin-entry-info">
                  <div className="admin-entry-name">{entry.name || 'Unknown'}</div>
                  <div className="admin-entry-meta">
                    {entry.score||0} pts &bull; {entry.accuracy||0}% acc &bull; {entry.scenarios||0} scenarios
                    {entry.livePlayed > 0 ? ` \u00B7 ${entry.livePlayed} live` : ''}
                    {entry.lastPlayed ? ` \u00B7 ${new Date(entry.lastPlayed).toLocaleDateString('en-US',{month:'short',day:'numeric',year:'2-digit'})}` : ''}
                  </div>
                  <div style={{fontSize:10,color:'var(--text3)',marginTop:1,fontFamily:"'JetBrains Mono',monospace"}}>{(entry.uid||'').slice(0,16)}...</div>
                </div>
                <button
                  className={`admin-del-btn${isDel?' deleted':''}`}
                  onClick={()=>!isDel&&handleDelete(entry)}
                  disabled={isDel||isDeleting}
                >
                  {isDeleting ? '...' : isDel ? 'Deleted' : '\uD83D\uDDD1\uFE0F Remove'}
                </button>
              </div>
            );
          })}
        </div>

        <div className="admin-stats">
          {filtered.length} of {entries.length} entries shown &bull; {deleted.size} deleted this session
        </div>
      </div>
    </div>
  );
}

function LeaderboardScreen({onPlay}) {
  const {user} = useAuth();
  const stats = user ? getAllStats(user.uid) : null;
  const [lbTab, setLbTab] = useState('score');
  const [lbMode, setLbMode] = useState('all'); // all, practice, live
  const [globalData, setGlobalData] = useState(null);
  const [loadingGlobal, setLoadingGlobal] = useState(false);
  const [showAdmin, setShowAdmin] = useState(false);
  const [adminAuthed, setAdminAuthed] = useState(false);
  const [adminPwInput, setAdminPwInput] = useState('');
  const [adminPwError, setAdminPwError] = useState(false);

  // Update local leaderboard with current user stats
  const localLb = useMemo(()=>{
    if(user && stats && stats.totalScenarios > 0) {
      let liveStats = null;
      try { liveStats = JSON.parse(localStorage.getItem(`mm_live_stats_${user.uid}`)); } catch(e){}
      return updateLeaderboard(user.uid, user.name, stats, liveStats);
    }
    return getLeaderboard();
  },[user, stats?.totalScenarios]);

  // Fetch global leaderboard from Firebase on mount + sync any local-only entries up
  useEffect(()=>{
    if(firebaseReady) {
      setLoadingGlobal(true);

      // Get admin blocklist (UIDs permanently deleted by admin)
      const blocked = new Set(JSON.parse(localStorage.getItem('mm_lb_blocked') || '[]'));
      // Clean any blocked entries out of localStorage leaderboard
      if(blocked.size > 0) {
        const cleaned = JSON.parse(localStorage.getItem('mm_leaderboard') || '[]').filter(e => !blocked.has(e.uid));
        localStorage.setItem('mm_leaderboard', JSON.stringify(cleaned));
        // Also delete from Firebase (in case they got re-added)
        blocked.forEach(uid => {
          db.collection('leaderboard').doc(uid).delete().catch(()=>{});
        });
      }
      // Push remaining local entries that aren't in Firebase yet (skip blocked)
      const localEntries = JSON.parse(localStorage.getItem('mm_leaderboard') || '[]').filter(e => !blocked.has(e.uid));
      if(localEntries.length > 0) {
        const batch = db.batch();
        localEntries.forEach(entry => {
          if(entry.uid) {
            const ref = db.collection('leaderboard').doc(entry.uid);
            batch.set(ref, entry, {merge: true});
          }
        });
        batch.commit().catch(e => console.warn('Sync to Firebase failed:', e));
      }

      // Then fetch
      fetchGlobalLeaderboard().then(data=>{
        if(data !== null) setGlobalData(data);  // show GLOBAL even if empty
        setLoadingGlobal(false);
      });
    }
  },[]);

  const leaderboard = (globalData !== null ? globalData : null) || localLb;
  const isGlobal = globalData !== null;  // true as soon as Firebase responds (even if empty)

  const sorted = useMemo(()=>{
    let lb = [...(leaderboard||[])];
    // Sort by selected column
    if(lbTab==='score') lb.sort((a,b)=>b.score-a.score);
    else if(lbTab==='accuracy') lb.sort((a,b)=>b.accuracy-a.accuracy);
    else if(lbTab==='scenarios') lb.sort((a,b)=>b.scenarios-a.scenarios);
    else if(lbTab==='live') lb.sort((a,b)=>(b.livePlayed||0)-(a.livePlayed||0));
    else if(lbTab==='liveAcc') lb.sort((a,b)=>(b.liveAccuracy||0)-(a.liveAccuracy||0));
    else if(lbTab==='streak') lb.sort((a,b)=>(b.liveBestStreak||0)-(a.liveBestStreak||0));
    return lb;
  },[leaderboard, lbTab]);

  const myRank = user ? sorted.findIndex(e=>e.uid===user.uid)+1 : 0;
  const myEntry = user ? sorted.find(e=>e.uid===user.uid) : null;

  return (
    <div className="stats-screen"><div className="stats-content">
      <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',flexWrap:'wrap',gap:12,marginBottom:8}}>
        <h1 className="stats-title" style={{animation:'fadeInUp 0.5s ease both',marginBottom:0}}>Leaderboard</h1>
        <div style={{display:'flex',alignItems:'center',gap:8,animation:'fadeInUp 0.5s ease 0.1s both'}}>
          {isGlobal && <span style={{display:'inline-flex',alignItems:'center',gap:6,fontSize:11,fontWeight:700,color:'var(--green)',border:'1px solid rgba(38,166,154,0.3)',borderRadius:100,padding:'4px 12px',background:'rgba(38,166,154,0.08)'}}><span style={{width:6,height:6,borderRadius:'50%',background:'var(--green)',animation:'pulse 1.5s ease infinite'}}/>GLOBAL</span>}
          {!isGlobal && <span style={{display:'inline-flex',alignItems:'center',gap:6,fontSize:11,fontWeight:700,color:'var(--orange)',border:'1px solid rgba(255,152,0,0.3)',borderRadius:100,padding:'4px 12px',background:'rgba(255,152,0,0.08)'}}>LOCAL</span>}
        </div>
      </div>
      <p className="stats-sub" style={{animation:'fadeInUp 0.5s ease 0.1s both'}}>{isGlobal ? 'Competing against players worldwide. Rankings update in real-time.' : 'Connect Firebase to compete globally. Local rankings shown.'}</p>

      {/* Your rank highlight */}
      {myEntry && (
        <div style={{display:'flex',alignItems:'center',gap:20,padding:'20px 24px',background:'var(--bg3)',border:'1px solid var(--border)',borderRadius:'var(--radius)',marginBottom:24,animation:'fadeInUp 0.5s ease 0.15s both',flexWrap:'wrap'}}>
          <div style={{display:'flex',flexDirection:'column',alignItems:'center',minWidth:60}}>
            <span style={{fontSize:36,fontWeight:900,fontFamily:"'JetBrains Mono',monospace",color:myRank===1?'#ffd700':myRank===2?'#c0c0c0':myRank===3?'#cd7f32':'var(--green)'}}>#{myRank}</span>
            <span style={{fontSize:11,color:'var(--text3)',textTransform:'uppercase',letterSpacing:'0.06em'}}>Your Rank</span>
          </div>
          <div style={{flex:1,display:'flex',gap:20,flexWrap:'wrap'}}>
            <div style={{display:'flex',flexDirection:'column',alignItems:'center'}}><span style={{fontSize:22,fontWeight:800,fontFamily:"'JetBrains Mono',monospace",color:'var(--accent)'}}>{myEntry.score}</span><span style={{fontSize:11,color:'var(--text3)'}}>Score</span></div>
            <div style={{display:'flex',flexDirection:'column',alignItems:'center'}}><span style={{fontSize:22,fontWeight:800,fontFamily:"'JetBrains Mono',monospace",color:'var(--green)'}}>{myEntry.accuracy}%</span><span style={{fontSize:11,color:'var(--text3)'}}>Accuracy</span></div>
            <div style={{display:'flex',flexDirection:'column',alignItems:'center'}}><span style={{fontSize:22,fontWeight:800,fontFamily:"'JetBrains Mono',monospace",color:'var(--purple)'}}>{myEntry.scenarios}</span><span style={{fontSize:11,color:'var(--text3)'}}>Scenarios</span></div>
            <div style={{width:1,background:'var(--border)',alignSelf:'stretch',margin:'0 4px'}}/>
            <div style={{display:'flex',flexDirection:'column',alignItems:'center'}}><span style={{fontSize:22,fontWeight:800,fontFamily:"'JetBrains Mono',monospace",color:'var(--orange)'}}>{myEntry.livePlayed||0}</span><span style={{fontSize:11,color:'var(--text3)'}}>Live Plays</span></div>
            <div style={{display:'flex',flexDirection:'column',alignItems:'center'}}><span style={{fontSize:22,fontWeight:800,fontFamily:"'JetBrains Mono',monospace",color:'#ef5350'}}>{myEntry.liveAccuracy||0}%</span><span style={{fontSize:11,color:'var(--text3)'}}>Live Acc</span></div>
            <div style={{display:'flex',flexDirection:'column',alignItems:'center'}}><span style={{fontSize:22,fontWeight:800,fontFamily:"'JetBrains Mono',monospace",color:'#26c6da'}}>{myEntry.liveBestStreak||0}</span><span style={{fontSize:11,color:'var(--text3)'}}>Best Streak</span></div>
          </div>
        </div>
      )}

      {/* Loading indicator */}
      {loadingGlobal && (
        <div style={{textAlign:'center',padding:16,fontSize:13,color:'var(--text3)'}}>
          <div style={{width:24,height:24,border:'2px solid var(--border)',borderTopColor:'var(--accent)',borderRadius:'50%',animation:'spin 0.8s linear infinite',margin:'0 auto 8px'}}/>
          Loading global leaderboard...
        </div>
      )}

      {/* Sort tabs */}
      <div className="leaderboard-section" style={{animation:'fadeInUp 0.5s ease 0.2s both'}}>
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',flexWrap:'wrap',gap:8,marginBottom:16}}>
          <div className="lb-tabs" style={{marginBottom:0}}>
            {[['score','Score'],['accuracy','Accuracy'],['scenarios','Scenarios'],['live','Live Plays'],['liveAcc','Live Acc'],['streak','Streak']].map(([id,label])=>(
              <button key={id} className={`lb-tab${lbTab===id?' active':''}`} onClick={()=>setLbTab(id)}>{label}</button>
            ))}
          </div>
        </div>
        {sorted.length === 0 ? (
          <div className="lb-empty">
            <div style={{fontSize:48,marginBottom:12}}>{'\u{1F3C6}'}</div>
            <p style={{fontSize:15,marginBottom:8}}>No players on the leaderboard yet.</p>
            <p style={{fontSize:13,color:'var(--text3)',marginBottom:16}}>Complete scenarios to claim the #1 spot!</p>
            <button className="stats-play-btn" onClick={onPlay}>Start Playing</button>
          </div>
        ) : (
          <table className="lb-table">
            <thead><tr>
              <th>#</th>
              <th>Player</th>
              <th>Practice</th>
              <th>Live</th>
              <th>Last Active</th>
            </tr></thead>
            <tbody>
              {sorted.slice(0,50).map((entry,i)=>(
                <tr key={entry.uid||i} style={entry.uid===user?.uid?{background:'rgba(38,166,154,0.06)'}:{}}>
                  <td className={`lb-rank${i===0?' gold':i===1?' silver':i===2?' bronze':''}`}>
                    {i===0?'\u{1F947}':i===1?'\u{1F948}':i===2?'\u{1F949}':i+1}
                  </td>
                  <td className={entry.uid===user?.uid?'lb-you':'lb-name'}>
                    {entry.name}{entry.uid===user?.uid?' (You)':''}
                  </td>
                  <td style={{fontSize:12}}>
                    <span style={{fontWeight:700,color:'var(--accent)',fontFamily:"'JetBrains Mono',monospace"}}>{entry.score}</span>
                    <span style={{color:'var(--text3)'}}> pts · {entry.accuracy}% · {entry.scenarios} sc</span>
                  </td>
                  <td style={{fontSize:12}}>
                    <span style={{fontWeight:700,color:'var(--orange)',fontFamily:"'JetBrains Mono',monospace"}}>{entry.livePlayed||0}</span>
                    <span style={{color:'var(--text3)'}}> plays · {entry.liveAccuracy||0}% · {entry.liveBestStreak||0} streak</span>
                  </td>
                  <td style={{fontSize:12,color:'var(--text3)'}}>
                    {entry.lastPlayed ? new Date(entry.lastPlayed).toLocaleDateString('en-US',{month:'short',day:'numeric'}) : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Firebase status note */}
      <div style={{padding:'16px 20px',background:isGlobal?'rgba(38,166,154,0.06)':'rgba(255,152,0,0.06)',border:`1px solid ${isGlobal?'rgba(38,166,154,0.2)':'rgba(255,152,0,0.2)'}`,borderRadius:'var(--radius)',fontSize:13,color:'var(--text2)',marginTop:8,animation:'fadeInUp 0.5s ease 0.3s both',display:'flex',alignItems:'flex-start',gap:10}}>
        <span style={{fontSize:16,flexShrink:0}}>{isGlobal?'\u{2705}':'\u{1F4A1}'}</span>
        <span>{isGlobal
          ? 'Connected to global leaderboard. Your scores are synced worldwide in real-time!'
          : 'Leaderboard is local to this browser. To enable global rankings, set up Firebase (free) and add your config to the site.'
        }</span>
      </div>

      {/* Friend Leaderboard */}
      <FriendLeaderboard user={user} globalData={globalData} localLb={localLb}/>

      {/* Admin trigger */}
      <div style={{textAlign:'center',marginTop:8}}>
        <span className="admin-trigger" onClick={()=>setShowAdmin(true)}>
          {'\uD83D\uDD10'} Admin Panel
        </span>
      </div>

      {/* Admin password gate */}
      {showAdmin && !adminAuthed && (
        <div className="admin-overlay" onClick={e=>e.target===e.currentTarget&&(setShowAdmin(false),setAdminPwInput(''),setAdminPwError(false))}>
          <div style={{background:'var(--bg2)',border:'1px solid rgba(239,83,80,0.4)',borderRadius:16,padding:28,width:320,animation:'fadeInScale 0.3s cubic-bezier(0.22,1,0.36,1)'}}>
            <div style={{fontSize:16,fontWeight:800,color:'#fff',marginBottom:6,display:'flex',alignItems:'center',gap:8}}>
              {'\uD83D\uDD10'} Admin Access
            </div>
            <div style={{fontSize:13,color:'var(--text2)',marginBottom:16}}>Enter admin password to manage the leaderboard.</div>
            <input
              type="password"
              placeholder="Admin password..."
              value={adminPwInput}
              onChange={e=>{setAdminPwInput(e.target.value);setAdminPwError(false);}}
              onKeyDown={e=>{
                if(e.key==='Enter') {
                  if(adminPwInput===ADMIN_PASSWORD){setAdminAuthed(true);setAdminPwInput('');}
                  else{setAdminPwError(true);}
                }
                if(e.key==='Escape'){setShowAdmin(false);setAdminPwInput('');}
              }}
              style={{width:'100%',padding:'10px 12px',borderRadius:8,border:`1px solid ${adminPwError?'var(--red)':'var(--border)'}`,background:'var(--bg3)',color:'var(--text)',fontSize:14,fontFamily:'Inter,sans-serif',outline:'none',marginBottom:8}}
              autoFocus
            />
            {adminPwError && <div style={{color:'var(--red)',fontSize:12,marginBottom:8}}>{'\u274C'} Incorrect password</div>}
            <div style={{display:'flex',gap:8}}>
              <button onClick={()=>{if(adminPwInput===ADMIN_PASSWORD){setAdminAuthed(true);setAdminPwInput('');}else{setAdminPwError(true);}}}
                style={{flex:1,padding:'10px',borderRadius:8,border:'none',background:'var(--red)',color:'#fff',fontSize:13,fontWeight:700,cursor:'pointer',fontFamily:'Inter,sans-serif'}}>
                Unlock
              </button>
              <button onClick={()=>{setShowAdmin(false);setAdminPwInput('');setAdminPwError(false);}}
                style={{padding:'10px 16px',borderRadius:8,border:'1px solid var(--border)',background:'var(--bg3)',color:'var(--text)',fontSize:13,cursor:'pointer',fontFamily:'Inter,sans-serif'}}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Admin panel (authenticated) */}
      {showAdmin && adminAuthed && (
        <AdminPanel
          onClose={()=>{setShowAdmin(false);setAdminAuthed(false);}}
          globalData={globalData}
          localLb={localLb}
          onDeleted={(uid)=>{
            if(globalData) setGlobalData(d=>d.filter(e=>e.uid!==uid));
          }}
        />
      )}
    </div></div>
  );
}

/* ======== FRIEND LEADERBOARD COMPONENT ======== */
function FriendLeaderboard({user, globalData, localLb}) {
  const [myCode] = useState(()=>{
    if(!user) return null;
    let c = localStorage.getItem('mm_friend_code');
    if(!c) {
      // Generate 6-char code from uid hash
      const h = user.uid.split('').reduce((a,b)=>(a<<5)-a+b.charCodeAt(0),0);
      c = Math.abs(h).toString(36).toUpperCase().padStart(6,'0').slice(0,6);
      localStorage.setItem('mm_friend_code', c);
    }
    return c;
  });
  const [joinInput, setJoinInput] = useState('');
  const [joinedCodes, setJoinedCodes] = useState(()=>{
    try { return JSON.parse(localStorage.getItem('mm_friend_groups')||'[]'); } catch(e){return [];}
  });
  const [copied, setCopied] = useState(false);
  const [joinMsg, setJoinMsg] = useState('');
  const [friendMembers, setFriendMembers] = useState([]);

  // Register own code in Firebase and fetch friends
  useEffect(()=>{
    if(!user || !myCode || !firebaseReady || !db) return;
    // Register this user under their code
    db.collection('friendGroups').doc(myCode).set({
      code: myCode, creatorUid: user.uid, updatedAt: new Date().toISOString()
    }, {merge:true}).catch(()=>{});
    // Add self to code's members
    db.collection('friendGroups').doc(myCode).collection('members').doc(user.uid).set({
      uid: user.uid, name: user.name, score: 0, lastUpdated: new Date().toISOString()
    }, {merge:true}).catch(()=>{});
  },[user, myCode]);

  // Fetch members from all joined groups
  useEffect(()=>{
    if(!user || joinedCodes.length === 0) {
      // Show local people with matching codes from localLb
      return;
    }
    if(!firebaseReady || !db) {
      // Fallback: show local leaderboard
      setFriendMembers(localLb || []);
      return;
    }
    // Fetch members from Firebase for all codes including own
    const allCodes = [...new Set([myCode, ...joinedCodes].filter(Boolean))];
    const fetches = allCodes.map(code =>
      db.collection('friendGroups').doc(code).collection('members').get()
        .then(snap => { const m = []; snap.forEach(d=>m.push(d.data())); return m; })
        .catch(()=>[])
    );
    Promise.all(fetches).then(results=>{
      const seen = new Set();
      const merged = [];
      results.flat().forEach(m=>{
        if(!seen.has(m.uid)) { seen.add(m.uid); merged.push(m); }
      });
      // Enrich with leaderboard data
      const allLb = globalData || localLb || [];
      const enriched = merged.map(m=>{
        const lb = allLb.find(e=>e.uid===m.uid);
        return lb ? {...lb, ...m} : m;
      }).sort((a,b)=>(b.score||0)-(a.score||0));
      setFriendMembers(enriched);
    });
  },[joinedCodes, user, globalData, localLb]);

  const handleCopy = () => {
    const url = `${window.location.origin}${window.location.pathname}?friend=${myCode}`;
    navigator.clipboard.writeText(url).catch(()=>{});
    setCopied(true);
    setTimeout(()=>setCopied(false), 2000);
  };

  const handleJoin = () => {
    const code = joinInput.trim().toUpperCase().slice(0,6);
    if(!code || code.length < 4) { setJoinMsg('Enter a valid code'); return; }
    if(code === myCode) { setJoinMsg("That's your own code!"); return; }
    if(joinedCodes.includes(code)) { setJoinMsg('Already in this group'); return; }
    const newCodes = [...joinedCodes, code];
    setJoinedCodes(newCodes);
    localStorage.setItem('mm_friend_groups', JSON.stringify(newCodes));
    // Register self in that group's members
    if(firebaseReady && db && user) {
      db.collection('friendGroups').doc(code).collection('members').doc(user.uid).set({
        uid: user.uid, name: user.name, score: 0, lastUpdated: new Date().toISOString()
      }, {merge:true}).catch(()=>{});
    }
    setJoinInput('');
    setJoinMsg('\u2713 Joined! Loading members...');
    setTimeout(()=>setJoinMsg(''), 3000);
  };

  // Handle ?friend=CODE in URL on load
  useEffect(()=>{
    const params = new URLSearchParams(window.location.search);
    const urlCode = params.get('friend');
    if(urlCode && user && urlCode !== myCode && !joinedCodes.includes(urlCode)) {
      const newCodes = [...joinedCodes, urlCode];
      setJoinedCodes(newCodes);
      localStorage.setItem('mm_friend_groups', JSON.stringify(newCodes));
      if(firebaseReady && db) {
        db.collection('friendGroups').doc(urlCode).collection('members').doc(user.uid).set({
          uid: user.uid, name: user.name, score: 0, lastUpdated: new Date().toISOString()
        }, {merge:true}).catch(()=>{});
      }
    }
  },[user]);

  if(!user) return (
    <div className="friend-section" style={{marginTop:20}}>
      <div className="friend-title">{'\uD83D\uDC65'} Friend Leaderboard</div>
      <p style={{fontSize:13,color:'var(--text2)'}}>Create a profile to generate your friend invite code and compete with friends!</p>
    </div>
  );

  return (
    <div className="friend-section" style={{marginTop:20}}>
      <div className="friend-title">{'\uD83D\uDC65'} Friend Leaderboard</div>
      <p style={{fontSize:13,color:'var(--text2)',marginBottom:14}}>Share your code with friends. Anyone who enters it will appear on your private leaderboard.</p>

      {/* Your code */}
      <div>
        <div style={{fontSize:11,fontWeight:600,color:'var(--text3)',textTransform:'uppercase',letterSpacing:'0.08em',marginBottom:8}}>Your Invite Code</div>
        <div style={{display:'flex',alignItems:'center',gap:10,flexWrap:'wrap'}}>
          <span className="friend-code-display">{myCode}</span>
          <div className="friend-actions">
            <button className="friend-copy-btn" onClick={handleCopy}>{copied ? '\u2713 Copied!' : '\uD83D\uDD17 Copy Link'}</button>
          </div>
        </div>
        <div style={{fontSize:11,color:'var(--text3)',marginTop:6}}>Share link: <code style={{fontSize:11,color:'var(--text2)'}}>{window.location.origin}?friend={myCode}</code></div>
      </div>

      {/* Join a group */}
      <div style={{marginTop:16}}>
        <div style={{fontSize:11,fontWeight:600,color:'var(--text3)',textTransform:'uppercase',letterSpacing:'0.08em',marginBottom:8}}>Join a Friend's Group</div>
        <div className="friend-join-row">
          <input className="friend-join-input" placeholder="Enter friend code..." value={joinInput} onChange={e=>setJoinInput(e.target.value.toUpperCase())} maxLength={6} onKeyDown={e=>e.key==='Enter'&&handleJoin()}/>
          <button className="friend-join-btn" onClick={handleJoin}>Join</button>
        </div>
        {joinMsg && <div style={{fontSize:12,color:'var(--green)',marginTop:6}}>{joinMsg}</div>}
        {joinedCodes.length > 0 && <div style={{fontSize:11,color:'var(--text3)',marginTop:4}}>In {joinedCodes.length} group(s): {joinedCodes.join(', ')}</div>}
      </div>

      {/* Friend members leaderboard */}
      {friendMembers.length > 0 && (
        <div style={{marginTop:16}}>
          <div style={{fontSize:11,fontWeight:600,color:'var(--text3)',textTransform:'uppercase',letterSpacing:'0.08em',marginBottom:8}}>Group Rankings ({friendMembers.length} players)</div>
          <div className="friend-lb-list">
            {friendMembers.slice(0,20).map((m,i)=>(
              <div key={m.uid||i} className={`friend-lb-item${m.uid===user.uid?' me':''}`}>
                <span className="friend-lb-rank">{i===0?'\uD83E\uDD47':i===1?'\uD83E\uDD48':i===2?'\uD83E\uDD49':i+1}</span>
                <span className="friend-lb-name">{m.name}{m.uid===user.uid?' (You)':''}</span>
                <span className="friend-lb-score">{m.score||0} pts</span>
                {m.accuracy > 0 && <span style={{fontSize:11,color:'var(--text3)',marginLeft:4}}>{m.accuracy}%</span>}
              </div>
            ))}
          </div>
        </div>
      )}
      {friendMembers.length === 0 && joinedCodes.length === 0 && (
        <div style={{marginTop:14,fontSize:13,color:'var(--text3)',fontStyle:'italic'}}>Share your code with friends to see their scores here!</div>
      )}
    </div>
  );
}

function StatsScreen({onPlay}) {
  const {user} = useAuth();
  const stats = user ? getAllStats(user.uid) : {totalGames:0,totalPoints:0,totalCorrect:0,totalScenarios:0,bestScore:0,avgScore:0,sessions:[]};
  const [apiKey,setApiKey] = useState(localStorage.getItem('mm_claude_api_key')||'');
  const [saved,setSaved] = useState(false);

  const handleSaveKey = () => {
    if(apiKey.trim()) localStorage.setItem('mm_claude_api_key', apiKey.trim());
    else localStorage.removeItem('mm_claude_api_key');
    setSaved(true);
    setTimeout(()=>setSaved(false),2000);
  };

  return (
    <div className="stats-screen"><div className="stats-content">
      <h1 className="stats-title">Your Statistics</h1>
      <p className="stats-sub">{user ? `Tracking progress for ${user.name}` : 'Create a profile to track your progress across sessions'}</p>

      <div className="stats-overview">
        <div className="stat-card"><span className="stat-num" style={{color:'var(--green)'}}>{stats.totalGames}</span><span className="stat-label">Games Played</span></div>
        <div className="stat-card"><span className="stat-num" style={{color:'var(--accent)'}}>{stats.totalPoints}</span><span className="stat-label">Total Points</span></div>
        <div className="stat-card"><span className="stat-num" style={{color:'var(--purple)'}}>{stats.totalCorrect}/{stats.totalScenarios}</span><span className="stat-label">Correct Calls</span></div>
        <div className="stat-card"><span className="stat-num" style={{color:'var(--orange)'}}>{stats.bestScore}</span><span className="stat-label">Best Score</span></div>
        <div className="stat-card"><span className="stat-num" style={{color:'#26c6da'}}>{stats.avgScore}</span><span className="stat-label">Avg Score</span></div>
      </div>

      {/* Achievements */}
      {user && <AchievementsPanel userId={user.uid}/>}

      <div className="stats-history">
        <h2 className="stats-history-title">Scenario Results</h2>
        {stats.totalScenarios === 0 ? (
          <div className="stats-empty">
            <p>{user ? 'No scenarios completed yet. Start your first challenge!' : 'Create a profile to save and view your progress.'}</p>
            <button className="stats-play-btn" onClick={onPlay}>Play Now</button>
          </div>
        ) : (
          <>
            {/* Individual scenario results */}
            {stats.scenarioResults && Object.keys(stats.scenarioResults).length > 0 && (
              <div style={{display:'flex',flexDirection:'column',gap:8,marginBottom:16}}>
                {Object.entries(stats.scenarioResults).map(([id,r])=>(
                  <div key={id} className={`review-item${r.isCorrect?' review-correct':' review-wrong'}`}>
                    <div className="review-left">
                      <span className={`review-icon${r.isCorrect?' correct':' wrong'}`}>{r.isCorrect?'\u2713':'\u2717'}</span>
                      <div className="review-info"><strong>{r.ticker}</strong><span>{r.badge}</span></div>
                    </div>
                    <div className="review-right"><span className="review-pts">+{r.points}</span></div>
                  </div>
                ))}
              </div>
            )}
            {/* Full game sessions */}
            {stats.sessions.length > 0 && (
              <>
                <h3 style={{fontSize:12,fontWeight:700,color:'var(--text3)',textTransform:'uppercase',letterSpacing:'0.08em',marginBottom:10,marginTop:8}}>Completed Games</h3>
                {stats.sessions.slice().reverse().map((s,i)=>(
                  <div key={i} className="stats-session">
                    <div className="stats-session-header">
                      <span className="stats-session-date">{new Date(s.date).toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric'})}</span>
                      <span className="stats-session-score">{s.totalScore} pts</span>
                    </div>
                    <div className="stats-session-details">
                      <span>{s.correct}/{s.total} correct</span>
                      <span>{s.pct}% accuracy</span>
                      <span>{s.rank}</span>
                    </div>
                  </div>
                ))}
              </>
            )}
          </>
        )}
      </div>

      {stats.totalScenarios > 0 && (
        <button onClick={()=>{if(confirm('Clear all your statistics and scenario progress? This will also remove you from the leaderboard. This cannot be undone.')){localStorage.removeItem('mm_sessions_'+user.uid);localStorage.removeItem('mm_results_'+user.uid);localStorage.removeItem('mm_badges_'+user.uid);localStorage.removeItem('mm_live_stats_'+user.uid);const lb=JSON.parse(localStorage.getItem('mm_leaderboard')||'[]').filter(e=>e.uid!==user.uid);localStorage.setItem('mm_leaderboard',JSON.stringify(lb));if(firebaseReady&&db){db.collection('leaderboard').doc(user.uid).delete().catch(e=>console.warn('Firebase delete failed:',e));}location.reload();}}} style={{padding:'10px 20px',borderRadius:8,border:'1px solid rgba(239,83,80,0.3)',background:'rgba(239,83,80,0.08)',color:'var(--red)',fontSize:13,fontWeight:600,cursor:'pointer',fontFamily:'Inter,sans-serif',transition:'all 0.2s',marginTop:16}}>Clear All Statistics</button>
      )}

      <div className="settings-section">
        <h2 className="settings-title">Reasoning Mode Settings</h2>
        <p style={{fontSize:13,color:'var(--text2)',marginBottom:14}}>To enable AI-powered reasoning grading, enter your Anthropic API key (free tier available at console.anthropic.com). Your key is stored only in this browser.</p>
        <div className="settings-row">
          <label>API Key</label>
          <input className="settings-input" type="password" placeholder="sk-ant-..." value={apiKey} onChange={e=>setApiKey(e.target.value)}/>
          <button className="settings-save" onClick={handleSaveKey}>{saved?'Saved!':'Save'}</button>
        </div>
        <p className="settings-note">Get your API key from console.anthropic.com. The key never leaves your browser.</p>
      </div>
    </div></div>
  );
}

/* ======== BADGE NOTIFICATION COMPONENT ======== */
function BadgeNotification({badge, onClose}) {
  const [exiting, setExiting] = useState(false);
  useEffect(()=>{
    const t = setTimeout(()=>{ setExiting(true); setTimeout(onClose, 420); }, 4500);
    return ()=>clearTimeout(t);
  },[]);
  return (
    <div className={`badge-toast${exiting?' exit':''}`}>
      <div className="badge-toast-icon">{badge.icon}</div>
      <div className="badge-toast-text">
        <span className="badge-toast-label">{'\u{1F3C5}'} Badge Unlocked!</span>
        <span className="badge-toast-name">{badge.name}</span>
        <span className="badge-toast-desc">{badge.desc}</span>
      </div>
      <button className="badge-toast-close" onClick={()=>{setExiting(true);setTimeout(onClose,420);}}>&#x2715;</button>
    </div>
  );
}

/* ======== APP ======== */
function AppInner() {
  const {user} = useAuth();
  const [showIntro,setShowIntro]=useState(true);
  const [activeTab,setActiveTab]=useState('home');
  const [gameState,setGameState]=useState('idle'); // idle, playing, result, summary
  const [idx,setIdx]=useState(0);
  const [answers,setAnswers]=useState([]);
  const [lastResult,setLastResult]=useState(null);
  const [gameMode,setGameMode]=useState(localStorage.getItem('mm_game_mode')||'prediction');
  const [difficulty,setDifficulty]=useState(localStorage.getItem('mm_difficulty')||'All');
  const [newBadgeQueue,setNewBadgeQueue]=useState([]);
  const [soundOn,setSoundOn]=useState(SoundSystem.enabled);

  const filteredScenarios = useMemo(()=>{
    if(difficulty==='All') return scenarios;
    return scenarios.filter(s=>s.difficulty===difficulty);
  },[difficulty]);

  const handleDifficultyChange = (d) => {
    setDifficulty(d);
    localStorage.setItem('mm_difficulty', d);
  };

  const handleModeChange = (mode) => {
    setGameMode(mode);
    localStorage.setItem('mm_game_mode', mode);
  };

  const handleStartGame = () => {
    // Resume from first incomplete scenario within filtered set
    const startIdx = user ? getNextScenarioIndex(user.uid, filteredScenarios) : 0;
    setIdx(startIdx);
    setAnswers([]);
    setLastResult(null);
    setGameState('playing');
    setActiveTab('play');
  };

  const handleBackToHome = () => {
    setGameState('idle');
    setActiveTab('home');
  };

  const handlePrevScenario = () => {
    if(idx > 0) { setIdx(i=>i-1); setGameState('playing'); }
  };

  const handleAnswer = useCallback((choice, reasoning, aiResult)=>{
    const sc=filteredScenarios[idx];
    const ok=choice===sc.correctAnswer;
    const sq=sc.signalQuality;
    const diffMult = DIFF_MULTIPLIERS[sc.difficulty] || 1.0;
    let pts=0,badge='';
    if(ok){if(sq==='strong'){pts=100;badge='Perfect Call';}else if(sq==='moderate'){pts=75;badge='Good Call';}else{pts=60;badge='Lucky Call';}}
    else{if(sq==='strong'){pts=0;badge='Missed Signal';}else if(sq==='moderate'){pts=10;badge='Tough Call';}else{pts=40;badge='Smart Reasoning';}}
    pts = Math.round(pts * diffMult);

    // Add AI reasoning bonus
    if(aiResult && aiResult.score) {
      pts += Math.round(aiResult.score / 5); // Up to 20 bonus points
    }

    const r={scenario:sc,choice,isCorrect:ok,points:pts,badge,qualityFeedback:sc.decisionFeedback[choice].feedback,reasoning,aiResult,diffMult};
    setAnswers(p=>[...p,r]);setLastResult(r);setGameState('result');

    // Sound feedback
    SoundSystem.play(ok ? 'correct' : 'wrong');

    // Save individual result immediately to localStorage
    if(user) {
      saveScenarioResult(user.uid, sc.id, {
        ticker: sc.ticker, choice, isCorrect: ok, points: pts, badge,
      });
      // Check for newly unlocked badges
      const {newlyUnlocked} = getUnlockedBadges(user.uid);
      if(newlyUnlocked.length > 0) {
        setNewBadgeQueue(q => [...q, ...newlyUnlocked]);
        SoundSystem.play('badge');
      }
      // Update leaderboard
      const latestStats = getAllStats(user.uid);
      let liveStats = null;
      try { liveStats = JSON.parse(localStorage.getItem(`mm_live_stats_${user.uid}`)); } catch(e){}
      updateLeaderboard(user.uid, user.name, latestStats, liveStats);
    }
  },[idx, user, filteredScenarios]);

  const handleNext = useCallback(()=>{
    if(idx+1>=filteredScenarios.length){setGameState('summary');}
    else{setIdx(i=>i+1);setGameState('playing');}
  },[idx, filteredScenarios]);

  const totalScore=answers.reduce((s,a)=>s+a.points,0);
  const showScore = activeTab==='play' && (gameState==='playing'||gameState==='result');

  // Map tab to content
  const renderContent = () => {
    if(activeTab==='home') return <HomeScreen onPlay={()=>setActiveTab('play')}/>;
    if(activeTab==='live') return <LiveChallengeScreen/>;
    if(activeTab==='leaderboard') return <LeaderboardScreen onPlay={handleStartGame}/>;
    if(activeTab==='stats') return <StatsScreen onPlay={handleStartGame}/>;
    if(activeTab==='play') {
      if(gameState==='playing') return <GameScreen scenario={filteredScenarios[idx]} scenarioNum={idx+1} totalScenarios={filteredScenarios.length} score={totalScore} onAnswer={handleAnswer} gameMode={gameMode} onBack={handlePrevScenario} onHome={handleBackToHome} canGoBack={idx>0}/>;
      if(gameState==='result' && lastResult) return <ResultScreen result={lastResult} scenarioNum={idx+1} totalScenarios={filteredScenarios.length} onNext={handleNext}/>;
      if(gameState==='summary') return <SummaryScreen answers={answers} totalScore={totalScore} onRestart={handleStartGame} onHome={()=>setActiveTab('home')}/>;
      return <PlayScreen onStart={handleStartGame} difficulty={difficulty} onDifficultyChange={handleDifficultyChange} scenarioCount={filteredScenarios.length} gameMode={gameMode} onModeChange={handleModeChange}/>;
    }
    return <HomeScreen onPlay={()=>setActiveTab('play')}/>;
  };

  const handleSoundToggle = () => {
    const newState = SoundSystem.toggle();
    setSoundOn(newState);
    if(newState) SoundSystem.play('correct');
  };

  return (
    <div className="app">
      {showIntro && <IntroOverlay onDismiss={()=>setShowIntro(false)}/>}
      <NavBar activeTab={activeTab} setActiveTab={setActiveTab} score={totalScore} showScore={showScore} soundOn={soundOn} onSoundToggle={handleSoundToggle}/>
      {renderContent()}
      {newBadgeQueue.length > 0 && (
        <BadgeNotification
          key={newBadgeQueue[0].id}
          badge={newBadgeQueue[0]}
          onClose={()=>setNewBadgeQueue(q=>q.slice(1))}
        />
      )}
    </div>
  );
}

/* ======== LOCK SCREEN ======== */
function LockScreen({onUnlock}) {
  const [pw, setPw] = React.useState('');
  const [err, setErr] = React.useState(false);
  const [shake, setShake] = React.useState(false);
  const [show, setShow] = React.useState(false);

  function attempt() {
    if(pw === DEMO_PASSWORD) {
      try { localStorage.setItem('mm_demo_unlocked','1'); } catch(e){}
      onUnlock();
    } else {
      setErr(true);
      setShake(true);
      setTimeout(()=>setShake(false), 600);
      setTimeout(()=>setErr(false), 2500);
    }
  }

  return (
    <div style={{
      position:'fixed',inset:0,background:'#0a0b10',display:'flex',
      alignItems:'center',justifyContent:'center',zIndex:99999,
      fontFamily:"'Inter',sans-serif"
    }}>
      <div style={{
        background:'#12141c',border:'1px solid rgba(38,166,154,0.2)',
        borderRadius:20,padding:'48px 40px',width:'100%',maxWidth:420,
        textAlign:'center',boxShadow:'0 24px 80px rgba(0,0,0,0.6)',
        animation:shake?'ls-shake 0.6s ease':'none'
      }}>
        <style>{`
          @keyframes ls-shake {
            0%,100%{transform:translateX(0)}
            15%{transform:translateX(-8px)}
            30%{transform:translateX(8px)}
            45%{transform:translateX(-6px)}
            60%{transform:translateX(6px)}
            75%{transform:translateX(-3px)}
            90%{transform:translateX(3px)}
          }
          .ls-input:focus{outline:none;border-color:rgba(38,166,154,0.7)!important;box-shadow:0 0 0 3px rgba(38,166,154,0.12)!important}
          .ls-btn:hover{background:linear-gradient(135deg,#2dd4bf,#26a69a)!important;transform:translateY(-1px);box-shadow:0 8px 24px rgba(38,166,154,0.35)!important}
          .ls-btn:active{transform:translateY(0)!important}
        `}</style>

        {/* Lock icon */}
        <div style={{
          width:64,height:64,borderRadius:16,
          background:'rgba(38,166,154,0.12)',border:'1px solid rgba(38,166,154,0.25)',
          display:'flex',alignItems:'center',justifyContent:'center',
          fontSize:28,margin:'0 auto 24px',
        }}>🔒</div>

        <h2 style={{color:'#fff',fontSize:22,fontWeight:800,marginBottom:6,letterSpacing:'-0.03em'}}>
          Market<span style={{color:'#26a69a'}}> Mastery</span>
        </h2>
        <p style={{color:'#6b7280',fontSize:13,marginBottom:32,lineHeight:1.5}}>
          This is a private demo.<br/>Enter the access password to continue.
        </p>

        {/* Password field */}
        <div style={{position:'relative',marginBottom:16}}>
          <input
            className="ls-input"
            type={show?'text':'password'}
            placeholder="Enter password"
            value={pw}
            onChange={e=>{setPw(e.target.value);setErr(false);}}
            onKeyDown={e=>e.key==='Enter'&&attempt()}
            style={{
              width:'100%',padding:'14px 48px 14px 16px',
              background:'#1a1d28',border:`1.5px solid ${err?'#ef4444':'rgba(255,255,255,0.1)'}`,
              borderRadius:12,color:'#fff',fontSize:15,
              transition:'all 0.2s',letterSpacing:show?'normal':'0.12em'
            }}
          />
          <button
            onClick={()=>setShow(s=>!s)}
            style={{
              position:'absolute',right:14,top:'50%',transform:'translateY(-50%)',
              background:'none',border:'none',color:'#6b7280',cursor:'pointer',
              fontSize:16,padding:0,lineHeight:1
            }}
          >{show?'🙈':'👁'}</button>
        </div>

        {err && (
          <p style={{color:'#ef4444',fontSize:13,marginBottom:12,textAlign:'left'}}>
            ✗ Incorrect password. Try again.
          </p>
        )}

        <button
          className="ls-btn"
          onClick={attempt}
          style={{
            width:'100%',padding:'14px',
            background:'linear-gradient(135deg,#26a69a,#1e8a7f)',
            border:'none',borderRadius:12,color:'#fff',
            fontSize:15,fontWeight:700,cursor:'pointer',
            transition:'all 0.2s',boxShadow:'0 4px 16px rgba(38,166,154,0.25)',
            letterSpacing:'0.01em'
          }}
        >
          Enter Demo →
        </button>

        <p style={{color:'#374151',fontSize:11,marginTop:24}}>
          Market Mastery · Private Preview
        </p>
      </div>
    </div>
  );
}

function App() {
  const [unlocked, setUnlocked] = React.useState(() => {
    try { return localStorage.getItem('mm_demo_unlocked') === '1'; } catch(e){return false;}
  });

  if(!unlocked) return <LockScreen onUnlock={()=>setUnlocked(true)}/>;

  return (
    <AuthProvider>
      <AppInner/>
    </AuthProvider>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App/>);
</script>
</body>
</html>'''

with open("index.html", "w") as f:
    f.write(html)

print(f"Built index.html: {len(html)/1024:.1f} KB")
