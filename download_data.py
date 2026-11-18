"""
Script reproducible para construir el corpus de 240 reseñas públicas de Steam
(60 por juego) combinando dos fuentes abiertas en GitHub:
  - `mrafifrbbn/steam-reviews` (GTA V, Dead by Daylight, Rocket League)
  - `mulhod/steam_reviews` (Counter-Strike)

Guarda el resultado en `data/steam_reviews.csv` para garantizar reproducibilidad
exacta.
"""

from __future__ import annotations

import html
import json
import os
import pandas as pd
import requests

MRAF_URL = (
    "https://raw.githubusercontent.com/mrafifrbbn/steam-reviews/main/data/steam_reviews.csv"
)
MULHOD_CS_URL = (
    "https://raw.githubusercontent.com/mulhod/steam_reviews/master/data/Counter_Strike.jsonlines"
)

MRAF_GAMES = [
    {"raw_title": "Grand Theft Auto V", "game": "GTA V", "genre": "Action / Open World"},
    {"raw_title": "Dead by Daylight", "game": "Dead by Daylight", "genre": "Survival Horror"},
    {"raw_title": "Rocket League®", "game": "Rocket League", "genre": "Sports / Arcade"},
]

TARGET_PER_GAME = 60
MIN_CHARS = 280
MAX_CHARS = 3000
OUTPUT_PATH = os.path.join("data", "steam_reviews.csv")


def clean_review_text(raw: str) -> str:
    """Decodifica entidades HTML y normaliza espacios en blanco."""
    unescaped = html.unescape(str(raw or ""))
    return " ".join(unescaped.split())


def is_mostly_english_ascii(text: str) -> bool:
    """Filtra textos en inglés con suficiente contenido alfabético."""
    if not text:
        return False
    ascii_chars = sum(1 for c in text if ord(c) < 128)
    alpha_chars = sum(1 for c in text if c.isascii() and c.isalpha())
    return (ascii_chars / len(text)) >= 0.95 and alpha_chars >= 180


def make_doc_id(game_name: str, index: int) -> str:
    slug = game_name.lower().replace(" ", "_").replace("-", "_")
    return f"{slug}_{index:02d}"


def extract_mraf_reviews(df_mraf: pd.DataFrame) -> list[dict]:
    """Extrae reseñas válidas de GTA V, Dead by Daylight y Rocket League."""
    rows: list[dict] = []
    for cfg in MRAF_GAMES:
        sub = df_mraf[df_mraf["title"] == cfg["raw_title"]]
        collected: list[dict] = []
        seen_prefixes: set[str] = set()

        for _, item in sub.iterrows():
            text = clean_review_text(item.get("review", ""))
            prefix = text[:120].lower()
            if (
                MIN_CHARS <= len(text) <= MAX_CHARS
                and is_mostly_english_ascii(text)
                and prefix not in seen_prefixes
            ):
                seen_prefixes.add(prefix)
                rec = str(item.get("recommendation", "")).strip()
                hours = pd.to_numeric(item.get("hour_played", 0.0), errors="coerce")
                helpful = pd.to_numeric(item.get("helpful", 0), errors="coerce")
                collected.append(
                    {
                        "doc_id": make_doc_id(cfg["game"], len(collected) + 1),
                        "game": cfg["game"],
                        "genre": cfg["genre"],
                        "recommendation": rec if rec else "Recommended",
                        "playtime_hours": round(float(0.0 if pd.isna(hours) else hours), 1),
                        "helpful_votes": int(0 if pd.isna(helpful) else helpful),
                        "text": text,
                    }
                )
                if len(collected) >= TARGET_PER_GAME:
                    break

        print(f"{cfg['game']} ({cfg['genre']}): {len(collected)} reseñas extraídas")
        rows.extend(collected)
    return rows


def extract_counter_strike_reviews() -> list[dict]:
    """Extrae vía streaming reseñas válidas de Counter-Strike desde mulhod/steam_reviews."""
    collected: list[dict] = []
    seen_prefixes: set[str] = set()

    with requests.get(MULHOD_CS_URL, stream=True, timeout=30) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines(decode_unicode=True):
            if not line:
                continue
            item = json.loads(line)
            text = clean_review_text(item.get("review", ""))
            prefix = text[:120].lower()
            if (
                MIN_CHARS <= len(text) <= MAX_CHARS
                and is_mostly_english_ascii(text)
                and prefix not in seen_prefixes
            ):
                seen_prefixes.add(prefix)
                hours = float(item.get("total_game_hours") or 0.0)
                helpful = int(item.get("num_found_helpful") or 0)
                collected.append(
                    {
                        "doc_id": make_doc_id("Counter-Strike", len(collected) + 1),
                        "game": "Counter-Strike",
                        "genre": "Tactical FPS",
                        "recommendation": str(item.get("rating", "Recommended")),
                        "playtime_hours": round(hours, 1),
                        "helpful_votes": helpful,
                        "text": text,
                    }
                )
                if len(collected) >= TARGET_PER_GAME:
                    break

    print(f"Counter-Strike (Tactical FPS): {len(collected)} reseñas extraídas")
    return collected


def main() -> None:
    os.makedirs("data", exist_ok=True)
    df_mraf = pd.read_csv(MRAF_URL)
    all_rows = extract_mraf_reviews(df_mraf)
    all_rows.extend(extract_counter_strike_reviews())

    df = pd.DataFrame(all_rows)
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
    print(f"\nCorpus guardado en {OUTPUT_PATH} ({len(df)} documentos en total).")


if __name__ == "__main__":
    main()
