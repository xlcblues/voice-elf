"""
科学计算器式函数编辑器组件
提供语法高亮、自动补全、错误检查等功能
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel,
    QPushButton, QFrame, QScrollArea, QMessageBox, QToolTip
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import (
    QTextCharFormat, QColor, QFont, QTextCursor, QPalette,
    QSyntaxHighlighter, QTextDocument, QTextBlock
)
import re
from typing import Dict, List, Optional, Tuple
from utils.error_handler import ParseError
from core.function_parser import get_parser


class FunctionSyntaxHighlighter(QSyntaxHighlighter):
    """函数语法高亮器"""

    def __init__(self, document: QTextDocument):
        super().__init__(document)
        self.setup_highlighting_rules()

    def setup_highlighting_rules(self):
        """设置语法高亮规则"""

        # 数学函数格式 - 蓝色
        self.math_function_format = QTextCharFormat()
        self.math_function_format.setForeground(QColor("#569CD6"))  # VS Code 蓝色
        self.math_function_format.setFontWeight(QFont.Weight.Bold)

        # 常数格式 - 红色
        self.constant_format = QTextCharFormat()
        self.constant_format.setForeground(QColor("#CE9178"))  # VS Code 橙色
        self.constant_format.setFontWeight(QFont.Weight.Bold)

        # 数字格式 - 浅蓝色
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#B5CEA8"))  # VS Code 浅绿色

        # 时间变量格式 - 紫色
        self.time_variable_format = QTextCharFormat()
        self.time_variable_format.setForeground(QColor("#C586C0"))  # VS Code 紫色
        self.time_variable_format.setFontWeight(QFont.Weight.Bold)

        # 括号格式 - 黄色
        self.bracket_format = QTextCharFormat()
        self.bracket_format.setForeground(QColor("#FFD700"))  # 金黄色

        # 运算符格式 - 粉色
        self.operator_format = QTextCharFormat()
        self.operator_format.setForeground(QColor("#D4A5FF"))  # 浅紫色

        # 错误格式 - 红色波浪线
        self.error_format = QTextCharFormat()
        self.error_format.setForeground(QColor("#F44747"))  # 错误红
        self.error_format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.WaveUnderline)

        # 定义关键字模式
        self.math_functions = [
            'sin', 'cos', 'tan', 'asin', 'acos', 'atan',
            'sinh', 'cosh', 'tanh', 'exp', 'log', 'log10', 'log2',
            'sqrt', 'power', 'abs', 'floor', 'ceil', 'round',
            'clip', 'sign', 'maximum', 'minimum', 'len', 'min', 'max',
            'square', 'sawtooth', 'pulse', 'uniform', 'rand', 'randn'
        ]

        self.constants = ['PI', 'pi', 'E', 'e']
        self.time_variables = ['t']
        self.operators = [r'\+', r'-', r'\*', r'/', r'\^', r'%', r'=']

    def highlightBlock(self, text: str):
        """高亮文本块"""
        # 保存原始状态
        self.setCurrentBlockState(0)

        # 高亮数学函数
        for func in self.math_functions:
            pattern = re.compile(r'\b' + func + r'\b')
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), self.math_function_format)

        # 高亮常数
        for const in self.constants:
            pattern = re.compile(r'\b' + const + r'\b')
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), self.constant_format)

        # 高亮时间变量
        for var in self.time_variables:
            pattern = re.compile(r'\b' + var + r'\b')
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), self.time_variable_format)

        # 高亮数字
        pattern = re.compile(r'\b\d+\.?\d*\b')
        for match in pattern.finditer(text):
            self.setFormat(match.start(), match.end() - match.start(), self.number_format)

        # 高亮括号
        pattern = re.compile(r'[()]')
        for match in pattern.finditer(text):
            self.setFormat(match.start(), match.end() - match.start(), self.bracket_format)

        # 高亮运算符
        for op in self.operators:
            pattern = re.compile(op)
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), self.operator_format)


class FunctionEditorWidget(QWidget):
    """函数编辑器组件"""

    # 信号定义
    expressionChanged = pyqtSignal(str)  # 表达式改变信号
    expressionValid = pyqtSignal(bool, str)  # 表达式验证信号
    insertRequested = pyqtSignal(str)  # 插入函数请求信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parser = get_parser()
        self.current_expression = ""
        self.validation_timer = QTimer()
        self.validation_timer.setSingleShot(True)
        self.validation_timer.timeout.connect(self.validate_expression)

        self.setup_ui()
        self.setup_function_palette()

    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # 标题和状态栏
        header_layout = QHBoxLayout()

        title_label = QLabel("📝 函数表达式编辑器")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2C3E50;
                background: transparent;
            }
        """)
        header_layout.addWidget(title_label)

        self.status_label = QLabel("✅ 就绪")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #27AE60;
                background: transparent;
            }
        """)
        header_layout.addWidget(self.status_label)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # 主要编辑区域
        editor_container = QFrame()
        editor_container.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border: 2px solid #3E3E42;
                border-radius: 6px;
            }
        """)
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(5, 5, 5, 5)

        # 函数输入框
        self.function_input = QTextEdit()
        self.function_input.setPlaceholderText("输入函数表达式，例如: sin(2*PI*440*t)")
        self.function_input.setMinimumHeight(80)
        self.function_input.setMaximumHeight(100)
        self.function_input.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: none;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 13px;
                padding: 8px;
            }
            QTextEdit:focus {
                border: 1px solid #007ACC;
            }
        """)

        # 设置字体
        font = QFont("Consolas", 13)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.function_input.setFont(font)

        # 添加语法高亮
        self.highlighter = FunctionSyntaxHighlighter(self.function_input.document())

        # 连接文本变化信号
        self.function_input.textChanged.connect(self.on_text_changed)

        editor_layout.addWidget(self.function_input)
        layout.addWidget(editor_container)

        # 实时预览区域
        preview_label = QLabel("🔍 实时预览:")
        preview_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                font-weight: bold;
                color: #2C3E50;
                background: transparent;
            }
        """)
        layout.addWidget(preview_label)

        self.preview_label = QLabel("sin(2*PI*440*t)")
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: #F8F9FA;
                border: 1px solid #DEE2E6;
                border-radius: 4px;
                padding: 6px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                color: #495057;
                min-height: 30px;
                max-height: 30px;
            }
        """)
        self.preview_label.setWordWrap(True)
        layout.addWidget(self.preview_label)

        # 函数面板区域
        palette_label = QLabel("📚 快速插入:")
        palette_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                font-weight: bold;
                color: #2C3E50;
                background: transparent;
            }
        """)
        layout.addWidget(palette_label)

        # 可滚动的函数按钮区域
        palette_scroll = QScrollArea()
        palette_scroll.setWidgetResizable(True)
        palette_scroll.setMaximumHeight(80)
        palette_scroll.setMinimumHeight(60)
        palette_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #DEE2E6;
                border-radius: 4px;
                background-color: #F8F9FA;
            }
            QScrollArea::-vertical-scrollbar {
                width: 6px;
            }
            QScrollArea::-vertical-scrollbar:hover {
                width: 8px;
            }
        """)

        self.function_palette_widget = QWidget()
        self.function_palette_layout = QVBoxLayout(self.function_palette_widget)
        self.function_palette_layout.setSpacing(2)
        self.function_palette_layout.setContentsMargins(4, 4, 4, 4)

        palette_scroll.setWidget(self.function_palette_widget)
        layout.addWidget(palette_scroll)

        # 帮助提示区域 - 简化
        help_label = QLabel("💡 点击按钮快速插入 | 实时验证语法")
        help_label.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: #6C757D;
                background: transparent;
                padding: 2px;
            }
        """)
        help_label.setWordWrap(False)
        layout.addWidget(help_label)

    def setup_function_palette(self):
        """设置函数面板"""
        # 定义函数分类
        function_categories = {
            "基础函数": [
                ("sin(t)", "正弦函数"),
                ("cos(t)", "余弦函数"),
                ("tan(t)", "正切函数"),
                ("exp(t)", "指数函数"),
                ("log(t)", "自然对数"),
                ("sqrt(t)", "平方根"),
            ],
            "高级函数": [
                ("sinh(t)", "双曲正弦"),
                ("cosh(t)", "双曲余弦"),
                ("abs(t)", "绝对值"),
                ("power(t,2)", "幂函数"),
                ("floor(t)", "向下取整"),
                ("ceil(t)", "向上取整"),
            ],
            "波形函数": [
                ("square(2*PI*440*t)", "方波"),
                ("sawtooth(2*PI*440*t)", "锯齿波"),
                ("pulse(t)", "脉冲波"),
                ("uniform(-1,1,len(t))", "均匀分布"),
                ("randn(len(t))", "正态分布"),
            ],
            "常用常数": [
                ("PI", "圆周率 π"),
                ("E", "自然常数 e"),
                ("2*PI*440*t", "A4音符频率"),
                ("1/(2*PI)*log(t)", "对数频率"),
            ]
        }

        # 创建分类函数按钮
        for category, functions in function_categories.items():
            category_label = QLabel(f"📁 {category}")
            category_label.setStyleSheet("""
                QLabel {
                    font-size: 10px;
                    font-weight: bold;
                    color: #495057;
                    background: transparent;
                    margin-top: 2px;
                    margin-bottom: 1px;
                }
            """)
            self.function_palette_layout.addWidget(category_label)

            button_layout = QHBoxLayout()
            button_layout.setSpacing(3)

            for func, desc in functions:
                btn = QPushButton(f"{func}")
                btn.setToolTip(desc)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #E9ECEF;
                        color: #495057;
                        border: 1px solid #CED4DA;
                        border-radius: 3px;
                        padding: 2px 5px;
                        font-family: 'Consolas', 'Monaco', monospace;
                        font-size: 10px;
                        min-height: 18px;
                        max-height: 22px;
                    }
                    QPushButton:hover {
                        background-color: #007ACC;
                        color: white;
                        border-color: #007ACC;
                    }
                    QPushButton:pressed {
                        background-color: #005A9E;
                    }
                """)
                btn.clicked.connect(lambda checked, f=func: self.insert_function(f))
                button_layout.addWidget(btn)

            self.function_palette_layout.addLayout(button_layout)

    def on_text_changed(self):
        """文本变化处理"""
        text = self.function_input.toPlainText()
        self.current_expression = text

        # 更新预览
        self.update_preview(text)

        # 重置验证定时器（延迟验证）
        self.validation_timer.stop()
        self.validation_timer.start(500)  # 500ms延迟

        # 发出表达式变化信号
        self.expressionChanged.emit(text)

    def update_preview(self, text: str):
        """更新预览显示"""
        if not text.strip():
            self.preview_label.setText("（空表达式）")
            return

        # 显示预处理后的表达式
        try:
            processed = self.parser.preprocess_expression(text)
            self.preview_label.setText(processed)
            self.preview_label.setStyleSheet("""
                QLabel {
                    background-color: #F8F9FA;
                    border: 1px solid #DEE2E6;
                    border-radius: 4px;
                    padding: 8px;
                    font-family: 'Consolas', 'Monaco', monospace;
                    font-size: 12px;
                    color: #495057;
                    min-height: 40px;
                }
            """)
        except Exception as e:
            self.preview_label.setText(f"预处理错误: {str(e)}")
            self.preview_label.setStyleSheet("""
                QLabel {
                    background-color: #F8D7DA;
                    border: 1px solid #F5C6CB;
                    border-radius: 4px;
                    padding: 8px;
                    font-family: 'Consolas', 'Monaco', monospace;
                    font-size: 12px;
                    color: #721C24;
                    min-height: 40px;
                }
            """)

    def validate_expression(self):
        """验证表达式"""
        text = self.function_input.toPlainText().strip()

        if not text:
            self.set_status("✅ 就绪", True)
            self.expressionValid.emit(True, "")
            return

        try:
            # 尝试验证表达式
            self.parser.validate_expression(text)
            self.parser.preprocess_expression(text)

            # 尝试解析表达式
            self.parser.parse_expression(text)

            self.set_status("✅ 表达式有效", True)
            self.expressionValid.emit(True, "")

        except ParseError as e:
            error_msg = str(e)
            self.set_status(f"❌ {error_msg}", False)
            self.expressionValid.emit(False, error_msg)
        except Exception as e:
            error_msg = f"未知错误: {str(e)}"
            self.set_status(f"❌ {error_msg}", False)
            self.expressionValid.emit(False, error_msg)

    def set_status(self, message: str, is_valid: bool):
        """设置状态显示"""
        self.status_label.setText(message)
        if is_valid:
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #27AE60;
                    background: transparent;
                }
            """)
        else:
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #DC3545;
                    background: transparent;
                }
            """)

    def insert_function(self, function: str):
        """在光标位置插入函数"""
        cursor = self.function_input.textCursor()

        # 在函数前后添加空格（如果需要）
        text_before = self.function_input.toPlainText()
        position = cursor.position()

        # 检查是否需要在函数前添加运算符
        need_operator = False
        if position > 0:
            char_before = text_before[position - 1]
            if char_before not in [' ', '+', '-', '*', '/', '(', '^', '%']:
                need_operator = True

        # 构建要插入的文本
        insert_text = function
        if need_operator:
            insert_text = "*" + insert_text

        # 插入文本
        cursor.insertText(insert_text)

        # 设置焦点到输入框
        self.function_input.setFocus()

        # 发出插入请求信号
        self.insertRequested.emit(insert_text)

    def get_expression(self) -> str:
        """获取当前表达式"""
        return self.function_input.toPlainText().strip()

    def set_expression(self, expression: str):
        """设置表达式"""
        self.function_input.setPlainText(expression)
        self.current_expression = expression
        self.update_preview(expression)

    def clear(self):
        """清空编辑器"""
        self.function_input.clear()
        self.current_expression = ""
        self.preview_label.setText("（空表达式）")
        self.set_status("✅ 就绪", True)

    def set_focus(self):
        """设置焦点到输入框"""
        self.function_input.setFocus()


class CalculatorStyleFunctionEditor(QWidget):
    """科学计算器风格的函数编辑器"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 创建函数编辑器
        self.editor = FunctionEditorWidget(self)
        layout.addWidget(self.editor)

        # 添加操作按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        clear_btn = QPushButton("🗑️ 清空")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #DC3545;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #C82333;
            }
        """)
        clear_btn.clicked.connect(self.editor.clear)
        button_layout.addWidget(clear_btn)

        validate_btn = QPushButton("✅ 验证")
        validate_btn.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        validate_btn.clicked.connect(self.editor.validate_expression)
        button_layout.addWidget(validate_btn)

        button_layout.addStretch()

        layout.addLayout(button_layout)

    def get_expression(self) -> str:
        """获取表达式"""
        return self.editor.get_expression()

    def set_expression(self, expression: str):
        """设置表达式"""
        self.editor.set_expression(expression)

    def clear(self):
        """清空"""
        self.editor.clear()