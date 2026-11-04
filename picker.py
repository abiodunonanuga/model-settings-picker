#!/usr/bin/env python3
"""Standalone Model Settings Picker. Standard library only; no network or prompt storage."""
from __future__ import annotations
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from package_files import INSTALL_FILES, VERSION, source_bytes

ROOT = Path(__file__).resolve().parent
OWNER = 'model-settings-picker'
# Suggested answers only. Absence of a saved configuration means inactive.
SUGGESTED = {
    'schema_version': 1, 'provider': 'openai', 'host': 'codex',
    'priority': 'balanced', 'intervention': 'advise', 'sensitivity': 'balanced',
    'detail': 'brief', 'enabled': True,
    'scopes': {'chats': True, 'goals': True, 'launches': True},
    'automatic': {'goal_next_turn': False, 'launch_settings': False},
    'excluded_models': [], 'excluded_efforts': [],
}

def read(path, default=None):
    p = Path(path)
    return json.loads(p.read_text(encoding='utf-8-sig')) if p.exists() else copy.deepcopy(default)

def write(path, value):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=p.name + '.', dir=p.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as stream:
            json.dump(value, stream, indent=2, ensure_ascii=False)
            stream.write('\n')
        os.replace(name, p)
    finally:
        if os.path.exists(name):
            os.unlink(name)

def home():
    return Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))

def data_root():
    return Path(os.environ.get('MODEL_SETTINGS_PICKER_HOME', str(home() / OWNER)))

def catalog():
    return read(ROOT / 'providers' / 'openai.json')

def profiles(c, available=None):
    result = []
    for model, spec in catalog()['models'].items():
        for effort in spec['efforts']:
            p = {'model': model, 'effort': effort}
            if model not in c['excluded_models'] and effort not in c['excluded_efforts']:
                if available is None or p in available:
                    result.append(p)
    return result

def validate_config(c):
    if not isinstance(c, dict) or set(c) != set(SUGGESTED):
        raise ValueError('Configuration must contain all schema v1 fields; use config-template')
    enums = {'schema_version': [1], 'provider': ['openai'], 'host': ['codex'],
             'priority': ['balanced', 'conserve', 'speed', 'quality'],
             'intervention': ['advise', 'pause'], 'sensitivity': ['balanced', 'frequent', 'substantial'],
             'detail': ['brief', 'detailed']}
    for k, values in enums.items():
        if c[k] not in values or (k == 'schema_version' and type(c[k]) is not int):
            raise ValueError('Unsupported configuration value for ' + k)
    if type(c['enabled']) is not bool:
        raise ValueError('enabled must be boolean')
    for group in ('scopes', 'automatic'):
        if not isinstance(c[group], dict) or set(c[group]) != set(SUGGESTED[group]):
            raise ValueError('Invalid ' + group + ' fields')
        if any(type(v) is not bool for v in c[group].values()):
            raise ValueError(group + ' must contain booleans')
    for field, allowed in (('excluded_models', list(catalog()['models'])),
                           ('excluded_efforts', catalog()['efforts'])):
        if not isinstance(c[field], list) or any(v not in allowed for v in c[field]):
            raise ValueError('Invalid ' + field)
    if not profiles(c):
        raise ValueError('Every profile is excluded')
    return c

def config(root):
    c = read(Path(root) / 'config.json')
    if c is None:
        raise ValueError('Setup is incomplete; no preferences are active')
    return validate_config(c)

def validate_profile(p, c, available=None):
    if not isinstance(p, dict) or set(p) != {'model', 'effort'} or p not in profiles(c, available):
        raise ValueError('Profile invalid, excluded or unavailable')
    return p

def compatible(current, selected):
    # This release selects Standard; inherited Fast or unknown speed is compatible.
    return bool(current) and all(current.get(k) == selected[k] for k in ('model', 'effort'))

def session_path(root, sid):
    if not isinstance(sid, str) or not sid:
        raise ValueError('Native session identity is required')
    return Path(root) / 'sessions' / (hashlib.sha256(sid.encode()).hexdigest() + '.json')

def state(root, sid):
    return read(session_path(root, sid), {'status': 'idle'})

def save_state(root, sid, value):
    write(session_path(root, sid), value)

