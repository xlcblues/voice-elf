"""
科学计算器式函数编辑器对话框
提供独立的科学计算器编辑界面
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QSizePolicy, QMessageBox, QSplitter, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from gui.function_editor_widget import FunctionEditorWidget
from core.function_parser import get_parser
from core.waveform_generator import WaveformGenerator


class ScientificCalculatorDialog(QDialog):
    """科学计算器式函数编辑器对话框"""

    def __init__(self, parent=None, initial_expression: str = ""):
        super().__init__(parent)
        self.initial_expression = initial_expression
        self.parser = get_parser()
        self.generator = WaveformGenerator()

        self.setup_ui()
        self.load_initial_expression()

    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("🧮 科学计算器式函数编辑器")
        self.setMinimumSize(900, 600)
        self.resize(1000, 700)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # 标题和说明
        header = QHBoxLayout()

        title_label = QLabel("🧮 科学计算器式函数编辑器")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2C3E50;
                background: transparent;
            }
        """)
        header.addWidget(title_label)

        header.addStretch()

        # 状态显示
        self.status_label = QLabel("✅ 准备就绪")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #27AE60;
                background: transparent;
                padding: 5px 10px;
                border-radius: 3px;
            }
        """)
        header.addWidget(self.status_label)

        main_layout.addLayout(header)

        # 使用分割器创建左右布局
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧：编辑器
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        editor_label = QLabel("📝 函数编辑器")
        editor_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2C3E50;
                background: transparent;
                padding: 5px 0px;
            }
        """)
        left_layout.addWidget(editor_label)

        # 创建函数编辑器
        self.editor = FunctionEditorWidget(self)
        left_layout.addWidget(self.editor)

        # 连接信号
        self.editor.expressionValid.connect(self.on_expression_valid)
        self.editor.expressionChanged.connect(self.on_expression_changed)

        splitter.addWidget(left_widget)

        # 右侧：帮助和预览
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        # 帮助信息
        help_group = QFrame()
        help_group.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border: 1px solid #DEE2E6;
                border-radius: 6px;
                padding: 12px;
            }
        """)
        help_layout = QVBoxLayout(help_group)
        help_layout.setSpacing(8)

        help_title = QLabel("📚 使用指南")
        help_title.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2C3E50;
                background: transparent;
            }
        """)
        help_layout.addWidget(help_title)

        help_text = QLabel("""
🎯 <b>功能特性:</b>
• 语法高亮: 实时彩色显示
• 智能验证: 自动检查错误
• 快速插入: 一键插入函数
• 实时预览: 显示处理结果

📝 <b>支持的函数:</b>
• 基础: sin, cos, tan, exp, log
• 高级: sinh, cosh, abs, power
• 波形: square, sawtooth, pulse
• 常数: PI, E 等

💡 <b>使用技巧:</b>
1. 点击按钮快速插入
2. 查看状态了解有效性
3. 利用颜色识别结构
4. 编辑完成后点击应用
        """)
        help_text.setStyleSheet("""
            QLabel {
                background: transparent;
                color: #495057;
                font-size: 11px;
                line-height: 1.5;
            }
        """)
        help_text.setWordWrap(True)
        help_layout.addWidget(help_text)

        right_layout.addWidget(help_group)

        # 测试按钮
        test_group = QFrame()
        test_group.setStyleSheet("""
            QFrame {
                background-color: #E3F2FD;
                border: 1px solid #BBDEFB;
                border-radius: 6px;
                padding: 12px;
            }
        """)
        test_layout = QVBoxLayout(test_group)
        test_layout.setSpacing(8)

        test_title = QLabel("🧪 测试功能")
        test_title.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #1976D2;
                background: transparent;
            }
        """)
        test_layout.addWidget(test_title)

        test_btn = QPushButton("🎵 测试生成并播放")
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 15px;
                font-weight: bold;
                font-size: 12px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        test_btn.clicked.connect(self.test_generation)
        test_layout.addWidget(test_btn)

        right_layout.addWidget(test_group)

        right_layout.addStretch()

        splitter.addWidget(right_widget)

        # 设置分割比例
        splitter.setStretchFactor(0, 3)  # 编辑器占3/4
        splitter.setStretchFactor(1, 1)  # 帮助占1/4

        main_layout.addWidget(splitter)

        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # 清空按钮
        clear_btn = QPushButton("🗑️ 清空")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #DC3545;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #C82333;
            }
        """)
        clear_btn.clicked.connect(self.clear_editor)
        button_layout.addWidget(clear_btn)

        button_layout.addStretch()

        # 取消按钮
        cancel_btn = QPushButton("❌ 取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #5A6268;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        # 应用并关闭按钮
        apply_btn = QPushButton("✅ 应用并关闭")
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        apply_btn.clicked.connect(self.apply_and_close)
        button_layout.addWidget(apply_btn)

        main_layout.addLayout(button_layout)

    def load_initial_expression(self):
        """加载初始表达式"""
        if self.initial_expression:
            self.editor.set_expression(self.initial_expression)

    def on_expression_valid(self, is_valid: bool, error_msg: str):
        """表达式验证结果处理"""
        if is_valid:
            self.status_label.setText("✅ 表达式有效")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #27AE60;
                    background: transparent;
                    padding: 5px 10px;
                    border-radius: 3px;
                }
            """)
        else:
            self.status_label.setText(f"❌ {error_msg}")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #DC3545;
                    background: transparent;
                    padding: 5px 10px;
                    border-radius: 3px;
                }
            """)

    def on_expression_changed(self, expression: str):
        """表达式变化处理"""
        # 重置状态
        if not expression:
            self.status_label.setText("⚠️ 表达式为空")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #FFC107;
                    background: transparent;
                    padding: 5px 10px;
                    border-radius: 3px;
                }
            """)

    def test_generation(self):
        """测试波形生成"""
        expression = self.editor.get_expression()

        if not expression:
            QMessageBox.warning(self, "警告", "请输入函数表达式")
            return

        try:
            # 尝试生成波形
            waveform_data, sample_rate = self.generator.generate_waveform(expression, duration=1.0)

            if waveform_data is not None and len(waveform_data) > 0:
                QMessageBox.information(
                    self,
                    "测试成功",
                    f"✅ 波形生成成功！\n\n"
                    f"表达式: {expression}\n"
                    f"数据长度: {len(waveform_data)}\n"
                    f"采样率: {sample_rate} Hz"
                )
            else:
                QMessageBox.warning(self, "生成失败", "波形数据为空")

        except Exception as e:
            QMessageBox.critical(self, "生成失败", f"错误: {str(e)}")

    def clear_editor(self):
        """清空编辑器"""
        self.editor.clear()
        self.status_label.setText("✅ 已清空")

    def apply_and_close(self):
        """应用并关闭"""
        expression = self.editor.get_expression()

        if not expression:
            QMessageBox.warning(self, "警告", "表达式不能为空")
            return

        try:
            # 验证表达式
            self.parser.validate_expression(expression)
            self.parser.parse_expression(expression)

            # 如果验证通过，接受并关闭
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"表达式验证失败:\n{str(e)}")

    def get_expression(self) -> str:
        """获取编辑后的表达式"""
        return self.editor.get_expression()