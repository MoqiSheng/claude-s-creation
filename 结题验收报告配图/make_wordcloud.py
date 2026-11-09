"""
学生评价词云生成脚本
依赖：pip install wordcloud jieba numpy pillow
用法：python make_wordcloud.py
输入：student_comments.txt（每行一条学生评价）
输出：student_wordcloud.png
"""
import random
from collections import Counter

import jieba
import numpy as np
from wordcloud import WordCloud

# ---------------- 配置 ----------------
COMMENTS_FILE = "student_comments.txt"
OUTPUT_FILE = "student_wordcloud.png" if __import__("os").path.exists("student_comments.txt") else "student_wordcloud_占位.png"

# 中文字体（必须支持中文）。脚本会按顺序自动查找下列字体，也可直接改成你电脑上的字体路径
FONT_CANDIDATES = [
    "C:/Windows/Fonts/msyhbd.ttc",                 # Windows 微软雅黑粗体
    "C:/Windows/Fonts/msyh.ttc",                   # Windows 微软雅黑
    "C:/Windows/Fonts/simhei.ttf",                 # Windows 黑体
    "/System/Library/Fonts/PingFang.ttc",          # macOS 苹方
    "/System/Library/Fonts/STHeiti Medium.ttc",    # macOS 黑体
    "NotoSansSC-Bold.otf",                         # 与脚本同目录的思源黑体
]

WIDTH, HEIGHT = 2400, 1350   # 16:9
MAX_WORDS = 90
RANDOM_SEED = 7

# 与申报书其他配图一致的配色：蓝、绿、红、紫、青
PALETTE = ["#1F5FA8", "#2E7DD1", "#2F8F5B", "#C0392B", "#6C4FB3", "#0E7C86", "#1B3F73"]

# 专业术语：保证分词时不被拆开
USER_WORDS = [
    "深度学习", "神经网络", "卷积神经网络", "循环神经网络", "注意力机制", "Transformer",
    "大语言模型", "目标检测", "图像分割", "反向传播", "梯度下降", "损失函数",
    "课程项目", "项目实践", "翻转课堂", "课堂研讨", "方案辩论", "代码互评", "组间互评",
    "评分量表", "前沿专题", "跨学科", "跨学科案例", "智慧城市", "智慧医疗", "交通预测",
    "交通流量预测", "下一位置预测", "医学影像", "病变分割", "知识体系", "动手能力",
    "团队合作", "学以致用", "循序渐进", "讲解清晰", "答疑及时", "科研兴趣", "数据集",
]

# 同义词合并：左边的词统计时并入右边
SYNONYMS = {
    "项目实战": "项目实践", "做项目": "项目实践", "课程项目": "项目实践",
    "动手实践": "动手能力", "实践能力": "动手能力", "编程能力": "动手能力",
    "收获很大": "收获", "很有收获": "收获",
    "清楚": "清晰", "讲解清晰": "清晰",
    "前沿专题": "前沿", "前沿技术": "前沿",
    "跨学科案例": "跨学科", "交通流量预测": "交通预测",
    "大模型": "大语言模型",
}

STOPWORDS = set("""
的 了 和 是 在 也 都 很 让 我 我们 这 那 一 一下 一些 一个 就 能 会 把 用 对 与 及 及其
以及 还 又 更 最 非常 特别 真正 比较 有 没有 自己 这些 那些 这门 这门课 课程 老师 同学
通过 能够 可以 以后 以前 原来 起来 之后 时候 方面 时候 东西 什么 怎么 如何 一步步
比 从 到 中 上 下 后 前 里 着 过 得 地 啊 吧 呢 很多 很好 大 小 多 少 学 学习 理解 帮助
看 看到 知道 觉得 感觉 希望 建议 打算 继续 第一次 一下子 方便 推荐 整体 意义 原理 方法
内容 例子 设计 安排 结合 联系 很大 一样 不同 角度 问题 以后 提前 适应
跟不上 担心 只会 调包 作为 学生 为主 一步 工作 产生 背后 方式 含义 增加 改进 跟着 始终
贯穿 熟悉 充分 材料 不失 最大 在实践中 看待 一下 用到 打下 打算 意犹未尽 薄弱 不用 打开 浏览器 运行 配置 环境 讲 讲解 讲得 讲课 提高 提升 加深 深刻 系统 部分 以及 后续
""".split())


