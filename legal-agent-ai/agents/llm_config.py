"""
Centralized LLM configuration and response text extraction for Nyaya Sahayaka.

Provides:
- get_llm(): returns ChatGoogleGenerativeAI with primary or fallback model,
  enforcing timeout and minimal retries to prevent latency bottlenecks.
- extract_text(): safely converts raw LangChain response content (string, list of dicts, etc.)
  into clean string markdown.
"""
import os
from typing import Any
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

PRIMARY_MODEL = os.environ.get("PRIMARY_GEMINI_MODEL", "gemini-2.5-flash")
FALLBACK_MODEL = os.environ.get("FALLBACK_GEMINI_MODEL", "gemini-2.5-flash-lite")

# Ordered list of models to try (primary first, then cascade)
_MODEL_CASCADE = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-flash-latest",
]


def extract_text(content: Any) -> str:
    """
    Safely converts LangChain AIMessage content into a plain string.
    Handles raw strings, lists of content blocks, and dictionary fragments.
    """
    if not content:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                if "text" in item:
                    parts.append(item["text"])
                elif "content" in item:
                    parts.append(str(item["content"]))
            elif hasattr(item, "text"):
                parts.append(item.text)
            elif isinstance(item, str):
                parts.append(item)
            else:
                parts.append(str(item))
        return "".join(parts).strip()
    return str(content).strip()


def get_llm(
    temperature: float = 0.0,
    fallback: bool = False,
    max_retries: int = 1,
    timeout: int = 25,
    max_output_tokens: int = None,
):
    """
    Returns a configured ChatGoogleGenerativeAI instance.
    Uses gemini-2.5-flash-lite (primary) or gemini-1.5-flash-8b (fallback).
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or not ChatGoogleGenerativeAI:
        return None

    model_name = FALLBACK_MODEL if fallback else PRIMARY_MODEL
    kwargs = {
        "model": model_name,
        "google_api_key": api_key,
        "temperature": temperature,
        "max_retries": max_retries,
        "timeout": timeout,
    }
    if max_output_tokens:
        kwargs["max_output_tokens"] = max_output_tokens

    return ChatGoogleGenerativeAI(**kwargs)


def get_llm_with_cascade(
    temperature: float = 0.0,
    max_retries: int = 1,
    timeout: int = 25,
    max_output_tokens: int = None,
):
    """
    Returns (llm, model_name) for the first available model in cascade.
    Does NOT invoke — just constructs. Use for manual try/except loops.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or not ChatGoogleGenerativeAI:
        return None, None

    for model_name in _MODEL_CASCADE:
        kwargs = {
            "model": model_name,
            "google_api_key": api_key,
            "temperature": temperature,
            "max_retries": max_retries,
            "timeout": timeout,
        }
        if max_output_tokens:
            kwargs["max_output_tokens"] = max_output_tokens
        return ChatGoogleGenerativeAI(**kwargs), model_name  # return first, caller handles exceptions

    return None, None
