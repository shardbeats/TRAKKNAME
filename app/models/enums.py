from __future__ import annotations

LANGUAGES = ("en", "es")
PARTS_OF_SPEECH = ("verb", "adjective", "noun")
GENDERS = ("masculine", "feminine", "neutral")
NUMBERS = ("singular", "plural")

LANGUAGE_LABELS = {"en": "English", "es": "Spanish"}

# Artist pool selector, driven ONLY by artists.language (single indexed
# predicate). Region stays as informational metadata.
ARTIST_POOLS = {"all": "All", "es": "En español", "en": "English"}
POOL_EMPTY_TEXT = {
    "all": "No artists configured for this genre.",
    "es": "No Spanish-language artists for this genre.",
    "en": "No English-language artists for this genre.",
    # legacy value from the region-based pool; mapped to "es" on load
    "latam": "No Spanish-language artists for this genre.",
}
# Legacy pool values -> current ones (settings + history display).
LEGACY_POOL_MAP = {"latam": "es"}
