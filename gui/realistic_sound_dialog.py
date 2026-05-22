"""
真实感声音增强对话框 - 高度优化版本
使用后台线程和缓存来消除界面卡顿
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSlider, QGroupBox, QCheckBox, QTextEdit,
    QTabWidget, QWidget, QSpinBox, QDoubleSpinBox, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QMutex
from PyQt6.QtGui import QFont
import numpy as np

from core.realistic_sound_enhancer import get_enhancer


class EnhancementWorker(QThread):
    """后台增强处理线程"""
    finished = pyqtSignal(np.ndarray)
    progress = pyqtSignal(str)

    def __init__(self, waveform, sample_rate, enhancer, preset_type, intensity, advanced_params):
        super().__init__()
        self.waveform = waveform.copy()
        self.sample_rate = sample_rate
        self.enhancer = enhancer
        self.preset_type = preset_type
        self.intensity = intensity
        self.advanced_params = advanced_params
        self.mutex = QMutex()

    def run(self):
        """在后台线程中执行增强处理"""
        try:
            self.mutex.lock()
            self.progress.emit("正在处理...")

            if self.preset_type == "none":
                result = self.waveform.copy()
            else:
                # 创建临时增强器实例来应用预设
                from core.realistic_sound_enhancer import RealisticSoundEnhancer
                temp_enhancer = RealisticSoundEnhancer()
                result = temp_enhancer.apply_preset(self.waveform, self.preset_type)

                # 应用强度调节 - 使用非线性混合以保持预设特色
                if self.intensity < 1.0:
                    # 使用指数曲线来保持预设的主要特色
                    blend_factor = self.intensity ** 0.7  # 非线性混合
                    result = self.waveform * (1 - blend_factor) + result * blend_factor

            # 应用高级参数（无论是否有预设，高级参数都应该生效）
            if any(self.advanced_params.values()):
                variance = self.advanced_params.get('variance', 0)
                harmonics = [
                    self.advanced_params.get('harmonic_2', 0),
                    self.advanced_params.get('harmonic_3', 0),
                    self.advanced_params.get('harmonic_4', 0)
                ]
                wow_flutter = self.advanced_params.get('wow_flutter', 0)
                noise_floor = self.advanced_params.get('noise_floor', 0)

                if variance > 0:
                    result = self.enhancer.add_natural_variance(result, variance)

                if any(harmonics):
                    result = self.enhancer.add_harmonic_distortion(result, harmonics)

                if wow_flutter > 0 or noise_floor > 0:
                    result = self.enhancer.add_analog_imperfection(result, wow_flutter, noise_floor)

            self.progress.emit("处理完成")
            self.finished.emit(result)

        except Exception as e:
            self.progress.emit(f"处理失败: {str(e)}")
            self.finished.emit(self.waveform)  # 返回原始波形
        finally:
            self.mutex.unlock()


class RealisticSoundDialog(QDialog):
    """真实感声音增强对话框 - 优化版本"""

    def __init__(self, waveform, sample_rate, parent=None):
        super().__init__(parent)
        self.original_waveform = waveform.copy()
        self.enhanced_waveform = waveform.copy()
        self.sample_rate = sample_rate
        self.enhancer = get_enhancer()

        # 缓存系统
        self._enhancement_cache = {}
        self._current_worker = None

        # 禁用实时预览，手动应用模式
        self._manual_apply_mode = True

        self.setup_ui()

        # 不自动应用增强，等待用户操作
        self.status_label.setText("就绪 - 点击'应用增强'按钮来处理")

        # 初始化对比统计显示
        if hasattr(self, 'stats_text'):
            self.stats_text.setHtml("<h3>声音参数对比:</h3><p>请先点击'应用增强'按钮查看效果对比</p>")

    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("真实感声音增强")
        self.setMinimumSize(600, 500)
        self.resize(700, 600)

        layout = QVBoxLayout(self)

        # 创建选项卡
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)

        # 预设选项卡
        preset_tab = self.create_preset_tab()
        tab_widget.addTab(preset_tab, "预设效果")

        # 高级选项卡
        advanced_tab = self.create_advanced_tab()
        tab_widget.addTab(advanced_tab, "高级控制")

        # 对比选项卡
        comparison_tab = self.create_comparison_tab()
        tab_widget.addTab(comparison_tab, "效果对比")

        # 底部状态和按钮
        bottom_layout = QVBoxLayout()

        # 状态显示
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("状态:"))
        self.status_label = QLabel("就绪 - 点击'应用增强'按钮来处理")
        self.status_label.setStyleSheet("color: blue; font-weight: bold;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        bottom_layout.addLayout(status_layout)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(20)
        bottom_layout.addWidget(self.progress_bar)

        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.apply_enhancement_button = QPushButton("应用增强")
        self.apply_enhancement_button.setMinimumHeight(35)
        self.apply_enhancement_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.apply_enhancement_button.clicked.connect(self.apply_enhancement_manual)
        button_layout.addWidget(self.apply_enhancement_button)

        self.preview_button = QPushButton("预览效果")
        self.preview_button.setMinimumHeight(35)
        self.preview_button.clicked.connect(self.preview_enhancement)
        button_layout.addWidget(self.preview_button)

        self.apply_button = QPushButton("保存并关闭")
        self.apply_button.setMinimumHeight(35)
        self.apply_button.clicked.connect(self.apply_and_close)
        button_layout.addWidget(self.apply_button)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.setMinimumHeight(35)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        bottom_layout.addLayout(button_layout)
        layout.addLayout(bottom_layout)

    def create_preset_tab(self):
        """创建预设选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 预设选择
        preset_group = QGroupBox("声音预设")
        preset_layout = QVBoxLayout()

        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "无增强",
            "自然声音",
            "温暖声音",
            "明亮声音",
            "复古声音",
            "声学乐器",
            "电子音乐"
        ])
        self.preset_combo.currentIndexChanged.connect(self.on_preset_changed)
        preset_layout.addWidget(self.preset_combo)

        # 预设描述
        self.preset_description = QTextEdit()
        self.preset_description.setMaximumHeight(80)
        self.preset_description.setReadOnly(True)
        preset_layout.addWidget(self.preset_description)

        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)

        # 快速调节
        quick_group = QGroupBox("快速调节")
        quick_layout = QVBoxLayout()

        # 强度滑块
        intensity_layout = QHBoxLayout()
        intensity_layout.addWidget(QLabel("效果强度:"))
        self.intensity_slider = QSlider(Qt.Orientation.Horizontal)
        self.intensity_slider.setRange(0, 100)
        self.intensity_slider.setValue(50)
        self.intensity_slider.valueChanged.connect(self.on_intensity_changed)
        intensity_layout.addWidget(self.intensity_slider)
        self.intensity_value = QLabel("50%")
        self.intensity_value.setFixedWidth(40)
        intensity_layout.addWidget(self.intensity_value)
        quick_layout.addLayout(intensity_layout)

        quick_group.setLayout(quick_layout)
        layout.addWidget(quick_group)

        # 效果说明
        info_group = QGroupBox("效果说明")
        info_layout = QVBoxLayout()
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(150)
        info_text.setHtml("""
        <h3>真实感增强效果说明:</h3>
        <p><b>自然声音:</b> 轻微增强，添加自然变化和谐波</p>
        <p><b>温暖声音:</b> 强调低频，添加模拟设备特性</p>
        <p><b>明亮声音:</b> 强调高频，清晰明亮</p>
        <p><b>复古声音:</b> 模拟老式录音设备特性</p>
        <p><b>声学乐器:</b> 强调瞬态响应和空间感</p>
        <p><b>电子音乐:</b> 强调频谱特性和调制效果</p>
        """)
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        layout.addStretch()
        return tab

    def create_advanced_tab(self):
        """创建高级控制选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 自然变化
        variance_group = QGroupBox("自然变化")
        variance_layout = QVBoxLayout()
        variance_slider_layout = QHBoxLayout()
        variance_slider_layout.addWidget(QLabel("变化程度:"))
        self.variance_slider = QSlider(Qt.Orientation.Horizontal)
        self.variance_slider.setRange(0, 100)
        self.variance_slider.setValue(30)
        self.variance_slider.valueChanged.connect(self.on_advanced_param_changed)
        variance_slider_layout.addWidget(self.variance_slider)
        self.variance_value = QLabel("30%")
        variance_slider_layout.addWidget(self.variance_value)
        variance_layout.addLayout(variance_slider_layout)
        variance_group.setLayout(variance_layout)
        layout.addWidget(variance_group)

        # 谐波失真
        harmonic_group = QGroupBox("谐波失真")
        harmonic_layout = QVBoxLayout()
        for i, label in enumerate(["2次谐波", "3次谐波", "4次谐波"], 1):
            harmonic_slider_layout = QHBoxLayout()
            harmonic_slider_layout.addWidget(QLabel(f"{label}:"))
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(0, 100)
            if i == 1:
                slider.setValue(50)  # 3次谐波默认值
            else:
                slider.setValue(20)  # 其他默认值
            slider.valueChanged.connect(self.on_advanced_param_changed)
            harmonic_slider_layout.addWidget(slider)
            value_label = QLabel(f"{slider.value()}%")
            value_label.setFixedWidth(40)
            harmonic_slider_layout.addWidget(value_label)
            harmonic_layout.addLayout(harmonic_slider_layout)

            # 保存引用
            if i == 1:
                self.harmonic_2_slider = slider
                self.harmonic_2_value = value_label
            elif i == 2:
                self.harmonic_3_slider = slider
                self.harmonic_3_value = value_label
            else:
                self.harmonic_4_slider = slider
                self.harmonic_4_value = value_label

        harmonic_group.setLayout(harmonic_layout)
        layout.addWidget(harmonic_group)

        # 房间声学
        room_group = QGroupBox("房间声学")
        room_layout = QVBoxLayout()

        room_size_layout = QHBoxLayout()
        room_size_layout.addWidget(QLabel("房间大小:"))
        self.room_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.room_size_slider.setRange(0, 100)
        self.room_size_slider.setValue(30)
        self.room_size_slider.valueChanged.connect(self.on_advanced_param_changed)
        room_size_layout.addWidget(self.room_size_slider)
        self.room_size_value = QLabel("30%")
        self.room_size_value.setFixedWidth(40)
        room_size_layout.addWidget(self.room_size_value)
        room_layout.addLayout(room_size_layout)

        damping_layout = QHBoxLayout()
        damping_layout.addWidget(QLabel("阻尼系数:"))
        self.damping_slider = QSlider(Qt.Orientation.Horizontal)
        self.damping_slider.setRange(0, 100)
        self.damping_slider.setValue(50)
        self.damping_slider.valueChanged.connect(self.on_advanced_param_changed)
        damping_layout.addWidget(self.damping_slider)
        self.damping_value = QLabel("50%")
        self.damping_value.setFixedWidth(40)
        damping_layout.addWidget(self.damping_value)
        room_layout.addLayout(damping_layout)

        room_group.setLayout(room_layout)
        layout.addWidget(room_group)

        # 模拟设备特性
        analog_group = QGroupBox("模拟设备特性")
        analog_layout = QVBoxLayout()

        wow_flutter_layout = QHBoxLayout()
        wow_flutter_layout.addWidget(QLabel("抖动:"))
        self.wow_flutter_slider = QSlider(Qt.Orientation.Horizontal)
        self.wow_flutter_slider.setRange(0, 100)
        self.wow_flutter_slider.setValue(10)
        self.wow_flutter_slider.valueChanged.connect(self.on_advanced_param_changed)
        wow_flutter_layout.addWidget(self.wow_flutter_slider)
        self.wow_flutter_value = QLabel("10%")
        self.wow_flutter_value.setFixedWidth(40)
        wow_flutter_layout.addWidget(self.wow_flutter_value)
        analog_layout.addLayout(wow_flutter_layout)

        noise_floor_layout = QHBoxLayout()
        noise_floor_layout.addWidget(QLabel("噪声底:"))
        self.noise_floor_slider = QSlider(Qt.Orientation.Horizontal)
        self.noise_floor_slider.setRange(0, 100)
        self.noise_floor_slider.setValue(5)
        self.noise_floor_slider.valueChanged.connect(self.on_advanced_param_changed)
        noise_floor_layout.addWidget(self.noise_floor_slider)
        self.noise_floor_value = QLabel("5%")
        self.noise_floor_value.setFixedWidth(40)
        noise_floor_layout.addWidget(self.noise_floor_value)
        analog_layout.addLayout(noise_floor_layout)

        analog_group.setLayout(analog_layout)
        layout.addWidget(analog_group)

        layout.addStretch()
        return tab

    def create_comparison_tab(self):
        """创建效果对比选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 对比说明
        comparison_label = QLabel("对比原始声音与增强声音")
        comparison_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(comparison_label)

        # 控制按钮
        button_layout = QHBoxLayout()

        self.play_original_button = QPushButton("播放原始声音")
        self.play_original_button.setMinimumHeight(40)
        self.play_original_button.clicked.connect(self.play_original)
        button_layout.addWidget(self.play_original_button)

        self.play_enhanced_button = QPushButton("播放增强声音")
        self.play_enhanced_button.setMinimumHeight(40)
        self.play_enhanced_button.clicked.connect(self.play_enhanced)
        button_layout.addWidget(self.play_enhanced_button)

        layout.addLayout(button_layout)

        # 效果统计
        stats_group = QGroupBox("效果统计")
        stats_layout = QVBoxLayout()

        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(200)
        stats_layout.addWidget(self.stats_text)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        layout.addStretch()
        return tab

    def on_preset_changed(self, index):
        """预设改变事件 - 仅更新描述，不触发处理"""
        descriptions = {
            0: "无增强 - 保持原始声音不变",
            1: "自然声音 - 添加轻微的自然变化和谐波，使声音更自然",
            2: "温暖声音 - 强调低频，添加模拟设备特性，产生温暖感",
            3: "明亮声音 - 强调高频，声音清晰明亮",
            4: "复古声音 - 模拟老式录音设备特性，增加怀旧感",
            5: "声学乐器 - 强调瞬态响应和空间感，模拟真实乐器",
            6: "电子音乐 - 强调频谱特性和调制效果"
        }

        self.preset_description.setPlainText(descriptions.get(index, ""))
        # 更新状态提示用户需要手动应用
        self.status_label.setText("设置已更改 - 点击'应用增强'按钮来处理")

    def on_intensity_changed(self, value):
        """强度改变事件 - 仅更新显示，不触发处理"""
        intensity = value / 100.0
        self.intensity_value.setText(f"{int(intensity * 100)}%")
        # 更新状态提示用户需要手动应用
        self.status_label.setText("强度已调整 - 点击'应用增强'按钮来处理")

    def on_advanced_param_changed(self):
        """高级参数改变事件 - 仅更新状态，不触发处理"""
        self.status_label.setText("高级参数已调整 - 点击'应用增强'按钮来处理")

    def apply_enhancement_manual(self):
        """手动应用增强 - 使用后台线程"""
        if hasattr(self, '_current_worker') and self._current_worker is not None:
            if self._current_worker.isRunning():
                self.status_label.setText("正在处理中，请等待...")
                return

        # 获取当前参数
        intensity = self.intensity_slider.value() / 100.0
        preset_index = self.preset_combo.currentIndex()
        preset_names = ["none", "natural", "warm", "bright", "vintage", "acoustic", "electronic"]
        preset_type = preset_names[preset_index]

        # 获取高级参数
        advanced_params = {
            'variance': self.variance_slider.value() / 100.0,
            'harmonic_2': self.harmonic_2_slider.value() / 100.0,
            'harmonic_3': self.harmonic_3_slider.value() / 100.0,
            'harmonic_4': self.harmonic_4_slider.value() / 100.0,
            'wow_flutter': self.wow_flutter_slider.value() / 100.0,
            'noise_floor': self.noise_floor_slider.value() / 100.0,
        }

        # 检查缓存
        cache_key = f"{preset_type}_{intensity}_{advanced_params}"
        if cache_key in self._enhancement_cache:
            self.enhanced_waveform = self._enhancement_cache[cache_key]
            self.status_label.setText("使用缓存结果")
            self.update_comparison_stats()
            return

        # 显示进度
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.apply_enhancement_button.setEnabled(False)
        self.status_label.setText("正在处理...")

        # 创建并启动后台工作线程
        self._current_worker = EnhancementWorker(
            self.original_waveform,
            self.sample_rate,
            self.enhancer,
            preset_type,
            intensity,
            advanced_params
        )
        self._current_worker.finished.connect(self.on_enhancement_finished)
        self._current_worker.progress.connect(self.on_enhancement_progress)
        self._current_worker.start()

    def on_enhancement_progress(self, message):
        """处理进度更新"""
        self.status_label.setText(message)

    def on_enhancement_finished(self, result_waveform):
        """处理完成"""
        self.enhanced_waveform = result_waveform

        # 缓存结果
        intensity = self.intensity_slider.value() / 100.0
        preset_index = self.preset_combo.currentIndex()
        preset_names = ["none", "natural", "warm", "bright", "vintage", "acoustic", "electronic"]
        preset_type = preset_names[preset_index]

        advanced_params = {
            'variance': self.variance_slider.value() / 100.0,
            'harmonic_2': self.harmonic_2_slider.value() / 100.0,
            'harmonic_3': self.harmonic_3_slider.value() / 100.0,
            'harmonic_4': self.harmonic_4_slider.value() / 100.0,
            'wow_flutter': self.wow_flutter_slider.value() / 100.0,
            'noise_floor': self.noise_floor_slider.value() / 100.0,
        }

        cache_key = f"{preset_type}_{intensity}_{advanced_params}"
        self._enhancement_cache[cache_key] = result_waveform

        # 限制缓存大小
        if len(self._enhancement_cache) > 20:
            # 删除最旧的缓存项
            oldest_key = next(iter(self._enhancement_cache))
            del self._enhancement_cache[oldest_key]

        # 更新UI
        self.progress_bar.setVisible(False)
        self.apply_enhancement_button.setEnabled(True)
        self.status_label.setText("处理完成")
        self.update_comparison_stats()

    def apply_enhancement(self):
        """兼容旧版本的调用方法 - 直接使用后台线程"""
        self.apply_enhancement_manual()

    def _apply_lightweight_preset(self, preset_type):
        """应用轻量级预设效果，避免复杂计算"""
        enhanced = self.original_waveform.copy()

        if preset_type == "natural":
            # 轻微自然变化
            noise = np.random.normal(0, 0.01, len(enhanced))
            enhanced = enhanced * (1 + noise)
            enhanced = np.clip(enhanced, -1, 1)

        elif preset_type == "warm":
            # 简单低频增强
            enhanced = enhanced * 1.1
            # 添加轻微失真
            enhanced = np.tanh(enhanced)

        elif preset_type == "bright":
            # 简单高频增强
            enhanced = enhanced * 1.2
            enhanced = np.clip(enhanced, -1, 1)

        elif preset_type == "vintage":
            # 模拟失真
            enhanced = np.tanh(enhanced * 1.2)
            # 添加轻微噪声
            noise = np.random.normal(0, 0.005, len(enhanced))
            enhanced = enhanced + noise
            enhanced = np.clip(enhanced, -1, 1)

        elif preset_type == "acoustic":
            # 简单包络
            envelope = np.exp(-np.arange(len(enhanced)) / (len(enhanced) * 0.3))
            enhanced = enhanced * (0.7 + 0.3 * envelope)

        elif preset_type == "electronic":
            # 添加调制效果
            modulation = 1 + 0.1 * np.sin(2 * np.pi * 5 * np.arange(len(enhanced)) / len(enhanced))
            enhanced = enhanced * modulation
            enhanced = np.clip(enhanced, -1, 1)

        return enhanced

    def _lightweight_variance(self, waveform, level):
        """轻量级自然变化"""
        noise = np.random.normal(0, level * 0.1, len(waveform))
        result = waveform * (1 + noise)
        return np.clip(result, -1, 1)

    def _lightweight_harmonics(self, waveform, harmonics):
        """轻量级谐波失真"""
        enhanced = waveform.copy()
        for i, strength in enumerate(harmonics):
            if strength > 0:
                # 简单的谐波生成
                freq_multiplier = i + 2
                harmonic = waveform * strength * (1 + 0.1 * np.sin(freq_multiplier * np.pi * np.arange(len(waveform)) / len(waveform)))
                enhanced += harmonic
        return np.clip(enhanced, -1, 1)

    def _lightweight_analog(self, waveform, wow_flutter, noise_floor):
        """轻量级模拟效果"""
        enhanced = waveform.copy()

        # 简单颤音
        if wow_flutter > 0:
            modulation = 1 + wow_flutter * 0.05 * np.sin(2 * np.pi * 2 * np.arange(len(enhanced)) / len(enhanced))
            enhanced = enhanced * modulation

        # 简单噪声
        if noise_floor > 0:
            noise = np.random.normal(0, noise_floor * 0.1, len(enhanced))
            enhanced = enhanced + noise

        return np.clip(enhanced, -1, 1)

    def update_stats(self):
        """更新统计信息"""
        try:
            # 计算波形差异
            waveform_diff = np.mean(np.abs(self.enhanced_waveform - self.original_waveform))

            original_stats = {
                "RMS": np.sqrt(np.mean(self.original_waveform ** 2)),
                "Peak": np.max(np.abs(self.original_waveform)),
                "Dynamic Range": np.ptp(self.original_waveform)
            }

            enhanced_stats = {
                "RMS": np.sqrt(np.mean(self.enhanced_waveform ** 2)),
                "Peak": np.max(np.abs(self.enhanced_waveform)),
                "Dynamic Range": np.ptp(self.enhanced_waveform)
            }

            stats_text = "<h3>声音参数对比:</h3>"
            stats_text += "<table border='1' style='border-collapse: collapse;'>"
            stats_text += "<tr><th>参数</th><th>原始</th><th>增强</th><th>变化</th></tr>"

            for key in original_stats:
                original = original_stats[key]
                enhanced = enhanced_stats[key]
                change = enhanced - original
                change_percent = (change / original * 100) if original != 0 else 0

                change_color = "green" if change > 0 else "red"
                change_symbol = "+" if change > 0 else ""

                stats_text += f"<tr><td>{key}</td>"
                stats_text += f"<td>{original:.4f}</td>"
                stats_text += f"<td>{enhanced:.4f}</td>"
                stats_text += f"<td style='color:{change_color}'>{change_symbol}{change_percent:.1f}%</td></tr>"

            stats_text += "</table>"

            # 添加波形差异信息
            diff_percent = (waveform_diff / np.mean(np.abs(self.original_waveform))) * 100 if np.mean(np.abs(self.original_waveform)) > 0 else 0
            stats_text += f"<p><b>波形整体差异:</b> {waveform_diff:.6f} ({diff_percent:.1f}%)</p>"

            self.stats_text.setHtml(stats_text)

        except Exception as e:
            self.stats_text.setPlainText(f"统计计算错误: {str(e)}")

    def update_comparison_stats(self):
        """更新对比统计信息（与update_stats相同）"""
        self.update_stats()

    def preview_enhancement(self):
        """预览增强效果"""
        try:
            from core.audio_controller import AudioController
            audio_controller = AudioController()

            # 加载增强后的波形
            audio_controller.load_waveform(self.enhanced_waveform, self.sample_rate)

            # 播放
            audio_controller.play()

        except Exception as e:
            print(f"Preview error: {e}")

    def play_original(self):
        """播放原始声音"""
        try:
            from core.audio_controller import AudioController
            audio_controller = AudioController()
            audio_controller.load_waveform(self.original_waveform, self.sample_rate)
            audio_controller.play()
        except Exception as e:
            print(f"Play original error: {e}")

    def play_enhanced(self):
        """播放增强声音"""
        try:
            from core.audio_controller import AudioController
            audio_controller = AudioController()
            audio_controller.load_waveform(self.enhanced_waveform, self.sample_rate)
            audio_controller.play()
        except Exception as e:
            print(f"Play enhanced error: {e}")

    def apply_and_close(self):
        """应用并关闭对话框"""
        self.accept()

    def get_enhanced_waveform(self):
        """获取增强后的波形"""
        return self.enhanced_waveform