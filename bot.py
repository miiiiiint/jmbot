import asyncio
import json
import logging
import re
from websockets.server import serve
from img2pdfr import *
from search import *

JM_CMD = re.compile(r"^/jm\s+(\d{1,9})$")
SEARCH_CMD = re.compile(r"^/s\s+(\S+?)\s+(\d{1,3})$")

def r(mt, e, a, p):
    params = {**p}
    if mt == "group":
        params["group_id"] = e["group_id"]
    else:
        params["user_id"] = e["user_id"]
    return {
        "action": a,
        "params": params
    }

async def handle_message(ws, path):
    async for msg in ws:
        try:
            e = json.loads(msg)
            if e.get("post_type") != "message":
                continue

            mt = e["message_type"]
            mtext = e["message"]
            logging.info(f"Msg: {e}")

            if jm_match := JM_CMD.match(mtext):
                q = jm_match[1]
                if mt == "group":
                    action_type = "send_group_msg"
                else:
                    action_type = "send_private_msg"
                await ws.send(json.dumps(r(mt, e, action_type, {"message": '下载中...'})))

                pdf_path = await ipdf(q)

                if mt == "group":
                    upload_action = "upload_group_file"
                else:
                    upload_action = "upload_private_file"

                if pdf_path:
                    await ws.send(json.dumps(r(mt, e, upload_action, {"file": pdf_path, 'name': f'{q}.pdf', 'floder': 'manga'})))
                else:
                    if mt == "group":
                        send_action_fail = "send_group_msg"
                    else:
                        send_action_fail = "send_private_msg"
                    await ws.send(json.dumps(r(mt, e, send_action_fail, {"message": '下载失败，或未开放'})))

            elif s_match := SEARCH_CMD.match(mtext):
                kw  = s_match[1]
                try:
                    page = int(s_match[2])
                except:
                    page = 1

                if mt == "group":
                    action_type_search_start = "send_group_msg"
                else:
                    action_type_search_start = "send_private_msg"
                await ws.send(json.dumps(r(mt, e, action_type_search_start, {"message": '搜索中...'})))

                if results := await search(kw, page):
                    fwd_msgs = [{
                        "type": "node",
                        "data": {
                            "user_id": 2438506194,
                            "nickname": 'cheater',
                            "content": [{"type": "text", "data": {"text": f'搜索结果，页{page}' if i==0 else msg}}]
                        }
                    } for i, msg in enumerate([""] + results)]
                    fwd_msgs[0]["data"]["content"][0]["data"]["text"] = f'搜索结果，页{page}'

                    if mt == "group":
                        action_type_forward = "send_group_forward_msg"
                    else:
                        action_type_forward = "send_private_forward_msg"
                    #这里lagrange和napcat构造转发消息的方式不同，请手动注释
                    #napcat
                    
                    await ws.send(json.dumps(r(mt, e,
                        action_type_forward,
                        {"messages": fwd_msgs, "prompt": f"搜索 {kw}"}
                    )))
                    
                    #lagrange
                    
                    # await ws.send(json.dumps(r(mt, e,
                    #    action_type_forward,
                    #    {"messages": fwd_msgs}
                    # )))
                elif results == []:
                    if mt == "group":
                        action_type_no_result = "send_group_msg"
                    else:
                        action_type_no_result = "send_private_msg"
                    await ws.send(json.dumps(r(mt, e, action_type_no_result, {"message": f'未找到 {kw} 的结果，页{page}'})))
                else:
                    if mt == "group":
                        action_type_no_result = "send_group_msg"
                    else:
                        action_type_no_result = "send_private_msg"
                    await ws.send(json.dumps(r(mt, e, action_type_no_result, {"message": f'未找到 {kw} 的结果'})))

        except Exception as err:
            logging.error(f"Error: {err}")

async def main():
    async with serve(handle_message, "0.0.0.0", 6700):
        await asyncio.Future()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())