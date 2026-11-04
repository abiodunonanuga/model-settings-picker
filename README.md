# Model Settings Picker

A native Codex plugin for OpenAI model/reasoning recommendations. Version 0.1.1.
It includes conversational setup and configurable preflight behavior, with no
personal workflow dependency, credentials, API calls or telemetry.

## Install through Codex (recommended)

Paste this into a Codex chat with local files and terminal access:

> Install Model Settings Picker from https://github.com/abiodunonanuga/model-settings-picker as a native Codex plugin. Read README.md and INSTALL.md, inspect the code and check compatibility before running anything. Preserve my existing configuration and explain conflicts first. Use the reviewed file manifest to stage the plugin, register its marketplace with Codex, then guide me through setup and save my chosen preferences.

Codex handles fetching a reviewed version, verifying Python 3.10+, staging only
approved files, and installing through its plugin controls. You may need to
approve local changes, review/trust bundled hooks, or restart/start a new chat.
The plugin appears in Codex's plugin manager for enable/disable/removal. It does
not add global hooks.json entries or copy a separate global skill. Setup is
available through the plugin's onboarding action or by asking **Set up Model
Settings Picker**. Reconfigure later with **Reconfigure Model Settings Picker**.

Installation is inactive until you choose preferences and authorize saving them.
Setup covers priorities, **Advise and continue** or **Pause for your decision**,
ordinary chats/Goals/launch scope, supported automatic permissions, sensitivity,
explanation detail and exclusions. Suggested answers never silently activate.

[INSTALL.md](INSTALL.md) is the installing agent's guide. Existing preflight
installations must not be silently replaced or combined. Lifecycle-hook plugins
use repository/local marketplaces; they are not eligible for the universal
public directory. Native packaging does not mean public-directory listing.

## Manual native-plugin alternative

Download/extract a reviewed release, verify Python 3.10+ and a compatible Codex
CLI, then run from the source directory (quote paths for your shell):

```text
python picker.py stage-plugin --output <new-directory-outside-source>
codex plugin marketplace add <staged-directory>
codex plugin add model-settings-picker@model-settings-picker --json
codex plugin list --marketplace model-settings-picker --json
```

The desktop plugin browser can install from the registered marketplace instead.
Review/trust hooks through supported Codex controls, then invoke plugin setup.
If the CLI lacks these commands, use supported app controls or update Codex with
permission; do not fall back to installing global hooks. Command availability
and runtime control support depend on the installed Codex version.

For updates, stage a new reviewed version and reconcile the existing marketplace
source through native controls before reinstall/refresh. Do not edit cached plugin
files. Native removal disables/removes packaged hooks and skills; local picker
preferences remain outside the versioned cache until you explicitly delete them.

## Migrating the old custom installation

Version 0.1.0 used a custom installer. Before native installation, inspect that
home's model-settings-picker/install.json, back up choices, and ask the user to
resolve customized-file conflicts. With migration authorized, run:

```text
python picker.py uninstall-legacy --home <actual-Codex-home>
```

This removes only legacy owned, hash-matching files and matching global hook
commands. It retains preferences, backups and modified files. Confirm global
picker hooks/skills are no longer active before enabling the native plugin.
Never remove another preflight system automatically.

## Behavior and local data

Advise mode shows an initial recommendation and continues. Pause mode returns a
final recommendation before work and waits for natural human intent. Matching
settings and ordinary work proceed silently; continuations do not repeat intake.
The agent performs semantic selection; this is not a security execution boundary.

No in-flight response/model switch or speed override is supported. Optional
Goal next-turn and parent launch settings depend on actual host tools and human
authority. launch-plan returns arguments without executing them. Verify native
settings readback before claiming a switch; never interrupt a busy recipient.

Runtime state is deliberately outside the plugin cache, in
<CODEX_HOME>/model-settings-picker (or ~/.codex/model-settings-picker). --data or
MODEL_SETTINGS_PICKER_HOME can select an independent location; setup and hook
processes must use the same location. PLUGIN_DATA is not used for preference
storage, so version/cache changes do not relocate saved choices. Native setup
runs picker.py from the plugin root, relative to its packaged skill location.
MODEL_SETTINGS_PICKER_PYTHON may name a verified Python 3.10+ executable for hooks;
otherwise wrappers check bundled/installed runtimes. Missing runtime fails open.

Session files contain hashed session-key filenames, lifecycle, turn ID, action
and selected profile. The hook inspects only a bounded native metadata header,
not conversation items. Local paths, native IDs and preferences enter host model
context; there is no direct network client. Legacy hooks backups, when present,
remain local and can contain private configuration. Never upload runtime data.

```text
python picker.py doctor
python picker.py config-template
python picker.py configure --file choices.json
python picker.py profiles
python picker.py status --session <native-session-id>
python picker.py reset-sessions
```

Only OpenAI/Codex is implemented. Anthropic/Google are future separate providers,
not aliases for OpenAI effort levels. Provider profiles are routing heuristics,
not benchmarks or account entitlements. Local learning, project overrides,
maintenance and authenticated cross-chat receipts are not included.

## Development and release

```text
python -m unittest discover -s tests -v
python build_release.py --output <directory-outside-source>
```

package_files.py defines explicit reviewed plugin/release file lists. Unlisted
.env/private JSON/local-state files are never selected. Required symlinks, linked
parents, Windows reparse points, missing/nonregular files and unsafe paths are
rejected before output writes. Intentionally distributed source still needs
content review for accidentally embedded secrets. Add files only through a
reviewed manifest change. The release builder emits a ZIP and SHA-256 manifest.

MIT license. Public publishing and universal-directory submission are separate
from native plugin registration. See https://developers.openai.com/plugins/build/plugins
for native packaging and https://learn.chatgpt.com/docs/hooks for the hook protocol.
