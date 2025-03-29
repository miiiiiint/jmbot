import jmcomic
import os
import yaml
from PIL import Image
from io import BytesIO
import shutil
import logging
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def load_config_async(config_file):
    try:
        load_config = await asyncio.to_thread(jmcomic.JmOption.from_file, config_file)
        with open(config_file, "r", encoding="utf8") as f:
            config_data = await asyncio.to_thread(yaml.load, f, Loader=yaml.FullLoader)
            base_dir = config_data["dir_rule"]["base_dir"]
        return load_config, base_dir
    except FileNotFoundError:
        logger.error(f"配置文件 '{config_file}' 未找到。")
        return None, None
    except Exception as e:
        logger.error(f"加载配置文件 '{config_file}' 失败: {e}")
        return None, None

async def download_album_async(manga_id, load_config):
    try:
        await asyncio.to_thread(jmcomic.download_album, manga_id, load_config)
        logger.info(f"漫画专辑 ID: {manga_id} 下载完成。")
        return True
    except Exception as e:
        logger.error(f"下载漫画专辑 ID: {manga_id} 失败: {e}")
        return False

async def open_image_async(file):
    try:
        img = await asyncio.to_thread(Image.open, file)
        return img
    except Exception as e:
        logger.error(f"打开图片文件 {file} 失败: {e}")
        return None

async def save_pdf_async(images, pdf_output_path, manga_id):
    try:
        if not images:
             logger.error(f"没有有效的图片列表传递给 save_pdf_async (漫画 ID: {manga_id})。")
             return False

        pdf_buffer = BytesIO()

        def save_action():
            images[0].save(
                pdf_buffer,
                "pdf",
                save_all=True,
                append_images=images[1:]
            )

        await asyncio.to_thread(save_action)

        def write_action():
            with open(pdf_output_path, "wb") as f:
                f.write(pdf_buffer.getvalue())

        await asyncio.to_thread(write_action)

        logger.info(f"漫画专辑 ID: {manga_id} 成功转换为 PDF，保存路径: {pdf_output_path}")
        return True
    except Exception as e:
        logger.error(f"创建 PDF 文件 {pdf_output_path} (漫画 ID: {manga_id}) 失败: {e}")
        return False

async def rmtree_async(manga_folder):
    try:
        await asyncio.to_thread(shutil.rmtree, manga_folder)
        logger.info(f"已删除下载的图片文件夹: {manga_folder}")
        return True
    except Exception as e:
        logger.error(f"删除图片文件夹 {manga_folder} 失败: {e}")
        return False

async def ipdf(manga_id: str, config_file: str = "config.yml"):
    load_config, base_dir = await load_config_async(config_file)
    if load_config is None or base_dir is None:
        return None

    try:
        await asyncio.to_thread(os.makedirs, base_dir, exist_ok=True)
    except Exception as e:
        logger.error(f"创建基础目录 {base_dir} 失败: {e}")
        return None

    logger.info(f"开始下载漫画专辑 ID: {manga_id}")
    if not await download_album_async(manga_id, load_config):
        return None

    manga_folder = os.path.join(base_dir, str(manga_id))

    if not await asyncio.to_thread(os.path.exists, manga_folder):
        logger.error(f"漫画文件夹 {manga_folder} 不存在。请检查下载路径或jmcomic的 `dir_rule` 配置。转换失败。")
        return None

    image_files = []
    try:
        for root, _, files in await asyncio.to_thread(os.walk, manga_folder):
            for file in files:
                if file.lower().endswith((".jpg", ".jpeg")):
                    image_files.append(os.path.join(root, file))
        image_files.sort()
    except Exception as e:
        logger.error(f"遍历漫画文件夹 {manga_folder} 时出错: {e}")
        return None

    if not image_files:
        logger.error(f"目录 {manga_folder} 中没有找到任何 JPG/JPEG 图片。")
        return None

    logger.info(f"在 {manga_folder} 中找到 {len(image_files)} 张图片，开始转换为 PDF。")

    simplified_pdf_name = "".join(c if c.isalnum() else "_" for c in str(manga_id))
    pdf_output_path = os.path.join(base_dir, simplified_pdf_name + ".pdf")

    images = []
    opened_images = []
    try:
        for file_path in image_files:
            img = await open_image_async(file_path)
            if img:
                opened_images.append(img)
                try:
                    rgb_img = await asyncio.to_thread(img.convert, "RGB")
                    images.append(rgb_img)
                except Exception as convert_err:
                    logger.warning(f"转换图片 {file_path} 到 RGB 时出错: {convert_err} - 跳过此图片。")
    finally:
        for img_obj in opened_images:
            try:
                await asyncio.to_thread(img_obj.close)
            except Exception as close_err:
                logger.warning(f"关闭图片对象时出错: {close_err}")

    if not images:
        logger.error(f"未能成功读取或转换任何有效的图片文件用于生成 PDF。")
        return None

    if not await save_pdf_async(images, pdf_output_path, manga_id):
        return None

    if not await rmtree_async(manga_folder):
        logger.warning(f"未能完全删除图片文件夹 {manga_folder}，但 PDF 已成功创建。")

    return os.path.abspath(pdf_output_path)

if __name__ == "__main__":
    config_file = "config.yml"
    if not os.path.exists(config_file):
        print(f"错误：配置文件 '{config_file}' 未找到。请确保此文件存在于脚本运行的目录下。")
        exit(1)

    manga_id = '490602'

    async def main():
        print(f"开始处理漫画 ID: {manga_id}")
        pdf_path = await ipdf(manga_id, config_file)

        print("-" * 30)
        if pdf_path:
            logger.info(f"任务成功完成!")
            logger.info(f"PDF 文件已保存在: {pdf_path}")
        else:
            logger.error(f"任务失败。未能为漫画 ID {manga_id} 创建 PDF。")
            logger.error(f"请检查上面的日志输出以获取详细错误信息。")
        print("-" * 30)

    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "cannot run event loop while another loop is running" in str(e):
             logger.warning("检测到已存在运行的事件循环。如果使用Jupyter Notebook等环境，请尝试安装并使用 `nest_asyncio`。")
        else:
            logger.exception("运行异步主函数时发生未处理的运行时错误:")
    except Exception as e:
        logger.exception("运行异步主函数时发生未处理的错误:")