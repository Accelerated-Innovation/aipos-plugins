"""The governed release contract of `aipos-opportunity-package`, checked on the skill folder.

discovery-engine runs this skill inside the engine from an exact, pinned release whose digest it
verifies (feature 31, ADR-AIG-044 §2A P4; requested in aipos-plugins#106). Its admission rule
refuses, in order: a missing manifest, a digest mismatch (of the package, the manifest, or the
release id), an executable asset, and an incompatible profile. This test is the control on our
side: it fails here, before a tag exists, for every byte the engine would refuse.

Each rule is a function over the folder, and each is also run on a planted violation, so every
check is proven able to fail rather than only seen to pass. Nothing here grades the skill's
coaching; `evals/evals.json` does that, model-graded, separately.

The package digest is the one the engine proposed on #106 and the manifest declares:

    find . -type f -print0 | LC_ALL=C sort -z | xargs -0 sha256sum | sha256sum

`package_digest` below is that definition in Python, so the digest a release states can be
recomputed without a shell. Its value is not asserted here: it is stated in the GitHub release
and `docs/rollout.md`, and it changes with every byte, by design.
"""

from __future__ import annotations

import hashlib
import os
import pathlib
import shutil
import stat

import pytest
import yaml

from skill_paths import skill_path

SKILL = skill_path("aipos-opportunity-package")

#: Mirrors discovery-engine `src/engine/domain/skill_release.py`. The profile its runtime admits,
#: and the suffixes that make a file an executable asset. Update the two together.
PROFILE = "soaa-agent-skills/0.2"
EXECUTABLE_SUFFIXES = frozenset(
    {".py", ".pyc", ".sh", ".bash", ".zsh", ".js", ".mjs", ".cjs", ".ts", ".ps1", ".bat", ".cmd",
     ".exe", ".rb", ".pl", ".so", ".dylib", ".dll", ".bin"}
)  # fmt: skip

#: The seven MCP reads `SKILL.md` names, and the capability each maps to (#106, item 3). The
#: engine resolves each capability to an in-process operation; external agents call the tool.
READ_MAPPING = {
    "get_problem": "pdg.problem.read",
    "list_evidence": "pdg.evidence.read",
    "get_lineage": "pdg.lineage.read",
    "list_problems": "pdg.problem.list",
    "list_opportunities": "pdg.opportunity.list",
    "get_work_item_links": "pdg.work_item_link.read",
    "get_evidence_text": "pdg.evidence_text.read",
}

#: What `SKILL.md` says it never calls (#106, item 4). The manifest must refuse at least these.
PROHIBITED = {"propose_problem", "attach_intent", "find_similar_problems"}


# ------------------------------------------------------------------ the rules


def files(folder: pathlib.Path):
    """Every non-directory entry under `folder` by its `/` path, links included, never entered.

    `os.walk` lists a symlink to a directory under `dirs` even with `followlinks=False`, so it
    is pulled out and yielded as an entry: it is a link, which a release may not contain, and
    it must never be walked into."""
    for root, dirs, names in os.walk(folder, followlinks=False):
        linked = [d for d in dirs if (pathlib.Path(root) / d).is_symlink()]
        dirs[:] = sorted(d for d in dirs if d not in linked)
        for name in sorted(names + linked):
            path = pathlib.Path(root) / name
            yield path.relative_to(folder).as_posix(), path


def package_digest(folder: pathlib.Path) -> str:
    """The engine's package digest: SHA-256 of the `sha256sum` listing, by `./path` bytes."""
    lines = []
    for name, path in sorted(files(folder), key=lambda item: item[0].encode()):
        if path.is_symlink() or not path.is_file():
            continue
        lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  ./{name}\n".encode())
    return hashlib.sha256(b"".join(lines)).hexdigest()


def front_matter(folder: pathlib.Path) -> dict:
    text = (folder / "SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---\n"), "SKILL.md has no front matter"
    return yaml.safe_load(text[4 : text.index("\n---", 4)])


