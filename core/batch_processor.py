"""
批量处理器
支持批量生成、处理和导出波形
"""

import numpy as np
import os
from typing import List, Dict, Any, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from datetime import datetime

from core import get_generator
from core.waveform_editor import WaveformEditor

class BatchProcessor:
    """批量处理器"""

    def __init__(self):
        """初始化批量处理器"""
        self.generator = get_generator()
        self.tasks = []
        self.results = []
        self.progress_callback = None
        self.max_workers = 4  # 最大并发处理数

    def set_progress_callback(self, callback: Callable[[int, int, str], None]):
        """
        设置进度回调函数
        :param callback: 回调函数 (current, total, description)
        """
        self.progress_callback = callback

    def add_generation_task(self, expression: str, duration: float = 5.0,
                           sample_rate: int = 44100, amplitude: float = 1.0,
                           task_id: str = None) -> str:
        """
       添加波形生成任务
        :param expression: 波形表达式
        :param duration: 持续时间
        :param sample_rate: 采样率
        :param amplitude: 振幅
        :param task_id: 任务ID（可选）
        :return: 任务ID
        """
        if task_id is None:
            task_id = f"gen_{int(time.time() * 1000)}"

        task = {
            "id": task_id,
            "type": "generate",
            "expression": expression,
            "duration": duration,
            "sample_rate": sample_rate,
            "amplitude": amplitude,
            "status": "pending",
            "result": None,
            "error": None
        }

        self.tasks.append(task)
        return task_id

    def add_processing_task(self, waveform: np.ndarray, operations: List[Dict[str, Any]],
                           task_id: str = None) -> str:
        """
        添加波形处理任务
        :param waveform: 输入波形
        :param operations: 操作列表
        :param task_id: 任务ID
        :return: 任务ID
        """
        if task_id is None:
            task_id = f"proc_{int(time.time() * 1000)}"

        task = {
            "id": task_id,
            "type": "process",
            "waveform": waveform,
            "operations": operations,
            "status": "pending",
            "result": None,
            "error": None
        }

        self.tasks.append(task)
        return task_id

    def add_export_task(self, waveform: np.ndarray, filename: str,
                       format: str = 'wav', sample_rate: int = 44100,
                       task_id: str = None) -> str:
        """
        添加导出任务
        :param waveform: 波形数据
        :param filename: 输出文件名
        :param format: 文件格式
        :param sample_rate: 采样率
        :param task_id: 任务ID
        :return: 任务ID
        """
        if task_id is None:
            task_id = f"export_{int(time.time() * 1000)}"

        task = {
            "id": task_id,
            "type": "export",
            "waveform": waveform,
            "filename": filename,
            "format": format,
            "sample_rate": sample_rate,
            "status": "pending",
            "result": None,
            "error": None
        }

        self.tasks.append(task)
        return task_id

    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理单个任务
        :param task: 任务字典
        :return: 处理结果
        """
        try:
            task["status"] = "processing"

            if task["type"] == "generate":
                # 波形生成任务
                waveform, sample_rate = self.generator.generate_waveform(
                    task["expression"],
                    task["duration"],
                    task["sample_rate"],
                    task["amplitude"]
                )

                task["result"] = {
                    "waveform": waveform,
                    "sample_rate": sample_rate
                }

            elif task["type"] == "process":
                # 波形处理任务
                editor = WaveformEditor()
                editor.load_waveform(task["waveform"])

                # 应用所有操作
                for operation in task["operations"]:
                    op_type = operation["type"]
                    params = operation.get("params", {})

                    if op_type == "gain":
                        editor.apply_gain(**params)
                    elif op_type == "fade_in":
                        editor.fade_in(**params)
                    elif op_type == "fade_out":
                        editor.fade_out(**params)
                    elif op_type == "envelope":
                        editor.apply_envelope(**params)
                    elif op_type == "normalize":
                        editor.normalize(**params)
                    elif op_type == "filter":
                        editor.apply_filter(**params)
                    elif op_type == "noise":
                        editor.add_noise(**params)
                    # 可以添加更多操作类型...

                task["result"] = {
                    "waveform": editor.current_waveform,
                    "sample_rate": editor.sample_rate
                }

            elif task["type"] == "export":
                # 导出任务
                from scipy.io import wavfile

                waveform = task["waveform"]
                waveform_int16 = np.int16(waveform * 32767)

                # 确保目录存在
                os.makedirs(os.path.dirname(task["filename"]), exist_ok=True)

                wavfile.write(task["filename"], task["sample_rate"], waveform_int16)

                task["result"] = {
                    "filename": task["filename"],
                    "size": len(waveform)
                }

            task["status"] = "completed"
            return task

        except Exception as e:
            task["status"] = "failed"
            task["error"] = str(e)
            return task

    def process_all(self, parallel: bool = True) -> List[Dict[str, Any]]:
        """
        处理所有任务
        :param parallel: 是否并行处理
        :return: 处理结果列表
        """
        self.results = []
        total_tasks = len(self.tasks)

        if parallel and total_tasks > 1:
            # 并行处理
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_task = {
                    executor.submit(self.process_task, task): task
                    for task in self.tasks
                }

                for future in as_completed(future_to_task):
                    task = future_to_task[future]
                    try:
                        result = future.result()
                        self.results.append(result)

                        # 更新进度
                        if self.progress_callback:
                            completed = len([r for r in self.results if r["status"] in ["completed", "failed"]])
                            self.progress_callback(completed, total_tasks, f"任务 {task['id']} 完成")

                    except Exception as e:
                        task["status"] = "failed"
                        task["error"] = str(e)
                        self.results.append(task)
        else:
            # 串行处理
            for i, task in enumerate(self.tasks):
                result = self.process_task(task)
                self.results.append(result)

                # 更新进度
                if self.progress_callback:
                    self.progress_callback(i + 1, total_tasks, f"任务 {task['id']} 完成")

        return self.results

    def batch_generate(self, expressions: List[str], common_params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        批量生成波形
        :param expressions: 表达式列表
        :param common_params: 通用参数
        :return: 生成结果列表
        """
        # 清除现有任务
        self.tasks = []
        self.results = []

        # 添加生成任务
        params = common_params or {}
        for expr in expressions:
            self.add_generation_task(
                expression=expr,
                duration=params.get("duration", 5.0),
                sample_rate=params.get("sample_rate", 44100),
                amplitude=params.get("amplitude", 1.0)
            )

        # 处理所有任务
        return self.process_all()

    def batch_export(self, waveforms: List[np.ndarray], filenames: List[str],
                    format: str = 'wav', sample_rate: int = 44100) -> List[Dict[str, Any]]:
        """
        批量导出波形
        :param waveforms: 波形列表
        :param filenames: 文件名列表
        :param format: 文件格式
        :param sample_rate: 采样率
        :return: 导出结果列表
        """
        # 清除现有任务
        self.tasks = []
        self.results = []

        # 添加导出任务
        for waveform, filename in zip(waveforms, filenames):
            self.add_export_task(
                waveform=waveform,
                filename=filename,
                format=format,
                sample_rate=sample_rate
            )

        # 处理所有任务
        return self.process_all()

    def batch_process(self, waveforms: List[np.ndarray],
                     operations: List[Dict[str, Any]]) -> List[np.ndarray]:
        """
        批量处理波形
        :param waveforms: 波形列表
        :param operations: 操作列表
        :return: 处理后的波形列表
        """
        # 清除现有任务
        self.tasks = []
        self.results = []

        # 添加处理任务
        for waveform in waveforms:
            self.add_processing_task(waveform, operations)

        # 处理所有任务
        results = self.process_all()

        # 提取处理后的波形
        processed_waveforms = []
        for result in results:
            if result["status"] == "completed" and result["result"]:
                processed_waveforms.append(result["result"]["waveform"])
            else:
                processed_waveforms.append(None)

        return processed_waveforms

    def get_progress(self) -> Dict[str, Any]:
        """获取处理进度"""
        total = len(self.tasks)
        if total == 0:
            return {"total": 0, "completed": 0, "failed": 0, "progress": 0.0}

        completed = len([r for r in self.results if r["status"] == "completed"])
        failed = len([r for r in self.results if r["status"] == "failed"])
        processed = completed + failed

        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "processed": processed,
            "progress": processed / total if total > 0 else 0.0
        }

    def clear_tasks(self):
        """清除所有任务"""
        self.tasks = []
        self.results = []

    def get_failed_tasks(self) -> List[Dict[str, Any]]:
        """获取失败的任务"""
        return [task for task in self.results if task["status"] == "failed"]

    def get_summary(self) -> Dict[str, Any]:
        """获取处理摘要"""
        if not self.results:
            return {}

        total_time = sum([
            r.get("processing_time", 0) for r in self.results
            if r["status"] == "completed"
        ])

        return {
            "total_tasks": len(self.tasks),
            "completed_tasks": len([r for r in self.results if r["status"] == "completed"]),
            "failed_tasks": len([r for r in self.results if r["status"] == "failed"]),
            "total_time": total_time,
            "average_time": total_time / len(self.results) if self.results else 0,
            "success_rate": len([r for r in self.results if r["status"] == "completed"]) / len(self.results) if self.results else 0
        }