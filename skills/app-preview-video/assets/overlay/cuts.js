// Layouts driven by plan.json. Two cuts share one timeline:
//   store   — full-bleed app footage, dissolves, one caption per scene,
//             an end card with the purchase disclosure. App Store / Google Play.
//   landing — device mockup, kinetic headline, callout chips, CTA end card.
// Each scene's screen comes from a <video> clip (real capture) or a mock
// function in window.SCREENS. The page exposes window.seek(frame).
(function () {
  const {interpolate, pop, ease, div, esc, Easing, css} = window.R;
  const PLAN = window.PLAN;
  const CUT = window.CUT; // {id, layout, w, h}
  const FPS = PLAN.fps || 30;
  const XF = PLAN.crossfade || 10;
  const FONT = PLAN.font || '-apple-system, "SF Pro Display", "SF Pro Text", system-ui, "Helvetica Neue", sans-serif';
  const B = Object.assign({primary: '#5B5BF7', primary2: '#9B6BFF', ink: '#11142A', bg: '#F4F5FB'}, PLAN.brand || {});

  // Scenes with absolute start frames; the end card is the last scene.
  const SCENES = [];
  let at = 0;
  for (const s of PLAN.scenes) { SCENES.push(Object.assign({from: at}, s)); at += s.dur; }
  const END = Object.assign({id: 'end', from: at, dur: 90}, PLAN.end || {});
  const TOTAL = END.from + END.dur;
  window.TOTAL = TOTAL;

  // Screen canvas: store cut is the canvas itself; landing shows a phone.
  const SW = PLAN.screen?.w || 886, SH = PLAN.screen?.h || 1920;
  const isLanding = CUT.layout === 'landing';
  const screenW = isLanding ? SW : CUT.w, screenH = isLanding ? SH : CUT.h;
  const S = isLanding ? (PLAN.landing?.phoneScale || 0.43) : 1;

  // ---------------------------------------------------------------- static DOM
  const root = document.getElementById('root');
  root.style.cssText = css({position: 'relative', width: CUT.w, height: CUT.h, overflow: 'hidden', fontFamily: FONT, background: B.bg});
  const bg = document.createElement('div'); bg.id = 'bg'; root.appendChild(bg);
  const phone = document.createElement('div'); phone.id = 'phone'; root.appendChild(phone);
  const bezel = document.createElement('div'); phone.appendChild(bezel);
  const screen = document.createElement('div'); screen.id = 'screen'; bezel.appendChild(screen);
  const glass = document.createElement('div'); bezel.appendChild(glass);
  const overlay = document.createElement('div'); overlay.id = 'overlay'; root.appendChild(overlay);
  overlay.style.cssText = css({position: 'absolute', inset: 0});
  screen.style.cssText = css({position: 'absolute', left: 0, top: 0, width: SW * S, height: SH * S, overflow: 'hidden', background: B.bg});

  const layers = SCENES.map((s) => {
    const el = document.createElement('div');
    el.style.cssText = css({position: 'absolute', left: 0, top: 0, width: screenW * S, height: screenH * S, display: 'none'});
    let video = null, mock = null;
    if (s.clip) {
      video = document.createElement('video');
      video.src = s.clip.src; video.muted = true; video.preload = 'auto';
      video.style.cssText = css({width: screenW * S, height: screenH * S, objectFit: 'cover', display: 'block'});
      el.appendChild(video);
    } else {
      mock = document.createElement('div');
      mock.style.cssText = css({width: SW, height: SH, transform: `scale(${(screenW * S) / SW})`, transformOrigin: '0 0'});
      el.appendChild(mock);
    }
    screen.appendChild(el);
    return {scene: s, el, video, mock};
  });

  window.ready = Promise.all(layers.filter((l) => l.video).map((l) => new Promise((res, rej) => {
    l.video.addEventListener('loadeddata', res, {once: true});
    l.video.addEventListener('error', () => rej(new Error('cannot load ' + l.scene.clip.src)), {once: true});
    l.video.load();
  })));

  const seekVideo = (v, t) => new Promise((res) => {
    if (Math.abs(v.currentTime - t) < 1 / (FPS * 4)) return res();
    v.addEventListener('seeked', () => res(), {once: true});
    v.currentTime = t;
  });

  // ---------------------------------------------------------------- store pieces
  const K = screenW / 430;
  const p = (pt) => pt * K;

  function caption(text, local, dur, y) {
    const inn = pop(local, 6, {damping: 16, stiffness: 160});
    const out = interpolate(local, [dur - 4, dur + XF - 2], [1, 0]);
    return div({position: 'absolute', left: 0, width: screenW, top: y != null ? y * screenH : screenH - p(83) - p(124), display: 'flex', justifyContent: 'center', zIndex: 80, opacity: Math.min(inn, out)},
      div({padding: `${p(14)}px ${p(24)}px`, borderRadius: p(22), background: PLAN.caption?.background || 'rgba(17,20,42,0.92)', color: PLAN.caption?.color || '#fff', fontSize: p(25), fontWeight: 800, letterSpacing: '-0.4px', boxShadow: '0 12px 36px rgba(17,20,42,0.35)', transform: `translateY(${(1 - inn) * p(30)}px) scale(${0.92 + 0.08 * inn})`, maxWidth: screenW - p(48), textAlign: 'center', whiteSpace: 'nowrap'}, esc(text)));
  }

  function endCard(f, w, h, variant) {
    const u = Math.min(w, h);
    const icon = pop(f, 0, {damping: 10, stiffness: 160});
    const name = pop(f, 6), tag = pop(f, 12), foot = ease(f, 22, 36);
    const rings = [0, 1, 2, 3].map((i) => {
      const t = (f - i * 9) / 60;
      if (t < 0) return '';
      const s = interpolate(t, [0, 1], [0.2, 2.6]);
      return div({position: 'absolute', left: w / 2 - u * 0.3, top: h * 0.42 - u * 0.3, width: u * 0.6, height: u * 0.6, borderRadius: u, border: `${u * 0.006}px solid rgba(255,255,255,${0.35 * (1 - Math.min(1, t))})`, transform: `scale(${s})`});
    });
    const iconHtml = PLAN.app.icon
      ? `<img src="${esc(PLAN.app.icon)}" style="width:${u * 0.3}px;height:${u * 0.3}px;border-radius:${u * 0.3 * 0.225}px;box-shadow:0 ${u * 0.024}px ${u * 0.075}px rgba(0,0,0,0.35)">`
      : window.APP_ICON ? window.APP_ICON(u * 0.3, f) : '';
    const footer = variant === 'landing'
      ? div({display: 'flex', gap: u * 0.025, justifyContent: 'center', marginTop: u * 0.05, opacity: foot, transform: `translateY(${(1 - foot) * u * 0.03}px)`},
          (END.stores || ['App Store', 'Google Play']).map((s) => div({padding: `${u * 0.018}px ${u * 0.04}px`, borderRadius: u * 0.03, background: '#fff', color: B.ink, fontSize: u * 0.03, fontWeight: 700}, esc('Get it on ' + s))))
      : div({fontSize: u * 0.03, opacity: foot * 0.75, marginTop: u * 0.06}, esc(END.disclosure || ''));
    return div({position: 'absolute', inset: 0, background: `radial-gradient(120% 80% at 50% 35%, ${B.primary2} 0%, ${B.primary} 45%, ${B.primary3 || '#2A1F8F'} 100%)`, color: '#fff', overflow: 'hidden'}, [
      ...rings,
      div({position: 'absolute', left: w / 2 - u * 0.15, top: h * 0.42 - u * 0.15, transform: `scale(${icon}) rotate(${(1 - icon) * -25}deg)`}, iconHtml),
      div({position: 'absolute', top: h * 0.42 + u * 0.2, width: '100%', textAlign: 'center'}, [
        div({fontSize: u * 0.11, fontWeight: 800, letterSpacing: `${-u * 0.003}px`, opacity: name, transform: `translateY(${(1 - name) * u * 0.04}px)`}, esc(PLAN.app.name)),
        div({fontSize: u * 0.045, fontWeight: 500, opacity: tag * 0.9, marginTop: u * 0.012, transform: `translateY(${(1 - tag) * u * 0.03}px)`}, esc(PLAN.app.tagline || '')),
        footer,
      ]),
    ]);
  }

  // ---------------------------------------------------------------- landing pieces
  const L = {w: CUT.w, h: CUT.h};
  const lx = (v) => (v / 1920) * L.w, ly = (v) => (v / 1080) * L.h, lu = (v) => (v / 1080) * Math.min(L.h, L.w * 9 / 16);

  function background(f) {
    const blobs = [{c: B.primary, x: 1350, y: 300, r: 620, sp: 90}, {c: B.primary2, x: 1650, y: 900, r: 520, sp: 70}, {c: B.accent || '#1FC79A', x: 200, y: 950, r: 420, sp: 110}]
      .map((b, i) => div({position: 'absolute', left: lx(b.x - b.r + Math.sin(f / b.sp + i) * 60), top: ly(b.y - b.r + Math.cos(f / b.sp + i * 2) * 50), width: lx(b.r * 2), height: lx(b.r * 2), borderRadius: lx(b.r), background: `radial-gradient(circle, ${b.c}55 0%, ${b.c}00 70%)`}));
    return div({position: 'absolute', inset: 0, background: PLAN.landing?.background || 'linear-gradient(135deg, #0D0F2B 0%, #17123F 55%, #0F1A3A 100%)', overflow: 'hidden'}, [
      ...blobs,
      div({position: 'absolute', inset: 0, backgroundImage: 'radial-gradient(rgba(255,255,255,0.07) 1.5px, transparent 1.5px)', backgroundSize: `${lx(38)}px ${lx(38)}px`}),
    ]);
  }

  function headline(s, local) {
    const out = interpolate(local, [s.dur - 2, s.dur + XF - 2], [0, 1], Easing.inCubic);
    let word = 0;
    const lines = (s.headline || [s.caption]).map((line, li) => div({fontSize: lu(104), fontWeight: 800, letterSpacing: `${-lu(3)}px`, lineHeight: 1.04, whiteSpace: 'nowrap'},
      line.split(' ').map((wd) => {
        const k = pop(local, 4 + word++ * 3, {damping: 15, stiffness: 140});
        return `<span style="${css({display: 'inline-block', marginRight: lu(26), opacity: k * (1 - out), filter: `blur(${(1 - k) * 12 + out * 10}px)`, transform: `translateY(${(1 - k) * lu(50) - out * lu(40)}px)`, color: li === 1 ? (B.headline2 || '#C9C3FF') : '#fff'})}">${esc(wd)}</span>`;
      })));
    const sub = pop(local, 16);
    return div({position: 'absolute', left: lx(150), top: ly(300), width: lx(820), color: '#fff'}, [
      ...lines,
      s.sub ? div({marginTop: lu(34), fontSize: lu(36), lineHeight: 1.35, color: 'rgba(255,255,255,0.72)', width: lx(720), opacity: sub * (1 - out), transform: `translateY(${(1 - sub) * lu(24)}px)`}, esc(s.sub)) : '',
    ]);
  }

  function chip(s, local) {
    if (!s.chip) return '';
    const k = pop(local, s.chip.at, {damping: 10, stiffness: 180});
    const out = interpolate(local, [s.dur - 2, s.dur + XF - 2], [1, 0]);
    return div({position: 'absolute', left: lx(1020), top: ly(720) + Math.sin(local / 12) * 6, padding: `${lu(22)}px ${lu(34)}px`, borderRadius: lu(28), background: 'rgba(255,255,255,0.96)', color: B.ink, fontSize: lu(38), fontWeight: 800, boxShadow: '0 24px 60px rgba(0,0,0,0.35)', transform: `scale(${k}) rotate(${(1 - k) * -12 - 3}deg)`, opacity: Math.min(1, k * 2) * out, zIndex: 20}, esc(s.chip.text));
  }

  function phoneStyle(f) {
    const enter = pop(f, 0, {damping: 18, stiffness: 90});
    const cut = SCENES.slice(1).reduce((a, s) => a + Math.sin(Math.min(1, Math.max(0, (f - s.from) / 24)) * Math.PI) * 5, 0);
    const ry = -16 + Math.sin(f / 50) * 3 + cut;
    const exit = interpolate(f, [END.from - 8, END.from + 8], [0, 1], Easing.inCubic);
    const bz = lu(16), w = SW * S, h = SH * S;
    phone.style.cssText = css({position: 'absolute', left: lx(PLAN.landing?.phoneX || 1180), top: L.h / 2 - h / 2 - bz + Math.sin(f / 28) * 8 + (1 - enter) * 300 + exit * 200, perspective: 2200, opacity: Math.min(1, enter * 1.5) * (1 - exit)});
    bezel.style.cssText = css({width: w + bz * 2, height: h + bz * 2, borderRadius: lu(78), background: 'linear-gradient(145deg,#3A3D55,#14162A)', padding: bz, boxSizing: 'border-box', transform: `rotateY(${ry}deg) rotateX(5deg)`, boxShadow: '40px 60px 120px rgba(0,0,0,0.55), inset 0 0 0 2px rgba(255,255,255,0.12)', position: 'relative'});
    screen.style.cssText = css({position: 'absolute', left: bz, top: bz, width: w, height: h, borderRadius: lu(64), overflow: 'hidden', background: B.bg});
    glass.innerHTML = div({position: 'absolute', left: w / 2 - lu(55), top: lu(14), width: lu(110), height: lu(32), borderRadius: lu(20), background: '#000', zIndex: 90}) +
      div({position: 'absolute', inset: 0, borderRadius: lu(64), background: 'linear-gradient(115deg, rgba(255,255,255,0.18) 0%, rgba(255,255,255,0) 35%)', zIndex: 91});
    glass.style.cssText = css({position: 'absolute', left: bz, top: bz, width: w, height: h, pointerEvents: 'none'});
  }

  // ---------------------------------------------------------------- seek
  window.seek = async function seek(f) {
    f = Math.max(0, Math.min(TOTAL - 1, Math.round(f)));
    const waits = [];
    let html = '';
    for (const l of layers) {
      const s = l.scene;
      const local = f - s.from;
      const visible = local >= 0 && local < s.dur + XF;
      l.el.style.display = visible ? 'block' : 'none';
      if (!visible) continue;
      l.el.style.opacity = s.from === 0 ? 1 : interpolate(local, [0, XF], [0, 1]);
      if (l.video) waits.push(seekVideo(l.video, (s.clip.in || 0) + Math.min(local, s.dur + XF - 1) / FPS));
      else {
        const fn = window.SCREENS && window.SCREENS[s.id];
        l.mock.innerHTML = fn ? fn(local, SW, SH) : div({width: SW, height: SH, background: '#999', color: '#fff', fontSize: 60, padding: 60}, 'Missing screen: ' + esc(s.id));
      }
      if (isLanding) html += headline(s, local) + chip(s, local);
      else if (s.caption) html += div({position: 'absolute', inset: 0, opacity: l.el.style.opacity}, caption(s.caption, local, s.dur, s.captionY));
    }
    const endLocal = f - END.from;
    if (endLocal >= 0) {
      const op = interpolate(endLocal, [0, isLanding ? 8 : XF], [0, 1]);
      html += div({position: 'absolute', inset: 0, opacity: op, zIndex: 100}, endCard(endLocal, CUT.w, CUT.h, isLanding ? 'landing' : 'store'));
    }
    if (isLanding) {
      bg.innerHTML = background(f);
      phoneStyle(f);
      html = div({position: 'absolute', left: lx(150), top: ly(200), padding: `${lu(10)}px ${lu(20)}px`, borderRadius: lu(30), border: '2px solid rgba(255,255,255,0.18)', color: 'rgba(255,255,255,0.8)', fontSize: lu(24), fontWeight: 700, letterSpacing: `${lu(3)}px`, opacity: interpolate(f, [0, 12, END.from - 10, END.from + 2], [0, 1, 1, 0])}, esc((PLAN.app.name + (PLAN.app.category ? ' · ' + PLAN.app.category : '')).toUpperCase())) + html;
    }
    overlay.innerHTML = html;
    await Promise.all(waits);
    document.title = `${CUT.id} f${f}`;
    return f;
  };

  // Scrubber for manual preview in a normal browser (not used during capture).
  if (!location.search.includes('capture')) {
    const bar = document.createElement('div');
    bar.style.cssText = 'position:fixed;left:0;right:0;bottom:0;padding:10px;background:#000c;color:#fff;font:14px system-ui;display:flex;gap:10px;align-items:center;z-index:9999';
    bar.innerHTML = `<button id="play">Play</button><input id="scrub" type="range" min="0" max="${TOTAL - 1}" value="0" style="flex:1"><span id="fr">0</span>`;
    document.body.appendChild(bar);
    const scrub = bar.querySelector('#scrub'), fr = bar.querySelector('#fr');
    scrub.oninput = () => { window.seek(+scrub.value); fr.textContent = scrub.value; };
    let playing = false, t0 = 0, f0 = 0;
    const tick = () => { if (!playing) return; const f = (f0 + ((performance.now() - t0) / 1000) * FPS) % TOTAL; scrub.value = f; fr.textContent = Math.round(f); window.seek(f).then(() => requestAnimationFrame(tick)); };
    bar.querySelector('#play').onclick = (e) => { playing = !playing; e.target.textContent = playing ? 'Pause' : 'Play'; if (playing) { t0 = performance.now(); f0 = +scrub.value; tick(); } };
    window.ready.then(() => window.seek(0));
  }
})();
