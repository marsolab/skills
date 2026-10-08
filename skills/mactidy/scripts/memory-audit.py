#!/usr/bin/env python3
"""Bounded, read-only macOS memory snapshots; never signal a process."""

import argparse
import datetime
import json
import math
import os
import platform
import re
import subprocess
import sys
import time
from decimal import Decimal


def parse_vm_stat(text):
    match = re.search(r"page size of (\d+) bytes", text)
    if not match or int(match[1]) <= 0:
        raise ValueError("vm_stat page size is missing")
    page_size = int(match[1])
    counters = {}
    for line in text.splitlines():
        match = re.fullmatch(r'\s*"?([^":]+)"?:\s*(\d+)\.\s*', line)
        if match:
            counters[match[1].strip()] = int(match[2])
    # These are individual measures, not additive partitions of physical RAM.
    byte_fields = {
        "free_bytes": "Pages free",
        "active_bytes": "Pages active",
        "inactive_bytes": "Pages inactive",
        "speculative_bytes": "Pages speculative",
        "wired_bytes": "Pages wired down",
        "purgeable_bytes": "Pages purgeable",
        "compressor_physical_bytes": "Pages occupied by compressor",
        "compressor_uncompressed_bytes": "Pages stored in compressor",
    }
    return {
        "page_size_bytes": page_size,
        "counters": counters,
        **{
            key: counters[label] * page_size if label in counters else None
            for key, label in byte_fields.items()
        },
    }


def parse_swap(text):
    result = {}
    factors = {"B": 1, "K": 1024, "M": 1024**2, "G": 1024**3, "T": 1024**4}
    for name in ("total", "used", "free"):
        match = re.search(rf"\b{name}\s*=\s*(\d+(?:\.\d+)?)\s*([BKMGT])\b", text)
        result[name + "_bytes"] = (
            int(Decimal(match[1]) * factors[match[2]]) if match else None
        )
    if result["used_bytes"] is None:
        raise ValueError("swap usage is missing")
    return result


def parse_processes(text):
    processes = []
    skipped = 0
    for line in text.splitlines():
        if not line.strip():
            continue
        fields = line.split(None, 11)
        try:
            if len(fields) != 12:
                raise ValueError("incomplete process row")
            uid, pid, ppid = map(int, fields[:3])
            cpu = float(fields[3])
            rss = int(fields[4])
            if not math.isfinite(cpu) or cpu < 0 or rss < 0 or pid <= 0:
                raise ValueError("invalid process values")
            processes.append(
                {
                    "uid": uid,
                    "pid": pid,
                    "ppid": ppid,
                    "cpu_percent_reported": cpu,
                    "rss_bytes": rss * 1024,
                    "elapsed": fields[5],
                    "start_time": " ".join(fields[6:11]),
                    "executable": fields[11],
                    "owned_by_current_user": uid == os.getuid(),
                    "cleanup_status": "needs_review",
                }
            )
        except (ValueError, OverflowError):
            skipped += 1
    return sorted(processes, key=lambda p: (-p["rss_bytes"], p["pid"])), skipped


def collect_snapshot(top=30):
    warnings = []

    def read(args):
        try:
            result = subprocess.run(
                args,
                text=True,
                capture_output=True,
                check=True,
                timeout=5,
                env={**os.environ, "LC_ALL": "C"},
            )
            return result.stdout
        except (OSError, subprocess.SubprocessError) as error:
            # Avoid environment, process arguments, and raw stderr in reports.
            warnings.append(f"{args[0]} unavailable: {type(error).__name__}")
            return None

    def parse_read(args, parser, label):
        value = read(args)
        if value is None:
            return None
        try:
            return parser(value)
        except (ValueError, KeyError) as error:
            warnings.append(f"{label} unavailable: {error}")
            return None

    captured_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    physical_bytes = parse_read(
        ["sysctl", "-n", "hw.memsize"], lambda s: int(s.strip()), "physical memory"
    )
    vm = parse_read(["vm_stat"], parse_vm_stat, "VM statistics")
    swap = parse_read(["sysctl", "-n", "vm.swapusage"], parse_swap, "swap")
    pressure_level = parse_read(
        ["sysctl", "-n", "kern.memorystatus_vm_pressure_level"],
        lambda s: int(s.strip()),
        "pressure level",
    )
    pressure_text = read(["memory_pressure", "-Q"])
    free_percentage = None
    if pressure_text is not None:
        match = re.search(
            r"System-wide memory free percentage:\s*(\d+)%", pressure_text
        )
        if match and 0 <= int(match[1]) <= 100:
            free_percentage = int(match[1])
        else:
            warnings.append("memory_pressure query did not return a free percentage")
    process_text = read(
        [
            "ps",
            "-axo",
            "uid=,pid=,ppid=,%cpu=,rss=,etime=,lstart=,comm=",
        ]
    )
    processes, skipped = parse_processes(process_text or "")
    if skipped:
        warnings.append(f"{skipped} process rows could not be parsed")
    return {
        "read_only": True,
        "captured_at": captured_at,
        "physical_memory_bytes": physical_bytes,
        "pressure": {
            "sysctl_level_raw": pressure_level,
            "system_wide_free_percentage": free_percentage,
        },
        "vm": vm,
        "swap": swap,
        "process_inventory_complete": process_text is not None and skipped == 0,
        "process_count": len(processes),
        "top_processes": processes[:top],
        "process_rss_is_not_additive_physical_memory": True,
        "warnings": warnings,
    }


def bounded_int(low, high):
    def parse(value):
        result = int(value)
        if not low <= result <= high:
            raise argparse.ArgumentTypeError(f"must be between {low} and {high}")
        return result

    return parse


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=bounded_int(1, 6), default=1)
    parser.add_argument(
        "--interval",
        type=bounded_int(1, 10),
        default=10,
        help="seconds between snapshots; at most 10",
    )
    parser.add_argument("--top", type=bounded_int(1, 100), default=30)
    parser.add_argument(
        "--jsonl",
        action="store_true",
        help="emit each snapshot immediately as one JSON line",
    )
    args = parser.parse_args()
    if platform.system() != "Darwin":
        parser.error("memory-audit supports macOS only")
    snapshots = []
    for index in range(args.samples):
        snapshot = collect_snapshot(args.top)
        snapshots.append(snapshot)
        if args.jsonl:
            print(json.dumps(snapshot, ensure_ascii=False), flush=True)
        if index + 1 < args.samples:
            time.sleep(args.interval)
    if not args.jsonl:
        print(json.dumps({"read_only": True, "snapshots": snapshots}, indent=2))
    return (
        0
        if any(
            s["process_inventory_complete"] and s["vm"] is not None for s in snapshots
        )
        else 2
    )


if __name__ == "__main__":
    sys.exit(main())
