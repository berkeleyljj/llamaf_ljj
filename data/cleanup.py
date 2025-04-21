#!/usr/bin/env python3
"""
Prune out any function_call or observation messages from traces.json.
"""

import json
import os
import argparse
import sys

def prune_conversations(obj):
    """
    Recursively walk the JSON structure:
      - Whenever you see a key "conversations" whose value is a list,
        drop any entries where "from" is "function_call" or "observation".
      - Recurse into dicts and lists.
    """
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k == "conversations" and isinstance(v, list):
                filtered = []
                for msg in v:
                    if not isinstance(msg, dict):
                        continue
                    src = msg.get("from", "")
                    if src in ("function_call", "observation", "functioncall"):
                        # skip
                        continue
                    filtered.append(prune_conversations(msg))
                out[k] = filtered
            else:
                out[k] = prune_conversations(v)
        return out

    elif isinstance(obj, list):
        return [prune_conversations(x) for x in obj]

    else:
        return obj

def main():
    parser = argparse.ArgumentParser(
        description="Remove function_call & observation entries from traces.json"
    )
    parser.add_argument("input", help="Path to original traces.json")
    parser.add_argument("output", help="Path to write cleaned JSON")
    args = parser.parse_args()

    # Load
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    # Prune
    cleaned = prune_conversations(data)

    # Ensure output dir exists
    outdir = os.path.dirname(args.output)
    if outdir and not os.path.exists(outdir):
        os.makedirs(outdir, exist_ok=True)

    # Write
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    print(f"✅ Cleaned JSON saved to {args.output}")

if __name__ == "__main__":
    main()
