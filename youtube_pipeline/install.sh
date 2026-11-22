#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
PIPELINE_HOME=$HOME/youtube-intelligence
if printenv YOUTUBE_PIPELINE_HOME >/dev/null 2>&1; then PIPELINE_HOME=$(printenv YOUTUBE_PIPELINE_HOME); fi
HERMES_HOME=$HOME/.hermes
if printenv HERMES_HOME_OVERRIDE >/dev/null 2>&1; then HERMES_HOME=$(printenv HERMES_HOME_OVERRIDE); fi
SCOUT=$PIPELINE_HOME/sources/youtube-scout
WRITER=$PIPELINE_HOME/sources/youtube-agent-skill
mkdir -p "$PIPELINE_HOME/sources" "$PIPELINE_HOME/runs" "$PIPELINE_HOME/bin" "$HERMES_HOME/skills"
for bin in git python3; do command -v "$bin" >/dev/null || { echo "Missing $bin" >&2; exit 2; }; done
python3 -c 'import sys; assert sys.version_info >= (3,10), "Python 3.10+ required"'
if [ ! -d "$SCOUT/.git" ]; then git clone https://github.com/AgriciDaniel/youtube-scout.git "$SCOUT"; fi
if [ ! -d "$WRITER/.git" ]; then git clone https://github.com/Jakeschincariol/youtube-agent-skill.git "$WRITER"; fi
# Pin known reviewed commits for reproducibility.
git -C "$SCOUT" checkout --detach 8edb2b66cb2da969d54ece257d0a81047f5f8c8e
git -C "$WRITER" checkout --detach a2feb2104981a375ffd4f87ee04f4f5344ac43c6
python3 -m venv "$PIPELINE_HOME/.venv"
"$PIPELINE_HOME/.venv/bin/pip" install --upgrade pip
"$PIPELINE_HOME/.venv/bin/pip" install -e "$SCOUT" yt-dlp
mkdir -p "$HERMES_HOME/skills/youtube-script-agent"
install -m 0755 "$ROOT/youtube_pipeline/scout_to_research.py" "$PIPELINE_HOME/bin/scout_to_research.py"
install -m 0755 "$ROOT/youtube_pipeline/hookscore_ru.py" "$HERMES_HOME/skills/youtube-script-agent/hookscore_ru.py"
cp "$WRITER/skills/yt-script/hooks.json" "$HERMES_HOME/skills/youtube-script-agent/hooks.json"
for name in youtube-research-agent youtube-script-agent youtube-shorts-pipeline; do
  src=$ROOT/youtube_pipeline/hermes_skills/$name/SKILL.md
  dst=$HERMES_HOME/skills/$name
  if [ -d "$dst" ]; then cp -a "$dst" "$dst.backup.$(date +%Y%m%d-%H%M%S)"; fi
  mkdir -p "$dst"
  sed -e "s|GENERATOR_ROOT|$ROOT|g" -e "s|RUN_DIR|$PIPELINE_HOME/runs/current|g" "$src" > "$dst/SKILL.md"
  chmod -R go-rwx "$dst"
done
mkdir -p "$HOME/.config/scout"
if [ ! -f "$HOME/.config/scout/.env" ] && ! printenv YOUTUBE_API_KEY >/dev/null 2>&1; then
  printf '%s\n' 'YOUTUBE_API_KEY=PASTE_KEY_HERE' > "$HOME/.config/scout/.env.example"
  chmod 600 "$HOME/.config/scout/.env.example"
fi
printf 'YOUTUBE_SCOUT_HOME=%s\nYOUTUBE_SCOUT_PYTHON=%s\nYOUTUBE_PIPELINE_HOME=%s\n' "$SCOUT" "$PIPELINE_HOME/.venv/bin/python" "$PIPELINE_HOME" > "$PIPELINE_HOME/pipeline.env.example"
chmod 600 "$PIPELINE_HOME/pipeline.env.example"
echo "Installed Scout and Script Agent sources. Hermes skills: $HERMES_HOME/skills/youtube-*"
echo "Configure ~/.config/scout/.env, then verify with: hermes skills list"
