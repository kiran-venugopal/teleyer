# Taken from megadlbot_oss <https://github.com/eyaadh/megadlbot_oss/blob/master/mega/webserver/routes.py>
# Thanks to Eyaadh <https://github.com/eyaadh>
import re
import time
import math
import logging
import secrets
import mimetypes
from aiohttp import web
from WebStreamer.vars import Var
from WebStreamer.bot import StreamBot
from WebStreamer import StartTime, __version__, bot_info
from WebStreamer.utils.time_format import get_readable_time
from WebStreamer.utils.custom_dl import TGCustomYield, chunk_size, offset_fix
import requests

routes = web.RouteTableDef()

@routes.post("/webhook/"+Var.BOT_TOKEN)
async def handle_webhook(request):
    try:
        req = await request.json()
        statusRes = requests.get(Var.HOST_URL)
        if statusRes.status_code != 200:
            print("-------no response from host-------")
            return
        data = statusRes.json()
        uptime = data['uptime']
        if (len(uptime) <= 3 and uptime[len(uptime) -1] == "s"):
            tel_api = "https://api.telegram.org/bot"+ Var.BOT_TOKEN; 
            chat_id = req['message']['chat']['id']
            message = "Sorry I was sleeping \xF0\x9F\x98\xB4! can you send the file again \xF0\x9F\x98\x8A"
            requests.get(tel_api+"/sendMessage?chat_id="+ str(chat_id) +"&text="+message)
            print("----bot was sleeping! send a request to wake up----")
            return
        else:
            print("-----bot is alive-----")
        return 
    except Exception as e:
        print("error in handling webhook!", e)
        return 


@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response({"server_status": "running",
                              "uptime": get_readable_time(time.time() - StartTime),
                              "telegram_bot": '@'+ bot_info.username,
                              "version": __version__})


@routes.get(r"/{message_id:\S+}")
async def stream_handler(request):
    try:
        message_id = request.match_info['message_id']
        message_id = int(re.search(r'(\d+)(?:\/\S+)?', message_id).group(1))
        return await media_streamer(request, message_id)
    except ValueError as e:
        logging.error(e)
        raise web.HTTPNotFound
    except AttributeError:
        pass



async def media_streamer(request, message_id: int):
    range_header = request.headers.get('Range', 0)
    media_msg = await StreamBot.get_messages(Var.BIN_CHANNEL, message_id)
    file_properties = await TGCustomYield().generate_file_properties(media_msg)
    file_size = file_properties.file_size

    if range_header:
        from_bytes, until_bytes = range_header.replace('bytes=', '').split('-')
        from_bytes = int(from_bytes)
        until_bytes = int(until_bytes) if until_bytes else file_size - 1
    else:
        from_bytes = request.http_range.start or 0
        until_bytes = request.http_range.stop or file_size - 1

    req_length = until_bytes - from_bytes

    new_chunk_size = await chunk_size(req_length)
    offset = await offset_fix(from_bytes, new_chunk_size)
    first_part_cut = from_bytes - offset
    last_part_cut = (until_bytes % new_chunk_size) + 1
    part_count = math.ceil(req_length / new_chunk_size)
    body = TGCustomYield().yield_file(media_msg, offset, first_part_cut, last_part_cut, part_count,
                                      new_chunk_size)

    file_name = file_properties.file_name if file_properties.file_name \
        else f"{secrets.token_hex(2)}.jpeg"
    mime_type = file_properties.mime_type if file_properties.mime_type \
        else f"{mimetypes.guess_type(file_name)}"

    return_resp = web.Response(
        status=206 if range_header else 200,
        body=body,
        headers={
            "Content-Type": mime_type,
            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
            "Content-Disposition": f'attachment; filename="{file_name}"',
            "Accept-Ranges": "bytes",
            "Access-Control-Allow-Origin": "*"
        }
    )

    if return_resp.status == 200:
        return_resp.headers.add("Content-Length", str(file_size))

    return return_resp