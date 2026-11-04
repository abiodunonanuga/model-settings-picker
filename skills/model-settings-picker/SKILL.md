---
name: model-settings-picker
description: Set up, reconfigure, explain or diagnose Model Settings Picker, including its preflight behavior and supported OpenAI/Codex settings routing.
---

# Model Settings Picker

For setup/reconfiguration, use a guided conversation in this chat. Installation
alone activates no preferences. Suggested answers are choices to explain, never
silent consent. Batch a few related questions; accept ordinary language. Preserve
existing choices during reconfiguration unless the user changes them.

Resolve the native plugin root from this packaged SKILL.md: the root is two
parent directories above this skill directory (skills/model-settings-picker).
Use picker.py in that root; do not use a versioned cache path from an earlier
installation or the legacy global package path. Verify Python 3.10+ is executable.
Run doctor first. Store preferences outside cache at CODEX_HOME/model-settings-picker
(or ~/.codex/model-settings-picker), honoring MODEL_SETTINGS_PICKER_HOME/--data.
PLUGIN_DATA is not used for preferences. Keep the hook and setup data paths consistent.

## Guided setup

1. Explain this release supports OpenAI models through Codex. Run doctor and inspect
   actual host tools/model availability. Display verified capabilities separately
   from unknown ones. Automatic in-flight switching and speed changes are absent.
2. Ask the user's priority: balanced, conserve usage, faster completion or quality.
   Explain these are selection preferences, not guaranteed savings or performance.
3. Ask intervention: **Advise and continue** (initial recommendation while working)
   or **Pause for your decision** (wait before work). Recommend advise as a suggested
   answer, but obtain their choice. Matching settings proceed silently in both.
4. Ask scope: ordinary chats, Goals, and parent-side launches/handoffs. These are
   independently configurable. Scope selection does not create tasks or messages.
5. Explain and ask separately about optional automatic launch settings and Goal
   next-turn adaptation. Offer only when actual tools support them; otherwise
   leave false and explain the limitation. No general "automatic mode". Record
   only permissions the user actually gives; obey stricter tool authority rules.
6. Offer advanced choices: sensitivity, explanation detail, excluded models/efforts.
   Explain local storage contains hashed session IDs, selected profiles and lifecycle
   status; no stored prompts or transcripts, telemetry or network. The hook reads
   only a bounded native metadata header for child identity. Local learning is not
   implemented in v0.1, so do not offer a nonfunctional switch. Maintenance is separate.
7. Run config-template to obtain the complete schema. Build a candidate JSON from
   confirmed choices. Show a short review including enabled automatic permissions
   and storage location. Resolve remaining choices in normal conversation; clear
   authorization to save is sufficient, never require an exact reply.
8. Call configure --file <candidate> and read back doctor. Demonstrate both the
   chosen behavior and silent matching in disposable data outside the saved profile,
   using configure/decide. Explain this demonstrates protocol behavior, not model
   quality or a real settings switch. Delete disposable demo files afterward.

## Operations

Use `status --session <native id>` for lifecycle inspection. `reset-sessions` clears
only picker decision records when the user requests a reset. `configure` preserves
the previous configuration in config.previous.json. Unknown schema versions hold
configuration and fail open during ordinary work; do not silently migrate them.
For model selection and launches read the installed package's policies/runtime.md.
Do not read or alter another picker's settings or personal policy files.
