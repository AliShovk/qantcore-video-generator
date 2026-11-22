---
name: youtube-shorts-pipeline
description: Полный цикл Shorts: YouTube Scout research → русский сценарий → Qantcore Video Generator → MP4.
---

# YouTube Shorts Pipeline

1. Создай уникальный RUN_DIR в ~/youtube-intelligence/runs/.
2. Запусти YouTube Research Agent. Он обязан собрать реальные данные Scout и создать research.json, research_report.md, handoff.json. Если API key отсутствует — остановись.
3. Передай эти три файла YouTube Script Agent. Получи video_spec.json, проверь факты и совместимость сцен.
4. После проверки запусти `python3 GENERATOR_ROOT/youtube_pipeline/render_short.py --spec RUN_DIR/video_spec.json`.
5. Верни концепцию, два лучших хука, сценарий, ссылки на референсы, пути MP4/SRT/manifest и предупреждения.

Не публикуй автоматически, не копируй MP4 в /var/www и не меняй production. Генератор сейчас делает типографические/инфографические анимации с TTS, не фотореалистичные AI-клипы.
