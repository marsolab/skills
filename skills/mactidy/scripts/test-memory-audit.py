"""Parser and read-only collection checks; no real processes are stopped."""

import importlib.util
import pathlib
import subprocess
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "memory_audit", pathlib.Path(__file__).with_name("memory-audit.py")
)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class MemoryAuditTests(unittest.TestCase):
    def test_page_size_and_compressor_measures(self):
        for size in (4096, 16384):
            vm = audit.parse_vm_stat(
                f"Mach Virtual Memory Statistics: (page size of {size} bytes)\n"
                "Pages free: 12.\nPages occupied by compressor: 4.\n"
                "Pages stored in compressor: 10.\nSwapouts: 2.\n"
            )
            self.assertEqual(vm["free_bytes"], 12 * size)
            self.assertEqual(vm["compressor_physical_bytes"], 4 * size)
            self.assertEqual(vm["compressor_uncompressed_bytes"], 10 * size)
            self.assertEqual(vm["counters"]["Swapouts"], 2)
            self.assertIsNone(vm["wired_bytes"])

    def test_missing_vm_page_size_is_not_guessed(self):
        with self.assertRaises(ValueError):
            audit.parse_vm_stat("Pages free: 100.\n")

    def test_swap_units(self):
        self.assertEqual(
            audit.parse_swap("total = 2.00G used = 512.50M free = 1.00K"),
            {
                "total_bytes": 2 * 1024**3,
                "used_bytes": int(512.5 * 1024**2),
                "free_bytes": 1024,
            },
        )
        with self.assertRaises(ValueError):
            audit.parse_swap("unknown")

    def test_all_process_owners_and_start_identity(self):
        processes, skipped = audit.parse_processes(
            "0 1 0 0.1 100 10-01:00:00 Mon Oct 5 12:00:00 2026 /sbin/launchd\n"
            "501 9 3 1.2 200 01:00 Mon Oct 5 13:00:00 2026 /Applications/Test App.app/Contents/MacOS/Test App\n"
            "incomplete\n"
        )
        self.assertEqual(skipped, 1)
        self.assertEqual([p["pid"] for p in processes], [9, 1])
        self.assertEqual(processes[0]["start_time"], "Mon Oct 5 13:00:00 2026")
        self.assertEqual(processes[0]["rss_bytes"], 200 * 1024)
        self.assertTrue(processes[0]["executable"].endswith("Test App"))
        self.assertTrue(all(p["cleanup_status"] == "needs_review" for p in processes))

    def test_collection_uses_only_queries_and_no_process_arguments(self):
        outputs = {
            ("sysctl", "-n", "hw.memsize"): "34359738368\n",
            (
                "vm_stat",
            ): "Mach Virtual Memory Statistics: (page size of 16384 bytes)\nPages free: 10.\n",
            ("sysctl", "-n", "vm.swapusage"): "total = 2.00M used = 1.00M free = 1.00M",
            ("sysctl", "-n", "kern.memorystatus_vm_pressure_level"): "2\n",
            ("memory_pressure", "-Q"): "System-wide memory free percentage: 42%\n",
            (
                "ps",
                "-axo",
                "uid=,pid=,ppid=,%cpu=,rss=,etime=,lstart=,comm=",
            ): "501 9 1 1.0 20 01:00 Mon Oct 5 12:00:00 2026 /usr/bin/test\n",
        }

        def run(args, **kwargs):
            self.assertNotIn("shell", kwargs)
            return subprocess.CompletedProcess(args, 0, outputs[tuple(args)], "")

        with patch.object(audit.subprocess, "run", side_effect=run):
            result = audit.collect_snapshot()
        self.assertEqual(result["warnings"], [])
        self.assertTrue(result["process_inventory_complete"])
        self.assertTrue(result["read_only"])
        self.assertNotIn("command", result["top_processes"][0])

    def test_unavailable_metrics_stay_unknown(self):
        with patch.object(audit.subprocess, "run", side_effect=FileNotFoundError()):
            result = audit.collect_snapshot()
        self.assertIsNone(result["physical_memory_bytes"])
        self.assertIsNone(result["vm"])
        self.assertIsNone(result["swap"])
        self.assertFalse(result["process_inventory_complete"])
        self.assertTrue(result["warnings"])


if __name__ == "__main__":
    unittest.main()
