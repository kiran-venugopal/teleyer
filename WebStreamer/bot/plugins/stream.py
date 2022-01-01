# This file is a part of TG-FileStreamBot
# Coding : Jyothis Jayanth [@EverythingSuckz]

from pyrogram import filters
from WebStreamer.vars import Var
from urllib.parse import quote_plus
from WebStreamer.bot import StreamBot
from pyrogram.types.messages_and_media import message
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from WebStreamer.db.config import get_database

def detect_type(m: Message):
    if m.document:
        return m.document
    elif m.video:
        return m.video
    elif m.audio:
        return m.audio
    else:
        return
    

@StreamBot.on_message(filters.document | filters.video | filters.audio, group=4)
async def media_receive_handler(_, m: Message):
    try:
       
        file = detect_type(m)
        file_name = ''
        if file:
            file_name = file.file_name
        log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)

        try:
            db = get_database()
            collection = db["messageids"]
            items = collection.find()
            [doc] = items
            mids_string = doc["mids"]
            mids_string = mids_string + "," +  str(log_msg.message_id)
            collection.update_one({'_id':doc['_id']}, {"$set":{"mids": mids_string}})
        except Exception as e: print(e)

        url=Var.URL
        if Var.CLIENT_URL:
            url=Var.CLIENT_URL
        file_path = str(log_msg.message_id) + '/' +quote_plus(file_name) if file_name else ''
        stream_link = url + file_path
        uploader_link = Var.GDRIVE_APP_URL + "?url=" + Var.HOST_URL + '/' + file_path
        await m.reply_text(
            text=file_name if file_name else '',
            quote=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Upload to Google Drive', url=uploader_link), InlineKeyboardButton('Play File', url=stream_link)]])
        )
    except:
        await m.reply_text(
            text= "Only Image, video, files are supported 📂! These type of messages not supported right now 😥"
        )