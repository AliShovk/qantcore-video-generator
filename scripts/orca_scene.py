"""Orca: флот coding-агентов в параллельных worktrees. Manim, 1080×1920, ~24 с."""
from manim import (
    DOWN, LEFT, RIGHT, UP, Arrow, Create, FadeIn, FadeOut, Indicate, Line,
    RoundedRectangle, Scene, Text, VGroup, Write, config,
)

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 30
config.background_color = "#FFFFFF"
config.frame_width = 4.5
config.frame_height = 8.0

TEAL = "#0E9F8A"
BLUE = "#2563EB"
GREY = "#5B6B7A"
WHITE = "#12161C"
AMBER = "#B45309"


def t(s, size=22, color=WHITE, weight="BOLD"):
    return Text(s, font="DejaVu Sans", font_size=size, color=color, weight=weight)


class OrcaScene(Scene):
    def construct(self):
        # титул
        title = t("Orca", 52)
        sub = t("флот coding-агентов", 19, TEAL, "NORMAL")
        note = t("34 CLI-агента · MIT · v1.4.237", 12, GREY, "NORMAL")
        head = VGroup(title, sub, note).arrange(DOWN, buff=0.16).move_to(UP * 2.9)
        self.play(FadeIn(title, shift=UP * 0.15), run_time=0.9)
        self.play(FadeIn(sub), FadeIn(note), run_time=0.8)
        self.wait(1.2)

        # промпт
        prompt = RoundedRectangle(width=2.2, height=0.62, corner_radius=0.12,
                                  fill_color="#F2F6F8", fill_opacity=1,
                                  stroke_color=BLUE, stroke_width=2)
        prompt_lbl = t("1 промпт", 17).move_to(prompt)
        prompt_grp = VGroup(prompt, prompt_lbl).move_to(UP * 1.75)
        self.play(FadeIn(prompt_grp, shift=DOWN * 0.1), run_time=0.6)

        # ствол и ветки
        names = ["Claude Code", "Codex", "OpenCode", "Gemini", "Cursor"]
        boxes = VGroup()
        for i, name in enumerate(names):
            box = RoundedRectangle(width=2.15, height=0.5, corner_radius=0.1,
                                   fill_color="#F7FAFB", fill_opacity=1,
                                   stroke_color=TEAL, stroke_width=1.4)
            lbl = t(f"worktree {i + 1}", 13).move_to(box.get_center() + UP * 0.085)
            who = t(name, 10, GREY, "NORMAL").move_to(box.get_center() + DOWN * 0.115)
            boxes.add(VGroup(box, lbl, who))
        boxes.arrange(DOWN, buff=0.2).move_to(RIGHT * 0.55 + DOWN * 0.75)

        trunk_x = -1.45
        y0 = prompt_grp.get_bottom()[1] - 0.08
        y1 = boxes[-1][0].get_center()[1]
        trunk_h = Line([prompt_grp.get_center()[0], y0, 0], [trunk_x, y0, 0],
                       stroke_width=1.6, color=TEAL)
        trunk_v = Line([trunk_x, y0, 0], [trunk_x, y1, 0], stroke_width=1.6, color=TEAL)
        trunk = VGroup(trunk_h, trunk_v)
        self.play(Create(trunk_h), Create(trunk_v), run_time=0.6)

        conns = VGroup()
        for b in boxes:
            conn = Line([trunk_x, b[0].get_center()[1], 0], b[0].get_left() + LEFT * 0.03,
                        stroke_width=1.4, color=TEAL)
            conns.add(conn)
            self.play(Create(conn), FadeIn(b, shift=RIGHT * 0.08), run_time=0.26)

        self.wait(2.2)

        # победитель и мерж
        win = boxes[2]
        self.play(win[0].animate.set_stroke(AMBER, width=2.6).set_fill(AMBER, 0.12), run_time=0.4)
        self.play(Indicate(win, color=AMBER, scale_factor=1.04), run_time=0.8)
        for b in boxes:
            if b is not win:
                b.animate.set_opacity(0.3)
        self.wait(0.6)

        merge_lbl = t("мерж победителя", 11, AMBER, "NORMAL").move_to(LEFT * 1.3 + DOWN * 2.55)
        self.play(FadeIn(merge_lbl), run_time=0.5)
        self.wait(2.6)

        # цифры
        self.play(FadeOut(VGroup(prompt_grp, boxes, trunk, conns, merge_lbl)), run_time=0.5)
        stats = VGroup(
            VGroup(t("102,6k", 22), t("звёзд GitHub", 9, GREY, "NORMAL")).arrange(DOWN, buff=0.05),
            VGroup(t("15 626", 22), t("коммитов в год", 9, GREY, "NORMAL")).arrange(DOWN, buff=0.05),
            VGroup(t("0 ₽", 22), t("клиент бесплатен", 9, GREY, "NORMAL")).arrange(DOWN, buff=0.05),
        ).arrange(RIGHT, buff=0.22).move_to(DOWN * 0.9)
        self.play(FadeIn(stats, shift=UP * 0.15), run_time=0.9)
        self.wait(3.8)

        # финал
        self.play(FadeOut(stats), run_time=0.5)
        url = t("qantcore.space", 30, TEAL)
        url_sub = t("обзор Orca", 14, GREY, "NORMAL")
        final = VGroup(url, url_sub).arrange(DOWN, buff=0.16).move_to(UP * 0.1)
        self.play(Write(url), run_time=1.1)
        self.play(FadeIn(url_sub), run_time=0.5)
        self.wait(3.2)
