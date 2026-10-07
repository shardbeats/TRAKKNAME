"""Shared dataclasses + errors for the generation engine."""
from __future__ import annotations

from dataclasses import dataclass, field


class GenerationError(Exception):
    pass


@dataclass
class GenerationResult:
    title: str
    genre_name: str
    genre_id: int | None
    language: str
    artists: list[str]
    pattern_name: str
    pattern_template: str
    moods: list[str] = field(default_factory=list)


@dataclass
class GenContext:
    """Everything generate_title resolves before attempting patterns."""
    genre_id: int | None
    genre_label: str
    language: str
    artists: list[str]
    related_ids: list[int]
    mood_names: list[str]
    mood_boost: dict[int, float]
    artist_boost: dict[int, float]
    artist_pool: str | None
