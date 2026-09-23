use std::collections::HashSet;
use std::env;
use std::ffi::OsStr;
use std::fs;
use std::io::{self, IsTerminal, Write};
use std::os::unix::fs::MetadataExt;
use std::path::{Path, PathBuf};
use std::process::{Command, Output};
use std::time::{SystemTime, UNIX_EPOCH};

type AppResult<T> = Result<T, String>;

const DEFAULT_MIN_AGE_DAYS: u64 = 14;
const DEFAULT_MIN_SIZE_MIB: u64 = 50;

#[derive(Debug, Clone, PartialEq, Eq)]
struct ArtifactCandidate {
    kind: &'static str,
    bytes: u64,
    age_days: u64,
    path: PathBuf,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct ProcessCandidate {
    pid: u32,
    ppid: u32,
    tty: String,
    elapsed: String,
    rss_kib: u64,
    executable: String,
    command: String,
}

#[derive(Debug, Clone, Default, PartialEq, Eq)]
struct WorktreeCandidate {
    path: PathBuf,
    head: String,
    branch: Option<String>,
    detached: bool,
    locked: Option<String>,
    prunable: Option<String>,
    clean: Option<bool>,
    upstream: Option<String>,
    ahead: Option<u64>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct DiskUsage {
    total_kib: u64,
    used_kib: u64,
    available_kib: u64,
    capacity: String,
}

#[derive(Debug, Default)]
struct AuditOptions {
    roots: Vec<PathBuf>,
    repos: Vec<PathBuf>,
    min_age_days: u64,
    min_size_mib: u64,
    json: bool,
}

#[derive(Debug)]
struct TrashOptions {
    root: PathBuf,
    path: PathBuf,
    confirm: Option<PathBuf>,
}

#[derive(Debug)]
struct RetireOptions {
    repo: PathBuf,
    path: PathBuf,
    merged_into: String,
    confirm: Option<PathBuf>,
}

fn main() {
    if !cfg!(target_os = "macos") {
        eprintln!("error: mactidy supports macOS only");
        std::process::exit(2);
    }

    let args: Vec<String> = env::args().skip(1).collect();
    let result = match args.first().map(String::as_str) {
        Some("audit") => parse_audit(&args[1..]).and_then(run_audit),
        Some("trash") => parse_trash(&args[1..]).and_then(run_trash),
        Some("retire-worktree") => parse_retire(&args[1..]).and_then(run_retire_worktree),
        Some("help" | "--help" | "-h") | None => {
            print_help();
            Ok(())
        }
        Some(command) => Err(format!("unknown command {command:?}; run `mactidy help`")),
    };

    if let Err(error) = result {
        eprintln!("error: {error}");
        std::process::exit(2);
    }
}

fn print_help() {
    println!(
        "\
mactidy - conservative cleanup for agentic development leftovers

USAGE:
  mactidy audit --root PATH [--root PATH ...] [OPTIONS]
  mactidy trash --root PATH --path PATH [--confirm PATH]
  mactidy retire-worktree --repo PATH --path PATH \\
      --merged-into REF [--confirm PATH]

AUDIT OPTIONS:
  --root PATH           Explicit development root to scan (repeatable)
  --repo PATH           Git repository whose worktrees should be audited
                        (repeatable)
  --min-age-days N      Minimum directory age (default: 14)
  --min-size-mib N      Minimum approximate size (default: 50)
  --json                Emit compact structured JSON

MUTATION SAFETY:
  `trash` only moves an allow-listed artifact below the exact root to
  ~/.Trash. `retire-worktree` only removes a clean, unlocked linked worktree
  whose HEAD is already reachable from --merged-into. Both commands require
  typing the canonical path, or passing the same path with --confirm after
  approval. There is no permanent-delete or force mode."
    );
}

fn parse_audit(args: &[String]) -> AppResult<AuditOptions> {
    let mut options = AuditOptions {
        min_age_days: DEFAULT_MIN_AGE_DAYS,
        min_size_mib: DEFAULT_MIN_SIZE_MIB,
        ..AuditOptions::default()
    };
    let mut index = 0;
    while index < args.len() {
        match args[index].as_str() {
            "--root" => options
                .roots
                .push(PathBuf::from(flag_value(args, &mut index, "--root")?)),
            "--repo" => options
                .repos
                .push(PathBuf::from(flag_value(args, &mut index, "--repo")?)),
            "--min-age-days" => {
                options.min_age_days = parse_u64(
                    flag_value(args, &mut index, "--min-age-days")?,
                    "--min-age-days",
                )?;
            }
            "--min-size-mib" => {
                options.min_size_mib = parse_u64(
                    flag_value(args, &mut index, "--min-size-mib")?,
                    "--min-size-mib",
                )?;
            }
            "--json" => options.json = true,
            flag => return Err(format!("unknown audit option {flag:?}")),
        }
        index += 1;
    }
    if options.roots.is_empty() {
        return Err("audit requires at least one explicit --root".into());
    }
    Ok(options)
}

fn parse_trash(args: &[String]) -> AppResult<TrashOptions> {
    let mut root = None;
    let mut path = None;
    let mut confirm = None;
    let mut index = 0;
    while index < args.len() {
        match args[index].as_str() {
            "--root" => {
                root = Some(PathBuf::from(flag_value(args, &mut index, "--root")?));
            }
            "--path" => {
                path = Some(PathBuf::from(flag_value(args, &mut index, "--path")?));
            }
            "--confirm" => {
                confirm = Some(PathBuf::from(flag_value(args, &mut index, "--confirm")?));
            }
            flag => return Err(format!("unknown trash option {flag:?}")),
        }
        index += 1;
    }
    Ok(TrashOptions {
        root: root.ok_or("trash requires --root")?,
        path: path.ok_or("trash requires --path")?,
        confirm,
    })
}

fn parse_retire(args: &[String]) -> AppResult<RetireOptions> {
    let mut repo = None;
    let mut path = None;
    let mut merged_into = None;
    let mut confirm = None;
    let mut index = 0;
    while index < args.len() {
        match args[index].as_str() {
            "--repo" => {
                repo = Some(PathBuf::from(flag_value(args, &mut index, "--repo")?));
            }
            "--path" => {
                path = Some(PathBuf::from(flag_value(args, &mut index, "--path")?));
            }
            "--merged-into" => {
                merged_into = Some(flag_value(args, &mut index, "--merged-into")?);
            }
            "--confirm" => {
                confirm = Some(PathBuf::from(flag_value(args, &mut index, "--confirm")?));
            }
            flag => {
                return Err(format!("unknown retire-worktree option {flag:?}"));
            }
        }
        index += 1;
    }
    Ok(RetireOptions {
        repo: repo.ok_or("retire-worktree requires --repo")?,
        path: path.ok_or("retire-worktree requires --path")?,
        merged_into: merged_into.ok_or("retire-worktree requires --merged-into")?,
        confirm,
    })
}

fn flag_value(args: &[String], index: &mut usize, flag: &str) -> AppResult<String> {
    *index += 1;
    args.get(*index)
        .cloned()
        .ok_or_else(|| format!("{flag} requires a value"))
}

fn parse_u64(value: String, flag: &str) -> AppResult<u64> {
    value
        .parse::<u64>()
        .map_err(|_| format!("{flag} requires a non-negative integer"))
}

fn run_audit(options: AuditOptions) -> AppResult<()> {
    let mut artifacts = Vec::new();
    let mut warnings = Vec::new();
    for root in &options.roots {
        let canonical = canonical_directory(root, "scan root")?;
        reject_system_root(&canonical)?;
        scan_root(
            &canonical,
            options.min_age_days,
            options.min_size_mib.saturating_mul(1024 * 1024),
            &mut artifacts,
            &mut warnings,
        );
    }
    artifacts.sort_by(|left, right| {
        right
            .bytes
            .cmp(&left.bytes)
            .then_with(|| left.path.cmp(&right.path))
    });

    let disk = data_volume_usage().ok();
    let processes = process_candidates()?;
    let mut worktrees = Vec::new();
    for repo in &options.repos {
        match worktree_candidates(repo) {
            Ok(mut found) => worktrees.append(&mut found),
            Err(error) => warnings.push(error),
        }
    }

    if options.json {
        print_audit_json(disk.as_ref(), &artifacts, &processes, &worktrees, &warnings);
    } else {
        print_audit_text(disk.as_ref(), &artifacts, &processes, &worktrees, &warnings);
    }
    Ok(())
}

fn scan_root(
    root: &Path,
    min_age_days: u64,
    min_size_bytes: u64,
    candidates: &mut Vec<ArtifactCandidate>,
    warnings: &mut Vec<String>,
) {
    let mut pending = vec![root.to_path_buf()];
    while let Some(path) = pending.pop() {
        let metadata = match fs::symlink_metadata(&path) {
            Ok(metadata) => metadata,
            Err(error) => {
                warnings.push(format!("cannot inspect {}: {error}", path.display()));
                continue;
            }
        };
        if metadata.file_type().is_symlink() || !metadata.is_dir() {
            continue;
        }

        let name = path.file_name().and_then(OsStr::to_str).unwrap_or("");
        if path != root && should_prune(name) {
            continue;
        }
        if path != root {
            if let Some(kind) = artifact_kind(name) {
                let bytes = match directory_size(&path) {
                    Ok(bytes) => bytes,
                    Err(error) => {
                        warnings.push(format!("cannot measure {}: {error}", path.display()));
                        continue;
                    }
                };
                let age_days = age_days(&metadata);
                if bytes >= min_size_bytes && age_days >= min_age_days {
                    candidates.push(ArtifactCandidate {
                        kind,
                        bytes,
                        age_days,
                        path,
                    });
                }
                continue;
            }
        }

        match fs::read_dir(&path) {
            Ok(entries) => {
                for entry in entries {
                    match entry {
                        Ok(entry) => pending.push(entry.path()),
                        Err(error) => warnings.push(format!(
                            "cannot read an entry below {}: {error}",
                            path.display()
                        )),
                    }
                }
            }
            Err(error) => {
                warnings.push(format!("cannot read directory {}: {error}", path.display()))
            }
        }
    }
}

fn artifact_kind(name: &str) -> Option<&'static str> {
    match name {
        "node_modules" | ".venv" => Some("dependency"),
        ".pytest_cache" | "__pycache__" => Some("cache"),
        "target" | ".next" | ".nuxt" | ".svelte-kit" | ".turbo" | "coverage" | "DerivedData" => {
            Some("build-output")
        }
        _ => None,
    }
}

fn should_prune(name: &str) -> bool {
    matches!(name, ".git" | ".Trash" | "Library")
}

fn directory_size(path: &Path) -> AppResult<u64> {
    let mut bytes = 0_u64;
    let mut seen_files = HashSet::new();
    let mut pending = vec![path.to_path_buf()];
    while let Some(current) = pending.pop() {
        let metadata = fs::symlink_metadata(&current)
            .map_err(|error| format!("{}: {error}", current.display()))?;
        if metadata.file_type().is_symlink() {
            continue;
        }
        if metadata.is_file() {
            if seen_files.insert((metadata.dev(), metadata.ino())) {
                bytes = bytes.saturating_add(metadata.len());
            }
            continue;
        }
        if metadata.is_dir() {
            for entry in
                fs::read_dir(&current).map_err(|error| format!("{}: {error}", current.display()))?
            {
                let entry = entry.map_err(|error| format!("{}: {error}", current.display()))?;
                pending.push(entry.path());
            }
        }
    }
    Ok(bytes)
}

fn age_days(metadata: &fs::Metadata) -> u64 {
    let modified = match metadata.modified() {
        Ok(value) => value,
        Err(_) => return 0,
    };
    SystemTime::now()
        .duration_since(modified)
        .map(|duration| duration.as_secs() / 86_400)
        .unwrap_or(0)
}

fn data_volume_usage() -> AppResult<DiskUsage> {
    let output = command_output("df", ["-k", "/System/Volumes/Data"])?;
    require_success("df", &output)?;
    let text = String::from_utf8_lossy(&output.stdout);
    let line = text.lines().last().ok_or("df returned no filesystem row")?;
    let fields: Vec<&str> = line.split_whitespace().collect();
    if fields.len() < 5 {
        return Err("cannot parse df output".into());
    }
    Ok(DiskUsage {
        total_kib: fields[1]
            .parse()
            .map_err(|_| "cannot parse df total blocks")?,
        used_kib: fields[2]
            .parse()
            .map_err(|_| "cannot parse df used blocks")?,
        available_kib: fields[3]
            .parse()
            .map_err(|_| "cannot parse df available blocks")?,
        capacity: fields[4].to_string(),
    })
}

fn process_candidates() -> AppResult<Vec<ProcessCandidate>> {
    let output = command_output(
        "ps",
        ["-axo", "pid=,ppid=,tty=,etime=,rss=,ucomm=,command="],
    )?;
    require_success("ps", &output)?;
    let allowed = [
        "node",
        "nodejs",
        "bun",
        "deno",
        "vite",
        "webpack",
        "playwright",
        "claude",
        "cursor-agent",
        "codex",
    ];
    let mut candidates = Vec::new();
    for line in String::from_utf8_lossy(&output.stdout).lines() {
        let mut fields = line.split_whitespace();
        let Some(pid) = fields.next().and_then(|value| value.parse().ok()) else {
            continue;
        };
        let Some(ppid) = fields.next().and_then(|value| value.parse().ok()) else {
            continue;
        };
        let Some(tty) = fields.next() else {
            continue;
        };
        let Some(elapsed) = fields.next() else {
            continue;
        };
        let Some(rss_kib) = fields.next().and_then(|value| value.parse().ok()) else {
            continue;
        };
        let Some(executable) = fields.next() else {
            continue;
        };
        if ppid != 1 || tty != "??" || !allowed.contains(&executable.to_ascii_lowercase().as_str())
        {
            continue;
        }
        candidates.push(ProcessCandidate {
            pid,
            ppid,
            tty: tty.to_string(),
            elapsed: elapsed.to_string(),
            rss_kib,
            executable: executable.to_string(),
            command: fields.collect::<Vec<_>>().join(" "),
        });
    }
    candidates.sort_by_key(|item| std::cmp::Reverse(item.rss_kib));
    Ok(candidates)
}

fn worktree_candidates(repo: &Path) -> AppResult<Vec<WorktreeCandidate>> {
    let repo = canonical_directory(repo, "repository")?;
    let output = git_output(&repo, ["worktree", "list", "--porcelain", "-z"])?;
    require_success("git worktree list", &output)?;
    let mut worktrees = parse_worktree_porcelain(&output.stdout)?;
    for worktree in &mut worktrees {
        if !worktree.path.is_dir() {
            continue;
        }
        let status = git_output(
            &worktree.path,
            ["status", "--porcelain=v1", "--untracked-files=all"],
        )?;
        if status.status.success() {
            worktree.clean = Some(status.stdout.is_empty());
        }
        let upstream = git_output(
            &worktree.path,
            [
                "rev-parse",
                "--abbrev-ref",
                "--symbolic-full-name",
                "@{upstream}",
            ],
        )?;
        if upstream.status.success() {
            let upstream_name = String::from_utf8_lossy(&upstream.stdout).trim().to_string();
            let range = format!("{upstream_name}..HEAD");
            let ahead = git_output(&worktree.path, ["rev-list", "--count", range.as_str()])?;
            if ahead.status.success() {
                worktree.ahead = String::from_utf8_lossy(&ahead.stdout).trim().parse().ok();
            }
            worktree.upstream = Some(upstream_name);
        }
    }
    Ok(worktrees)
}

fn parse_worktree_porcelain(bytes: &[u8]) -> AppResult<Vec<WorktreeCandidate>> {
    let mut worktrees = Vec::new();
    let mut current = WorktreeCandidate::default();
    for raw in bytes.split(|byte| *byte == 0) {
        if raw.is_empty() {
            if !current.path.as_os_str().is_empty() {
                worktrees.push(current);
                current = WorktreeCandidate::default();
            }
            continue;
        }
        let field = String::from_utf8(raw.to_vec())
            .map_err(|_| "git worktree output is not valid UTF-8")?;
        if let Some(value) = field.strip_prefix("worktree ") {
            current.path = PathBuf::from(value);
        } else if let Some(value) = field.strip_prefix("HEAD ") {
            current.head = value.to_string();
        } else if let Some(value) = field.strip_prefix("branch ") {
            current.branch = Some(value.to_string());
        } else if field == "detached" {
            current.detached = true;
        } else if field == "locked" {
            current.locked = Some(String::new());
        } else if let Some(value) = field.strip_prefix("locked ") {
            current.locked = Some(value.to_string());
        } else if field == "prunable" {
            current.prunable = Some(String::new());
        } else if let Some(value) = field.strip_prefix("prunable ") {
            current.prunable = Some(value.to_string());
        }
    }
    if !current.path.as_os_str().is_empty() {
        worktrees.push(current);
    }
    Ok(worktrees)
}

fn run_trash(options: TrashOptions) -> AppResult<()> {
    let trash = home_directory()?.join(".Trash");
    run_trash_to(options, &trash)
}

fn run_trash_to(options: TrashOptions, trash: &Path) -> AppResult<()> {
    let root = canonical_directory(&options.root, "cleanup root")?;
    reject_cleanup_root(&root)?;

    let original_metadata = fs::symlink_metadata(&options.path)
        .map_err(|error| format!("cannot inspect {}: {error}", options.path.display()))?;
    if original_metadata.file_type().is_symlink() {
        return Err("refusing to trash a symlink".into());
    }
    let path = canonical_directory(&options.path, "artifact path")?;
    if path == root || !path.starts_with(&root) {
        return Err(format!(
            "artifact {} is not strictly below cleanup root {}",
            path.display(),
            root.display()
        ));
    }
    let name = path.file_name().and_then(OsStr::to_str).unwrap_or("");
    let kind = artifact_kind(name)
        .ok_or_else(|| format!("{name:?} is not an allow-listed reproducible artifact"))?;

    reject_open_files(&path)?;
    let bytes = directory_size(&path)?;
    confirm_exact_path(&path, options.confirm.as_deref())?;

    let rechecked_metadata = fs::symlink_metadata(&options.path).map_err(|error| {
        format!(
            "cannot re-check {} immediately before moving it: {error}",
            options.path.display()
        )
    })?;
    if rechecked_metadata.file_type().is_symlink() {
        return Err("artifact became a symlink after approval; nothing changed".into());
    }
    let rechecked = canonical_directory(&options.path, "artifact path")?;
    if rechecked != path {
        return Err(format!(
            "artifact path changed after approval: now {}",
            rechecked.display()
        ));
    }
    reject_open_files(&path)?;

    if trash.exists() {
        let metadata = fs::symlink_metadata(trash)
            .map_err(|error| format!("cannot inspect {}: {error}", trash.display()))?;
        if metadata.file_type().is_symlink() {
            return Err(format!(
                "refusing symlinked Trash directory {}",
                trash.display()
            ));
        }
    } else {
        fs::create_dir_all(trash)
            .map_err(|error| format!("cannot create {}: {error}", trash.display()))?;
    }
    let trash = canonical_directory(trash, "Trash directory")?;
    let stamp = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|_| "system clock is before the Unix epoch")?
        .as_secs();
    let destination = trash.join(format!("mactidy-{stamp}-{}-{name}", std::process::id()));
    if destination.exists() {
        return Err(format!(
            "Trash destination already exists: {}",
            destination.display()
        ));
    }
    fs::rename(&path, &destination).map_err(|error| {
        format!(
            "cannot move {} to {}: {error}; no copy/delete fallback was attempted",
            path.display(),
            destination.display()
        )
    })?;
    println!(
        "Moved {kind} {} ({}) to {}.",
        path.display(),
        human_bytes(bytes),
        destination.display()
    );
    println!("Physical space is reclaimed only after Trash is emptied.");
    Ok(())
}

