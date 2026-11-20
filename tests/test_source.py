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


def test_active_model_is_upgraded():
    """Guard against accidentally restoring the retired model as the default."""
    tree = ast.parse((ROOT / "model.py").read_text(encoding="utf-8"))
    settings = {
        node.targets[0].id: ast.literal_eval(node.value)
        for node in tree.body
        if isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id in {"MODEL_REPO", "MODEL_FILENAME", "MODEL_NAME"}
    }
    assert settings["MODEL_REPO"] == "Qwen/Qwen2.5-1.5B-Instruct-GGUF"
    assert settings["MODEL_FILENAME"] == "qwen2.5-1.5b-instruct-q4_k_m.gguf"
    assert "1.5B" in settings["MODEL_NAME"]
