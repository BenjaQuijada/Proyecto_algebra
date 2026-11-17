"""
Script reproducible para construir el corpus de reseñas de videojuegos en Steam
a partir del repositorio público `mulhod/steam_reviews` en GitHub:
https://github.com/mulhod/steam_reviews

Descarga vía streaming 60 reseñas sustanciales por juego (240 documentos en total)
de 4 títulos representativos de géneros bien diferenciados:
  - The Elder Scrolls V: Skyrim (RPG / Fantasía)
  - Sid Meier's Civilization V (Estrategia 4X)
  - Counter-Strike: Global Offensive (Shooter Táctico / FPS)
  - Football Manager 2015 (Simulación Deportiva)

Guarda el resultado en `data/steam_reviews.csv` para garantizar reproducibilidad
exacta sin necesidad de descargar los archivos completos (~40 MB).
"""

from __future__ import annotations

import json
import os
import pandas as pd
import requests

BASE_URL = "https://raw.githubusercontent.com/mulhod/steam_reviews/master/data"

GAMES = [
    {
        "file": "The_Elder_Scrolls_V.jsonlines",
        "game": "Skyrim",
        "genre": "RPG / Fantasy",
    },
    {
        "file": "Sid_Meiers_Civilization_5.jsonlines",
        "game": "Civilization V",
        "genre": "Strategy 4X",
    },
    {
        "file": "Counter_Strike_Global_Offensive.jsonlines",
        "game": "CS:GO",
        "genre": "Tactical FPS",
    },
    {
        "file": "Football_Manager_2015.jsonlines",
        "game": "Football Manager 2015",
        "genre": "Sports Sim",
    },
]

TARGET_PER_GAME = 60
MIN_CHARS = 300
MAX_CHARS = 3000
OUTPUT_PATH = os.path.join("data", "steam_reviews.csv")


def is_mostly_english_ascii(text: str) -> bool:
    """Filtra textos con alta proporción de caracteres ASCII alfabéticos."""
    if not text:
        return False
    ascii_chars = sum(1 for c in text if ord(c) < 128)
    alpha_chars = sum(1 for c in text if c.isascii() and c.isalpha())
    return (ascii_chars / len(text)) >= 0.95 and alpha_chars >= 200


def fetch_reviews_for_game(
    filename: str,
    game_name: str,
    genre: str,
    target_count: int = TARGET_PER_GAME,
) -> list[dict]:
    """Lee por streaming un archivo .jsonlines y extrae reseñas válidas."""
    url = f"{BASE_URL}/{filename}"
    collected: list[dict] = []
    seen_texts: set[str] = set()

    with requests.get(url, stream=True, timeout=30) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines(decode_unicode=True):
            if not line:
                continue
            item = json.loads(line)
            raw_text = (item.get("review") or "").strip()
            clean_text = " ".join(raw_text.split())

            if (
                MIN_CHARS <= len(clean_text) <= MAX_CHARS
                and is_mostly_english_ascii(clean_text)
                and clean_text not in seen_texts
            ):
                seen_texts.add(clean_text)
                collected.append(
                    {
                        "doc_id": f"{game_name.lower().replace(' ', '_').replace(':', '')}_{len(collected) + 1:02d}",
                        "game": game_name,
                        "genre": genre,
                        "rating": item.get("rating", ""),
                        "total_game_hours": item.get("total_game_hours", 0.0),
                        "num_found_helpful": item.get("num_found_helpful", 0),
                        "date_posted": item.get("date_posted", ""),
                        "text": clean_text,
                    }
                )
                if len(collected) >= target_count:
                    break

    return collected


def main() -> None:
    os.makedirs("data", exist_ok=True)
    all_rows: list[dict] = []

    for g in GAMES:
        rows = fetch_reviews_for_game(g["file"], g["game"], g["genre"])
        print(f"{g['game']} ({g['genre']}): {len(rows)} reseñas extraídas")
        all_rows.extend(rows)

    df = pd.DataFrame(all_rows)
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
    print(f"\nCorpus guardado en {OUTPUT_PATH} ({len(df)} documentos en total).")


if __name__ == "__main__":
    main()