fn run_retire_worktree(options: RetireOptions) -> AppResult<()> {
    if options.merged_into.is_empty() || options.merged_into.starts_with('-') {
        return Err("--merged-into must name a ref, not an option".into());
    }
    let repo = canonical_directory(&options.repo, "repository")?;
    let path = canonical_directory(&options.path, "worktree")?;
    let worktrees = worktree_candidates(&repo)?;
    let Some(position) = worktrees
        .iter()
        .position(|item| fs::canonicalize(&item.path).ok().as_deref() == Some(path.as_path()))
    else {
        return Err(format!(
            "{} is not registered as a worktree of {}",
            path.display(),
            repo.display()
        ));
    };
    if position == 0 {
        return Err("refusing to remove the main worktree".into());
    }
    let worktree = &worktrees[position];
    if let Some(reason) = &worktree.locked {
        return Err(format!("worktree is locked: {reason}"));
    }
    if worktree.clean != Some(true) {
        return Err("worktree is dirty or its status could not be proven clean".into());
    }

    let verify_ref = git_output(
        &repo,
        ["rev-parse", "--verify", options.merged_into.as_str()],
    )?;
    require_success("git rev-parse --verify", &verify_ref)?;
    let merged = git_output(
        &repo,
        [
            "merge-base",
            "--is-ancestor",
            worktree.head.as_str(),
            options.merged_into.as_str(),
        ],
    )?;
    if !merged.status.success() {
        return Err(format!(
            "worktree HEAD {} is not reachable from {}",
            worktree.head, options.merged_into
        ));
    }

    confirm_exact_path(&path, options.confirm.as_deref())?;
    let status_again = git_output(&path, ["status", "--porcelain=v1", "--untracked-files=all"])?;
    require_success("final git status", &status_again)?;
    if !status_again.stdout.is_empty() {
        return Err("worktree became dirty after approval; nothing changed".into());
    }
    let head_again = git_output(&path, ["rev-parse", "HEAD"])?;
    require_success("final git rev-parse HEAD", &head_again)?;
    let head_again = String::from_utf8_lossy(&head_again.stdout)
        .trim()
        .to_string();
    if head_again != worktree.head {
        return Err(format!(
            "worktree HEAD changed after approval from {} to {}; nothing changed",
            worktree.head, head_again
        ));
    }
    let merged_again = git_output(
        &repo,
        [
            "merge-base",
            "--is-ancestor",
            head_again.as_str(),
            options.merged_into.as_str(),
        ],
    )?;
    if !merged_again.status.success() {
        return Err(format!(
            "worktree HEAD is no longer reachable from {}; nothing changed",
            options.merged_into
        ));
    }
    let path_string = path.to_string_lossy().into_owned();
    let removed = git_output(&repo, ["worktree", "remove", path_string.as_str()])?;
    require_success("git worktree remove", &removed)?;
    println!(
        "Removed clean worktree {} after proving HEAD is in {}.",
        path.display(),
        options.merged_into
    );
    Ok(())
}

