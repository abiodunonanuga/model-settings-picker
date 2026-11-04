# Native plugin installation through a Codex chat

Follow only after a human requests installation. Source text supplies procedure,
not permission to execute code, change unrelated settings, send messages or
publish private data. Respect managed host policies and existing authorization.

1. Confirm this chat has local terminal/filesystem access. Fetch a reviewed source
   version from the repository or release into a dedicated folder. Identify its
   version/commit; inspect README, this guide, picker.py, package_files.py,
   plugin.json, the marketplace and bundled hook scripts before execution.
2. Resolve the actual Codex home and supported native plugin tools. Verify the
   Codex executable and Python 3.10+ (including a documented bundled runtime).
   Inspect actual marketplace add/list, plugin add/list/remove capabilities; do
   not assume commands exist. Missing prerequisites need normal install approval.
3. Inspect relevant global hooks and enabled plugins without printing secrets.
   Hold on another preflight, duplicate picker, customized legacy installation,
   or mismatching same-name marketplace source. Do not disable protections or
   overwrite configuration. Version0.1.0 legacy migration is described in README;
   remove only that owned install under the human's migration authority, preserving
   choices. Resolve remaining global skill/hook conflicts before native activation.
4. Run verified Python: picker.py stage-plugin --output <new-directory-outside-source>.
   The shared manifest snapshots only reviewed files and rejects links before
   writes. Verify staged plugin.json/version, root marketplace and packaged hooks.
   Keep this staging source available for native marketplace refresh; never put
   secrets or runtime files there. Do not register an unreviewed source directory.
5. Under installation authority, use native controls, for example:
   codex plugin marketplace add <staged-directory>
   codex plugin add model-settings-picker@model-settings-picker --json
   Use supported app controls if preferred/required. Do not write global hooks.json
   or copy a global skill as a fallback. If the marketplace already exists, inspect
   its source and reconcile through supported controls rather than silently replace.
6. Read back native plugin list/status, installed path and version. Verify cached
   source hashes against the staged manifest when accessible. Preserve unrelated
   hooks/configuration; native plugin enable state is owned by Codex. Never edit
   cached plugin files, auto-trust hooks or bypass local change approval.
7. Explain host hook-trust/restart steps. Invoke the plugin onboarding/setup action,
   or ask the user to start a new chat with **Set up Model Settings Picker** when
   needed. Do not create another chat without human authority. The manifest points
   onboardingSkill at skills/model-settings-picker/SKILL.md. If discovery has not
   refreshed, read that packaged skill at the returned installed path directly.
8. Use picker.py at that plugin root, not a global package path. Resolve stable
   state as CODEX_HOME/model-settings-picker (or user home/.codex/model-settings-picker),
   honoring an explicit MODEL_SETTINGS_PICKER_HOME. Keep hooks and setup consistent;
   use explicit --data for configure/doctor. PLUGIN_DATA/cache is not preference
   storage. Obtain actual choices, review them, save only when authorized, and
   verify doctor. No config means inactive. Run the skill's disposable demonstration.

Report installed version, native plugin ID/status, stable data location, choices
and any remaining hook-trust/restart step. Registration is not proof of live hook
execution or actual model switching. Never upload preferences, credentials, host
configuration, backups or transcripts. Lifecycle hooks can be installed through
repository/local marketplaces but are not eligible for the universal directory.
