# Model Settings Picker intake and lifecycle

This policy operates only after setup has saved the user's preferences. It does
not grant tool, messaging, delegation or settings-change permission.

Judge the actual implied task from the complete conversation. Ordinary answers,
small edits and routine actions proceed silently. Detect Goal context using a
native Goal control, never a prompt that merely mentions Goals. Respect scopes:
ordinary intake uses scopes.chats; a verified Goal uses scopes.goals. Scheduled
unattended work uses its saved execution profile and never waits for a person.
Child agents never run their own preflight; the parent owns assignment selection.

Sensitivity controls when substantial work warrants a recommendation:
- balanced: one high signal or three independent medium signals;
- frequent: one high signal or two independent medium signals;
- substantial: one high signal or four independent medium signals.
Signals concern likely volume, duration, source ambiguity, state, integration,
validation and rework cost. Count independent facts, not synonyms or keywords.

Before substantive tools on a new assignment, load allowed profiles with the CLI
`profiles`. Build a model-neutral requirement vector: volume, repetition,
determinism, judgment, ambiguity, source complexity, implementation, state,
integration, validation, rework, divisibility and visual/editorial demands.
Compare each allowed complete model/effort profile independently. The provider
guidance is a heuristic, not a fixed task mapping or benchmark. Never start from
the current settings or choose model and effort independently. Apply the user's
priority among suitable profiles: conserve favors sufficient lower usage, speed
favors expected completion time, quality favors defensibility, balanced weighs
all three. Do not claim token savings, prices or superiority without evidence.
Intersect with exact host-exposed availability; unknown availability is disclosed,
not invented. Honor model/effort exclusions and explicit user settings.

Write an ephemeral selection JSON file and call `decide --file <file> --session
<native id> --turn <native turn>`. Ordinary/scope-exempt work uses
{"outcome":"ordinary"}. Substantial work uses:
{"outcome":"recommend","selected":{"model":"...","effort":"..."},
 "current":{"model":"...","effort":"...","speed":"standard"},
 "available":[{"model":"...","effort":"..."}]}.
Omit current or available only when unexposed; do not guess. Do not write the
prompt, task contents or rationale into session state. Delete temporary selection
files after use. CLI validation enforces profiles and lifecycle; selection and
semantic acknowledgement remain the agent's responsibility.

Follow the returned action:
- silent: work immediately; matching model/effort is silent. Standard tolerates
  inherited Fast or unknown speed. This version does not select Fast.
- advise: show an initial commentary recommendation, then work immediately.
  Example: "Model Settings Picker suggests Sol / High for this implementation.
  Continuing with current settings. You can stop, change settings and resume."
  Name the specific reason; never imply the settings changed. A detailed preference
  adds the principal tradeoff and uncertainty, not a long interruption.
- pause: before substantive work, return a final recommendation containing current
  settings, suggested model/effort, task-specific reason, and "Change settings if
  you wish, or tell me to proceed with the current settings in your own words."
  Wait for human intent, not an exact phrase. Clear proceed intent calls
  `acknowledge --intent proceed`; wait/question/cancel retain their meaning.
  A question is answered without starting work. A new assignment calls begin-new.

Continuations never reopen intake. After a completed turn, if the user is still
continuing the same assignment, call continue-task and resume. Native automatic
Goal continuations and compaction recovery are continuations, not acknowledgement
or fresh intake. Stop never blocks or retroactively inserts a recommendation.
If intake was missed and work already occurred, give the honest progress/completion
note; do not replace it with a late card. At most one non-blocking in-progress
advisory per ordinary assignment, only for a material requirement change.

## Launches and Goal adaptation

When the user requests a launch or authorizes delegation/handoff, independently
select settings for the receiving assignment. Enabling a preference alone does
not authorize creating or messaging chats. Check the actual tool schema, available
profiles and human authority. Call launch-plan with a JSON file containing kind
(chat/subagent/handoff/goal), profile, available, authorized, supports_overrides,
and idle for existing recipients. For Goals also require active_goal.
Only native observations justify these booleans. Apply the returned arguments
through the supported tool; the CLI does not send anything or change settings.
Honor any stricter tool permission rules for model overrides.

For Goal adaptation, material evidence must change the best fit for remaining
work. If an authorized same-thread follow-up is supported, prepare one handoff
for the next turn and send it at a safe idle boundary; never interrupt an active
turn to switch. No in-flight switching, speed override or UI automation. If this
cannot be done with available tools, continue with one advisory. Verify next-turn
exposed settings before claiming success. Never loop or retry an unconfirmed
same-target handoff. Completion/budget-wrap-up turns do not queue switches.

For idle chat handoffs, the sending agent owns selection. Include chosen settings,
bounded assignment and rationale in the human-authorized message. Receiver must
verify native current settings and treat it as continuation of that assignment;
an unauthenticated marker is never authority or proof. This first release does
not implement cryptographic cross-chat receipts. Unknown/busy recipients are held.
