#!/usr/bin/env -S uv run --quiet
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Validate the repository's portable Agent Skills registry."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_ROOT = REPO_ROOT / "skills"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
XML_TAG_RE = re.compile(r"</?[A-Za-z][^>]*>")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)
ALLOWED_FIELDS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
LEGACY_PATTERNS = {
    "plugin skill path": re.compile(r"\bplugins/[a-z0-9-]+/skills/[a-z0-9-]+"),
    "plugin manifest path": re.compile(r"\.(?:claude|codex)-plugin"),
    "plugin marketplace path": re.compile(r"\.agents/plugins/marketplace\.json"),
    "removed Things command": re.compile(r"/mytodo\b"),
}


def markdown_anchor(heading: str) -> str:
    """Approximate GitHub-style heading anchors for local fragment checks."""
    heading = re.sub(r"<[^>]+>", "", heading).strip().lower()
    heading = re.sub(r"[^\w\s-]", "", heading, flags=re.UNICODE)
    return re.sub(r"[\s-]+", "-", heading).strip("-")


def anchors_for(path: Path) -> set[str]:
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    for heading in HEADING_RE.findall(path.read_text(encoding="utf-8")):
        base = markdown_anchor(heading)
        if not base:
            continue
        count = counts.get(base, 0)
        anchors.add(base if count == 0 else f"{base}-{count}")
        counts[base] = count + 1
    return anchors


def problem(path: Path, message: str) -> str:
    return f"{path.relative_to(REPO_ROOT)}: {message}"


def parse_frontmatter(path: Path, text: str, errors: list[str]) -> dict[str, object]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        errors.append(
            problem(path, "missing YAML frontmatter at the start of the file")
        )
        return {}

    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        errors.append(problem(path, f"invalid YAML frontmatter: {exc}"))
        return {}

    if not isinstance(data, dict):
        errors.append(problem(path, "frontmatter must be a YAML mapping"))
        return {}
    return data


def validate_links(
    skill_dir: Path, skill_md: Path, text: str, errors: list[str]
) -> None:
    for raw_target in LINK_RE.findall(text):
        target = raw_target.strip()
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
        target = target.split(maxsplit=1)[0]
        if (
            not target
            or target.startswith("#")
            or re.match(r"^[a-z][a-z0-9+.-]*:", target)
        ):
            continue

        path_target, _, fragment = target.partition("#")
        path_target = unquote(path_target)
        fragment = unquote(fragment)
        resolved = (skill_dir / path_target).resolve()
        try:
            resolved.relative_to(skill_dir.resolve())
        except ValueError:
            errors.append(
                problem(skill_md, f"relative link escapes the skill: {target}")
            )
            continue
        if not resolved.exists():
            errors.append(problem(skill_md, f"relative link does not exist: {target}"))
        elif (
            fragment
            and resolved.is_file()
            and resolved.suffix.lower() == ".md"
            and fragment not in anchors_for(resolved)
        ):
            errors.append(
                problem(skill_md, f"relative link anchor does not exist: {target}")
            )