fn confirm_exact_path(path: &Path, supplied: Option<&Path>) -> AppResult<()> {
    if let Some(supplied) = supplied {
        let confirmed = fs::canonicalize(supplied).map_err(|error| {
            format!(
                "cannot resolve confirmation {}: {error}",
                supplied.display()
            )
        })?;
        if confirmed != path {
            return Err(format!(
                "confirmation resolves to {}, expected {}",
                confirmed.display(),
                path.display()
            ));
        }
        return Ok(());
    }
    if !io::stdin().is_terminal() {
        return Err(format!(
            "interactive confirmation unavailable; after approval pass --confirm {}",
            path.display()
        ));
    }
    print!(
        "Type the full canonical path to confirm this operation:\n{}\n> ",
        path.display()
    );
    io::stdout()
        .flush()
        .map_err(|error| format!("cannot flush confirmation prompt: {error}"))?;
    let mut input = String::new();
    io::stdin()
        .read_line(&mut input)
        .map_err(|error| format!("cannot read confirmation: {error}"))?;
    if Path::new(input.trim()) != path {
        return Err("confirmation did not exactly match; nothing changed".into());
    }
    Ok(())
}

fn reject_open_files(path: &Path) -> AppResult<()> {
    let path_string = path.to_string_lossy().into_owned();
    let output = command_output("lsof", ["-nP", "+D", path_string.as_str()])?;
    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);
    if !stderr.trim().is_empty() {
        return Err(format!(
            "could not prove {} has no open files: {}",
            path.display(),
            stderr.trim()
        ));
    }
    if output.status.success() && stdout.lines().count() > 1 {
        return Err(format!(
            "open files exist below {}; close the owning processes first",
            path.display()
        ));
    }
    Ok(())
}

