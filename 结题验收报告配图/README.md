# 结题验收报告配图

| 文件 | 说明 |
|---|---|
| 图1_PBL驱动+翻转课堂双核教学模式.png | 第2项 主要改革成果（与年检报告图2相同） |
| 学生评价词云_占位.png | 第2项 实践效果。占位用，须换成真实问卷生成的词云后再提交 |
| wordcloud_fig.py | 词云生成脚本 |

## 用真实数据替换词云

1. 安装依赖：`pip install wordcloud jieba fonttools`
2. 准备中文字体文件，命名为 `NotoSansSC-Medium.otf` 放在脚本同目录（也可在脚本里把 `FONT` 改成本机任意中文字体路径，如 Windows 的 `C:/Windows/Fonts/msyh.ttc`）。
3. 把问卷第7题（印象最深的地方）的回答逐行粘贴进同目录的 `answers.txt`。
4. 运行 `python wordcloud_fig.py`，生成不带标注的 `学生评价词云.png`。
