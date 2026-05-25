# Voice Elf - 波形模拟器 🎵

一个功能强大的波形模拟器，支持用户输入任意波形函数及其组合，实时生成对应的波形图像和声音。使用 PyQt6 构建的现代化用户界面，提供丰富的音频处理和可视化功能。

## 功能特性

### 核心功能
- **数学表达式解析**: 支持输入任意数学表达式生成波形，如 `sin(2*PI*440*t)`
- **实时波形显示**: 时域和频域双视图可视化
- **音频播放控制**: 播放、暂停、停止和音量控制
- **参数调节**: 频率、音量、时长、采样率等参数实时调整

### 高级功能
- **波形库**: 内置常见波形模板（正弦波、方波、锯齿波等）
- **波形编辑**: 增益调整、淡入淡出、ADSR包络、滤波等
- **音频录制**: 支持麦克风录音
- **真实感增强**: 添加自然声音特性
- **科学计算器**: 复杂表达式编辑器
- **项目管理**: 保存和加载波形项目

## 技术栈

- **界面框架**: PyQt6
- **数值计算**: NumPy
- **音频处理**: SciPy, sounddevice
- **数据可视化**: Matplotlib
- **语言**: Python 3.8+

## 安装

### 环境要求
- Python 3.8 或更高版本
- 操作系统: Windows, macOS, Linux

### 安装依赖

```bash
pip install -r requirements.txt
```

依赖包包括:
- PyQt6 >= 6.4.0
- NumPy >= 1.24.0
- Matplotlib >= 3.7.0
- sounddevice >= 0.4.6
- SciPy >= 1.10.0

## 使用方法

### 启动应用

```bash
python main.py
```

## 打包分发

如果你想将波形模拟器打包成独立的可执行文件，可以分发给没有Python环境的用户：

### 快速打包（推荐）

1. **进入build目录**
   ```bash
   cd build
   ```

2. **安装打包依赖**
   ```bash
   pip install -r build_requirements.txt
   ```

3. **运行打包脚本**
   ```bash
   # Windows用户推荐
   python build_windows.py

   # 或使用通用方法
   python build.py
   ```

4. **验证打包结果**
   ```bash
   python test_package.py
   ```

### 打包结果

打包成功后，可执行文件位于：
- Windows: `dist/WaveformSimulator/WaveformSimulator.exe`
- 大小约 13-15 MB

整个 `dist/WaveformSimulator/` 目录可以独立运行，无需Python环境。

### 详细文档

更多打包信息和故障排除，请查看：
- `build/README.md` - 打包工具说明
- `build/BUILD_GUIDE.md` - 详细打包指南
- `build/PACKAGE_SUCCESS.md` - 打包成功案例

### 基础使用

1. **输入波形表达式**
   - 在函数输入框中输入数学表达式
   - 例如: `sin(2*PI*440*t)` 生成440Hz正弦波
   - 或使用频率变量: `sin(2*PI*f*t)` 然后调整频率参数

2. **调整参数**
   - **频率**: 20Hz - 20000Hz
   - **音量**: 0.0 - 1.0
   - **时长**: 0.1秒 - 60秒
   - **采样率**: 8000Hz - 48000Hz

3. **生成和播放**
   - 点击"播放"按钮生成并播放波形
   - 使用"快速波形"按钮快速选择常见波形

### 高级功能

#### 波形表达式语法

支持的数学函数和常数:
- **三角函数**: `sin`, `cos`, `tan`, `asin`, `acos`, `atan`
- **指数对数**: `exp`, `log`, `log10`, `sqrt`
- **信号函数**: `square`, `sawtooth`, `pulse`
- **常数**: `PI`, `E`
- **随机数**: `random`, `randn`, `uniform`

