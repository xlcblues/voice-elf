"""
波形浏览器对话框
提供完整波形库的浏览和选择功能
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QStackedWidget,
    QGroupBox, QLineEdit, QTextEdit, QSplitter, QWidget
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from core.common_waveforms import CommonWaveforms
from core import get_generator


class WaveformBrowserDialog(QDialog):
    """波形浏览器对话框"""

    def __init__(self, parent=None):
        """初始化波形浏览器"""
        super().__init__(parent)
        self.waveform_generator = None
        self.selected_expression = None
        self.selected_name = None
        self.preview_timer = None
        self.current_preview_request = None
        self.setup_ui()
        self.initialize_generator()
        self.load_waveforms()

    def initialize_generator(self):
        """初始化波形生成器"""
        try:
            self.waveform_generator = get_generator()
            print("Waveform generator initialized successfully")
        except Exception as e:
            print(f"Failed to initialize waveform generator: {e}")
            import traceback
            traceback.print_exc()

    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("波形浏览器")
        self.setMinimumSize(900, 600)
        self.resize(1000, 700)

        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # 左侧面板
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)

        # 右侧面板
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)

        # 设置分割器比例
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.use_button = QPushButton("使用选中的波形")
        self.use_button.setMinimumHeight(35)
        self.use_button.setStyleSheet("""
            QPushButton {
                background-color: #1890ff;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #40a9ff;
            }
            QPushButton:disabled {
                background-color: #d9d9d9;
                color: #8c8c8c;
            }
        """)
        self.use_button.setEnabled(False)
        self.use_button.clicked.connect(self.on_use_clicked)
        button_layout.addWidget(self.use_button)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.setMinimumHeight(35)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                color: #333;
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                font-size: 14px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
        """)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

    def create_left_panel(self) -> QWidget:
        """创建左侧面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        # 搜索框
        search_group = QGroupBox("搜索波形")
        search_layout = QVBoxLayout(search_group)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键词搜索...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #1890ff;
            }
        """)
        self.search_input.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(self.search_input)

        layout.addWidget(search_group)

        # 分类列表
        category_group = QGroupBox("波形分类")
        category_layout = QVBoxLayout(category_group)

        self.category_list = QListWidget()
        self.category_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:selected {
                background-color: #e6f7ff;
                color: #1890ff;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
        """)
        self.category_list.currentRowChanged.connect(self.on_category_changed)
        category_layout.addWidget(self.category_list)

        layout.addWidget(category_group)

        # 波形列表
        waveform_group = QGroupBox("波形列表")
        waveform_layout = QVBoxLayout(waveform_group)

        self.waveform_list = QListWidget()
        self.waveform_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:selected {
                background-color: #e6f7ff;
                color: #1890ff;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
        """)
        self.waveform_list.currentRowChanged.connect(self.on_waveform_changed)
        waveform_layout.addWidget(self.waveform_list)

        layout.addWidget(waveform_group)

        return panel

    def create_right_panel(self) -> QWidget:
        """创建右侧面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        # 预览区域
        preview_group = QGroupBox("波形预览")
        preview_layout = QVBoxLayout(preview_group)

        # 波形名称
        self.waveform_name_label = QLabel("选择一个波形查看详情")
        self.waveform_name_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                padding: 10px;
                background-color: #f5f5f5;
                border-radius: 4px;
            }
        """)
        preview_layout.addWidget(self.waveform_name_label)

        # 波形描述
        self.waveform_description_label = QLabel("")
        self.waveform_description_label.setWordWrap(True)
        self.waveform_description_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #666;
                padding: 8px;
            }
        """)
        preview_layout.addWidget(self.waveform_description_label)

        # 波形图表
        self.preview_figure = Figure(figsize=(8, 4), dpi=100)
        self.preview_canvas = FigureCanvas(self.preview_figure)
        self.preview_figure.patch.set_facecolor('white')
        self.preview_canvas.setMinimumHeight(300)

        self.preview_axis = self.preview_figure.add_subplot(111)
        self.preview_axis.set_title("波形预览", fontsize=12, fontweight='bold')
        self.preview_axis.set_xlabel("时间 (秒)", fontsize=10)
        self.preview_axis.set_ylabel("振幅", fontsize=10)
        self.preview_axis.grid(True, alpha=0.3)

        preview_layout.addWidget(self.preview_canvas)

        layout.addWidget(preview_group)

        # 波形表达式
        expression_group = QGroupBox("波形表达式")
        expression_layout = QVBoxLayout(expression_group)

        self.expression_text = QTextEdit()
        self.expression_text.setReadOnly(True)
        self.expression_text.setMaximumHeight(100)
        self.expression_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
                background-color: #f9f9f9;
            }
        """)
        expression_layout.addWidget(self.expression_text)

        layout.addWidget(expression_group)

        # 参数信息
        params_group = QGroupBox("波形参数")
        params_layout = QVBoxLayout(params_group)

        self.params_label = QLabel("选择波形后查看参数信息")
        self.params_label.setWordWrap(True)
        self.params_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666;
                padding: 8px;
            }
        """)
        params_layout.addWidget(self.params_label)

        layout.addWidget(params_group)

        return panel

    def load_waveforms(self):
        """加载所有波形"""
        self.all_waveforms = CommonWaveforms.get_all_waveforms()
        self.current_category_waveforms = {}

        # 填充分类列表
        self.category_list.clear()
        for category_name in self.all_waveforms.keys():
            self.category_list.addItem(category_name)

        # 默认选择第一个分类
        if self.category_list.count() > 0:
            self.category_list.setCurrentRow(0)

    def on_category_changed(self, row):
        """分类改变事件"""
        if row < 0 or row >= len(self.all_waveforms):
            return

        category_name = self.category_list.currentItem().text()
        waveforms = self.all_waveforms[category_name]

        # 存储当前分类的波形
        self.current_category_waveforms = waveforms

        # 填充波形列表
        self.waveform_list.clear()
        for waveform_name in waveforms.keys():
            self.waveform_list.addItem(waveform_name)

        # 默认选择第一个波形
        if self.waveform_list.count() > 0:
            self.waveform_list.setCurrentRow(0)

    def on_waveform_changed(self, row):
        """波形选择改变事件"""
        if row < 0:
            self.use_button.setEnabled(False)
            return

        waveform_name = self.waveform_list.currentItem().text()
        category_name = self.category_list.currentItem().text()

        if waveform_name in self.current_category_waveforms:
            waveform_info = self.current_category_waveforms[waveform_name]
            self.show_waveform_details(waveform_name, waveform_info)
            self.use_button.setEnabled(True)

    def show_waveform_details(self, name: str, info: dict):
        """显示波形详细信息"""
        # 更新标签
        self.waveform_name_label.setText(f"{info.get('icon', '🌊')} {name}")
        self.waveform_description_label.setText(info.get('description', ''))
        self.expression_text.setPlainText(info.get('expression', ''))

        # 显示参数
        params = info.get('params', {})
        if params:
            params_text = "\n".join([f"• {k}: {v}" for k, v in params.items()])
            self.params_label.setText(params_text)
        else:
            self.params_label.setText("无特殊参数")

        # 存储选中的波形信息
        self.selected_expression = info.get('expression', '')
        self.selected_name = name

        # 使用防抖机制生成预览
        self.schedule_preview_generation(self.selected_expression)

    def schedule_preview_generation(self, expression: str):
        """调度预览生成（使用防抖机制）"""
        # 清除之前的定时器
        if self.preview_timer is not None:
            self.preview_timer.stop()
            self.preview_timer = None

        # 存储当前请求
        self.current_preview_request = expression

        # 创建新的防抖定时器
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(lambda: self.execute_preview_generation(expression))
        self.preview_timer.start(200)  # 200ms延迟，避免频繁预览生成

    def execute_preview_generation(self, expression: str):
        """执行预览生成"""
        # 检查是否是最新的请求
        if expression != self.current_preview_request:
            return  # 忽略过期的请求

        self.generate_preview(expression)

    def generate_preview(self, expression: str):
        """生成波形预览"""
        try:
            print(f"[BROWSER DEBUG] Starting preview generation for: {expression}")

            # 检查波形生成器是否可用
            if self.waveform_generator is None:
                print("[BROWSER ERROR] Waveform generator is None")
                self.preview_axis.clear()
                self.preview_axis.text(0.5, 0.5, "波形生成器未初始化",
                                      ha='center', va='center', fontsize=12, color='red')
                self.preview_canvas.draw()
                return

            print(f"[BROWSER DEBUG] Generator available: {self.waveform_generator is not None}")

            # 生成短时波形用于预览
            print(f"[BROWSER DEBUG] Calling generate_waveform with duration=1.0")
            waveform_data, sample_rate = self.waveform_generator.generate_waveform(
                expression, duration=1.0
            )
            print(f"[BROWSER DEBUG] Generation result: waveform_data={waveform_data is not None}, sample_rate={sample_rate}")

            if waveform_data is not None:
                # 绘制波形
                self.preview_axis.clear()

                # 显示前0.5秒
                duration = min(0.5, len(waveform_data) / sample_rate)
                samples = int(duration * sample_rate)
                t = np.linspace(0, duration, samples)

                self.preview_axis.plot(t, waveform_data[:samples],
                                     color='#1890ff', linewidth=1.5)
                self.preview_axis.set_title("波形预览", fontsize=12, fontweight='bold')
                self.preview_axis.set_xlabel("时间 (秒)", fontsize=10)
                self.preview_axis.set_ylabel("振幅", fontsize=10)
                self.preview_axis.grid(True, alpha=0.3)
                self.preview_axis.set_xlim(0, duration)
                self.preview_axis.set_ylim(-1.1, 1.1)

                self.preview_canvas.draw()
            else:
                # 波形生成返回None
                self.preview_axis.clear()
                self.preview_axis.text(0.5, 0.5, "波形生成失败: 返回空数据",
                                      ha='center', va='center', fontsize=12, color='red')
                self.preview_canvas.draw()

        except Exception as e:
            # 详细的错误信息
            import traceback
            error_details = f"预览生成失败:\n{str(e)}\n\n表达式:\n{expression[:50]}..."

            self.preview_axis.clear()
            self.preview_axis.text(0.5, 0.5, error_details,
                                  ha='center', va='center', fontsize=10, color='red')
            self.preview_canvas.draw()

            # 打印详细的错误信息到控制台
            print(f"Waveform Browser Preview Error:")
            print(f"Expression: {expression}")
            print(f"Error: {str(e)}")
            print(f"Traceback:")
            traceback.print_exc()

    def on_search_changed(self, text: str):
        """搜索文本改变事件"""
        if not text:
            # 恢复显示所有分类和波形
            self.load_waveforms()
            return

        # 搜索波形
        results = CommonWaveforms.search_waveforms(text)

        if results:
            # 清空当前列表
            self.waveform_list.clear()
            self.category_list.clear()

            # 创建一个"搜索结果"分类
            self.category_list.addItem("搜索结果")

            # 填充搜索结果
            self.current_category_waveforms = {}
            for result in results:
                name = result['name']
                self.waveform_list.addItem(name)
                self.current_category_waveforms[name] = {
                    'expression': result['expression'],
                    'description': result['description'],
                    'category': result['category']
                }

            # 选择第一个结果
            if self.waveform_list.count() > 0:
                self.waveform_list.setCurrentRow(0)

    def on_use_clicked(self):
        """使用按钮点击事件"""
        if self.selected_expression and self.selected_name:
            self.accept()

    def get_selected_waveform(self) -> tuple:
        """获取选中的波形信息"""
        return self.selected_expression, self.selected_name