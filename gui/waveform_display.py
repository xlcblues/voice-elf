"""
波形显示组件
提供高级的波形可视化功能
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel, QPushButton, QComboBox, QGroupBox
from PyQt6.QtCore import Qt, QTimer
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

class WaveformDisplayWidget(QWidget):
    """波形显示组件"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 数据存储
        self.waveform_data = None
        self.sample_rate = 44100
        self.display_mode = "2D时域"  # 默认显示模式

        # 显示参数
        self.zoom_level = 1.0
        self.offset = 0
        self.auto_scale = True
        self.show_grid = True

        # 设置matplotlib中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False

        # 先创建图表
        self.setup_figure()

        # 再设置UI
        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 控制面板
        control_panel = self.create_control_panel()
        layout.addWidget(control_panel)

        # 图表区域
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

    def create_control_panel(self) -> QGroupBox:
        """创建控制面板"""
        panel = QGroupBox("显示控制")
        panel_layout = QHBoxLayout()

        # 显示模式选择
        mode_label = QLabel("显示模式:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "2D时域",
            "2D频域",
            "2D时频",
            "3D波形",
            "3D频谱"
        ])
        self.mode_combo.currentTextChanged.connect(self.change_display_mode)

        # 缩放控制
        zoom_label = QLabel("缩放:")
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(1, 100)
        self.zoom_slider.setValue(10)  # 1.0x zoom
        self.zoom_slider.valueChanged.connect(self.update_zoom)

        # 位置控制
        offset_label = QLabel("位置:")
        self.offset_slider = QSlider(Qt.Orientation.Horizontal)
        self.offset_slider.setRange(0, 100)
        self.offset_slider.setValue(0)
        self.offset_slider.valueChanged.connect(self.update_offset)

        # 自动缩放按钮
        self.auto_scale_btn = QPushButton("自动缩放")
        self.auto_scale_btn.setCheckable(True)
        self.auto_scale_btn.setChecked(True)
        self.auto_scale_btn.clicked.connect(self.toggle_auto_scale)

        # 网格显示按钮
        self.grid_btn = QPushButton("显示网格")
        self.grid_btn.setCheckable(True)
        self.grid_btn.setChecked(True)
        self.grid_btn.clicked.connect(self.toggle_grid)

        # 导出图像按钮
        export_btn = QPushButton("导出图像")
        export_btn.clicked.connect(self.export_image)

        # 添加到布局
        panel_layout.addWidget(mode_label)
        panel_layout.addWidget(self.mode_combo)
        panel_layout.addWidget(zoom_label)
        panel_layout.addWidget(self.zoom_slider)
        panel_layout.addWidget(offset_label)
        panel_layout.addWidget(self.offset_slider)
        panel_layout.addWidget(self.auto_scale_btn)
        panel_layout.addWidget(self.grid_btn)
        panel_layout.addWidget(export_btn)

        panel.setLayout(panel_layout)
        return panel

    def setup_figure(self):
        """设置图表"""
        self.figure = Figure(figsize=(10, 6))
        self.ax = self.figure.add_subplot(111)
        self.setup_2d_time_domain()

    def setup_2d_time_domain(self):
        """设置2D时域显示"""
        self.ax.clear()
        self.ax.set_title("时域波形")
        self.ax.set_xlabel("时间 (秒)")
        self.ax.set_ylabel("幅度")
        if self.show_grid:
            self.ax.grid(True, alpha=0.3)

        # 如果有数据，显示波形
        if self.waveform_data is not None:
            self.display_waveform_2d()

    def setup_2d_frequency_domain(self):
        """设置2D频域显示"""
        self.ax.clear()
        self.ax.set_title("频域波形")
        self.ax.set_xlabel("频率 (Hz)")
        self.ax.set_ylabel("幅度")
        if self.show_grid:
            self.ax.grid(True, alpha=0.3)

        # 如果有数据，显示频谱
        if self.waveform_data is not None:
            self.display_spectrum_2d()

    def setup_3d_waveform(self):
        """设置3D波形显示"""
        self.figure.clear()
        self.ax = self.figure.add_subplot(111, projection='3d')
        self.ax.set_title("3D波形显示")
        self.ax.set_xlabel("时间 (秒)")
        self.ax.set_ylabel("幅度")
        self.ax.set_zlabel("频率 (Hz)")

        if self.waveform_data is not None:
            self.display_waveform_3d()

    def setup_time_frequency_display(self):
        """设置时频显示"""
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("时频分析")
        self.ax.set_xlabel("时间 (秒)")
        self.ax.set_ylabel("频率 (Hz)")

        if self.waveform_data is not None:
            self.display_time_frequency()

    def display_waveform_2d(self):
        """显示2D波形"""
        if self.waveform_data is None:
            return

        # 应用缩放和偏移
        display_data = self.apply_display_settings(self.waveform_data)

        # 生成时间轴
        duration = len(self.waveform_data) / self.sample_rate
        time_axis = np.linspace(0, duration, len(display_data))

        # 绘制波形
        self.ax.plot(time_axis, display_data, linewidth=0.5, color='blue')
        self.ax.set_title("时域波形")
        self.ax.set_xlabel("时间 (秒)")
        self.ax.set_ylabel("幅度")

        if self.show_grid:
            self.ax.grid(True, alpha=0.3)

        self.canvas.draw()

    def display_spectrum_2d(self):
        """显示2D频谱"""
        if self.waveform_data is None:
            return

        from scipy.fft import fft, fftfreq

        # 计算FFT
        n = len(self.waveform_data)
        yf = fft(self.waveform_data)
        xf = fftfreq(n, 1/self.sample_rate)[:n//2]
        magnitude = 2.0/n * np.abs(yf[0:n//2])

        # 限制显示范围
        max_freq = min(10000, xf[-1])
        mask = xf <= max_freq

        # 绘制频谱
        self.ax.plot(xf[mask], magnitude[mask], linewidth=0.5, color='red')
        self.ax.set_title("频域波形")
        self.ax.set_xlabel("频率 (Hz)")
        self.ax.set_ylabel("幅度")

        if self.show_grid:
            self.ax.grid(True, alpha=0.3)

        self.canvas.draw()

    def display_waveform_3d(self):
        """显示3D波形"""
        if self.waveform_data is None:
            return

        # 应用显示设置
        display_data = self.apply_display_settings(self.waveform_data)

        # 创建3D表面图
        # 这里我们创建一个"波形卷"效果
        duration = len(display_data) / self.sample_rate
        time_axis = np.linspace(0, duration, len(display_data))

        # 创建3D网格
        num_frames = 50
        frame_length = len(display_data) // num_frames

        X, Y = np.meshgrid(
            np.linspace(0, duration, num_frames),
            np.linspace(-1, 1, 100)
        )

        # Z值存储波形数据
        Z = np.zeros_like(X)

        for i in range(num_frames):
            start_idx = i * frame_length
            end_idx = min(start_idx + frame_length, len(display_data))
            frame_data = display_data[start_idx:end_idx]

            # 插值到固定长度
            if len(frame_data) > 0:
                frame_interpolated = np.interp(
                    np.linspace(0, 1, 100),
                    np.linspace(0, 1, len(frame_data)),
                    frame_data
                )
                Z[:, i] = frame_interpolated

        # 绘制3D表面
        surf = self.ax.plot_surface(X, Y, Z, cmap=cm.viridis, alpha=0.8)
        self.figure.colorbar(surf, ax=self.ax, shrink=0.5, aspect=5)

        self.ax.set_title("3D波形显示")
        self.ax.set_xlabel("时间 (秒)")
        self.ax.set_ylabel("幅度")
        self.ax.set_zlabel("时间帧")

        self.figure_canvas.draw()

    def display_time_frequency(self):
        """显示时频分析"""
        if self.waveform_data is None:
            return

        # 简化的时频分析 - 使用短时傅里叶变换的概念
        from scipy import signal as scipy_signal

        # 计算频谱图
        f, t, Sxx = scipy_signal.spectrogram(
            self.waveform_data,
            self.sample_rate,
            nperseg=256,
            noverlap=128
        )

        # 绘制频谱图
        im = self.ax.pcolormesh(t, f, 10 * np.log10(Sxx + 1e-10), shading='gouraud', cmap='viridis')
        self.figure.colorbar(im, ax=self.ax, label='功率 (dB)')

        self.ax.set_title("时频分析")
        self.ax.set_xlabel("时间 (秒)")
        self.ax.set_ylabel("频率 (Hz)")

        self.figure_canvas.draw()

    def apply_display_settings(self, data):
        """应用显示设置（缩放、偏移）"""
        if not self.auto_scale:
            # 应用缩放
            zoom_points = int(len(data) * self.zoom_level)
            start_idx = int(self.offset * (len(data) - zoom_points))
            end_idx = start_idx + zoom_points
            return data[start_idx:end_idx]
        return data

    def change_display_mode(self, mode):
        """改变显示模式"""
        self.display_mode = mode

        # 根据模式设置不同的图表
        if mode == "2D时域":
            self.figure.clear()
            self.ax = self.figure.add_subplot(111)
            self.setup_2d_time_domain()

        elif mode == "2D频域":
            self.figure.clear()
            self.ax = self.figure.add_subplot(111)
            self.setup_2d_frequency_domain()

        elif mode == "3D波形":
            self.setup_3d_waveform()

        elif mode == "2D时频":
            self.figure.clear()
            self.ax = self.figure.add_subplot(111)
            self.setup_time_frequency_display()

        elif mode == "3D频谱":
            self.figure.clear()
            self.ax = self.figure.add_subplot(111, projection='3d')
            self.setup_3d_waveform()  # 复用3D波形显示

    def update_zoom(self):
        """更新缩放级别"""
        self.zoom_level = self.zoom_slider.value() / 10.0
        if not self.auto_scale:
            self.refresh_display()

    def update_offset(self):
        """更新偏移位置"""
        self.offset = self.offset_slider.value() / 100.0
        if not self.auto_scale:
            self.refresh_display()

    def toggle_auto_scale(self):
        """切换自动缩放"""
        self.auto_scale = self.auto_scale_btn.isChecked()

        # 启用/禁用缩放控件
        self.zoom_slider.setEnabled(not self.auto_scale)
        self.offset_slider.setEnabled(not self.auto_scale)

        self.refresh_display()

    def toggle_grid(self):
        """切换网格显示"""
        self.show_grid = self.grid_btn.isChecked()
        self.refresh_display()

    def refresh_display(self):
        """刷新显示"""
        if self.display_mode == "2D时域":
            self.setup_2d_time_domain()
        elif self.display_mode == "2D频域":
            self.setup_2d_frequency_domain()
        elif self.display_mode == "3D波形":
            self.setup_3d_waveform()
        elif self.display_mode == "2D时频":
            self.setup_time_frequency_display()

    def set_waveform_data(self, waveform, sample_rate):
        """设置波形数据"""
        self.waveform_data = waveform
        self.sample_rate = sample_rate
        self.refresh_display()

    def clear_display(self):
        """清除显示"""
        self.waveform_data = None
        self.ax.clear()
        self.figure_canvas.draw()

    def export_image(self):
        """导出图像"""
        import os
        from datetime import datetime

        if self.waveform_data is None:
            return

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"waveform_{self.display_mode}_{timestamp}.png"

        try:
            self.figure.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"图像已导出: {filename}")
        except Exception as e:
            print(f"导出图像失败: {e}")

    def get_current_view_settings(self) -> dict:
        """获取当前视图设置"""
        return {
            'display_mode': self.display_mode,
            'zoom_level': self.zoom_level,
            'offset': self.offset,
            'auto_scale': self.auto_scale,
            'show_grid': self.show_grid
        }