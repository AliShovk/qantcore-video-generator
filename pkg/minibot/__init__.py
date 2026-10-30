"""minibot — скриптовая анимация мини-бота."""
from .bot import MiniBot
from .character import Pose, draw_bot
from .objects import Arrow, Chart, Highlight, Number, Scheme, Text
from .scene import Scene

__all__ = ['MiniBot', 'Scene', 'Chart', 'Text', 'Arrow', 'Highlight', 'Scheme', 'Number', 'Pose', 'draw_bot']
__version__ = '0.1.0'
