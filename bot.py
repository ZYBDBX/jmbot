from ncatbot.core import BotClient
from ncatbot.core import GroupMessage
import os
from wand.image import Image as WandImage
from ncatbot.utils import config
import jmcomic

bot = BotClient()

@bot.group_event()
async def on_group_message(msg: GroupMessage):
    if msg.raw_message.isdigit():  # 检测消息是否为纯数字
        download_member = msg.raw_message
        await download_and_convert(msg.group_id, download_member)

async def download_and_convert(group_id, download_member):
    current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件夹路径
    download_dir = os.path.join(current_dir, 'download')  # 设置下载文件夹为当前文件夹下的 download 文件夹

    # 如果 download 文件夹不存在，则创建它
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # 切换到 download_dir 目录下
    os.chdir(download_dir)

    # 使用 jmcomic 库下载文件
    jmcomic.download_album(download_member)

    # 切换回原来的目录
    os.chdir(current_dir)

    # 自动检测 download 文件夹中最新的文件夹
    latest_folder = max([os.path.join(download_dir, d) for d in os.listdir(download_dir)], key=os.path.getmtime)

    # 将最新的文件夹内的 webp 文件转换成 pdf
    webp_files = [f for f in os.listdir(latest_folder) if f.endswith('.webp')]
    pdf_path = os.path.join(latest_folder, f'{download_member}.pdf')

    with WandImage() as pdf:
        for webp_file in webp_files:
            webp_path = os.path.join(latest_folder, webp_file)
            with WandImage(filename=webp_path) as img:
                img.format = 'pdf'
                pdf.sequence.append(img)
        pdf.save(filename=pdf_path)

    # 将 pdf 发送到检测到这个数字的 QQ 群
    await bot.api.post_group_file(group_id=group_id, file=pdf_path)
          
bot.run(enable_webui_interaction=False)
