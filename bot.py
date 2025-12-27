from ncatbot.core import BotClient
from ncatbot.core import GroupMessage
from wand.image import Image as WandImage
from ncatbot.utils import config
from jmcomic import *
import random
import asyncio
import os


bot = BotClient()


async def download_and_convert(group_id, download_member):
    current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件夹路径
    download_dir = os.path.join(current_dir, 'download')  # 设置下载文件夹为当前文件夹下的 download 文件夹

    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # 切换到 download_dir 目录下
    os.chdir(download_dir)

    # 使用 jmcomic 库下载文件
    download_album(download_member)

    # 切换回原来的目录
    os.chdir(current_dir)

    # 自动检测 download 文件夹中最新的文件夹
    try:
        latest_folder = max([os.path.join(download_dir, d) for d in os.listdir(download_dir)], key=os.path.getmtime)
    except ValueError:
        await bot.api.post_group_msg(group_id=group_id, text="下载失败，未找到下载的文件")
        return

    # 将最新的文件夹内的 webp 文件转换成 pdf
    webp_files = [f for f in os.listdir(latest_folder) if f.endswith('.webp')]

    # 如果没有找到webp文件，尝试查找其他图片格式
    if not webp_files:
        image_files = [f for f in os.listdir(latest_folder) if f.endswith(('.jpg', '.jpeg', '.png', '.webp'))]
        if not image_files:
            await bot.api.post_group_msg(group_id=group_id, text="下载失败，未找到图片文件")
            return
        # 如果有其他格式的图片，使用它们
        webp_files = image_files

    pdf_path = os.path.join(latest_folder, f'{download_member}.pdf')

    try:
        # 使用更安全的方式创建PDF
        with WandImage() as pdf:
            images_added = False
            for webp_file in sorted(webp_files):  # 确保按顺序处理文件
                webp_path = os.path.join(latest_folder, webp_file)
                try:
                    # 检查文件是否存在且不为空
                    if os.path.exists(webp_path) and os.path.getsize(webp_path) > 0:
                        with WandImage(filename=webp_path) as img:
                            # 确保图像格式正确
                            img.format = 'pdf'
                            pdf.sequence.append(img)
                            images_added = True
                    else:
                        print(f"跳过空文件或不存在文件: {webp_path}")
                except Exception as e:
                    print(f"处理图片 {webp_file} 时出错: {e}")
                    continue

            # 只有在成功添加了图片时才保存PDF
            if images_added:
                pdf.save(filename=pdf_path)

                # 检查PDF文件是否成功创建
                if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
                    # 将 pdf 发送到检测到这个数字的 QQ 群
                    await bot.api.post_group_file(group_id=group_id, file=pdf_path)
                else:
                    await bot.api.post_group_msg(group_id=group_id, text="PDF转换失败，生成的文件为空")
            else:
                await bot.api.post_group_msg(group_id=group_id, text="没有有效的图片文件可以转换为PDF")

    except Exception as e:
        print(f"PDF转换错误: {e}")
        await bot.api.post_group_msg(group_id=group_id, text=f"PDF转换失败: {str(e)}")


def get_album_page_count(album_id):
    """获取本子的页数"""
    try:
        op = JmOption.default()
        cl = op.new_jm_client()

        # 获取专辑详情
        album_detail = cl.get_album_detail(album_id)

        # 返回页数
        return album_detail.page_count
    except Exception as e:
        print(f"获取本子 {album_id} 页数失败: {e}")
        return None





class First3ImageDownloader(JmDownloader):
    """自定义下载器，只下载前三张图片"""

    def __init__(self, album_id):
        super().__init__(option=JmOption.default())
        self.album_id = album_id
        self.image_data = []

    def download_album(self, album_id):
        # 重写下载方法，只下载前三张图片
        album = self.client.get_album_detail(album_id)

        # 应用过滤器
        filtered_album = self.do_filter(album)

        # 下载过滤后的专辑
        if filtered_album:
            self.download_album(filtered_album)

    def after_download(self, detail, filepath):
        # 重写下载后的处理，将图片数据保存到内存中
        if detail.is_photo():
            # 读取下载的图片数据
            with open(filepath, 'rb') as f:
                self.image_data.append(f.read())

            # 删除临时文件
            os.remove(filepath)