def manifest(folder: pathlib.Path) -> tuple[dict, str]:
    """The manifest the front matter points at, and the digest of its exact bytes."""
    meta = front_matter(folder).get("metadata") or {}
    relative = meta.get("soaa-manifest", "")
    target = (folder / relative).resolve()
    target.relative_to(folder.resolve())  # refuses parent traversal
    data = target.read_bytes()
    return yaml.safe_load(data), hashlib.sha256(data).hexdigest()


def metadata_problems(folder: pathlib.Path) -> list[str]:
    """The four `soaa-*` keys: present, flat strings, and consistent with the manifest."""
    meta = front_matter(folder).get("metadata")
    if not isinstance(meta, dict):
        return ["SKILL.md declares no metadata mapping"]
    problems = [
        f"metadata.{key} is missing or not a non-empty string"
        for key in ("soaa-profile", "soaa-manifest", "soaa-manifest-digest", "soaa-release-id")
        if not isinstance(meta.get(key), str) or not meta[key]
    ]
    if problems:
        return problems
    if meta["soaa-profile"] != PROFILE:
        problems.append(f"soaa-profile {meta['soaa-profile']!r} is not {PROFILE!r}")
    if meta["soaa-manifest"] != "soaa/manifest.yaml" or ".." in meta["soaa-manifest"]:
        problems.append(f"soaa-manifest {meta['soaa-manifest']!r} is not soaa/manifest.yaml")
    try:
        doc, digest = manifest(folder)
    except (OSError, ValueError) as exc:
        return problems + [f"manifest unreadable: {exc}"]
    if meta["soaa-manifest-digest"] != f"sha256:{digest}":
        problems.append("soaa-manifest-digest does not match the manifest's bytes")
    identity = doc.get("identity") or {}
    if meta["soaa-release-id"] != identity.get("release_id"):
        problems.append("soaa-release-id does not match identity.release_id in the manifest")
    if doc.get("profile") != PROFILE:
        problems.append(f"manifest profile {doc.get('profile')!r} is not {PROFILE!r}")
    if identity.get("name") != folder.name:
        problems.append(f"identity.name {identity.get('name')!r} is not the folder name")
    version = str(identity.get("version", ""))
    if not version or f"-v{version}" not in str(identity.get("release_id", "")):
        problems.append("identity.release_id does not carry identity.version")
    return problems


def manifest_problems(folder: pathlib.Path) -> list[str]:
    """The eight areas are declared, the reads are mapped, and the writes are prohibited."""
    doc, _digest = manifest(folder)
    areas = ("identity", "applicability", "procedure", "conditions", "interfaces",
             "dependencies", "authority", "evaluation")  # fmt: skip
    problems = [f"manifest declares no {area!r} area" for area in areas if area not in doc]
    authority = doc.get("authority") or {}
    reads = authority.get("reads")
    if reads != READ_MAPPING:
        problems.append(f"authority.reads is not the seven-read mapping: {reads!r}")
    tools = set((doc.get("dependencies") or {}).get("tools") or [])
    if tools != set(READ_MAPPING):
        problems.append(f"dependencies.tools {sorted(tools)} differ from the mapped reads")
    prohibited = {p for p in authority.get("prohibited") or [] if isinstance(p, str)}
    missing = sorted(PROHIBITED - prohibited)
    if missing:
        problems.append(f"authority.prohibited omits {missing}")
    if prohibited & set(READ_MAPPING):
        problems.append("authority.prohibited names a read the skill depends on")
    for mapping_key in ("examples", "references"):
        for entry in (doc.get("procedure") or {}).get(mapping_key) or []:
            path = entry.get("path") if isinstance(entry, dict) else entry
            if not (folder / str(path)).is_file():
                problems.append(f"procedure.{mapping_key} names a missing file {path!r}")
    return problems


