#!/usr/bin/env node
// Build app preview videos from a plan.json.
//   node build.mjs prepare --plan plan.json --out out/      write preview pages
//   node build.mjs capture --plan plan.json --out out/      screenshot every frame -> video
//   node build.mjs encode  --plan plan.json --out out/      mix audio, encode store presets, verify
//   node build.mjs all     --plan plan.json --out out/
// Options: --cut <id> (repeatable), --cdp <ws-url> (skip agent-browser), --dry-run
// Needs: node >= 22, ffmpeg/ffprobe, and agent-browser (or any Chrome with --remote-debugging-port).
import {execFileSync, spawn, spawnSync} from 'node:child_process';
import {existsSync, mkdirSync, readFileSync, statSync, writeFileSync} from 'node:fs';
import {basename, dirname, join, resolve} from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const SKILL = resolve(HERE, '..');
const OVERLAY = join(SKILL, 'assets', 'overlay');
const AUDIO = join(SKILL, 'assets', 'audio');

export const CUTS = {
  // Apple accepted resolutions: 6.9"/6.5"/6.1"/5.8" iPhone share 886x1920.
  appstore: {layout: 'store', w: 886, h: 1920, encode: 'appstore', label: 'App Store · iPhone 6.9"–5.8"'},
  'appstore-ipad': {layout: 'store', w: 1200, h: 1600, encode: 'appstore', label: 'App Store · iPad 13"/12.9"/11"'},
  'appstore-landscape': {layout: 'store', w: 1920, h: 886, encode: 'appstore', label: 'App Store · iPhone landscape'},
  googleplay: {layout: 'store', w: 1080, h: 1920, encode: 'play', label: 'Google Play · YouTube portrait'},
  landing: {layout: 'landing', w: 1920, h: 1080, encode: 'landing', label: 'Landing page hero'},
};

export function parseArgs(argv) {
  const a = {cmd: argv[0], cuts: [], dryRun: false};
  for (let i = 1; i < argv.length; i++) {
    const k = argv[i];
    if (k === '--plan') a.plan = argv[++i];
    else if (k === '--out') a.out = argv[++i];
    else if (k === '--cut') a.cuts.push(argv[++i]);
    else if (k === '--cdp') a.cdp = argv[++i];
    else if (k === '--dry-run') a.dryRun = true;
    else throw new Error('unknown option ' + k);
  }
  if (!a.plan) throw new Error('--plan is required');
  return a;
}

export function loadPlan(planPath) {
  const file = resolve(planPath);
  const plan = JSON.parse(readFileSync(file, 'utf8'));
  plan.dir = dirname(file);
  plan.fps = plan.fps || 30;
  if (!plan.app?.name) throw new Error('plan.app.name is required');
  if (!Array.isArray(plan.scenes) || !plan.scenes.length) throw new Error('plan.scenes must have at least one scene');
  let at = 0;
  for (const s of plan.scenes) {
    if (!s.id || !(s.dur > 0)) throw new Error('each scene needs id and dur (frames)');
    s.from = at; at += s.dur;
    if (s.clip) {
      s.clip.src = resolve(plan.dir, s.clip.src);
      if (!existsSync(s.clip.src)) throw new Error(`clip not found for scene ${s.id}: ${s.clip.src}`);
    }
  }
  plan.end = Object.assign({dur: 90}, plan.end || {});
  plan.end.from = at;
  plan.total = at + plan.end.dur;
  plan.cuts = (plan.outputs || ['appstore', 'googleplay', 'landing']).map((o) => {
    const base = typeof o === 'string' ? {id: o} : o;
    const def = CUTS[base.id];
    if (!def && !(base.w && base.h && base.layout)) throw new Error(`unknown cut ${base.id}; known: ${Object.keys(CUTS).join(', ')}`);
    return Object.assign({}, def || {}, base);
  });
  // expand repeated cues: {at, sfx, repeat, every}
  plan.cueList = [];
  for (const c of plan.cues || []) {
    const n = c.repeat || 1;
    for (let i = 0; i < n; i++) plan.cueList.push({at: c.at + i * (c.every || 0), sfx: c.sfx, vol: c.vol ?? 0.5});
  }
  return plan;
}

