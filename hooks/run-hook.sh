#!/bin/sh
# Plugin hooks inherit stdin directly; no prompt content is saved by this wrapper.
picker_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd) || exit 0
if [ -n "${MODEL_SETTINGS_PICKER_PYTHON:-}" ]; then
    if [ -x "$MODEL_SETTINGS_PICKER_PYTHON" ] && "$MODEL_SETTINGS_PICKER_PYTHON" -c 'import sys; sys.exit(sys.version_info < (3,10))' 2>/dev/null; then
        exec "$MODEL_SETTINGS_PICKER_PYTHON" "$picker_root/picker.py" hook
    fi
else
    for candidate in "$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3" python3 python; do
        if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; sys.exit(sys.version_info < (3,10))' 2>/dev/null; then
            exec "$candidate" "$picker_root/picker.py" hook
        fi
    done
fi
printf '%s\n' '{"systemMessage":"Model Settings Picker needs Python 3.10+; continuing without a gate. Complete plugin setup."}'
exit 0
