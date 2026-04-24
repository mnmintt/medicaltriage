"""
TriageAI Tools — Groq API Utility
Mirrors FinSight's clean agent pattern but uses Groq (ultra-fast inference).
Each agent calls call_groq() to get a JSON response.

Model used: llama-3.1-8b-instant — best Groq model for structured clinical JSON.
"""

import json
import os
import re
from groq import Groq

_client = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY", "")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY environment variable is not set")
        _client = Groq(api_key=api_key)
    return _client


def call_groq(system: str, user: str, max_tokens: int = 800) -> str:
    """
    Call Groq llama-3.1-8b-instant with a system + user prompt.
    Returns the raw text response string.
    Same interface as call_claude() — drop-in replacement across all agents.
    """
    client = _get_client()
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        max_tokens=max_tokens,
        temperature=0.2,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},   # force JSON output
    )
    return completion.choices[0].message.content


def parse_llm_json(raw_text: str) -> dict:
    """
    Strip markdown code fences from a Groq response and parse as JSON.
    Returns {'raw': ..., 'error': 'parse_failed'} on failure.
    """
    clean = raw_text.strip()

    if clean.startswith("```json"):
        clean = clean[len("```json"):]
    elif clean.startswith("```"):
        clean = clean[len("```"):]

    if clean.endswith("```"):
        clean = clean[:-len("```")]

    clean = clean.strip()

    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", clean, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {"raw": raw_text, "error": "parse_failed"}