def asset_problems(folder: pathlib.Path) -> list[str]:
    """No symlink, no executable bit, no `#!`, no script or binary suffix (#106, constraints)."""
    problems = []
    for name, path in files(folder):
        if path.is_symlink():
            problems.append(f"{name} is a symlink")
            continue
        mode = path.stat().st_mode
        if mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
            problems.append(f"{name} has an executable bit")
        if path.suffix.lower() in EXECUTABLE_SUFFIXES:
            problems.append(f"{name} has an executable suffix")
        with path.open("rb") as handle:
            if handle.read(2) == b"#!":
                problems.append(f"{name} starts with #!")
    return problems


def skill_md_problems(folder: pathlib.Path) -> list[str]:
    """Standard Agent Skills validation still passes with `soaa/` ignored: name matches the
    folder, description is a non-empty string, and metadata values are all flat strings."""
    front = front_matter(folder)
    problems = []
    if front.get("name") != folder.name:
        problems.append("name does not match the folder")
    if not isinstance(front.get("description"), str) or not front["description"].strip():
        problems.append("description is not a non-empty string")
    for key, value in (front.get("metadata") or {}).items():
        if not isinstance(value, str):
            problems.append(f"metadata.{key} is not a string; Agent Skills metadata is flat")
    return problems


# ------------------------------------------------------------------ the release as committed


def test_the_release_declares_its_manifest_and_identity():
    assert metadata_problems(SKILL) == []


def test_the_manifest_declares_every_area_maps_every_read_and_refuses_every_write():
    assert manifest_problems(SKILL) == []


def test_the_release_holds_no_executable_asset():
    assert asset_problems(SKILL) == []


def test_skill_md_still_validates_as_a_plain_agent_skill():
    assert skill_md_problems(SKILL) == []


def test_the_evals_the_engine_builds_on_are_still_in_the_package():
    cases = yaml.safe_load((SKILL / "evals" / "evals.json").read_text(encoding="utf-8"))["evals"]
    assert len(cases) == 7


def test_the_package_digest_is_the_engines_definition(tmp_path):
    """The Python digest equals the shell pipeline's on a folder with nested paths and a
    byte-order case the locale could get wrong (`B` sorts before `a` in LC_ALL=C)."""
    folder = tmp_path / "pkg"
    (folder / "soaa").mkdir(parents=True)
    (folder / "SKILL.md").write_bytes(b"---\nname: pkg\n---\n")
    (folder / "soaa" / "manifest.yaml").write_bytes(b"identity: {}\n")
    (folder / "a.md").write_bytes(b"a\n")
    (folder / "B.md").write_bytes(b"B\n")
    listing = b"".join(
        hashlib.sha256((folder / name).read_bytes()).hexdigest().encode() + b"  ./" + name.encode() + b"\n"
        for name in ("B.md", "SKILL.md", "a.md", "soaa/manifest.yaml")
    )
    assert package_digest(folder) == hashlib.sha256(listing).hexdigest()
    assert package_digest(SKILL) == package_digest(SKILL)  # deterministic on the real folder


# ------------------------------------------------------------------ every rule can fail


@pytest.fixture
def copy(tmp_path):
    target = tmp_path / SKILL.name
    shutil.copytree(SKILL, target)
    return target


