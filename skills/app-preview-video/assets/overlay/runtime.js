// Animation helpers for the overlay page. Everything is a pure function of the
// frame number, so a frame renders the same way every time it is requested.
// No dependencies; works in the browser and in Node (for tests).
(function (root) {
  'use strict';

  const FPS = 30;
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));

  const Easing = {
    linear: (t) => t,
    inCubic: (t) => t * t * t,
    outCubic: (t) => 1 - Math.pow(1 - t, 3),
    inOutCubic: (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
  };

  // Map `v` from the input range to the output range, clamped at both ends.
  // `ranges` may hold more than two stops: interpolate(f, [0, 10, 20], [0, 1, 0]).
  function interpolate(v, input, output, easing) {
    const n = input.length;
    if (v <= input[0]) return output[0];
    if (v >= input[n - 1]) return output[n - 1];
    let i = 1;
    while (input[i] < v) i++;
    let t = (v - input[i - 1]) / (input[i] - input[i - 1]);
    if (easing) t = easing(t);
    return output[i - 1] + (output[i] - output[i - 1]) * t;
  }

  // Analytic damped spring from 0 to 1, same parameters as the common
  // {damping, stiffness, mass} model. Overshoots when under-damped.
  function spring(frame, config, fps) {
    const {damping = 10, stiffness = 100, mass = 1} = config || {};
    if (frame <= 0) return 0;
    const t = frame / (fps || FPS);
    const w0 = Math.sqrt(stiffness / mass);
    const z = damping / (2 * Math.sqrt(stiffness * mass));
    if (z < 1) {
      const wd = w0 * Math.sqrt(1 - z * z);
      return 1 - Math.exp(-z * w0 * t) * (Math.cos(wd * t) + ((z * w0) / wd) * Math.sin(wd * t));
    }
    if (z === 1) return 1 - Math.exp(-w0 * t) * (1 + w0 * t);
    const s1 = -w0 * (z - Math.sqrt(z * z - 1));
    const s2 = -w0 * (z + Math.sqrt(z * z - 1));
    return 1 - (s2 * Math.exp(s1 * t) - s1 * Math.exp(s2 * t)) / (s2 - s1);
  }

  // Spring that stays at 0 before frame `at`.
  const pop = (f, at, config) => (f < at ? 0 : spring(f - at, config || {damping: 13, stiffness: 170}));

  // Eased ramp between frames a and b, from `from` to `to`.
  const ease = (f, a, b, from, to, fn) =>
    interpolate(f, [a, b], [from === undefined ? 0 : from, to === undefined ? 1 : to], fn || Easing.inOutCubic);

  // Deterministic pseudo-random number in [0, 1) for a string seed.
  function random(seed) {
    let h = 1779033703 ^ String(seed).length;
    for (let i = 0; i < String(seed).length; i++) {
      h = Math.imul(h ^ String(seed).charCodeAt(i), 3432918353);
      h = (h << 13) | (h >>> 19);
    }
    h = Math.imul(h ^ (h >>> 16), 2246822507);
    h = Math.imul(h ^ (h >>> 13), 3266489909);
    return ((h ^= h >>> 16) >>> 0) / 4294967296;
  }

  // Style object -> inline CSS. Numbers get `px` except for unitless properties,
  // like React's style prop.
  const UNITLESS = new Set(['opacity', 'zIndex', 'fontWeight', 'lineHeight', 'flex', 'flexGrow', 'flexShrink', 'order', 'zoom']);
  function css(style) {
    let out = '';
    for (const k in style) {
      const v = style[k];
      if (v === undefined || v === null || v === false) continue;
      const prop = k.replace(/[A-Z]/g, (m) => '-' + m.toLowerCase());
      out += prop + ':' + (typeof v === 'number' && !UNITLESS.has(k) ? v + 'px' : v) + ';';
    }
    return out;
  }

  // <div style=...>children</div>
  const div = (style, children, attrs) =>
    '<div style="' + css(style) + '"' + (attrs ? ' ' + attrs : '') + '>' + (children == null ? '' : Array.isArray(children) ? children.join('') : children) + '</div>';

  const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

  const api = {FPS, clamp, Easing, interpolate, spring, pop, ease, random, css, div, esc};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.R = api;
})(typeof window !== 'undefined' ? window : globalThis);
