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
    assert settings["MODEL_REPO"] == "bartowski/Llama-3.2-1B-Instruct-GGUF"
    assert settings["MODEL_FILENAME"] == "Llama-3.2-1B-Instruct-Q4_K_M.gguf"
    assert "1B" in settings["MODEL_NAME"]


def test_reference_file_exists():
    assert (ROOT / "knowledge.txt").exists()
    assert "knowledge.txt" in (ROOT / "model.py").read_text(encoding="utf-8")


def test_example_knowledge_is_active_and_labeled_demo():
    text = (ROOT / "knowledge.txt").read_text(encoding="utf-8")
    active = [line.strip() for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    assert any("24 ชั่วโมง" in line for line in active)
    assert any("จันทร์ถึงวันศุกร์" in line for line in active)
    assert "สถานการณ์จำลอง" in text


def test_prompt_does_not_copy_previous_bad_phrase():
    text = (ROOT / "model.py").read_text(encoding="utf-8")
    assert "หากมีข้อมูลยืนยันได้เพียงบางส่วน" not in text
    assert "ห้ามเดาหรือฟันธงเกินข้อมูล" in text


def test_short_prompt_and_small_history():
    tree = ast.parse((ROOT / "model.py").read_text(encoding="utf-8"))
    assignments = {
        target.id: node.value
        for node in tree.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }
    prompt_text = ast.literal_eval(assignments["SYSTEM_PROMPT"])
    assert len(prompt_text) < 500
    assert "ห้ามเดาหรือฟันธงเกินข้อมูล" in prompt_text
    assert "conversation[-6:]" in (ROOT / "model.py").read_text(encoding="utf-8")


def test_new_model_in_app():
    app = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "Meta Llama 3.2" in app
    assert "Qwen3.5" not in app


def test_chat_template_and_reasoning_filter_removed():
    source = (ROOT / "model.py").read_text(encoding="utf-8")
    assert 'chat_format="chatml"' not in source
    assert "def _hide_thinking" not in source
    assert 'if not has_text:' in source
    assert 'stream=False' in source


def test_first_boot_without_huggingface_cache_does_not_fail():
    """A fresh Streamlit instance has no HF cache: cleanup must be optional."""
    source = (ROOT / "model.py").read_text(encoding="utf-8")
    assert "cache_dir = Path(HF_HUB_CACHE)" in source
    assert "if not cache_dir.is_dir():" in source
    assert "except Exception as exc:" in source