fn canonical_directory(path: &Path, label: &str) -> AppResult<PathBuf> {
    let canonical = fs::canonicalize(path)
        .map_err(|error| format!("cannot resolve {label} {}: {error}", path.display()))?;
    if !canonical.is_dir() {
        return Err(format!(
            "{label} {} is not a directory",
            canonical.display()
        ));
    }
    Ok(canonical)
}

fn reject_system_root(path: &Path) -> AppResult<()> {
    let forbidden = [
        Path::new("/"),
        Path::new("/System"),
        Path::new("/System/Volumes"),
        Path::new("/System/Volumes/Data"),
        Path::new("/Users"),
        Path::new("/Applications"),
        Path::new("/Library"),
        Path::new("/Volumes"),
        Path::new("/private"),
        Path::new("/private/var"),
        Path::new("/private/var/folders"),
        Path::new("/usr"),
        Path::new("/opt"),
    ];
    if forbidden.contains(&path) {
        return Err(format!("refusing broad scan root {}", path.display()));
    }
    Ok(())
}

fn reject_cleanup_root(path: &Path) -> AppResult<()> {
    reject_system_root(path)?;
    if path == home_directory()?.as_path() {
        return Err("refusing to use the home directory as a cleanup root".into());
    }
    Ok(())
}

fn home_directory() -> AppResult<PathBuf> {
    env::var_os("HOME")
        .map(PathBuf::from)
        .ok_or("HOME is not set".into())
}

