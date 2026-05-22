"""
项目文件管理器
支持保存、加载、导入、导出项目文件
"""

import json
import os
import time
from typing import Dict, Any, Optional
from datetime import datetime
import numpy as np

class ProjectManager:
    """项目管理器"""

    def __init__(self, project_dir: str = "projects"):
        """
        初始化项目管理器
        :param project_dir: 项目文件目录
        """
        self.project_dir = project_dir
        self.current_project = None
        self.auto_save_enabled = True
        self.auto_save_interval = 300  # 5分钟

        # 创建项目目录
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)

    def create_project(self, project_name: str, settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        创建新项目
        :param project_name: 项目名称
        :param settings: 项目设置
        :return: 项目信息字典
        """
        project = {
            "name": project_name,
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "version": "1.0",
            "settings": settings or {},
            "waveforms": [],
            "presets": [],
            "history": []
        }

        self.current_project = project
        return project

    def save_project(self, project: Dict[str, Any] = None, filename: str = None) -> str:
        """
        保存项目
        :param project: 项目数据
        :param filename: 文件名（可选）
        :return: 保存的文件路径
        """
        project = project or self.current_project
        if not project:
            raise ValueError("没有项目数据可保存")

        # 更新修改时间
        project["modified"] = datetime.now().isoformat()

        # 生成文件名
        if not filename:
            filename = f"{project['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = os.path.join(self.project_dir, filename)

        # 保存项目数据
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(project, f, indent=2, ensure_ascii=False)

        self.current_project = project
        return filepath

    def load_project(self, filepath: str) -> Dict[str, Any]:
        """
        加载项目
        :param filepath: 项目文件路径
        :return: 项目数据
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            project = json.load(f)

        self.current_project = project
        return project

    def add_waveform_to_project(self, expression: str, parameters: Dict[str, Any],
                                waveform_data: np.ndarray = None):
        """
        添加波形到项目
        :param expression: 波形表达式
        :param parameters: 波形参数
        :param waveform_data: 波形数据（可选）
        """
        if not self.current_project:
            raise ValueError("没有加载的项目")

        waveform_entry = {
            "id": int(time.time()),
            "expression": expression,
            "parameters": parameters,
            "created": datetime.now().isoformat(),
            "has_data": waveform_data is not None
        }

        # 如果有波形数据，保存到单独的文件
        if waveform_data is not None:
            data_filename = f"waveform_{waveform_entry['id']}.npy"
            data_filepath = os.path.join(self.project_dir, data_filename)
            np.save(data_filepath, waveform_data)
            waveform_entry["data_file"] = data_filename

        self.current_project["waveforms"].append(waveform_entry)

        # 添加到历史记录
        self.add_history_entry("add_waveform", f"添加波形: {expression}")

    def export_waveform(self, waveform_id: int, export_format: str = "wav",
                       output_dir: str = "exports") -> str:
        """
        导出波形
        :param waveform_id: 波形ID
        :param export_format: 导出格式 (wav, csv, txt)
        :param output_dir: 输出目录
        :return: 导出文件路径
        """
        if not self.current_project:
            raise ValueError("没有加载的项目")

        # 查找波形
        waveform_entry = None
        for wf in self.current_project["waveforms"]:
            if wf["id"] == waveform_id:
                waveform_entry = wf
                break

        if not waveform_entry:
            raise ValueError(f"找不到波形ID: {waveform_id}")

        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"waveform_{waveform_id}_{timestamp}.{export_format}"
        filepath = os.path.join(output_dir, filename)

        if export_format == "wav":
            # 导出为WAV文件
            from scipy.io import wavfile

            # 加载波形数据
            if "data_file" in waveform_entry:
                waveform_data = np.load(os.path.join(self.project_dir, waveform_entry["data_file"]))
            else:
                # 如果没有保存数据，重新生成
                from core import get_generator
                generator = get_generator()
                params = waveform_entry["parameters"]
                waveform_data, _ = generator.generate_waveform(
                    waveform_entry["expression"],
                    params.get("duration", 5.0),
                    params.get("sample_rate", 44100),
                    params.get("amplitude", 1.0)
                )

            # 转换为16位整数
            sample_rate = waveform_entry["parameters"].get("sample_rate", 44100)
            waveform_int16 = np.int16(waveform_data * 32767)
            wavfile.write(filepath, sample_rate, waveform_int16)

        elif export_format == "csv":
            # 导出为CSV文件
            import pandas as pd

            if "data_file" in waveform_entry:
                waveform_data = np.load(os.path.join(self.project_dir, waveform_entry["data_file"]))
            else:
                # 重新生成数据
                from core import get_generator
                generator = get_generator()
                params = waveform_entry["parameters"]
                waveform_data, sample_rate = generator.generate_waveform(
                    waveform_entry["expression"],
                    params.get("duration", 5.0),
                    params.get("sample_rate", 44100),
                    params.get("amplitude", 1.0)
                )

            # 创建时间轴
            sample_rate = waveform_entry["parameters"].get("sample_rate", 44100)
            time_axis = np.linspace(0, len(waveform_data) / sample_rate, len(waveform_data))

            # 创建DataFrame并保存
            df = pd.DataFrame({
                'time': time_axis,
                'amplitude': waveform_data
            })
            df.to_csv(filepath, index=False)

        elif export_format == "txt":
            # 导出为文本文件
            with open(filepath, 'w') as f:
                f.write(f"波形表达式: {waveform_entry['expression']}\n")
                f.write(f"参数: {waveform_entry['parameters']}\n")
                f.write(f"创建时间: {waveform_entry['created']}\n")
                f.write("-" * 40 + "\n")
                f.write("时间(秒)\t幅度\n")

                if "data_file" in waveform_entry:
                    waveform_data = np.load(os.path.join(self.project_dir, waveform_entry["data_file"]))
                else:
                    from core import get_generator
                    generator = get_generator()
                    params = waveform_entry["parameters"]
                    waveform_data, sample_rate = generator.generate_waveform(
                        waveform_entry["expression"],
                        params.get("duration", 5.0),
                        params.get("sample_rate", 44100),
                        params.get("amplitude", 1.0)
                    )

                sample_rate = waveform_entry["parameters"].get("sample_rate", 44100)
                time_axis = np.linspace(0, len(waveform_data) / sample_rate, len(waveform_data))

                for t, amp in zip(time_axis, waveform_data):
                    f.write(f"{t:.6f}\t{amp:.8f}\n")

        # 添加到历史记录
        self.add_history_entry("export", f"导出波形 {waveform_id} 为 {export_format}")

        return filepath

    def import_waveform(self, filepath: str, expression: str = "") -> int:
        """
        导入波形
        :param filepath: 波形文件路径
        :param expression: 关联的表达式
        :return: 波形ID
        """
        # 根据文件扩展名导入
        ext = os.path.splitext(filepath)[1].lower()

        if ext == '.wav':
            from scipy.io import wavfile
            sample_rate, waveform_data = wavfile.read(filepath)

            # 确保是单声道
            if len(waveform_data.shape) > 1:
                waveform_data = waveform_data[:, 0]

            # 归一化
            if waveform_data.dtype == np.int16:
                waveform_data = waveform_data / 32768.0

        elif ext in ['.npy']:
            waveform_data = np.load(filepath)
            sample_rate = 44100  # 默认采样率

        elif ext in ['.csv', '.txt']:
            import pandas as pd
            df = pd.read_csv(filepath)
            waveform_data = df['amplitude'].values
            sample_rate = 44100  # 默认采样率

        else:
            raise ValueError(f"不支持的文件格式: {ext}")

        # 创建波形条目
        waveform_entry = {
            "id": int(time.time()),
            "expression": expression or f"imported_{os.path.basename(filepath)}",
            "parameters": {
                "sample_rate": sample_rate,
                "duration": len(waveform_data) / sample_rate,
                "amplitude": 1.0,
                "imported_from": filepath
            },
            "created": datetime.now().isoformat(),
            "has_data": True
        }

        # 保存波形数据
        data_filename = f"waveform_{waveform_entry['id']}.npy"
        data_filepath = os.path.join(self.project_dir, data_filename)
        np.save(data_filepath, waveform_data)
        waveform_entry["data_file"] = data_filename

        # 添加到项目
        if self.current_project:
            self.current_project["waveforms"].append(waveform_entry)
            self.add_history_entry("import", f"导入波形: {filepath}")

        return waveform_entry["id"]

    def add_history_entry(self, action: str, description: str):
        """添加历史记录"""
        if not self.current_project:
            return

        entry = {
            "time": datetime.now().isoformat(),
            "action": action,
            "description": description
        }

        self.current_project["history"].append(entry)

        # 限制历史记录数量
        if len(self.current_project["history"]) > 100:
            self.current_project["history"] = self.current_project["history"][-100:]

    def get_project_list(self) -> list:
        """获取项目列表"""
        projects = []

        for filename in os.listdir(self.project_dir):
            if filename.endswith('.json'):
                try:
                    filepath = os.path.join(self.project_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        project = json.load(f)

                    projects.append({
                        "filename": filename,
                        "name": project.get("name", "未命名"),
                        "modified": project.get("modified", ""),
                        "waveforms_count": len(project.get("waveforms", []))
                    })
                except Exception as e:
                    print(f"读取项目文件失败 {filename}: {e}")

        # 按修改时间排序
        projects.sort(key=lambda x: x["modified"], reverse=True)
        return projects

    def delete_project(self, filename: str) -> bool:
        """删除项目"""
        try:
            filepath = os.path.join(self.project_dir, filename)

            # 读取项目以获取相关文件
            with open(filepath, 'r', encoding='utf-8') as f:
                project = json.load(f)

            # 删除波形数据文件
            for waveform in project.get("waveforms", []):
                if "data_file" in waveform:
                    data_path = os.path.join(self.project_dir, waveform["data_file"])
                    if os.path.exists(data_path):
                        os.remove(data_path)

            # 删除项目文件
            os.remove(filepath)

            return True
        except Exception as e:
            print(f"删除项目失败: {e}")
            return False

    def get_recent_projects(self, limit: int = 10) -> list:
        """获取最近的项目"""
        projects = self.get_project_list()
        return projects[:limit]

    def clear_current_project(self):
        """清除当前项目"""
        self.current_project = None

    def get_project_stats(self) -> dict:
        """获取项目统计信息"""
        if not self.current_project:
            return {}

        return {
            "name": self.current_project.get("name", "未命名"),
            "created": self.current_project.get("created", ""),
            "modified": self.current_project.get("modified", ""),
            "waveforms_count": len(self.current_project.get("waveforms", [])),
            "history_count": len(self.current_project.get("history", [])),
            "version": self.current_project.get("version", "1.0")
        }