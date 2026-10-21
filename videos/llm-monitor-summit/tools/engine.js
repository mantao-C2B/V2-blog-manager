/* LLM Monitor @ SEO & GEO Summit — edit engine.
   Reads window.EDL (written by tools/build.py) and builds ONE paused GSAP timeline:
   camera moves and transitions on the footage wrappers, motion-design overlays, captions.
   The <video>/<audio> elements themselves are static HTML (timed by data-* attributes).
   Deterministic: no clocks, no Math.random, no network. */
window.buildEdit = function (E) {
  const LM = window.LM;
  const C = LM.C;
  const W = E.W;
  const H = E.H;
  const WIDE = W > H;
  const M = WIDE ? 96 : 72; // safe margin
  const tl = gsap.timeline({ paused: true });
  const ov = document.getElementById("overlays");

  function el(tag, cls, parent, html) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    (parent || ov).appendChild(e);
    return e;
  }
  function box(cls, t0, t1, parent) {
    const b = el("div", "ov " + (cls || ""), parent);
    gsap.set(b, { autoAlpha: 0 });
    tl.set(b, { autoAlpha: 1 }, t0);
    tl.set(b, { autoAlpha: 0 }, t1);
    return b;
  }
  function out(targets, vars, at) {
    tl.to(targets, Object.assign({ immediateRender: false }, vars), at);
  }
  function words(text) {
    // "**mot**" marks a highlighted word
    return text.split(/\s+/).filter(Boolean).map(function (w) {
      const hl = /^\*\*.*\*\*$/.test(w);
      return '<span class="w' + (hl ? " hl" : "") + '">' + w.replace(/\*\*/g, "") + "</span>";
    }).join(" ");
  }

  /* ------------------------------------------------------------------ footage */
  E.shots.forEach(function (s) {
    const wrap = document.getElementById("w-" + s.id);
    const inner = document.getElementById("i-" + s.id);
    if (!wrap) return;
    const fx = s.focal[0] + "%";
    const fy = s.focal[1] + "%";
    const z = s.zoom || 1;
    gsap.set(wrap, { transformOrigin: fx + " " + fy, scale: z });
    gsap.set(inner, { transformOrigin: "50% 50%" });
    const t0 = s.start;
    const d = s.dur;
    // camera move over the whole shot
    const mv = s.move || "none";
    if (mv === "push") tl.fromTo(wrap, { scale: z }, { scale: z * 1.07, duration: d, ease: "none" }, t0);
    else if (mv === "pull") tl.fromTo(wrap, { scale: z * 1.08 }, { scale: z, duration: d, ease: "none" }, t0);
    else if (mv === "pan-l") tl.fromTo(wrap, { scale: z * 1.08, xPercent: 2.5 }, { scale: z * 1.08, xPercent: -2.5, duration: d, ease: "none" }, t0);
    else if (mv === "pan-r") tl.fromTo(wrap, { scale: z * 1.08, xPercent: -2.5 }, { scale: z * 1.08, xPercent: 2.5, duration: d, ease: "none" }, t0);
    // entry transition
    const tin = s.tin || "cut";
    if (tin === "punch") {
      tl.fromTo(inner, { scale: 1.16, filter: "blur(10px)" }, { scale: 1, filter: "blur(0px)", duration: 0.3, ease: "power3.out" }, t0);
    } else if (tin === "whip") {
      tl.fromTo(inner, { xPercent: 9, filter: "blur(18px)" }, { xPercent: 0, filter: "blur(0px)", duration: 0.22, ease: "power3.out" }, t0);
    } else if (tin === "zoom") {
      tl.fromTo(inner, { scale: 0.86, filter: "blur(8px)" }, { scale: 1, filter: "blur(0px)", duration: 0.34, ease: "expo.out" }, t0);
    } else if (tin === "slide") {
      tl.fromTo(inner, { yPercent: 6, scale: 1.04 }, { yPercent: 0, scale: 1, duration: 0.4, ease: "power3.out" }, t0);
    }
    // exit transition (shot is the outgoing side)
    const tout = s.tout || "cut";
    if (tout === "whip") {
      tl.fromTo(inner, { xPercent: 0, filter: "blur(0px)" }, { xPercent: -9, filter: "blur(18px)", duration: 0.16, ease: "power2.in", immediateRender: false }, t0 + d - 0.16);
    } else if (tout === "zoom") {
      tl.fromTo(inner, { scale: 1, filter: "blur(0px)" }, { scale: 1.22, filter: "blur(9px)", duration: 0.2, ease: "power2.in", immediateRender: false }, t0 + d - 0.2);
    }
  });

  /* flashes and dips between shots */
  const flash = el("div", "flash");
  gsap.set(flash, { autoAlpha: 0 });
  (E.flashes || []).forEach(function (t) {
    tl.fromTo(flash, { autoAlpha: 0 }, { autoAlpha: 0.9, duration: 0.06, ease: "none", immediateRender: false }, t - 0.06);
    tl.fromTo(flash, { autoAlpha: 0.9 }, { autoAlpha: 0, duration: 0.32, ease: "power2.out", immediateRender: false }, t);
  });
  const dip = el("div", "dip");
  gsap.set(dip, { autoAlpha: 0 });
  (E.dips || []).forEach(function (t) {
    tl.fromTo(dip, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.2, ease: "power2.in", immediateRender: false }, t - 0.2);
    tl.fromTo(dip, { autoAlpha: 1 }, { autoAlpha: 0, duration: 0.35, ease: "power2.out", immediateRender: false }, t);
  });

  /* ------------------------------------------------------------------ overlays */
  const BUILD = {};

  // Small brand bug, top corner.
  BUILD.bug = function (o) {
    const b = box("bug", o.start, o.start + o.dur);
    b.innerHTML = '<span class="bug-sym">' + LM.symbol({ color: C.mint, size: 46 }) + '</span><span class="bug-txt">' + o.text + "</span>";
    tl.fromTo(b, { opacity: 0, y: -12 }, { opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }, o.start);
    out(b, { opacity: 0, duration: 0.3 }, o.start + o.dur - 0.3);
  };

  // Kinetic hook / headline: lines of words that slam in on given times.
  BUILD.headline = function (o) {
    const b = box("headline " + (o.cls || ""), o.start, o.start + o.dur);
    if (o.shade !== false) el("div", "shade", b);
    const wrapEl = el("div", "hl-wrap " + (o.align || "center"), b);
    if (o.kicker) {
      const k = el("div", "hl-kicker", wrapEl, LM.symbol({ color: C.mint, size: 40 }) + "<span>" + o.kicker + "</span>");
      tl.fromTo(k, { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }, o.start + (o.kickerAt || 0));
    }
    (o.lines || []).forEach(function (ln, i) {
      const line = el("div", "hl-line " + (ln.style || "sora"), wrapEl, words(ln.text));
      const ws = line.querySelectorAll(".w");
      const at = o.start + (ln.at != null ? ln.at : i * 0.35);
      if (ln.fx === "slam") {
        tl.fromTo(ws, { opacity: 0, scale: 1.6, filter: "blur(14px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.32, ease: "expo.out", stagger: ln.stagger == null ? 0.09 : ln.stagger }, at);
      } else if (ln.fx === "rise") {
        tl.fromTo(ws, { opacity: 0, yPercent: 60 }, { opacity: 1, yPercent: 0, duration: 0.5, ease: "power4.out", stagger: ln.stagger == null ? 0.06 : ln.stagger }, at);
      } else {
        LM.focusIn(tl, ws, at, { stagger: ln.stagger == null ? 0.06 : ln.stagger, duration: 0.55, blur: 14, y: 22 });
      }
    });
    if (o.sub) {
      const s = el("div", "hl-sub", wrapEl, o.sub);
      tl.fromTo(s, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }, o.start + (o.subAt || 0.6));
    }
    out(wrapEl, { opacity: 0, scale: 1.04, filter: "blur(10px)", duration: 0.3, ease: "power2.in" }, o.start + o.dur - 0.3);
    if (o.shade !== false) out(b.querySelector(".shade"), { opacity: 0, duration: 0.3 }, o.start + o.dur - 0.3);
  };

  // Name / role lower third.
  BUILD.lower = function (o) {
    const b = box("lower " + (o.side || "left"), o.start, o.start + o.dur);
    const card = el("div", "lt-card", b);
    const sym = el("div", "lt-sym", card, LM.symbol({ color: C.mint, size: 64 }));
    const txt = el("div", "lt-txt", card);
    const name = el("div", "lt-name", txt, o.name);
    const role = el("div", "lt-role", txt, o.role);
    const bar = el("div", "lt-bar", card);
    tl.fromTo(card, { clipPath: "inset(0 100% 0 0 round 22px)" }, { clipPath: "inset(0 0% 0 0 round 22px)", duration: 0.6, ease: "power4.inOut" }, o.start);
    LM.symbolDraw(tl, sym.querySelector("svg"), o.start + 0.15, { duration: 0.7 });
    tl.fromTo(name, { opacity: 0, x: -20 }, { opacity: 1, x: 0, duration: 0.5, ease: "power3.out" }, o.start + 0.3);
    tl.fromTo(role, { opacity: 0, x: -20 }, { opacity: 1, x: 0, duration: 0.5, ease: "power3.out" }, o.start + 0.42);
    tl.fromTo(bar, { scaleX: 0 }, { scaleX: 1, duration: 0.7, ease: "power3.inOut", transformOrigin: "0% 50%" }, o.start + 0.35);
    out(card, { clipPath: "inset(0 0 0 100% round 22px)", duration: 0.45, ease: "power3.in" }, o.start + o.dur - 0.45);
  };

  // Location tag.
  BUILD.location = function (o) {
    const b = box("location", o.start, o.start + o.dur);
    const pin = el("div", "loc-pin", b, LM.icon("target", { stroke: C.navy900, strokeWidth: 2.4 }));
    const txt = el("div", "loc-txt", b);
    const p = el("div", "loc-place", txt, o.place);
    const d = el("div", "loc-detail", txt, o.detail);
    tl.fromTo(pin, { scale: 0, rotation: -90 }, { scale: 1, rotation: 0, duration: 0.55, ease: "back.out(2)" }, o.start);
    tl.fromTo(p, { opacity: 0, x: -24 }, { opacity: 1, x: 0, duration: 0.5, ease: "power3.out" }, o.start + 0.15);
    tl.fromTo(d, { opacity: 0, x: -24 }, { opacity: 1, x: 0, duration: 0.5, ease: "power3.out" }, o.start + 0.28);
    out([pin, txt], { opacity: 0, y: -10, duration: 0.35, ease: "power2.in" }, o.start + o.dur - 0.35);
  };

  // Chapter card: panel wipes in from the side, number + title, wipes out.
  BUILD.chapter = function (o) {
    const b = box("chapter", o.start, o.start + o.dur);
    const panel = el("div", "ch-panel", b);
    const line = el("div", "ch-line", panel);
    const num = el("div", "ch-num", panel, o.num);
    const title = el("div", "ch-title", panel, words(o.title));
    const kick = o.kicker ? el("div", "ch-kicker", panel, o.kicker) : null;
    tl.fromTo(panel, { clipPath: "inset(0 100% 0 0)" }, { clipPath: "inset(0 0% 0 0)", duration: 0.5, ease: "power4.inOut" }, o.start);
    tl.fromTo(line, { scaleY: 0 }, { scaleY: 1, transformOrigin: "50% 0%", duration: 0.5, ease: "power3.out" }, o.start + 0.2);
    tl.fromTo(num, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }, o.start + 0.25);
    LM.focusIn(tl, title.querySelectorAll(".w"), o.start + 0.32, { stagger: 0.07, duration: 0.55, blur: 12, y: 24 });
    if (kick) tl.fromTo(kick, { opacity: 0 }, { opacity: 1, duration: 0.4 }, o.start + 0.55);
    out(panel, { clipPath: "inset(0 0 0 100%)", duration: 0.45, ease: "power4.in" }, o.start + o.dur - 0.45);
  };

  // AI platform logos popping on the words that name them.
  BUILD.logos = function (o) {
    const b = box("logos " + (o.pos || "top"), o.start, o.start + o.dur);
    const row = el("div", "lg-row", b);
    o.items.forEach(function (it) {
      const chip = el("div", "lg-chip", row, '<span class="lg-ico">' + LM.logo(it.logo) + '</span><span class="lg-name">' + it.name + "</span>");
      tl.fromTo(chip, { opacity: 0, scale: 0.5, y: 24 }, { opacity: 1, scale: 1, y: 0, duration: 0.45, ease: "back.out(2.2)" }, it.t);
    });
    out(row.children, { opacity: 0, y: -16, duration: 0.3, stagger: 0.04, ease: "power2.in" }, o.start + o.dur - 0.42);
  };

  // Count-up card.
  BUILD.counter = function (o) {
    const b = box("counter " + (o.pos || "right"), o.start, o.start + o.dur);
    const card = el("div", "ct-card", b);
    const lab = el("div", "ct-label", card, o.kicker || "");
    const num = el("div", "ct-num", card, "0");
    const txt = el("div", "ct-txt", card, o.label);
    const fmt = function (v) {
      return (o.prefix || "") + Math.round(v).toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ") + (o.suffix || "");
    };
    tl.fromTo(card, { opacity: 0, y: 40, scale: 0.94 }, { opacity: 1, y: 0, scale: 1, duration: 0.55, ease: "power3.out" }, o.start);
    tl.fromTo(lab, { opacity: 0 }, { opacity: 1, duration: 0.4 }, o.start + 0.2);
    LM.countUp(tl, num, 0, o.value, o.start + 0.2, o.countDur || 1.4, fmt, "power3.out");
    tl.fromTo(txt, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }, o.start + 0.5);
    out(card, { opacity: 0, y: 24, duration: 0.35, ease: "power2.in" }, o.start + o.dur - 0.35);
  };

  // Big stat card (product world: white card, green figure).
  BUILD.stat = function (o) {
    const b = box("stat " + (o.pos || "right"), o.start, o.start + o.dur);
    if (o.shade) el("div", "shade side", b);
    const card = el("div", "st-card", b);
    const lab = el("div", "st-label", card, '<span class="dot"></span>' + o.kicker);
    const num = el("div", "st-num", card, "0");
    const txt = el("div", "st-txt", card, o.text);
    const rule = el("div", "st-rule", card);
    const foot = el("div", "st-foot", card, o.foot || "");
    tl.fromTo(card, { opacity: 0, x: o.pos === "left" ? -60 : 60 }, { opacity: 1, x: 0, duration: 0.6, ease: "power4.out" }, o.start);
    tl.fromTo(lab, { opacity: 0 }, { opacity: 1, duration: 0.4 }, o.start + 0.25);
    LM.countUp(tl, num, 0, o.value, o.start + 0.3, 1.1, function (v) { return Math.round(v) + " %"; }, "power3.out");
    tl.fromTo(txt, { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }, o.start + 0.7);
    tl.fromTo(rule, { scaleX: 0 }, { scaleX: 1, transformOrigin: "0% 50%", duration: 0.5, ease: "power3.inOut" }, o.start + 1.1);
    tl.fromTo(foot, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }, o.start + (o.footAt || 1.4));
    out(card, { opacity: 0, x: o.pos === "left" ? -40 : 40, duration: 0.4, ease: "power3.in" }, o.start + o.dur - 0.4);
    if (o.shade) out(b.querySelector(".shade"), { opacity: 0, duration: 0.4 }, o.start + o.dur - 0.4);
  };

  // Chips list ("À faire").
  BUILD.chips = function (o) {
    const b = box("chips " + (o.pos || "center"), o.start, o.start + o.dur);
    el("div", "shade", b);
    const card = el("div", "cp-card", b);
    const lab = el("div", "cp-label", card, o.kicker);
    const title = el("div", "cp-title", card, words(o.title));
    const row = el("div", "cp-row", card);
    o.items.forEach(function (it, i) {
      const c = el("div", "cp-chip", row, LM.icon(it.icon, { stroke: C.mint, strokeWidth: 2.2 }) + "<span>" + it.text + "</span>");
      tl.fromTo(c, { opacity: 0, scale: 0.6, y: 20 }, { opacity: 1, scale: 1, y: 0, duration: 0.45, ease: "back.out(2)" }, o.start + (o.itemsAt || 0.9) + i * (o.itemStagger || 0.22));
    });
    tl.fromTo(card, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.55, ease: "power3.out" }, o.start);
    tl.fromTo(lab, { opacity: 0 }, { opacity: 1, duration: 0.4 }, o.start + 0.2);
    LM.focusIn(tl, title.querySelectorAll(".w"), o.start + 0.25, { stagger: 0.05, duration: 0.5, blur: 10, y: 16 });
    out([card, b.querySelector(".shade")], { opacity: 0, duration: 0.35, ease: "power2.in" }, o.start + o.dur - 0.35);
  };

  // Pull quote.
  BUILD.quote = function (o) {
    const b = box("quote " + (o.pos || "center"), o.start, o.start + o.dur);
    el("div", "shade", b);
    const q = el("div", "qt-wrap", b);
    const mark = el("div", "qt-mark", q, "«");
    const txt = el("div", "qt-txt", q, words(o.text));
    const by = el("div", "qt-by", q, o.by || "");
    tl.fromTo(mark, { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1, duration: 0.5, ease: "back.out(2)" }, o.start);
    LM.focusIn(tl, txt.querySelectorAll(".w"), o.start + 0.15, { stagger: o.stagger || 0.06, duration: 0.55, blur: 12, y: 18 });
    tl.fromTo(by, { opacity: 0 }, { opacity: 1, duration: 0.4 }, o.start + (o.byAt || 0.9));
    out([q, b.querySelector(".shade")], { opacity: 0, duration: 0.35, ease: "power2.in" }, o.start + o.dur - 0.35);
  };

  // Talk title card (the conference slide, restyled).
  BUILD.talk = function (o) {
    const b = box("talk " + (o.pos || "left"), o.start, o.start + o.dur);
    el("div", "shade side", b);
    const card = el("div", "tk-card", b);
    const lab = el("div", "tk-label", card, o.kicker);
    const title = el("div", "tk-title", card, words(o.title));
    const sub = el("div", "tk-sub", card, o.sub || "");
    const by = el("div", "tk-by", card, o.by || "");
    tl.fromTo(card, { clipPath: "inset(0 100% 0 0 round 28px)" }, { clipPath: "inset(0 0% 0 0 round 28px)", duration: 0.6, ease: "power4.inOut" }, o.start);
    tl.fromTo(lab, { opacity: 0 }, { opacity: 1, duration: 0.4 }, o.start + 0.3);
    LM.focusIn(tl, title.querySelectorAll(".w"), o.start + 0.35, { stagger: 0.06, duration: 0.55, blur: 12, y: 20 });
    tl.fromTo(sub, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.5 }, o.start + 0.9);
    tl.fromTo(by, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.5 }, o.start + 1.15);
    out([card, b.querySelector(".shade")], { opacity: 0, duration: 0.4, ease: "power2.in" }, o.start + o.dur - 0.4);
  };

  // Full-frame end card.
  BUILD.end = function (o) {
    const b = box("end", o.start, o.start + o.dur);
    const bg = el("div", "end-bg", b);
    const glow = el("div", "end-glow", b);
    const center = el("div", "end-center", b);
    const sym = el("div", "end-sym", center, LM.symbol({ color: C.mint, size: WIDE ? 190 : 210 }));
    const name = el("div", "end-name", center, "LLM Monitor");
    const tag = el("div", "end-tag", center, words(o.tagline));
    const cta = el("div", "end-cta", center, '<span class="cta-dot"></span>' + o.cta);
    const url = el("div", "end-url", center, o.url);
    tl.fromTo(bg, { opacity: 0 }, { opacity: 1, duration: 0.45, ease: "power2.out" }, o.start);
    tl.fromTo(glow, { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: 1.4, ease: "power2.out" }, o.start);
    tl.fromTo(glow, { scale: 1 }, { scale: 1.12, duration: o.dur - 1.4, ease: "sine.inOut", immediateRender: false }, o.start + 1.4);
    LM.symbolDraw(tl, sym.querySelector("svg"), o.start + 0.2, { duration: 0.95 });
    LM.symbolQuarter(tl, sym.querySelector("svg"), o.start + 1.3, 1);
    LM.symbolPulse(tl, sym.querySelector("svg"), o.start + 2.1, Math.max(1, Math.floor((o.dur - 2.4) / 1.3)), 1.3);
    tl.fromTo(name, { opacity: 0, y: 24, letterSpacing: "0.04em" }, { opacity: 1, y: 0, letterSpacing: "-0.035em", duration: 0.8, ease: "power3.out" }, o.start + 0.75);
    LM.focusIn(tl, tag.querySelectorAll(".w"), o.start + 1.25, { stagger: 0.07, duration: 0.6, blur: 12, y: 16 });
    tl.fromTo(cta, { opacity: 0, y: 16, scale: 0.94 }, { opacity: 1, y: 0, scale: 1, duration: 0.5, ease: "back.out(1.8)" }, o.start + 1.9);
    tl.fromTo(url, { opacity: 0 }, { opacity: 1, duration: 0.5 }, o.start + 2.2);
  };

  // Logo sting (short, over footage).
  BUILD.sting = function (o) {
    const b = box("sting", o.start, o.start + o.dur);
    el("div", "shade", b);
    const c = el("div", "sting-center", b);
    const sym = el("div", "sting-sym", c, LM.symbol({ color: C.mint, size: 150 }));
    const name = el("div", "sting-name", c, "LLM Monitor");
    const sub = o.sub ? el("div", "sting-sub", c, o.sub) : null;
    LM.symbolDraw(tl, sym.querySelector("svg"), o.start, { duration: 0.7 });
    tl.fromTo(name, { opacity: 0, x: -30 }, { opacity: 1, x: 0, duration: 0.55, ease: "power3.out" }, o.start + 0.35);
    if (sub) tl.fromTo(sub, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.45 }, o.start + 0.6);
    out([c, b.querySelector(".shade")], { opacity: 0, scale: 1.05, duration: 0.3, ease: "power2.in" }, o.start + o.dur - 0.3);
  };

  // Keyword pop (side callout synced to speech).
  BUILD.callout = function (o) {
    const b = box("callout " + (o.pos || "right"), o.start, o.start + o.dur);
    const card = el("div", "co-card", b);
    const ico = el("div", "co-ico", card, LM.icon(o.icon || "sparkles", { stroke: C.navy900, strokeWidth: 2.2 }));
    const txt = el("div", "co-txt", card, o.text);
    tl.fromTo(card, { opacity: 0, x: o.pos === "left" ? -40 : 40, scale: 0.9 }, { opacity: 1, x: 0, scale: 1, duration: 0.45, ease: "back.out(1.6)" }, o.start);
    tl.fromTo(ico, { rotation: -120, scale: 0 }, { rotation: 0, scale: 1, duration: 0.5, ease: "back.out(2)" }, o.start + 0.1);
    out(card, { opacity: 0, x: o.pos === "left" ? -30 : 30, duration: 0.3, ease: "power2.in" }, o.start + o.dur - 0.3);
  };

  (E.overlays || []).forEach(function (o) {
    if (BUILD[o.type]) BUILD[o.type](o);
  });

  /* ------------------------------------------------------------------ captions */
  const capLayer = document.getElementById("captions");
  (E.captions || []).forEach(function (g, gi) {
    const grp = el("div", "cap", capLayer);
    const inner = el("span", "cap-in", grp);
    gsap.set(grp, { autoAlpha: 0 });
    const spans = g.words.map(function (w, i) {
      const s = el("span", "cw" + (w.hl ? " hl" : ""), inner, w.w);
      if (i < g.words.length - 1) inner.appendChild(document.createTextNode(" "));
      return s;
    });
    tl.set(grp, { autoAlpha: 1 }, g.start);
    tl.fromTo(grp, { y: 14, scale: 0.97 }, { y: 0, scale: 1, duration: 0.16, ease: "power2.out" }, g.start);
    g.words.forEach(function (w, i) {
      tl.fromTo(spans[i], { opacity: 0.55 }, { opacity: 1, duration: 0.08, ease: "none" }, w.t);
      tl.fromTo(spans[i], { scale: 1 }, { scale: 1.08, duration: 0.08, ease: "power2.out", immediateRender: false }, w.t);
      tl.to(spans[i], { scale: 1, duration: 0.12, ease: "power2.out" }, w.t + 0.1);
    });
    tl.set(grp, { autoAlpha: 0 }, g.end);
  });

  tl.set({}, {}, E.duration);
  return tl;
};
