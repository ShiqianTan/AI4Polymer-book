# 构建与检查脚本

| 脚本 | 用途 |
| --- | --- |
| [build_site.py](build_site.py) | 收集正文 Markdown 与引用的图片，构建阅读网站；`--serve` 启动本地预览 |
| [check_site.py](check_site.py) | 检查生成网站的页面、锚点和资源链接 |
| [check_no_html.py](check_no_html.py) | 拒绝提交 HTML 源文件（包括被 `.gitignore` 忽略后强制添加的文件） |
| [verify_core_principles.py](verify_core_principles.py) | 检查章末小结、参考链接、图号与脚注；需要 `manuscripts/` 下 16 章正文 |
| [outline_text.py](outline_text.py)、[test_outline_text.py](test_outline_text.py) | 大纲渲染用的行内文本处理及其测试 |

网站构建方法见 [website/README.md](../website/README.md)，PDF 构建见 [book/README.md](../book/README.md)。
