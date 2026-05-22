"""
波形模拟器 - 主程序入口
支持用户输入任意波形函数及其组合，实时生成对应的波形图像和声音
"""

import sys
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from gui import MainWindow
from utils import setup_logger, ConfigManager

def main():
    """主函数"""
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("波形模拟器")
    app.setOrganizationName("VoiceElf")

    try:
        # 初始化日志系统
        logger = setup_logger()
        logger.info("应用程序启动")

        # 加载配置
        config = ConfigManager()
        logger.info(f"配置加载完成: {config.get('app_name')} v{config.get('version')}")

        # 创建并显示主窗口
        window = MainWindow()
        window.show()

        logger.info("主窗口显示成功")

        # 设置异常处理
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            logger.error("未捕获的异常", exc_info=(exc_type, exc_value, exc_traceback))

        sys.excepthook = handle_exception

        # 运行事件循环
        exit_code = app.exec()

        logger.info(f"应用程序退出，退出代码: {exit_code}")
        sys.exit(exit_code)

    except Exception as e:
        logger.error(f"应用程序启动失败: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()