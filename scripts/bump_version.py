"""Synchronize the integration and Python project release versions."""

import argparse
import json
import os
import re
import tempfile
import tomllib
from pathlib import Path


def atomic_write(path: Path, content: str) -> None:
    """Replace a metadata file only after its complete contents are written."""
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(content)
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def bump_version(root: Path, version: str) -> None:
    """Validate both metadata files before changing either version."""
    if not re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?", version):
        raise ValueError("Expected a Semantic Version such as 4.0.0")
    manifest_path = root / "custom_components/xiaomi_miio_airpurifier_ng/manifest.json"
    project_path = root / "pyproject.toml"
    old_manifest = manifest_path.read_text()
    old_project = project_path.read_text()
    manifest = json.loads(old_manifest)
    project = tomllib.loads(old_project)
    if manifest["version"] != project["project"]["version"]:
        raise ValueError("Existing versions are not synchronized")
    updated, count = re.subn(r'(?m)^version\s*=\s*"[^"]+"', f'version = "{version}"', old_project)
    if count != 1:
        raise ValueError("Expected one project version declaration")
    manifest["version"] = version
    atomic_write(manifest_path, json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    try:
        atomic_write(project_path, updated)
    except OSError:
        atomic_write(manifest_path, old_manifest)
        raise


def main() -> None:
    """Read the release version from the command line."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        bump_version(args.root, args.version)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
