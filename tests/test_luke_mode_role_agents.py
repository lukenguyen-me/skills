"""Verify role_agents.py generates role agents and its hook enforces the profile."""

from pathlib import Path
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills' / 'luke-mode'
SCRIPT = SKILL / 'scripts' / 'role_agents.py'

spec = importlib.util.spec_from_file_location('role_agents', SCRIPT)
role_agents = importlib.util.module_from_spec(spec)
spec.loader.exec_module(role_agents)

PROFILE = """# Luke Mode models

## Codex

| Role | Model | Reasoning effort | Fallback |
| --- | --- | --- | --- |
| Reasoning | gpt-5 | high | stop |
| Coding | gpt-5 | medium | stop |
| Verifier | gpt-5 | medium | stop |
| Explorer | gpt-5-mini | low | stop |
| Reviewer | gpt-5 | high | stop |

## Claude Code

| Role | Model | Reasoning effort | Fallback |
| --- | --- | --- | --- |
| Reasoning | opus | inherit | stop |
| Coding | sonnet | high | stop |
| Verifier | sonnet | inherit | stop |
| Explorer | haiku | inherit | stop |
| Reviewer | opus | inherit | stop |
"""


def run(*args, stdin=None):
    return subprocess.run([sys.executable, str(SCRIPT), *args], input=stdin,
                          capture_output=True, text=True)


class RoleAgentsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.home = self.tmp / 'home'
        # check reads ~/.claude/agents for overrides; keep it off the real home.
        patcher = mock.patch.dict(os.environ, {'HOME': str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.models = self.home / '.config' / 'luke-mode' / 'models.md'
        self.models.parent.mkdir(parents=True)
        self.models.write_text(PROFILE)
        self.agents = self.home / '.claude' / 'agents'
        self.repo = self.tmp / 'repo'
        self.repo.mkdir()
        subprocess.run(['git', 'init', '--quiet', str(self.repo)], check=True)

    def write_agents(self, *extra):
        result = run('write', '--models', str(self.models), '--dest', str(self.agents), *extra)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def decide(self, **tool_input):
        return role_agents.decide(tool_input, str(self.repo), self.home)

    def test_parse_reads_only_the_claude_code_profile(self):
        profile = role_agents.parse_profile(PROFILE)
        self.assertEqual(profile['Coding'], ('sonnet', 'high'))
        self.assertEqual(profile['Explorer'], ('haiku', 'inherit'))
        self.assertEqual(profile['Verifier'], ('sonnet', 'inherit'))
        self.assertIsNone(role_agents.parse_profile(PROFILE.split('## Claude Code')[0]))

    def test_parse_rejects_a_profile_missing_a_role(self):
        with self.assertRaises(role_agents.ProfileError):
            role_agents.parse_profile(PROFILE.replace('| Explorer | haiku | inherit | stop |\n', ''))

    def test_parse_points_a_worker_profile_to_setup(self):
        legacy = PROFILE.replace('| Verifier | sonnet | inherit | stop |\n| Explorer |', '| Worker |')
        with self.assertRaisesRegex(role_agents.ProfileError, 'Verifier, Explorer.*Worker role is retired'):
            role_agents.parse_profile(legacy)

    def test_write_pins_model_effort_and_tools(self):
        self.write_agents()
        coding = (self.agents / 'luke-coding.md').read_text()
        self.assertIn('name: luke-coding\n', coding)
        self.assertIn('model: sonnet\n', coding)
        self.assertIn('effort: high\n', coding)
        self.assertIn('disallowedTools: Agent\n', coding)
        explorer = (self.agents / 'luke-explorer.md').read_text()
        self.assertIn('model: haiku\n', explorer)
        self.assertNotIn('effort:', explorer)
        self.assertIn('tools: Read, Grep, Glob, Bash\n', explorer)
        verifier = (self.agents / 'luke-verifier.md').read_text()
        self.assertIn('model: sonnet\n', verifier)
        self.assertIn('disallowedTools: Agent, Edit, Write, NotebookEdit\n', verifier)
        self.assertEqual(run('check', '--models', str(self.models), '--dest', str(self.agents)).returncode, 0)

    def test_check_reports_drift_after_the_profile_changes(self):
        self.write_agents()
        self.models.write_text(PROFILE.replace('| Coding | sonnet |', '| Coding | opus |'))
        result = run('check', '--models', str(self.models), '--dest', str(self.agents))
        self.assertEqual(result.returncode, 1)
        self.assertIn('luke-coding.md', result.stdout)

    def test_write_leaves_a_hand_written_agent_until_forced(self):
        self.agents.mkdir(parents=True)
        (self.agents / 'luke-coding.md').write_text('---\nname: luke-coding\n---\nmine\n')
        result = run('write', '--models', str(self.models), '--dest', str(self.agents))
        self.assertEqual(result.returncode, 2)
        self.assertIn('mine', (self.agents / 'luke-coding.md').read_text())
        self.assertFalse((self.agents / 'luke-explorer.md').exists())
        self.write_agents('--force')
        self.assertIn('model: sonnet', (self.agents / 'luke-coding.md').read_text())

    def test_hook_allows_everything_without_a_claude_code_profile(self):
        self.models.write_text(PROFILE.split('## Claude Code')[0])
        self.assertIsNone(self.decide(subagent_type='general-purpose'))
        self.models.unlink()
        self.assertIsNone(self.decide(subagent_type='fork'))

    def test_hook_routes_to_installed_role_agents(self):
        self.write_agents()
        self.assertIsNone(self.decide(subagent_type='luke-coding'))
        self.assertIsNone(self.decide(subagent_type='luke-coding', model='sonnet'))
        self.assertIn('luke-coding', self.decide(subagent_type='general-purpose', model='sonnet'))
        self.assertIn('luke-coding', self.decide(description='no type given'))
        self.assertIn('fork', self.decide(subagent_type='fork'))
        self.assertIn('Omit the model', self.decide(subagent_type='luke-coding', model='opus'))

    def test_hook_blocks_role_agents_that_drift_from_the_profile(self):
        self.write_agents()
        self.models.write_text(PROFILE.replace('| Explorer | haiku |', '| Explorer | sonnet |'))
        self.assertIn('/luke-mode setup', self.decide(subagent_type='luke-explorer'))

    def test_write_removes_the_generated_worker_agent(self):
        self.agents.mkdir(parents=True)
        worker = self.agents / 'luke-worker.md'
        worker.write_text(role_agents.render('Explorer', 'haiku', 'inherit').replace('explorer', 'worker'))
        result = run('check', '--models', str(self.models), '--dest', str(self.agents))
        self.assertIn('luke-worker.md: the Worker role is retired', result.stdout)
        self.write_agents()
        self.assertFalse(worker.exists())
        self.assertEqual(run('check', '--models', str(self.models), '--dest', str(self.agents)).returncode, 0)
        self.assertIn('outside the roster', self.decide(subagent_type='luke-worker'))

    def test_write_keeps_a_hand_written_worker_agent(self):
        self.agents.mkdir(parents=True)
        (self.agents / 'luke-worker.md').write_text('---\nname: luke-worker\n---\nmine\n')
        self.write_agents()
        self.assertTrue((self.agents / 'luke-worker.md').exists())

    def test_hook_fallback_needs_a_profile_model_while_agents_are_missing(self):
        self.assertIsNone(self.decide(subagent_type='general-purpose', model='sonnet'))
        self.assertIsNone(self.decide(subagent_type='Explore', model='haiku'))
        self.assertIn('/luke-mode setup', self.decide(subagent_type='general-purpose'))
        self.assertIn('/luke-mode setup', self.decide(subagent_type='Explore', model='fable'))

    def test_repository_profile_and_agents_take_precedence(self):
        self.write_agents()
        repo_models = self.repo / '.luke-mode' / 'models.md'
        repo_models.parent.mkdir()
        repo_models.write_text(PROFILE.replace('| Coding | sonnet |', '| Coding | opus |'))
        # Personal agents pin sonnet, so they disagree with the repository profile.
        self.assertIn(str(repo_models), self.decide(subagent_type='luke-coding'))
        result = run('write', '--models', str(repo_models), '--dest', str(self.repo / '.claude' / 'agents'))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIsNone(self.decide(subagent_type='luke-coding'))

    def test_hook_command_prints_a_deny_decision(self):
        payload = {'tool_name': 'Agent', 'cwd': str(self.repo),
                   'tool_input': {'subagent_type': 'fork', 'prompt': 'x', 'description': 'x'}}
        result = subprocess.run([sys.executable, str(SCRIPT), 'hook'], input=json.dumps(payload),
                                capture_output=True, text=True, env={'HOME': str(self.home), 'PATH': '/usr/bin:/bin'})
        self.assertEqual(result.returncode, 0, result.stderr)
        decision = json.loads(result.stdout)['hookSpecificOutput']
        self.assertEqual(decision['permissionDecision'], 'deny')
        self.assertIn('fork', decision['permissionDecisionReason'])

    def test_parse_tolerates_formatting_in_cells(self):
        text = PROFILE.replace('| Coding | sonnet | high |', '| **Coding** | `Sonnet` |  |')
        self.assertEqual(role_agents.parse_profile(text)['Coding'], ('sonnet', 'inherit'))

    def test_hook_denies_an_effort_override_on_a_role_agent(self):
        self.write_agents()
        self.assertIsNone(self.decide(subagent_type='luke-coding', effort='high'))
        self.assertIn('Omit the effort', self.decide(subagent_type='luke-coding', effort='low'))
        self.assertIn('Omit the effort', self.decide(subagent_type='luke-explorer', effort='low'))

    def test_hook_fallback_lets_an_inherit_role_omit_the_model(self):
        self.models.write_text(PROFILE.replace('| Reasoning | opus |', '| Reasoning | inherit |'))
        self.assertIsNone(self.decide(subagent_type='Plan'))

    def test_check_reports_a_project_agent_that_overrides_the_personal_one(self):
        self.write_agents()
        project_agents = self.repo / '.claude' / 'agents'
        project_agents.mkdir(parents=True)
        (project_agents / 'luke-coding.md').write_text('---\nname: luke-coding\nmodel: haiku\n---\n')
        result = subprocess.run([sys.executable, str(SCRIPT), 'check', '--models', str(self.models),
                                 '--dest', str(self.agents), '--cwd', str(self.repo)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn(str(project_agents / 'luke-coding.md'), result.stdout)

    def test_hook_reads_agents_from_the_session_project_not_the_shell_cwd(self):
        payload = {'tool_name': 'Agent', 'cwd': str(self.tmp),
                   'tool_input': {'subagent_type': 'general-purpose', 'prompt': 'x', 'description': 'x'}}
        env = {'HOME': str(self.home), 'PATH': '/usr/bin:/bin', 'CLAUDE_PROJECT_DIR': str(self.repo)}
        repo_models = self.repo / '.luke-mode' / 'models.md'
        repo_models.parent.mkdir()
        repo_models.write_text(PROFILE.split('## Claude Code')[0])  # Repository file without a profile.
        result = subprocess.run([sys.executable, str(SCRIPT), 'hook'], input=json.dumps(payload),
                                capture_output=True, text=True, env=env)
        self.assertEqual(result.stdout, '')

    def test_hook_skips_quietly_on_bad_input(self):
        for stdin in ('', 'not json', json.dumps({'tool_name': 'Read'})):
            result = run('hook', stdin=stdin)
            with self.subTest(stdin=stdin):
                self.assertEqual(result.returncode, 0)
                self.assertEqual(result.stdout, '')

    def test_skill_registers_the_hook(self):
        frontmatter = (SKILL / 'SKILL.md').read_text().split('\n---', 1)[0]
        self.assertIn('matcher: Agent', frontmatter)
        self.assertIn('scripts/role_agents.py" hook', frontmatter)


if __name__ == '__main__':
    unittest.main()
