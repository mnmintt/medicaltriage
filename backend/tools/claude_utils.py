"""
TriageAI Tools — Claude API Utility
Shared helper that mirrors FinSight's clean agent pattern but uses Claude
(Anthropic) instead of Gemini. Each agent calls this to get a JSON response.
"""

import json
import os
import re
import anthropic

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY environment variable is not set")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def call_claude(system: str, user: str, max_tokens: int = 800) -> str:
    """
    Call Claude claude-sonnet-4-5 with a system + user prompt.
    Returns the raw text response string.
    Mirrors exactly how FinSight calls Gemini — clean, minimal, no retries at this level.
    """
    client = _get_client()
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return message.content[0].text


def parse_llm_json(raw_text: str) -> dict:
    """
    Strip markdown code fences from a Claude response and parse as JSON.
    Identical to FinSight's parse_llm_json — returns {'raw': ..., 'error': 'parse_failed'} on failure.
    """
    clean = raw_text.strip()

    # Strip opening fence
    if clean.startswith("```json"):
        clean = clean[len("```json"):]
    elif clean.startswith("```"):
        clean = clean[len("```"):]

    # Strip closing fence
    if clean.endswith("```"):
        clean = clean[:-len("```")]

    clean = clean.strip()

    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        # Try extracting the first JSON object with regex as a fallback
        match = re.search(r"\{.*\}", clean, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {"raw": raw_text, "error": "parse_failed"}