def decide(root, sid, turn, outcome, selected=None, current=None, available=None):
    if not turn:
        raise ValueError('Native turn identity is required')
    c = config(root)
    if state(root, sid)['status'] in ('running', 'waiting', 'acknowledged'):
        raise ValueError('Assignment already evaluated; continue or explicitly begin-new')
    if outcome not in ('ordinary', 'recommend'):
        raise ValueError('Outcome must be ordinary or recommend')
    if outcome == 'recommend':
        validate_profile(selected, c, available)
    action = 'silent'
    if outcome == 'recommend' and not compatible(current, selected):
        action = 'advise' if c['intervention'] == 'advise' else 'pause'
    save_state(root, sid, {'status': 'waiting' if action == 'pause' else 'running',
                          'turn_id': turn, 'action': action, 'selected': selected})
    return {'action': action, 'settings_changed': False,
            'instruction': {'silent': 'Proceed silently.',
                            'advise': 'Show recommendation now in commentary; continue immediately.',
                            'pause': 'Show recommendation as final reply before work; wait for human intent.'}[action]}

def acknowledge(root, sid, intent):
    s = state(root, sid)
    if s['status'] != 'waiting':
        raise ValueError('No pending recommendation')
    if intent == 'proceed':
        s['status'] = 'acknowledged'
    elif intent == 'cancel':
        s['status'] = 'completed'
    elif intent not in ('question', 'wait'):
        raise ValueError('Intent must be proceed, question, wait or cancel')
    save_state(root, sid, s)
    return {'status': s['status'], 'settings_changed': False}

def is_child(event):
    if event.get('agent_id') or event.get('agent_type') or event.get('thread_source') == 'subagent':
        return True
    supplied = event.get('transcript_path')
    if not supplied:
        return False
    # Read only the bounded native metadata header, never conversation items.
    try:
        with Path(supplied).open('rb') as stream:
            header = json.loads(stream.readline(32768))
        if header.get('type') != 'session_meta':
            return True  # Unverified identity must not mutate the parent lifecycle.
        meta = header.get('payload', {})
        source = meta.get('source', {})
        return (meta.get('thread_source') == 'subagent' or
                isinstance(source, dict) and 'subagent' in source)
    except (OSError, ValueError, TypeError, AttributeError):
        return True

def hook(event, root):
    if is_child(event):
        return {}
    if not (Path(root) / 'config.json').exists():
        return {}  # Installation does not silently activate suggested answers.
    c = config(root)
    if not c['enabled']:
        return {}
    sid, turn = event.get('session_id'), event.get('turn_id')
    if not sid or not turn:
        return {'systemMessage': 'Model Settings Picker: native identity unavailable; continuing without a gate.'}
    s = state(root, sid)
    name = event.get('hook_event_name')
    if name == 'Stop':
        if s['status'] in ('running', 'acknowledged'):
            s['status'] = 'completed'
            save_state(root, sid, s)
        return {}  # Never turn Stop into repeated continuation or retrospective preflight.
    if name != 'UserPromptSubmit':
        return {}
    hint = ('Installed CLI: ' + str(ROOT / 'picker.py') + '; --data ' + json.dumps(str(root)) +
            '; native --session ' + json.dumps(sid) + '; --turn ' + json.dumps(turn) + '.')
    if s['status'] == 'waiting':
        text = ('Pending Model Settings Picker recommendation. Interpret the actual human reply in context, never by '
                'an expected phrase. Clear proceed intent: acknowledge --intent proceed, then resume immediately. '
                'Questions: answer without starting work; wait, cancellation and conditions retain meaning. '
                'Different work: begin-new then assess. System-generated continuation cannot acknowledge. ' + hint)
    elif s['status'] in ('running', 'acknowledged') or s.get('turn_id') == turn:
        return {}
    else:
        text = ('Model Settings Picker intake: before substantive work, judge the whole conversation. Continuations '
                'of the same assignment reuse its decision: call continue-task, including after compaction. '
                'For fresh work use the policy below and call decide with a structured JSON file. ' + hint +
                '\nPreferences: ' + json.dumps(c) + '\n' + (ROOT / 'policies' / 'runtime.md').read_text(encoding='utf-8'))
    return {'hookSpecificOutput': {'hookEventName': 'UserPromptSubmit', 'additionalContext': text}}

