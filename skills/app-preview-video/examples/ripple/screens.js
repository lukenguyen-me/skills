// Mock screens for the "Ripple" demo app. Each screen is a function
// (f, w, h) -> HTML string, laid out in iOS points and scaled to the canvas.
// Real projects replace these with screen recordings (plan.scenes[].clip);
// keep mocks only for storyboards and landing-page cuts.
(function () {
  const {interpolate, pop, ease, random, div, Easing} = window.R;
  const C = {primary: '#5B5BF7', primary2: '#9B6BFF', mint: '#1FC79A', flame: '#FF7A45', ink: '#11142A', sub: '#6B7090', bg: '#F4F5FB', card: '#FFFFFF', line: '#E3E5F0'};
  const K = 886 / 430;
  const p = (pt) => pt * K;
  const abs = (x, y, extra) => Object.assign({position: 'absolute', left: x, top: y}, extra);

  // ---------------------------------------------------------------- UI kit
  const statusBar = (w, dark) => {
    const col = dark ? '#fff' : C.ink;
    const bars = [5, 7, 9.5, 12].map((hh) => div({width: p(3), height: p(hh), borderRadius: p(1), background: col})).join('');
    return div({position: 'absolute', top: 0, left: 0, width: w, height: p(54), display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: `${p(4)}px ${p(34)}px 0`, boxSizing: 'border-box', color: col, zIndex: 50}, [
      div({fontSize: p(17), fontWeight: 600, letterSpacing: '-0.3px'}, '9:41'),
      div({display: 'flex', gap: p(6), alignItems: 'center'}, [
        div({display: 'flex', gap: p(2), alignItems: 'flex-end', height: p(12)}, bars),
        `<svg width="${p(17)}" height="${p(12)}" viewBox="0 0 17 12"><path d="M8.5 11.5 L5.6 8.3 A4.2 4.2 0 0 1 11.4 8.3 Z" fill="${col}"/><path d="M3.4 6.1 A7.3 7.3 0 0 1 13.6 6.1" stroke="${col}" stroke-width="1.7" fill="none" stroke-linecap="round"/><path d="M1 3.4 A10.8 10.8 0 0 1 16 3.4" stroke="${col}" stroke-width="1.7" fill="none" stroke-linecap="round"/></svg>`,
        div({width: p(25), height: p(12), borderRadius: p(3.5), border: `${p(1)}px solid ${col}`, opacity: 0.9, padding: p(1.5), boxSizing: 'border-box'}, div({width: '78%', height: '100%', borderRadius: p(1.5), background: col})),
      ]),
    ]);
  };

  const TAB_ICONS = {
    Today: '<path d="M4 12 l5 5 l11 -11" stroke-width="2.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>',
    Insights: '<path d="M5 20 V12 M12 20 V5 M19 20 V9" stroke-width="2.8" fill="none" stroke-linecap="round"/>',
    Reminders: '<path d="M12 3 a6 6 0 0 1 6 6 v4 l2 3 H4 l2 -3 V9 a6 6 0 0 1 6 -6 Z M10 19 a2 2 0 0 0 4 0" stroke-width="2" fill="none" stroke-linejoin="round"/>',
  };
  const tabBar = (w, h, active) =>
    div({position: 'absolute', left: 0, top: h - p(83), width: w, height: p(83), background: 'rgba(255,255,255,0.92)', borderTop: `1px solid ${C.line}`, display: 'flex', justifyContent: 'space-around', paddingTop: p(8), boxSizing: 'border-box'},
      Object.keys(TAB_ICONS).map((k) => {
        const col = k === active ? C.primary : '#A3A7BF';
        return div({display: 'flex', flexDirection: 'column', alignItems: 'center', gap: p(3), color: col}, [
          `<svg width="${p(26)}" height="${p(26)}" viewBox="0 0 24 24" stroke="${col}">${TAB_ICONS[k]}</svg>`,
          div({fontSize: p(10.5), fontWeight: 600}, k),
        ]);
      }));

  const phone = (w, h, children) => div({position: 'relative', width: w, height: h, background: C.bg, overflow: 'hidden', color: C.ink}, [children, statusBar(w)]);

  const largeTitle = (eyebrow, title) => div(abs(p(20), p(62)), [
    eyebrow ? div({fontSize: p(13), fontWeight: 600, color: C.sub, letterSpacing: '0.4px', textTransform: 'uppercase'}, eyebrow) : '',
    div({fontSize: p(34), fontWeight: 800, letterSpacing: '-0.8px', marginTop: p(2)}, title),
  ]);

  const card = (x, y, w, h, style, children) => div(Object.assign(abs(x, y), {width: w, height: h, background: C.card, borderRadius: p(20), boxShadow: '0 6px 24px rgba(30,34,80,0.07)'}, style || {}), children);

  // Touch hotspot: allowed by Apple's preview guidance to show interaction.
  const touch = (f, at, x, y) => {
    const rel = f - at;
    if (rel < -9 || rel > 22) return '';
    const dotIn = interpolate(rel, [-9, 0], [0, 1]);
    const dotOut = interpolate(rel, [6, 14], [1, 0]);
    const press = interpolate(rel, [-2, 0, 4], [1, 0.82, 1]);
    const ring = interpolate(rel, [0, 20], [0, 1], Easing.outCubic);
    const size = p(44);
    return div(abs(x - size / 2, y - size / 2, {width: size, height: size, borderRadius: size, background: 'rgba(40,40,80,0.28)', border: `${p(2)}px solid rgba(255,255,255,0.9)`, boxShadow: '0 4px 14px rgba(0,0,0,0.18)', opacity: dotIn * dotOut, transform: `scale(${press * (0.8 + 0.2 * dotIn)})`, zIndex: 60})) +
      (rel >= 0 ? div(abs(x - size, y - size, {width: size * 2, height: size * 2, borderRadius: size * 2, border: `${p(2.5)}px solid rgba(91,91,247,0.6)`, opacity: 1 - ring, transform: `scale(${0.4 + ring * 0.9})`, zIndex: 60})) : '');
  };

  const CONFETTI = ['#5B5BF7', '#1FC79A', '#FF7A45', '#FFC93C', '#FF5C8A', '#9B6BFF'];
  const confetti = (f, at, x, y, n) => {
    const t = f - at;
    if (t < 0 || t > 75) return '';
    let out = '';
    for (let i = 0; i < (n || 80); i++) {
      const a = random('a' + i) * Math.PI * 2;
      const v = p(7 + random('v' + i) * 13);
      const drag = 1 - Math.exp(-t / 9);
      const px = x + Math.cos(a) * v * 9 * drag;
      const py = y + Math.sin(a) * v * 9 * drag - p(4) * 9 * drag + 0.05 * p(1) * t * t * 1.4;
      const rot = random('r' + i) * 360 + t * (random('s' + i) * 20 - 10);
      const wob = Math.abs(Math.cos(t / 4 + i));
      out += div(abs(px, py, {width: p(7), height: p(12) * wob + p(2), background: CONFETTI[i % CONFETTI.length], borderRadius: i % 3 === 0 ? p(6) : p(1.5), transform: `rotate(${rot}deg)`, opacity: interpolate(t, [50, 75], [1, 0]), zIndex: 55}));
    }
    return out;
  };

  const appIcon = (size, f) => div({width: size, height: size, borderRadius: size * 0.225, background: `linear-gradient(145deg, ${C.primary2}, ${C.primary})`, position: 'relative', overflow: 'hidden', boxShadow: `0 ${size * 0.08}px ${size * 0.25}px rgba(60,40,200,0.35)`}, [
    ...[0.62, 0.42, 0.22].map((r, i) => div({position: 'absolute', left: '50%', top: '50%', width: size * r, height: size * r, marginLeft: (-size * r) / 2, marginTop: (-size * r) / 2, borderRadius: size, border: `${size * 0.045}px solid rgba(255,255,255,${0.35 + i * 0.3})`, transform: `scale(${1 + 0.04 * Math.sin((f || 0) / 9 - i)})`})),
    div({position: 'absolute', left: '50%', top: '50%', width: size * 0.09, height: size * 0.09, marginLeft: -size * 0.045, marginTop: -size * 0.045, borderRadius: size, background: '#fff'}),
  ]);

  const checkMark = (size, progress) => `<svg width="${size}" height="${size}" viewBox="0 0 24 24"><path d="M6 12.5 l4 4 l8 -9" stroke="#fff" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="20" stroke-dashoffset="${20 * (1 - progress)}"/></svg>`;

  const iconTile = (emoji, tint, size) => div(abs(p(12), p(11), {width: p(size || 44), height: p(size || 44), borderRadius: p(14), background: tint, fontSize: p(24), display: 'flex', alignItems: 'center', justifyContent: 'center'}), emoji);

  // ---------------------------------------------------------------- Today
  const ROWS = [
    {emoji: '🏃', title: 'Morning run', sub: '5 km · 7:12 AM', tint: '#FFE9DE', doneAt: -1},
    {emoji: '🧘', title: 'Meditate', sub: '10 min', tint: '#E8E7FF', doneAt: 20},
    {emoji: '📚', title: 'Read 20 pages', sub: 'Before bed', tint: '#DCF6EE', doneAt: 60},
    {emoji: '💧', title: 'Drink water', sub: '8 glasses', tint: '#DFF0FF', doneAt: -1},
    {emoji: '🤸', title: 'Stretch', sub: '5 min', tint: '#FFF3D6', doneAt: -1},
  ];
  const COMPLETE = 85;

  function today(f, w, h) {
    const done = ROWS.map((r) => (r.doneAt < 0 ? 1 : pop(f, r.doneAt)));
    const count = ROWS.filter((r) => r.doneAt < 0 || f >= r.doneAt).length;
    const progress = done.reduce((a, b) => a + Math.min(b, 1), 0) / ROWS.length;
    const perfect = pop(f, COMPLETE, {damping: 11, stiffness: 140});
    const cardX = p(16), cardW = w - p(32), ringR = p(46);
    const ringCx = cardX + p(22) + ringR + p(8), ringCy = p(150) + p(75);
    const circ = 2 * Math.PI * ringR;
    const all = count === ROWS.length;
    const ringSvg = `<svg style="position:absolute;left:${ringCx - cardX - ringR - p(8)}px;top:${p(75) - ringR - p(8)}px" width="${ringR * 2 + p(16)}" height="${ringR * 2 + p(16)}"><circle cx="${ringR + p(8)}" cy="${ringR + p(8)}" r="${ringR}" stroke="${C.line}" stroke-width="${p(12)}" fill="none"/><circle cx="${ringR + p(8)}" cy="${ringR + p(8)}" r="${ringR}" stroke="${progress >= 0.999 ? C.mint : C.primary}" stroke-width="${p(12)}" fill="none" stroke-linecap="round" stroke-dasharray="${circ}" stroke-dashoffset="${circ * (1 - progress)}" transform="rotate(-90 ${ringR + p(8)} ${ringR + p(8)})"/></svg>`;

    const rows = ROWS.map((r, i) => {
      const y = p(352 + i * 76), d = done[i], cs = p(30);
      const flash = r.doneAt < 0 ? 0 : interpolate(f - r.doneAt, [0, 6, 22], [0, 1, 0]);
      return card(cardX, y, cardW, p(66), {background: flash > 0 ? `rgba(31,199,154,${0.06 + 0.1 * flash})` : C.card}, [
        iconTile(r.emoji, r.tint),
        div(abs(p(68), p(12)), [div({fontSize: p(17), fontWeight: 650}, r.title), div({fontSize: p(13.5), color: C.sub, marginTop: p(2)}, r.sub)]),
        div({position: 'absolute', right: p(18), top: p(18), width: cs, height: cs, borderRadius: cs, border: `${p(2.5)}px solid ${C.line}`, boxSizing: 'border-box'}),
        div({position: 'absolute', right: p(18), top: p(18), width: cs, height: cs, borderRadius: cs, background: C.mint, transform: `scale(${d})`, display: 'flex', alignItems: 'center', justifyContent: 'center'}, checkMark(p(22), Math.min(1, d * 1.2))),
      ]);
    });
    const touches = ROWS.map((r, i) => (r.doneAt >= 0 ? touch(f, r.doneAt, w - p(16) - p(18) - p(15), p(352 + i * 76) + p(33)) : ''));

    return phone(w, h, [
      largeTitle('Good morning, Sam', 'Today'),
      div({position: 'absolute', right: p(20), top: p(72), width: p(40), height: p(40), borderRadius: p(20), background: 'linear-gradient(135deg,#FFB38A,#FF7A9C)', color: '#fff', fontWeight: 700, fontSize: p(17), display: 'flex', alignItems: 'center', justifyContent: 'center'}, 'S'),
      card(cardX, p(150), cardW, p(150), {boxShadow: `0 6px 24px rgba(30,34,80,0.07), 0 0 0 ${p(3) * perfect}px rgba(31,199,154,${0.5 * perfect})`}, [
        ringSvg,
        div(abs(ringCx - cardX - ringR, p(75) - p(16), {width: ringR * 2, textAlign: 'center', fontSize: p(26), fontWeight: 800, letterSpacing: '-0.5px'}), `${count}/${ROWS.length}`),
        div(abs(ringCx - cardX + ringR + p(26), p(40)), [
          div({fontSize: p(22), fontWeight: 800, letterSpacing: '-0.4px'}, all ? 'Perfect day! 🎉' : `${count} of ${ROWS.length} done`),
          div({fontSize: p(15), color: C.sub, marginTop: p(4)}, all ? 'Every habit checked off.' : 'Keep the momentum going.'),
          div({marginTop: p(10), display: 'inline-flex', alignItems: 'center', gap: p(6), padding: `${p(5)}px ${p(10)}px`, borderRadius: p(20), background: '#FFF0E8', color: C.flame, fontWeight: 700, fontSize: p(14), transform: `scale(${0.6 + 0.4 * perfect})`, opacity: perfect}, '🔥 +1 day streak'),
        ]),
      ]),
      div(abs(p(20), p(318), {fontSize: p(20), fontWeight: 700}), 'Habits'),
      ...rows, ...touches,
      confetti(f, COMPLETE, ringCx, ringCy),
      tabBar(w, h, 'Today'),
    ]);
  }

  // ---------------------------------------------------------------- Streak
  const PRE = [0.35, 0, 0.6, 0.35, 0];
  function streak(f, w, h) {
    const count = Math.round(interpolate(f, [8, 68], [1, 30], Easing.outCubic));
    const flame = 1 + 0.06 * Math.sin(f / 4) + 0.12 * interpolate(f, [8, 68], [0, 1]);
    const badge = pop(f, 80, {damping: 9, stiffness: 200});
    const cardX = p(16), cardW = w - p(32), cell = p(36);
    const gap = (cardW - p(36) - cell * 7) / 6;
    const cells = [];
    for (let i = 0; i < 35; i++) {
      const col = i % 7, row = Math.floor(i / 7), pre = i < 5, day = i - 4;
      const on = pre ? PRE[i] : pop(f, 8 + (day - 1) * 2, {damping: 12, stiffness: 220});
      const isToday = i === 34;
      cells.push(div(abs(p(18) + col * (cell + gap), p(76) + row * (cell + p(9)), {width: cell, height: cell, borderRadius: p(10), background: '#EEF0F7'}),
        div({position: 'absolute', inset: 0, borderRadius: p(10), background: pre ? `rgba(91,91,247,${PRE[i]})` : C.primary, transform: `scale(${pre ? 1 : on})`, boxShadow: isToday && on > 0.5 ? `0 0 0 ${p(3)}px rgba(255,122,69,0.9)` : 'none'})));
    }
    return phone(w, h, [
      div(abs(p(14), p(60), {color: C.primary, fontSize: p(17), fontWeight: 500}), '‹ Today'),
      div(abs(p(20), p(98), {display: 'flex', alignItems: 'center', gap: p(14)}), [
        div({width: p(60), height: p(60), borderRadius: p(18), background: '#E8E7FF', fontSize: p(32), display: 'flex', alignItems: 'center', justifyContent: 'center'}, '🧘'),
        div({}, [div({fontSize: p(28), fontWeight: 800, letterSpacing: '-0.6px'}, 'Meditate'), div({fontSize: p(15), color: C.sub}, '10 min · every day')]),
      ]),
      card(cardX, p(186), cardW, p(190), {background: 'linear-gradient(135deg,#FF8A50,#FF5C7A)', color: '#fff', overflow: 'hidden'}, [
        div({position: 'absolute', right: -p(30), top: -p(40), width: p(220), height: p(220), borderRadius: p(200), background: 'rgba(255,255,255,0.12)'}),
        div(abs(p(22), p(26), {fontSize: p(58), transform: `scale(${flame})`, transformOrigin: '50% 80%'}), '🔥'),
        div(abs(p(104), p(18), {fontSize: p(84), fontWeight: 800, letterSpacing: '-3px', fontVariantNumeric: 'tabular-nums'}), String(count)),
        div(abs(p(108), p(122), {fontSize: p(19), fontWeight: 600, opacity: 0.92}), 'day streak'),
        div({position: 'absolute', left: p(22), bottom: p(16), fontSize: p(14), opacity: 0.85}, 'Longest ever · keep it going'),
      ]),
      div({position: 'absolute', right: p(30), top: p(196), padding: `${p(8)}px ${p(14)}px`, borderRadius: p(14), background: '#fff', color: C.flame, fontWeight: 800, fontSize: p(15), boxShadow: '0 8px 24px rgba(0,0,0,0.18)', transform: `scale(${interpolate(badge, [0, 1], [2.2, 1])}) rotate(${interpolate(badge, [0, 1], [-20, -6])}deg)`, opacity: Math.min(1, badge * 2), zIndex: 10}, '🏅 30-day badge'),
      card(cardX, p(396), cardW, p(300), {}, [
        div(abs(p(18), p(16), {fontSize: p(17), fontWeight: 700}), 'Last 5 weeks'),
        div({position: 'absolute', right: p(18), top: p(18), fontSize: p(14), color: C.sub}, `${Math.round(((count + 2) / 35) * 100)}% done`),
        ...['M', 'T', 'W', 'T', 'F', 'S', 'S'].map((d, i) => div(abs(p(18) + i * (cell + gap), p(52), {width: cell, textAlign: 'center', fontSize: p(12), color: C.sub, fontWeight: 600}), d)),
        ...cells,
      ]),
      tabBar(w, h, 'Today'),
    ]);
  }

  // ---------------------------------------------------------------- Insights
  const WEEK = {labels: ['M', 'T', 'W', 'T', 'F', 'S', 'S'], values: [0.6, 0.8, 1, 0.8, 1, 1, 0.8]};
  const MONTH = {labels: ['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct'], values: [0.52, 0.61, 0.58, 0.7, 0.76, 0.83, 0.87]};
  function insights(f, w, h) {
    const TAP = 80;
    const cardX = p(16), cardW = w - p(32);
    const seg = ease(f, TAP + 1, TAP + 9);
    const monthMode = f >= TAP + 2;
    const up = (to) => Math.round(interpolate(f, [10, 55], [0, to], Easing.outCubic));
    const stats = [{v: `${up(87)}%`, l: 'Consistency', c: C.primary}, {v: `${up(142)}`, l: 'Check-ins', c: C.mint}, {v: `${up(30)}d`, l: 'Best streak', c: C.flame}];
    const statW = (cardW - p(20)) / 3;
    const chartTop = p(48), chartH = p(200), barW = p(26), span = cardW - p(48);
    const segW = p(240), segX = (w - segW) / 2;
    const bars = WEEK.values.map((wv, i) => {
      const grow = pop(f, 10 + i * 3, {damping: 14, stiffness: 120});
      const morph = pop(f, TAP + 4 + i * 2, {damping: 14, stiffness: 140});
      const v = interpolate(morph, [0, 1], [wv, MONTH.values[i]]) * grow;
      const x = p(24) + (span / 7) * i + (span / 7 - barW) / 2;
      const last = i === 6;
      return div(abs(x, chartTop + chartH * (1 - v), {width: barW, height: chartH * v, borderRadius: p(8), background: last ? `linear-gradient(180deg, ${C.mint}, #12A57E)` : `linear-gradient(180deg, ${C.primary2}, ${C.primary})`})) +
        div(abs(x - p(10), chartTop + chartH + p(10), {width: barW + p(20), textAlign: 'center', fontSize: p(13), color: C.sub, fontWeight: 600}), monthMode ? MONTH.labels[i] : WEEK.labels[i]);
    });
    const note = ease(f, 96, 106);
    return phone(w, h, [
      largeTitle('Your progress', 'Insights'),
      div(abs(segX, p(150), {width: segW, height: p(34), borderRadius: p(10), background: '#E6E8F2'}), [
        div(abs(p(2) + seg * (segW / 2 - p(2)), p(2), {width: segW / 2 - p(2), height: p(30), borderRadius: p(8), background: '#fff', boxShadow: '0 2px 6px rgba(0,0,0,0.1)'})),
        ...['Week', 'Month'].map((t, i) => div(abs((i * segW) / 2, p(7), {width: segW / 2, textAlign: 'center', fontSize: p(14), fontWeight: 600}), t)),
      ]),
      ...stats.map((s, i) => card(cardX + i * (statW + p(10)), p(200), statW, p(104), {}, [
        div(abs(p(14), p(16), {fontSize: p(30), fontWeight: 800, letterSpacing: '-1px', color: s.c, fontVariantNumeric: 'tabular-nums'}), s.v),
        div(abs(p(14), p(62), {fontSize: p(13.5), color: C.sub, fontWeight: 600}), s.l),
      ])),
      card(cardX, p(320), cardW, p(330), {}, [
        div(abs(p(20), p(18), {fontSize: p(17), fontWeight: 700}), monthMode ? 'Completion by month' : 'Habits done this week'),
        ...[0.25, 0.5, 0.75, 1].map((g) => div({position: 'absolute', left: p(20), right: p(20), top: chartTop + chartH * (1 - g), height: 1, background: C.line})),
        ...bars,
        div({position: 'absolute', left: p(20), bottom: p(18), fontSize: p(15), fontWeight: 700, color: C.mint, opacity: note, transform: `translateY(${(1 - note) * p(8)}px)`}, '↑ 12% vs last month'),
      ]),
      touch(f, TAP, segX + (segW * 3) / 4, p(150) + p(17)),
      tabBar(w, h, 'Insights'),
    ]);
  }

  // ---------------------------------------------------------------- Reminders
  const HOURS = Array.from({length: 12}, (_, i) => `${i + 1}`);
  const MINS = Array.from({length: 12}, (_, i) => String(i * 5).padStart(2, '0'));
  const toggle = (on) => div({width: p(51), height: p(31), borderRadius: p(16), background: on > 0.5 ? C.mint : '#E3E5EE', position: 'relative'},
    div(abs(p(2) + on * p(20), p(2), {width: p(27), height: p(27), borderRadius: p(14), background: '#fff', boxShadow: '0 2px 5px rgba(0,0,0,0.2)'})));
  const wheel = (items, pos, x, width, rowH) => div(abs(x, 0, {width, height: rowH * 5, overflow: 'hidden'}),
    items.map((it, i) => {
      const d = i - pos;
      if (Math.abs(d) > 3) return '';
      return div(abs(0, rowH * (2 + d), {width, height: rowH, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: p(22), fontWeight: Math.abs(d) < 0.5 ? 600 : 400, color: C.ink, opacity: Math.max(0, 1 - Math.abs(d) * 0.32), transform: `scaleY(${1 - Math.min(1, Math.abs(d)) * 0.12})`}), it);
    }));

  function reminders(f, w, h) {
    const TOGGLE = 20, NOTIFY = 90;
    const cardX = p(16), cardW = w - p(32);
    const on = pop(f, TOGGLE + 1, {damping: 16, stiffness: 260});
    const open = pop(f, TOGGLE + 4, {damping: 18, stiffness: 140});
    const rowH = p(40), pickH = rowH * 5;
    const hour = ease(f, 32, 72, 8, 6), minute = ease(f, 32, 72, 0, 6);
    const note = pop(f, NOTIFY, {damping: 15, stiffness: 150});
    const expanded = (pickH + p(56)) * open;
    const row = (emoji, tint, title, sub, tg) => [iconTile(emoji, tint, 44).replace('top:' + p(11) + 'px', 'top:' + p(16) + 'px'),
      div(abs(p(70), p(16)), [div({fontSize: p(17), fontWeight: 650}, title), div({fontSize: p(13.5), color: C.sub, marginTop: p(2)}, sub)]),
      div({position: 'absolute', right: p(16), top: p(22)}, tg)];
    return phone(w, h, [
      largeTitle('Stay on track', 'Reminders'),
      card(cardX, p(150), cardW, p(76) + expanded, {overflow: 'hidden'}, [
        ...row('🧘', '#E8E7FF', 'Meditate', on > 0.5 ? 'Daily reminder on' : 'No reminder', toggle(on)),
        div({position: 'absolute', left: p(16), right: p(16), top: p(76), height: 1, background: C.line, opacity: open}),
        div(abs(p(18), p(92), {fontSize: p(15), fontWeight: 600, color: C.sub, opacity: open}), 'Remind me at'),
        div({position: 'absolute', left: p(16), right: p(16), top: p(120), height: pickH, opacity: open}, [
          div({position: 'absolute', left: 0, right: 0, top: rowH * 2, height: rowH, borderRadius: p(10), background: '#EFF0F7'}),
          wheel(HOURS, hour, cardW * 0.18, p(60), rowH), wheel(MINS, minute, cardW * 0.18 + p(70), p(60), rowH), wheel(['AM', 'PM'], 0, cardW * 0.18 + p(140), p(60), rowH),
        ]),
      ]),
      card(cardX, p(150) + p(92) + expanded, cardW, p(76), {}, row('✨', '#FFF3D6', 'Smart timing', 'Learns when you usually check in', toggle(1))),
      div(abs(p(10), interpolate(note, [0, 1], [-p(130), p(52)]), {width: w - p(20), height: p(92), borderRadius: p(26), background: 'rgba(250,250,255,0.86)', backdropFilter: 'blur(20px)', boxShadow: '0 12px 40px rgba(20,20,60,0.25)', zIndex: 40, opacity: interpolate(note, [0, 0.3], [0, 1])}), [
        div(abs(p(14), p(18)), appIcon(p(38), f)),
        div({position: 'absolute', left: p(64), right: p(16), top: p(16)}, [
          div({display: 'flex', justifyContent: 'space-between', fontSize: p(15), fontWeight: 700}, ['<span>Time to meditate 🧘</span>', `<span style="font-weight:400;color:${C.sub};font-size:${p(13)}px">now</span>`]),
          div({fontSize: p(15), marginTop: p(3), color: '#2A2D45'}, '10 minutes keeps your 30-day streak alive.'),
        ]),
      ]),
      touch(f, TOGGLE, w - p(16) - p(16) - p(25), p(150) + p(22) + p(15)),
      tabBar(w, h, 'Reminders'),
    ]);
  }

  window.SCREENS = {today, streak, insights, reminders};
  window.APP_ICON = appIcon;
})();