const seconds = (plan, frames) => frames / plan.fps;

export function resolveAudio(plan, name) {
  const dirs = [plan.dir, plan.audio_dir ? resolve(plan.dir, plan.audio_dir) : null, AUDIO].filter(Boolean);
  for (const d of dirs) {
    for (const ext of ['', '.flac', '.wav', '.m4a', '.mp3', '.ogg', '.aac']) {
      const p = join(d, name + ext);
      if (existsSync(p) && statSync(p).isFile()) return p;
    }
  }
  throw new Error(`audio "${name}" not found in ${dirs.join(', ')}`);
}

// ---------------------------------------------------------------- prepare
export function previewHtml(plan, cut) {
  const planForPage = JSON.parse(JSON.stringify(plan));
  for (const s of planForPage.scenes) if (s.clip) s.clip.src = pathToFileURL(s.clip.src).href;
  if (planForPage.app.icon) planForPage.app.icon = pathToFileURL(resolve(plan.dir, plan.app.icon)).href;
  const mock = plan.mock ? readFileSync(resolve(plan.dir, plan.mock), 'utf8') : '';
  const cutDef = {id: cut.id, layout: cut.layout, w: cut.w, h: cut.h};
  return `<!doctype html>
<meta charset="utf-8">
<title>${plan.app.name} · ${cut.id}</title>
<style>html,body{margin:0;background:#000}body{overflow:hidden}#root{position:relative}*{-webkit-font-smoothing:antialiased}</style>
<div id="root"></div>
<script>${readFileSync(join(OVERLAY, 'runtime.js'), 'utf8')}</script>
<script>window.PLAN=${JSON.stringify(planForPage)};window.CUT=${JSON.stringify(cutDef)};</script>
<script>${mock}</script>
<script>${readFileSync(join(OVERLAY, 'cuts.js'), 'utf8')}</script>
`;
}

function prepare(plan, out, cuts) {
  mkdirSync(join(out, 'preview'), {recursive: true});
  const pages = [];
  for (const cut of cuts) {
    const file = join(out, 'preview', `${cut.id}.html`);
    writeFileSync(file, previewHtml(plan, cut));
    pages.push(file);
    console.log(`prepared ${file}  (${cut.w}x${cut.h}, ${plan.total} frames)`);
  }
  return pages;
}

// ---------------------------------------------------------------- capture
function cdp(wsUrl) {
  const ws = new WebSocket(wsUrl);
  const pending = new Map();
  let id = 0;
  ws.onmessage = (e) => {
    const m = JSON.parse(e.data);
    if (!pending.has(m.id)) return;
    const {res, rej} = pending.get(m.id);
    pending.delete(m.id);
    m.error ? rej(new Error(m.error.message)) : res(m.result);
  };
  const send = (method, params = {}) => new Promise((res, rej) => { pending.set(++id, {res, rej}); ws.send(JSON.stringify({id, method, params})); });
  return {open: new Promise((r, j) => { ws.onopen = r; ws.onerror = j; }), send, close: () => ws.close()};
}

async function pageTarget(browserWs, urlMatch) {
  const http = browserWs.replace(/^ws/, 'http').replace(/\/devtools\/browser\/.*$/, '');
  for (let i = 0; i < 50; i++) {
    const targets = await (await fetch(http + '/json/list')).json();
    const t = targets.find((x) => x.type === 'page' && x.url.includes(urlMatch));
    if (t) return t;
    await new Promise((r) => setTimeout(r, 100));
  }
  throw new Error('page not found in browser targets: ' + urlMatch);
}

function ab(session, ...args) {
  return execFileSync('agent-browser', args, {env: {...process.env, AGENT_BROWSER_SESSION: session}, encoding: 'utf8'}).trim();
}

