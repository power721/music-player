# lyrics_widget_pro.py
import sys
import re
from dataclasses import dataclass
from typing import List

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


# =========================================================
# 数据结构
# =========================================================

@dataclass
class LyricLine:
    time: float
    text: str


# =========================================================
# LRC 解析
# =========================================================

class LrcParser:

    TIME_RE = re.compile(r"\[(\d+):(\d+(?:\.\d+)?)\]")

    @staticmethod
    def parse(lrc: str) -> List[LyricLine]:

        lines: List[LyricLine] = []

        for line in lrc.splitlines():

            matches = LrcParser.TIME_RE.findall(line)

            text = LrcParser.TIME_RE.sub("", line).strip()

            if not matches:
                continue

            for m in matches:
                minute = int(m[0])
                second = float(m[1])

                t = minute * 60 + second

                lines.append(LyricLine(t, text))

        lines.sort(key=lambda x: x.time)

        return lines


# =========================================================
# 歌词引擎
# =========================================================

class LyricsEngine:

    def __init__(self):
        self.lines: List[LyricLine] = []
        self.current_index = 0

    def set_lyrics(self, lines):

        self.lines = lines
        self.current_index = 0

    def update(self, time_sec):

        if not self.lines:
            return 0

        for i in range(len(self.lines) - 1):

            if self.lines[i].time <= time_sec < self.lines[i + 1].time:
                self.current_index = i
                return i

        if time_sec >= self.lines[-1].time:
            self.current_index = len(self.lines) - 1

        return self.current_index


# =========================================================
# 歌词 Widget
# =========================================================

