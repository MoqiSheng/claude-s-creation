# 结题验收报告配图

| 文件 | 说明 |
|---|---|
| 图1_PBL驱动+翻转课堂双核教学模式.png | 第2项 主要改革成果（与年检报告图2相同） |
| 学生评价词云_占位_v4.png | 第2项 实践效果。占位用，须换成真实评价生成的词云后再提交 |
| make_wordcloud.py | 词云生成脚本（沿用暑期学校申报书的格式与配色，术语表已换成本课程） |

## 用真实评价生成词云

1. 安装依赖：`pip install wordcloud jieba numpy pillow`
2. 把学生评价逐行粘贴进脚本同目录的 `student_comments.txt`。
3. 运行 `python make_wordcloud.py`，输出 `student_wordcloud.png`，终端会打印高频词前20，可用于改写正文。
4. 脚本会自动查找 Windows 微软雅黑、macOS 苹方等中文字体。
