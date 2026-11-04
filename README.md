# Model Settings Picker

An independent local OpenAI/Codex settings recommendation package. Version 0.1.1.
It has no dependency on personal workflows, employer policy, memories or another
preflight repository. No account credentials, API calls or telemetry are used.

## Install through Codex (recommended)

Paste this into a Codex chat that can access your local files and terminal:

> Install Model Settings Picker from https://github.com/abiodunonanuga/model-settings-picker on this computer. Read its README and INSTALL.md, inspect the installer, and check compatibility and dependencies before running it. Preserve my existing configuration and explain conflicts before making changes. Then guide me through setup and save my chosen preferences.

Codex handles fetching the package, checking Python and the target installation,
and running the installer. It then walks you through priorities, intervention
style, scope and advanced choices. It reviews the choices with you before saving.
Installation alone leaves the picker inactive. No special acknowledgement phrase
is required. Suggested answers are not active settings before setup is saved.

You may still need to approve local changes, review/trust the new hooks, or restart
Codex and start a new chat. Codex should explain the exact remaining step. When
needed, start that chat with **Set up Model Settings Picker**. A chat without
local terminal access can guide you but cannot install onto your computer.

The installing agent follows [INSTALL.md](INSTALL.md). Requires Python 3.10+ and
a Codex version supporting command hooks and local skills. Existing preflight
installations are not silently replaced or combined. Your preferences and runtime
state stay on your computer; do not upload them with the source package.

## Manual alternative

Download and extract the latest source ZIP from
[Releases](https://github.com/abiodunonanuga/model-settings-picker/releases/latest).
Verify Python is available, then run from the extracted source directory:

```text
python picker.py install --home <your-target-Codex-home>
```

Use `~/.codex` or the actual CODEX_HOME path, expanding `~` in your shell. The target
is explicit to avoid accidentally changing another installation. Existing preflight
hooks cause a refusal; use a separate Codex home for evaluation. Existing unrelated
hooks are preserved. Review/trust the new hooks through Codex's supported controls.
Start a new chat and ask **Set up Model Settings Picker**. Reconfigure later with
**Reconfigure Model Settings Picker**.

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
The release builder produces a source ZIP and per-file SHA-256 manifest using the
explicit reviewed file lists in package_files.py. The installer uses the same
boundary with a smaller runtime list. Unlisted files (including .env files,
private JSON, virtual environments and local state) are never selected. Listed
files must exist and be regular files; symbolic links, linked parent directories
and Windows reparse points are rejected before output is written. This prevents
accidental extra-file inclusion; review remains necessary for secrets mistakenly
written into an intentionally distributed source file. Adding a source file
requires an intentional manifest update and review.

Official event protocol: https://learn.chatgpt.com/docs/hooks
