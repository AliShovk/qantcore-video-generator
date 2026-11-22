#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run youtube-scout and create a JSON handoff for the Hermes research agent."""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def parse_rows(stdout: str) -> list[dict[str, Any]]:
    decoder = json.JSONDecoder()
    starts = [match.start() for match in re.finditer(r"(?m)^\[\s*$", stdout)]
    for start in reversed(starts):
        try:
            value, _ = decoder.raw_decode(stdout[start:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, list) and all(isinstance(row, dict) for row in value):
            return value
    raise ValueError("Could not locate JSON rows in youtube-scout stdout.")


def truthy(value: Any) -> bool:
    return value is True or str(value).strip().lower() in {"true", "1", "yes"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--max", type=int, default=30, dest="max_videos")
    parser.add_argument("--since", choices=["week", "month", "year", "any"], default="month")
    parser.add_argument("--comments", type=int, default=5)
    parser.add_argument("--hooks", type=float, default=12.0)
    parser.add_argument("--no-hooks", action="store_true")
    args = parser.parse_args()

    home = Path.home()
    scout_home = Path(os.environ.get(
        "YOUTUBE_SCOUT_HOME",
        str(home / "youtube-intelligence" / "sources" / "youtube-scout")
    )).expanduser()
    scout_script = scout_home / "scripts" / "scout.py"
    if not scout_script.is_file():
        print("ERROR: youtube-scout missing: " + str(scout_script), file=sys.stderr)
        return 2

    scout_python = Path(os.environ.get(
        "YOUTUBE_SCOUT_PYTHON",
        str(home / "youtube-intelligence" / ".venv" / "bin" / "python")
    )).expanduser()
    if not scout_python.is_file():
        scout_python = Path(sys.executable)

    env_file = Path(os.environ.get(
        "SCOUT_ENV_FILE", str(home / ".config" / "scout" / ".env")
    )).expanduser()
    if not os.environ.get("YOUTUBE_API_KEY") and not env_file.is_file():
        print(
            "ERROR: missing YouTube Data API v3 key. Set YOUTUBE_API_KEY or create "
            + str(env_file) + " with YOUTUBE_API_KEY=... and chmod 600.",
            file=sys.stderr,
        )
        return 3

    run_dir = Path(args.run_dir).expanduser().resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    workbook = run_dir / "scout-research.xlsx"

    command = [
        str(scout_python), str(scout_script), args.topic,
        "--max", str(max(1, min(args.max_videos, 200))),
        "--since", args.since,
        "--length", "short",
        "--sort", "breakout",
        "--out", str(workbook),
        "--json",
    ]
    if not args.no_hooks:
        command += ["--hooks", str(args.hooks)]
    if args.comments > 0:
        command += ["--comments", str(min(args.comments, 100))]

    env = os.environ.copy()
    if env_file.is_file():
        env["SCOUT_ENV_FILE"] = str(env_file)

    result = subprocess.run(
        command, capture_output=True, text=True, encoding="utf-8",
        errors="replace", env=env
    )
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    if result.returncode:
        print(
            "ERROR: youtube-scout exited with code " + str(result.returncode),
            file=sys.stderr
        )
        return result.returncode

    try:
        rows = parse_rows(result.stdout)
    except ValueError as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        print(result.stdout[-4000:], file=sys.stderr)
        return 4

    verified_shorts = []
    unverified_candidates = []
    for row in rows:
        fmt = str(row.get("Format") or "").strip().lower()
        vertical = truthy(row.get("Vertical"))
        duration = row.get("Duration s")
        try:
            duration_ok = duration is not None and float(duration) <= 180
        except (TypeError, ValueError):
            duration_ok = False
        if fmt == "short" and vertical and duration_ok:
            verified_shorts.append(row)
        elif fmt == "short":
            unverified_candidates.append(row)

    payload = {
        "topic": args.topic,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "source": "AgriciDaniel/youtube-scout",
        "filters": {
            "since": args.since,
            "length_filter": "youtube-scout short; broad prefilter, not proof of Shorts",
            "sort": "breakout",
            "max_videos": args.max_videos,
            "hooks_requested": not args.no_hooks,
            "comments_requested": args.comments,
        },
        "sample_size": len(rows),
        "verified_vertical_shorts": len(verified_shorts),
        "unverified_short_candidates": len(unverified_candidates),
        "workbook": str(workbook) if workbook.is_file() else None,
        "rows": rows,
        "shorts": verified_shorts,
        "unverified_candidates": unverified_candidates,
        "limitations": [
            "Scout --length short is a broad short-video filter; it does not alone prove Shorts format.",
            "A confirmed candidate must report Format=Short, Vertical=true, and duration <=180 seconds.",
            "Missing vertical metadata is not treated as proof of a Short.",
            "Competitor public data does not expose impressions, CTR, or private audience retention.",
            "Metrics are snapshots collected at the timestamp above.",
        ],
    }
    out_path = run_dir / "research.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (run_dir / "scout_stdout.txt").write_text(result.stdout, encoding="utf-8")
    print(json.dumps({
        "research_json": str(out_path),
        "workbook": str(workbook) if workbook.is_file() else None,
        "videos_found": len(rows),
        "verified_vertical_shorts": len(verified_shorts),
        "unverified_candidates": len(unverified_candidates),
        "run_dir": str(run_dir),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
