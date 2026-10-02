"""Pattern rendering: tokens ADJ/NOUN/VERB are slots, anything else is a literal."""
from __future__ import annotations

SLOT_MAP = {"ADJ": "adjective", "ADJECTIVE": "adjective", "NOUN": "noun", "VERB": "verb"}


def parse_template(template: str) -> list[tuple[str, str]]:
    """Return list of (kind, value): kind in {'slot','literal'}."""
    parts: list[tuple[str, str]] = []
    for tok in template.split():
        up = tok.upper()
        if up in SLOT_MAP:
            parts.append(("slot", SLOT_MAP[up]))
        else:
            parts.append(("literal", tok))
    return parts


def slots_in_template(template: str) -> list[str]:
    return [v for k, v in parse_template(template) if k == "slot"]
