"""Qwen3 CPU chat inference with reusable instructions and local knowledge."""
from __future__ import annotations

import logging
import os
from pathlib import Path
from threading import Lock
from typing import Any, Iterator

import streamlit as st

MODEL_REPO = "bartowski/Qwen_Qwen3.5-0.8B-GGUF"
MODEL_FILENAME = "Qwen_Qwen3.5-0.8B-Q5_K_M.gguf"
MODEL_NAME = "Qwen3.5-0.8B Q5_K_M"
LEGACY_REPOS = (
    "Qwen/Qwen2.5-0.5B-Instruct-GGUF",
    "Qwen/Qwen2.5-1.5B-Instruct-GGUF",
    "ggml-org/Qwen3-1.7B-GGUF",
)
LOGGER = logging.getLogger(__name__)
CONTEXT_TOKENS = 2048
SYSTEM_PROMPT = (
    "คุณคือ Mali AI ผู้ช่วยตอบคำถามที่เข้าใจง่ายและเป็นธรรมชาติ "
    "อ่านคำถามให้ครบทุกประเด็น แล้วตอบตรงคำถามด้วยเหตุผลสั้นๆ "
    "ใช้ข้อมูลอ้างอิงเป็นหลัก หากรู้เพียงบางส่วน ให้ตอบส่วนที่รู้ก่อน "
    "แล้วบอกว่าส่วนใดยังยืนยันไม่ได้ ห้ามแต่งข้อเท็จจริงหรือฟันธงเกินข้อมูล "
    "เวลาทำการปกติไม่ได้ยืนยันว่าไม่มีเจ้าหน้าที่ในวันหยุด "
    "แยกเวลารับคำร้องของเว็บไซต์ออกจากเวลาทำงานของเจ้าหน้าที่ "
    "ห้ามอธิบายกฎหรือกระบวนการคิดของคุณ "
    "สำหรับคำถามทั่วไปที่ไม่เกี่ยวกับข้อมูลบริการ ให้ตอบจากความรู้ทั่วไปได้"
)


def reference_information() -> str:
    """Read editable facts from the repository for every new user question."""
    file = Path(__file__).with_name("knowledge.txt")
    if not file.is_file():
        return ""
    try:
        lines = file.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        LOGGER.warning("Cannot read knowledge file: %s", exc)
        return ""
    facts = [line.strip() for line in lines if line.strip() and not line.lstrip().startswith("#")]
    return "\n".join(facts)[:1200]


def remove_legacy_model_cache() -> None:
    """Remove only obsolete model revisions cached in this cloud instance."""
    from huggingface_hub import scan_cache_dir

    try:
        cache = scan_cache_dir()
        revisions = [
            revision.commit_hash
            for repo in cache.repos
            if repo.repo_id in LEGACY_REPOS and repo.repo_type == "model"
            for revision in repo.revisions
        ]
        if revisions:
            cache.delete_revisions(*revisions).execute()
            LOGGER.info("Cleared %d obsolete model revisions", len(revisions))
    except (OSError, ValueError) as exc:
        LOGGER.warning("Could not clean old model cache: %s", exc)


@st.cache_resource(show_spinner=False)
def load_engine() -> tuple[Any, Lock]:
    """Share one loaded model among Streamlit sessions to reduce memory use."""
    from huggingface_hub import hf_hub_download
    from llama_cpp import Llama

    remove_legacy_model_cache()
    path = hf_hub_download(repo_id=MODEL_REPO, filename=MODEL_FILENAME)
    model = Llama(
        model_path=path,
        n_ctx=CONTEXT_TOKENS,
        n_threads=max(1, min(2, os.cpu_count() or 2)),
        n_batch=64,
        n_gpu_layers=0,
        use_mmap=True,
        verbose=False,
        chat_format="chatml",
    )
    return model, Lock()


def _token_count(model: Any, content: str) -> int:
    return len(model.tokenize(content.encode("utf-8"), add_bos=False)) + 14


def create_prompt(model: Any, conversation: list[dict[str, str]], max_tokens: int) -> list[dict[str, str]]:
    """Send all rules and current knowledge on every request within context limits."""
    facts = reference_information()
    instructions = SYSTEM_PROMPT
    if facts:
        instructions += (
            "\n\nข้อมูลอ้างอิงที่ต้องใช้ตอบ (อย่าคาดเดานอกเหนือจากข้อมูล):\n" + facts
        )
    budget = CONTEXT_TOKENS - max_tokens - 120 - _token_count(model, instructions)
    if budget < 64:
        raise ValueError("ข้อมูลอ้างอิงยาวเกินไป กรุณาลดข้อความใน knowledge.txt")
    selected = []
    for message in reversed(conversation[-6:]):
        count = _token_count(model, message["content"])
        if count > budget:
            if not selected:
                raise ValueError("ข้อความยาวเกินไปสำหรับโมเดล กรุณาพิมพ์ให้สั้นลง")
            break
        selected.append({"role": message["role"], "content": message["content"]})
        budget -= count
    selected.reverse()
    while selected and selected[0]["role"] == "assistant":
        selected.pop(0)
    return [{"role": "system", "content": instructions}, *selected]


def _hide_thinking(chunks: Iterator[str]) -> Iterator[str]:
    """Keep any Qwen <think>...</think> segments out of the chat interface."""
    pending = ""
    inside = False
    open_tag = "<think>"
    close_tag = "</think>"
    for part in chunks:
        pending += part
        while pending:
            if inside:
                end = pending.find(close_tag)
                if end == -1:
                    pending = pending[-(len(close_tag) - 1):]
                    break
                pending = pending[end + len(close_tag):]
                inside = False
                continue
            start = pending.find(open_tag)
            if start != -1:
                if start:
                    yield pending[:start]
                pending = pending[start + len(open_tag):]
                inside = True
                continue
            safe = len(pending) - len(open_tag) + 1
            if safe > 0:
                yield pending[:safe]
                pending = pending[safe:]
            break
    if not inside and pending:
        yield pending


def generate_chunks(
    model: Any,
    lock: Lock,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
) -> Iterator[str]:
    """Prevent concurrent inference in one llama.cpp context."""
    with lock:
        response = model.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.85,
            repeat_penalty=1.05,
            stream=True,
        )

        def raw_chunks() -> Iterator[str]:
            for chunk in response:
                delta = chunk.get("choices", [{}])[0].get("delta", {})
                part = delta.get("content", "") if isinstance(delta, dict) else ""
                if part:
                    yield part

        yield from _hide_thinking(raw_chunks())
