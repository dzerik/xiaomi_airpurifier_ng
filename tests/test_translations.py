"""Keep translations, placeholders, and translated exception usage synchronized."""

import ast
import json
from pathlib import Path
from string import Formatter

import pytest

ROOT = Path("custom_components/xiaomi_miio_airpurifier_ng")


def leaves(value, path=()):
    if not isinstance(value, dict):
        return {path: value}
    return {
        key: text
        for name, child in value.items()
        for key, text in leaves(child, (*path, name)).items()
    }


@pytest.mark.parametrize(
    "translation", sorted((ROOT / "translations").glob("*.json")), ids=lambda p: p.stem
)
def test_translation_keys_and_placeholders(translation):
    source = leaves(json.loads((ROOT / "strings.json").read_text()))
    translated = leaves(json.loads(translation.read_text()))
    assert translated.keys() == source.keys()
    for key, value in source.items():
        expected = {name for _, name, _, _ in Formatter().parse(value) if name}
        actual = {name for _, name, _, _ in Formatter().parse(translated[key]) if name}
        assert actual == expected, key


def test_action_errors_have_existing_translation_keys():
    exceptions = json.loads((ROOT / "strings.json").read_text()).get("exceptions", {})
    for path in ROOT.rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                continue
            if node.func.id not in {
                "HomeAssistantError",
                "ServiceValidationError",
                "ConfigEntryError",
            }:
                continue
            keywords = {kw.arg: kw.value for kw in node.keywords}
            assert "translation_key" in keywords, (path, node.lineno)
            assert keywords["translation_key"].value in exceptions, (path, node.lineno)
