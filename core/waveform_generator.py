"""
波形生成引擎模块
负责根据用户输入的函数表达式生成波形数据
"""

import numpy as np
from typing import Tuple, Optional, Callable
from core.function_parser import get_parser
from utils.error_handler import WaveformError

class WaveformGenerator:
    """波形生成器类"""

    def __init__(self):
        """初始化波形生成器"""
        self.parser = get_parser()
        self.current_waveform = None
        self.current_params = {}

    def generate_waveform(
        self,
        expression: str,
        duration: float = 5.0,
        sample_rate: int = 44100,
        amplitude: float = 1.0
    ) -> Tuple[np.ndarray, int]:
        """
        生成波形数据
        :param expression: 波形表达式
        :param duration: 持续时间(秒)
        :param sample_rate: 采样率
        :param amplitude: 振幅因子
        :return: (波形数据, 采样率)
        """
        try:
            # 验证参数
            self._validate_parameters(duration, sample_rate, amplitude)

            # 解析表达式
            waveform_function = self.parser.parse_expression(expression)

            # 生成时间数组
            t = self._generate_time_array(duration, sample_rate)

            # 计算波形
            waveform = waveform_function(t)

            # 应用振幅因子
            waveform = waveform * amplitude

            # 后处理波形
            waveform = self._postprocess_waveform(waveform)

            # 保存当前波形信息
            self.current_waveform = waveform
            self.current_params = {
                'expression': expression,
                'duration': duration,
                'sample_rate': sample_rate,
                'amplitude': amplitude,
                'points': len(waveform)
            }

            return waveform, sample_rate

        except Exception as e:
            raise WaveformError(f"波形生成失败: {str(e)}")

    def _validate_parameters(self, duration: float, sample_rate: int, amplitude: float):
        """验证生成参数"""
        if duration <= 0:
            raise WaveformError("持续时间必须大于0")
        if duration > 60:  # 最大60秒
            raise WaveformError("持续时间不能超过60秒")
        if sample_rate < 8000 or sample_rate > 48000:
            raise WaveformError("采样率必须在8000-48000之间")
        if amplitude < 0 or amplitude > 2:
            raise WaveformError("振幅因子必须在0-2之间")

    def _generate_time_array(self, duration: float, sample_rate: int) -> np.ndarray:
        """生成时间数组"""
        num_points = int(duration * sample_rate)
        return np.linspace(0, duration, num_points, endpoint=False)

    def _postprocess_waveform(self, waveform: np.ndarray) -> np.ndarray:
        """后处理波形数据"""
        # 限制振幅范围防止削波
        max_amplitude = np.max(np.abs(waveform))

        if max_amplitude > 1.0:
            # 如果振幅过大，进行归一化
            waveform = waveform / max_amplitude
            print(f"警告: 波形振幅过大，已归一化到[-1, 1]范围")

        # 确保数据类型正确
        waveform = np.asarray(waveform, dtype=np.float64)

        return waveform

    def get_waveform_info(self) -> dict:
        """获取当前波形信息"""
        if self.current_waveform is None:
            return {}

        waveform = self.current_waveform
        params = self.current_params

        return {
            **params,
            'actual_amplitude': float(np.max(np.abs(waveform))),
            'rms_level': float(np.sqrt(np.mean(waveform ** 2))),
            'peak_to_peak': float(np.ptp(waveform)),
            'dc_offset': float(np.mean(waveform)),
            'duration_sec': len(waveform) / params.get('sample_rate', 44100)
        }

    def analyze_frequency_content(self) -> dict:
        """分析频率内容"""
        if self.current_waveform is None:
            return {}

        try:
            from scipy.fft import fft, fftfreq

            waveform = self.current_waveform
            sample_rate = self.current_params.get('sample_rate', 44100)

            # 计算FFT
            n = len(waveform)
            yf = fft(waveform)
            xf = fftfreq(n, 1/sample_rate)[:n//2]

            # 计算幅度谱
            magnitude = 2.0/n * np.abs(yf[0:n//2])

            # 找到主频率
            dominant_freq_idx = np.argmax(magnitude[1:]) + 1  # 跳过DC分量
            dominant_frequency = xf[dominant_freq_idx]
            dominant_magnitude = magnitude[dominant_freq_idx]

            return {
                'frequencies': xf,
                'magnitudes': magnitude,
                'dominant_frequency': float(dominant_frequency),
                'dominant_magnitude': float(dominant_magnitude),
                'max_frequency': float(xf[-1]),
                'frequency_resolution': float(xf[1] - xf[0])
            }

        except Exception as e:
            return {'error': str(e)}

    def generate_waveform_batch(
        self,
        expressions: list,
        duration: float = 5.0,
        sample_rate: int = 44100,
        amplitude: float = 1.0
    ) -> list:
        """批量生成波形"""
        results = []

        for expr in expressions:
            try:
                waveform, sr = self.generate_waveform(expr, duration, sample_rate, amplitude)
                results.append({
                    'expression': expr,
                    'waveform': waveform,
                    'sample_rate': sr,
                    'success': True
                })
            except Exception as e:
                results.append({
                    'expression': expr,
                    'error': str(e),
                    'success': False
                })

        return results

    def mix_waveforms(
        self,
        waveforms: list,
        weights: Optional[list] = None
    ) -> np.ndarray:
        """混合多个波形"""
        if not waveforms:
            raise WaveformError("波形列表不能为空")

        if weights is None:
            weights = [1.0] * len(waveforms)

        if len(weights) != len(waveforms):
            raise WaveformError("权重数量必须与波形数量相同")

        # 确保所有波形长度相同
        min_length = min(len(w) for w in waveforms)
        mixed = np.zeros(min_length)

        for waveform, weight in zip(waveforms, weights):
            mixed += waveform[:min_length] * weight

        # 归一化防止削波
        max_amplitude = np.max(np.abs(mixed))
        if max_amplitude > 1.0:
            mixed = mixed / max_amplitude

        return mixed

    def apply_envelope(
        self,
        waveform: np.ndarray,
        attack_time: float = 0.01,
        decay_time: float = 0.1,
        sustain_level: float = 0.7,
        release_time: float = 0.2,
        sample_rate: int = 44100
    ) -> np.ndarray:
        """应用ADSR包络"""
        total_samples = len(waveform)

        # 计算各阶段样本数
        attack_samples = int(attack_time * sample_rate)
        decay_samples = int(decay_time * sample_rate)
        release_samples = int(release_time * sample_rate)

        # 确保不超过总样本数
        attack_samples = min(attack_samples, total_samples // 4)
        decay_samples = min(decay_samples, total_samples // 4)
        release_samples = min(release_samples, total_samples // 4)

        # 创建包络
        envelope = np.ones(total_samples)

        # Attack阶段 (0 -> 1)
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

        # Decay阶段 (1 -> sustain_level)
        if decay_samples > 0:
            decay_end = attack_samples + decay_samples
            envelope[attack_samples:decay_end] = np.linspace(1, sustain_level, decay_samples)

        # Sustain阶段 (sustain_level)
        sustain_start = attack_samples + decay_samples
        sustain_end = total_samples - release_samples

        if sustain_end > sustain_start:
            envelope[sustain_start:sustain_end] = sustain_level

        # Release阶段 (sustain_level -> 0)
        if release_samples > 0:
            envelope[-release_samples:] = np.linspace(sustain_level, 0, release_samples)

        return waveform * envelope

    def export_waveform(self, filename: str, format: str = 'wav') -> bool:
        """导出波形到文件"""
        if self.current_waveform is None:
            raise WaveformError("没有可导出的波形")

        try:
            from scipy.io import wavfile

            if format.lower() == 'wav':
                # 转换为16位整数
                waveform_int16 = np.int16(
                    self.current_waveform * 32767
                )
                sample_rate = self.current_params.get('sample_rate', 44100)

                wavfile.write(filename, sample_rate, waveform_int16)
                return True
            else:
                raise WaveformError(f"不支持的格式: {format}")

        except Exception as e:
            raise WaveformError(f"导出失败: {str(e)}")

# 创建全局波形生成器实例
_generator_instance = None

def get_generator() -> WaveformGenerator:
    """获取全局波形生成器实例"""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = WaveformGenerator()
    return _generator_instance