# This file is a part of TG-FileStreamBot
# Coding : Jyothis Jayanth [@EverythingSuckz]

from asyncio import constants
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
    print(m)
    try:
       
        file = detect_type(m)
        file_name = ''
        if file:
            file_name = file.file_name
        log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)

        try:
            user = {}
            from_user = m.from_user
            if from_user:
                user["username"] = from_user.username
                user["first_name"] = from_user.first_name
                user["last_name"] = from_user.last_name
                user["id"] = from_user.id
                user["phone_number"] = from_user.phone_number
                user["is_bot"] = from_user.is_bot
            

 
            db = get_database()
            collection = db["messageids"]
            items = collection.find()
            file_doc = {"fileId": log_msg.id, "fileName":file.file_name, "user": user }
            collection.insert_one(file_doc)
        except Exception as e: print(e)

        url=Var.URL
        if Var.CLIENT_URL:
            url=Var.CLIENT_URL
        file_path = str(log_msg.id) + '/' +quote_plus(file_name) if file_name else ''
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