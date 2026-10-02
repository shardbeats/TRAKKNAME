"""Minimal deterministic Spanish adjective agreement (no NLP engine)."""
from __future__ import annotations

# base masculine-singular adjective -> (masc, fem) pairs for common endings
# Strategy: if noun gender known and adjective ends in -o/-os/-or/-án etc., inflect.


def agree_adjective(adjective: str, gender: str | None, number: str | None) -> str:
    adj = adjective.strip()
    if not adj or not gender:
        return adj
    g = gender.lower()
    n = (number or "singular").lower()
    low = adj.lower()

    def match_number(word: str) -> str:
        if n == "plural":
            if word.endswith("s"):
                return word
            if word.endswith(("á", "é", "í", "ó", "ú")):
                return word + "s"
            return word + "s"
        else:
            # singularize naive plural
            if low.endswith("es") and len(word) > 3:
                return word
            if word.endswith("s") and not low.endswith(("és", "is", "os", "as")):
                return word
            return word

    if g == "feminine":
        if low.endswith("o"):
            adj = adj[:-1] + "a"
        elif low.endswith("os") and n == "plural":
            adj = adj[:-2] + "as"
        elif low.endswith(("or", "án", "ón")):
            adj = adj + "a"
    result = match_number(adj)
    # preserve original capitalization pattern loosely
    return result


def agree_pair(noun: str, adjective: str, gender: str | None, number: str | None, order: str = "NOUN ADJ") -> tuple[str, str]:
    """Return (noun, adjective) with adjective agreed to noun."""
    return noun, agree_adjective(adjective, gender, number)