示例表达式:
```
# 简单正弦波
sin(2*PI*440*t)

# 和弦
0.5*sin(2*PI*440*t) + 0.3*sin(2*PI*554*t) + 0.2*sin(2*PI*659*t)

# 调幅波
(1 + 0.5*sin(2*PI*10*t)) * sin(2*PI*440*t)

# 调频波
sin(2*PI*(440 + 50*sin(2*PI*5*t))*t)

# 方波
signal.square(2*PI*440*t)
```

#### 波形编辑

1. 点击"编辑"按钮打开编辑对话框
2. 选择编辑操作:
   - 增益调整
   - 淡入/淡出效果
   - ADSR包络
   - 归一化
   - 低通/高通滤波
   - 添加噪音

#### 音频录制

1. 点击"录音"按钮
2. 设置录音时长
3. 录音完成后可对录制的音频进行编辑和处理

#### 项目管理

1. 创建新项目
2. 保存当前波形和参数
3. 加载历史项目继续编辑

## 项目结构

```
voice-elf/
├── main.py                      # 应用程序入口
├── config.json                  # 配置文件
├── requirements.txt             # 依赖列表
├── core/                        # 核心功能模块
│   ├── waveform_generator.py    # 波形生成器
│   ├── audio_controller.py      # 音频控制器
│   ├── function_parser.py       # 表达式解析器
│   ├── waveform_editor.py       # 波形编辑器
│   ├── audio_recorder.py        # 音频录制器
│   └── common_waveforms.py      # 常见波形定义
├── gui/                         # 用户界面模块
│   ├── main_window.py           # 主窗口
│   ├── waveform_display.py      # 波形显示组件
│   ├── preset_manager.py        # 预设管理器
│   ├── scientific_calculator_dialog.py  # 科学计算器对话框
│   ├── waveform_browser_dialog.py       # 波形浏览器
│   └── realistic_sound_dialog.py        # 真实感增强对话框
├── utils/                       # 工具模块
│   ├── config_manager.py        # 配置管理器
│   ├── logger.py                # 日志记录器
│   ├── error_handler.py         # 错误处理器
│   ├── project_manager.py       # 项目管理器
│   └── user_preferences.py      # 用户偏好设置
├── projects/                    # 项目文件存储目录
└── logs/                        # 日志文件目录
```

## 配置

应用程序通过 `config.json` 文件进行配置:

```json
{
    "app_name": "波形模拟器",
    "version": "1.0.0",
    "audio": {
        "default_sample_rate": 44100,
        "default_duration": 5.0,
        "max_duration": 60.0,
        "default_volume": 0.8
    },
    "gui": {
        "window_title": "波形模拟器",
        "window_size": [1200, 800],
        "theme": "default"
    }
}
```

## 键盘快捷键

- **空格键**: 播放/暂停
- **Esc**: 停止播放
- **Ctrl+S**: 保存项目
- **Ctrl+O**: 打开项目
- **Ctrl+E**: 导出波形

## 故障排除

### 音频设备问题
如果遇到音频播放问题:
1. 检查系统音频设备是否正常
2. 确认音频设备未被其他应用占用
3. 尝试调整采样率设置

### 性能优化
- 对于长时间波形，减少显示点数
- 降低采样率可提高性能
- 关闭频域显示可节省资源

### 表达式解析错误
- 确保表达式包含时间变量 `t`
- 检查括号匹配
- 使用支持的数学函数
- 注意乘号不能省略

## 开发贡献

欢迎贡献代码、报告问题或提出改进建议!

### 开发环境设置

```bash
# 克隆项目
git clone <repository-url>
cd voice-elf

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

## 许可证

本项目采用 MIT 许可证。

## 作者

Voice Elf 开发团队

## 更新日志

### v1.0.0
- 初始版本发布
- 基础波形生成和播放功能
- 用户界面完善
- 高级编辑功能
- 项目管理功能

## 联系方式

如有问题或建议，请通过以下方式联系:
- 提交 Issue
- 发送邮件
- 加入讨论组

---

**享受音乐创造的乐趣！** 🎶