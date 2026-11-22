# YouTube Shorts Intelligence Pipeline

Связка: YouTube Research Agent (YouTube Scout) → YouTube Script Agent (youtube-agent-skill, адаптация под русский/Hermes) → Qantcore Video Generator.

Установка из корня репозитория:

```bash
bash youtube_pipeline/install.sh
```

Нужны Python 3.10+, git, Chrome/Chromium, ffmpeg, зависимости текущего видеогенератора и YouTube Data API v3 key.

Ключ: Google Cloud Console → включить YouTube Data API v3 → создать API key. Хранить только в `~/.config/scout/.env`, chmod 600. Не коммитить.

Research создаёт `research.json`, `research_report.md`, `handoff.json`. Script Agent создаёт `video_spec.json`. Рендерер создаёт MP4, SRT и manifest в `output/youtube_shorts/<slug>/`.

Ограничения: Scout `--length short` — фильтр до 4 минут, а не доказательство Shorts; требуется проверка Format=Short, Vertical=true и duration <=180s. Публичные данные конкурентов не дают impressions, CTR и приватное удержание. Генератор создаёт типографические/инфографические анимации с TTS, не фотореалистичные клипы. Автопубликация и production deploy отключены.
