import asyncio
from jmcomic import *

async def search(arg,pa=1):
  client = JmOption.default().new_jm_client()
  page: JmSearchPage = client.search_site(search_query=arg, page=pa)
  lines = [f'[{album_id}]: {title}\n' for album_id, title in page]
  mess = []
  for i in range(0, len(lines), 20):
      mess.append("".join(lines[i:i+20]))
  return mess


if __name__ == "__main__":
    print(asyncio.run(search("")))