"""
波形预览组件
提供鼠标悬停时的波形预览功能
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout,
    QFrame, QPushButton, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap, QPainter, QFont
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class WaveformPreviewWidget(QWidget):
    """波形预览组件"""

    def __init__(self, parent=None):
        """初始化预览组件"""
        super().__init__(parent)

        self.setup_ui()
        self.current_waveform_data = None
        self.waveform_name = ""

        # 设置窗口属性
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 设置固定大小
        self.setFixedSize(300, 200)

        # 隐藏初始化
        self.hide()

    def setup_ui(self):
        """设置用户界面"""
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # 创建背景框
        self.background_frame = QFrame()
        self.background_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(40, 40, 40, 240);
                border: 1px solid #555;
                border-radius: 8px;
            }
        """)
        frame_layout = QVBoxLayout(self.background_frame)
        frame_layout.setContentsMargins(10, 10, 10, 10)

        # 波形名称标签
        self.name_label = QLabel("波形预览")
        self.name_label.setStyleSheet("""
            QLabel {
                color: #fff;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
                padding: 5px;
            }
        """)
        frame_layout.addWidget(self.name_label)

        # 预览图表
        self.preview_figure = Figure(figsize=(2.5, 1.5), dpi=80)
        self.preview_canvas = FigureCanvas(self.preview_figure)
        self.preview_canvas.setStyleSheet("background: transparent;")

        # 设置matplotlib样式
        self.preview_figure.patch.set_facecolor('none')
        self.preview_canvas.setStyleSheet("background: transparent;")

        self.preview_axis = self.preview_figure.add_subplot(111)
        self.preview_axis.set_facecolor('#2a2a2a')

        # 设置图表样式
        self.preview_axis.tick_params(colors='white', labelsize=6)
        for spine in self.preview_axis.spines.values():
            spine.set_edgecolor('#555')

        self.preview_axis.grid(True, alpha=0.3, color='#555')
        frame_layout.addWidget(self.preview_canvas)

        layout.addWidget(self.background_frame)

    def show_preview(self, waveform_data: np.ndarray, sample_rate: int, name: str, position: tuple):
        """
        显示波形预览

        Args:
            waveform_data: 波形数据
            sample_rate: 采样率
            name: 波形名称
            position: 显示位置 (x, y)
        """
        try:
            self.current_waveform_data = waveform_data
            self.waveform_name = name

            # 更新名称标签
            self.name_label.setText(name)

            # 绘制预览波形
            self._plot_preview(waveform_data, sample_rate)

            # 移动到指定位置
            self.move(*position)

            # 显示预览（带动画效果）
            self._show_with_animation()

        except Exception as e:
            print(f"预览显示失败: {e}")
            self.hide()

    def _plot_preview(self, waveform_data: np.ndarray, sample_rate: int):
        """绘制预览波形"""
        try:
            # 清除之前的图表
            self.preview_axis.clear()

            # 验证数据
            if waveform_data is None or len(waveform_data) == 0:
                raise ValueError("波形数据为空")

            # 计算时间轴（只显示前0.15秒，稍微长一点）
            duration = min(0.15, len(waveform_data) / sample_rate)
            samples = min(int(duration * sample_rate), len(waveform_data))
            t = np.linspace(0, duration, samples)

            # 安全检查：确保波形数据在合理范围内
            plot_data = waveform_data[:samples]
            if len(plot_data) > 0:
                max_amplitude = np.max(np.abs(plot_data))
                if max_amplitude > 10:  # 如果振幅过大，可能是错误数据
                    plot_data = plot_data / max_amplitude  # 归一化

            # 绘制波形
            self.preview_axis.plot(t, plot_data,
                                  color='#00d4ff', linewidth=1.5)

            # 设置样式
            self.preview_axis.set_facecolor('#2a2a2a')
            self.preview_axis.tick_params(colors='white', labelsize=6)
            for spine in self.preview_axis.spines.values():
                spine.set_edgecolor('#555')

            self.preview_axis.grid(True, alpha=0.3, color='#555')
            self.preview_axis.set_xlim(0, duration)
            self.preview_axis.set_ylim(-1.2, 1.2)

            # 设置标题
            self.preview_axis.set_title(f"预览 (前{duration:.2f}秒)",
                                       color='white', fontsize=8, pad=2)

            # 刷新画布
            self.preview_canvas.draw()

        except Exception as e:
            # 绘制失败时显示错误信息
            self.preview_axis.clear()
            self.preview_axis.text(0.5, 0.5, "预览生成失败",
                                  ha='center', va='center',
                                  color='white', fontsize=8)
            self.preview_canvas.draw()

    def _show_with_animation(self):
        """带动画效果显示预览"""
        # 设置透明度动画
        self.setWindowOpacity(0)
        self.show()

        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(150)  # 150ms动画
        self.opacity_animation.setStartValue(0)
        self.opacity_animation.setEndValue(1)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.opacity_animation.start()

    def hide_preview(self):
        """隐藏预览"""
        # 延迟隐藏，避免快速切换时闪烁
        QTimer.singleShot(100, self._hide_with_animation)

    def _hide_with_animation(self):
        """带动画效果隐藏预览"""
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(100)  # 100ms动画
        self.opacity_animation.setStartValue(1)
        self.opacity_animation.setEndValue(0)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.opacity_animation.finished.connect(self.hide)
        self.opacity_animation.start()

    def mousePressEvent(self, event):
        """鼠标点击事件 - 点击预览窗口时隐藏"""
        self.hide_preview()
        super().mousePressEvent(event)


class WaveformPreviewManager:
    """波形预览管理器"""

    def __init__(self, main_window):
        """初始化预览管理器"""
        self.main_window = main_window
        self.preview_widget = WaveformPreviewWidget(main_window)
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self._show_preview)

        self.current_waveform_expression = None
        self.current_waveform_name = None

    def schedule_preview(self, expression: str, name: str, button_widget, delay_ms=300):
        """
        调度波形预览

        Args:
            expression: 波形表达式
            name: 波形名称
            button_widget: 按钮组件（用于定位）
            delay_ms: 延迟时间（毫秒）
        """
        self.current_waveform_expression = expression
        self.current_waveform_name = name
        self.button_widget = button_widget

        # 重置计时器
        self.preview_timer.stop()
        self.preview_timer.start(delay_ms)

    def cancel_preview(self):
        """取消预览"""
        self.preview_timer.stop()
        self.preview_widget.hide_preview()

    def _show_preview(self):
        """显示预览"""
        if not self.current_waveform_expression or not self.current_waveform_name:
            return

        try:
            # 生成预览波形（短时长）
            generator = self.main_window.waveform_generator
            waveform_data, sample_rate = generator.generate_waveform(
                self.current_waveform_expression,
                duration=0.3  # 缩短到0.3秒，更快生成
            )

            if waveform_data is not None and len(waveform_data) > 0:
                # 计算预览位置
                button_pos = self.button_widget.mapToGlobal(self.button_widget.rect().bottomLeft())
                preview_x = button_pos.x() + 10
                preview_y = button_pos.y() + 10

                # 显示预览
                self.preview_widget.show_preview(
                    waveform_data,
                    sample_rate,
                    self.current_waveform_name,
                    (preview_x, preview_y)
                )

        except Exception as e:
            # 静默失败，不影响用户体验
            # 某些复杂波形可能生成失败，这是正常的
            pass