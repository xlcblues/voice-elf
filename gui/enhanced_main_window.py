"""
增强版主窗口模块
集成高级可视化功能和预设管理
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTabWidget, QGroupBox, QLabel,
    QPushButton, QTextEdit, QDoubleSpinBox, QSpinBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

import numpy as np
from gui.waveform_display import WaveformDisplayWidget
from gui.preset_manager import PresetManager

# 导入原有组件
from gui.main_window import MainWindow as BaseMainWindow

class EnhancedMainWindow(BaseMainWindow):
    """增强版主窗口类"""

    def __init__(self):
        """初始化增强主窗口"""
        # 调用父类初始化
        super().__init__()

        # 添加增强功能
        self.setup_enhanced_features()

    def setup_enhanced_features(self):
        """设置增强功能"""
        # 替换原有的显示区域为新的波形显示组件
        self.replace_display_area()

        # 添加预设管理器
        self.add_preset_manager()

        # 优化布局
        self.optimize_layout()

    def replace_display_area(self):
        """替换显示区域为新的波形显示组件"""
        # 创建新的波形显示组件
        self.waveform_display = WaveformDisplayWidget()

        # 找到原有的显示区域并替换
        # 这里我们需要重构主窗口的布局
        central_widget = self.centralWidget()
        main_layout = central_widget.layout()

        # 清除原有布局
        while main_layout.count():
            item = main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 创建新的布局
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧：波形显示
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(self.waveform_display)

        # 右侧：控制面板
        right_widget = self.create_control_panel()

        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(right_widget)
        main_splitter.setSizes([700, 300])  # 设置分割比例

        main_layout.addWidget(main_splitter)

    def create_control_panel(self) -> QWidget:
        """创建控制面板"""
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)

        # 参数设置区域
        params_group = self.create_params_group()
        control_layout.addWidget(params_group)

        # 预设管理器
        preset_group = QGroupBox("预设模板")
        preset_layout = QVBoxLayout()
        self.preset_manager = PresetManager()
        preset_layout.addWidget(self.preset_manager)
        preset_group.setLayout(preset_layout)
        control_layout.addWidget(preset_group)

        # 播放控制
        playback_group = self.create_playback_group()
        control_layout.addWidget(playback_group)

        control_layout.addStretch()

        return control_widget

    def create_params_group(self) -> QGroupBox:
        """创建参数设置组"""
        group = QGroupBox("参数设置")
        layout = QVBoxLayout()

        # 函数输入
        layout.addWidget(QLabel("波形表达式:"))
        self.function_input = QTextEdit()
        self.function_input.setMaximumHeight(80)
        self.function_input.setPlaceholderText("输入波形表达式，例如: sin(2*PI*440*t)")
        layout.addWidget(self.function_input)

        # 参数控制
        params_layout = QHBoxLayout()

        # 频率
        freq_layout = QVBoxLayout()
        freq_layout.addWidget(QLabel("频率 (Hz):"))
        self.frequency_spin = QDoubleSpinBox()
        self.frequency_spin.setRange(20, 20000)
        self.frequency_spin.setValue(440)
        freq_layout.addWidget(self.frequency_spin)
        params_layout.addLayout(freq_layout)

        # 音量
        volume_layout = QVBoxLayout()
        volume_layout.addWidget(QLabel("音量:"))
        self.volume_spin = QDoubleSpinBox()
        self.volume_spin.setRange(0, 1)
        self.volume_spin.setSingleStep(0.1)
        self.volume_spin.setValue(0.8)
        volume_layout.addWidget(self.volume_spin)
        params_layout.addLayout(volume_layout)

        # 时长
        duration_layout = QVBoxLayout()
        duration_layout.addWidget(QLabel("时长 (秒):"))
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(0.1, 60)
        self.duration_spin.setValue(5.0)
        duration_layout.addWidget(self.duration_spin)
        params_layout.addLayout(duration_layout)

        # 采样率
        sample_rate_layout = QVBoxLayout()
        sample_rate_layout.addWidget(QLabel("采样率 (Hz):"))
        self.sample_rate_spin = QSpinBox()
        self.sample_rate_spin.setRange(8000, 48000)
        self.sample_rate_spin.setValue(44100)
        self.sample_rate_spin.setSingleStep(100)
        sample_rate_layout.addWidget(self.sample_rate_spin)
        params_layout.addLayout(sample_rate_layout)

        layout.addLayout(params_layout)
        group.setLayout(layout)

        return group

    def create_playback_group(self) -> QGroupBox:
        """创建播放控制组"""
        group = QGroupBox("播放控制")
        layout = QVBoxLayout()

        # 播放控制按钮
        button_layout = QHBoxLayout()

        self.play_button = QPushButton("播放")
        self.play_button.setMinimumHeight(40)
        self.play_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        button_layout.addWidget(self.play_button)

        self.pause_button = QPushButton("暂停")
        self.pause_button.setMinimumHeight(40)
        self.pause_button.setEnabled(False)
        button_layout.addWidget(self.pause_button)

        self.stop_button = QPushButton("停止")
        self.stop_button.setMinimumHeight(40)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        self.export_button = QPushButton("导出")
        self.export_button.setMinimumHeight(40)
        button_layout.addWidget(self.export_button)

        layout.addLayout(button_layout)

        # 信息显示
        self.info_label = QLabel("就绪")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        group.setLayout(layout)

        return group

    def add_preset_manager(self):
        """添加预设管理器"""
        # 连接预设管理器信号
        if hasattr(self, 'preset_manager'):
            # 双击预设时应用
            self.preset_manager.preset_list.itemDoubleClicked.connect(self.on_preset_double_clicked)

    def on_preset_double_clicked(self, item):
        """预设双击事件"""
        expression = self.preset_manager.get_current_expression()
        if expression:
            self.function_input.setText(expression)
            self.update_status(f"已加载预设: {item.text()}")

    def optimize_layout(self):
        """优化布局"""
        # 设置窗口大小
        self.resize(1400, 900)

        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QPushButton {
                border: 2px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e6f7ff;
                border-color: #1890ff;
            }
        """)

    def generate_and_display_waveform(self):
        """生成并显示波形（重写父类方法）"""
        try:
            # 获取参数
            expression = self.function_input.toPlainText()
            if not expression:
                raise ValueError("请输入波形表达式")

            duration = self.duration_spin.value()
            sample_rate = self.sample_rate_spin.value()
            volume = self.volume_spin.value()

            # 生成波形
            self.update_status("正在生成波形...")
            self.info_label.setText("正在生成波形...")

            waveform, sr = self.waveform_generator.generate_waveform(
                expression, duration, sample_rate, volume
            )

            # 保存当前波形
            self.current_waveform = waveform
            self.current_sample_rate = sr

            # 使用新的波形显示组件
            self.waveform_display.set_waveform_data(waveform, sr)

            # 更新信息
            duration_sec = len(waveform) / sr
            rms_level = np.sqrt(np.mean(waveform ** 2))
            max_amplitude = np.max(np.abs(waveform))

            info_text = f"""波形信息:
时长: {duration_sec:.2f}秒
采样点: {len(waveform)}
采样率: {sr} Hz
RMS: {rms_level:.4f}
最大振幅: {max_amplitude:.4f}"""

            self.info_label.setText(info_text)
            self.update_status(f"波形生成完成: {len(waveform)} 点, {duration:.2f}秒")

        except Exception as e:
            from utils import handle_error
            error_msg = handle_error(e)
            self.info_label.setText(f"错误: {error_msg}")
            raise Exception(f"波形生成失败: {error_msg}")

    def set_expression(self, expression: str):
        """设置表达式（供预设管理器调用）"""
        self.function_input.setText(expression)

    def on_play_clicked(self):
        """播放按钮点击事件（重写父类方法）"""
        try:
            # 生成波形
            self.generate_and_display_waveform()

            # 加载到音频控制器
            if self.current_waveform is not None:
                self.audio_controller.load_waveform(self.current_waveform, self.current_sample_rate)
                self.audio_controller.play()

                self.update_status("正在播放...")
                self.info_label.setText("正在播放...")
                self.update_playback_buttons()

        except Exception as e:
            from utils import handle_error
            from PyQt6.QtWidgets import QMessageBox
            error_msg = handle_error(e)
            QMessageBox.warning(self, "错误", f"播放失败: {error_msg}")
            self.update_status(f"播放失败: {error_msg}")