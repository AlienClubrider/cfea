#!/usr/bin/env python3
"""Merge a hook config snippet into a Claude Code settings.json without
clobbering whatever's already there (other hooks, permissions, etc)."""
import json
import os
import sys


def load(path):
    if os.path.isfile(path):
        with open(path) as f:
            return json.load(f)
    return {}


def main():
    target_path, snippet_path = sys.argv[1], sys.argv[2]
    target = load(target_path)
    snippet = load(snippet_path)

    target.setdefault("hooks", {})
    for event, entries in snippet.get("hooks", {}).items():
        target["hooks"].setdefault(event, [])
        for entry in entries:
            if entry not in target["hooks"][event]:
                target["hooks"][event].append(entry)

    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "w") as f:
        json.dump(target, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
