"""
音频录制器
支持实时音频录制和采集
"""

import numpy as np
import sounddevice as sd
from threading import Thread, Event
from typing import Callable, Optional
import time
from datetime import datetime

class AudioRecorder:
    """音频录制器"""

    def __init__(self):
        """初始化音频录制器"""
        self.recording = False
        self.paused = False
        self.recorded_data = None
        self.sample_rate = 44100
        self.channels = 1
        self.recording_thread = None
        self.stop_event = Event()
        self.pause_event = Event()
        self.progress_callback = None

        # 录制参数
        self.device = None
        self.dtype = np.float64

    def set_progress_callback(self, callback: Callable[[float, int], None]):
        """
        设置进度回调函数
        :param callback: 回调函数 (duration, sample_count)
        """
        self.progress_callback = callback

    def get_input_devices(self) -> list:
        """获取输入设备列表"""
        devices = sd.query_devices()
        input_devices = []

        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                input_devices.append({
                    'id': i,
                    'name': device['name'],
                    'channels': device['max_input_channels'],
                    'sample_rates': device['default_samplerate']
                })

        return input_devices

    def set_input_device(self, device_id: int):
        """设置输入设备"""
        self.device = device_id

    def start_recording(self, duration: float = None, sample_rate: int = 44100,
                       channels: int = 1):
        """
        开始录制
        :param duration: 录制时长（秒），None表示手动停止
        :param sample_rate: 采样率
        :param channels: 声道数
        """
        if self.recording:
            raise RuntimeError("正在录制中")

        self.sample_rate = sample_rate
        self.channels = channels
        self.recording = True
        self.paused = False
        self.stop_event.clear()
        self.pause_event.clear()

        # 清除之前的录制数据
        self.recorded_data = []

        # 启动录制线程
        self.recording_thread = Thread(
            target=self._recording_worker,
            args=(duration,),
            daemon=True
        )
        self.recording_thread.start()

    def _recording_worker(self, duration: Optional[float]):
        """录制工作线程"""
        try:
            def audio_callback(indata, frames, time, status):
                """音频回调函数"""
                if status:
                    print(f"录制状态: {status}")

                if not self.recording or self.stop_event.is_set():
                    raise sd.CallbackStop

                if not self.paused:
                    # 如果是多声道，只取第一声道
                    if self.channels > 1 and indata.shape[1] > 1:
                        data = indata[:, 0]
                    else:
                        data = indata.flatten()

                    self.recorded_data.append(data.copy())

                    # 更新进度
                    if self.progress_callback:
                        current_duration = len(self.recorded_data) * len(data) / self.sample_rate
                        sample_count = sum(len(d) for d in self.recorded_data)
                        self.progress_callback(current_duration, sample_count)

            # 开始录制
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype,
                device=self.device,
                callback=audio_callback
            ):
                if duration is None:
                    # 手动停止模式
                    while not self.stop_event.is_set():
                        time.sleep(0.1)
                else:
                    # 定时录制
                    time.sleep(duration)
                    self.stop_event.set()

        except Exception as e:
            print(f"录制错误: {e}")
            self.recording = False

    def stop_recording(self) -> np.ndarray:
        """
        停止录制
        :return: 录制的音频数据
        """
        if not self.recording:
            raise RuntimeError("没有正在进行的录制")

        # 停止录制
        self.stop_event.set()
        self.recording = False

        # 等待录制线程结束
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=2.0)

        # 合并录制的数据
        if self.recorded_data:
            self.recorded_data = np.concatenate(self.recorded_data)
        else:
            self.recorded_data = np.array([])

        return self.recorded_data

    def pause_recording(self):
        """暂停录制"""
        if not self.recording:
            raise RuntimeError("没有正在进行的录制")

        self.paused = True
        self.pause_event.set()

    def resume_recording(self):
        """恢复录制"""
        if not self.recording:
            raise RuntimeError("没有正在进行的录制")

        self.paused = False
        self.pause_event.clear()

    def get_recorded_data(self) -> np.ndarray:
        """获取录制的数据"""
        if self.recorded_data is None:
            return np.array([])

        if isinstance(self.recorded_data, list):
            return np.concatenate(self.recorded_data) if self.recorded_data else np.array([])

        return self.recorded_data

    def get_recording_info(self) -> dict:
        """获取录制信息"""
        data = self.get_recorded_data()

        return {
            "duration": len(data) / self.sample_rate if len(data) > 0 else 0,
            "sample_count": len(data),
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "is_recording": self.recording,
            "is_paused": self.paused,
            "file_size_bytes": data.nbytes if len(data) > 0 else 0
        }

    def save_recording(self, filename: str, format: str = 'wav') -> bool:
        """
        保存录制
        :param filename: 文件名
        :param format: 文件格式
        :return: 是否成功
        """
        data = self.get_recorded_data()

        if len(data) == 0:
            raise ValueError("没有录制数据可保存")

        try:
            if format.lower() == 'wav':
                from scipy.io import wavfile

                # 归一化并转换为16位整数
                max_val = np.max(np.abs(data))
                if max_val > 0:
                    data_normalized = data / max_val
                else:
                    data_normalized = data

                data_int16 = np.int16(data_normalized * 32767)
                wavfile.write(filename, self.sample_rate, data_int16)

            elif format.lower() == 'npy':
                np.save(filename, data)

            else:
                raise ValueError(f"不支持的格式: {format}")

            return True

        except Exception as e:
            print(f"保存录制失败: {e}")
            return False

    def clear_recording(self):
        """清除录制数据"""
        self.recorded_data = None
        self.recording = False
        self.paused = False
        self.stop_event.clear()
        self.pause_event.clear()

    def analyze_recording(self) -> dict:
        """分析录制数据"""
        data = self.get_recorded_data()

        if len(data) == 0:
            return {}

        # 基础分析
        analysis = {
            "duration": len(data) / self.sample_rate,
            "max_amplitude": float(np.max(np.abs(data))),
            "rms_level": float(np.sqrt(np.mean(data ** 2))),
            "dc_offset": float(np.mean(data)),
            "dynamic_range": float(np.ptp(data)),
            "snr_estimate": self._estimate_snr(data)
        }

        # 频率分析
        from scipy.fft import fft, fftfreq
        n = len(data)
        if n > 0:
            yf = fft(data)
            xf = fftfreq(n, 1/self.sample_rate)[:n//2]
            magnitude = 2.0/n * np.abs(yf[0:n//2])

            # 找到主频率
            if len(magnitude) > 1:
                dominant_freq_idx = np.argmax(magnitude[1:]) + 1
                analysis["dominant_frequency"] = float(xf[dominant_freq_idx])
                analysis["dominant_magnitude"] = float(magnitude[dominant_freq_idx])

        return analysis

    def _estimate_snr(self, data: np.ndarray) -> float:
        """估算信噪比"""
        # 简化的SNR估算
        signal_power = np.mean(data ** 2)
        noise_floor = np.percentile(np.abs(data), 10)  # 使用10%分位数作为噪声底
        noise_power = noise_floor ** 2

        if noise_power > 0:
            snr_db = 10 * np.log10(signal_power / noise_power)
            return float(snr_db)
        else:
            return float('inf')