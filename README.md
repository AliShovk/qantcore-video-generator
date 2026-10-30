# Qantcore Video Generator

Генератор вертикальных роликов 1080×1920 для обзоров и гайдов: несколько движков под разные типы контента, один общий постпродакшн (голос, музыка, маскот, субтитры).

Сделан для [qantcore.space](https://qantcore.space) — обзоры и гайды по AI-агентам.

## Что внутри

| Движок | Когда использовать | Код |
|---|---|---|
| **minibot** | Персонаж-робот, схемы из примитивов, быстрый рендер на PIL | `pkg/minibot/` |
| **htmlvid** | Типографика, count-up, CSS-анимации, скриншоты схем из статей | `pkg/rendering/` |
| **Manim** | Математические схемы: деревья, пайплайны, метрики | `scripts/orca_scene.py` |
| **whiteboard-animate** | Эффект рисования от руки | `scripts/whiteboard_*.py` |

Общее: озвучка Silero TTS (резерв — Piper), подложка и whoosh через numpy-микс, маскот с монетой, SRT.

## Установка

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt

# для Manim нужны системные библиотеки
sudo apt-get install -y libcairo2-dev libpango1.0-dev pkg-config build-essential

# голоса Silero подтягиваются torch.hub при первом запуске (~200 МБ)
```

Chrome/Chromium нужен для `htmlvid` (покадровый скриншот headless-браузера) и `ffmpeg` для сборки.

## Быстрый старт

```bash
# 1. ролик из HTML-сцены: правим review_context_mode.py, затем
python3 scripts/review_context_mode.py

# 2. ролик из схемы Manim
manim -qh -r 1080,1920 --fps 30 scripts/orca_scene.py OrcaScene
python3 scripts/post_orca.py

# 3. whiteboard-ролик
python3 scripts/whiteboard_graphify.py
```

Результат складывается в `output/reviews/*.mp4` и `*.srt`.

## Структура

```
pkg/minibot/       персонаж (14 векторных частей), сцена, объекты, голос, звук
pkg/rendering/     render.py (HTML→Chrome→FFmpeg), mascot.py (птица с монетой)
scripts/           готовые сценарии роликов: HTML, Manim, whiteboard
assets/            спрайт маскота, QR на сайт
```

## Правила, которые зашиты в код

- **Фон всегда белый**, чернила тёмные `#12161C`, акценты — тёмные варианты (`#0E9F8A`, `#2563EB`, `#B45309`). Светлые оттенки на белом не читаются.
- **Маскот** — внизу кадра, целиком, не перекрывает схемы и текст; на финальной плашке уходит.
- **Финал** — крупный адрес `qantcore.space` + QR, подпись «подробнее на сайте».
- **Звук** — дорожки складываются в numpy с лимитером; `ffmpeg amix` режет громкость каждого входа вдвое.
- **Субтитры** — текст из сценария, тайминг из фактической длительности реплик (Whisper — только для проверки границ).

## Зависимости-лицензии

Код — MIT (см. `LICENSE`). Шрифты Manrope и JetBrains Mono — OFL, в репозиторий не входят: положите `.ttf` в `assets/fonts/`. Маскот нарисован для проекта.

## Статус

Рабочий пайплайн, на нём собраны ролики: `orca`, `context-mode`, `graphify-wb`, `llama3-wb`, `hyperframes`, `grokbot`, `ecc`, `ai-seo`, `deepseek`, `tradingagents`.
