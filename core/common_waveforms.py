"""
常见波形模板库
提供常用的波形表达式和预设配置
"""

class CommonWaveforms:
    """常见波形模板类"""

    @staticmethod
    def get_all_waveforms() -> dict:
        """获取所有常见波形"""
        return {
            "基础波形": {
                "正弦波 (440Hz)": {
                    "expression": "sin(2*PI*440*t)",
                    "description": "标准的正弦波，频率440Hz（A4音符）",
                    "category": "基础",
                    "params": {"frequency": 440, "duration": 3.0}
                },
                "低频正弦波 (100Hz)": {
                    "expression": "sin(2*PI*100*t)",
                    "description": "低频正弦波，100Hz",
                    "category": "基础",
                    "params": {"frequency": 100, "duration": 3.0}
                },
                "高频正弦波 (1000Hz)": {
                    "expression": "sin(2*PI*1000*t)",
                    "description": "高频正弦波，1000Hz",
                    "category": "基础",
                    "params": {"frequency": 1000, "duration": 2.0}
                },
                "方波 (440Hz)": {
                    "expression": "signal.square(2*PI*440*t)",
                    "description": "方波，440Hz",
                    "category": "基础",
                    "params": {"frequency": 440, "duration": 3.0}
                },
                "锯齿波 (440Hz)": {
                    "expression": "signal.sawtooth(2*PI*440*t)",
                    "description": "锯齿波，440Hz",
                    "category": "基础",
                    "params": {"frequency": 440, "duration": 3.0}
                },
                "三角波 (440Hz)": {
                    "expression": "2*abs(2*(t*440 - floor(0.5 + t*440))) - 1",
                    "description": "三角波，440Hz",
                    "category": "基础",
                    "params": {"frequency": 440, "duration": 3.0}
                }
            },

            "音乐和弦": {
                "大三和弦 (C大调)": {
                    "expression": "0.5*sin(2*PI*261.63*t) + 0.3*sin(2*PI*329.63*t) + 0.2*sin(2*PI*392*t)",
                    "description": "C大调大三和弦 (C-E-G)",
                    "category": "音乐",
                    "params": {"duration": 4.0}
                },
                "小三和弦 (A小调)": {
                    "expression": "0.5*sin(2*PI*220*t) + 0.3*sin(2*PI*261.63*t) + 0.2*sin(2*PI*329.63*t)",
                    "description": "A小调和弦 (A-C-E)",
                    "category": "音乐",
                    "params": {"duration": 4.0}
                },
                "七和弦 (属七)": {
                    "expression": "0.4*sin(2*PI*392*t) + 0.3*sin(2*PI*493.88*t) + 0.2*sin(2*PI*587.33*t) + 0.1*sin(2*PI*783.99*t)",
                    "description": "G7七和弦",
                    "category": "音乐",
                    "params": {"duration": 4.0}
                },
                "强力五和弦": {
                    "expression": "0.7*sin(2*PI*440*t) + 0.5*sin(2*PI*554*t) + 0.3*sin(2*PI*659*t)",
                    "description": "摇滚常用强力五和弦",
                    "category": "音乐",
                    "params": {"duration": 4.0}
                }
            },

            "调制效果": {
                "调幅 (AM)": {
                    "expression": "(1 + 0.5*sin(2*PI*10*t)) * sin(2*PI*440*t)",
                    "description": "幅度调制，10Hz调制频率",
                    "category": "效果",
                    "params": {"carrier_freq": 440, "mod_freq": 10, "duration": 5.0}
                },
                "调频 (FM)": {
                    "expression": "sin(2*PI*(440 + 50*sin(2*PI*5*t))*t)",
                    "description": "频率调制，产生颤音效果",
                    "category": "效果",
                    "params": {"carrier_freq": 440, "mod_freq": 5, "duration": 5.0}
                },
                "颤音": {
                    "expression": "(1 + 0.1*sin(2*PI*6*t)) * sin(2*PI*440*t)",
                    "description": "振幅颤音，6Hz",
                    "category": "效果",
                    "params": {"frequency": 440, "vibrato_rate": 6, "duration": 4.0}
                },
                " Vibrato": {
                    "expression": "sin(2*PI*(440 + 10*sin(2*PI*5*t))*t)",
                    "description": "音高颤音，5Hz",
                    "category": "效果",
                    "params": {"center_freq": 440, "vibrato_rate": 5, "duration": 4.0}
                }
            },

            "包络效果": {
                "钢琴音色": {
                    "expression": "exp(-t*3) * sin(2*PI*440*t) + exp(-t*3) * sin(2*PI*880*t) + exp(-t*3) * sin(2*PI*1320*t)",
                    "description": "钢琴般的衰减音色",
                    "category": "包络",
                    "params": {"duration": 3.0}
                },
                "钟声效果": {
                    "expression": "exp(-t*2) * (sin(2*PI*800*t) + sin(2*PI*1200*t) + sin(2*PI*1600*t) + sin(2*PI*2000*t))",
                    "description": "金属质感的钟声效果",
                    "category": "包络",
                    "params": {"duration": 4.0}
                },
                "脉冲音": {
                    "expression": "exp(-((t-0.5)**2)/0.01) * sin(2*PI*880*t)",
                    "description": "类似敲击的脉冲音",
                    "category": "包络",
                    "params": {"duration": 2.0}
                },
                "渐强音": {
                    "expression": "(1-exp(-t*10)) * sin(2*PI*440*t)",
                    "description": "从弱渐强的音色",
                    "category": "包络",
                    "params": {"duration": 3.0}
                }
            },

            "特殊效果": {
                "拍频": {
                    "expression": "sin(2*PI*440*t) + sin(2*PI*445*t)",
                    "description": "两个相近频率产生的拍频效果",
                    "category": "特殊",
                    "params": {"freq1": 440, "freq2": 445, "duration": 5.0}
                },
                "频率扫描": {
                    "expression": "sin(2*PI*(200 + 400*t)*t)",
                    "description": "从200Hz扫到600Hz的线性扫描",
                    "category": "特殊",
                    "params": {"start_freq": 200, "end_freq": 600, "duration": 3.0}
                },
                "脉冲序列": {
                    "expression": "pulse(2*PI*10*t, 0.3) * sin(2*PI*880*t)",
                    "description": "10Hz的脉冲序列",
                    "category": "特殊",
                    "params": {"pulse_rate": 10, "tone_freq": 880, "duration": 4.0}
                },
                "白噪音": {
                    "expression": "(uniform(-0.5, 0.5, len(t))) * 0.5",
                    "description": "随机白噪音",
                    "category": "特殊",
                    "params": {"duration": 3.0}
                }
            },

            "合成器音色": {
                "主音 (Lead)": {
                    "expression": "0.3*sin(2*PI*440*t) + 0.2*sin(2*PI*880*t) + 0.1*sin(2*PI*1320*t) + 0.05*sin(2*PI*1760*t)",
                    "description": "合成器主音音色",
                    "category": "合成器",
                    "params": {"duration": 4.0}
                },
                "贝斯 (Bass)": {
                    "expression": "0.6*sin(2*PI*55*t) + 0.3*sin(2*PI*110*t) + 0.1*sin(2*PI*165*t)",
                    "description": "深沉的贝斯音色",
                    "category": "合成器",
                    "params": {"duration": 4.0}
                },
                "铜管音": {
                    "expression": "0.4*sin(2*PI*220*t) + 0.3*sin(2*PI*440*t) + 0.2*sin(2*PI*660*t) + 0.1*sin(2*PI*880*t)",
                    "description": "铜管乐器的音色",
                    "category": "合成器",
                    "params": {"duration": 4.0}
                },
                "电子琴": {
                    "expression": "signal.square(2*PI*110*t) * (1 + 0.5*sin(2*PI*8*t))",
                    "description": "电子琴/风琴音色",
                    "category": "合成器",
                    "params": {"duration": 4.0}
                }
            },

            "测试信号": {
                "双音测试": {
                    "expression": "sin(2*PI*1000*t) + sin(2*PI*2000*t)",
                    "description": "1kHz和2kHz的双音测试信号",
                    "category": "测试",
                    "params": {"duration": 3.0}
                },
                "多频测试": {
                    "expression": "sin(2*PI*500*t) + 0.5*sin(2*PI*1000*t) + 0.3*sin(2*PI*2000*t)",
                    "description": "500Hz, 1kHz, 2kHz多频测试",
                    "category": "测试",
                    "params": {"duration": 3.0}
                },
                "频率扫描测试": {
                    "expression": "sin(2*PI*(20 + 1000*t)*t)",
                    "description": "20Hz到1kHz的对数频率扫描",
                    "category": "测试",
                    "params": {"duration": 5.0}
                }
            },

            "高级效果": {
                "合唱效果": {
                    "expression": "0.6*sin(2*PI*440*t) + 0.2*sin(2*PI*442*t) + 0.2*sin(2*PI*438*t)",
                    "description": "稍微失谐的多重声音产生合唱效果",
                    "category": "高级",
                    "params": {"duration": 4.0}
                },
                "相位调制": {
                    "expression": "sin(2*PI*440*t + 5*sin(2*PI*3*t))",
                    "description": "相位调制产生金属音色",
                    "category": "高级",
                    "params": {"carrier_freq": 440, "mod_freq": 3, "duration": 4.0}
                },
                "环形调制": {
                    "expression": "sin(2*PI*440*t) * sin(2*PI*50*t)",
                    "description": "环形调制产生铃音效果",
                    "category": "高级",
                    "params": {"carrier_freq": 440, "mod_freq": 50, "duration": 4.0}
                },
                "失真效果": {
                    "expression": "tanh(3 * sin(2*PI*440*t))",
                    "description": "软削波失真效果",
                    "category": "高级",
                    "params": {"frequency": 440, "distortion": 3, "duration": 4.0}
                }
            },

            "自然环境": {
                "风声": {
                    "expression": "(uniform(-0.5, 0.5, len(t))) * 0.3 * (1 + 0.5*sin(2*PI*0.5*t))",
                    "description": "模拟风声的噪音变化",
                    "category": "自然",
                    "params": {"duration": 5.0}
                },
                "海浪声": {
                    "expression": "exp(-((t%2)**2)*3) * (uniform(-0.5, 0.5, len(t))) * 0.5",
                    "description": "模拟海浪的周期性噪音",
                    "category": "自然",
                    "params": {"duration": 6.0}
                },
                "鸟鸣": {
                    "expression": "sin(2*PI*(2000 + 1000*sin(2*PI*5*t))*t) * exp(-t*2)",
                    "description": "模拟鸟鸣的频率调制和衰减",
                    "category": "自然",
                    "params": {"duration": 2.0}
                },
                "心跳": {
                    "expression": "(sin(2*PI*30*t) > 0.8) * 0.8 + (sin(2*PI*50*t) > 0.6) * 0.4",
                    "description": "模拟心跳的双重节拍",
                    "category": "自然",
                    "params": {"duration": 3.0}
                }
            },

            "电子音效": {
                "警报": {
                    "expression": "sin(2*PI*(800 + 400*(t%2 < 1))*t)",
                    "description": "高低交替的警报声",
                    "category": "电子",
                    "params": {"duration": 4.0}
                },
                "激光枪": {
                    "expression": "sin(2*PI*(2000 - 1500*t)*t) * exp(-t*5)",
                    "description": "频率快速下降的激光音效",
                    "category": "电子",
                    "params": {"duration": 1.0}
                },
                "电话铃声": {
                    "expression": "sin(2*PI*(400 + 600*(t%0.1 < 0.05))*t)",
                    "description": "双音频电话铃声",
                    "category": "电子",
                    "params": {"duration": 3.0}
                },
                "摩托引擎": {
                    "expression": "0.5*sin(2*PI*100*t) + 0.3*sin(2*PI*200*t) + 0.2*sin(2*PI*(50 + 20*t)*t)",
                    "description": "模拟引擎的复杂振动",
                    "category": "电子",
                    "params": {"duration": 5.0}
                }
            },

            "乐器仿真": {
                "小提琴": {
                    "expression": "(1 - exp(-t*20)) * 0.8*sin(2*PI*440*t) + 0.3*sin(2*PI*880*t) + 0.1*sin(2*PI*1320*t)",
                    "description": "小提琴的起音和丰富谐波",
                    "category": "乐器",
                    "params": {"duration": 4.0}
                },
                "长笛": {
                    "expression": "(1 - exp(-t*5)) * sin(2*PI*880*t) + 0.1*sin(2*PI*1760*t)",
                    "description": "长笛的纯净音色",
                    "category": "乐器",
                    "params": {"duration": 3.0}
                },
                "小号": {
                    "expression": "(1 - exp(-t*10)) * (0.7*sin(2*PI*440*t) + 0.3*sin(2*PI*880*t) + 0.1*sin(2*PI*1320*t))",
                    "description": "小号的明亮音色",
                    "category": "乐器",
                    "params": {"duration": 3.0}
                },
                "鼓声": {
                    "expression": "exp(-t*10) * sin(2*PI*80*t) + 0.5*exp(-t*20) * uniform(-0.5, 0.5, len(t))",
                    "description": "鼓的衰减音调和噪音",
                    "category": "乐器",
                    "params": {"duration": 1.0}
                }
            },

            "数学波形": {
                "高斯脉冲": {
                    "expression": "exp(-((t-1)**2)/0.01) * sin(2*PI*440*t)",
                    "description": "高斯窗调制的正弦波",
                    "category": "数学",
                    "params": {"duration": 2.0}
                },
                "sinc函数": {
                    "expression": "sin(2*PI*20*(t-1)) / (2*PI*20*(t-1) + 0.001)",
                    "description": "sinc函数波形",
                    "category": "数学",
                    "params": {"duration": 2.0}
                },
                "chirp信号": {
                    "expression": "sin(2*PI*(100 + 500*t)*t)",
                    "description": "线性调频信号",
                    "category": "数学",
                    "params": {"duration": 3.0}
                },
                "多普勒效应": {
                    "expression": "sin(2*PI*440*(1 - 0.3*exp(-t*2))*t)",
                    "description": "模拟多普勒效应的频率变化",
                    "category": "数学",
                    "params": {"duration": 4.0}
                }
            },

            "音乐音阶": {
                "C大调音阶": {
                    "expression": "sin(2*PI*261.63*t) + sin(2*PI*293.66*t) + sin(2*PI*329.63*t) + sin(2*PI*349.23*t) + sin(2*PI*392*t) + sin(2*PI*440*t) + sin(2*PI*493.88*t) + sin(2*PI*523.25*t)",
                    "description": "完整的C大调音阶 (Do-Re-Mi-Fa-Sol-La-Ti-Do)",
                    "category": "音乐",
                    "params": {"duration": 4.0}
                },
                "五声音阶": {
                    "expression": "sin(2*PI*261.63*t) + sin(2*PI*293.66*t) + sin(2*PI*329.63*t) + sin(2*PI*392*t) + sin(2*PI*440*t)",
                    "description": "中国五声音阶 (宫商角徵羽)",
                    "category": "音乐",
                    "params": {"duration": 4.0}
                },
                "半音阶": {
                    "expression": "sin(2*PI*440*t) + sin(2*PI*466.16*t) + sin(2*PI*493.88*t) + sin(2*PI*523.25*t) + sin(2*PI*554.37*t) + sin(2*PI*587.33*t)",
                    "description": "半音阶序列",
                    "category": "音乐",
                    "params": {"duration": 3.0}
                },
                "八度跳跃": {
                    "expression": "sin(2*PI*261.63*t) + sin(2*PI*523.25*t) + sin(2*PI*1046.5*t)",
                    "description": "跨越三个八度的音程",
                    "category": "音乐",
                    "params": {"duration": 3.0}
                }
            },

            "现代音乐": {
                " EDM低音": {
                    "expression": "0.8*sin(2*PI*55*t) + 0.4*sin(2*PI*110*t) + 0.2*sin(2*PI*55*t)*sin(2*PI*8*t)",
                    "description": "电子舞曲的深沉低音",
                    "category": "现代",
                    "params": {"duration": 4.0}
                },
                "合成器Pad": {
                    "expression": "0.3*sin(2*PI*220*t) + 0.2*sin(2*PI*440*t) + 0.2*sin(2*PI*660*t) + 0.1*sin(2*PI*880*t)",
                    "description": "氛围音乐用的合成器Pad音色",
                    "category": "现代",
                    "params": {"duration": 5.0}
                },
                "阿卡贝拉和声": {
                    "expression": "0.4*sin(2*PI*261.63*t) + 0.3*sin(2*PI*329.63*t) + 0.2*sin(2*PI*392*t) + 0.1*sin(2*PI*523.25*t)",
                    "description": "模拟人声和声",
                    "category": "现代",
                    "params": {"duration": 4.0}
                },
                "金属节奏": {
                    "expression": "signal.square(2*PI*110*t) + 0.5*signal.square(2*PI*55*t) + 0.3*sin(2*PI*220*t)",
                    "description": "重金属音乐节奏吉他音色",
                    "category": "现代",
                    "params": {"duration": 3.0}
                }
            },

            "经典合成器": {
                "Moog贝斯": {
                    "expression": "(1 - exp(-t*10)) * (sin(2*PI*55*t) + 0.3*sin(2*PI*110*t) + 0.1*sin(2*PI*165*t))",
                    "description": "经典的Moog合成器贝斯",
                    "category": "合成器",
                    "params": {"duration": 3.0}
                },
                "TB-303音序": {
                    "expression": "sawtooth(2*PI*110*t) * (1 + 0.5*sin(2*PI*4*t)) * exp(-t*2)",
                    "description": "Roland TB-303风格音序",
                    "category": "合成器",
                    "params": {"duration": 2.0}
                },
                "ARP 2600": {
                    "expression": "sin(2*PI*440*t) * (1 + 0.3*sin(2*PI*8*t)) + 0.2*sin(2*PI*50*t)",
                    "description": "ARP 2600合成器音色",
                    "category": "合成器",
                    "params": {"duration": 4.0}
                },
                "模拟合成器": {
                    "expression": "sawtooth(2*PI*220*t) + 0.5*square(2*PI*440*t) + 0.3*sin(2*PI*660*t)",
                    "description": "多振荡器模拟合成器",
                    "category": "合成器",
                    "params": {"duration": 4.0}
                }
            },

            "人声模拟": {
                "元音A": {
                    "expression": "sin(2*PI*800*t) + 0.5*sin(2*PI*1200*t) + 0.3*sin(2*PI*2600*t)",
                    "description": "模拟人声元音'A'的共振峰",
                    "category": "人声",
                    "params": {"duration": 2.0}
                },
                "元音E": {
                    "expression": "sin(2*PI*400*t) + 0.6*sin(2*PI*2200*t) + 0.2*sin(2*PI*3000*t)",
                    "description": "模拟人声元音'E'的共振峰",
                    "category": "人声",
                    "params": {"duration": 2.0}
                },
                "歌唱颤音": {
                    "expression": "(1 + 0.1*sin(2*PI*6*t)) * sin(2*PI*(440 + 5*sin(2*PI*5*t))*t)",
                    "description": "模拟歌唱时的颤音效果",
                    "category": "人声",
                    "params": {"duration": 4.0}
                },
                "合唱团": {
                    "expression": "0.3*sin(2*PI*440*t) + 0.25*sin(2*PI*442*t) + 0.25*sin(2*PI*438*t) + 0.2*sin(2*PI*441*t)",
                    "description": "模拟多人合唱效果",
                    "category": "人声",
                    "params": {"duration": 4.0}
                }
            },

            "游戏音效": {
                "金币收集": {
                    "expression": "sin(2*PI*(880 + 880*t)*t) * exp(-t*3)",
                    "description": "游戏中收集金币的音效",
                    "category": "游戏",
                    "params": {"duration": 1.0}
                },
                "跳跃音效": {
                    "expression": "sin(2*PI*(200 + 600*t)*t) * (1 - t/2)",
                    "description": "角色跳跃的音效",
                    "category": "游戏",
                    "params": {"duration": 1.0}
                },
                "爆炸声": {
                    "expression": "exp(-t*10) * (uniform(-0.5, 0.5, len(t))) + sin(2*PI*50*t)*exp(-t*5)",
                    "description": "游戏中的爆炸音效",
                    "category": "游戏",
                    "params": {"duration": 1.5}
                },
                "魔法施放": {
                    "expression": "sin(2*PI*(1000 + 2000*sin(2*PI*8*t))*t) * exp(-t*2)",
                    "description": "施放魔法的音效",
                    "category": "游戏",
                    "params": {"duration": 2.0}
                }
            },

            "信号处理": {
                "高斯脉冲": {
                    "expression": "exp(-((t-1)**2)/0.01) * sin(2*PI*440*t)",
                    "description": "高斯窗函数调制的正弦脉冲",
                    "category": "信号",
                    "params": {"duration": 2.0}
                },
                "Raised Cosine": {
                    "expression": "(1 + cos(PI*t))/2 * sin(2*PI*440*t)",
                    "description": "升余弦窗函数",
                    "category": "信号",
                    "params": {"duration": 2.0}
                },
                "Hamming窗": {
                    "expression": "(0.54 - 0.46*cos(2*PI*t)) * sin(2*PI*440*t)",
                    "description": "Hamming窗函数调制",
                    "category": "信号",
                    "params": {"duration": 1.0}
                },
                "Barker码": {
                    "expression": "sign(sin(2*PI*10*t)) * sin(2*PI*440*t)",
                    "description": "相位编码脉冲信号",
                    "category": "信号",
                    "params": {"duration": 1.0}
                }
            },

            "通信信号": {
                "ASK调制": {
                    "expression": "(1 + sign(sin(2*PI*5*t)))/2 * sin(2*PI*440*t)",
                    "description": "幅移键控调制",
                    "category": "通信",
                    "params": {"duration": 3.0}
                },
                "FSK调制": {
                    "expression": "sin(2*PI*(440 + 200*sign(sin(2*PI*5*t)))*t)",
                    "description": "频移键控调制",
                    "category": "通信",
                    "params": {"duration": 3.0}
                },
                "PSK调制": {
                    "expression": "sin(2*PI*440*t + PI*sign(sin(2*PI*5*t)))",
                    "description": "相移键控调制",
                    "category": "通信",
                    "params": {"duration": 3.0}
                },
                "QAM信号": {
                    "expression": "sin(2*PI*440*t + sign(sin(2*PI*5*t))*PI/4) * (1 + 0.3*sin(2*PI*3*t))",
                    "description": "正交幅度调制信号",
                    "category": "通信",
                    "params": {"duration": 3.0}
                }
            },

            "影视音效": {
                "科幻扫描": {
                    "expression": "sin(2*PI*(1000 + 3000*sin(2*PI*10*t))*t) * (1 + 0.5*sin(2*PI*15*t))",
                    "description": "科幻电影中的扫描音效",
                    "category": "影视",
                    "params": {"duration": 3.0}
                },
                "时空扭曲": {
                    "expression": "sin(2*PI*440*exp(t*2)*t) * exp(-t*1.5)",
                    "description": "时空扭曲的音效",
                    "category": "影视",
                    "params": {"duration": 2.0}
                },
                "机器人语音": {
                    "expression": "square(2*PI*100*t) + 0.5*square(2*PI*200*t) + 0.3*square(2*PI*300*t)",
                    "description": "机器人的电子语音",
                    "category": "影视",
                    "params": {"duration": 2.0}
                },
                " UFO悬停": {
                    "expression": "sin(2*PI*60*t) + 0.5*sin(2*PI*63*t) + 0.3*sin(2*PI*57*t)",
                    "description": "UFO悬停的低频嗡嗡声",
                    "category": "影视",
                    "params": {"duration": 5.0}
                }
            },

            "医疗器械": {
                "心率监测": {
                    "expression": "pulse(2*PI*1.2*t, 0.1) * sin(2*PI*800*t)",
                    "description": "医疗设备的心率监测音",
                    "category": "医疗",
                    "params": {"duration": 4.0}
                },
                "核磁共振": {
                    "expression": "sin(2*PI*(500 + 200*t)*t) * (1 + 0.3*sin(2*PI*8*t))",
                    "description": "核磁共振机的扫描音",
                    "category": "医疗",
                    "params": {"duration": 3.0}
                },
                "超声波": {
                    "expression": "sin(2*PI*20000*t) * (1 + 0.5*sin(2*PI*5*t))",
                    "description": "超声波扫描音效",
                    "category": "医疗",
                    "params": {"duration": 2.0}
                },
                "除颤器": {
                    "expression": "exp(-((t-0.5)**2)/0.001) * sin(2*PI*1000*t)",
                    "description": "医疗除颤器充电音",
                    "category": "医疗",
                    "params": {"duration": 1.5}
                }
            },

            "交通工具": {
                "汽车引擎": {
                    "expression": "0.6*sin(2*PI*80*t) + 0.4*sin(2*PI*120*t) + 0.2*sin(2*PI*160*t)",
                    "description": "汽车引擎的轰鸣声",
                    "category": "交通",
                    "params": {"duration": 3.0}
                },
                "飞机起飞": {
                    "expression": "sin(2*PI*(100 + 500*t)*t) * (1 - exp(-t*3))",
                    "description": "飞机起飞时的引擎声",
                    "category": "交通",
                    "params": {"duration": 4.0}
                },
                "火车汽笛": {
                    "expression": "sin(2*PI*440*t) * (1 + 0.5*sin(2*PI*2*t)) * exp(-t*0.5)",
                    "description": "火车汽笛的长鸣声",
                    "category": "交通",
                    "params": {"duration": 4.0}
                },
                "船笛": {
                    "expression": "sin(2*PI*150*t) + 0.5*sin(2*PI*300*t) + 0.3*sin(2*PI*450*t)",
                    "description": "轮船的低沉汽笛声",
                    "category": "交通",
                    "params": {"duration": 5.0}
                }
            },

            "自然界": {
                "雷声": {
                    "expression": "exp(-t*2) * (uniform(-0.5, 0.5, len(t))) + sin(2*PI*40*t)*exp(-t*1)",
                    "description": "远处的雷声隆隆",
                    "category": "自然",
                    "params": {"duration": 4.0}
                },
                "瀑布声": {
                    "expression": "exp(-((t%1)**2)*5) * (uniform(-0.5, 0.5, len(t))) * 0.6",
                    "description": "瀑布的持续水流声",
                    "category": "自然",
                    "params": {"duration": 6.0}
                },
                "火焰燃烧": {
                    "expression": "exp(-((t%0.5)**2)*10) * (uniform(-0.3, 0.3, len(t))) + sin(2*PI*50*t)*0.1",
                    "description": "火焰燃烧的噼啪声",
                    "category": "自然",
                    "params": {"duration": 3.0}
                },
                "地震": {
                    "expression": "sin(2*PI*10*t) * (1 + uniform(-0.5, 0.5, len(t))) * exp(-t*0.5)",
                    "description": "地震的低频震动声",
                    "category": "自然",
                    "params": {"duration": 5.0}
                }
            },

            "办公环境": {
                "打印机": {
                    "expression": "square(2*PI*50*t) * (1 + 0.5*sin(2*PI*20*t)) * exp(-((t%2)**2)*3)",
                    "description": "打印机的工作音效",
                    "category": "办公",
                    "params": {"duration": 3.0}
                },
                "键盘打字": {
                    "expression": "pulse(2*PI*8*t, 0.05) * sin(2*PI*1200*t)",
                    "description": "键盘打字的清脆声",
                    "category": "办公",
                    "params": {"duration": 2.0}
                },
                "电话铃声": {
                    "expression": "sin(2*PI*(400 + 200*sin(2*PI*8*t))*t) * (1 + sign(sin(2*PI*1*t))*0.5)",
                    "description": "现代电话铃声",
                    "category": "办公",
                    "params": {"duration": 4.0}
                },
                "传真机": {
                    "expression": "square(2*PI*110*t) + 0.3*sin(2*PI*1300*t)",
                    "description": "传真机的通讯音",
                    "category": "办公",
                    "params": {"duration": 3.0}
                }
            },

            "建筑工地": {
                "电钻": {
                    "expression": "square(2*PI*100*t) * (1 + 0.5*sin(2*PI*15*t)) + uniform(-0.2, 0.2, len(t))",
                    "description": "电钻的高频噪音",
                    "category": "建筑",
                    "params": {"duration": 2.0}
                },
                "锤击": {
                    "expression": "pulse(2*PI*2*t, 0.1) * sin(2*PI*200*t) * exp(-((t%0.5)**2)*20)",
                    "description": "锤子的敲击声",
                    "category": "建筑",
                    "params": {"duration": 3.0}
                },
                "起重机": {
                    "expression": "sin(2*PI*60*t) + 0.5*sin(2*PI*120*t) + 0.3*sin(2*PI*180*t)",
                    "description": "起重机的机械声",
                    "category": "建筑",
                    "params": {"duration": 4.0}
                },
                "混凝土搅拌": {
                    "expression": "sin(2*PI*30*t) * (1 + uniform(-0.5, 0.5, len(t))) + exp(-((t%1)**2)*5)",
                    "description": "混凝土搅拌机的声音",
                    "category": "建筑",
                    "params": {"duration": 5.0}
                }
            },

            "体育运动": {
                "哨声": {
                    "expression": "sin(2*PI*3000*t) * (1 + 0.5*sin(2*PI*5*t)) * exp(-t*3)",
                    "description": "体育裁判的哨声",
                    "category": "体育",
                    "params": {"duration": 1.0}
                },
                "击球声": {
                    "expression": "exp(-((t-0.1)**2)/0.0001) * sin(2*PI*500*t)",
                    "description": "网球/棒球击球声",
                    "category": "体育",
                    "params": {"duration": 0.5}
                },
                "跑道跑步": {
                    "expression": "sin(2*PI*(100 + 200*t)*t) * (1 - exp(-t*5))",
                    "description": "跑步时的脚步节奏声",
                    "category": "体育",
                    "params": {"duration": 2.0}
                },
                "游泳池": {
                    "expression": "exp(-((t%2)**2)*3) * (uniform(-0.5, 0.5, len(t))) * 0.8",
                    "description": "游泳池的水声",
                    "category": "体育",
                    "params": {"duration": 4.0}
                }
            }
        }

    @staticmethod
    def get_quick_access_waveforms() -> list:
        """获取快速访问的波形（最常用）"""
        return [
            {
                "name": "正弦波 (440Hz)",
                "expression": "sin(2*PI*440*t)",
                "category": "基础",
                "icon": "🌊"
            },
            {
                "name": "方波 (440Hz)",
                "expression": "signal.square(2*PI*440*t)",
                "category": "基础",
                "icon": "🔲"
            },
            {
                "name": "大三和弦",
                "expression": "0.5*sin(2*PI*261.63*t) + 0.3*sin(2*PI*329.63*t) + 0.2*sin(2*PI*392*t)",
                "category": "音乐",
                "icon": "🎵"
            },
            {
                "name": "调幅效果",
                "expression": "(1 + 0.5*sin(2*PI*10*t)) * sin(2*PI*440*t)",
                "category": "效果",
                "icon": "📻"
            },
            {
                "name": "钢琴音色",
                "expression": "exp(-t*3) * sin(2*PI*440*t) + exp(-t*3) * sin(2*PI*880*t) + exp(-t*3) * sin(2*PI*1320*t)",
                "category": "包络",
                "icon": "🎹"
            },
            {
                "name": "频率扫描",
                "expression": "sin(2*PI*(200 + 400*t)*t)",
                "category": "特殊",
                "icon": "📈"
            },
            {
                "name": "合唱效果",
                "expression": "0.6*sin(2*PI*440*t) + 0.2*sin(2*PI*442*t) + 0.2*sin(2*PI*438*t)",
                "category": "高级",
                "icon": "🎤"
            },
            {
                "name": "小提琴",
                "expression": "(1 - exp(-t*20)) * 0.8*sin(2*PI*440*t) + 0.3*sin(2*PI*880*t) + 0.1*sin(2*PI*1320*t)",
                "category": "乐器",
                "icon": "🎻"
            },
            {
                "name": "激光枪",
                "expression": "sin(2*PI*(2000 - 1500*t)*t) * exp(-t*5)",
                "category": "电子",
                "icon": "🔫"
            },
            {
                "name": "鸟鸣",
                "expression": "sin(2*PI*(2000 + 1000*sin(2*PI*5*t))*t) * exp(-t*2)",
                "category": "自然",
                "icon": "🐦"
            },
            {
                "name": "多普勒效应",
                "expression": "sin(2*PI*440*(1 - 0.3*exp(-t*2))*t)",
                "category": "数学",
                "icon": "📡"
            },
            {
                "name": "相位调制",
                "expression": "sin(2*PI*440*t + 5*sin(2*PI*3*t))",
                "category": "高级",
                "icon": "🔧"
            }
        ]

    @staticmethod
    def get_expression_by_name(name: str) -> str:
        """根据名称获取表达式"""
        all_waveforms = CommonWaveforms.get_all_waveforms()

        for category, waveforms in all_waveforms.items():
            if name in waveforms:
                return waveforms[name]["expression"]

        return ""

    @staticmethod
    def get_waveform_info(name: str) -> dict:
        """获取波形详细信息"""
        all_waveforms = CommonWaveforms.get_all_waveforms()

        for category, waveforms in all_waveforms.items():
            if name in waveforms:
                return waveforms[name]

        return {}

    @staticmethod
    def search_waveforms(keyword: str) -> list:
        """搜索波形"""
        results = []
        all_waveforms = CommonWaveforms.get_all_waveforms()

        for category, waveforms in all_waveforms.items():
            for name, info in waveforms.items():
                if (keyword.lower() in name.lower() or
                    keyword.lower() in info["description"].lower() or
                    keyword.lower() in category.lower()):
                    results.append({
                        "category": category,
                        "name": name,
                        "expression": info["expression"],
                        "description": info["description"]
                    })

        return results