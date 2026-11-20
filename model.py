"""Download a public GGUF model once and run CPU inference with llama.cpp."""
from __future__ import annotations

import os
from threading import Lock
from typing import Any, Iterator

import streamlit as st

MODEL_REPO = "Qwen/Qwen2.5-0.5B-Instruct-GGUF"
MODEL_FILENAME = "qwen2.5-0.5b-instruct-q4_k_m.gguf"
MODEL_NAME = "Qwen2.5-0.5B-Instruct Q4_K_M"
CONTEXT_TOKENS = 2048
SYSTEM_PROMPT = (
    "คุณชื่อ Mali AI เป็นผู้ช่วย AI ที่สุภาพและเป็นมิตร "
    "ตอบเป็นภาษาไทยเมื่อผู้ใช้ถามภาษาไทย และตอบสั้นชัดเจน "
    "หากไม่ทราบคำตอบ ให้ยอมรับว่าไม่แน่ใจ อย่าสร้างข้อเท็จจริงขึ้นมาเอง "
    "คุณเป็นโมเดล AI ขนาดเล็กและไม่สามารถท่องเว็บหรือดูภาพได้"
)


@st.cache_resource(show_spinner=False)
def load_engine() -> tuple[Any, Lock]:
    """Streamlit shares one model instance across sessions to keep RAM manageable."""
    from huggingface_hub import hf_hub_download
    from llama_cpp import Llama

    path = hf_hub_download(repo_id=MODEL_REPO, filename=MODEL_FILENAME)
    model = Llama(
        model_path=path,
        n_ctx=CONTEXT_TOKENS,
        n_threads=max(1, min(2, os.cpu_count() or 2)),
        n_batch=128,
        n_gpu_layers=0,
        use_mmap=True,
        verbose=False,
        chat_format="chatml",
    )
    return model, Lock()


def _token_count(model: Any, content: str) -> int:
    return len(model.tokenize(content.encode("utf-8"), add_bos=False)) + 14


def create_prompt(model: Any, conversation: list[dict[str, str]], max_tokens: int) -> list[dict[str, str]]:
    """Fit the newest messages into a small context, leaving space for output."""
    budget = CONTEXT_TOKENS - max_tokens - 120 - _token_count(model, SYSTEM_PROMPT)
    selected = []
    for message in reversed(conversation[-14:]):
        count = _token_count(model, message["content"])
        if count > budget:
            if not selected:
                raise ValueError("ข้อความยาวเกินไปสำหรับโมเดลขนาดเล็ก กรุณาพิมพ์ให้สั้นลง")
            break
        selected.append({"role": message["role"], "content": message["content"]})
        budget -= count
    selected.reverse()
    while selected and selected[0]["role"] == "assistant":
        selected.pop(0)
    return [{"role": "system", "content": SYSTEM_PROMPT}, *selected]


def generate_chunks(
    model: Any,
    lock: Lock,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
) -> Iterator[str]:
    """Serialize inference: llama.cpp context should not be shared concurrently."""
    with lock:
        response = model.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.9,
            repeat_penalty=1.1,
            stream=True,
        )
        for chunk in response:
            delta = chunk.get("choices", [{}])[0].get("delta", {})
            part = delta.get("content", "") if isinstance(delta, dict) else ""
            if part:
                yield part
