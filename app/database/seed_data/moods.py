"""Seed data: The 20 type-beat moods and their vibe words."""
from __future__ import annotations


# ---------------------------------------------------------------- moods
# The 20 most common type-beat moods (BeatStars/YouTube/store taxonomy
# research): labels stay in English because that is what artists search.
# (name, description, icon — icons removed: text-only UI)
MOODS: list[tuple[str, str, str]] = [
    ("Dark", "Minor keys, heavy 808s; trap, drill, phonk", ""),
    ("Sad", "Emotional piano/guitar; emo trap, R&B", ""),
    ("Aggressive", "Distorted 808s, fast hats; trap, drill", ""),
    ("Hard", "Punchy street weight; drill, trap", ""),
    ("Chill", "Relaxed and laid-back; lo-fi, R&B", ""),
    ("Emotional", "Expressive, heartfelt melodies; trap, R&B", ""),
    ("Melodic", "Melody-forward; trap, drill, R&B", ""),
    ("Energetic", "Driving and fast; pop, jersey, rage", ""),
    ("Hype", "Club-ready intensity; jersey, rage, drill", ""),
    ("Bouncy", "Danceable bounce; jersey club, Detroit", ""),
    ("Smooth", "Silky grooves; R&B, soul", ""),
    ("Romantic", "Love songs; R&B, afrobeat, reggaeton", ""),
    ("Sexy", "Slow and seductive; R&B, dancehall", ""),
    ("Dreamy", "Hazy and reverberant; lo-fi, R&B, rage", ""),
    ("Melancholy", "Nostalgic sadness; boom bap, lo-fi", ""),
    ("Cinematic", "Big and dramatic; trap, drill", ""),
    ("Epic", "Triumphant and larger-than-life; trap, drill", ""),
    ("Uplifting", "Positive and motivational; pop, afrobeat", ""),
    ("Gritty", "Raw and dusty; boom bap, east coast", ""),
    ("Mysterious", "Suspenseful and eerie; phonk, drill", ""),
]

# mood -> vibe words (matched against EN+ES pools like GENRE_VIBES)


# mood -> vibe words (matched against EN+ES pools like GENRE_VIBES)
MOOD_VIBES: dict[str, list[str]] = {
    "Dark": ["dark", "midnight", "shadows", "ghost", "danger", "haunted", "cursed", "pressure", "silence", "smoke", "ritual", "omen", "noche", "sombra", "fantasma", "peligro", "presión", "oscuro", "medianoche"],
    "Sad": ["lonely", "lost", "broken", "rain", "rainy", "hollow", "empty", "silent", "silence", "memory", "midnight", "weep", "lluvia", "lágrima", "triste", "solo", "vacío", "noche", "silencio", "dolor", "corazón", "alma"],
    "Aggressive": ["savage", "reckless", "brutal", "violent", "strike", "fight", "explode", "crash", "blast", "scream", "thunder", "storm", "golpe", "trueno", "tormenta", "guerra", "batalla", "fuego", "gritos"],
    "Hard": ["heavy", "hard", "steel", "iron", "pressure", "block", "streets", "hustle", "grind", "thunder", "golpe", "presión", "barrio", "calle", "hierro", "acero"],
    "Chill": ["calm", "peaceful", "smooth", "float", "drift", "dream", "breeze", "soft", "gentle", "wave", "tranquilo", "suave", "ola", "mar", "cielo", "tardes"],
    "Emotional": ["desire", "lonely", "cry", "confess", "promise", "remember", "hope", "fear", "echo", "memory", "deseo", "amor", "corazón", "alma", "lágrima", "esperanza", "miedo", "promesas", "memoria"],
    "Melodic": ["melody", "harmony", "chord", "rhythm", "tune", "song", "hymn", "echo", "flow", "glide", "melodía", "armonía", "ritmo", "canción", "verso", "coro", "voz", "tono"],
    "Energetic": ["rush", "electric", "neon", "bounce", "dance", "race", "sprint", "blaze", "thunder", "lightning", "corre", "baila", "salta", "brilla", "fuego", "chispa"],
    "Hype": ["bounce", "dance", "loud", "noisy", "anthem", "banger", "rush", "blaze", "electric", "baila", "salta", "corre", "grita", "fuego", "noche"],
    "Bouncy": ["bounce", "groove", "swing", "dance", "rhythm", "tempo", "drum", "wave", "motion", "groove", "baila", "ritmo", "tambor", "tambores", "ola", "movimiento"],
    "Smooth": ["smooth", "silk", "satin", "velvet", "honey", "wine", "glide", "slide", "sway", "soft", "suave", "miel", "vino", "mar", "ola"],
    "Romantic": ["lover", "kiss", "rose", "moon", "desire", "tender", "gentle", "star", "dream", "slow", "amor", "beso", "abrazo", "rosa", "rosas", "luna", "estrella", "amante", "corazón"],
    "Sexy": ["velvet", "silk", "whisper", "midnight", "desire", "smooth", "wine", "smoke", "medianoche", "deseo", "miel", "vino", "mirada", "beso", "noche"],
    "Dreamy": ["dream", "hazy", "misty", "float", "drift", "lucid", "vivid", "echo", "mirage", "halo", "sueño", "sueños", "niebla", "luna", "estrella", "cielo"],
    "Melancholy": ["broken", "faded", "memory", "rain", "autumn", "dust", "static", "lonely", "empty", "hollow", "memoria", "lluvia", "otoño", "polvo", "ventana", "roto", "solo", "vacío", "triste", "noche"],
    "Cinematic": ["anthem", "prophecy", "legend", "myth", "saga", "thunder", "storm", "crown", "throne", "kingdom", "empire", "glory", "leyenda", "mito", "profecía", "gloria", "reino", "corona", "trueno", "himno"],
    "Epic": ["glory", "crown", "throne", "kingdom", "anthem", "legend", "gold", "diamond", "thunder", "empire", "gloria", "corona", "trono", "reino", "himno", "leyenda", "oro", "diamantes", "trueno", "tesoro"],
    "Uplifting": ["rise", "shine", "glow", "golden", "radiant", "bright", "hope", "faith", "dream", "heaven", "feliz", "esperanza", "fe", "cielo", "sol", "amanecer", "luces", "brilla", "sube"],
    "Gritty": ["rough", "rusted", "dust", "static", "vinyl", "tape", "streets", "block", "alley", "hustle", "grind", "polvo", "barrio", "calle", "callejón", "oxidado", "áspero"],
    "Mysterious": ["secret", "hidden", "shadows", "whisper", "ghost", "phantom", "omen", "midnight", "smoke", "secreto", "secretos", "sombra", "sombras", "fantasma", "fantasmas", "medianoche", "humo", "susurra"],
}