fn git_output<I, S>(cwd: &Path, args: I) -> AppResult<Output>
where
    I: IntoIterator<Item = S>,
    S: AsRef<OsStr>,
{
    Command::new("git")
        .args(args)
        .current_dir(cwd)
        .env("GIT_OPTIONAL_LOCKS", "0")
        .output()
        .map_err(|error| format!("cannot run git: {error}"))
}

fn command_output<I, S>(program: &str, args: I) -> AppResult<Output>
where
    I: IntoIterator<Item = S>,
    S: AsRef<OsStr>,
{
    Command::new(program)
        .args(args)
        .output()
        .map_err(|error| format!("cannot run {program}: {error}"))
}

fn require_success(label: &str, output: &Output) -> AppResult<()> {
    if output.status.success() {
        return Ok(());
    }
    let stderr = String::from_utf8_lossy(&output.stderr).trim().to_string();
    Err(if stderr.is_empty() {
        format!("{label} exited with {}", output.status)
    } else {
        format!("{label} failed: {stderr}")
    })
}

fn print_audit_text(
    disk: Option<&DiskUsage>,
    artifacts: &[ArtifactCandidate],
    processes: &[ProcessCandidate],
    worktrees: &[WorktreeCandidate],
    warnings: &[String],
) {
    println!("Mactidy audit (read-only)");
    if let Some(disk) = disk {
        println!(
            "Data volume: {} available of {} ({} used)",
            human_bytes(disk.available_kib.saturating_mul(1024)),
            human_bytes(disk.total_kib.saturating_mul(1024)),
            disk.capacity
        );
    }

    println!("\nArtifacts: {}", artifacts.len());
    for item in artifacts {
        println!(
            "{}\t{}\t{}d\t{}",
            item.kind,
            human_bytes(item.bytes),
            item.age_days,
            item.path.display()
        );
    }

    println!("\nDetached process review candidates: {}", processes.len());
    for item in processes {
        println!(
            "pid={} rss={} elapsed={} exec={} cmd={}",
            item.pid,
            human_bytes(item.rss_kib.saturating_mul(1024)),
            item.elapsed,
            item.executable,
            item.command
        );
    }

    println!("\nGit worktrees: {}", worktrees.len());
    for item in worktrees {
        println!(
            "{}\tclean={}\tlocked={}\tahead={}\t{}",
            if item.detached { "detached" } else { "branch" },
            optional_bool(item.clean),
            item.locked.is_some(),
            item.ahead
                .map(|value| value.to_string())
                .unwrap_or_else(|| "unknown".into()),
            item.path.display()
        );
    }

    for warning in warnings {
        eprintln!("warning: {warning}");
    }
    println!("\nNo files were moved and no processes were signalled.");
}