def _rewrite(path: pathlib.Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert old in text
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def test_a_changed_manifest_byte_is_a_digest_mismatch(copy):
    (copy / "soaa" / "manifest.yaml").write_bytes(
        (copy / "soaa" / "manifest.yaml").read_bytes() + b"\n# one more byte\n"
    )
    assert any("soaa-manifest-digest" in p for p in metadata_problems(copy))
    assert package_digest(copy) != package_digest(SKILL)


def test_a_release_id_that_differs_from_the_manifest_is_refused(copy):
    _rewrite(copy / "SKILL.md", "skill-opportunity-package-v", "skill-opportunity-package-vX")
    assert any("soaa-release-id" in p for p in metadata_problems(copy))


def test_a_missing_metadata_key_is_refused(copy):
    _rewrite(copy / "SKILL.md", "  soaa-profile:", "  soaa-profil:")
    assert any("soaa-profile" in p for p in metadata_problems(copy))


def test_a_manifest_outside_the_folder_is_refused(copy):
    _rewrite(copy / "SKILL.md", '"soaa/manifest.yaml"', '"../manifest.yaml"')
    assert metadata_problems(copy)


def test_an_unmapped_read_is_refused(copy):
    _rewrite(copy / "soaa" / "manifest.yaml", "    get_lineage: pdg.lineage.read\n", "")
    assert any("authority.reads" in p for p in manifest_problems(copy))


def test_a_write_that_is_not_prohibited_is_refused(copy):
    _rewrite(copy / "soaa" / "manifest.yaml", "    - attach_intent\n", "")
    assert any("attach_intent" in p for p in manifest_problems(copy))


def test_a_missing_area_is_refused(copy):
    _rewrite(copy / "soaa" / "manifest.yaml", "\nevaluation:\n", "\nevaluations:\n")
    assert any("'evaluation'" in p for p in manifest_problems(copy))


@pytest.mark.parametrize(
    ("name", "content", "mode"),
    [
        ("scripts/run.sh", b"echo hi\n", 0o644),
        ("helper.py", b"print(1)\n", 0o644),
        ("references/notes.md", b"notes\n", 0o755),
        ("references/run", b"#!/bin/sh\n", 0o644),
    ],
    ids=["script-suffix", "python", "executable-bit", "shebang"],
)
def test_an_executable_asset_is_refused(copy, name, content, mode):
    path = copy / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    path.chmod(mode)
    assert asset_problems(copy)


def test_a_symlink_is_refused(copy):
    (copy / "link.md").symlink_to(copy / "SKILL.md")
    assert any("symlink" in p for p in asset_problems(copy))


def test_a_symlink_to_a_directory_is_refused_and_never_entered(copy):
    """`os.walk` hides a linked directory under `dirs`; it must surface as a link, and the
    files behind it must not be listed twice or enter the digest."""
    (copy / "linked-evals").symlink_to(copy / "evals", target_is_directory=True)
    names = [name for name, _ in files(copy)]
    assert "linked-evals" in names and not any(n.startswith("linked-evals/") for n in names)
    assert any("linked-evals is a symlink" in p for p in asset_problems(copy))
    assert package_digest(copy) == package_digest(SKILL)  # a link adds no bytes; admission refuses it


def test_nested_metadata_fails_plain_validation(copy):
    _rewrite(copy / "SKILL.md", '  soaa-profile: "soaa-agent-skills/0.2"',
             "  soaa-profile:\n    nested: true")  # fmt: skip
    assert any("flat" in p for p in skill_md_problems(copy))


# ------------------------------------------------------------------ the published digest

ROLLOUT = pathlib.Path(__file__).resolve().parents[1] / "docs" / "rollout.md"


def published_digest(text: str) -> str:
    """The package digest `docs/rollout.md` states for the release the manifest declares: the
    first fenced 64-hex block after the first mention of that exact release id."""
    import re

    release_id = manifest(SKILL)[0]["identity"]["release_id"]
    assert release_id in text, f"rollout.md does not mention {release_id}"
    match = re.search(r"```\n([0-9a-f]{64})\n```", text[text.index(release_id):])
    assert match, f"rollout.md states no digest after {release_id}"
    return match.group(1)


def test_the_digest_rollout_publishes_is_the_folders():
    """The engine pins what the release notes state. A folder edit without a new stated digest
    would ship bytes the engine refuses, so the two must agree in every commit."""
    assert published_digest(ROLLOUT.read_text(encoding="utf-8")) == package_digest(SKILL)


def test_a_stale_published_digest_is_caught(copy):
    (copy / "SKILL.md").write_bytes((copy / "SKILL.md").read_bytes() + b"\n")
    assert published_digest(ROLLOUT.read_text(encoding="utf-8")) != package_digest(copy)
