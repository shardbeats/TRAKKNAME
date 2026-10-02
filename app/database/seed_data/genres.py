"""Seed data: Genres, genre relations and genre vibe words."""
from __future__ import annotations


GENRES: list[tuple[str, str]] = [
    ("Trap", "Heavy 808s, dark street luxury"),
    ("Hip Hop", "Classic rap energy"),
    ("Boom Bap", "90s dusty drums"),
    ("Drill", "Sliding 808s, cold streets"),
    ("R&B", "Smooth, intimate, velvet"),
    ("Soul", "Warm, gospel-tinged"),
    ("Lo-Fi", "Dusty, nostalgic, chill"),
    ("Reggaeton", "Dembow perreo"),
    ("Latin Trap", "Spanish trap nocturno"),
    ("Jersey Club", "Bouncy club energy"),
    ("House", "Four on the floor"),
    ("Tech House", "Minimal rolling groove"),
    ("Deep House", "Warm deep chords"),
    ("Afrobeat", "Afro-fusion groove"),
    ("Dancehall", "Caribbean bounce"),
    ("Pop", "Bright catchy hooks"),
    ("Phonk", "Memphis cowbell drift"),
    ("West Coast", "G-funk glide"),
    ("East Coast", "Gritty NYC bars"),
    ("Experimental", "Left-field textures"),
]

# artist -> [(genre, weight)]


GENRE_RELATIONS: list[tuple[str, str, float]] = [
    ("Trap", "Hip Hop", 1.0), ("Trap", "Drill", 0.8), ("Trap", "Latin Trap", 0.6),
    ("Hip Hop", "Boom Bap", 0.7), ("Hip Hop", "West Coast", 0.6), ("Hip Hop", "East Coast", 0.6),
    ("Drill", "Trap", 0.8), ("Drill", "Hip Hop", 0.5),
    ("R&B", "Soul", 0.9), ("R&B", "Hip Hop", 0.5),
    ("Soul", "R&B", 0.9), ("Soul", "Lo-Fi", 0.5),
    ("Lo-Fi", "Boom Bap", 0.7), ("Lo-Fi", "Soul", 0.5),
    ("Reggaeton", "Latin Trap", 0.9), ("Reggaeton", "Dancehall", 0.6),
    ("Latin Trap", "Reggaeton", 0.9), ("Latin Trap", "Trap", 0.7),
    ("House", "Deep House", 0.8), ("House", "Tech House", 0.8),
    ("Afrobeat", "Dancehall", 0.6), ("Afrobeat", "R&B", 0.5),
    ("Phonk", "Trap", 0.6), ("Phonk", "Experimental", 0.4),
    ("West Coast", "Hip Hop", 0.7), ("East Coast", "Boom Bap", 0.8),
    ("Pop", "R&B", 0.5), ("Pop", "House", 0.4),
]


# genre -> vibe words (matched case-insensitively against EN+ES pools)
GENRE_VIBES: dict[str, list[str]] = {
    "Trap": ["pressure", "money", "chrome", "drip", "night", "danger", "ghost", "ice", "motion", "midnight", "savage", "toxic", "noche", "presión", "dinero", "hielo", "peligro", "fantasma"],
    "Drill": ["cold", "street", "shadow", "pressure", "danger", "block", "rage", "night", "frío", "calle", "sombra", "noche", "peligro"],
    "R&B": ["desire", "velvet", "touch", "midnight", "love", "silence", "dream", "slow", "deseo", "silencio", "sueño", "noche", "miel"],
    "Soul": ["velvet", "honey", "church", "choir", "prayer", "soul", "heart", "miel", "coro", "oración", "alma", "corazón"],
    "Lo-Fi": ["rain", "memory", "coffee", "window", "dream", "dust", "autumn", "static", "lluvia", "memoria", "polvo", "ventana", "sueño"],
    "Reggaeton": ["fire", "dance", "night", "heat", "motion", "bounce", "fuego", "noche", "calle", "baile"],
    "Latin Trap": ["noche", "calle", "fuego", "sueño", "presión", "peligro", "night", "street", "fire", "pressure"],
    "Phonk": ["ghost", "phantom", "midnight", "drift", "chrome", "smoke", "fantasma", "medianoche", "humo"],
    "House": ["lights", "motion", "night", "pulse", "wave", "luces", "noche", "pulso", "ola"],
    "Afrobeat": ["sun", "dance", "golden", "motion", "sol", "oro", "baile"],
    "Boom Bap": ["streets", "concrete", "vinyl", "tape", "raw", "barrio", "calle"],
    "Experimental": ["static", "noise", "void", "echo", "ruido", "eco", "vacío"],
}
