"""
主窗口模块
定义应用程序的主窗口界面
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLabel, QPushButton, QTextEdit,
    QDoubleSpinBox, QSpinBox, QSlider, QTabWidget, QMessageBox,
    QDialog, QVBoxLayout, QHBoxLayout, QComboBox, QCheckBox, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import time

# 导入核心功能模块
from core import get_generator, get_audio_controller, PlaybackState, WaveformEditor, AudioRecorder
from utils import ConfigManager, handle_error, ProjectManager, get_user_preferences
from core.common_waveforms import CommonWaveforms
from gui.waveform_preview_widget import WaveformPreviewManager
from gui.waveform_browser_dialog import WaveformBrowserDialog
from gui.function_editor_widget import CalculatorStyleFunctionEditor

class MainWindow(QMainWindow):
    """主窗口类"""

    def __init__(self):
        """初始化主窗口"""
        super().__init__()

        # 初始化核心组件
        self.config = ConfigManager()
        self.waveform_generator = get_generator()
        self.audio_controller = get_audio_controller()

        # 初始化新功能组件
        self.waveform_editor = WaveformEditor()
        self.audio_recorder = AudioRecorder()
        self.project_manager = ProjectManager()
        self.user_preferences = get_user_preferences()

        # 初始化波形预览管理器
        self.preview_manager = WaveformPreviewManager(self)

        # 当前波形数据
        self.current_waveform = None
        self.current_sample_rate = 44100

        # 设置matplotlib中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False

        self.setup_ui()
        self.setup_status_bar()
        self.connect_signals()
        self.setup_timer()

    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("波形模拟器")
        self.setMinimumSize(1200, 800)  # 增加最小尺寸以适应科学计算器编辑器

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 创建各个区域
        main_layout.addWidget(self.create_display_area())
        main_layout.addWidget(self.create_control_area())

        # 设置样式
        self.apply_styles()

    def create_display_area(self) -> QGroupBox:
        """
        创建显示区域

        Returns:
            显示区域的分组框
        """
        display_group = QGroupBox("波形显示")
        display_layout = QVBoxLayout()
        display_group.setMinimumHeight(350)  # 设置最小高度确保显示区域不被压缩

        # 创建选项卡
        tab_widget = QTabWidget()
        tab_widget.setMinimumHeight(300)  # 确保选项卡有足够高度

        # 时域波形选项卡
        time_domain_tab = QWidget()
        time_layout = QVBoxLayout(time_domain_tab)

        # 创建时域波形图表
        self.time_figure = Figure(figsize=(10, 5))  # 增大图表尺寸
        self.time_canvas = FigureCanvas(self.time_figure)
        self.time_canvas.setMinimumHeight(280)  # 设置画布最小高度

        self.time_axis = self.time_figure.add_subplot(111)
        self.time_axis.set_title("时域波形", fontsize=12, fontweight='bold')
        self.time_axis.set_xlabel("时间 (秒)", fontsize=10)
        self.time_axis.set_ylabel("幅度", fontsize=10)
        self.time_axis.grid(True, alpha=0.3)

        time_layout.addWidget(self.time_canvas)
        tab_widget.addTab(time_domain_tab, "时域波形")

        # 频域波形选项卡
        freq_domain_tab = QWidget()
        freq_layout = QVBoxLayout(freq_domain_tab)

        # 创建频域波形图表
        self.freq_figure = Figure(figsize=(10, 5))  # 增大图表尺寸
        self.freq_canvas = FigureCanvas(self.freq_figure)
        self.freq_canvas.setMinimumHeight(280)  # 设置画布最小高度

        self.freq_axis = self.freq_figure.add_subplot(111)
        self.freq_axis.set_title("频域波形", fontsize=12, fontweight='bold')
        self.freq_axis.set_xlabel("频率 (Hz)", fontsize=10)
        self.freq_axis.set_ylabel("幅度", fontsize=10)
        self.freq_axis.grid(True, alpha=0.3)

        freq_layout.addWidget(self.freq_canvas)
        tab_widget.addTab(freq_domain_tab, "频域波形")

        display_layout.addWidget(tab_widget)
        display_group.setLayout(display_layout)

        return display_group

    def create_common_waveforms_panel(self) -> QGroupBox:
        """
        创建常见波形快速访问面板
        :return: 常见波形面板组件
        """
        panel = QGroupBox("快速波形")
        panel_layout = QVBoxLayout()
        panel.setMaximumHeight(180)  # 设置最大高度，防止占用过多空间

        # 添加说明和浏览器按钮
        header_layout = QHBoxLayout()

        info_label = QLabel("常用波形 (悬停预览，点击浏览器查看全部)")
        info_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #666;
                padding: 2px;
            }
        """)
        header_layout.addWidget(info_label)

        header_layout.addStretch()

        browse_button = QPushButton("📚 全部波形")
        browse_button.setMaximumHeight(25)
        browse_button.setStyleSheet("""
            QPushButton {
                background-color: #52c41a;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #73d13d;
            }
        """)
        browse_button.clicked.connect(self.on_browse_waveforms_clicked)
        header_layout.addWidget(browse_button)

        panel_layout.addLayout(header_layout)

        # 创建快速访问按钮（只显示前6个，2行布局）
        quick_waveforms = CommonWaveforms.get_quick_access_waveforms()[:6]

        # 使用网格布局排列按钮
        from PyQt6.QtWidgets import QGridLayout

        grid_layout = QGridLayout()
        grid_layout.setSpacing(4)  # 减小间距
        grid_layout.setContentsMargins(0, 0, 0, 0)  # 减少边距

        row, col = 0, 0
        max_cols = 3  # 每行3个按钮

        for waveform in quick_waveforms:
            btn = QPushButton(f"{waveform['icon']} {waveform['name']}")
            btn.setMinimumHeight(28)  # 减小按钮高度
            btn.setMaximumHeight(28)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 4px;
                    font-size: 11px;
                    border: 1px solid #d9d9d9;
                    border-radius: 3px;
                    background-color: white;
                }
                QPushButton:hover {
                    background-color: #e6f7ff;
                    border-color: #1890ff;
                }
            """)

            # 存储表达式和名称到按钮属性中
            btn.expression = waveform['expression']
            btn.waveform_name = waveform['name']

            # 点击事件
            btn.clicked.connect(lambda checked, expr=btn.expression, name=btn.waveform_name:
                               self.on_quick_waveform_clicked(expr, name))

            # 添加预览功能（鼠标悬停事件）
            btn.enterEvent = lambda event, b=btn, expr=btn.expression, name=btn.waveform_name: \
                               self.on_waveform_button_hover(event, b, expr, name)
            btn.leaveEvent = lambda event, b=btn: \
                               self.on_waveform_button_leave(event, b)

            grid_layout.addWidget(btn, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        panel_layout.addLayout(grid_layout)
        panel.setLayout(panel_layout)

        return panel

    def create_control_area(self) -> QGroupBox:
        """
        创建控制区域

        Returns:
            控制区域的分组框
        """
        control_group = QGroupBox("控制面板")
        control_layout = QVBoxLayout()

        # 函数输入区域 - 恢复简洁的输入框 + 科学计算器按钮
        function_layout = QHBoxLayout()
        function_layout.setSpacing(10)

        # 简洁的输入框容器
        input_container = QVBoxLayout()
        input_container.setSpacing(5)

        input_label = QLabel("📝 波形函数表达式:")
        input_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #2C3E50;
                background: transparent;
            }
        """)
        input_container.addWidget(input_label)

        self.function_input = QTextEdit()
        self.function_input.setMaximumHeight(50)
        self.function_input.setPlaceholderText("输入波形表达式，例如: sin(2*PI*f*t) 或直接使用具体频率 sin(2*PI*440*t)")
        self.function_input.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: 2px solid #3E3E42;
                border-radius: 4px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                padding: 6px;
            }
            QTextEdit:focus {
                border: 2px solid #007ACC;
            }
        """)
        # 设置输入框不阻止鼠标事件传播到相邻控件
        self.function_input.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        input_container.addWidget(self.function_input)
        function_layout.addLayout(input_container, stretch=3)

        # 科学计算器按钮容器
        button_container = QVBoxLayout()
        button_container.setSpacing(5)

        button_label = QLabel("🧮 高级编辑:")
        button_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #2C3E50;
                background: transparent;
            }
        """)
        button_container.addWidget(button_label)

        calculator_btn = QPushButton("科学计算器")
        calculator_btn.setStyleSheet("""
            QPushButton {
                background-color: #007ACC;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
        """)
        calculator_btn.clicked.connect(self.open_calculator_editor)
        button_container.addWidget(calculator_btn)
        button_container.addStretch()

        function_layout.addLayout(button_container, stretch=1)

        control_layout.addLayout(function_layout)

        # 参数设置区域
        params_layout = QHBoxLayout()
        params_layout.setSpacing(15)  # 增加控件之间的间距

        # 频率
        freq_layout = QVBoxLayout()
        freq_layout.setSpacing(2)
        freq_layout.addWidget(QLabel("频率:"))
        self.frequency_spin = QDoubleSpinBox()
        self.frequency_spin.setRange(20, 20000)
        self.frequency_spin.setValue(440)
        self.frequency_spin.setMinimumWidth(100)  # 设置最小宽度
        freq_layout.addWidget(self.frequency_spin)
        params_layout.addLayout(freq_layout)

        # 音量
        volume_layout = QVBoxLayout()
        volume_layout.setSpacing(2)
        volume_layout.addWidget(QLabel("音量:"))
        self.volume_spin = QDoubleSpinBox()
        self.volume_spin.setRange(0, 1)
        self.volume_spin.setSingleStep(0.1)
        self.volume_spin.setValue(0.8)
        self.volume_spin.setMinimumWidth(80)  # 设置最小宽度
        volume_layout.addWidget(self.volume_spin)
        params_layout.addLayout(volume_layout)

        # 时长
        duration_layout = QVBoxLayout()
        duration_layout.setSpacing(2)
        duration_layout.addWidget(QLabel("时长 (秒):"))
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(0.1, 60)
        self.duration_spin.setValue(5.0)
        self.duration_spin.setMinimumWidth(80)  # 设置最小宽度
        duration_layout.addWidget(self.duration_spin)
        params_layout.addLayout(duration_layout)

        # 采样率
        sample_rate_layout = QVBoxLayout()
        sample_rate_layout.setSpacing(2)
        sample_rate_layout.addWidget(QLabel("采样率:"))
        self.sample_rate_spin = QSpinBox()
        self.sample_rate_spin.setRange(8000, 48000)
        self.sample_rate_spin.setValue(44100)
        self.sample_rate_spin.setSingleStep(100)
        self.sample_rate_spin.setMinimumWidth(100)  # 设置最小宽度
        sample_rate_layout.addWidget(self.sample_rate_spin)
        params_layout.addLayout(sample_rate_layout)

        control_layout.addLayout(params_layout)

        # 快速波形 - 水平紧凑布局
        quick_waveforms_layout = QHBoxLayout()
        quick_waveforms_layout.setSpacing(4)

        # 添加标签和浏览器按钮
        info_label = QLabel("快速:")
        info_label.setStyleSheet("font-size: 11px; color: #666;")
        quick_waveforms_layout.addWidget(info_label)

        # 创建6个快速波形按钮（图标按钮）
        quick_waveforms = CommonWaveforms.get_quick_access_waveforms()[:6]
        for waveform in quick_waveforms:
            btn = QPushButton(f"{waveform['icon']}")
            btn.setMaximumSize(30, 25)  # 小尺寸按钮
            btn.setToolTip(f"{waveform['name']}\n点击生成波形")
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 12px;
                    border: 1px solid #d9d9d9;
                    border-radius: 3px;
                    background-color: white;
                    padding: 2px;
                }
                QPushButton:hover {
                    background-color: #e6f7ff;
                    border-color: #1890ff;
                }
            """)

            # 存储表达式和名称
            btn.expression = waveform['expression']
            btn.waveform_name = waveform['name']

            # 点击事件
            btn.clicked.connect(lambda checked, expr=btn.expression, name=btn.waveform_name:
                               self.on_quick_waveform_clicked(expr, name))

            # 预览功能
            btn.enterEvent = lambda event, b=btn, expr=btn.expression, name=btn.waveform_name: \
                               self.on_waveform_button_hover(event, b, expr, name)
            btn.leaveEvent = lambda event, b=btn: \
                               self.on_waveform_button_leave(event, b)

            quick_waveforms_layout.addWidget(btn)

        quick_waveforms_layout.addStretch()

        # 浏览器按钮
        browse_button = QPushButton("📚 更多波形")
        browse_button.setMaximumHeight(25)
        browse_button.setStyleSheet("""
            QPushButton {
                background-color: #52c41a;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #73d13d;
            }
        """)
        browse_button.clicked.connect(self.on_browse_waveforms_clicked)
        quick_waveforms_layout.addWidget(browse_button)

        control_layout.addLayout(quick_waveforms_layout)

        # 常见波形快速访问 - 移除原来占用大量空间的面板
        # common_waveforms_group = self.create_common_waveforms_panel()
        # control_layout.addWidget(common_waveforms_group)

        # 播放控制按钮
        button_layout = QHBoxLayout()

        self.play_button = QPushButton("▶ 播放")
        self.play_button.setMinimumHeight(28)
        self.play_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; font-size: 11px;")
        button_layout.addWidget(self.play_button)

        self.pause_button = QPushButton("⏸ 暂停")
        self.pause_button.setMinimumHeight(28)
        self.pause_button.setEnabled(False)
        button_layout.addWidget(self.pause_button)

        self.stop_button = QPushButton("⏹ 停止")
        self.stop_button.setMinimumHeight(28)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        self.export_button = QPushButton("💾 导出")
        self.export_button.setMinimumHeight(28)
        button_layout.addWidget(self.export_button)

        control_layout.addLayout(button_layout)

        # 新功能按钮
        new_features_layout = QHBoxLayout()

        self.record_button = QPushButton("🎙️ 录音")
        self.record_button.setMinimumHeight(28)
        self.record_button.setStyleSheet("background-color: #FF9800; color: white; font-size: 11px;")
        new_features_layout.addWidget(self.record_button)

        self.edit_button = QPushButton("✂️ 编辑")
        self.edit_button.setMinimumHeight(28)
        new_features_layout.addWidget(self.edit_button)

        # 真实感增强按钮
        self.realistic_button = QPushButton("🎵 真实感增强")
        self.realistic_button.setMinimumHeight(28)
        self.realistic_button.setStyleSheet("background-color: #9C27B0; color: white; font-size: 11px;")
        self.realistic_button.clicked.connect(self.on_realistic_enhancement)
        new_features_layout.addWidget(self.realistic_button)

        self.project_button = QPushButton("📁 项目")
        self.project_button.setMinimumHeight(28)
        new_features_layout.addWidget(self.project_button)

        self.settings_button = QPushButton("⚙️ 设置")
        self.settings_button.setMinimumHeight(28)
        new_features_layout.addWidget(self.settings_button)

        control_layout.addLayout(new_features_layout)

        control_group.setLayout(control_layout)

        return control_group

    def setup_status_bar(self):
        """设置状态栏"""
        self.statusBar().showMessage("就绪")

    def apply_styles(self):
        """应用样式"""
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
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
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
            QPushButton:pressed {
                background-color: #d6e4ff;
            }
            QPushButton:disabled {
                background-color: #f5f5f5;
                color: #cccccc;
                border-color: #d9d9d9;
            }
            QTextEdit, QSpinBox, QDoubleSpinBox {
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
                font-size: 13px;
            }
            QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border-color: #40a9ff;
                outline: none;
            }
            QLabel {
                font-size: 13px;
                color: #333;
            }
        """)

    def update_status(self, message: str):
        """
        更新状态栏消息

        Args:
            message: 状态消息
        """
        self.statusBar().showMessage(message)

    def connect_signals(self):
        """连接信号和槽"""
        self.play_button.clicked.connect(self.on_play_clicked)
        self.pause_button.clicked.connect(self.on_pause_clicked)
        self.stop_button.clicked.connect(self.on_stop_clicked)
        self.export_button.clicked.connect(self.on_export_clicked)

        # 新功能按钮连接
        self.record_button.clicked.connect(self.on_record_clicked)
        self.edit_button.clicked.connect(self.on_edit_clicked)
        self.project_button.clicked.connect(self.on_project_clicked)
        self.settings_button.clicked.connect(self.on_settings_clicked)

        # 参数变化信号连接 - 实时响应参数变化
        self.frequency_spin.valueChanged.connect(self.on_parameter_changed)
        self.volume_spin.valueChanged.connect(self.on_parameter_changed)
        self.duration_spin.valueChanged.connect(self.on_parameter_changed)
        self.sample_rate_spin.valueChanged.connect(self.on_parameter_changed)

        # 设置音频控制器回调
        self.audio_controller.set_callbacks(
            playback_callback=self.on_playback_complete,
            position_callback=self.on_playback_position_update
        )

    def open_calculator_editor(self):
        """打开科学计算器编辑器窗口"""
        from gui.scientific_calculator_dialog import ScientificCalculatorDialog

        # 获取当前表达式
        current_expression = self.function_input.toPlainText()

        # 创建并显示科学计算器对话框
        dialog = ScientificCalculatorDialog(self, current_expression)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 获取编辑后的表达式
            edited_expression = dialog.get_expression()
            if edited_expression:
                # 应用到主窗口
                self.function_input.setPlainText(edited_expression)
                # 自动生成波形
                self.generate_and_display_waveform()
                # 如果生成成功，自动播放
                if self.current_waveform is not None:
                    self.audio_controller.load_waveform(self.current_waveform, self.current_sample_rate)
                    self.audio_controller.play()

    def setup_timer(self):
        """设置定时器"""
        # 创建定时器用于更新UI
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_ui_state)
        self.update_timer.start(100)  # 每100ms更新一次

    def on_parameter_changed(self):
        """参数变化时的处理"""
        # 只有在有当前表达式时才自动重新生成波形
        current_expression = self.function_input.toPlainText().strip()
        if current_expression:
            # 使用防抖机制，避免频繁重新生成
            if not hasattr(self, '_parameter_debounce_timer'):
                self._parameter_debounce_timer = None

            # 清除之前的定时器
            if self._parameter_debounce_timer is not None:
                self._parameter_debounce_timer.stop()

            # 创建新的防抖定时器
            self._parameter_debounce_timer = QTimer()
            self._parameter_debounce_timer.setSingleShot(True)
            self._parameter_debounce_timer.timeout.connect(self.generate_and_display_waveform)
            self._parameter_debounce_timer.start(300)  # 300ms延迟

    def on_play_clicked(self):
        """播放按钮点击事件"""
        try:
            # 如果没有当前波形，先生成一个
            if self.current_waveform is None:
                self.generate_and_display_waveform()

            # 加载到音频控制器
            if self.current_waveform is not None:
                self.audio_controller.load_waveform(self.current_waveform, self.current_sample_rate)
                self.audio_controller.play()

                self.update_status("正在播放...")
                self.update_playback_buttons()

        except Exception as e:
            error_msg = handle_error(e)
            QMessageBox.warning(self, "错误", f"播放失败: {error_msg}")
            self.update_status(f"播放失败: {error_msg}")

    def on_pause_clicked(self):
        """暂停按钮点击事件"""
        try:
            state = self.audio_controller.get_state()

            if state == PlaybackState.PLAYING:
                self.audio_controller.pause()
                self.pause_button.setText("继续")
                self.update_status("已暂停")
            elif state == PlaybackState.PAUSED:
                self.audio_controller.play()
                self.pause_button.setText("暂停")
                self.update_status("继续播放")

        except Exception as e:
            error_msg = handle_error(e)
            QMessageBox.warning(self, "错误", f"暂停失败: {error_msg}")

    def on_stop_clicked(self):
        """停止按钮点击事件"""
        try:
            self.audio_controller.stop()
            self.pause_button.setText("暂停")
            self.update_status("已停止")
            self.update_playback_buttons()

        except Exception as e:
            error_msg = handle_error(e)
            QMessageBox.warning(self, "错误", f"停止失败: {error_msg}")

    def on_export_clicked(self):
        """导出按钮点击事件"""
        try:
            # 如果没有当前波形，先生成一个
            if self.current_waveform is None:
                self.generate_and_display_waveform()

            if self.current_waveform is not None:
                import os
                filename = f"waveform_{int(os.time.time())}.wav"
                self.waveform_generator.export_waveform(filename)

                QMessageBox.information(self, "成功", f"波形已导出到: {filename}")
                self.update_status(f"已导出到: {filename}")

        except Exception as e:
            error_msg = handle_error(e)
            QMessageBox.warning(self, "错误", f"导出失败: {error_msg}")

    def on_quick_waveform_clicked(self, expression: str, name: str):
        """快速波形按钮点击事件"""
        try:
            # 设置表达式到输入框
            self.function_input.setPlainText(expression)

            # 自动生成并播放波形
            self.generate_and_display_waveform()

            # 如果生成成功，自动播放
            if self.current_waveform is not None:
                self.audio_controller.load_waveform(self.current_waveform, self.current_sample_rate)
                self.audio_controller.play()

            # 更新状态栏
            self.update_status(f"已生成快速波形: {name}")

        except Exception as e:
            error_msg = handle_error(e)
            QMessageBox.warning(self, "错误", f"生成快速波形失败: {error_msg}")

    def on_waveform_button_hover(self, event, button, expression: str, name: str):
        """波形按钮鼠标悬停事件"""
        try:
            # 调度预览显示（延迟300ms避免频繁触发）
            self.preview_manager.schedule_preview(expression, name, button, delay_ms=300)
        except Exception as e:
            print(f"预览调度失败: {e}")

    def on_waveform_button_leave(self, event, button):
        """波形按钮鼠标离开事件"""
        try:
            # 取消预览
            self.preview_manager.cancel_preview()
        except Exception as e:
            print(f"取消预览失败: {e}")

    def on_browse_waveforms_clicked(self):
        """浏览全部波形按钮点击事件"""
        try:
            # 创建波形浏览器对话框
            browser = WaveformBrowserDialog(self)

            # 显示对话框
            if browser.exec() == QDialog.DialogCode.Accepted:
                # 获取选中的波形
                expression, name = browser.get_selected_waveform()

                if expression and name:
                    # 使用选中的波形
                    self.function_input.setPlainText(expression)
                    self.generate_and_display_waveform()

                    # 如果生成成功，自动播放
                    if self.current_waveform is not None:
                        self.audio_controller.load_waveform(self.current_waveform, self.current_sample_rate)
                        self.audio_controller.play()

                    # 更新状态栏
                    self.update_status(f"已从波形库生成: {name}")

        except Exception as e:
            error_msg = handle_error(e)
            QMessageBox.warning(self, "错误", f"打开波形浏览器失败: {error_msg}")

    def generate_and_display_waveform(self):
        """生成并显示波形"""
        try:
            # 获取参数
            expression = self.function_input.toPlainText()
            if not expression:
                raise ValueError("请输入波形表达式")

            duration = self.duration_spin.value()
            sample_rate = self.sample_rate_spin.value()
            volume = self.volume_spin.value()
            frequency = self.frequency_spin.value()

            # 处理频率参数：如果表达式中包含'f'，则替换为实际频率值
            # 这允许用户在表达式中使用 'f' 作为频率变量
            if 'f' in expression:
                import re
                # 使用正则表达式只替换独立的 'f' 变量，避免替换函数名中的 'f'
                # 匹配模式：单词边界 + f + 单词边界
                processed_expression = re.sub(r'\bf\b', str(frequency), expression)
                print(f"[DEBUG] Frequency replacement: '{expression}' -> '{processed_expression}'")
            else:
                # 如果表达式中没有 'f'，则不进行自动频率插入
                # 用户需要明确指定完整的数学表达式
                processed_expression = expression

            # 生成波形
            self.update_status("正在生成波形...")
            waveform, sr = self.waveform_generator.generate_waveform(
                processed_expression, duration, sample_rate, volume
            )

            # 保存当前波形
            self.current_waveform = waveform
            self.current_sample_rate = sr

            # 显示波形
            self.display_waveform(waveform, sr)
            self.update_status(f"波形生成完成: {len(waveform)} 点, {duration:.2f}秒")

        except Exception as e:
            error_msg = handle_error(e)
            raise Exception(f"波形生成失败: {error_msg}")

    def display_waveform(self, waveform, sample_rate):
        """显示波形"""
        try:
            # 显示时域波形
            self.time_axis.clear()

            # 降采样显示以提高性能
            max_points = self.config.get('display.max_display_points', 10000)
            if len(waveform) > max_points:
                step = len(waveform) // max_points
                display_waveform = waveform[::step]
                display_time = np.linspace(0, len(waveform) / sample_rate, len(display_waveform))
            else:
                display_waveform = waveform
                display_time = np.linspace(0, len(waveform) / sample_rate, len(waveform))

            self.time_axis.plot(display_time, display_waveform, linewidth=0.5)
            self.time_axis.set_title("时域波形")
            self.time_axis.set_xlabel("时间 (秒)")
            self.time_axis.set_ylabel("幅度")
            self.time_axis.grid(True)
            self.time_canvas.draw()

            # 显示频域波形
            self.display_frequency_spectrum(waveform, sample_rate)

        except Exception as e:
            print(f"波形显示错误: {e}")

    def display_frequency_spectrum(self, waveform, sample_rate):
        """显示频域波形"""
        try:
            from scipy.fft import fft, fftfreq

            self.freq_axis.clear()

            # 计算FFT
            n = len(waveform)
            yf = fft(waveform)
            xf = fftfreq(n, 1/sample_rate)[:n//2]

            # 计算幅度谱
            magnitude = 2.0/n * np.abs(yf[0:n//2])

            # 限制显示范围
            max_freq = min(5000, xf[-1])  # 显示到5kHz
            mask = xf <= max_freq

            self.freq_axis.plot(xf[mask], magnitude[mask], linewidth=0.5)
            self.freq_axis.set_title("频域波形")
            self.freq_axis.set_xlabel("频率 (Hz)")
            self.freq_axis.set_ylabel("幅度")
            self.freq_axis.grid(True)
            self.freq_canvas.draw()

        except Exception as e:
            print(f"频谱显示错误: {e}")

    def update_playback_buttons(self):
        """更新播放按钮状态"""
        state = self.audio_controller.get_state()

        self.play_button.setEnabled(state == PlaybackState.STOPPED)
        self.pause_button.setEnabled(state in [PlaybackState.PLAYING, PlaybackState.PAUSED])
        self.stop_button.setEnabled(state != PlaybackState.STOPPED)
        self.export_button.setEnabled(True)

    def update_ui_state(self):
        """更新UI状态"""
        self.update_playback_buttons()

    def on_playback_complete(self, success: bool, error_msg: str = ""):
        """播放完成回调"""
        if success:
            self.update_status("播放完成")
        else:
            self.update_status(f"播放错误: {error_msg}")

        self.update_playback_buttons()

    def on_playback_position_update(self, current: int, total: int):
        """播放位置更新回调"""
        progress = current / total if total > 0 else 0
        self.update_status(f"播放中... {progress*100:.1f}%")

    # 新功能回调函数

    def on_record_clicked(self):
        """录音按钮点击事件"""
        try:
            # 简单的录音对话框
            from PyQt6.QtWidgets import QInputDialog

            duration, ok = QInputDialog.getDouble(
                self, "录音时长", "请输入录音时长（秒）:", 5.0, 0.1, 60.0
            )

            if ok:
                self.update_status(f"开始录音 {duration} 秒...")
                self.audio_recorder.start_recording(duration=duration)

                # 等待录音完成
                import time
                while self.audio_recorder.recording:
                    time.sleep(0.1)
                    info = self.audio_recorder.get_recording_info()
                    self.update_status(f"录音中... {info['duration']:.1f}秒")

                # 获取录音数据
                recorded_data = self.audio_recorder.get_recorded_data()

                if len(recorded_data) > 0:
                    # 设置为当前波形
                    self.current_waveform = recorded_data
                    self.current_sample_rate = self.audio_recorder.sample_rate

                    # 显示波形
                    self.display_waveform(recorded_data, self.audio_recorder.sample_rate)

                    self.update_status(f"录音完成: {len(recorded_data)} 个采样点")
                else:
                    QMessageBox.warning(self, "录音失败", "没有录制到音频数据")

        except Exception as e:
            error_msg = handle_error(e)
            QMessageBox.warning(self, "录音错误", f"录音失败: {error_msg}")

    def on_edit_clicked(self):
        """编辑按钮点击事件"""
        try:
            if self.current_waveform is None:
                QMessageBox.warning(self, "编辑失败", "请先生成或加载波形")
                return

            # 简单的编辑对话框
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QDoubleSpinBox, QPushButton

            dialog = QDialog(self)
            dialog.setWindowTitle("波形编辑")
            dialog.setMinimumWidth(300)

            layout = QVBoxLayout(dialog)

            # 编辑操作选择
            layout.addWidget(QLabel("选择编辑操作:"))
            operation_combo = QComboBox()
            operation_combo.addItems([
                "增益调整",
                "淡入效果",
                "淡出效果",
                "ADSR包络",
                "归一化",
                "低通滤波",
                "高通滤波",
                "添加噪音"
            ])
            layout.addWidget(operation_combo)

            # 参数输入
            param_spin = QDoubleSpinBox()
            param_spin.setRange(0, 2)
            param_spin.setValue(0.5)
            param_spin.setSingleStep(0.1)
            layout.addWidget(QLabel("参数值:"))
            layout.addWidget(param_spin)

            # 应用按钮
            apply_btn = QPushButton("应用")
            layout.addWidget(apply_btn)

            def apply_edit():
                try:
                    operation = operation_combo.currentText()
                    param = param_spin.value()

                    # 加载波形到编辑器
                    self.waveform_editor.load_waveform(self.current_waveform, self.current_sample_rate)

                    # 应用编辑操作
                    if operation == "增益调整":
                        result = self.waveform_editor.apply_gain(param)
                    elif operation == "淡入效果":
                        result = self.waveform_editor.fade_in(param)
                    elif operation == "淡出效果":
                        result = self.waveform_editor.fade_out(param)
                    elif operation == "归一化":
                        result = self.waveform_editor.normalize(param)
                    elif operation == "ADSR包络":
                        result = self.waveform_editor.apply_envelope(
                            attack=0.01, decay=param, sustain=0.7, release=0.2
                        )
                    elif operation == "低通滤波":
                        result = self.waveform_editor.apply_filter('lowpass', param * 1000)
                    elif operation == "高通滤波":
                        result = self.waveform_editor.apply_filter('highpass', param * 100)
                    elif operation == "添加噪音":
                        result = self.waveform_editor.add_noise(param, 'white')
                    else:
                        result = self.current_waveform

                    # 更新当前波形
                    self.current_waveform = result

                    # 更新显示 - 确保显示的是编辑后的波形
                    self.display_waveform(result, self.current_sample_rate)

                    # 同时更新函数输入框，反映这是一个编辑后的波形
                    current_expr = self.function_input.toPlainText()
                    self.function_input.setPlainText(f"[编辑后] {current_expr}")

                    self.update_status(f"编辑操作应用成功: {operation}")
                    dialog.accept()

                except Exception as e:
                    QMessageBox.warning(dialog, "编辑失败", f"编辑操作失败: {str(e)}")

            apply_btn.clicked.connect(apply_edit)
            dialog.exec()

        except Exception as e:
            error_msg = handle_error(e)
            QMessageBox.warning(self, "编辑错误", f"编辑功能失败: {error_msg}")

    def on_realistic_enhancement(self):
        """真实感增强按钮点击事件"""
        try:
            if self.current_waveform is None:
                QMessageBox.warning(self, "真实感增强", "请先生成波形！")
                return

            from gui.realistic_sound_dialog import RealisticSoundDialog

            # 创建真实感增强对话框
            dialog = RealisticSoundDialog(
                self.current_waveform,
                self.current_sample_rate,
                self
            )

            if dialog.exec() == QDialog.DialogCode.Accepted:
                # 获取增强后的波形
                enhanced_waveform = dialog.get_enhanced_waveform()

                # 更新当前波形
                self.current_waveform = enhanced_waveform

                # 更新显示
                self.display_waveform(enhanced_waveform, self.current_sample_rate)

                self.update_status("真实感增强已应用")

        except Exception as e:
            from utils.error_handler import handle_error
            error_msg = handle_error(e)
            QMessageBox.warning(self, "真实感增强错误", f"增强功能失败: {error_msg}")

    def on_project_clicked(self):
        """项目按钮点击事件"""
        try:
            # 简单的项目管理对话框
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLineEdit

            dialog = QDialog(self)
            dialog.setWindowTitle("项目管理")
            dialog.setMinimumWidth(500)

            layout = QVBoxLayout(dialog)

            # 项目操作按钮
            button_layout = QHBoxLayout()

            new_project_btn = QPushButton("新建项目")
            save_project_btn = QPushButton("保存项目")
            load_project_btn = QPushButton("加载项目")
            export_btn = QPushButton("导出波形")

            button_layout.addWidget(new_project_btn)
            button_layout.addWidget(save_project_btn)
            button_layout.addWidget(load_project_btn)
            button_layout.addWidget(export_btn)

            layout.addLayout(button_layout)

            # 项目列表
            layout.addWidget(QLabel("已有项目:"))
            project_list = QListWidget()

            # 加载项目列表
            try:
                projects = self.project_manager.get_project_list()
                for project in projects[:10]:  # 只显示前10个
                    project_list.addItem(f"{project['name']} ({project['modified']})")
            except Exception as e:
                project_list.addItem(f"加载项目列表失败: {e}")

            layout.addWidget(project_list)

            def create_project():
                project_name = f"项目_{int(time.time())}"
                self.project_manager.create_project(project_name)
                QMessageBox.information(dialog, "成功", f"项目创建成功: {project_name}")

            def save_project():
                if self.current_waveform is not None:
                    expression = self.function_input.toPlainText()
                    params = {
                        "duration": self.duration_spin.value(),
                        "sample_rate": self.sample_rate_spin.value(),
                        "amplitude": self.volume_spin.value()
                    }

                    self.project_manager.add_waveform_to_project(
                        expression, params, self.current_waveform
                    )

                    filepath = self.project_manager.save_project()
                    QMessageBox.information(dialog, "成功", f"项目保存成功: {filepath}")
                else:
                    QMessageBox.warning(dialog, "保存失败", "没有波形数据可保存")

            new_project_btn.clicked.connect(create_project)
            save_project_btn.clicked.connect(save_project)

            dialog.exec()

        except Exception as e:
            error_msg = handle_error(e)
            QMessageBox.warning(self, "项目管理错误", f"项目管理功能失败: {error_msg}")

    def on_settings_clicked(self):
        """设置按钮点击事件"""
        try:
            # 简单的设置对话框
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel, QSpinBox, QDoubleSpinBox, QCheckBox

            dialog = QDialog(self)
            dialog.setWindowTitle("用户设置")
            dialog.setMinimumWidth(400)

            layout = QVBoxLayout(dialog)

            # 选项卡
            tab_widget = QTabWidget()

            # 音频设置
            audio_tab = QWidget()
            audio_layout = QVBoxLayout(audio_tab)

            audio_layout.addWidget(QLabel("默认采样率:"))
            sample_rate_spin = QSpinBox()
            sample_rate_spin.setRange(8000, 48000)
            sample_rate_spin.setValue(self.user_preferences.get("audio.default_sample_rate"))
            audio_layout.addWidget(sample_rate_spin)

            audio_layout.addWidget(QLabel("默认音量:"))
            volume_spin = QDoubleSpinBox()
            volume_spin.setRange(0, 1)
            volume_spin.setSingleStep(0.1)
            volume_spin.setValue(self.user_preferences.get("audio.default_volume"))
            audio_layout.addWidget(volume_spin)

            tab_widget.addTab(audio_tab, "音频")

            # 显示设置
            display_tab = QWidget()
            display_layout = QVBoxLayout(display_tab)

            show_grid_check = QCheckBox("显示网格")
            show_grid_check.setChecked(self.user_preferences.get("display.show_grid"))
            display_layout.addWidget(show_grid_check)

            auto_scale_check = QCheckBox("自动缩放")
            auto_scale_check.setChecked(self.user_preferences.get("display.auto_scale"))
            display_layout.addWidget(auto_scale_check)

            tab_widget.addTab(display_tab, "显示")

            layout.addWidget(tab_widget)

            # 保存按钮
            save_btn = QPushButton("保存设置")
            layout.addWidget(save_btn)

            def save_settings():
                try:
                    # 保存音频设置
                    self.user_preferences.set("audio.default_sample_rate", sample_rate_spin.value())
                    self.user_preferences.set("audio.default_volume", volume_spin.value())

                    # 保存显示设置
                    self.user_preferences.set("display.show_grid", show_grid_check.isChecked())
                    self.user_preferences.set("display.auto_scale", auto_scale_check.isChecked())

                    # 保存到文件
                    success = self.user_preferences.save_preferences()

                    if success:
                        QMessageBox.information(dialog, "成功", "设置保存成功")
                        dialog.accept()
                    else:
                        QMessageBox.warning(dialog, "失败", "设置保存失败")

                except Exception as e:
                    QMessageBox.warning(dialog, "保存失败", f"设置保存失败: {str(e)}")

            save_btn.clicked.connect(save_settings)
            dialog.exec()

        except Exception as e:
            error_msg = handle_error(e)
            QMessageBox.warning(self, "设置错误", f"设置功能失败: {error_msg}")