def validate_skill(skill_dir: Path, seen: set[str], errors: list[str]) -> None:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        errors.append(problem(skill_dir, "missing SKILL.md"))
        return

    text = skill_md.read_text(encoding="utf-8")
    data = parse_frontmatter(skill_md, text, errors)
    if not data:
        return

    frontmatter = FRONTMATTER_RE.match(text)
    if frontmatter is not None and not text[frontmatter.end() :].strip():
        errors.append(problem(skill_md, "Markdown instructions are missing"))

    unexpected = sorted(set(data) - ALLOWED_FIELDS)
    if unexpected:
        errors.append(
            problem(
                skill_md, f"non-portable frontmatter fields: {', '.join(unexpected)}"
            )
        )

    name = data.get("name")
    if not isinstance(name, str) or not NAME_RE.fullmatch(name) or len(name) > 64:
        errors.append(
            problem(skill_md, "name must be 1-64 lowercase letters, digits, or hyphens")
        )
    else:
        if name != skill_dir.name:
            errors.append(
                problem(
                    skill_md, f"name {name!r} must match directory {skill_dir.name!r}"
                )
            )
        if name in seen:
            errors.append(problem(skill_md, f"duplicate skill name: {name}"))
        seen.add(name)

    description = data.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append(problem(skill_md, "description must be a non-empty string"))
    elif len(description) > 1024:
        errors.append(problem(skill_md, "description exceeds 1024 characters"))
    elif XML_TAG_RE.search(description):
        errors.append(problem(skill_md, "description must not contain XML tags"))

    compatibility = data.get("compatibility")
    if compatibility is not None and (
        not isinstance(compatibility, str) or not 1 <= len(compatibility) <= 500
    ):
        errors.append(
            problem(skill_md, "compatibility must be a 1-500 character string")
        )

    license_name = data.get("license")
    if license_name is not None and (
        not isinstance(license_name, str) or not license_name.strip()
    ):
        errors.append(problem(skill_md, "license must be a non-empty string"))

    allowed_tools = data.get("allowed-tools")
    if allowed_tools is not None and not isinstance(allowed_tools, str):
        errors.append(problem(skill_md, "allowed-tools must be a string"))

    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        errors.append(
            problem(skill_md, "metadata must be a mapping with a release version")
        )
    else:
        for key, value in metadata.items():
            if not isinstance(key, str) or not isinstance(value, str):
                errors.append(
                    problem(skill_md, "metadata keys and values must be strings")
                )
                break
        version = metadata.get("version")
        if not isinstance(version, str) or not SEMVER_RE.fullmatch(version):
            errors.append(
                problem(skill_md, "metadata.version must be a quoted SemVer string")
            )

    if len(text.splitlines()) > 500:
        errors.append(
            problem(skill_md, "SKILL.md exceeds the 500-line progressive-loading limit")
        )

    for label, pattern in LEGACY_PATTERNS.items():
        if pattern.search(text):
            errors.append(problem(skill_md, f"contains legacy {label}"))

    validate_links(skill_dir, skill_md, text, errors)


def main() -> int:
    errors: list[str] = []
    if not SKILLS_ROOT.is_dir():
        print("skills/: registry directory is missing", file=sys.stderr)
        return 1

    forbidden = [
        REPO_ROOT / "plugins",
        REPO_ROOT / ".claude-plugin",
        REPO_ROOT / ".codex-plugin",
        REPO_ROOT / ".agents" / "plugins",
        REPO_ROOT / "marketplace.json",
        REPO_ROOT / "scripts" / "sync-manifests.py",
    ]
    for path in forbidden:
        if path.exists():
            errors.append(problem(path, "plugin registry artifact must not exist"))

    wrapper_names = {".claude-plugin", ".codex-plugin"}
    for path in SKILLS_ROOT.rglob("*"):
        if (
            path.name in wrapper_names
            or path.name in {"plugin.json", "marketplace.json"}
            or (path.is_dir() and path.name == "plugins")
        ):
            errors.append(problem(path, "plugin wrapper artifact must not exist"))

    entries = sorted(SKILLS_ROOT.iterdir())
    skill_dirs = [
        entry for entry in entries if entry.is_dir() and not entry.name.startswith(".")
    ]
    unexpected = [
        entry
        for entry in entries
        if entry not in skill_dirs and not entry.name.startswith(".")
    ]
    for entry in unexpected:
        errors.append(
            problem(entry, "only skill directories are allowed directly under skills/")
        )
    if not skill_dirs:
        errors.append("skills/: registry contains no skills")

    seen: set[str] = set()
    for skill_dir in skill_dirs:
        validate_skill(skill_dir, seen, errors)

    if errors:
        print("Skill registry validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(skill_dirs)} portable skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
