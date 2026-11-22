#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cyrillic-aware editorial hook scorer. It does not predict views or retention."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

NUMBERS = re.compile(r"\b\d+(?:[.,]\d+)?\s?(?:%|тыс\.?|млн|секунд|сек\.?|минут|мин\.?|раза?|кг|км|лет)?\b", re.I)
DIRECT = re.compile(r"\b(ты|тебе|тебя|твой|твоя|твоё|твои|вы|вам|вас|ваш|ваша|ваше|ваши)\b", re.I)
STAKES = re.compile(r"\b(риск|опасн\w*|ошибк\w*|потер\w*|слом\w*|разруш\w*|стоил|цена|дорого|дешевле|выгод\w*|провал\w*|неудач\w*|выжив\w*|погиб\w*|невозможн\w*)\b", re.I)
CURIOSITY = re.compile(r"\b(почему|как|что если|зачем|откуда|оказывается|но|пока|до тех пор|секрет|причина|вот почему|что произошло)\b", re.I)
VAGUE = {"невероятный", "удивительный", "шокирующий", "безумный", "крутой", "лучший", "гениальный", "фантастический"}
FILLER = {"сегодня", "друзья", "привет", "добро", "пожаловать", "расскажу", "покажу", "видео", "канал", "подписывайтесь"}


def tokens(text: str) -> list[str]:
    return re.findall(r"[а-яёa-z0-9]+", text.lower())


def clamp(value: float) -> int:
    return max(0, min(100, round(value)))


def score(text: str) -> dict:
    words = tokens(text)
    if not words:
        return {"hook": text, "score": 0, "band": "weak", "dimensions": {}}
    number_count = len(NUMBERS.findall(text))
    vague_count = sum(word in VAGUE for word in words)
    filler_count = sum(word in FILLER for word in words)
    specificity = clamp(38 + min(number_count, 2) * 24 - vague_count * 14 - filler_count * 5)
    direct_address = clamp(32 + min(len(DIRECT.findall(text)), 2) * 30)
    stakes = clamp(30 + min(len(STAKES.findall(text)), 2) * 32 + (12 if number_count else 0))
    curiosity = clamp(28 + min(len(CURIOSITY.findall(text)), 2) * 26 + (12 if text.strip().endswith("?") else 0))
    count = len(words)
    brevity = 100 if 5 <= count <= 12 else clamp(100 - (5-count)*12 if count < 5 else 100 - (count-12)*8)
    dimensions = {
        "specificity": specificity,
        "direct_address": direct_address,
        "stakes": stakes,
        "curiosity_gap": curiosity,
        "brevity": brevity,
    }
    average = sum(dimensions.values()) / len(dimensions)
    total = clamp(0.6 * average + 0.4 * min(dimensions.values()))
    band = "strong" if total >= 72 else "workable" if total >= 55 else "weak"
    return {
        "hook": text, "score": total, "band": band,
        "dimensions": dimensions, "word_count": count,
        "note": "Редакционная эвристика, не прогноз просмотров или удержания."
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hook", action="append", default=[])
    parser.add_argument("--file")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    hooks = list(args.hook)
    if args.file:
        hooks.extend(
            line.strip()
            for line in Path(args.file).read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    if not hooks:
        parser.error("provide --hook or --file")
    results = sorted((score(hook) for hook in hooks), key=lambda item: item["score"], reverse=True)
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for item in results:
            print(str(item["score"]) + "/100 [" + item["band"] + "] " + item["hook"])
            for name, value in item["dimensions"].items():
                print("  " + name + ": " + str(value))
            print("  " + item["note"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
