"""Offline checks for the app preview video plan, overlay runtime, and encode commands."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1] / "skills/app-preview-video"
BUILD = SKILL / "scripts/build.mjs"
EXAMPLE = SKILL / "examples/ripple/plan.json"


def node(code, *args):
    return subprocess.run(["node", "--input-type=module", "-e", code, "--", *args],
                          capture_output=True, text=True, check=True, cwd=SKILL).stdout


@unittest.skipUnless(shutil.which("node"), "node is required")
class RuntimeTests(unittest.TestCase):
    def test_spring_settles_and_pop_waits(self):
        out = node("""
            import {createRequire} from 'node:module';
            const R = createRequire(import.meta.url)('./assets/overlay/runtime.js');
            console.log(JSON.stringify({
              zero: R.spring(0), mid: R.spring(8, {damping: 10, stiffness: 100}), settled: R.spring(400),
              before: R.pop(5, 10), after: R.pop(60, 10),
              interp: R.interpolate(5, [0, 10], [0, 100]), clampHi: R.interpolate(50, [0, 10], [0, 100]),
              multi: R.interpolate(15, [0, 10, 20], [0, 1, 0]),
              rnd: [R.random('a'), R.random('a'), R.random('b')],
              css: R.css({opacity: 0.5, fontWeight: 700, left: 10, zIndex: 2}),
            }));
        """)
        r = json.loads(out)
        self.assertEqual(r["zero"], 0)
        self.assertGreater(r["mid"], 0.5)
        self.assertAlmostEqual(r["settled"], 1, places=4)
        self.assertEqual(r["before"], 0)
        self.assertAlmostEqual(r["after"], 1, places=2)
        self.assertEqual(r["interp"], 50)
        self.assertEqual(r["clampHi"], 100)
        self.assertEqual(r["multi"], 0.5)
        self.assertEqual(r["rnd"][0], r["rnd"][1])
        self.assertNotEqual(r["rnd"][0], r["rnd"][2])
        self.assertEqual(r["css"], "opacity:0.5;font-weight:700;left:10px;z-index:2;")


@unittest.skipUnless(shutil.which("node"), "node is required")
class PlanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def load(self, plan):
        path = self.root / "plan.json"
        path.write_text(json.dumps(plan))
        return json.loads(node(f"""
            import {{loadPlan}} from '{BUILD.as_uri()}';
            const p = loadPlan(process.argv[1]);
            console.log(JSON.stringify({{total: p.total, end: p.end.from, cues: p.cueList, cuts: p.cuts.map(c => [c.id, c.w, c.h, c.layout])}}));
        """, str(path)))

    def test_example_plan_timeline_and_cue_expansion(self):
        plan = json.loads(EXAMPLE.read_text())
        plan.pop("mock")
        p = self.load(plan)
        self.assertEqual(p["end"], 660)
        self.assertEqual(p["total"], 750)
        ticks = [c for c in p["cues"] if c["sfx"] == "tick" and 222 <= c["at"] <= 276]
        self.assertEqual([c["at"] for c in ticks], list(range(222, 277, 6)))
        self.assertEqual(p["cuts"][0], ["appstore", 886, 1920, "store"])
        self.assertEqual(p["cuts"][2], ["landing", 1920, 1080, "landing"])

    def test_missing_clip_and_unknown_cut_are_rejected(self):
        base = {"app": {"name": "X"}, "scenes": [{"id": "a", "dur": 300}]}
        with self.assertRaises(subprocess.CalledProcessError) as ctx:
            self.load({**base, "scenes": [{"id": "a", "dur": 300, "clip": {"src": "nope.mp4"}}]})
        self.assertIn("clip not found", ctx.exception.stderr)
        with self.assertRaises(subprocess.CalledProcessError) as ctx:
            self.load({**base, "outputs": ["tiktok"]})
        self.assertIn("unknown cut", ctx.exception.stderr)

    def test_encode_dry_run_matches_store_specs(self):
        plan = json.loads(EXAMPLE.read_text())
        plan.pop("mock")
        path = self.root / "plan.json"
        path.write_text(json.dumps(plan))
        out = subprocess.run(["node", str(BUILD), "encode", "--plan", str(path), "--out", str(self.root / "out"), "--dry-run"],
                             capture_output=True, text=True, check=True).stdout
        lines = out.splitlines()
        mix = lines[0]
        self.assertIn("amix=inputs=", mix)
        self.assertIn("loudnorm=I=-16:TP=-1.5", mix)
        self.assertIn("music.m4a", mix)
        appstore = next(l for l in lines if "ripple-appstore-886x1920.mp4" in l)
        for flag in ["-profile:v high", "-level:v 4.0", "-b:v 11M", "-maxrate 11M", "-c:a aac", "-b:a 256k", "-ar 48000", "-ac 2", "-r 30"]:
            self.assertIn(flag, appstore)
        self.assertTrue(any("ripple-googleplay-1080x1920.srt" in l for l in lines))
        self.assertTrue(any("ripple-landing-1920x1080-muted.webm" in l for l in lines))
        self.assertTrue(any("poster-5s.png" in l for l in lines))

    def test_srt_covers_each_caption(self):
        out = node(f"""
            import {{loadPlan, srt}} from '{BUILD.as_uri()}';
            console.log(srt(loadPlan(process.argv[1])));
        """, str(EXAMPLE))
        self.assertIn("00:00:00,200 --> 00:00:07,000\nBuild habits that stick", out)
        self.assertIn("Ripple. Small habits. Big change.", out)


@unittest.skipUnless(shutil.which("node"), "node is required")
class PreviewPageTests(unittest.TestCase):
    def test_prepare_inlines_runtime_plan_and_mock(self):
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["node", str(BUILD), "prepare", "--plan", str(EXAMPLE), "--out", tmp, "--cut", "landing"],
                           capture_output=True, text=True, check=True)
            html = Path(tmp, "preview", "landing.html").read_text()
        self.assertIn('window.CUT={"id":"landing","layout":"landing","w":1920,"h":1080}', html)
        self.assertIn("window.SCREENS = {today, streak, insights, reminders}", html)
        self.assertIn("window.seek = async function seek", html)
        self.assertNotIn("<script src=", html)


if __name__ == "__main__":
    unittest.main()
