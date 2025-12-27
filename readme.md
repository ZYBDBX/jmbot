##由于不可抗力 本仓库从2025.12.27起进入只读
# NapCat 机器人部署教程（零基础小白向）

> **说明**：本教程专为零基础用户编写。如已安装所需运行库，请直接跳过相应步骤。

---

## Step 1：安装 Python（如已安装请跳过）

1. 双击运行压缩包内的 Python 安装程序。
2. **务必勾选下方的 `Add python.exe to PATH`**。
3. 点击 **Install Now**。
4. 等待安装进度条完成。

---

## Step 2：安装依赖包

1. 按下 `Win + R`，输入 `cmd` 并回车，打开命令提示符。
2. 依次执行以下命令（**不要带引号**，每条命令执行完并看到 `Successfully installed` 后再执行下一条）：

```bash
pip install somepackage -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install jmcomic
pip install ncatbot
pip install wand
执行完 pip install wand 后，双击运行 ImageMagick-7.1.1-47-Q16-x64-dll.exe 并完成安装。
Step 3：部署 NapCat
找到 Napcat.Shell.Windows.Onekey.zip 并解压。
双击运行解压后的 .exe 文件，等待进度条跑完。
运行完成后，双击 napcat.bat。
根据提示扫码登录 QQ（⚠️ 登录后请保持该窗口开启，不要关闭）。
Step 4：配置 WebUI
打开浏览器，访问：
http://127.0.0.1:3011/webui
初始密码（Token）为：napcat
进入后点击 网络配置 → 新建 HTTP 服务端。
保持所有设置为默认，点击 启用。
Step 5：启动机器人
双击运行 bot.py。
按提示填入你的机器人 QQ 号。
若显示 机器人xxxx成功启动，则表示部署成功。
将机器人账号拉入群聊，在群中发送纯数字（如 1234）进行测试。
✅ 有效示例：1234、1456
❌ 无效示例：jm1234、经历1场战斗和2个敌人作战最终战胜3人
注意事项
检测时必须在群聊中发送纯数字，混合文本不会被识别。
切勿在短时间内反复启动 napcat.bat，否则有 QQ 被限制（封号）风险。
如遇本文未提及的问题，欢迎联系作者：
QQ：1340265938
在线时间：
工作日：21:00 – 23:00
节假日：几乎任意时间