async function captureCut(plan, cut, page, out, opts) {
  const workDir = join(out, 'work');
  mkdirSync(workDir, {recursive: true});
  const video = join(workDir, `${cut.id}.video.mp4`);
  const url = pathToFileURL(page).href + '?capture';
  let browserWs = opts.cdp, session = null;
  if (!browserWs) {
    session = `apv-${process.pid}`;
    ab(session, 'open', url);
    browserWs = ab(session, 'get', 'cdp-url');
  }
  const target = await pageTarget(browserWs, basename(page));
  const c = cdp(target.webSocketDebuggerUrl);
  await c.open;
  try {
    await c.send('Page.enable');
    if (opts.cdp) { await c.send('Page.navigate', {url}); await new Promise((r) => setTimeout(r, 300)); }
    await c.send('Emulation.setDeviceMetricsOverride', {width: cut.w, height: cut.h, deviceScaleFactor: 1, mobile: false});
    await c.send('Runtime.evaluate', {expression: 'window.ready', awaitPromise: true});
    const total = (await c.send('Runtime.evaluate', {expression: 'window.TOTAL'})).result.value;
    if (total !== plan.total) throw new Error(`page total ${total} != plan total ${plan.total}`);

    const ff = spawn('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', String(plan.fps), '-i', '-',
      '-c:v', 'libx264', '-preset', 'fast', '-crf', '8', '-pix_fmt', 'yuv420p', video], {stdio: ['pipe', 'inherit', 'inherit']});
    const t0 = Date.now();
    for (let f = 0; f < total; f++) {
      await c.send('Runtime.evaluate', {expression: `window.seek(${f})`, awaitPromise: true});
      const {data} = await c.send('Page.captureScreenshot', {format: 'png', captureBeyondViewport: false});
      const buf = Buffer.from(data, 'base64');
      if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
      // sample frames every 5 s for inspection without decoding the video
      if (f % (plan.fps * 5) === 0 || f === total - 1) writeFileSync(join(workDir, `${cut.id}.f${String(f).padStart(4, '0')}.png`), buf);
      if (f === 0 || (f + 1) % 100 === 0 || f === total - 1) process.stdout.write(`\r${cut.id}: frame ${f + 1}/${total}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
    ff.stdin.end();
    await new Promise((r, j) => ff.on('close', (code) => (code ? j(new Error('ffmpeg exit ' + code)) : r())));
    console.log(`\n${cut.id}: wrote ${video}`);
  } finally {
    c.close();
    if (session) try { ab(session, 'close'); } catch {}
  }
  return video;
}

// ---------------------------------------------------------------- encode
export function audioMixCommand(plan, outWav) {
  const inputs = [], filters = [], mixIn = [];
  let n = 0;
  const T = seconds(plan, plan.total).toFixed(3);
  if (plan.music) {
    inputs.push('-i', resolveAudio(plan, plan.music.src));
    filters.push(`[${n}]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,volume=${plan.music.vol ?? 0.4}[m]`);
    mixIn.push('[m]'); n++;
  } else {
    inputs.push('-f', 'lavfi', '-t', T, '-i', 'anullsrc=r=48000:cl=stereo');
    mixIn.push(`[${n}]`); n++;
  }
  for (const [i, cue] of plan.cueList.entries()) {
    const ms = Math.round(seconds(plan, cue.at) * 1000);
    inputs.push('-i', resolveAudio(plan, cue.sfx));
    filters.push(`[${n}]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,volume=${cue.vol},adelay=${ms}:all=1[s${i}]`);
    mixIn.push(`[s${i}]`); n++;
  }
  const graph = filters.concat([`${mixIn.join('')}amix=inputs=${mixIn.length}:normalize=0:dropout_transition=0,atrim=0:${T},loudnorm=I=-16:TP=-1.5:LRA=11[out]`]).join(';');
  return ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', ...inputs, '-filter_complex', graph, '-map', '[out]', '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s16le', outWav];
}

const AAC = ['-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-ac', '2'];
export function encodeCommands(plan, cut, video, audio, out) {
  const final = join(out, 'final');
  const base = `${slug(plan.app.name)}-${cut.id}-${cut.w}x${cut.h}`;
  const cmds = [];
  const vIn = ['-i', video, '-i', audio, '-map', '0:v', '-map', '1:a', '-shortest'];
  if (cut.encode === 'appstore') {
    // Apple: H.264 High ≤ 4.0 (4.1 for the larger iPad canvas), ≤30 fps, 10–12 Mbps, AAC 256 kbps stereo 44.1/48 kHz.
    const level = cut.w * cut.h > 886 * 1920 ? '4.1' : '4.0';
    cmds.push({out: join(final, base + '.mp4'), args: ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', ...vIn, '-c:v', 'libx264', '-profile:v', 'high', '-level:v', level, '-pix_fmt', 'yuv420p', '-r', String(plan.fps),
      '-b:v', '11M', '-minrate', '11M', '-maxrate', '11M', '-bufsize', '11M', '-x264-params', 'nal-hrd=cbr', '-preset', 'slow', ...AAC, '-movflags', '+faststart']});
    cmds.push({out: join(final, base + '-poster-5s.png'), args: ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-ss', '5', '-i', video, '-frames:v', '1']});
  } else if (cut.encode === 'play') {
    cmds.push({out: join(final, base + '.mp4'), args: ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', ...vIn, '-c:v', 'libx264', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-r', String(plan.fps), '-crf', '16', '-preset', 'slow', ...AAC, '-movflags', '+faststart']});
    cmds.push({out: join(final, base + '.srt'), text: srt(plan)});
  } else {
    cmds.push({out: join(final, base + '.mp4'), args: ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', ...vIn, '-c:v', 'libx264', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'slow', ...AAC, '-movflags', '+faststart']});
    cmds.push({out: join(final, base + '-muted.webm'), args: ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', video, '-an', '-c:v', 'libvpx-vp9', '-b:v', '0', '-crf', '34', '-row-mt', '1']});
    cmds.push({out: join(final, base + '-poster.jpg'), args: ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-ss', '5', '-i', video, '-frames:v', '1', '-q:v', '3']});
  }
  return cmds;
}

const slug = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
const tc = (sec) => { const ms = Math.round(sec * 1000); const h = Math.floor(ms / 3600000), m = Math.floor(ms / 60000) % 60, s = Math.floor(ms / 1000) % 60; return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')},${String(ms % 1000).padStart(3, '0')}`; };
export function srt(plan) {
  const lines = [];
  let i = 1;
  for (const s of plan.scenes) if (s.caption) lines.push(`${i++}\n${tc(seconds(plan, s.from + 6))} --> ${tc(seconds(plan, s.from + s.dur))}\n${s.caption}\n`);
  lines.push(`${i++}\n${tc(seconds(plan, plan.end.from))} --> ${tc(seconds(plan, plan.total))}\n${[plan.app.name, plan.app.tagline].filter(Boolean).join('. ')}\n`);
  return lines.join('\n');
}

export function verify(plan, cut, file) {
  const info = JSON.parse(execFileSync('ffprobe', ['-v', 'error', '-show_streams', '-show_format', '-of', 'json', file], {encoding: 'utf8'}));
  const v = info.streams.find((s) => s.codec_type === 'video'), a = info.streams.find((s) => s.codec_type === 'audio');
  const dur = parseFloat(info.format.duration), size = parseInt(info.format.size, 10);
  const fps = v ? eval(v.r_frame_rate) : 0;
  const checks = [
    ['resolution', `${v?.width}x${v?.height}`, v?.width === cut.w && v?.height === cut.h],
    ['video codec', `${v?.codec_name} ${v?.profile || ''} L${v?.level}`, cut.encode === 'landing' || (v?.codec_name === 'h264' && (cut.encode !== 'appstore' || v.level <= 41))],
    ['frame rate', `${fps}`, fps <= 30],
    ['duration', `${dur.toFixed(2)} s`, cut.encode === 'landing' || (dur >= 15 && dur <= 30.5)],
    ['audio', a ? `${a.codec_name} ${a.sample_rate} Hz ${a.channels}ch ${Math.round(a.bit_rate / 1000)} kbps` : 'none', !a || (a.codec_name === 'aac' && a.channels === 2 && ['44100', '48000'].includes(a.sample_rate))],
    ['file size', `${(size / 1e6).toFixed(1)} MB`, size < 500e6],
  ];
  if (cut.encode === 'appstore') checks.push(['bit rate', `${(parseInt(v.bit_rate, 10) / 1e6).toFixed(1)} Mbps`, parseInt(v.bit_rate, 10) >= 9e6 && parseInt(v.bit_rate, 10) <= 13e6]);
  return checks;
}

function encode(plan, cuts, out, dryRun) {
  mkdirSync(join(out, 'final'), {recursive: true});
  mkdirSync(join(out, 'work'), {recursive: true});
  const audio = join(out, 'work', 'audio.wav');
  const mix = audioMixCommand(plan, audio);
  run(mix, dryRun);
  const report = [];
  for (const cut of cuts) {
    const video = join(out, 'work', `${cut.id}.video.mp4`);
    if (!dryRun && !existsSync(video)) throw new Error(`missing ${video}; run capture first`);
    for (const c of encodeCommands(plan, cut, video, audio, out)) {
      if (c.text !== undefined) { if (!dryRun) writeFileSync(c.out, c.text); else console.log('write', c.out); continue; }
      run([...c.args, c.out], dryRun);
      if (!dryRun && c.out.endsWith('.mp4')) report.push({cut, file: c.out, checks: verify(plan, cut, c.out)});
    }
  }
  for (const r of report) {
    console.log(`\n${r.cut.label || r.cut.id}  →  ${r.file}`);
    for (const [k, v, ok] of r.checks) console.log(`  ${ok ? '✓' : '✗'} ${k.padEnd(12)} ${v}`);
  }
  const bad = report.flatMap((r) => r.checks.filter((c) => !c[2]));
  if (bad.length) { console.error(`\n${bad.length} check(s) failed`); process.exitCode = 2; }
}

function run(cmd, dryRun) {
  if (dryRun) { console.log(cmd.map((x) => (/[\s;\[\]]/.test(x) ? `'${x}'` : x)).join(' ')); return; }
  const r = spawnSync(cmd[0], cmd.slice(1), {stdio: 'inherit'});
  if (r.status !== 0) throw new Error(`${cmd[0]} failed (${r.status})`);
}

// ---------------------------------------------------------------- main
async function main() {
  const args = parseArgs(process.argv.slice(2));
  const plan = loadPlan(args.plan);
  const out = resolve(args.out || join(plan.dir, 'out'));
  const cuts = args.cuts.length ? plan.cuts.filter((c) => args.cuts.includes(c.id)) : plan.cuts;
  if (!cuts.length) throw new Error('no cuts selected');
  if (args.cmd === 'prepare' || args.cmd === 'all') prepare(plan, out, cuts);
  if (args.cmd === 'capture' || args.cmd === 'all') {
    for (const cut of cuts) {
      const page = join(out, 'preview', `${cut.id}.html`);
      if (!existsSync(page)) prepare(plan, out, [cut]);
      if (args.dryRun) { console.log(`would capture ${plan.total} frames of ${page}`); continue; }
      await captureCut(plan, cut, page, out, args);
    }
  }
  if (args.cmd === 'encode' || args.cmd === 'all') encode(plan, cuts, out, args.dryRun);
  if (!['prepare', 'capture', 'encode', 'all'].includes(args.cmd)) throw new Error('command must be prepare | capture | encode | all');
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch((e) => { console.error('error:', e.message); process.exit(1); });
}
