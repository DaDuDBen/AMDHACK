"""Deterministic safety filter for experiment requests."""

from __future__ import annotations

from typing import Any

SAFETY_RULES: list[dict[str, Any]] = []


def configure_safety_rules(rules: list[dict[str, Any]]) -> None:
    """Configure in-memory safety rules loaded from safety_blocklist.json."""
    global SAFETY_RULES
    SAFETY_RULES = rules


def check_safety(user_input: str) -> dict[str, Any]:
    """Check user input against deterministic keyword rules.

    Returns:
        {
            "is_safe": bool,
            "reason": str | None,
            "educational_note": str | None,
            "severity": str | None,
        }
    """
    lowered = (user_input or "").strip().lower()

    for rule in SAFETY_RULES:
        keywords = [kw.strip().lower() for kw in rule.get("keywords", []) if kw]
        if keywords and all(keyword in lowered for keyword in keywords):
            return {
                "is_safe": False,
                "reason": rule.get("reason"),
                "educational_note": rule.get("educational_note"),
                "severity": rule.get("severity"),
            }

    return {
        "is_safe": True,
        "reason": None,
        "educational_note": None,
        "severity": None,
    }