def get_ranking_top_three(ranking_type):
    """获取排行前三名"""
    op = JmOption.default()
    cl = op.new_jm_client()

    try:
        # 根据类型获取排行
        if ranking_type == "week":
            # 获取周榜
            ranking_data = cl.week_ranking(page=1)
            title = "本周排行"
        elif ranking_type == "month":
            # 获取月榜
            ranking_data = cl.month_ranking(page=1)
            title = "本月排行"
        else:
            return None, "未知的排行类型"

        # 获取前三名
        top_three = []
        count = 0

        # 遍历排行数据
        for album in ranking_data:
            if count >= 3:
                break

            # 处理元组格式 (album_id, title) 或对象格式
            if isinstance(album, tuple) and len(album) >= 2:
                album_id = album[0]
                album_title = album[1]
                top_three.append((album_id, album_title))
                count += 1
            elif hasattr(album, 'album_id') and hasattr(album, 'title'):
                album_id = album.album_id
                album_title = album.title
                top_three.append((album_id, album_title))
                count += 1

        return top_three, title
    except Exception as e:
        print(f"获取{ranking_type}排行失败: {e}")
        return None, f"获取{ranking_type}排行失败"


def get_tag_top_three(tag_name):
    """获取指定标签下排行前三的本子"""
    op = JmOption.default()
    cl = op.new_jm_client()

    try:
        # 使用 search_site 方法进行站内搜索
        # 这是官方文档示例中使用的方法
        search_result = cl.search_site(
            search_query=tag_name,
            page=1
        )

        # 或者使用更简单的 search_tag 方法
        # search_result = cl.search_tag(tag_name, page=1)

        # 获取前三名
        top_three = []
        count = 0

        # 遍历搜索结果
        # search_site 返回的是 JmSearchPage 对象，可以使用 iter_id_title 方法
        for album_id, title in search_result.iter_id_title():
            if count >= 3:
                break
            top_three.append((album_id, title))
            count += 1

        return top_three, tag_name
    except Exception as e:
        print(f"获取标签 '{tag_name}' 排行失败: {e}")
        return None, f"获取标签 '{tag_name}' 排行失败"
def get_random_album_id():
    """获取随机本子ID"""
    # 创建客户端
    client = JmOption.default().new_jm_client()

    # 尝试获取最新的本子ID
    try:
        # 获取最新的本子（通常是排行榜的第一个）
        latest_albums = client.week_ranking(page=1)
        if latest_albums:
            # 获取最新本子的ID
            if isinstance(latest_albums[0], tuple):
                latest_id = latest_albums[0][0]
            else:
                latest_id = latest_albums[0].album_id
        else:
            # 如果获取失败，使用一个较大的默认值
            latest_id = 1200000
    except:
        # 如果获取最新ID失败，使用一个较大的默认值
        latest_id = 1200000

    # 最老的本子ID，从1开始
    oldest_id = 1

    # 生成一个随机ID
    random_id = random.randint(oldest_id, latest_id)

    return str(random_id)


