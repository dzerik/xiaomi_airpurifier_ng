"""Release metadata must describe the same installable integration."""

import json
import subprocess
import sys
import tomllib
from datetime import datetime
from pathlib import Path

from miio.protocol import Message


def test_miio_packet_round_trip():
    """The pinned construct version preserves encrypted miIO payloads."""
    payload = {"id": 1, "method": "get_prop", "params": ["power"]}
    token = bytes.fromhex("00" * 16)
    packet = Message.build(
        {
            "data": {"value": payload},
            "header": {"value": {"device_id": b"\x00\x00\x00\x01", "ts": datetime(2026, 1, 1)}},
            "checksum": None,
        },
        token=token,
    )
    parsed = Message.parse(packet, token=token)
    assert parsed.data.value == payload
    assert parsed.header.value.device_id == b"\x00\x00\x00\x01"


def test_runtime_requirements_match_manifest():
    """Every runtime constraint is covered by both exact test environments."""
    from scripts.check_project import check_runtime_locks

    manifest = json.loads(
        Path("custom_components/xiaomi_miio_airpurifier_ng/manifest.json").read_text()
    )
    check_runtime_locks(Path("."), manifest["requirements"])


def test_bump_updates_both_versions(tmp_path):
    """A version bump cannot leave HA and project metadata out of sync."""
    component = tmp_path / "custom_components/xiaomi_miio_airpurifier_ng"
    component.mkdir(parents=True)
    (component / "manifest.json").write_text('{"version": "3.3.4"}\n')
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "3.3.4"\n')
    result = subprocess.run(
        [
            sys.executable,
            str(Path("scripts/bump_version.py").resolve()),
            "4.0.0",
            "--root",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads((component / "manifest.json").read_text())["version"] == "4.0.0"
    assert tomllib.loads((tmp_path / "pyproject.toml").read_text())["project"]["version"] == "4.0.0"


def test_metadata_checker_rejects_mismatch_with_optimization(tmp_path):
    """Release validation remains effective under python -O."""
    from shutil import copyfile

    component = tmp_path / "custom_components/xiaomi_miio_airpurifier_ng"
    component.mkdir(parents=True)
    (tmp_path / "scripts").mkdir()
    copyfile("scripts/check_project.py", tmp_path / "scripts/check_project.py")
    (component / "manifest.json").write_text('{"version":"1.0.0","requirements":[]}')
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nversion="2.0.0"\nrequires-python=">=3.14.2"\n'
    )
    (tmp_path / "hacs.json").write_text('{"homeassistant":"2026.3.4"}')
    (tmp_path / "requirements_test_common.txt").write_text("")
    result = subprocess.run(
        [sys.executable, "-O", str(tmp_path / "scripts/check_project.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "Release versions differ" in result.stderr


def test_bump_rejects_invalid_version_without_writes(tmp_path):
    """Invalid releases are rejected before either file is touched."""
    component = tmp_path / "custom_components/xiaomi_miio_airpurifier_ng"
    component.mkdir(parents=True)
    manifest = component / "manifest.json"
    manifest.write_text('{"version": "3.3.4"}\n')
    project = tmp_path / "pyproject.toml"
    project.write_text('[project]\nversion = "3.3.4"\n')
    before = (manifest.read_bytes(), project.read_bytes())
    result = subprocess.run(
        [
            sys.executable,
            str(Path("scripts/bump_version.py").resolve()),
            "banana",
            "--root",
            str(tmp_path),
        ],
        capture_output=True,
        check=False,
    )
    assert result.returncode != 0
    assert (manifest.read_bytes(), project.read_bytes()) == before