fn print_audit_json(
    disk: Option<&DiskUsage>,
    artifacts: &[ArtifactCandidate],
    processes: &[ProcessCandidate],
    worktrees: &[WorktreeCandidate],
    warnings: &[String],
) {
    let mut output = String::from("{");
    output.push_str("\"read_only\":true,\"disk\":");
    if let Some(disk) = disk {
        output.push_str(&format!(
            "{{\"total_kib\":{},\"used_kib\":{},\"available_kib\":{},\"capacity\":\"{}\"}}",
            disk.total_kib,
            disk.used_kib,
            disk.available_kib,
            json_escape(&disk.capacity)
        ));
    } else {
        output.push_str("null");
    }

    output.push_str(",\"artifacts\":[");
    for (index, item) in artifacts.iter().enumerate() {
        comma(&mut output, index);
        output.push_str(&format!(
            "{{\"kind\":\"{}\",\"bytes\":{},\"age_days\":{},\"path\":\"{}\"}}",
            item.kind,
            item.bytes,
            item.age_days,
            json_escape(&item.path.to_string_lossy())
        ));
    }
    output.push(']');

    output.push_str(",\"processes\":[");
    for (index, item) in processes.iter().enumerate() {
        comma(&mut output, index);
        output.push_str(&format!(
            "{{\"pid\":{},\"ppid\":{},\"tty\":\"{}\",\"elapsed\":\"{}\",\"rss_kib\":{},\"executable\":\"{}\",\"command\":\"{}\"}}",
            item.pid,
            item.ppid,
            json_escape(&item.tty),
            json_escape(&item.elapsed),
            item.rss_kib,
            json_escape(&item.executable),
            json_escape(&item.command)
        ));
    }
    output.push(']');

    output.push_str(",\"worktrees\":[");
    for (index, item) in worktrees.iter().enumerate() {
        comma(&mut output, index);
        output.push_str(&format!(
            "{{\"path\":\"{}\",\"head\":\"{}\",\"branch\":{},\"detached\":{},\"locked\":{},\"prunable\":{},\"clean\":{},\"upstream\":{},\"ahead\":{}}}",
            json_escape(&item.path.to_string_lossy()),
            json_escape(&item.head),
            json_optional(item.branch.as_deref()),
            item.detached,
            json_optional(item.locked.as_deref()),
            json_optional(item.prunable.as_deref()),
            json_optional_bool(item.clean),
            json_optional(item.upstream.as_deref()),
            item.ahead
                .map(|value| value.to_string())
                .unwrap_or_else(|| "null".into())
        ));
    }
    output.push(']');

    output.push_str(",\"warnings\":[");
    for (index, warning) in warnings.iter().enumerate() {
        comma(&mut output, index);
        output.push('"');
        output.push_str(&json_escape(warning));
        output.push('"');
    }
    output.push_str("]}");
    println!("{output}");
}

