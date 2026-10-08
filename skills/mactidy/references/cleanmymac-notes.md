# CleanMyMac CLI design review

Inspected 2026-10-06. Use as a comparison reference when considering cleanup
design; refresh upstream state before relying on version-specific behavior.

## Available evidence

The [public repository](https://github.com/MacPaw/cleanmymac-cli) at commit
`599fd1cabeda2879ee2bc6ad6edfe4b0fb0d12aa` contains `README.md`, `LICENSE`, and
`SECURITY.md`, without implementation source. The product is proprietary. Its
[command documentation](https://github.com/MacPaw/cleanmymac-cli/wiki/Commands)
describes analysis, cleanup, project artifact review, and RAM/purgeable-space
optimization. This documents behavior, not the internal optimization algorithm.

The [Homebrew cask](https://github.com/MacPaw/homebrew-taps/blob/main/Casks/cleanmymac-cli.rb)
identified version 1.0.0 and its public ZIP. A local static inspection downloaded
that ZIP and verified SHA-256
`f22dcf72e26a680e16e7d4deb0f36c0588f5beb0f7a892248e0ddacf68fb737a`
against the cask. The executable is a universal arm64/x86_64 Mach-O. String and
import inspection found `RamOptimizeTaskRunner`, `PurgeableOptimizeTaskRunner`,
`CMRAMCleaner`, and `CMTimedRAMCleaner` names, plus an imported
`host_statistics64` symbol. Packaged frameworks include
`ProjectArtifactsScanning`, `DeveloperJunkScanning`, `SystemJunkScanning`,
`SpaceLensScanning`, `ScanningCore`, and `FileManagerService`. These observations
support separate scanner/task modules and the presence of host-statistics
access; they do not establish the exact RAM
release mechanism or prove which code path calls the symbol. No runtime
optimization experiment was performed.

## Useful adaptations for Mactidy

| Documented pattern | Mactidy adaptation |
| --- | --- |
| Storage explorer | Owner/project drill-down from a fresh audit |
| Review/select/confirm | Exact targets and an explicitly submitted choice |
| Project artifacts and caches | Separate resource views |
| Ignore list | Per-audit protected paths, excluded from cleanup |
| RAM/purgeable commands | Separate RAM observations and disk deletion |

The review and protected-path behavior is described in
[Safety and Privacy](https://github.com/MacPaw/cleanmymac-cli/wiki/Safety-and-Privacy).
The project purger preselects artifacts older than seven days. Mactidy should
instead start with no selections: age is an investigation hint, while known
ownership, task state, and dependencies establish cleanup eligibility.

The following are Mactidy decisions, not claims about MacPaw's implementation:

- Favor typed review targets with ownership, measurement basis, safety status,
  exact action, and recovery information over a single "junk" label.
- Keep resource-specific inventory adapters separate from review and execution:
  project artifacts, shared tool caches, Docker, disk accounting, and memory
  have different measurements and removal rules. The framework names motivate
  this separation; they do not disclose MacPaw's internal scanner contracts.
- Keep a bounded, read-only memory observation tool. Look for sustained
  pressure and trends before suggesting stop candidates.
- Stop a known unused workload through its owner after explicit selection and
  fresh identity checks. Do not invent a blanket RSS/age process-kill heuristic.
- Treat cache eviction and forced RAM reclamation as separate operations whose
  practical benefit would need measured evidence. Do not imitate an opaque
  optimization merely because its command promises to release memory.
- Keep per-audit exclusions local and explicit. This review does not authorize
  changing global settings, adding persistent rules, or broadening scan roots.

## Inspection boundary

Static names/imports are clues, not reconstructed control flow. A fuller
reverse-engineering task would need a specific question and additional binary
analysis or controlled observations. For this skill update, the useful outcome
is a transparent review workflow and an independently implemented query-only
memory collector. Do not claim that Mactidy reproduces MacPaw's private cleanup
engine, safety rules, or RAM optimizer.
