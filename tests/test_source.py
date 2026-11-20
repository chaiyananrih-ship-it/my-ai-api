"""Lightweight checks that work without downloading model weights."""
from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]


def test_python_sources_parse():
    for name in ("app.py", "model.py"):
        ast.parse((ROOT / name).read_text(encoding="utf-8"))


def test_expected_files():
    assert (ROOT / "requirements.txt").exists()
    assert (ROOT / ".streamlit" / "config.toml").exists()


def test_repository_does_not_include_model_weights():
    assert not list(ROOT.rglob("*.gguf"))
