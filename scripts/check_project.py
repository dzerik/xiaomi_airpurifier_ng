"""Validate release metadata used by Home Assistant and developer environments."""

import json
import tomllib
from pathlib import Path


def main() -> None:
    """Fail when installation or version metadata diverges."""
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads(
        (root / "custom_components/xiaomi_miio_airpurifier_ng/manifest.json").read_text()
    )
    project = tomllib.loads((root / "pyproject.toml").read_text())["project"]
    hacs = json.loads((root / "hacs.json").read_text())
    if not (manifest["version"] == project["version"]):
        raise SystemExit("Release versions differ")
    check_runtime_locks(root, manifest["requirements"])
    if not (project["requires-python"] == ">=3.14.2"):
        raise SystemExit("Python floor differs")
    if not (hacs["homeassistant"] == "2026.3.4"):
        raise SystemExit("Home Assistant floor differs")
    print(f"Release {manifest['version']}: metadata consistent")


def check_runtime_locks(root: Path, runtime: list[str]) -> None:
    """Both reproducible environments must satisfy every declared runtime constraint."""
    from packaging.requirements import Requirement

    for filename in ("requirements_test_lock.txt", "requirements_test_min_lock.txt"):
        pins = {}
        for line in (root / filename).read_text().splitlines():
            if not line or line.startswith(("#", " ", "-")):
                continue
            requirement = Requirement(line)
            pins[requirement.name] = next(
                (item.version for item in requirement.specifier if item.operator == "=="), None
            )
        for item in runtime:
            requirement = Requirement(item)
            version = pins.get(requirement.name)
            if version is None or version not in requirement.specifier:
                raise SystemExit(f"Runtime requirements differ: {item} in {filename}")


if __name__ == "__main__":
    main()
