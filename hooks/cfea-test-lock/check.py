#!/usr/bin/env python3
"""PreToolUse hook: block edits under locked test paths during cfea-tdd's Green phase.

Reads .cfea/state.json (written by the cfea-tdd skill). If phase == "green",
any Edit/Write/NotebookEdit/MultiEdit targeting a file under one of the
recorded locked_paths is blocked. Absence of the state file means no CFEA
TDD loop is in progress, so nothing is restricted.
"""
import json
import os
import sys

LOCKED_PHASE = "green"
STATE_PATH = os.path.join(".cfea", "state.json")
GUARDED_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}


def main():
    payload = json.load(sys.stdin)
    tool_name = payload.get("tool_name")
    if tool_name not in GUARDED_TOOLS:
        return 0

    cwd = payload.get("cwd") or os.getcwd()
    state_file = os.path.join(cwd, STATE_PATH)
    if not os.path.isfile(state_file):
        return 0

    with open(state_file) as f:
        state = json.load(f)

    if state.get("phase") != LOCKED_PHASE:
        return 0

    locked_paths = state.get("locked_paths", [])
    file_path = payload.get("tool_input", {}).get("file_path", "")
    rel_path = os.path.relpath(file_path, cwd) if os.path.isabs(file_path) else file_path

    for locked in locked_paths:
        if rel_path == locked.rstrip("/") or rel_path.startswith(locked.rstrip("/") + os.sep):
            sys.stderr.write(
                f"cfea-test-lock: '{rel_path}' is under '{locked}', which is locked "
                f"during the Green phase (cfea-tdd). Tests are frozen once Red is "
                f"confirmed — if this test looks wrong, stop and report it instead "
                f"of editing it. The lock lifts automatically when cfea-tdd hands "
                f"off to cfea-mutate.\n"
            )
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
