"""
函数解析器模块
负责解析用户输入的数学表达式并生成可执行的波形函数
"""

import numpy as np
from scipy import signal
import re
from typing import Callable, Dict, Any
from utils.error_handler import ParseError

class FunctionParser:
    """函数解析器类"""

    def __init__(self):
        """初始化函数解析器"""
        self._init_math_namespace()

    def _init_math_namespace(self):
        """初始化数学函数命名空间"""
        self.math_namespace = {
            # 基础数学常数
            'PI': np.pi,
            'pi': np.pi,
            'E': np.e,
            'e': np.e,

            # 基础数学函数
            'sin': np.sin,
            'cos': np.cos,
            'tan': np.tan,
            'asin': np.arcsin,
            'acos': np.arccos,
            'atan': np.arctan,
            'sinh': np.sinh,
            'cosh': np.cosh,
            'tanh': np.tanh,

            # 指数和对数函数
            'exp': np.exp,
            'log': np.log,
            'log10': np.log10,
            'log2': np.log2,
            'sqrt': np.sqrt,
            'power': np.power,
            'abs': np.abs,

            # 随机数函数
            'random': lambda size=None: np.random.random(size=size) if size is not None else np.random.random(),  # 修复：支持size参数
            'rand': np.random.rand,
            'randn': np.random.randn,
            'uniform': np.random.uniform,

            # 信号处理函数
            'square': signal.square,
            'sawtooth': signal.sawtooth,
            'pulse': self._pulse_function,
            'signal': signal,  # 添加整个signal模块

            # 取整函数
            'floor': np.floor,
            'ceil': np.ceil,
            'round': np.round,

            # 其他有用函数
            'clip': np.clip,
            'sign': np.sign,
            'maximum': np.maximum,
            'minimum': np.minimum,
            'len': len,  # 添加 len 函数
            'min': np.minimum,
            'max': np.maximum
        }

    def _pulse_function(self, t, duty=0.5):
        """
        脉冲波函数
        :param t: 时间数组
        :param duty: 占空比
        :return: 脉冲波
        """
        # 使用模运算创建周期性脉冲
        period = 1.0  # 基础周期
        phase = np.mod(t, period)
        return np.where(phase < duty * period, 1.0, 0.0)

    def validate_expression(self, expression: str) -> bool:
        """
        验证表达式是否安全有效
        :param expression: 数学表达式
        :return: 是否有效
        """
        if not expression or not expression.strip():
            raise ParseError("表达式不能为空")

        # 检查是否有危险函数调用
        dangerous_patterns = [
            r'__import__',
            r'eval\s*\(',
            r'exec\s*\(',
            r'compile\s*\(',
            r'open\s*\(',
            r'file\s*\(',
            r'__builtins__'
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, expression, re.IGNORECASE):
                raise ParseError(f"表达式包含不允许的函数: {pattern}")

        # 检查是否包含时间变量 t
        if 't' not in expression:
            raise ParseError("表达式必须包含时间变量 't'")

        return True

    def preprocess_expression(self, expression: str) -> str:
        """
        预处理表达式，处理常见的数学符号
        :param expression: 原始表达式
        :return: 处理后的表达式
        """
        import re

        # 移除多余空格
        expression = expression.strip()

        # 替换常见的数学符号
        replacements = {
            'π': 'pi',
            '×': '*',
            '÷': '/',
            '^': '**',
            'ln': 'log',
            'lg': 'log10'
        }

        for old, new in replacements.items():
            expression = expression.replace(old, new)

        # 自动插入乘号：处理数字后直接跟变量或函数的情况
        # 例如：400t -> 400*t, 2sin -> 2*sin
        # 匹配模式：数字后面直接跟变量名或函数名
        # 但是要注意不要处理类似 1e-5 这样的科学计数法

        # 首先保护科学计数法，暂时替换
        sci_notation_pattern = r'(\d+\.?\d*)[eE]([+-]?\d+\.?\d*)'
        sci_placeholders = []
        def replace_sci(match):
            placeholder = f"__SCI_{len(sci_placeholders)}__"
            sci_placeholders.append(match.group(0))
            return placeholder

        expression = re.sub(sci_notation_pattern, replace_sci, expression)

        # 在数字和变量/函数之间插入乘号
        # 匹配：数字后跟 ( 或者 字母开头的内容
        expression = re.sub(r'(\d)([a-zA-Z(])', r'\1*\2', expression)

        # 在右括号和左括号/数字之间插入乘号
        # 例如：2(x) -> 2*(x), (x)(y) -> (x)*(y)
        expression = re.sub(r'(\))([a-zA-Z(0-9])', r'\1*\2', expression)

        # 恢复科学计数法
        for i, sci_expr in enumerate(sci_placeholders):
            expression = expression.replace(f"__SCI_{i}__", sci_expr)

        return expression

    def parse_expression(self, expression: str) -> Callable[[np.ndarray], np.ndarray]:
        """
        解析表达式并返回可调用函数
        :param expression: 数学表达式字符串
        :return: 接受时间数组并返回波形值的函数
        """
        try:
            # 预处理表达式
            processed_expr = self.preprocess_expression(expression)

            # 验证表达式
            self.validate_expression(processed_expr)

            # 编译表达式
            def waveform_function(t: np.ndarray) -> np.ndarray:
                """波形函数"""
                try:
                    import sys
                    # 创建安全的局部命名空间
                    local_namespace = {
                        't': t,
                        **self.math_namespace
                    }

                    # 添加详细日志
                    print(f"[DEBUG] Executing expression: {processed_expr}")
                    print(f"[DEBUG] Time array shape: {t.shape}, len: {len(t)}")
                    print(f"[DEBUG] Available functions: {list(self.math_namespace.keys())[:10]}...")  # 只显示前10个

                    # 计算表达式
                    result = eval(processed_expr, {'__builtins__': {}}, local_namespace)

                    print(f"[DEBUG] Result type: {type(result)}, shape: {getattr(result, 'shape', 'N/A')}")

                    # 确保结果是numpy数组
                    result = np.asarray(result, dtype=np.float64)

                    # 检查结果有效性
                    if np.any(np.isnan(result)):
                        raise ParseError("计算结果包含NaN值")
                    if np.any(np.isinf(result)):
                        raise ParseError("计算结果包含无穷大值")

                    print(f"[DEBUG] Final result shape: {result.shape}")
                    return result

                except Exception as e:
                    print(f"[ERROR] Expression execution failed: {str(e)}")
                    print(f"[ERROR] Expression: {processed_expr}")
                    print(f"[ERROR] Error type: {type(e).__name__}")
                    import traceback
                    traceback.print_exc()
                    raise ParseError(f"表达式计算错误: {str(e)}")

            return waveform_function

        except ParseError:
            raise
        except Exception as e:
            raise ParseError(f"表达式解析失败: {str(e)}")

    def get_function_info(self, expression: str) -> Dict[str, Any]:
        """
        获取表达式的信息
        :param expression: 数学表达式
        :return: 包含函数信息的字典
        """
        try:
            # 预处理表达式
            processed_expr = self.preprocess_expression(expression)

            # 提取使用的函数名
            used_functions = []
            for func_name in self.math_namespace.keys():
                if func_name in processed_expr:
                    used_functions.append(func_name)

            # 分析表达式复杂度
            complexity = len(processed_expr)

            # 检查是否是复合函数
            is_composite = '+' in processed_expr or '-' in processed_expr or '*' in processed_expr

            return {
                'expression': processed_expr,
                'used_functions': used_functions,
                'complexity': complexity,
                'is_composite': is_composite,
                'has_time_variable': 't' in processed_expr
            }

        except Exception as e:
            raise ParseError(f"无法分析表达式: {str(e)}")

    def suggest_corrections(self, expression: str) -> list:
        """
        为常见错误提供修正建议
        :param expression: 有问题的表达式
        :return: 建议列表
        """
        suggestions = []

        # 检查常见错误
        if 'sin' in expression and 'PI' not in expression and 'pi' not in expression:
            suggestions.append("提示: 在三角函数中使用 PI 或 pi 表示π")

        if 't' not in expression:
            suggestions.append("错误: 表达式必须包含时间变量 't'")

        if expression.count('(') != expression.count(')'):
            suggestions.append("错误: 括号不匹配")

        # 检查是否缺少乘号
        if re.search(r'\d\s*[a-zA-Z]', expression):
            suggestions.append("提示: 数字和变量之间需要乘号，如: 2*PI*t")

        return suggestions

# 创建全局解析器实例
_parser_instance = None

def get_parser() -> FunctionParser:
    """获取全局解析器实例"""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = FunctionParser()
    return _parser_instance