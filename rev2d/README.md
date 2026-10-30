# Rev2D: маскот Fox

Риг из одной иллюстрации (`source.png`) инструментом [Rev2D](https://github.com/RevStudio/Rev2D) (MIT): `avatar.json` → `fox.r2d.json`.

```bash
git clone https://github.com/RevStudio/Rev2D.git && cd Rev2D && npm ci
node bin/rev2d.js avatar validate <этот каталог>
node bin/rev2d.js avatar build <этот каталог>
node bin/rev2d.js avatar poses <этот каталог>
node bin/rev2d.js frames fox.r2d.json -o anim --anim idle --anim "talk@0.85" --fps 30 --to 4
```

11 параметров (поворот/наклон головы, веки, зрачки, рот, дыхание, наклон корпуса), 6 анимаций: idle, blink, talk, nod, look_around, sweep. Кадры собираются в ролик скриптом `scripts/build_fox.py`.
