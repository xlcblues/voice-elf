"""
错误处理模块
定义自定义异常和错误处理函数
"""

from typing import Optional

class WaveformError(Exception):
    """波形模拟器基础异常类"""

    def __init__(self, message: str, error_code: Optional[str] = None):
        """
        初始化异常

        Args:
            message: 错误消息
            error_code: 错误代码
        """
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ParseError(WaveformError):
    """表达式解析错误"""

    def __init__(self, message: str):
        super().__init__(message, "PARSE_ERROR")

class AudioError(WaveformError):
    """音频处理错误"""

    def __init__(self, message: str):
        super().__init__(message, "AUDIO_ERROR")

class ConfigError(WaveformError):
    """配置错误"""

    def __init__(self, message: str):
        super().__init__(message, "CONFIG_ERROR")

def handle_error(error: Exception) -> str:
    """
    统一错误处理函数

    Args:
        error: 异常对象

    Returns:
        用户友好的错误消息
    """
    if isinstance(error, WaveformError):
        return error.message

    error_messages = {
        SyntaxError: "表达式语法错误，请检查输入格式",
        ValueError: "数值计算错误，请检查函数参数",
        ZeroDivisionError: "除零错误，请检查分母",
        OverflowError: "数值溢出错误，请调整参数范围",
        MemoryError: "内存不足，请尝试减少采样点数或时长",
        ImportError: "缺少必要的库，请检查依赖包安装",
    }

    error_type = type(error)
    return error_messages.get(error_type, f"未知错误: {str(error)}")

def safe_execute(func):
    """
    安全执行装饰器，捕获并处理异常

    Args:
        func: 要装饰的函数

    Returns:
        装饰后的函数
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = handle_error(e)
            print(f"错误: {error_msg}")
            return None

    return wrapper