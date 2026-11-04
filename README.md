# Model Settings Picker

An independent local OpenAI/Codex settings recommendation package. Version 0.1.0.
It has no dependency on personal workflows, employer policy, memories or another
preflight repository. No account credentials, API calls or telemetry are used.

## Install

Requires Python 3.10+ and a Codex version supporting command hooks and local skills.
Verify Python is available before using the commands. From this source directory:

```text
python picker.py install --home <your-target-Codex-home>
```

Use `~/.codex` or the actual CODEX_HOME path, expanding `~` in your shell. The target
is explicit to avoid accidentally changing another installation. Existing preflight
hooks cause a refusal; use a separate Codex home for evaluation. Existing unrelated
hooks are preserved. Review/trust the new hooks through Codex's supported controls.
Start a new chat and ask **Set up Model Settings Picker**. Installation alone
leaves the picker inactive. The conversation explains each preference, obtains
choices, shows a review, and saves configuration. Reconfigure later with
**Reconfigure Model Settings Picker**. No special acknowledgement phrase is needed.

Setup supports priority, intervention, scope, supported automatic permissions,
sensitivity, explanation detail and model/effort exclusions. Suggested answers are
not active settings until setup is completed. No default model is selected.

## Behavior

**Advise and continue:** an initial recommendation appears in commentary and work
continues. You may stop, change settings and resume. **Pause for your decision:**
the agent returns a final recommendation before work and waits for ordinary human
intent. Matching settings proceed silently. Continuations do not repeat preflight.
The hook supplies instructions; the host agent performs semantic task assessment
and respects pause behavior. This is not a hard execution security boundary.

The picker cannot switch an in-flight response or change speed. Parent launches
can supply model/reasoning when tools and human authority allow. Goal adaptation
is conditional next-turn routing, not an unconditional self-switch capability.
The launch-plan CLI validates arguments; the host agent executes them and verifies
readback. Busy or unknown-state chat recipients are never interrupted.

## Configuration and diagnostics

```text
python picker.py doctor
python picker.py config-template
python picker.py configure --file choices.json
python picker.py profiles
python picker.py status --session <native-session-id>
python picker.py reset-sessions
python picker.py uninstall --home <your-target-Codex-home>
```

State lives in `<CODEX_HOME>/model-settings-picker`, falling back to `~/.codex`.
MODEL_SETTINGS_PICKER_HOME or --data can select independent runtime storage.
The installer pins its hook to its target home. Sessions contain only lifecycle,
turn ID and selected model/effort, keyed by a hash of the session ID. The hook
inspects only a bounded native transcript metadata header to identify child
agents; it does not read conversation items. Unknown identity is bypassed safely.
Reset removes
those records. Configuration and its previous version remain until you remove
them. Uninstall preserves preferences, backups, unrelated hooks and modified files.
Reinstall preserves preferences and refuses customized owned code. Review such
customizations before upgrading; never overwrite them silently.

## Provider and host boundaries

providers/openai.json defines starter profiles and routing guidance; picker.py is
the Codex adapter plus lifecycle/configuration controls. Anthropic and Google are
future separate providers, not aliases for OpenAI reasoning levels. Only OpenAI
is accepted by this configuration schema. Current profiles are heuristics, not
benchmarks or proof of account access. Exposed host availability controls launches.
No cross-provider routing, automatic model discovery API, local learning, general
maintenance automation, authenticated handoff receipts or public-directory listing
is included. A host agent can inspect its exposed model tools during setup.

## Development and release

```text
python -m unittest discover -s tests -v
python build_release.py --output <directory-outside-source>
```

The source is designed to use Python on Windows/macOS/Linux; CI is provided for
all three. Local verification covers Windows. Native conversational UX and host
tool capabilities still depend on the installed Codex version.

This is a fresh implementation. No source from the private EPR package is bundled.
See LICENSE for reuse terms. Public hosting/publishing is a separate action.
The release builder produces a source ZIP and per-file SHA-256 manifest.

Official event protocol: https://learn.chatgpt.com/docs/hooks