@bot.group_event()
async def on_group_message(msg: GroupMessage):
    try:
        blacklist = [4399, 666, 111, 1]  # 改为列表而不是字符串

        # 检测纯数字消息（本子ID）
        if msg.raw_message.isdigit() and int(msg.raw_message) not in blacklist:
            download_member = msg.raw_message

            # 获取本子页数
            page_count = get_album_page_count(download_member)

            # 发送识别到的本子信息 - 安全处理None值
            if page_count is not None:
                await bot.api.post_group_msg(
                    group_id=msg.group_id,
                    text=f"已识别到本子ID：{download_member}，共{page_count}页"
                )
            else:
                await bot.api.post_group_msg(
                    group_id=msg.group_id,
                    text=f"已识别到本子ID：{download_member}，正在获取本子信息..."
                )

            # 下载并发送本子
            await download_and_convert(msg.group_id, download_member)

        elif msg.raw_message == '随机本子':
            # 获取随机本子ID
            download_member = get_random_album_id()

            # 获取本子页数
            page_count = get_album_page_count(download_member)

            # 先发送随机本子信息 - 安全处理None值
            if page_count is not None:
                await bot.api.post_group_msg(
                    group_id=msg.group_id,
                    text=f"随机本子ID为：{download_member}，共{page_count}页"
                )
            else:
                await bot.api.post_group_msg(
                    group_id=msg.group_id,
                    text=f"随机本子ID为：{download_member}"
                )

            # 然后下载并发送本子
            await download_and_convert(msg.group_id, download_member)

        # 其他功能保持不变...
        elif msg.raw_message == '周排行':
            top_three, title = get_ranking_top_three("week")
            if not top_three:
                await bot.api.post_group_msg(group_id=msg.group_id, text="获取周排行失败，请稍后再试")
                return
            await bot.api.post_group_msg(group_id=msg.group_id, text=f"{title}前三名:")
            for i, (aid, album_title) in enumerate(top_three, 1):
                await bot.api.post_group_msg(group_id=msg.group_id, text=f"第{i}名: ID: {aid}, 标题: {album_title}")
                await asyncio.sleep(1)

        elif msg.raw_message == '月排行':
            top_three, title = get_ranking_top_three("month")
            if not top_three:
                await bot.api.post_group_msg(group_id=msg.group_id, text="获取月排行失败，请稍后再试")
                return
            await bot.api.post_group_msg(group_id=msg.group_id, text=f"{title}前三名:")
            for i, (aid, album_title) in enumerate(top_three, 1):
                await bot.api.post_group_msg(group_id=msg.group_id, text=f"第{i}名: ID: {aid}, 标题: {album_title}")
                await asyncio.sleep(1)

        elif msg.raw_message.startswith('tag：') or msg.raw_message.startswith('标签：'):
            tag_name = msg.raw_message[3:].strip() if msg.raw_message.startswith('标签：') else msg.raw_message[
                                                                                               4:].strip()

            if not tag_name:
                await bot.api.post_group_msg(group_id=msg.group_id, text="请提供标签名称，例如: tag：萝莉 或 标签：御姐")
                return

            top_three, tag_title = get_tag_top_three(tag_name)
            if not top_three:
                await bot.api.post_group_msg(group_id=msg.group_id,
                                             text=f"获取标签 '{tag_name}' 的排行失败，请检查标签名称是否正确")
                return

            await bot.api.post_group_msg(group_id=msg.group_id, text=f"标签 '{tag_name}' 排行前三名:")
            for i, (aid, album_title) in enumerate(top_three, 1):
                await bot.api.post_group_msg(group_id=msg.group_id, text=f"第{i}名: ID: {aid}, 标题: {album_title}")
                await asyncio.sleep(1)

    except JmcomicException as e:
        if "本子不存在" in str(e) or "MissingAlbumPhotoException" in str(type(e).__name__):
            await bot.api.post_group_msg(group_id=msg.group_id, text=f"本子不存在或ID错误")
        else:
            await bot.api.post_group_msg(group_id=msg.group_id, text=f"机器人出现问题: {str(e)}")
    except Exception as e:
        # 添加详细错误信息以便调试
        import traceback
        error_detail = traceback.format_exc()
        print(f"详细错误信息:\n{error_detail}")  # 打印到控制台
        await bot.api.post_group_msg(group_id=msg.group_id, text=f"发生未知错误: {str(e)}")



bot.run()
