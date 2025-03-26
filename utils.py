import asyncio
import os
from pathlib import Path
from jmcomic import *

async def download_to_pdf(manga_id):
  """异步下载漫画并转为 PDF，返回 PDF 路径或 None"""
  config_file = Path("config.yml")
  option = create_option_by_file(str(config_file))
  await asyncio.get_event_loop().run_in_executor(None, download_album, manga_id, option)
  pdf_path = Path("jm_data") / f"{manga_id}.pdf"
  return str(pdf_path.resolve()) if pdf_path.exists() else None

# 自动创建配置文件（如果不存在）
if not Path("config.yml").exists():
    with open("config.yml", "w", encoding="utf-8") as f:
        f.write(
            """dir_rule:
  base_dir: jm_data
plugins:
  after_photo:
    - plugin: img2pdf
      kwargs:
        pdf_dir: jm_data
        filename_rule: Pid
  
  after_album:
    - plugin: img2pdf
      kwargs:
        pdf_dir: jm_data
        filename_rule: Aid

download:
  cache: true 
  image:
    decode: true 
    suffix: .jpg 
  threading:

    batch_count: 45"""
        )


async def search(arg,pa=1):
  client = JmOption.default().new_jm_client()
  page: JmSearchPage = client.search_site(search_query=arg, page=pa)
  lines = [f'[{album_id}]: {title}\n' for album_id, title in page]
  mess = []
  for i in range(0, len(lines), 20):
      mess.append("".join(lines[i:i+20])) 
  return mess


  
# 测试代码
if __name__ == "__main__":
    print(asyncio.run(download_to_pdf("1112159")))
    print(asyncio.run(search("")))
    
