Xiaomi Note Exporter (小米笔记批量导出工具)
这是一个专为小米云服务 (i.mi.com) 开发的 Python 批量导出工具，旨在解决官方笔记难以迁移的问题。

📌 项目定位
自用脚本：针对个人用户设计的轻量化导出方案。

极简操作：无需处理复杂的 Selenium 浏览器驱动报错，通过直接写入 Cookie 即可实现绕过验证，快速导出笔记内容。
方便账号是国内服务器的使用，如果是国外的可以用https://github.com/datsuraku147/exportNotes-XiaomiCloud的，当然国内也可以，自己修改地址，配置chromedriver环境


🚀 核心功能
一键批量导出：自动抓取所有云端笔记，并保存为标准的 .md (Markdown) 格式。
信息完整保留：自动提取笔记标题，并记录准确的创建与修改时间。
异常容错逻辑：自动处理无标题笔记，防止因数据格式缺失导致的程序崩溃。
有风险但避免了selem配置Chromedriver的麻烦

📖 使用说明
1. 环境准备
确保你的电脑已安装 Python 3.x 环境，且已安装 requests 库：

Bash
pip install requests   PIP安装请求
2. 配置凭证
本脚本采用“手动注入”方案以提高成功率：

打开 export.py。

**在 getNotes() 函数的 cookieHeader 字典中，填入你的个人凭证数据（见下文获取教程）。**

保存文件。

3. 运行导出
在项目根目录下打开终端或 PowerShell，运行：

Bash
python export.py
所有笔记将以 .md 文件形式生成在当前文件夹。

🔍 如何获取查看 Cookie？
为了保证 API 调用成功，建议填入完整的校验参数。请按以下步骤操作：

登录网页版：在 Chrome 浏览器登录 小米云服务笔记页。

进入开发者模式：按下 F12 键，点击顶部的 Network (网络) 标签页。

定位数据请求：

在左侧过滤框输入 full。
刷新页面，点击列表中出现的名为 full?... 的请求。
获取标头数据：
在右侧选择 Headers (标头)，找到 Request Headers (请求标头) 下的 Cookie 字段。

需要提取的关键键值对包括：
userId: 你的小米账号 ID。
serviceToken: 核心身份令牌。
i.mi.com_ph & i.mi.com_slh: 域名校验参数。i.mi.com_ph & i.mi.com_slh: 域名校验参数。
填写建议：直接从浏览器复制对应的 Value 值并粘贴到代码中。

⚠️ 开发备注与安全
Token 时效：serviceToken 会随时间过期，如遇到 401 报错，请重新执行上述抓取流程。

隐私提示：请妥善保管包含 Cookie 的 export.py 文件，切勿将其上传至公共代码仓库。