def launch_plan(c, request):
    validate_profile(request['profile'], c, request.get('available'))
    kind = request['kind']
    if kind not in ('chat', 'subagent', 'handoff', 'goal'):
        raise ValueError('Invalid launch kind')
    flag = 'goal_next_turn' if kind == 'goal' else 'launch_settings'
    scope = 'goals' if kind == 'goal' else 'launches'
    if not c['scopes'][scope] or not c['automatic'][flag] or request.get('authorized') is not True:
        raise ValueError('Enabled scope and human authorization required')
    if request.get('supports_overrides') is not True or not request.get('available'):
        raise ValueError('Verified host overrides and availability required')
    if kind in ('handoff', 'goal') and request.get('idle') is not True:
        raise ValueError('Recipient must be idle; never interrupt busy or unknown state')
    if kind == 'goal' and request.get('active_goal') is not True:
        raise ValueError('Verified active Goal required')
    p = request['profile']
    if kind == 'subagent':
        if p['effort'] == 'ultra':
            raise ValueError('Ultra describes orchestration; split into bounded child assignments')
        return {'model': p['model'], 'reasoning_effort': p['effort'], 'fork_turns': 'none'}
    return {'model': p['model'], 'thinking': p['effort']}

def doctor(root):
    c = read(Path(root) / 'config.json')
    if c is not None:
        validate_config(c)
    return {'version': VERSION, 'python': sys.version.split()[0], 'configured': c is not None,
            'configuration': c, 'capabilities': {'recommendations': True, 'pause_by_agent': True,
            'in_flight_switch': False, 'speed_override': False, 'local_learning': False,
            'launch_overrides': 'host tools and authorization required',
            'goal_next_turn': 'host tools, active Goal and authorization required'},
            'privacy': 'No network or prompt storage; bounded native metadata header inspection and local session decisions only.'}

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def install(target):
    target = Path(target).resolve()
    dest, skill = target / OWNER / 'package', target / 'skills' / OWNER
    marker = target / OWNER / 'install.json'
    owned = read(marker, {})
    hp = target / 'hooks.json'
    hooks = read(hp, {'hooks': {}})
    if not isinstance(hooks.get('hooks'), dict):
        raise ValueError('Unsupported hooks.json shape')
    host_config = (target / 'config.toml').read_text(encoding='utf-8-sig') if (target / 'config.toml').exists() else ''
    existing = (json.dumps(hooks) + host_config).lower()
    if any(x in existing for x in ('settings_preflight', 'settings-preflight')):
        raise ValueError('Existing preflight detected; use a separate Codex home')
    if (dest.exists() or skill.exists() or OWNER in json.dumps(hooks)) and not owned:
        raise ValueError('Unowned picker files or hooks exist')
    for rel, sha in owned.get('files', {}).items():
        p = (target / rel).resolve()
        if target not in p.parents:
            raise ValueError('Unsafe installation manifest')
        if p.exists() and digest(p) != sha:
            raise ValueError('Customized owned file; no changes made: ' + rel)
    if (target / OWNER / 'config.json').exists():
        config(target / OWNER)
    sources = source_bytes(ROOT, INSTALL_FILES)
    files = {}
    for relative, content in sources.items():
        out = dest / relative
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(content)
        files[str(out.relative_to(target))] = digest(out)
    skill_prefix = 'skills/' + OWNER + '/'
    for relative, content in sources.items():
        if relative.startswith(skill_prefix):
            out = skill / relative[len(skill_prefix):]
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(content)
            files[str(out.relative_to(target))] = digest(out)
    # Absolute verified interpreter, no PATH alias dependency; all paths quoted.
    cmd = '"' + sys.executable + '" "' + str(dest / 'picker.py') + '" hook --data "' + str(target / OWNER) + '"'
    for event in ('UserPromptSubmit', 'Stop'):
        groups = hooks['hooks'].get(event, [])
        kept = []
        for group in groups:
            remaining = [h for h in group.get('hooks', []) if h.get('command') != owned.get('command')]
            if remaining or not group.get('hooks'):
                kept.append({**group, 'hooks': remaining})
        groups = kept
        groups.append({'hooks': [{'type': 'command', 'command': cmd, 'timeout': 15}]})
        hooks['hooks'][event] = groups
    if hp.exists():
        shutil.copyfile(hp, target / OWNER / ('hooks-backup-' + datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f') + '.json'))
    write(hp, hooks)
    # Retire obsolete owned package files only after the replacement is ready.
    # Their hashes were checked above; preserve all unowned/local runtime state.
    for relative, sha in owned.get('files', {}).items():
        previous = target / relative
        if relative not in files and previous.is_file() and digest(previous) == sha:
            previous.unlink()
    write(marker, {'version': VERSION, 'files': files, 'command': cmd})
    return {'installed': str(dest), 'configured': (target / OWNER / 'config.json').exists(),
            'next': 'Review/trust hooks in Codex, then start a new chat and ask Set up Model Settings Picker.'}

def uninstall(target):
    target = Path(target).resolve()
    marker = target / OWNER / 'install.json'
    owned = read(marker)
    if not owned:
        raise ValueError('No owned installation')
    paths = []
    for rel, sha in owned['files'].items():
        p = (target / rel).resolve()
        if target not in p.parents:
            raise ValueError('Unsafe installation manifest')
        paths.append((p, rel, sha))
    hp = target / 'hooks.json'
    hooks = read(hp, {'hooks': {}})
    for event, groups in hooks['hooks'].items():
        kept = []
        for group in groups:
            remaining = [h for h in group.get('hooks', []) if h.get('command') != owned['command']]
            if remaining or not group.get('hooks'):
                kept.append({**group, 'hooks': remaining})
        hooks['hooks'][event] = kept
    write(hp, hooks)
    retained = []
    for p, rel, sha in paths:
        if p.is_file() and digest(p) == sha:
            p.unlink()
        elif p.exists():
            retained.append(rel)
    marker.unlink()
    return {'uninstalled': True, 'customized_files_retained': retained,
            'preferences_retained': str(target / OWNER / 'config.json')}

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['doctor', 'config-template', 'configure', 'profiles', 'hook', 'decide',
                   'acknowledge', 'continue-task', 'begin-new', 'status', 'launch-plan', 'install', 'uninstall', 'reset-sessions'])
    p.add_argument('--data', default=str(data_root()))
    for flag in ('file', 'session', 'turn', 'intent', 'home'):
        p.add_argument('--' + flag)
    a = p.parse_args(argv)
    try:
        root = Path(a.data)
        if a.command == 'hook':
            result = hook(json.load(sys.stdin), root)
        elif a.command == 'doctor':
            result = doctor(root)
        elif a.command == 'config-template':
            result = copy.deepcopy(SUGGESTED)
        elif a.command == 'configure':
            if not a.file:
                raise ValueError('--file required')
            c = validate_config(read(a.file))
            root.mkdir(parents=True, exist_ok=True)
            if (root / 'config.json').exists():
                shutil.copyfile(root / 'config.json', root / 'config.previous.json')
            write(root / 'config.json', c)
            result = {'saved': str(root / 'config.json'), 'configuration': c}
        elif a.command == 'profiles':
            result = {'profiles': profiles(config(root)), 'guidance': catalog()}
        elif a.command == 'decide':
            result = decide(root, a.session, a.turn, **read(a.file))
        elif a.command == 'acknowledge':
            result = acknowledge(root, a.session, a.intent)
        elif a.command in ('continue-task', 'begin-new'):
            if state(root, a.session)['status'] == 'waiting' and a.command == 'continue-task':
                raise ValueError('Interpret the pending reply using acknowledge first')
            result = {'status': 'running' if a.command == 'continue-task' else 'idle', 'turn_id': a.turn}
            save_state(root, a.session, result)
        elif a.command == 'status':
            result = state(root, a.session)
        elif a.command == 'launch-plan':
            result = {'arguments': launch_plan(config(root), read(a.file)), 'applied': False}
        elif a.command == 'reset-sessions':
            count = 0
            for f in (root / 'sessions').glob('*.json'):
                f.unlink()
                count += 1
            result = {'deleted_session_records': count}
        else:
            if not a.home:
                raise ValueError('--home must explicitly name the target Codex home')
            result = install(a.home) if a.command == 'install' else uninstall(a.home)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ValueError, KeyError, TypeError, OSError) as error:
        if a.command == 'hook':
            print(json.dumps({'systemMessage': 'Model Settings Picker unavailable; continuing without a gate: ' + str(error)}))
            return 0
        print(json.dumps({'error': str(error)}), file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