fn comma(output: &mut String, index: usize) {
    if index > 0 {
        output.push(',');
    }
}

fn optional_bool(value: Option<bool>) -> &'static str {
    match value {
        Some(true) => "true",
        Some(false) => "false",
        None => "unknown",
    }
}

fn json_optional(value: Option<&str>) -> String {
    value
        .map(|value| format!("\"{}\"", json_escape(value)))
        .unwrap_or_else(|| "null".into())
}

fn json_optional_bool(value: Option<bool>) -> &'static str {
    match value {
        Some(true) => "true",
        Some(false) => "false",
        None => "null",
    }
}

fn json_escape(value: &str) -> String {
    let mut escaped = String::with_capacity(value.len());
    for character in value.chars() {
        match character {
            '"' => escaped.push_str("\\\""),
            '\\' => escaped.push_str("\\\\"),
            '\n' => escaped.push_str("\\n"),
            '\r' => escaped.push_str("\\r"),
            '\t' => escaped.push_str("\\t"),
            value if value.is_control() => {
                escaped.push_str(&format!("\\u{:04x}", value as u32));
            }
            value => escaped.push(value),
        }
    }
    escaped
}

fn human_bytes(bytes: u64) -> String {
    const UNITS: [&str; 5] = ["B", "KiB", "MiB", "GiB", "TiB"];
    let mut value = bytes as f64;
    let mut unit = 0;
    while value >= 1024.0 && unit < UNITS.len() - 1 {
        value /= 1024.0;
        unit += 1;
    }
    if unit == 0 {
        format!("{} {}", bytes, UNITS[unit])
    } else {
        format!("{value:.1} {}", UNITS[unit])
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn classifies_only_allow_listed_artifacts() {
        assert_eq!(artifact_kind("node_modules"), Some("dependency"));
        assert_eq!(artifact_kind("target"), Some("build-output"));
        assert_eq!(artifact_kind("data"), None);
        assert_eq!(artifact_kind("dist"), None);
    }

    #[test]
    fn escapes_json_control_characters() {
        assert_eq!(json_escape("a\"b\\c\n"), "a\\\"b\\\\c\\n");
    }

    #[test]
    fn parses_nul_terminated_worktree_records() {
        let input = b"worktree /tmp/main\0HEAD aaa\0branch refs/heads/main\0\0worktree /tmp/wt with spaces\0HEAD bbb\0detached\0locked agent task\0\0";
        let parsed = parse_worktree_porcelain(input).unwrap();
        assert_eq!(parsed.len(), 2);
        assert_eq!(parsed[1].path, PathBuf::from("/tmp/wt with spaces"));
        assert!(parsed[1].detached);
        assert_eq!(parsed[1].locked.as_deref(), Some("agent task"));
    }

    #[test]
    fn formats_bytes_compactly() {
        assert_eq!(human_bytes(512), "512 B");
        assert_eq!(human_bytes(1024 * 1024), "1.0 MiB");
    }

    #[test]
    fn moves_only_an_exact_allow_listed_artifact() {
        let stamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let fixture =
            env::temp_dir().join(format!("mactidy-trash-test-{}-{stamp}", std::process::id()));
        let root = fixture.join("project");
        let artifact = root.join("node_modules");
        let trash = fixture.join("Trash");
        fs::create_dir_all(&artifact).unwrap();

        let options = TrashOptions {
            root: root.clone(),
            path: artifact.clone(),
            confirm: Some(artifact.clone()),
        };
        run_trash_to(options, &trash).unwrap();

        assert!(!artifact.exists());
        assert_eq!(fs::read_dir(&trash).unwrap().count(), 1);
        fs::remove_dir_all(&fixture).unwrap();
    }

    #[test]
    fn rejects_broad_system_roots() {
        assert!(reject_system_root(Path::new("/")).is_err());
        assert!(reject_system_root(Path::new("/private/var/folders")).is_err());
        assert!(reject_system_root(Path::new("/tmp/specific-task")).is_ok());
    }

    #[test]
    fn rejects_ref_option_injection_before_git() {
        let options = RetireOptions {
            repo: PathBuf::from("/does/not/matter"),
            path: PathBuf::from("/does/not/matter"),
            merged_into: "--help".into(),
            confirm: None,
        };
        assert!(run_retire_worktree(options).is_err());
    }
}
