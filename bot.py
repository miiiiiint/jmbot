import asyncio
import json
import logging
import re
from websockets.server import serve
from utils import *

JM_CMD = re.compile(r"^/jm\s+(\d{1,9})$")  
SEARCH_CMD = re.compile(r"^/s\s+(\S+?)\s+(\d{1,3})$")  

def r(mt, e, a, p):
    return {
        "action": a,
        "params": {**p, "group_id" if mt == "group" else "user_id": e["group_id"] if mt == "group" else e["user_id"]}
    }

async def handle_message(ws, path):
    async for msg in ws:
        try:
            e = json.loads(msg)
            if e["post_type"] != "message":
                continue

            mt = e["message_type"]
            mtext = e["message"]
            logging.info(f"Msg: {e}")

            if jm_match := JM_CMD.match(mtext):
                q = jm_match[1]
                await ws.send(json.dumps(r(mt, e, "send_group_msg" if mt == "group" else "send_private_msg", {"message": '下载中...'})))
                pdf_path = await download_to_pdf(q)
                action = "upload_group_file" if mt == "group" else "upload_private_file"
                await ws.send(json.dumps(r(mt, e, action, {"file": pdf_path, 'name': f'{q}.pdf', 'floder': 'manga'} if pdf_path else {"message": '下载失败，或未开放'})))

            elif s_match := SEARCH_CMD.match(mtext):
                kw  = s_match[1]
                try:
                    page = int(s_match[2])
                except:
                    page = 1
                await ws.send(json.dumps(r(mt, e, "send_group_msg" if mt == "group" else "send_private_msg", {"message": '搜索中...'})))
                
                if results := await search(kw, page):
                    fwd_msgs = [{
                        "type": "node",
                        "data": {
                            "user_id": 2438506194,
                            "nickname": 'fool',
                            "content": [{"type": "text", "data": {"text": f'搜索结果，页{page}' if i==0 else msg}}]
                        }
                    } for i, msg in enumerate([""] + results)]
                    fwd_msgs[0]["data"]["content"][0]["data"]["text"] = f'搜索结果，页{page}'
                    
                    await ws.send(json.dumps(r(mt, e, 
                        "send_group_forward_msg" if mt == "group" else "send_private_forward_msg",
                        {"messages": fwd_msgs, "prompt": f"搜索 {kw}"}
                    )))
                else:
                    await ws.send(json.dumps(r(mt, e, "send_group_msg" if mt == "group" else "send_private_msg", {"message": f'未找到 {kw} 的结果'})))

        except Exception as err:
            logging.error(f"Error: {err}")

async def main():
    async with serve(handle_message, "0.0.0.0", 6700):
        await asyncio.Future()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())