"""学生评价词云。
使用方法：把真实问卷开放题（第7题）的回答逐行放进 answers.txt，运行本脚本即可替换占位图。
answers.txt 不存在时，使用下面的占位词频生成示意图，并在图上标注“占位示意”。"""
import os, random
from collections import Counter
from wordcloud import WordCloud
from PIL import Image, ImageDraw, ImageFont

FONT = "NotoSansSC-Medium.otf"
PALETTE = ["#1F3A5F", "#2E5A87", "#3F6FA0", "#5B86B5", "#7A9CC6", "#41546B"]

def freqs_from_answers(path):
    import jieba  # 仅在使用真实数据时需要：pip install jieba
    stop = set("的 了 是 在 和 也 很 都 就 我 我们 这门 课程 课 老师 非常 比较 一些 可以 有 让 对 中 与 及".split())
    words = [w for line in open(path, encoding="utf-8") for w in jieba.lcut(line.strip())
             if len(w) > 1 and w not in stop]
    return dict(Counter(words).most_common(80)), False

def placeholder_freqs():
    f = {"项目实践": 100, "收获很大": 88, "动手能力": 82, "前沿": 76, "翻转课堂": 70, "讲解清晰": 66,
         "跨学科": 62, "团队合作": 58, "代码互评": 52, "大语言模型": 50, "注意力机制": 46, "Transformer": 44,
         "循序渐进": 42, "学以致用": 40, "案例丰富": 38, "交通预测": 34, "医学影像": 32, "智慧城市": 30,
         "评分标准清楚": 28, "课堂研讨": 27, "有挑战": 26, "知识体系": 25, "方案辩论": 24, "实用": 23,
         "循环神经网络": 22, "卷积神经网络": 21, "认真负责": 20, "自主学习": 19, "数据集": 18, "答疑及时": 17,
         "科研兴趣": 16, "图像分割": 15, "互评公平": 14, "课时紧张": 12, "工作量大": 11}
    return f, True

freqs, is_placeholder = (freqs_from_answers("answers.txt") if os.path.exists("answers.txt")
                         else placeholder_freqs())

import numpy as np
W, H = 1600, 1000
yy, xx = np.ogrid[:H, :W]
ellipse = ((xx - W/2) / (W/2 - 10))**2 + ((yy - H/2) / (H/2 - 10))**2 <= 1
MASK = np.where(ellipse, 0, 255).astype(np.uint8)

def color(*a, **k): return random.choice(PALETTE)
random.seed(7)
wc = WordCloud(font_path=FONT, mask=MASK, background_color="white",
               max_words=80, prefer_horizontal=0.95, margin=8, relative_scaling=0.35, max_font_size=170, min_font_size=22,
               color_func=color, random_state=7).generate_from_frequencies(freqs)
img = wc.to_image().convert("RGB")

out = "学生评价词云_占位.png" if is_placeholder else "学生评价词云.png"
img.save(out); print("saved", out)
