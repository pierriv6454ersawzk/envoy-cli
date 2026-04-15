"""Tests for envoy/template.py"""

import pytest
from pathlib import Path

from envoy.template import list_placeholders, render_template, render_template_file
from envoy.vault import save


# ---------------------------------------------------------------------------
# render_template
# ---------------------------------------------------------------------------

def test_render_template_substitutes_known_keys():
    result = render_template("Hello, {{ NAME }}!", {"NAME": "World"})
    assert result == "Hello, World!"


def test_render_template_leaves_unknown_placeholders():
    result = render_template("{{ UNKNOWN }}", {})
    assert result == "{{ UNKNOWN }}"


def test_render_template_multiple_occurrences():
    result = render_template("{{ A }} and {{ A }}", {"A": "x"})
    assert result == "x and x"


def test_render_template_whitespace_in_placeholder():
    result = render_template("{{  KEY  }}", {"KEY": "val"})
    assert result == "val"


def test_render_template_empty_variables():
    text = "DB_HOST={{ DB_HOST }}"
    assert render_template(text, {}) == text


# ---------------------------------------------------------------------------
# list_placeholders
# ---------------------------------------------------------------------------

def test_list_placeholders_basic():
    text = "{{ FOO }} {{ BAR }} {{ FOO }}"
    assert list_placeholders(text) == ["BAR", "FOO"]


def test_list_placeholders_empty():
    assert list_placeholders("no placeholders here") == []


# ---------------------------------------------------------------------------
# render_template_file
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_vault(tmp_path: Path) -> Path:
    vault = tmp_path / "default.vault"
    save(vault, "secret", {"API_KEY": "abc123", "HOST": "localhost"})
    return vault


def test_render_template_file_basic(tmp_path: Path, tmp_vault: Path):
    tpl = tmp_path / "config.tpl"
    tpl.write_text("HOST={{ HOST }}\nKEY={{ API_KEY }}\n")
    result = render_template_file(tpl, tmp_vault, "secret")
    assert result == "HOST=localhost\nKEY=abc123\n"


def test_render_template_file_writes_output(tmp_path: Path, tmp_vault: Path):
    tpl = tmp_path / "config.tpl"
    tpl.write_text("{{ HOST }}")
    out = tmp_path / "config.rendered"
    render_template_file(tpl, tmp_vault, "secret", output_path=out)
    assert out.read_text() == "localhost"


def test_render_template_file_missing_template_raises(tmp_path: Path, tmp_vault: Path):
    with pytest.raises(FileNotFoundError):
        render_template_file(tmp_path / "missing.tpl", tmp_vault, "secret")


def test_render_template_file_wrong_passphrase_raises(tmp_path: Path, tmp_vault: Path):
    tpl = tmp_path / "t.tpl"
    tpl.write_text("{{ HOST }}")
    with pytest.raises(ValueError):
        render_template_file(tpl, tmp_vault, "wrong-passphrase")
