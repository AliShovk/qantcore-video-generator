---
name: youtube-script-agent
description: Пишет оригинальные русские Shorts по исследованию, создаёт video_spec.json и запускает Qantcore Video Generator.
---

# YouTube Script Agent

Вход: research.json, research_report.md, handoff.json. Используй 21 hook formulas из MIT-проекта Jakeschincariol/youtube-agent-skill как структурные приёмы, не копируй чужие тексты.

Оценивай русский текст через:

```bash
python3 ~/.hermes/skills/youtube-script-agent/hookscore_ru.py --hook "ВАРИАНТ 1" --hook "ВАРИАНТ 2" --json
```

Это редакционная эвристика, не прогноз просмотров. Создай 5 разных хуков, выбери два лучших и объясни почему. Сценарий — 6–8 коротких сцен, русский язык, 30–60 секунд, цель около 38 секунд реального аудио. Без приветствий, пустых вступлений и выдуманных фактов.

ВАЖНО: текущий Qantcore Video Generator — кодовый 2D/инфографический рендерер с HTML/Chrome, PIL, TTS и FFmpeg, а не text-to-video. Он не генерирует фотореалистичные сцены животных, людей или локаций. Для MVP используй визуальные типы text, stat, steps, comparison, diagram. Если идея требует AI-клипов, отметь это как отдельную потребность.

Создай RUN_DIR/video_spec.json:

```json
{
  "id":"short-slug",
  "title":"Заголовок",
  "category":"НАУКА",
  "min_duration_seconds":30,
  "max_duration_seconds":60,
  "outro_seconds":2.2,
  "voice":{"backend":"silero","speaker":"eugene","gap":0.18},
  "style":{"accent":"#0E9F8A","accent2":"#2563EB"},
  "scenes":[
    {"voiceover":"Реплика диктора.","on_screen_text":"Текст на экране","visual":{"type":"text","eyebrow":"ХУК","headline":"Главная мысль","body":"Пояснение"}}
  ],
  "outro_text":"короткие видео и эксперименты"
}
```

Каждая сцена должна содержать voiceover и visual. Допустимые visual.type: text, stat, steps, comparison, diagram. Факты сверяй с research evidence. Реальную длительность проверяет TTS.

После проверки выполни:

```bash
python3 GENERATOR_ROOT/youtube_pipeline/render_short.py --spec RUN_DIR/video_spec.json
```

Верни MP4, SRT, manifest.json и отчёт. Не публикуй и не копируй файлы в production.
