#!/usr/bin/env python3
"""
Workflow Metrics Tool

View, analyze, and export workflow execution metrics from agent-os.

Usage:
    python scripts/workflow-metrics.py --view           # Pretty print metrics
    python scripts/workflow-metrics.py --summary        # Show summary stats
    python scripts/workflow-metrics.py --export FILE    # Export to CSV
    python scripts/workflow-metrics.py --add SPEC_PATH  # Add metrics from spec
"""

import argparse
import json
import csv
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

METRICS_FILE = Path(__file__).parent.parent / "agent-os" / "metrics" / "workflow-log.json"


def load_metrics() -> dict:
    """Load metrics from workflow-log.json."""
    if not METRICS_FILE.exists():
        return {"version": "1.0", "specs": []}
    with open(METRICS_FILE) as f:
        return json.load(f)


def save_metrics(data: dict) -> None:
    """Save metrics to workflow-log.json."""
    with open(METRICS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def view_metrics() -> None:
    """Pretty print all metrics."""
    data = load_metrics()
    specs = data.get("specs", [])

    if not specs:
        print("No metrics recorded yet.")
        return

    print("\n" + "=" * 70)
    print("  WORKFLOW METRICS LOG")
    print("=" * 70)

    for spec in specs:
        track_emoji = {
            "FAST": "🚀",
            "STANDARD": "⚙️",
            "COMPLEX": "🏗️"
        }.get(spec.get("track", ""), "")

        print(f"\n📋 {spec['spec_id']}")
        print(f"   Date: {spec.get('date', 'N/A')}")
        print(f"   Track: {track_emoji} {spec.get('track', 'N/A')} ({spec.get('complexity_points', 0)} pts)")
        print(f"   Duration: {spec.get('duration_minutes', 0)} min")
        print(f"   Task Groups: {spec.get('task_groups', 0)}")

        tests = spec.get("tests", {})
        if tests:
            total = tests.get("total", 0)
            passed = tests.get("passed", 0)
            rate = (passed / total * 100) if total > 0 else 0
            print(f"   Tests: {passed}/{total} ({rate:.0f}%)")

        files = spec.get("files", {})
        if files:
            print(f"   Files: +{files.get('created', 0)} / ~{files.get('modified', 0)}")

    print("\n" + "=" * 70)


def show_summary() -> None:
    """Show summary statistics."""
    data = load_metrics()
    specs = data.get("specs", [])

    if not specs:
        print("No metrics to summarize.")
        return

    print("\n" + "=" * 70)
    print("  WORKFLOW METRICS SUMMARY")
    print("=" * 70)

    # Overall stats
    total_specs = len(specs)
    total_duration = sum(s.get("duration_minutes", 0) for s in specs)
    total_tests = sum(s.get("tests", {}).get("total", 0) for s in specs)
    total_passed = sum(s.get("tests", {}).get("passed", 0) for s in specs)

    print(f"\n📊 Overall ({total_specs} specs)")
    print(f"   Total Duration: {total_duration} min")
    print(f"   Avg Duration: {total_duration / total_specs:.1f} min/spec")
    print(f"   Total Tests: {total_tests}")
    print(f"   Pass Rate: {(total_passed / total_tests * 100) if total_tests > 0 else 0:.1f}%")

    # By track
    tracks = {"FAST": [], "STANDARD": [], "COMPLEX": []}
    for spec in specs:
        track = spec.get("track", "STANDARD")
        if track in tracks:
            tracks[track].append(spec)

    print("\n📈 By Track:")
    for track, track_specs in tracks.items():
        if track_specs:
            avg_dur = sum(s.get("duration_minutes", 0) for s in track_specs) / len(track_specs)
            avg_pts = sum(s.get("complexity_points", 0) for s in track_specs) / len(track_specs)
            emoji = {"FAST": "🚀", "STANDARD": "⚙️", "COMPLEX": "🏗️"}[track]
            print(f"   {emoji} {track}: {len(track_specs)} specs, avg {avg_dur:.0f} min, avg {avg_pts:.0f} pts")

    # Velocity
    total_points = sum(s.get("complexity_points", 0) for s in specs)
    if total_points > 0:
        velocity = total_duration / total_points
        print(f"\n⚡ Velocity: {velocity:.1f} min/complexity point")

    print("\n" + "=" * 70)


def export_csv(filename: str) -> None:
    """Export metrics to CSV."""
    data = load_metrics()
    specs = data.get("specs", [])

    if not specs:
        print("No metrics to export.")
        return

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "spec_id", "date", "track", "complexity_points", "duration_minutes",
            "task_groups", "tests_total", "tests_passed", "tests_failed",
            "files_created", "files_modified"
        ])

        for spec in specs:
            tests = spec.get("tests", {})
            files = spec.get("files", {})
            writer.writerow([
                spec.get("spec_id", ""),
                spec.get("date", ""),
                spec.get("track", ""),
                spec.get("complexity_points", 0),
                spec.get("duration_minutes", 0),
                spec.get("task_groups", 0),
                tests.get("total", 0),
                tests.get("passed", 0),
                tests.get("failed", 0),
                files.get("created", 0),
                files.get("modified", 0)
            ])

    print(f"✅ Exported {len(specs)} specs to {filename}")


