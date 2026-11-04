import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import package_files
import picker

ROOT = Path(__file__).resolve().parents[1]


class NativePluginTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='picker native ')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)

    def stage(self):
        path = self.base / 'marketplace with spaces'
        picker.stage_plugin(path)
        return path

    def test_native_identity_hooks_onboarding_and_marketplace(self):
        manifest = picker.read(ROOT / 'plugin.json')
        compat = picker.read(ROOT / '.codex-plugin/plugin.json')
        market = picker.read(ROOT / '.agents/plugins/marketplace.json')
        self.assertEqual(manifest['version'], package_files.VERSION)
        self.assertEqual(compat['version'], package_files.VERSION)
        self.assertEqual(manifest['name'], picker.OWNER)
        self.assertEqual(market['plugins'][0]['source']['path'], './')
        extension = manifest['extensions']['com.openai']
        for key in ('hooks', 'onboardingSkill'):
            self.assertTrue((ROOT / extension[key]).is_file())
        hooks = picker.read(ROOT / extension['hooks'])['hooks']
        self.assertEqual(set(hooks), {'UserPromptSubmit', 'Stop'})
        for groups in hooks.values():
            self.assertIn('commandWindows', groups[0]['hooks'][0])

    def test_staging_exact_allowlist_and_no_global_installation(self):
        source = self.base / 'source'
        for name in package_files.PLUGIN_FILES:
            p = source / name
            p.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, p)
        (source / '.env').write_text('private dummy')
        with patch.object(picker, 'ROOT', source):
            staged = self.stage()
        self.assertEqual({p.relative_to(staged).as_posix() for p in staged.rglob('*') if p.is_file()}, set(package_files.PLUGIN_FILES))
        self.assertFalse((self.base / 'hooks.json').exists())
        self.assertFalse((self.base / 'skills').exists())
        self.assertFalse((staged / 'config.json').exists())

    def test_stage_refuses_existing_destination(self):
        target = self.stage()
        before = (target / 'plugin.json').read_bytes()
        with self.assertRaises(ValueError):
            picker.stage_plugin(target)
        self.assertEqual((target / 'plugin.json').read_bytes(), before)

    def test_stage_cannot_write_inside_source(self):
        with self.assertRaises(ValueError):
            picker.stage_plugin(ROOT / 'accidental-stage')

    def test_preferences_live_outside_plugin_cache(self):
        with patch.dict(os.environ, {'CODEX_HOME': str(self.base), 'PLUGIN_DATA': str(self.base / 'cache-data')}, clear=True):
            self.assertEqual(picker.data_root(), self.base / picker.OWNER)
        with patch.dict(os.environ, {'MODEL_SETTINGS_PICKER_HOME': str(self.base / 'custom')}, clear=True):
            self.assertEqual(picker.data_root(), self.base / 'custom')

    def wrapper(self, stage):
        if os.name == 'nt':
            executable = shutil.which('powershell.exe')
            if not executable:
                self.skipTest('Windows PowerShell unavailable')
            return [executable, '-NoProfile', '-File', str(stage / 'hooks/run-hook.ps1')]
        executable = shutil.which('sh')
        if not executable:
            self.skipTest('POSIX sh unavailable')
        return [executable, str(stage / 'hooks/run-hook.sh')]

    def test_native_hook_wrapper_receives_stdin_and_stable_preferences(self):
        stage = self.stage()
        env = {**os.environ, 'CODEX_HOME': str(self.base / 'codex-home'), 'MODEL_SETTINGS_PICKER_PYTHON': sys.executable}
        env.pop('MODEL_SETTINGS_PICKER_HOME', None)
        event = json.dumps({'hook_event_name': 'UserPromptSubmit', 'session_id': 's', 'turn_id': 't'})
        first = subprocess.run(self.wrapper(stage), input=event, text=True, capture_output=True, env=env)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(json.loads(first.stdout), {})
        data = Path(env['CODEX_HOME']) / picker.OWNER
        picker.write(data / 'config.json', picker.SUGGESTED)
        second = subprocess.run(self.wrapper(stage), input=event, text=True, capture_output=True, env=env)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn('additionalContext', json.loads(second.stdout)['hookSpecificOutput'])

    def test_missing_explicit_runtime_fails_open(self):
        stage = self.stage()
        env = {**os.environ, 'MODEL_SETTINGS_PICKER_PYTHON': str(self.base / 'missing-python')}
        result = subprocess.run(self.wrapper(stage), input='{}', text=True, capture_output=True, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('systemMessage', json.loads(result.stdout))

    def test_legacy_removal_preserves_other_hooks_modified_files_and_preferences(self):
        target = self.base / 'legacy-home'
        owned = target / picker.OWNER / 'package' / 'old.py'
        owned.parent.mkdir(parents=True)
        owned.write_text('old')
        modified = owned.with_name('custom.py')
        modified.write_text('custom')
        rel = str(owned.relative_to(target))
        modified_rel = str(modified.relative_to(target))
        command = 'legacy-picker-command'
        picker.write(target / picker.OWNER / 'install.json', {'command': command, 'files': {rel: picker.digest(owned), modified_rel: 'not-the-current-hash'}})
        picker.write(target / picker.OWNER / 'config.json', picker.SUGGESTED)
        picker.write(target / 'hooks.json', {'hooks': {'Stop': [{'hooks': [{'command': command}, {'command': 'unrelated'}]}]}})
        result = picker.uninstall(target)
        self.assertFalse(owned.exists())
        self.assertTrue(modified.exists())
        self.assertIn(modified_rel, result['customized_files_retained'])
        self.assertEqual(picker.read(target / picker.OWNER / 'config.json'), picker.SUGGESTED)
        self.assertEqual(picker.read(target / 'hooks.json')['hooks']['Stop'][0]['hooks'], [{'command': 'unrelated'}])

    @unittest.skipUnless(os.environ.get('MODEL_SETTINGS_PICKER_CODEX'), 'Optional native Codex CLI integration')
    def test_real_native_plugin_install_list_remove_preserves_global_files(self):
        executable = os.environ['MODEL_SETTINGS_PICKER_CODEX']
        self.assertTrue(Path(executable).is_file())
        help_result = subprocess.run([executable, 'plugin', '--help'], capture_output=True, text=True)
        self.assertEqual(help_result.returncode, 0)
        self.assertIn('Install a plugin', help_result.stdout)
        stage = self.stage()
        target = self.base / 'native-home'
        picker.write(target / 'hooks.json', {'hooks': {'Stop': []}})
        (target / 'AGENTS.md').write_text('preserve these instructions')
        original = {name: (target / name).read_bytes() for name in ('hooks.json', 'AGENTS.md')}
        env = {**os.environ, 'CODEX_HOME': str(target)}
        def cli(*args):
            r = subprocess.run([executable, *args], capture_output=True, text=True, env=env)
            self.assertEqual(r.returncode, 0, r.stderr)
            return r.stdout
        cli('plugin', 'marketplace', 'add', str(stage))
        installed = json.loads(cli('plugin', 'add', picker.OWNER + '@' + picker.OWNER, '--json'))
        cache = Path(installed['installedPath'])
        self.assertEqual(installed['version'], package_files.VERSION)
        for name in package_files.PLUGIN_FILES:
            self.assertEqual((cache / name).read_bytes(), (stage / name).read_bytes(), name)
        listed = json.loads(cli('plugin', 'list', '--marketplace', picker.OWNER, '--json'))
        self.assertTrue(any(p['name'] == picker.OWNER and p['enabled'] for p in listed['installed']))
        preferences = target / picker.OWNER / 'config.json'
        picker.write(preferences, picker.SUGGESTED)
        cli('plugin', 'add', picker.OWNER + '@' + picker.OWNER, '--json')
        self.assertEqual(picker.read(preferences), picker.SUGGESTED)
        cli('plugin', 'remove', picker.OWNER + '@' + picker.OWNER, '--json')
        self.assertEqual(picker.read(preferences), picker.SUGGESTED)
        for name, body in original.items():
            self.assertEqual((target / name).read_bytes(), body)
        self.assertFalse((target / 'skills' / picker.OWNER).exists())


if __name__ == '__main__':
    unittest.main()
