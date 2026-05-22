"""
GUI模块
包含所有用户界面相关的组件
"""

from .main_window import MainWindow
from .waveform_display import WaveformDisplayWidget
from .preset_manager import PresetManager

__all__ = ['MainWindow', 'WaveformDisplayWidget', 'PresetManager']