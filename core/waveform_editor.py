"""
波形编辑器
提供波形数据处理和编辑功能
"""

import numpy as np
from typing import Tuple, Optional, Callable
from scipy import signal as scipy_signal
from scipy.fft import fft, ifft, fftfreq

class WaveformEditor:
    """波形编辑器类"""

    def __init__(self):
        """初始化波形编辑器"""
        self.current_waveform = None
        self.sample_rate = 44100
        self.edit_history = []
        self.redo_history = []
        self.max_history = 50

    def load_waveform(self, waveform: np.ndarray, sample_rate: int = 44100):
        """
        加载波形数据
        :param waveform: 波形数据
        :param sample_rate: 采样率
        """
        self.current_waveform = np.asarray(waveform, dtype=np.float64)
        self.sample_rate = sample_rate
        self.edit_history = []
        self.redo_history = []

    def save_state(self):
        """保存当前状态到历史记录"""
        if self.current_waveform is not None:
            self.edit_history.append(self.current_waveform.copy())
            if len(self.edit_history) > self.max_history:
                self.edit_history.pop(0)
            self.redo_history.clear()  # 清空重做历史

    def undo(self) -> bool:
        """撤销操作"""
        if len(self.edit_history) > 0:
            self.redo_history.append(self.current_waveform.copy())
            self.current_waveform = self.edit_history.pop()
            return True
        return False

    def redo(self) -> bool:
        """重做操作"""
        if len(self.redo_history) > 0:
            self.edit_history.append(self.current_waveform.copy())
            self.current_waveform = self.redo_history.pop()
            return True
        return False

    def apply_gain(self, gain_factor: float) -> np.ndarray:
        """
        应用增益
        :param gain_factor: 增益因子
        :return: 处理后的波形
        """
        if self.current_waveform is None:
            raise ValueError("没有加载波形数据")

        self.save_state()

        result = self.current_waveform * gain_factor

        # 防止削波
        max_val = np.max(np.abs(result))
        if max_val > 1.0:
            result = result / max_val

        self.current_waveform = result
        return result

    def fade_in(self, duration: float = 0.1) -> np.ndarray:
        """
        淡入效果
        :param duration: 淡入时长（秒）
        :return: 处理后的波形
        """
        if self.current_waveform is None:
            raise ValueError("没有加载波形数据")

        self.save_state()

        fade_samples = int(duration * self.sample_rate)
        fade_samples = min(fade_samples, len(self.current_waveform))

        # 创建淡入曲线
        fade_curve = np.linspace(0, 1, fade_samples)

        # 应用淡入
        result = self.current_waveform.copy()
        result[:fade_samples] *= fade_curve

        self.current_waveform = result
        return result

    def fade_out(self, duration: float = 0.1) -> np.ndarray:
        """
        淡出效果
        :param duration: 淡出时长（秒）
        :return: 处理后的波形
        """
        if self.current_waveform is None:
            raise ValueError("没有加载波形数据")

        self.save_state()

        fade_samples = int(duration * self.sample_rate)
        fade_samples = min(fade_samples, len(self.current_waveform))

        # 创建淡出曲线
        fade_curve = np.linspace(1, 0, fade_samples)

        # 应用淡出
        result = self.current_waveform.copy()
        result[-fade_samples:] *= fade_curve

        self.current_waveform = result
        return result

    def apply_envelope(self, attack: float = 0.01, decay: float = 0.1,
                      sustain: float = 0.7, release: float = 0.2) -> np.ndarray:
        """
        应用ADSR包络
        :param attack: 起音时间
        :param decay: 衰减时间
        :param sustain: 延音水平
        :param release: 释音时间
        :return: 处理后的波形
        """
        if self.current_waveform is None:
            raise ValueError("没有加载波形数据")

        self.save_state()

        total_samples = len(self.current_waveform)

        # 计算各阶段样本数
        attack_samples = int(attack * self.sample_rate)
        decay_samples = int(decay * self.sample_rate)
        release_samples = int(release * self.sample_rate)

        # 限制样本数
        attack_samples = min(attack_samples, total_samples // 4)
        decay_samples = min(decay_samples, total_samples // 4)
        release_samples = min(release_samples, total_samples // 4)

        # 创建包络
        envelope = np.ones(total_samples)

        # Attack阶段
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

        # Decay阶段
        if decay_samples > 0:
            decay_end = attack_samples + decay_samples
            envelope[attack_samples:decay_end] = np.linspace(1, sustain, decay_samples)

        # Sustain阶段
        sustain_start = attack_samples + decay_samples
        sustain_end = total_samples - release_samples

        if sustain_end > sustain_start:
            envelope[sustain_start:sustain_end] = sustain

        # Release阶段
        if release_samples > 0:
            envelope[-release_samples:] = np.linspace(sustain, 0, release_samples)

        # 应用包络
        result = self.current_waveform * envelope

        self.current_waveform = result
        return result

    def reverse(self) -> np.ndarray:
        """
        反转波形
        :return: 反转后的波形
        """
        if self.current_waveform is None:
            raise ValueError("没有加载波形数据")

        self.save_state()

        result = np.flip(self.current_waveform)
        self.current_waveform = result
        return result

    def trim(self, start_time: float, end_time: float) -> np.ndarray:
        """
        裁剪波形
        :param start_time: 开始时间（秒）
        :param end_time: 结束时间（秒）
        :return: 裁剪后的波形
        """
        if self.current_waveform is None:
            raise ValueError("没有加载波形数据")

        self.save_state()

        start_sample = int(start_time * self.sample_rate)
        end_sample = int(end_time * self.sample_rate)

        # 确保范围有效
        start_sample = max(0, min(start_sample, len(self.current_waveform)))
        end_sample = max(0, min(end_sample, len(self.current_waveform)))

        if start_sample >= end_sample:
            raise ValueError("开始时间必须小于结束时间")

        result = self.current_waveform[start_sample:end_sample]
        self.current_waveform = result
        return result

    def normalize(self, target_level: float = 1.0) -> np.ndarray:
        """
        归一化波形
        :param target_level: 目标电平
        :return: 归一化后的波形
        """
        if self.current_waveform is None:
            raise ValueError("没有加载波形数据")

        self.save_state()

        current_max = np.max(np.abs(self.current_waveform))
        if current_max > 0:
            result = self.current_waveform * (target_level / current_max)
            self.current_waveform = result
        else:
            result = self.current_waveform

        return result

    def apply_filter(self, filter_type: str, cutoff_freq: float,
                    order: int = 4) -> np.ndarray:
        """
        应用滤波器
        :param filter_type: 滤波器类型 ('lowpass', 'highpass', 'bandpass', 'bandstop')
        :param cutoff_freq: 截止频率（Hz）
        :param order: 滤波器阶数
        :return: 滤波后的波形
        """
        if self.current_waveform is None:
            raise ValueError("没有加载波形数据")

        self.save_state()

        # 归一化截止频率
        nyquist = self.sample_rate / 2
        normalized_cutoff = cutoff_freq / nyquist

        # 设计滤波器
        if filter_type == 'lowpass':
            b, a = scipy_signal.butter(order, normalized_cutoff, btype='low')
        elif filter_type == 'highpass':
            b, a = scipy_signal.butter(order, normalized_cutoff, btype='high')
        elif filter_type == 'bandpass':
            # 带通滤波需要两个截止频率
            low_cutoff = normalized_cutoff * 0.8
            high_cutoff = normalized_cutoff * 1.2
            b, a = scipy_signal.butter(order, [low_cutoff, high_cutoff], btype='band')
        elif filter_type == 'bandstop':
            # 带阻滤波需要两个截止频率
            low_cutoff = normalized_cutoff * 0.8
            high_cutoff = normalized_cutoff * 1.2
            b, a = scipy_signal.butter(order, [low_cutoff, high_cutoff], btype='bandstop')
        else:
            raise ValueError(f"不支持的滤波器类型: {filter_type}")

        # 应用滤波器
        result = scipy_signal.filtfilt(b, a, self.current_waveform)
        self.current_waveform = result
        return result

    def add_noise(self, noise_level: float = 0.01, noise_type: str = 'white') -> np.ndarray:
        """
        添加噪音
        :param noise_level: 噪音水平
        :param noise_type: 噪音类型 ('white', 'pink', 'brown')
        :return: 添加噪音后的波形
        """
        if self.current_waveform is None:
            raise ValueError("没有加载波形数据")

        self.save_state()

        if noise_type == 'white':
            noise = np.random.randn(len(self.current_waveform))
        elif noise_type == 'pink':
            # 简化的粉红噪音生成
            white = np.random.randn(len(self.current_waveform))
            # 粉红噪音滤波器
            b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
            a = [1, -2.494956002, 2.017265875, -0.522189400]
            noise = scipy_signal.lfilter(b, a, white)
        elif noise_type == 'brown':
            # 简化的布朗噪音生成
            white = np.random.randn(len(self.current_waveform))
            # 布朗噪音滤波器
            b = [0.052347518, 0.044894278, 0.046250551, 0.041674495, 0.046564798, 0.041946730]
            a = [1, -1.717198605, 1.032429414, -0.228875582, 0.129220862, -0.021220562]
            noise = scipy_signal.lfilter(b, a, white)
        else:
            raise ValueError(f"不支持的噪音类型: {noise_type}")

        # 归一化噪音
        noise = noise / np.std(noise) * noise_level

        result = self.current_waveform + noise

        # 防止削波
        max_val = np.max(np.abs(result))
        if max_val > 1.0:
            result = result / max_val

        self.current_waveform = result
        return result

    def change_speed(self, speed_factor: float) -> np.ndarray:
        """
        改变播放速度
        :param speed_factor: 速度因子（1.0为原速，2.0为两倍速）
        :return: 变速后的波形
        """
        if self.current_waveform is None:
            raise ValueError("没有加载波形数据")

        self.save_state()

        # 计算新长度
        new_length = int(len(self.current_waveform) / speed_factor)

        # 使用重采样改变速度
        result = scipy_signal.resample(self.current_waveform, new_length)
        self.current_waveform = result
        return result

    def change_pitch(self, semitones: float) -> np.ndarray:
        """
        改变音高
        :param semitones: 音高变化（半音数，正数升高，负数降低）
        :return: 变调后的波形
        """
        if self.current_waveform is None:
            raise ValueError("没有加载波形数据")

        self.save_state()

        # 计算重采样因子
        pitch_factor = 2.0 ** (semitones / 12.0)

        # 计算新长度
        new_length = int(len(self.current_waveform) / pitch_factor)

        # 重采样改变音高
        result = scipy_signal.resample(self.current_waveform, new_length)

        self.current_waveform = result
        return result

    def get_waveform_info(self) -> dict:
        """获取波形信息"""
        if self.current_waveform is None:
            return {}

        return {
            "length": len(self.current_waveform),
            "duration": len(self.current_waveform) / self.sample_rate,
            "sample_rate": self.sample_rate,
            "max_amplitude": float(np.max(np.abs(self.current_waveform))),
            "rms_level": float(np.sqrt(np.mean(self.current_waveform ** 2))),
            "dc_offset": float(np.mean(self.current_waveform)),
            "dynamic_range": float(np.ptp(self.current_waveform)),
            "undo_steps": len(self.edit_history),
            "redo_steps": len(self.redo_history)
        }

    def export_processed(self, filename: str, format: str = 'wav') -> bool:
        """
        导出处理后的波形
        :param filename: 文件名
        :param format: 文件格式
        :return: 是否成功
        """
        if self.current_waveform is None:
            raise ValueError("没有波形数据可导出")

        try:
            if format.lower() == 'wav':
                from scipy.io import wavfile
                waveform_int16 = np.int16(self.current_waveform * 32767)
                wavfile.write(filename, self.sample_rate, waveform_int16)
            elif format.lower() == 'npy':
                np.save(filename, self.current_waveform)
            else:
                raise ValueError(f"不支持的格式: {format}")

            return True
        except Exception as e:
            print(f"导出失败: {e}")
            return False