class LyricsWidget(QWidget):

    seekRequested = Signal(int)

    def __init__(self, parent=None):

        super().__init__(parent)

        self.engine = LyricsEngine()

        self.current_time = 0
        self.current_index = 0

        self.scroll_y = 0
        self.target_scroll = 0

        self.line_height = 60

        self.gradient_shift = 0

        self.hover_index = -1

        self.margin_x = 40

        # 字体
        self.font_normal = QFont("Microsoft YaHei", 18)
        self.font_current = QFont("Microsoft YaHei", 26, QFont.Bold)

        # 颜色
        self.color_normal = QColor(150, 150, 150)

        # 动画
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(16)

        self.setMouseTracking(True)

    # =====================================================
    # API
    # =====================================================

    def set_lyrics(self, lrc_text):

        lines = LrcParser.parse(lrc_text)

        self.engine.set_lyrics(lines)

        self.scroll_y = 0
        self.target_scroll = 0

        self.update()

    def update_position(self, sec):

        self.current_time = sec

        index = self.engine.update(sec)

        if index != self.current_index:

            self.current_index = index

            self.target_scroll = index * self.line_height

    # =====================================================
    # 动画
    # =====================================================

    def _animate(self):

        diff = self.target_scroll - self.scroll_y

        self.scroll_y += diff * 0.12

        self.gradient_shift += 2

        if self.gradient_shift > self.width():
            self.gradient_shift = 0

        self.update()

    # =====================================================
    # 绘制
    # =====================================================

    def paintEvent(self, e):

        p = QPainter(self)

        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.TextAntialiasing)

        p.fillRect(self.rect(), QColor(10, 10, 10))

        lines = self.engine.lines

        if not lines:

            p.setPen(QColor(120, 120, 120))
            p.setFont(self.font_normal)

            p.drawText(self.rect(), Qt.AlignCenter, "No Lyrics")

            return

        center_y = self.height() / 2

        for i, line in enumerate(lines):

            y = center_y + (i * self.line_height - self.scroll_y)

            if y < -100 or y > self.height() + 100:
                continue

            if i == self.current_index:

                progress = self._line_progress(i)

                self._draw_current_line(p, line.text, y, progress)

            else:

                self._draw_normal_line(p, line.text, y, i)

    # =====================================================
    # 行进度
    # =====================================================

    def _line_progress(self, i):

        lines = self.engine.lines

        if i >= len(lines) - 1:
            return 1

        start = lines[i].time
        end = lines[i + 1].time

        dur = end - start

        if dur <= 0:
            return 1

        return max(0, min(1, (self.current_time - start) / dur))

    # =====================================================
    # 普通歌词
    # =====================================================

    def _draw_normal_line(self, p, text, y, index):

        distance = abs(index - self.current_index)

        scale = max(0.7, 1 - distance * 0.15)
        opacity = max(0.3, 1 - distance * 0.25)

        font = QFont(self.font_normal)
        font.setPointSizeF(self.font_normal.pointSizeF() * scale)

        p.setOpacity(opacity)
        p.setFont(font)

        if index == self.hover_index:
            p.setPen(QColor(220, 220, 220))
        else:
            p.setPen(self.color_normal)

        rect = QRectF(
            self.margin_x,
            y - self.line_height / 2,
            self.width() - self.margin_x * 2,
            self.line_height
        )

        p.drawText(rect, Qt.AlignCenter, text)

        p.setOpacity(1)

    # =====================================================
    # 当前歌词
    # =====================================================

    def _draw_current_line(self, p, text, y, progress):

        metrics = QFontMetrics(self.font_current)

        text_width = metrics.horizontalAdvance(text)

        x = self.width() / 2 - text_width / 2

        rect = QRectF(x, y - 30, text_width, 60)

        # 未唱部分
        p.setFont(self.font_current)
        p.setPen(QColor(180, 180, 180))

        p.drawText(rect, Qt.AlignCenter, text)

        clip = QRectF(x, y - 30, text_width * progress, 60)

        p.save()

        p.setClipRect(clip)

        gradient = QLinearGradient(
            x - self.gradient_shift,
            0,
            x + text_width - self.gradient_shift,
            0
        )

        gradient.setColorAt(0.0, QColor("#00F5FF"))
        gradient.setColorAt(0.3, QColor("#00C3FF"))
        gradient.setColorAt(0.6, QColor("#7A5CFF"))
        gradient.setColorAt(1.0, QColor("#FF4D9D"))

        path = QPainterPath()
        path.addText(x, y + 12, self.font_current, text)

        # glow
        for i in range(6, 0, -1):

            glow = QPen(QColor(80, 80, 255, 30), i * 2)

            p.setPen(glow)
            p.drawPath(path)

        p.setPen(QPen(QBrush(gradient), 2))

        p.drawPath(path)

        p.restore()

    # =====================================================
    # 鼠标
    # =====================================================

    def mouseMoveEvent(self, e):

        lines = self.engine.lines

        if not lines:
            return

        center_y = self.height() / 2

        for i in range(len(lines)):

            y = center_y + (i * self.line_height - self.scroll_y)

            rect = QRectF(0, y - 30, self.width(), 60)

            if rect.contains(e.pos()):

                self.hover_index = i

                self.setCursor(Qt.PointingHandCursor)

                self.update()

                return

        self.hover_index = -1

        self.unsetCursor()

    def mousePressEvent(self, e):

        if e.button() == Qt.LeftButton and self.hover_index >= 0:

            t = self.engine.lines[self.hover_index].time * 1000

            self.seekRequested.emit(int(t))

        super().mousePressEvent(e)


# =========================================================
# Demo
# =========================================================

demo_lrc = """
[00:01.00]Harmony Music Player
[00:04.00]This is a demo lyric line
[00:08.00]Beautiful gradient lyrics
[00:12.00]Smooth scrolling animation
[00:16.00]Click lyrics to seek
[00:20.00]Python + Qt + Music
[00:24.00]Enjoy the music
[00:28.00]Harmony Player
"""


class DemoWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("LyricsWidgetPro Demo")

        self.resize(900, 600)

        layout = QVBoxLayout(self)

        self.lyrics = LyricsWidgetPro()

        layout.addWidget(self.lyrics)

        self.lyrics.set_lyrics(demo_lrc)

        self.time = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(100)

    def tick(self):

        self.time += 0.1

        self.lyrics.update_position(self.time)


# =========================================================
# main
# =========================================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    win = DemoWindow()

    win.show()

    sys.exit(app.exec())
