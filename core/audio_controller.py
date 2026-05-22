"""
音频控制器模块
负责音频播放、暂停、停止和音量控制
"""

import numpy as np
import sounddevice as sd
from typing import Optional, Callable
from enum import Enum
from utils.error_handler import AudioError
import threading
import time

class PlaybackState(Enum):
    """播放状态枚举"""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"

class AudioController:
    """音频控制器类"""

    def __init__(self):
        """初始化音频控制器"""
        self.waveform = None
        self.sample_rate = 44100
        self.state = PlaybackState.STOPPED
        self.volume = 0.8
        self.stream = None
        self.playback_thread = None
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        self.current_position = 0
        self.playback_callback = None
        self.position_callback = None

    def load_waveform(self, waveform: np.ndarray, sample_rate: int = 44100):
        """
        加载波形数据
        :param waveform: 波形数据
        :param sample_rate: 采样率
        """
        if waveform is None or len(waveform) == 0:
            raise AudioError("波形数据不能为空")

        # 如果正在播放，先停止
        if self.state != PlaybackState.STOPPED:
            self.stop()

        self.waveform = np.asarray(waveform, dtype=np.float64)
        self.sample_rate = sample_rate
        self.current_position = 0

        # 归一化波形
        if np.max(np.abs(self.waveform)) > 0:
            self.waveform = self.waveform / np.max(np.abs(self.waveform))

    def play(self):
        """开始播放"""
        if self.waveform is None:
            raise AudioError("没有加载波形数据")

        if self.state == PlaybackState.PLAYING:
            return  # 已经在播放

        if self.state == PlaybackState.PAUSED:
            # 从暂停位置恢复播放
            self.state = PlaybackState.PLAYING
            self.pause_event.clear()
            return

        # 开始新的播放 - 非阻塞方式
        self.state = PlaybackState.PLAYING
        self.stop_event.clear()
        self.pause_event.clear()
        self.current_position = 0

        # 应用音量
        audio_data = self.waveform * self.volume

        # 直接播放整个音频（非阻塞）
        try:
            sd.play(audio_data, self.sample_rate)

            # 启动监控线程来跟踪播放状态
            self.playback_thread = threading.Thread(target=self._playback_monitor, daemon=True)
            self.playback_thread.start()

        except Exception as e:
            self.state = PlaybackState.STOPPED
            raise AudioError(f"播放失败: {str(e)}")

    def _playback_monitor(self):
        """监控播放状态"""
        try:
            # 计算预期的播放时长
            duration = len(self.waveform) / self.sample_rate
            start_time = time.time()

            while self.state == PlaybackState.PLAYING:
                # 计算已播放时间
                elapsed = time.time() - start_time

                # 检查音频是否还在播放
                try:
                    is_playing = sd.get_stream().active
                except:
                    is_playing = False

                # 如果播放时间已过或者音频停止了
                if (elapsed >= duration + 0.1) or (not is_playing and elapsed > 0.1):
                    # 播放自然结束
                    self.state = PlaybackState.STOPPED
                    self.current_position = 0

                    # 调用播放完成回调
                    if self.playback_callback:
                        self.playback_callback(True)
                    break

                # 检查是否被停止
                if self.stop_event.is_set():
                    break

                # 检查暂停
                if self.pause_event.is_set():
                    self.state = PlaybackState.PAUSED
                    break

                # 更新进度（模拟进度，因为sd.play没有精确的进度信息）
                self.current_position += int(self.sample_rate * 0.05)
                if self.current_position > len(self.waveform):
                    self.current_position = len(self.waveform)

                # 调用位置回调
                if self.position_callback:
                    self.position_callback(self.current_position, len(self.waveform))

                # 短暂休眠避免CPU占用过高
                time.sleep(0.05)  # 50ms检查一次

        except Exception as e:
            print(f"播放监控错误: {e}")
            self.state = PlaybackState.STOPPED
            if self.playback_callback:
                self.playback_callback(False, str(e))

    def pause(self):
        """暂停播放"""
        if self.state == PlaybackState.PLAYING:
            self.state = PlaybackState.PAUSED
            self.pause_event.set()

    def stop(self):
        """停止播放"""
        if self.state != PlaybackState.STOPPED:
            self.state = PlaybackState.STOPPED
            self.stop_event.set()
            self.pause_event.clear()
            self.current_position = 0

            # 立即停止音频播放
            try:
                sd.stop()
            except:
                pass

            # 等待播放线程结束
            if self.playback_thread and self.playback_thread.is_alive():
                self.playback_thread.join(timeout=1.0)

    def set_volume(self, volume: float):
        """
        设置音量
        :param volume: 音量 (0.0 - 1.0)
        """
        if volume < 0 or volume > 1:
            raise AudioError("音量必须在0.0-1.0之间")
        self.volume = volume

    def get_volume(self) -> float:
        """获取当前音量"""
        return self.volume

    def get_state(self) -> PlaybackState:
        """获取播放状态"""
        return self.state

    def get_position(self) -> int:
        """获取当前播放位置"""
        return self.current_position

    def get_duration(self) -> float:
        """获取音频时长(秒)"""
        if self.waveform is None:
            return 0.0
        return len(self.waveform) / self.sample_rate

    def get_progress(self) -> float:
        """获取播放进度 (0.0 - 1.0)"""
        if self.waveform is None or len(self.waveform) == 0:
            return 0.0
        return self.current_position / len(self.waveform)

    def set_callbacks(self, playback_callback: Optional[Callable] = None,
                     position_callback: Optional[Callable] = None):
        """设置回调函数"""
        self.playback_callback = playback_callback
        self.position_callback = position_callback

    def play_test_tone(self, frequency: float = 440, duration: float = 1.0):
        """
        播放测试音
        :param frequency: 频率 (Hz)
        :param duration: 时长 (秒)
        """
        try:
            # 生成测试音
            t = np.linspace(0, duration, int(self.sample_rate * duration), False)
            test_tone = 0.5 * np.sin(2 * np.pi * frequency * t)

            self.load_waveform(test_tone, self.sample_rate)
            self.play()

            # 等待播放完成
            while self.state == PlaybackState.PLAYING:
                time.sleep(0.1)

        except Exception as e:
            raise AudioError(f"测试音播放失败: {str(e)}")

    def get_audio_devices(self) -> dict:
        """获取可用音频设备"""
        try:
            devices = sd.query_devices()
            return {
                'input_devices': [dev for dev in devices if dev['max_input_channels'] > 0],
                'output_devices': [dev for dev in devices if dev['max_output_channels'] > 0],
                'default_output_device': sd.query_devices(kind='output')
            }
        except Exception as e:
            return {'error': str(e)}

    def set_output_device(self, device_id: int):
        """设置输出设备"""
        try:
            sd.default.device = device_id
        except Exception as e:
            raise AudioError(f"设置输出设备失败: {str(e)}")

    def __del__(self):
        """析构函数"""
        self.stop()

# 创建全局音频控制器实例
_controller_instance = None

def get_audio_controller() -> AudioController:
    """获取全局音频控制器实例"""
    global _controller_instance
    if _controller_instance is None:
        _controller_instance = AudioController()
    return _controller_instance