PLACEHOLDER_FREQS = {
    "项目实践": 100, "收获": 90, "动手能力": 84, "前沿": 78, "翻转课堂": 72, "清晰": 68,
    "跨学科": 64, "团队合作": 58, "代码互评": 52, "大语言模型": 50, "注意力机制": 46,
    "Transformer": 44, "循序渐进": 42, "学以致用": 40, "案例丰富": 38, "交通预测": 34,
    "医学影像": 32, "智慧城市": 30, "评分量表": 28, "课堂研讨": 27, "有挑战": 26,
    "知识体系": 25, "方案辩论": 24, "实用": 23, "循环神经网络": 22, "卷积神经网络": 21,
    "认真负责": 20, "自主学习": 19, "数据集": 18, "答疑及时": 17, "科研兴趣": 16,
    "图像分割": 15, "互评公平": 14, "课时紧张": 12, "工作量大": 11,
}


def find_font():
    import os
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return path
    raise FileNotFoundError("未找到中文字体，请在 FONT_CANDIDATES 中填写你电脑上的中文字体路径")


def load_comments(path):
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def count_words(comments):
    for w in USER_WORDS:
        jieba.add_word(w)
    counter = Counter()
    for line in comments:
        # 含空格的英文术语先替换成占位符，避免被拆开
        line = line.replace("Diffusion K-means", "DIFFKMEANS")
        for w in jieba.lcut(line):
            if w == "DIFFKMEANS":
                counter["Diffusion K-means"] += 1
                continue
            w = w.strip()
            if len(w) < 2 or w in STOPWORDS or w.isdigit():
                continue
            w = SYNONYMS.get(w, w)
            counter[w] += 1
    return counter


def ellipse_mask(w, h, margin=0.03):
    """椭圆形遮罩：白色(255)区域不放字，黑色(0)区域放字"""
    y, x = np.ogrid[:h, :w]
    cx, cy = w / 2, h / 2
    rx, ry = w / 2 * (1 - margin), h / 2 * (1 - margin)
    inside = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1
    mask = np.full((h, w), 255, dtype=np.uint8)
    mask[inside] = 0
    return mask


def palette_color(word, font_size, position, orientation, random_state=None, **kwargs):
    rng = random_state or random
    # 大号词用深色，提升可读性
    if font_size > 140:
        return rng.choice(["#1F5FA8", "#1B3F73", "#C0392B"])
    return rng.choice(PALETTE)


def main():
    random.seed(RANDOM_SEED)
    import os
    if os.path.exists(COMMENTS_FILE):
        comments = load_comments(COMMENTS_FILE)
        freqs = count_words(comments)
    else:  # 占位词频，仅用于排版，拿到真实评价后放入 student_comments.txt 重新运行
        comments = []
        freqs = Counter(PLACEHOLDER_FREQS)

    print(f"共 {len(comments)} 条评价，高频词前 20：")
    for w, c in freqs.most_common(20):
        print(f"  {w}: {c}")

    wc = WordCloud(
        font_path=find_font(),
        width=WIDTH,
        height=HEIGHT,
        background_color="white",
        mask=ellipse_mask(WIDTH, HEIGHT),
        max_words=MAX_WORDS,
        prefer_horizontal=0.92,
        min_font_size=22,
        max_font_size=300,
        relative_scaling=0.45,
        margin=6,
        color_func=palette_color,
        random_state=RANDOM_SEED,
        collocations=False,
    ).generate_from_frequencies(dict(freqs))

    wc.to_file(OUTPUT_FILE)
    print(f"已保存：{OUTPUT_FILE}")


if __name__ == "__main__":
    main()
