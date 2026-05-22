"""
预设波形模板管理器
提供常用的波形表达式模板
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
    QPushButton, QLabel, QTextEdit, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt

class PresetManager(QWidget):
    """预设模板管理器"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 预设模板库
        self.presets = {
            "基础波形": {
                "正弦波 (440Hz)": "sin(2*PI*440*t)",
                "低频正弦波 (100Hz)": "sin(2*PI*100*t)",
                "高频正弦波 (1000Hz)": "sin(2*PI*1000*t)",
                "方波 (440Hz)": "signal.square(2*PI*440*t)",
                "锯齿波 (440Hz)": "signal.sawtooth(2*PI*440*t)",
                "脉冲波 (440Hz)": "pulse(2*PI*440*t, 0.5)"
            },

            "和弦": {
                "大三和弦": "0.5*sin(2*PI*440*t) + 0.3*sin(2*PI*554*t) + 0.2*sin(2*PI*659*t)",
                "小三和弦": "0.5*sin(2*PI*440*t) + 0.3*sin(2*PI*522*t) + 0.2*sin(2*PI*659*t)",
                "七和弦": "0.4*sin(2*PI*440*t) + 0.3*sin(2*PI*554*t) + 0.2*sin(2*PI*659*t) + 0.1*sin(2*PI*784*t)",
                "强力五和弦": "0.6*sin(2*PI*440*t) + 0.4*sin(2*PI*554*t) + 0.3*sin(2*PI*659*t)"
            },

            "调制效果": {
                "调幅 (AM)": "(1 + 0.5*sin(2*PI*10*t)) * sin(2*PI*440*t)",
                "调频 (FM)": "sin(2*PI*(440 + 50*sin(2*PI*5*t))*t)",
                "颤音": "(1 + 0.1*sin(2*PI*6*t)) * sin(2*PI*440*t)",
                " vibrato": "sin(2*PI*(440 + 10*sin(2*PI*5*t))*t)"
            },

            "特殊效果": {
                "衰减正弦波": "exp(-t*2) * sin(2*PI*440*t)",
                "包络波": "(1-exp(-t*10)) * exp(-t*0.5) * sin(2*PI*440*t)",
                "拍频": "sin(2*PI*440*t) + sin(2*PI*445*t)",
                "频率扫描": "sin(2*PI*(200 + 400*t)*t)",
                "噪音": "(random.rand(len(t)) - 0.5) * 0.5"
            },

            "复杂波形": {
                "合成器主音": "0.3*sin(2*PI*440*t) + 0.2*sin(2*PI*880*t) + 0.1*sin(2*PI*1320*t) + 0.05*sin(2*PI*1760*t)",
                "管风琴": "0.4*sin(2*PI*220*t) + 0.3*sin(2*PI*440*t) + 0.2*sin(2*PI*660*t) + 0.1*sin(2*PI*880*t)",
                "电子音": "signal.square(2*PI*110*t) * (1 + 0.5*sin(2*PI*8*t))",
                "卡拉OK-OK音": "exp(-t*3) * (sin(2*PI*1000*t) + sin(2*PI*1500*t))"
            },

            "测试信号": {
                "双音测试": "sin(2*PI*1000*t) + sin(2*PI*2000*t)",
                "多频测试": "sin(2*PI*500*t) + 0.5*sin(2*PI*1000*t) + 0.3*sin(2*PI*2000*t)",
                "线性扫描": "sin(2*PI*(20 + 1000*t)*t)",
                "对数扫描": "sin(2*PI*20*pow(50, t)*t)"
            },

            "音乐音阶": {
                "C大调音阶": "sin(2*PI*261.63*t) + sin(2*PI*293.66*t) + sin(2*PI*329.63*t) + sin(2*PI*349.23*t)",
                "A小调五声": "sin(2*PI*220*t) + sin(2*PI*261.63*t) + sin(2*PI*293.66*t) + sin(2*PI*329.63*t) + sin(2*PI*392*t)",
                "半音阶": "sin(2*PI*440*t) + sin(2*PI*466.16*t) + sin(2*PI*493.88*t) + sin(2*PI*523.25*t)"
            }
        }

        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 标题
        title = QLabel("预设波形模板")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # 分类和预设列表
        content_layout = QHBoxLayout()

        # 左侧：分类列表
        category_group = QGroupBox("分类")
        category_layout = QVBoxLayout()
        self.category_list = QListWidget()
        self.category_list.addItems(self.presets.keys())
        self.category_list.currentTextChanged.connect(self.on_category_changed)
        category_layout.addWidget(self.category_list)
        category_group.setLayout(category_layout)

        # 右侧：预设列表
        preset_group = QGroupBox("预设")
        preset_layout = QVBoxLayout()
        self.preset_list = QListWidget()
        self.preset_list.itemDoubleClicked.connect(self.on_preset_selected)
        preset_layout.addWidget(self.preset_list)

        # 应用按钮
        apply_btn = QPushButton("应用选中预设")
        apply_btn.clicked.connect(self.apply_selected_preset)
        preset_layout.addWidget(apply_btn)

        preset_group.setLayout(preset_layout)

        content_layout.addWidget(category_group)
        content_layout.addWidget(preset_group)
        layout.addLayout(content_layout)

        # 预设预览
        preview_group = QGroupBox("预览")
        preview_layout = QVBoxLayout()
        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(80)
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        # 初始化显示第一个分类
        if self.presets:
            # 使用索引设置当前项
            self.category_list.setCurrentRow(0)
            # 手动触发分类改变
            self.on_category_changed(list(self.presets.keys())[0])

    def on_category_changed(self, category):
        """分类改变事件"""
        self.preset_list.clear()

        if category in self.presets:
            presets = self.presets[category]
            self.preset_list.addItems(presets.keys())
            # 如果有预设，默认选中第一个
            if presets:
                self.preset_list.setCurrentRow(0)
                self.preview_preset()

    def on_preset_selected(self, item):
        """预设选择事件"""
        self.preview_preset()

    def preview_preset(self):
        """预览选中的预设"""
        category = self.category_list.currentText()
        preset_name = self.preset_list.currentItem().text()

        if category in self.presets and preset_name in self.presets[category]:
            expression = self.presets[category][preset_name]
            self.preview_text.setText(expression)

    def apply_selected_preset(self):
        """应用选中的预设"""
        if self.preset_list.currentItem() is None:
            return

        category = self.category_list.currentText()
        preset_name = self.preset_list.currentItem().text()

        if category in self.presets and preset_name in self.presets[category]:
            expression = self.presets[category][preset_name]

            # 发送信号给主窗口（如果有父窗口的话）
            if self.parent() and hasattr(self.parent(), 'set_expression'):
                self.parent().set_expression(expression)
            else:
                # 否则只显示在预览中
                self.preview_text.setText(expression)

            # 显示应用成功消息
            QMessageBox.information(self, "预设应用", f"已应用预设: {preset_name}")

    def get_current_expression(self) -> str:
        """获取当前选中的表达式"""
        category = self.category_list.currentText()
        preset_name = self.preset_list.currentItem().text() if self.preset_list.currentItem() else ""

        if category in self.presets and preset_name in self.presets[category]:
            return self.presets[category][preset_name]
        return ""

    def add_custom_preset(self, category: str, name: str, expression: str):
        """添加自定义预设"""
        if category not in self.presets:
            self.presets[category] = {}

        self.presets[category][name] = expression

        # 刷新UI
        current_category = self.category_list.currentText()
        self.category_list.clear()
        self.category_list.addItems(self.presets.keys())
        self.category_list.setCurrentText(current_category)

    def search_presets(self, keyword: str):
        """搜索预设"""
        results = []

        for category, presets in self.presets.items():
            for name, expression in presets.items():
                if (keyword.lower() in name.lower() or
                    keyword.lower() in expression.lower() or
                    keyword.lower() in category.lower()):
                    results.append({
                        'category': category,
                        'name': name,
                        'expression': expression
                    })

        return results