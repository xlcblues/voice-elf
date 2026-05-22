"""
真实感声音增强模块
提供各种效果使合成声音更加真实和接近现实
"""

import numpy as np
from scipy import signal
from scipy.fft import fft, ifft
import random

class RealisticSoundEnhancer:
    """真实感声音增强器"""

    @staticmethod
    def add_natural_variance(waveform, variance_level=0.05):
        """
        添加自然变化 - 模拟真实声音的微小不规则性
        :param waveform: 原始波形
        :param variance_level: 变化程度 (0.0-1.0)
        :return: 增强后的波形
        """
        enhanced = waveform.copy()

        # 添加微小的幅度变化，更自然的方式
        amplitude_variation = 1 + np.random.normal(0, variance_level * 0.05, len(waveform))
        enhanced = enhanced * amplitude_variation

        # 添加微小的相位变化
        phase_shift = np.random.normal(0, variance_level * 0.02, len(waveform))
        enhanced = enhanced * np.cos(phase_shift)

        # 添加非常微小的随机噪声
        noise = np.random.normal(0, variance_level * 0.01, len(waveform))
        enhanced = enhanced + noise

        # 归一化防止削波
        max_val = np.max(np.abs(enhanced))
        if max_val > 1.0:
            enhanced = enhanced / max_val

        return enhanced

    @staticmethod
    def add_harmonic_distortion(waveform, harmonics=[0.1, 0.05, 0.02]):
        """
        添加谐波失真 - 模拟真实乐器的泛音
        :param waveform: 原始波形
        :param harmonics: 谐波强度列表 [2次谐波, 3次谐波, 4次谐波...]
        :return: 增强后的波形
        """
        enhanced = waveform.copy()

        # 生成时间数组用于创建真实的谐波
        t = np.arange(len(waveform)) / 44100  # 假设44100Hz采样率

        for i, harmonic_strength in enumerate(harmonics):
            if harmonic_strength > 0:
                # 创建真正的谐波：频率倍乘
                harmonic_freq = (i + 2)  # 2次, 3次, 4次谐波...
                # 使用调制方式创建谐波效果
                harmonic_modulation = 1 + harmonic_strength * 0.3 * np.sin(2 * np.pi * harmonic_freq * 100 * t)
                enhanced = enhanced * harmonic_modulation

                # 添加轻微的失真效果
                distortion = harmonic_strength * 0.1 * np.sin(2 * np.pi * harmonic_freq * 50 * t)
                enhanced = enhanced + distortion

        # 归一化防止削波
        max_val = np.max(np.abs(enhanced))
        if max_val > 1.0:
            enhanced = enhanced / max_val

        return enhanced

    @staticmethod
    def add_room_acoustics(waveform, room_size=0.3, damping=0.5):
        """
        添加房间声学效果 - 模拟空间感
        :param waveform: 原始波形
        :param room_size: 房间大小 (0.0-1.0)
        :param damping: 阻尼系数 (0.0-1.0)
        :return: 增强后的波形
        """
        # 计算延迟时间（基于房间大小）
        delay_samples = int(room_size * 0.1 * 44100)  # 最多100ms延迟

        if delay_samples < 10:
            return waveform

        # 创建早期反射 - 降低强度
        early_reflection = np.zeros_like(waveform)
        early_reflection[delay_samples:] = waveform[:-delay_samples] * 0.05  # 从0.3降低到0.05

        # 创建混响尾音 - 降低强度和复杂度
        reverb_decay = np.exp(-np.arange(len(waveform)) * damping / (44100 * room_size))
        reverb_tail = np.convolve(waveform, reverb_decay[:len(waveform)//8], mode='same') * 0.03  # 从0.2降低到0.03，卷积核减半

        # 组合原始声音、早期反射和混响 - 主要保持原始声音
        enhanced = waveform * 0.85 + early_reflection + reverb_tail  # 保持85%原始声音

        # 归一化
        max_val = np.max(np.abs(enhanced))
        if max_val > 1.0:
            enhanced = enhanced / max_val

        return enhanced

    @staticmethod
    def add_spectral_coloration(waveform, brightness=1.0, warmth=0.0):
        """
        添加频谱着色 - 模拟不同乐器的音色特性
        :param waveform: 原始波形
        :param brightness: 亮度 (高频增强) (0.5-2.0)
        :param warmth: 温暖度 (低频增强) (0.0-1.0)
        :return: 增强后的波形
        """
        # FFT变换
        spectrum = fft(waveform)
        frequencies = np.fft.fftfreq(len(waveform), 1/44100)

        # 创建频谱滤波器
        spectral_filter = np.ones_like(spectrum, dtype=complex)

        # 高频增强（亮度）
        if brightness != 1.0:
            high_freq_mask = np.abs(frequencies) > 1000
            spectral_filter[high_freq_mask] *= brightness

        # 低频增强（温暖度）
        if warmth > 0:
            low_freq_mask = np.abs(frequencies) < 500
            bass_boost = 1 + warmth * 0.5 * (1 - np.abs(frequencies[low_freq_mask]) / 500)
            spectral_filter[low_freq_mask] *= bass_boost

        # 应用滤波器
        colored_spectrum = spectrum * spectral_filter

        # 逆FFT变换回时域
        enhanced = np.real(ifft(colored_spectrum))

        # 归一化
        max_val = np.max(np.abs(enhanced))
        if max_val > 1.0:
            enhanced = enhanced / max_val

        return enhanced

    @staticmethod
    def add_transient_response(waveform, attack_time=0.01, decay_time=0.1):
        """
        添加瞬态响应 - 模拟真实乐器的起音和衰减特性
        :param waveform: 原始波形
        :param attack_time: 起音时间（秒）
        :param decay_time: 衰减时间（秒）
        :return: 增强后的波形
        """
        sample_rate = 44100
        attack_samples = int(attack_time * sample_rate)
        decay_samples = int(decay_time * sample_rate)

        # 创建起音包络
        attack_envelope = np.linspace(0, 1, attack_samples)

        # 创建衰减包络
        decay_envelope = np.exp(-np.arange(decay_samples) / (decay_samples * 0.3))

        # 组合包络
        total_samples = len(waveform)
        envelope = np.ones(total_samples)

        if attack_samples + decay_samples < total_samples:
            # 有稳态阶段
            envelope[:attack_samples] = attack_envelope
            envelope[attack_samples:attack_samples + decay_samples] = decay_envelope
        else:
            # 没有稳态阶段，只有起音和衰减
            envelope_portion = attack_samples + decay_samples
            if envelope_portion > total_samples:
                envelope_portion = total_samples

            combined_envelope = np.concatenate([attack_envelope, decay_envelope])
            envelope[:envelope_portion] = combined_envelope[:envelope_portion]

        return waveform * envelope

    @staticmethod
    def add_vibrato(waveform, rate=5.0, depth=0.02):
        """
        添加颤音效果 - 模拟真实乐器的音高波动
        :param waveform: 原始波形
        :param rate: 颤音频率（Hz）
        :param depth: 颤音深度 (0.0-1.0)
        :return: 增强后的波形
        """
        sample_rate = 44100
        t = np.arange(len(waveform)) / sample_rate

        # 创建颤音调制信号
        vibrato = 1 + depth * np.sin(2 * np.pi * rate * t)

        return waveform * vibrato

    @staticmethod
    def add_analog_imperfection(waveform, wow_flutter=0.0, noise_floor=0.001):
        """
        添加模拟设备的不完美特性 - 增加真实感和温暖感
        :param waveform: 原始波形
        :param wow_flutter: 抖动程度 (0.0-1.0)
        :param noise_floor: 噪声底电平 (0.0-1.0)
        :return: 增强后的波形
        """
        enhanced = waveform.copy()

        # 添加Wow & Flutter（磁带录音机的速度波动）
        if wow_flutter > 0:
            sample_rate = 44100
            t = np.arange(len(waveform)) / sample_rate

            # 低频波动 (Wow)
            wow_modulation = 1 + wow_flutter * 0.02 * np.sin(2 * np.pi * 0.5 * t)

            # 高频波动 (Flutter)
            flutter_modulation = 1 + wow_flutter * 0.01 * np.sin(2 * np.pi * 6.0 * t)

            # 应用时间拉伸压缩效果
            enhanced = enhanced * wow_modulation * flutter_modulation

        # 添加模拟设备噪声
        if noise_floor > 0:
            analog_noise = np.random.normal(0, noise_floor, len(waveform))
            enhanced += analog_noise

        # 归一化
        max_val = np.max(np.abs(enhanced))
        if max_val > 1.0:
            enhanced = enhanced / max_val

        return enhanced

    @staticmethod
    def add_stereo_width(waveform, width=0.5):
        """
        添加立体声宽度 - 创建空间感
        :param waveform: 单声道波形
        :param width: 宽度 (0.0=单声道, 1.0=宽立体声)
        :return: 立体声波形 (2通道)
        """
        if waveform.ndim == 1:
            # 转换为立体声
            stereo = np.zeros((2, len(waveform)))
            stereo[0] = waveform  # 左声道
            stereo[1] = waveform  # 右声道

            if width > 0:
                # 创建立体声差异
                time_shift = int(width * 100)  # 最多100样本延迟
                frequency_response = np.random.random(len(waveform)) * width * 0.1

                # 右声道添加微小差异
                if time_shift > 0 and time_shift < len(waveform):
                    stereo[1, time_shift:] = stereo[1, :-time_shift] * (1 + frequency_response[: -time_shift])
                else:
                    stereo[1] *= (1 + frequency_response)

                # 中间-侧边处理
                mid = (stereo[0] + stereo[1]) / 2
                side = (stereo[0] - stereo[1]) / 2 * width

                stereo[0] = mid + side
                stereo[1] = mid - side

            return stereo
        else:
            return waveform

    @staticmethod
    def apply_preset(waveform, preset_type="natural"):
        """
        应用预设效果 - 每个预设都有独特的声音特色
        :param waveform: 原始波形
        :param preset_type: 预设类型
        :return: 增强后的波形
        """
        enhancer = RealisticSoundEnhancer()
        enhanced = waveform.copy()

        if preset_type == "natural":
            # 自然声音 - 适度增强，保持真实感
            enhanced = enhancer.add_natural_variance(enhanced, variance_level=0.20)
            enhanced = enhancer.add_harmonic_distortion(enhanced, harmonics=[0.15, 0.08, 0.04])
            enhanced = enhancer.add_room_acoustics(enhanced, room_size=0.3, damping=0.6)
            enhanced = enhancer.add_stereo_width(enhanced, width=0.4)

        elif preset_type == "warm":
            # 温暖声音 - 强烈低频和模拟特性
            enhanced = enhancer.add_spectral_coloration(enhanced, brightness=0.6, warmth=1.0)  # 显著温暖度
            enhanced = enhancer.add_analog_imperfection(enhanced, wow_flutter=0.5, noise_floor=0.015)
            enhanced = enhancer.add_harmonic_distortion(enhanced, harmonics=[0.3, 0.2, 0.12])  # 丰富谐波
            enhanced = enhancer.add_room_acoustics(enhanced, room_size=0.4, damping=0.4)  # 更多混响

        elif preset_type == "bright":
            # 明亮声音 - 强烈高频，现代感
            enhanced = enhancer.add_spectral_coloration(enhanced, brightness=2.5, warmth=0.1)  # 非常明亮
            enhanced = enhancer.add_natural_variance(enhanced, variance_level=0.08)  # 较少变化
            enhanced = enhancer.add_vibrato(enhanced, rate=6.0, depth=0.03)  # 快速轻微颤音
            enhanced = enhancer.add_harmonic_distortion(enhanced, harmonics=[0.1, 0.05, 0.02])  # 轻微谐波

        elif preset_type == "vintage":
            # 复古声音 - 强烈设备特性和失真
            enhanced = enhancer.add_analog_imperfection(enhanced, wow_flutter=0.7, noise_floor=0.03)  # 明显模拟特性
            enhanced = enhancer.add_spectral_coloration(enhanced, brightness=0.5, warmth=1.2)  # 很暗很温暖
            enhanced = enhancer.add_room_acoustics(enhanced, room_size=0.6, damping=0.2)  # 长混响
            enhanced = enhancer.add_harmonic_distortion(enhanced, harmonics=[0.4, 0.3, 0.2])  # 强烈失真

        elif preset_type == "acoustic":
            # 声学乐器 - 明显瞬态和自然感
            enhanced = enhancer.add_transient_response(enhanced, attack_time=0.005, decay_time=0.6)  # 明显瞬态
            enhanced = enhancer.add_room_acoustics(enhanced, room_size=0.7, damping=0.3)  # 大房间感
            enhanced = enhancer.add_natural_variance(enhanced, variance_level=0.25)  # 较强自然变化
            enhanced = enhancer.add_harmonic_distortion(enhanced, harmonics=[0.12, 0.06, 0.03])  # 轻微谐波

        elif preset_type == "electronic":
            # 电子音乐 - 强烈调制和频谱特性
            enhanced = enhancer.add_spectral_coloration(enhanced, brightness=2.2, warmth=0.3)
            enhanced = enhancer.add_vibrato(enhanced, rate=8.0, depth=0.12)  # 强烈颤音
            enhanced = enhancer.add_natural_variance(enhanced, variance_level=0.18)  # 数字感变化
            enhanced = enhancer.add_harmonic_distortion(enhanced, harmonics=[0.35, 0.25, 0.15])  # 现代失真

        return enhanced

# 创建全局实例
_enhancer_instance = None

def get_enhancer() -> RealisticSoundEnhancer:
    """获取全局增强器实例"""
    global _enhancer_instance
    if _enhancer_instance is None:
        _enhancer_instance = RealisticSoundEnhancer()
    return _enhancer_instance