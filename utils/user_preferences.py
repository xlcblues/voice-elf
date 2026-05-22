"""
用户偏好设置管理
管理用户的个人配置和偏好
"""

import json
import os
from typing import Any, Dict, Optional
from pathlib import Path

class UserPreferences:
    """用户偏好管理类"""

    def __init__(self, config_file: str = "user_preferences.json"):
        """
        初始化用户偏好管理
        :param config_file: 配置文件路径
        """
        self.config_file = config_file
        self.preferences = self._load_preferences()

    def _load_preferences(self) -> Dict[str, Any]:
        """加载用户偏好"""
        default_preferences = {
            # 音频设置
            "audio": {
                "default_sample_rate": 44100,
                "default_duration": 5.0,
                "default_volume": 0.8,
                "default_bit_depth": 16,
                "default_channels": 1,
                "buffer_size": 1024
            },

            # 显示设置
            "display": {
                "theme": "default",
                "color_scheme": "viridis",
                "show_grid": True,
                "auto_scale": True,
                "max_display_points": 10000,
                "update_interval": 50,
                "font_size": 10,
                "line_width": 0.5
            },

            # 编辑设置
            "editing": {
                "undo_limit": 50,
                "auto_save": True,
                "auto_save_interval": 300,  # 5分钟
                "backup_enabled": True,
                "backup_count": 5
            },

            # 文件设置
            "files": {
                "default_export_format": "wav",
                "default_export_dir": "exports",
                "default_project_dir": "projects",
                "remember_recent_files": True,
                "recent_files_limit": 10,
                "auto_create_dirs": True
            },

            # 性能设置
            "performance": {
                "max_workers": 4,
                "cache_enabled": True,
                "cache_size": 100,  # MB
                "parallel_processing": True,
                "gpu_acceleration": False
            },

            # 界面设置
            "interface": {
                "show_tooltips": True,
                "confirm_destructive": True,
                "animation_enabled": True,
                "status_bar_visible": True,
                "toolbar_visible": True,
                "sidebar_width": 300
            },

            # 高级设置
            "advanced": {
                "debug_mode": False,
                "log_level": "INFO",
                "experimental_features": False,
                "plugin_enabled": False
            },

            # 用户自定义
            "custom": {
                "user_presets": [],
                "user_macros": [],
                "favorite_expressions": []
            }
        }

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_prefs = json.load(f)
                # 合并默认设置和加载的设置
                return self._merge_preferences(default_preferences, loaded_prefs)
            except Exception as e:
                print(f"加载用户偏好失败: {e}")
                return default_preferences
        else:
            return default_preferences

    def _merge_preferences(self, default: Dict, loaded: Dict) -> Dict:
        """合并默认设置和加载的设置"""
        result = default.copy()

        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_preferences(result[key], value)
            else:
                result[key] = value

        return result

    def save_preferences(self) -> bool:
        """保存用户偏好"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存用户偏好失败: {e}")
            return False

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        获取偏好设置
        :param key_path: 键路径（如 "audio.default_sample_rate"）
        :param default: 默认值
        :return: 设置值
        """
        keys = key_path.split('.')
        value = self.preferences

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path: str, value: Any) -> None:
        """
        设置偏好
        :param key_path: 键路径
        :param value: 设置值
        """
        keys = key_path.split('.')
        prefs = self.preferences

        for key in keys[:-1]:
            if key not in prefs:
                prefs[key] = {}
            prefs = prefs[key]

        prefs[keys[-1]] = value

    def reset_to_defaults(self, category: str = None) -> None:
        """
        重置为默认设置
        :param category: 要重置的类别（None表示全部重置）
        """
        if category is None:
            self.preferences = self._load_preferences()
        else:
            # 重新加载该类别的默认值
            default_prefs = self._load_preferences()
            if category in default_prefs:
                self.preferences[category] = default_prefs[category]

    def export_preferences(self, filename: str) -> bool:
        """
        导出偏好设置
        :param filename: 导出文件名
        :return: 是否成功
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"导出偏好设置失败: {e}")
            return False

    def import_preferences(self, filename: str) -> bool:
        """
        导入偏好设置
        :param filename: 导入文件名
        :return: 是否成功
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                imported_prefs = json.load(f)

            # 合并导入的设置
            self.preferences = self._merge_preferences(self.preferences, imported_prefs)
            return True
        except Exception as e:
            print(f"导入偏好设置失败: {e}")
            return False

    def add_favorite_expression(self, expression: str, name: str = "") -> None:
        """添加常用表达式"""
        favorites = self.get("custom.favorite_expressions", [])
        favorite_entry = {
            "expression": expression,
            "name": name or expression,
            "added": str(Path(__file__).stat().st_mtime)
        }

        # 检查是否已存在
        for fav in favorites:
            if fav["expression"] == expression:
                return  # 已存在，不重复添加

        favorites.append(favorite_entry)
        self.set("custom.favorite_expressions", favorites)

    def remove_favorite_expression(self, expression: str) -> None:
        """移除常用表达式"""
        favorites = self.get("custom.favorite_expressions", [])
        favorites = [fav for fav in favorites if fav["expression"] != expression]
        self.set("custom.favorite_expressions", favorites)

    def get_recent_files(self) -> list:
        """获取最近文件列表"""
        return self.get("recent_files", [])

    def add_recent_file(self, filepath: str) -> None:
        """添加最近文件"""
        recent_files = self.get_recent_files()

        # 移除重复项
        recent_files = [f for f in recent_files if f != filepath]

        # 添加到开头
        recent_files.insert(0, filepath)

        # 限制数量
        limit = self.get("files.recent_files_limit", 10)
        recent_files = recent_files[:limit]

        self.set("recent_files", recent_files)

    def get_display_settings(self) -> Dict[str, Any]:
        """获取显示设置"""
        return self.preferences.get("display", {})

    def get_audio_settings(self) -> Dict[str, Any]:
        """获取音频设置"""
        return self.preferences.get("audio", {})

    def get_performance_settings(self) -> Dict[str, Any]:
        """获取性能设置"""
        return self.preferences.get("performance", {})

    def update_display_settings(self, **kwargs) -> None:
        """更新显示设置"""
        display = self.preferences.get("display", {})
        display.update(kwargs)
        self.set("display", display)

    def update_audio_settings(self, **kwargs) -> None:
        """更新音频设置"""
        audio = self.preferences.get("audio", {})
        audio.update(kwargs)
        self.set("audio", audio)

    def create_profile(self, profile_name: str, settings: Dict[str, Any]) -> None:
        """创建配置文件"""
        profiles = self.get("profiles", {})
        profiles[profile_name] = settings
        self.set("profiles", profiles)

    def load_profile(self, profile_name: str) -> bool:
        """加载配置文件"""
        profiles = self.get("profiles", {})
        if profile_name in profiles:
            self.preferences = self._merge_preferences(self.preferences, profiles[profile_name])
            return True
        return False

    def get_summary(self) -> Dict[str, Any]:
        """获取配置摘要"""
        return {
            "config_file": self.config_file,
            "categories": list(self.preferences.keys()),
            "total_settings": sum(len(v) if isinstance(v, dict) else 1 for v in self.preferences.values()),
            "custom_presets": len(self.get("custom.user_presets", [])),
            "favorite_expressions": len(self.get("custom.favorite_expressions", [])),
            "recent_files": len(self.get_recent_files())
        }

# 创建全局用户偏好实例
_user_prefs_instance = None

def get_user_preferences() -> UserPreferences:
    """获取全局用户偏好实例"""
    global _user_prefs_instance
    if _user_prefs_instance is None:
        _user_prefs_instance = UserPreferences()
    return _user_prefs_instance