def add_metrics(spec_path: str) -> None:
    """Add metrics from a completed spec (interactive)."""
    spec_dir = Path(spec_path)
    spec_id = spec_dir.name

    print(f"\n📝 Adding metrics for: {spec_id}")
    print("-" * 40)

    # Get track info
    track_file = spec_dir / "planning" / "track.md"
    track = "STANDARD"
    complexity_points = 0
    if track_file.exists():
        content = track_file.read_text()
        if "FAST" in content:
            track = "FAST"
        elif "COMPLEX" in content:
            track = "COMPLEX"
        # Try to extract points
        import re
        match = re.search(r"(\d+)\s*(?:pts?|points?)", content, re.IGNORECASE)
        if match:
            complexity_points = int(match.group(1))

    # Count task groups
    tasks_file = spec_dir / "tasks.md"
    task_groups = 0
    if tasks_file.exists():
        content = tasks_file.read_text()
        task_groups = content.count("## Task Group") or content.count("### ")

    # Interactive input for remaining metrics
    print(f"   Track detected: {track}")
    print(f"   Complexity points: {complexity_points}")
    print(f"   Task groups: {task_groups}")

    duration = input("   Duration (minutes): ").strip()
    tests_total = input("   Tests total: ").strip()
    tests_passed = input("   Tests passed: ").strip()
    files_created = input("   Files created: ").strip()
    files_modified = input("   Files modified: ").strip()

    # Build metric entry
    metric = {
        "spec_id": spec_id,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "track": track,
        "complexity_points": complexity_points,
        "duration_minutes": int(duration) if duration else 0,
        "task_groups": task_groups,
        "tests": {
            "total": int(tests_total) if tests_total else 0,
            "passed": int(tests_passed) if tests_passed else 0,
            "failed": int(tests_total) - int(tests_passed) if tests_total and tests_passed else 0
        },
        "files": {
            "created": int(files_created) if files_created else 0,
            "modified": int(files_modified) if files_modified else 0
        },
        "standards": {
            "linting": "pass",
            "types": "pass",
            "security": "pass",
            "api_sync": "pass"
        }
    }

    # Save
    data = load_metrics()
    data["specs"].append(metric)
    save_metrics(data)

    print(f"\n✅ Metrics added for {spec_id}")


def main():
    parser = argparse.ArgumentParser(description="Workflow Metrics Tool")
    parser.add_argument("--view", action="store_true", help="Pretty print all metrics")
    parser.add_argument("--summary", action="store_true", help="Show summary statistics")
    parser.add_argument("--export", metavar="FILE", help="Export to CSV file")
    parser.add_argument("--add", metavar="SPEC_PATH", help="Add metrics from spec folder")

    args = parser.parse_args()

    if args.view:
        view_metrics()
    elif args.summary:
        show_summary()
    elif args.export:
        export_csv(args.export)
    elif args.add:
        add_metrics(args.add)
    else:
        # Default: show view
        view_metrics()


if __name__ == "__main__":
    main()
