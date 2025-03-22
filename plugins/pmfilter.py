# Owneer @hyoshcoder

import asyncio
import re
import ast
import math
import random
import pytz
from database.refer import referdb
from datetime import datetime, timedelta, date, time
lock = asyncio.Lock()
from database.users_chats_db import db
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import Script
script = Script
import pyrogram
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, make_inactive
from info import *
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, CallbackQuery, InputMediaPhoto
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import get_size, is_req_subscribed, get_poster, search_gagala, temp, get_settings, save_group_settings, get_shortlink, get_tutorial, send_all, get_cap
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results, get_bad_files
from database.filters_mdb import (
    del_all,
    find_filter,
    get_filters,
)
from database.gfilters_mdb import (
    find_gfilter,
    get_gfilters,
    del_allg
)
import logging
from urllib.parse import quote_plus
from util.file_properties import get_name, get_hash, get_media_file_size

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

import requests
import string
import tracemalloc
# Enable tracemalloc
tracemalloc.start()

TIMEZONE = "UTC"
BUTTON = {}
BUTTONS = {}
FRESH = {}
BUTTONS0 = {}
BUTTONS1 = {}
BUTTONS2 = {}
SPELL_CHECK = {}
FILTER_MODE = {}
REACTIONS = ["🔥", "❤️", "😍", "⚡"]
# ENABLE_SHORTLINK = ""

def generate_random_alphanumeric():
    """Generate a random 8-letter alphanumeric string."""
    characters = string.ascii_letters + string.digits
    random_chars = ''.join(random.choice(characters) for _ in range(8))
    return random_chars
  
def get_shortlink_sync(url):
    try:
        rget = requests.get(f"https://{STREAM_SITE}/api?api={STREAM_API}&url={url}&alias={generate_random_alphanumeric()}")
        rjson = rget.json()
        if rjson["status"] == "success" or rget.status_code == 200:
            return rjson["shortenedUrl"]
        else:
            return url
    except Exception as e:
        print(f"Error in get_shortlink_sync: {e}")
        return url

async def get_shortlink(url):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_shortlink_sync, url)


@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    if message.chat.id != SUPPORT_CHAT_ID:
        manual = await manual_filters(client, message)
        if manual == False:
            settings = await get_settings(message.chat.id)
            try:
                if settings['auto_ffilter']:
                    await auto_filter(client, message)
            except KeyError:
                grpid = await active_connection(str(message.from_user.id))
                await save_group_settings(grpid, 'auto_ffilter', True)
                settings = await get_settings(message.chat.id)
                if settings['auto_ffilter']:
                    await auto_filter(client, message) 
    else: # Une meilleure logique pour éviter les répétitions de code dans la fonction auto_filter
        search = message.text
        temp_files, temp_offset, total_results = await get_search_results(chat_id=message.chat.id, query=search.lower(), offset=0, filter=True)
        if total_results == 0:
            return
        else:
            return await message.reply_text(
                text=f"<b>ʜᴇʏ {message.from_user.mention}, {str(total_results)} ʀᴇ́sᴜʟᴛᴀᴛs ᴏɴᴛ ᴇ́ᴛᴇ́ ᴛʀᴏᴜᴠᴇ́s ᴅᴀɴs ᴍᴀ ʙᴀsᴇ ᴅᴇ ᴅᴏɴɴᴇ́ᴇs ᴘᴏᴜʀ ᴠᴏᴛʀᴇ ʀᴇᴄʜᴇʀᴄʜᴇ <code>{search}</code>. \n\nCᴇ ᴇsᴛ ᴜɴ ɢʀᴏᴜᴘᴇ ᴅᴇ sᴜᴘᴘᴏʀᴛ, ᴅᴏɴᴄ ᴠᴏᴜs ɴᴇ ᴘᴏᴜᴠᴇᴢ ᴘᴀs ᴏʙᴛᴇɴɪʀ ᴅᴇ ғɪᴄʜɪᴇʀs ɪᴄɪ...\n\nRᴇᴊᴏɪɢɴᴇᴢ-ɴᴏᴜs ᴇᴛ ғᴀɪᴛᴇs ᴠᴏᴛʀᴇ ʀᴇᴄʜᴇʀᴄʜᴇ ɪᴄɪ</b>",
                parse_mode=enums.ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(
                        [[
                            InlineKeyboardButton('• Rᴇᴊᴏɪɢɴᴇᴢ ɴᴏᴛʀᴇ ɢʀᴏᴜᴘᴇ ᴅᴇ ғɪʟᴍs •', url ='https://telegram.me/BingeFinderclub')
                        ]]
                    )
                )

@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_text(bot, message):
    content = message.text
    user = message.from_user.first_name
    user_id = message.from_user.id
    if content.startswith("/") or content.startswith("#"): return  # Ignorer les commandes et les hashtags
    if user_id in ADMINS: return # Ignorer les admins
    await message.reply_text(
         text="<b>ʜᴇʏ ʙʀᴏ/sɪs, ᴛᴜ ɴᴇ ᴘᴇᴜx ᴘᴀs ᴏʙᴛᴇɴɪʀ �ᴇ ғɪᴄʜɪᴇʀs ɪᴄɪ... \n\nRᴇᴊᴏɪɴs ɴᴏᴛʀᴇ ɢʀᴏᴜᴘᴇ ᴇᴛ ғᴀɪᴛs ᴛᴀ ʀᴇᴄʜᴇʀᴄʜᴇ ɪᴄɪ</b>",   
         reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("• Rᴇᴊᴏɪɴs ɴᴏᴛʀᴇ ɢʀᴏᴜᴘᴇ ᴅᴇ ғɪʟᴍs • ​ ", url=f"https://telegram.me/BingeFinderclub")]]), disable_web_page_preview=True
    )
    await bot.send_message(
        chat_id=LOG_CHANNEL,
        text=f"<b>#𝐌𝐄𝐒𝐒𝐀𝐆𝐄\n\nNᴏᴍ : {user}\n\nID : {user_id}\n\nMᴇssᴀɢᴇ : {content}</b>"
    )
    
@Client.on_callback_query(filters.regex(r"^reffff"))
async def refercall(bot, query):
    btn = [[
        InlineKeyboardButton('• ᴘᴀʀᴛᴀɢᴇʀ ʟᴇ ʟɪᴇɴ', url=f'https://telegram.me/share/url?url=https://t.me/{bot.me.username}?start=reff_{query.from_user.id}&text=Bonjour%21%20Découvrez%20un%20bot%20qui%20propose%20une%20vaste%20bibliothèque%20de%20films%20et%20séries%20illimités.%20%F0%9F%98%83'),
        InlineKeyboardButton(f'⏳ {referdb.get_refer_points(query.from_user.id)}', callback_data='ref_point'),
        InlineKeyboardButton('ʀᴇᴛᴏᴜʀ •', callback_data='start')
    ]]
    reply_markup = InlineKeyboardMarkup(btn)
    await bot.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto("https://graph.org/file/1a2e64aee3d4d10edd930.jpg")
        )
    await query.message.edit_text(
        text=f'<b>» ᴠᴏᴛʀᴇ ʟɪᴇɴ ᴅᴇ ᴘᴀʀʀᴀɪɴᴀɢᴇ :\n\nhttps://t.me/{bot.me.username}?start=reff_{query.from_user.id}\n\nᴘᴀʀᴛᴀɢᴇᴢ ᴄᴇ ʟɪᴇɴ ᴀᴠᴇᴄ ᴠᴏs ᴀᴍɪs, ᴘᴏᴜʀ ᴄʜᴀϙᴜᴇ ᴘᴇʀsᴏɴɴᴇ ϙᴜɪ ʀᴇᴊᴏɪɴᴛ, ᴠᴏᴜs ᴏʙᴛɪᴇɴᴅʀᴇᴢ 𝟷𝟶 ᴘᴏɪɴᴛs ᴅᴇ ᴘᴀʀʀᴀɪɴᴀɢᴇ. ᴀᴘʀᴇ̀s ᴀᴠᴏɪʀ ᴀᴛᴛᴇɪɴᴛ 𝟷𝟶𝟶 ᴘᴏɪɴᴛs, ᴠᴏᴜs ʀᴇᴄᴇᴠʀᴇᴢ ᴜɴ ᴀʙᴏɴɴᴇᴍᴇɴᴛ ᴘʀᴇ́ᴍɪᴜᴍ ᴅᴇ 𝟷 ᴍᴏɪs.</b>',
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
        )
    await query.answer()

@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    curr_time = datetime.now(pytz.timezone('Africa/kinshasa')).time()
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    if BUTTONS.get(key)!=None:
        search = BUTTONS.get(key)
    else:
        search = FRESH.get(key)
    if not search:
        await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name),show_alert=True)
        return

    files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    temp.GETALL[key] = files
    temp.SHORT[query.from_user.id] = query.message.chat.id
    settings = await get_settings(query.message.chat.id)
    pre = 'filep' if settings['file_secure'] else 'file'
    if settings['button']:
        btn = [
            [
                InlineKeyboardButton(
                    text=f" {get_size(file.file_size)}  {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'), file.file_name.split()))}", callback_data=f'{pre}#{file.file_id}'
                ),
            ]
            for file in files
        ]


        btn.insert(0, 
            [
                InlineKeyboardButton("⇈ Sélectionnez les options ici ⇈", 'reqinfo')
            ]
        )
        btn.insert(0, 
            [
                InlineKeyboardButton(f'ǫᴜᴀʟɪᴛᴇ́', callback_data=f"qualities#{key}"),
                InlineKeyboardButton("ʟᴀɴɢᴜᴇ", callback_data=f"languages#{key}"),
                InlineKeyboardButton("ꜱᴀɪsᴏɴ",  callback_data=f"seasons#{key}")
            ]
        )
        btn.insert(0, [
            InlineKeyboardButton("ᴘʀᴇᴍɪᴜᴍ", url=f"https://t.me/hyoshcoder"),
            InlineKeyboardButton("ᴇɴᴠᴏʏᴇʀ ᴛᴏᴜᴛ", callback_data=f"sendfiles#{key}")
        ])

    else:
        btn = []
        btn.insert(0, 
            [
                InlineKeyboardButton("⇈ Sélectionnez les options ici ⇈", 'reqinfo')
            ]
        )
        btn.insert(0, 
            [
                InlineKeyboardButton(f'ǫᴜᴀʟɪᴛᴇ́', callback_data=f"qualities#{key}"),
                InlineKeyboardButton("ʟᴀɴɢᴜᴇ", callback_data=f"languages#{key}"),
                InlineKeyboardButton("ꜱᴀɪsᴏɴ",  callback_data=f"seasons#{key}")
            ]
        )
        btn.insert(0, [
            InlineKeyboardButton("ᴘʀᴇᴍɪᴜᴍ", url=f"https://t.me/hyoshcoder"),
            InlineKeyboardButton("ᴇɴᴠᴏʏᴇʀ ᴛᴏᴜᴛ", callback_data=f"sendfiles#{key}")
        ])

    try:
        if settings['max_btn']:
            if 0 < offset <= 10:
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - 10
            if n_offset == 0:
                btn.append(
                    [InlineKeyboardButton("⋞ ʀᴇᴛᴏᴜʀ", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages")]
                )
            elif off_set is None:
                btn.append([InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"), InlineKeyboardButton("ꜱᴜɪᴠᴀɴᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")])
            else:
                btn.append(
                    [
                        InlineKeyboardButton("⋞ ʀᴇᴛᴏᴜʀ", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
                        InlineKeyboardButton("ꜱᴜɪᴠᴀɴᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")
                    ],
                )
        else:
            if 0 < offset <= int(MAX_B_TN):
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - int(MAX_B_TN)
            if n_offset == 0:
                btn.append(
                    [InlineKeyboardButton("⋞ ʀᴇᴛᴏᴜʀ", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages")]
                )
            elif off_set is None:
                btn.append([InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"), InlineKeyboardButton("ꜱᴜɪᴠᴀɴᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")])
            else:
                btn.append(
                    [
                        InlineKeyboardButton("⋞ ʀᴇᴛᴏᴜʀ", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"),
                        InlineKeyboardButton("ꜱᴜɪᴠᴀɴᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")
                    ],
                )
    except KeyError:
        await save_group_settings(query.message.chat.id, 'max_btn', True)
        if 0 < offset <= 10:
            off_set = 0
        elif offset == 0:
            off_set = None
        else:
            off_set = offset - 10
        if n_offset == 0:
            btn.append(
                [InlineKeyboardButton("⋞ ʀᴇᴛᴏᴜʀ", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages")]
            )
        elif off_set is None:
            btn.append([InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"), InlineKeyboardButton("ꜱᴜɪᴠᴀɴᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")])
        else:
            btn.append(
                [
                    InlineKeyboardButton("⋞ ʀᴇᴛᴏᴜʀ", callback_data=f"next_{req}_{key}_{off_set}"),
                    InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
                    InlineKeyboardButton("ꜱᴜɪᴠᴀɴᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")
                ],
            )
    if not settings["button"]:
        cur_time = datetime.now(pytz.timezone('Africa/kinshasa')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        cap = await get_cap(settings, remaining_seconds, files, query, total, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(btn)
            )
        except MessageNotModified:
            pass
    await query.answer()
    
@Client.on_callback_query(filters.regex(r"^spol"))
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    movies = SPELL_CHECK.get(query.message.reply_to_message.id)
    if not movies:
        return await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movie = movies[(int(movie_))]
    movie = re.sub(r"[:\-]", " ", movie)
    movie = re.sub(r"\s+", " ", movie).strip()
    await query.answer(script.TOP_ALRT_MSG)
    gl = await global_filters(bot, query.message, text=movie)
    if gl == False:
        k = await manual_filters(bot, query.message, text=movie)
        if k == False:
            files, offset, total_results = await get_search_results(query.message.chat.id, movie, offset=0, filter=True)
            if files:
                k = (movie, files, offset, total_results)
                await auto_filter(bot, query, k)
            else:
                reqstr1 = query.from_user.id if query.from_user else 0
                reqstr = await bot.get_users(reqstr1)
                if NO_RESULTS_MSG:
                    await bot.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, movie)))
                k = await query.message.edit(script.MVE_NT_FND)
                await asyncio.sleep(10)
                await k.delete()
#Qualities 
@Client.on_callback_query(filters.regex(r"^qualities#"))
async def qualities_cb_handler(client: Client, query: CallbackQuery):

    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʙᴏɴᴊᴏᴜʀ {query.from_user.first_name},\nᴄᴇᴄɪ ɴ'ᴇꜱᴛ ᴘᴀꜱ ᴠᴏᴛʀᴇ ᴅᴇᴍᴀɴᴅᴇ ᴅᴇ ꜰɪʟᴍ,\nꜰᴀɪᴛᴇꜱ ᴠᴏᴛʀᴇ ᴘʀᴏᴘʀᴇ ᴅᴇᴍᴀɴᴅᴇ...",
                show_alert=True,
            )
    except:
        pass
    _, key = query.data.split("#")
    # if BUTTONS.get(key+"1")!=None:
    #     search = BUTTONS.get(key+"1")
    # else:
    #     search = BUTTONS.get(key)
    #     BUTTONS[key+"1"] = search
    search = FRESH.get(key)
    search = search.replace(' ', '_')
    btn = []
    for i in range(0, len(QUALITIES)-1, 2):
        btn.append([
            InlineKeyboardButton(
                text=QUALITIES[i].title(),
                callback_data=f"fq#{QUALITIES[i].lower()}#{key}"
            ),
            InlineKeyboardButton(
                text=QUALITIES[i+1].title(),
                callback_data=f"fq#{QUALITIES[i+1].lower()}#{key}"
            ),
        ])

    btn.insert(
        0,
        [
            InlineKeyboardButton(
                text="⇊ Sélectionnez la qualité ⇊", callback_data="ident"
            )
        ],
    )
    req = query.from_user.id
    offset = 0
    btn.append([InlineKeyboardButton(text="↭ ʀᴇᴛᴏᴜʀ ᴀᴜx ꜰɪᴄʜɪᴇʀꜱ ↭", callback_data=f"fq#homepage#{key}")])

    await query.edit_message_reply_markup(InlineKeyboardMarkup(btn))
    

@Client.on_callback_query(filters.regex(r"^fq#"))
async def filter_qualities_cb_handler(client: Client, query: CallbackQuery):
    _, qual, key = query.data.split("#")
    curr_time = datetime.now(pytz.timezone('Africa/kinshasa')).time()
    search = FRESH.get(key)
    search = search.replace("_", " ")
    baal = qual in search
    if baal:
        search = search.replace(qual, "")
    else:
        search = search
    req = query.from_user.id
    chat_id = query.message.chat.id
    message = query.message
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʙᴏɴᴊᴏᴜʀ {query.from_user.first_name},\nᴄᴇᴄɪ ɴ'ᴇꜱᴛ ᴘᴀꜱ ᴠᴏᴛʀᴇ ᴅᴇᴍᴀɴᴅᴇ ᴅᴇ ꜰɪʟᴍ,\nꜰᴀɪᴛᴇꜱ ᴠᴏᴛʀᴇ ᴘʀᴏᴘʀᴇ ᴅᴇᴍᴀɴᴅᴇ...",
                show_alert=True,
            )
    except:
        pass
    if qual != "homepage":
        search = f"{search} {qual}" 
    BUTTONS[key] = search

    files, offset, total_results = await get_search_results(chat_id, search, offset=0, filter=True)
    if not files:
        await query.answer("ᴀᴜᴄᴜɴ ꜰɪᴄʜɪᴇʀ ᴛʀᴏᴜᴠᴇ́", show_alert=1)
        return
    temp.GETALL[key] = files
    settings = await get_settings(message.chat.id)
    pre = 'filep' if settings['file_secure'] else 'file'
    if settings["button"]:
        btn = [
            [
                InlineKeyboardButton(
                    text=f" {get_size(file.file_size)} {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'), file.file_name.split()))}", callback_data=f'{pre}#{file.file_id}'
                ),
            ]
            for file in files
        ]
        btn.insert(0, 
            [
                InlineKeyboardButton("⇈ Sélectionnez les options ici ⇈", 'reqinfo')
            ]
        )
        btn.insert(0, 
            [
                InlineKeyboardButton(f'ǫᴜᴀʟɪᴛᴇ́', callback_data=f"qualities#{key}"),
                InlineKeyboardButton("ʟᴀɴɢᴜᴇ", callback_data=f"languages#{key}"),
                InlineKeyboardButton("ꜱᴀɪsᴏɴ",  callback_data=f"seasons#{key}")
            ]
        )
        btn.insert(0, [
            InlineKeyboardButton("ᴘʀᴇᴍɪᴜᴍ", url=f"https://t.me/hyoshcoder"),
            InlineKeyboardButton("ᴇɴᴠᴏʏᴇʀ ᴛᴏᴜᴛ", callback_data=f"sendfiles#{key}")
        ])

    else:
        btn = []
        btn.insert(0, 
            [
                InlineKeyboardButton("⇈ Sélectionnez les options ici ⇈", 'reqinfo')
            ]
        )
        btn.insert(0, 
            [
                InlineKeyboardButton(f'ǫᴜᴀʟɪᴛᴇ́', callback_data=f"qualities#{key}"),
                InlineKeyboardButton("ʟᴀɴɢᴜᴇ", callback_data=f"languages#{key}"),
                InlineKeyboardButton("ꜱᴀɪsᴏɴ",  callback_data=f"seasons#{key}")
            ]
        )
        btn.insert(0, [
            InlineKeyboardButton("ᴘʀᴇᴍɪᴜᴍ", url=f"https://t.me/hyoshcoder"),
            InlineKeyboardButton("ᴇɴᴠᴏʏᴇʀ ᴛᴏᴜᴛ", callback_data=f"sendfiles#{key}")
        ])

    if offset != "":
        try:
            if settings['max_btn']:
                btn.append(
                    [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="ꜱᴜɪᴠᴀɴᴛ ⋟",callback_data=f"next_{req}_{key}_{offset}")]
                )
    
            else:
                btn.append(
                    [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="ꜱᴜɪᴠᴀɴᴛ ⋟",callback_data=f"next_{req}_{key}_{offset}")]
                )
        except KeyError:
            await save_group_settings(query.message.chat.id, 'max_btn', True)
            btn.append(
                [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="ꜱᴜɪᴠᴀɴᴛ ⋟",callback_data=f"next_{req}_{key}_{offset}")]
            )
    else:
        btn.append(
            [InlineKeyboardButton(text="↭ ᴘʟᴜꜱ ᴅᴇ ᴘᴀɢᴇꜱ ᴅɪꜱᴘᴏɴɪʙʟᴇꜱ ↭",callback_data="pages")]
        )
    
    if not settings["button"]:
        cur_time = datetime.now(pytz.timezone('Africa/kinshasa')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        cap = await get_cap(settings, remaining_seconds, files, query, total_results, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(btn)
            )
        except MessageNotModified:
            pass
    await query.answer()
    
#languages

@Client.on_callback_query(filters.regex(r"^languages#"))
async def languages_cb_handler(client: Client, query: CallbackQuery):
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʙᴏɴᴊᴏᴜʀ {query.from_user.first_name},\nᴄᴇᴄɪ ɴ'ᴇꜱᴛ ᴘᴀꜱ ᴠᴏᴛʀᴇ ᴅᴇᴍᴀɴᴅᴇ ᴅᴇ ꜰɪʟᴍ,\nꜰᴀɪᴛᴇꜱ ᴠᴏᴛʀᴇ ᴘʀᴏᴘʀᴇ ᴅᴇᴍᴀɴᴅᴇ...",
                show_alert=True,
            )
    except:
        pass
    _, key = query.data.split("#")
    # if BUTTONS.get(key+"1")!=None:
    #     search = BUTTONS.get(key+"1")
    # else:
    #     search = BUTTONS.get(key)
    #     BUTTONS[key+"1"] = search
    search = FRESH.get(key)
    search = search.replace(' ', '_')
    btn = []
    for i in range(0, len(LANGUAGES)-1, 2):
        btn.append([
            InlineKeyboardButton(
                text=LANGUAGES[i].title(),
                callback_data=f"fl#{LANGUAGES[i].lower()}#{key}"
            ),
            InlineKeyboardButton(
                text=LANGUAGES[i+1].title(),
                callback_data=f"fl#{LANGUAGES[i+1].lower()}#{key}"
            ),
        ])

    btn.insert(
        0,
        [
            InlineKeyboardButton(
                text="⇊ Sélectionnez la langue ⇊", callback_data="ident"
            )
        ],
    )
    req = query.from_user.id
    offset = 0
    btn.append([InlineKeyboardButton(text="↭ ʀᴇᴛᴏᴜʀ ᴀᴜx ꜰɪᴄʜɪᴇʀꜱ ​↭", callback_data=f"fl#homepage#{key}")])

    await query.edit_message_reply_markup(InlineKeyboardMarkup(btn))
      

@Client.on_callback_query(filters.regex(r"^fl#"))
async def filter_languages_cb_handler(client: Client, query: CallbackQuery):
    _, lang, key = query.data.split("#")
    curr_time = datetime.now(pytz.timezone('Africa/kinshasa')).time()
    search = FRESH.get(key)
    search = search.replace("_", " ")
    baal = lang in search
    if baal:
        search = search.replace(lang, "")
    else:
        search = search
    req = query.from_user.id
    chat_id = query.message.chat.id
    message = query.message
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʙᴏɴᴊᴏᴜʀ {query.from_user.first_name},\nᴄᴇᴄɪ ɴ'ᴇꜱᴛ ᴘᴀꜱ ᴠᴏᴛʀᴇ ᴅᴇᴍᴀɴᴅᴇ ᴅᴇ ꜰɪʟᴍ,\nꜰᴀɪᴛᴇꜱ ᴠᴏᴛʀᴇ ᴘʀᴏᴘʀᴇ ᴅᴇᴍᴀɴᴅᴇ...",
                show_alert=True,
            )
    except:
        pass
    if lang != "homepage":
        search = f"{search} {lang}" 
    BUTTONS[key] = search

    files, offset, total_results = await get_search_results(chat_id, search, offset=0, filter=True)
    if not files:
        await query.answer("ᴀᴜᴄᴜɴ ꜰɪᴄʜɪᴇʀ ᴛʀᴏᴜᴠᴇ́", show_alert=1)
        return
    temp.GETALL[key] = files
    settings = await get_settings(message.chat.id)
    pre = 'filep' if settings['file_secure'] else 'file'
    if settings["button"]:
        btn = [
            [
                InlineKeyboardButton(
                    text=f" {get_size(file.file_size)}  {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'), file.file_name.split()))}", callback_data=f'{pre}#{file.file_id}'
                ),
            ]
            for file in files
        ]
        btn.insert(0, 
            [
                InlineKeyboardButton("⇈ Sélectionnez les options ici ⇈", 'reqinfo')
            ]
        )
        btn.insert(0, 
            [
                InlineKeyboardButton(f'ǫᴜᴀʟɪᴛᴇ́', callback_data=f"qualities#{key}"),
                InlineKeyboardButton("ʟᴀɴɢᴜᴇ", callback_data=f"languages#{key}"),
                InlineKeyboardButton("ꜱᴀɪsᴏɴ",  callback_data=f"seasons#{key}")
            ]
        )
        btn.insert(0, [
            InlineKeyboardButton("ᴘʀᴇᴍɪᴜᴍ", url=f"https://t.me/hyoshcoder"),
            InlineKeyboardButton("ᴇɴᴠᴏʏᴇʀ ᴛᴏᴜᴛ", callback_data=f"sendfiles#{key}")
        ])

    else:
        btn = []
        btn.insert(0, 
            [
                InlineKeyboardButton("⇈ Sélectionnez les options ici ⇈", 'reqinfo')
            ]
        )
        btn.insert(0, 
            [
                InlineKeyboardButton(f'ǫᴜᴀʟɪᴛᴇ́', callback_data=f"qualities#{key}"),
                InlineKeyboardButton("ʟᴀɴɢᴜᴇ", callback_data=f"languages#{key}"),
                InlineKeyboardButton("ꜱᴀɪsᴏɴ",  callback_data=f"seasons#{key}")
            ]
        )
        btn.insert(0, [
            InlineKeyboardButton("ᴘʀᴇᴍɪᴜᴍ", url=f"https://t.me/hyoshcoder"),
            InlineKeyboardButton("ᴇɴᴠᴏʏᴇʀ ᴛᴏᴜᴛ", callback_data=f"sendfiles#{key}")
        ])

    if offset != "":
        try:
            if settings['max_btn']:
                btn.append(
                    [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="ꜱᴜɪᴠᴀɴᴛ ⋟",callback_data=f"next_{req}_{key}_{offset}")]
                )
    
            else:
                btn.append(
                    [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="ꜱᴜɪᴠᴀɴᴛ ⋟",callback_data=f"next_{req}_{key}_{offset}")]
                )
        except KeyError:
            await save_group_settings(query.message.chat.id, 'max_btn', True)
            btn.append(
                [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="ꜱᴜɪᴠᴀɴᴛ ⋟",callback_data=f"next_{req}_{key}_{offset}")]
            )
    else:
        btn.append(
            [InlineKeyboardButton(text="↭ ᴘʟᴜꜱ ᴅᴇ ᴘᴀɢᴇꜱ ᴅɪꜱᴘᴏɴɪʙʟᴇꜱ ↭",callback_data="pages")]
        )
    
    if not settings["button"]:
        cur_time = datetime.now(pytz.timezone('Africa/kinshasa')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        cap = await get_cap(settings, remaining_seconds, files, query, total_results, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(btn)
            )
        except MessageNotModified:
            pass
    await query.answer()  
    
    
@Client.on_callback_query(filters.regex(r"^seasons#"))
async def seasons_cb_handler(client: Client, query: CallbackQuery):
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʙᴏɴᴊᴏᴜʀ {query.from_user.first_name},\nᴄᴇᴄɪ ɴ'ᴇꜱᴛ ᴘᴀꜱ ᴠᴏᴛʀᴇ ᴅᴇᴍᴀɴᴅᴇ ᴅᴇ ꜰɪʟᴍ,\nꜰᴀɪᴛᴇꜱ ᴠᴏᴛʀᴇ ᴘʀᴏᴘʀᴇ ᴅᴇᴍᴀɴᴅᴇ...",
                show_alert=True,
            )
    except:
        pass
    _, key = query.data.split("#")
    # if BUTTONS.get(key+"2")!=None:
    #     search = BUTTONS.get(key+"2")
    # else:
    #     search = BUTTONS.get(key)
    #     BUTTONS[key+"2"] = search
    search = FRESH.get(key)
    BUTTONS[key] = None
    search = search.replace(' ', '_')
    btn = []
    for i in range(0, len(SEASONS)-1, 2):
        btn.append([
            InlineKeyboardButton(
                text=SEASONS[i].title(),
                callback_data=f"fs#{SEASONS[i].lower()}#{key}"
            ),
            InlineKeyboardButton(
                text=SEASONS[i+1].title(),
                callback_data=f"fs#{SEASONS[i+1].lower()}#{key}"
            ),
        ])

    btn.insert(
        0,
        [
            InlineKeyboardButton(
                text="⇊ Sélectionnez la saison ⇊", callback_data="ident"
            )
        ],
    )
    req = query.from_user.id
    offset = 0
    btn.append([InlineKeyboardButton(text="↭ ʀᴇᴛᴏᴜʀ ᴀᴜx ꜰɪᴄʜɪᴇʀꜱ ​↭", callback_data=f"next_{req}_{key}_{offset}")])

    await query.edit_message_reply_markup(InlineKeyboardMarkup(btn))

@Client.on_callback_query(filters.regex(r"^fs#"))
async def filter_seasons_cb_handler(client: Client, query: CallbackQuery):
    _, seas, key = query.data.split("#")
    curr_time = datetime.now(pytz.timezone('Africa/kinshasa')).time()
    search = FRESH.get(key)
    search = search.replace("_", " ")
    sea = ""
    season_search = [
        "s01","s02", "s03", "s04", "s05", "s06", "s07", "s08", "s09", "s10", 
        "season 01","season 02","season 03","season 04","season 05","season 06","season 07","season 08","season 09","season 10", 
        "season 1","season 2","season 3","season 4","season 5","season 6","season 7","season 8","season 9", "season 10",  
        "saison 1", "saison 2", "saison 3", "saison 4", "saison 5", "saison 6", "saison 7", "saison 8","saison 9","saison 10",]
    for x in range (len(season_search)):
        if season_search[x] in search:
            sea = season_search[x]
            break
    if sea:
        search = search.replace(sea, "")
    else:
        search = search
    
    req = query.from_user.id
    chat_id = query.message.chat.id
    message = query.message
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʙᴏɴᴊᴏᴜʀ {query.from_user.first_name},\nᴄᴇᴄɪ ɴ'ᴇꜱᴛ ᴘᴀꜱ ᴠᴏᴛʀᴇ ᴅᴇᴍᴀɴᴅᴇ ᴅᴇ ꜰɪʟᴍ,\nꜰᴀɪᴛᴇꜱ ᴠᴏᴛʀᴇ ᴘʀᴏᴘʀᴇ ᴅᴇᴍᴀɴᴅᴇ...",
                show_alert=True,
            )
    except:
        pass
    
    searchagn = search
    search1 = search
    search2 = search
    search = f"{search} {seas}"
    BUTTONS0[key] = search
    
    files, _, _ = await get_search_results(chat_id, search, max_results=10)
    files = [file for file in files if re.search(seas, file.file_name, re.IGNORECASE)]
    
    seas1 = "s01" if seas == "season 1" else "s02" if seas == "season 2" else "s03" if seas == "season 3" else "s04" if seas == "season 4" else "s05" if seas == "season 5" else "s06" if seas == "season 6" else "s07" if seas == "season 7" else "s08" if seas == "season 8" else "s09" if seas == "season 9" else "s10" if seas == "season 10" else ""
    search1 = f"{search1} {seas1}"
    BUTTONS1[key] = search1
    files1, _, _ = await get_search_results(chat_id, search1, max_results=10)
    files1 = [file for file in files1 if re.search(seas1, file.file_name, re.IGNORECASE)]
    
    if files1:
        files.extend(files1)
    
    seas2 = "season 01" if seas == "season 1" else "season 02" if seas == "season 2" else "season 03" if seas == "season 3" else "season 04" if seas == "season 4" else "season 05" if seas == "season 5" else "season 06" if seas == "season 6" else "season 07" if seas == "season 7" else "season 08" if seas == "season 8" else "season 09" if seas == "season 9" else "s010"
    search2 = f"{search2} {seas2}"
    BUTTONS2[key] = search2
    files2, _, _ = await get_search_results(chat_id, search2, max_results=10)
    files2 = [file for file in files2 if re.search(seas2, file.file_name, re.IGNORECASE)]

    if files2:
        files.extend(files2)
        
    if not files:
        await query.answer("ᴀᴜᴄᴜɴ ꜰɪᴄʜɪᴇʀ ᴛʀᴏᴜᴠᴇ́", show_alert=1)
        return
    temp.GETALL[key] = files
    settings = await get_settings(message.chat.id)
    pre = 'filep' if settings['file_secure'] else 'file'
    if settings["button"]:
        btn = [
            [
                InlineKeyboardButton(
                    text=f" {get_size(file.file_size)}  {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'), file.file_name.split()))}", callback_data=f'{pre}#{file.file_id}'
                ),
            ]
            for file in files
        ]
        btn.insert(0, [
            InlineKeyboardButton("ᴇɴᴠᴏʏᴇʀ ᴛᴏᴜᴛ", callback_data=f"sendfiles#{key}"),
            InlineKeyboardButton("ꜱᴇʟᴇᴄᴛɪᴏɴɴᴇᴢ ᴀ̀ ɴᴏᴜᴠᴇᴀᴜ", callback_data=f"seasons#{key}")
        ])
    else:
        btn = []
        btn.insert(0, 
            [
                InlineKeyboardButton("⇈ Sélectionnez les options ici ⇈", 'reqinfo')
            ]
        )
        btn.insert(0, 
            [
                InlineKeyboardButton(f'ǫᴜᴀʟɪᴛᴇ́', callback_data=f"qualities#{key}"),
                InlineKeyboardButton("ʟᴀɴɢᴜᴇ", callback_data=f"languages#{key}"),
                InlineKeyboardButton("ꜱᴀɪsᴏɴ",  callback_data=f"seasons#{key}")
            ]
        )
        btn.insert(0, [
            InlineKeyboardButton("ᴘʀᴇᴍɪᴜᴍ", url=f"https://t.me/hyoshcoder"),
            InlineKeyboardButton("ᴇɴᴠᴏʏᴇʀ ᴛᴏᴜᴛ", callback_data=f"sendfiles#{key}")
        ])
    
    offset = 0

    btn.append([
            InlineKeyboardButton(
                text="↭ ʀᴇᴛᴏᴜʀ ᴀᴜx ꜰɪᴄʜɪᴇʀꜱ ​↭",
                callback_data=f"next_{req}_{key}_{offset}"
                ),
    ])
    
    if not settings["button"]:
        cur_time = datetime.now(pytz.timezone('Africa/kinshasa')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        total_results = len(files)
        cap = await get_cap(settings, remaining_seconds, files, query, total_results, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
        except MessageNotModified:
            pass
    await query.answer()
                
@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    lazyData = query.data
    try:
        link = await client.create_chat_invite_link(int(REQST_CHANNEL))
    except:
        pass
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "gfiltersdeleteallconfirm":
        await del_allg(query.message, 'gfilters')
        await query.answer("ᴅᴏɴᴇ !")
        return
    elif query.data == "gfiltersdeleteallcancel": 
        await query.message.reply_to_message.delete()
        await query.message.delete()
        await query.answer("ᴘʀᴏᴄᴇꜱꜱ ᴄᴀɴᴄᴇʟʟᴇᴅ !")
        return
    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            grpid = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("Aꜱꜱᴜʀᴇᴢ-ᴠᴏᴜꜱ ϙᴜᴇ ᴊᴇ ꜱᴜɪꜱ ᴘʀᴇ́ꜱᴇɴᴛ ᴅᴀɴꜱ ᴠᴏᴛʀᴇ ɢʀᴏᴜᴘᴇ !!", quote=True)
                    return await query.answer(MSG_ALRT)
            else:
                await query.message.edit_text(
                    "Jᴇ ɴᴇ ꜱᴜɪꜱ ᴄᴏɴɴᴇᴄᴛᴇ́ ᴀ̀ ᴀᴜᴄᴜɴ ɢʀᴏᴜᴘᴇ !\nVᴇ́ʀɪꜰɪᴇᴢ /connections ᴏᴜ ᴄᴏɴɴᴇᴄᴛᴇᴢ-ᴍᴏɪ ᴀ̀ ᴜɴ ɢʀᴏᴜᴘᴇ.",
                    quote=True
                )
                return await query.answer(MSG_ALRT)

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return await query.answer(MSG_ALRT)

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
            await del_all(query.message, grp_id, title)
        else:
            await query.answer("Vᴏᴜꜱ ᴅᴇᴠᴇᴢ ᴇ̂ᴛʀᴇ ᴘʀᴏᴘʀɪᴇ́ᴛᴀɪʀᴇ ᴅᴜ ɢʀᴏᴜᴘᴇ ᴏᴜ ᴜɴ ᴜᴛɪʟɪꜱᴀᴛᴇᴜʀ ᴀᴜᴛᴏʀɪꜱᴇ́ ᴘᴏᴜʀ ꜰᴀɪʀᴇ ᴄᴇᴄɪ !", show_alert=True)
            
    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer("Cᴇᴄɪ ɴ'ᴇꜱᴛ ᴘᴀꜱ ᴘᴏᴜʀ ᴠᴏᴜꜱ !!", show_alert=True)
    elif "groupcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        if act == "":
            stat = "ᴄᴏɴɴᴇᴄᴛᴇʀ"
            cb = "connectcb"
        else:
            stat = "ᴅᴇ́ᴄᴏɴɴᴇᴄᴛᴇʀ"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
            InlineKeyboardButton("ꜱᴜᴘᴘʀɪᴍᴇʀ", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("ʀᴇᴛᴏᴜʀ", callback_data="backcb")]
        ])

        await query.message.edit_text(
            f"ɴᴏᴍ ᴅᴜ ɢʀᴏᴜᴘᴇ : **{title}**\nID ᴅᴜ ɢʀᴏᴜᴘᴇ : `{group_id}`",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return await query.answer(MSG_ALRT)
    
    elif "connectcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title

        user_id = query.from_user.id

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"Cᴏɴɴᴇᴄᴛᴇ́ ᴀ̀ **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text('Qᴜᴇʟϙᴜᴇ ᴄʜᴏꜱᴇ ᴀ ᴍᴀʟ ᴛᴏᴜʀɴᴇ́ !!', parse_mode=enums.ParseMode.MARKDOWN)
        return await query.answer(MSG_ALRT)
    elif "disconnect" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"Dᴇ́ᴄᴏɴɴᴇᴄᴛᴇ́ ᴅᴇ **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text(
                f"Qᴜᴇʟϙᴜᴇ ᴄʜᴏꜱᴇ ᴀ ᴍᴀʟ ᴛᴏᴜʀɴᴇ́ !!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer(MSG_ALRT)
    elif "deletecb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Cᴏɴɴᴇxɪᴏɴ ꜱᴜᴘᴘʀɪᴍᴇ́ᴇ ᴀᴠᴇᴄ ꜱᴜᴄᴄᴇ̀ꜱ !"
            )
        else:
            await query.message.edit_text(
                f"Qᴜᴇʟϙᴜᴇ ᴄʜᴏꜱᴇ ᴀ ᴍᴀʟ ᴛᴏᴜʀɴᴇ́ !!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer(MSG_ALRT)
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "Iʟ ɴ'ʏ ᴀ ᴀᴜᴄᴜɴᴇ ᴄᴏɴɴᴇxɪᴏɴ ᴀᴄᴛɪᴠᴇ !! Cᴏɴɴᴇᴄᴛᴇᴢ-ᴠᴏᴜꜱ ᴅ'ᴀʙᴏʀᴅ ᴀ̀ ᴜɴ ɢʀᴏᴜᴘᴇ.",
            )
            return await query.answer(MSG_ALRT)
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIF" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Dᴇ́ᴛᴀɪʟꜱ ᴅᴇ ᴠᴏꜱ ɢʀᴏᴜᴘᴇꜱ ᴄᴏɴɴᴇᴄᴛᴇ́ꜱ ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    elif "gfilteralert" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_gfilter('gfilters', keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
            
    if query.data.startswith("file"):
        clicked = query.from_user.id
        try:
            typed = query.from_user.id
        except:
            typed = query.from_user.id
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('Aᴜᴄᴜɴ ꜰɪᴄʜɪᴇʀ ᴇxɪꜱᴛᴀɴᴛ.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        settings = await get_settings(query.message.chat.id)
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                    file_size='' if size is None else size,
                                                    file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"

        try:
            if not await db.has_premium_access(clicked) and settings['is_shortlink']: # Ne changez rien sans ma permission @CodeluffyTG
                if clicked == query.from_user.id:
                    temp.SHORT[clicked] = query.message.chat.id
                    await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=short_{file_id}")
                    return
                else:
                    await query.answer(f"Hᴇʏ {query.from_user.first_name},\nCᴇᴄɪ ɴ'ᴇꜱᴛ ᴘᴀꜱ ᴠᴏᴛʀᴇ ᴅᴇᴍᴀɴᴅᴇ ᴅᴇ ꜰɪʟᴍ.\nFᴀɪᴛᴇꜱ ᴠᴏᴛʀᴇ ᴘʀᴏᴘʀᴇ ᴅᴇᴍᴀɴᴅᴇ !", show_alert=True)
            else:
                if clicked == query.from_user.id:
                    await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start={ident}_{file_id}")
                    return
                else:
                    await query.answer(f"Hᴇʏ {query.from_user.first_name},\nCᴇᴄɪ ɴ'ᴇꜱᴛ ᴘᴀꜱ ᴠᴏᴛʀᴇ ᴅᴇᴍᴀɴᴅᴇ ᴅᴇ ꜰɪʟᴍ.\nFᴀɪᴛᴇꜱ ᴠᴏᴛʀᴇ ᴘʀᴏᴘʀᴇ ᴅᴇᴍᴀɴᴅᴇ !", show_alert=True)
        except UserIsBlocked:
            await query.answer('Dᴇ́ʙʟᴏϙᴜᴇᴢ ʟᴇ ʙᴏᴛ ᴍᴀɪɴ !', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start={ident}_{file_id}")
        except Exception as e:
            await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start={ident}_{file_id}")
            
    elif query.data.startswith("sendfiles"):
        clicked = query.from_user.id
        ident, key = query.data.split("#")
        settings = await get_settings(query.message.chat.id)
        try:
            if not await db.has_premium_access(clicked) and settings['is_shortlink']: # Ne changez rien sans ma permission @CoderluffyTG
                await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=sendfiles1_{key}")
                return
            else:
                await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=allfiles_{key}")
                return
        except UserIsBlocked:
            await query.answer('Dᴇ́ʙʟᴏϙᴜᴇᴢ ʟᴇ ʙᴏᴛ ᴍᴀɪɴ !', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=sendfiles3_{key}")
        except Exception as e:
            logger.exception(e)
            await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=sendfiles4_{key}")

    elif query.data.startswith("del"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('Aᴜᴄᴜɴ ꜰɪᴄʜɪᴇʀ ᴇxɪꜱᴛᴀɴᴛ.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        settings = await get_settings(query.message.chat.id)
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                    file_size='' if size is None else size,
                                                    file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"
        await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=file_{file_id}")

    elif query.data.startswith("checksub"):
        if AUTH_CHANNEL and not await is_req_subscribed(client, query):
            await query.answer("Rᴇᴊᴏɪɢɴᴇᴢ ɴᴏᴛʀᴇ ᴄʜᴀɴɴᴇʟ ᴅᴇ ᴍɪꜱᴇ ᴀ̀ ᴊᴏᴜʀ ᴍᴀɪɴ ! 😒", show_alert=True)
            return
        ident, kk, file_id = query.data.split("#")
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start={kk}_{file_id}")

    elif query.data == "pages":
        await query.answer()

    elif query.data.startswith("send_fsall"):
        temp_var, ident, key, offset = query.data.split("#")
        search = BUTTON.get(key)
        if not search:
            await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name),show_alert=True)
            return
        files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
        await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
        search = BUTTONS1.get(key)
        files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
        await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
        search = BUTTONS2.get(key)
        files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
        await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
        await query.answer(f"Hᴇʏ {query.from_user.first_name}, ᴛᴏᴜꜱ ʟᴇꜱ ꜰɪᴄʜɪᴇʀꜱ ᴅᴇ ᴄᴇᴛᴛᴇ ᴘᴀɢᴇ ᴏɴᴛ ᴇ́ᴛᴇ́ ᴇɴᴠᴏʏᴇ́ꜱ ᴀᴠᴇᴄ ꜱᴜᴄᴄᴇ̀ꜱ ᴘᴀʀ ᴍᴇꜱꜱᴀɢᴇ ᴘʀɪᴠᴇ́ !", show_alert=True)
        
    elif query.data.startswith("send_fall"):
        temp_var, ident, key, offset = query.data.split("#")
        
        if BUTTONS.get(key)!=None:
            search = BUTTONS.get(key)
        else:
            search = FRESH.get(key)
        if not search:
            await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name),show_alert=True)
            return
        files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
        await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
        await query.answer(f"Hᴇʏ {query.from_user.first_name}, ᴛᴏᴜꜱ ʟᴇꜱ ꜰɪᴄʜɪᴇʀꜱ ᴅᴇ ᴄᴇᴛᴛᴇ ᴘᴀɢᴇ ᴏɴᴛ ᴇ́ᴛᴇ́ ᴇɴᴠᴏʏᴇ́ꜱ ᴀᴠᴇᴄ ꜱᴜᴄᴄᴇ̀ꜱ ᴘᴀʀ ᴍᴇꜱꜱᴀɢᴇ ᴘʀɪᴠᴇ́ !", show_alert=True)
        
    elif query.data.startswith("killfilesdq"):
        ident, keyword = query.data.split("#")
        #await query.message.edit_text(f"<b>Rᴇᴄʜᴇʀᴄʜᴇ ᴅᴇꜱ ꜰɪᴄʜɪᴇʀꜱ ᴘᴏᴜʀ ᴠᴏᴛʀᴇ ʀᴇϙᴜᴇ̂ᴛᴇ {keyword} ꜱᴜʀ ʟᴀ ʙᴀꜱᴇ ᴅᴇ ᴅᴏɴɴᴇ́ᴇꜱ... ᴠᴇᴜɪʟʟᴇᴢ ᴘᴀᴛɪᴇɴᴛᴇʀ...</b>")
        files, total = await get_bad_files(keyword)
        await query.message.edit_text("<b>Lᴇ ᴘʀᴏᴄᴇꜱꜱᴜꜱ ᴅᴇ ꜱᴜᴘᴘʀᴇꜱꜱɪᴏɴ ᴅᴇꜱ ꜰɪᴄʜɪᴇʀꜱ ᴠᴀ ᴄᴏᴍᴍᴇɴᴄᴇʀ ᴅᴀɴꜱ 5 ꜱᴇᴄᴏɴᴅᴇꜱ !</b>")
        await asyncio.sleep(5)
        deleted = 0
        async with lock:
            try:
                for file in files:
                    file_ids = file.file_id
                    file_name = file.file_name
                    result = await Media.collection.delete_one({
                        '_id': file_ids,
                    })
                    if result.deleted_count:
                        logger.info(f'Fɪᴄʜɪᴇʀ ᴛʀᴏᴜᴠᴇ́ ᴘᴏᴜʀ �ᴏᴛʀᴇ ʀᴇϙᴜᴇ̂ᴛᴇ {keyword} ! ꜱᴜᴘᴘʀɪᴍᴇ́ ᴀᴠᴇᴄ ꜱᴜᴄᴄᴇ̀ꜱ {file_name} ᴅᴇ ʟᴀ ʙᴀꜱᴇ ᴅᴇ ᴅᴏɴɴᴇ́ᴇꜱ.')
                    deleted += 1
                    if deleted % 20 == 0:
                        await query.message.edit_text(f"<b>Pʀᴏᴄᴇꜱꜱᴜꜱ ᴅᴇ ᴅᴇ́ᴛʀᴜᴄᴛɪᴏɴ ᴅᴇꜱ ꜰɪᴄʜɪᴇʀꜱ ᴅᴇ ʟᴀ ʙᴀꜱᴇ ᴅᴇ ᴅᴏɴɴᴇ́ᴇꜱ ᴇɴ ᴄᴏᴜʀꜱ. ꜱᴜᴘᴘʀɪᴍᴇ́ ᴀᴠᴇᴄ ꜱᴜᴄᴄᴇ̀ꜱ {str(deleted)} ꜰɪᴄʜɪᴇʀꜱ ᴅᴇ ʟᴀ ʙᴀꜱᴇ ᴅᴇ ᴅᴏɴɴᴇ́ᴇꜱ ᴘᴏᴜʀ ᴠᴏᴛʀᴇ ʀᴇϙᴜᴇ̂ᴛᴇ {keyword} !\n\nVᴇᴜɪʟʟᴇᴢ ᴘᴀᴛɪᴇɴᴛᴇʀ...</b>")
            except Exception as e:
                logger.exception(e)
                await query.message.edit_text(f'Eʀʀᴇᴜʀ : {e}')
            else:
                await query.message.edit_text(f"<b>Pʀᴏᴄᴇꜱꜱᴜꜱ ᴛᴇʀᴍɪɴᴇ́ ᴘᴏᴜʀ ʟᴀ ꜱᴜᴘᴘʀᴇꜱꜱɪᴏɴ ᴅᴇꜱ ꜰɪᴄʜɪᴇʀꜱ !\n\nꜱᴜᴘᴘʀɪᴍᴇ́ ᴀᴠᴇᴄ ꜱᴜᴄᴄᴇ̀ꜱ {str(deleted)} ꜰɪᴄʜɪᴇʀꜱ ᴅᴇ ʟᴀ ʙᴀꜱᴇ ᴅᴇ ᴅᴏɴɴᴇ́ᴇꜱ ᴘᴏᴜʀ ᴠᴏᴛʀᴇ ʀᴇϙᴜᴇ̂ᴛᴇ {keyword}.</b>")

    elif query.data.startswith("opnsetgrp"):
        ident, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        st = await client.get_chat_member(grp_id, userid)
        if (
                st.status != enums.ChatMemberStatus.ADMINISTRATOR
                and st.status != enums.ChatMemberStatus.OWNER
                and str(userid) not in ADMINS
        ):
            await query.answer("Vᴏᴜꜱ ɴ'ᴀᴠᴇᴢ ᴘᴀꜱ ʟᴇꜱ ᴅʀᴏɪᴛꜱ ᴘᴏᴜʀ ꜰᴀɪʀᴇ ᴄᴇᴄɪ !", show_alert=True)
            return
        title = query.message.chat.title
        settings = await get_settings(grp_id)
        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Pᴀɢᴇ ᴅᴇ ʀᴇ́ꜱᴜʟᴛᴀᴛꜱ',
                                        callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Bᴏᴜᴛᴏɴ' if settings["button"] else 'Tᴇxᴛᴇ',
                                        callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Mᴏᴅᴇ ᴅᴇɴᴠᴏɪ ᴅᴇꜱ ꜰɪᴄʜɪᴇʀꜱ', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Dᴇ́ᴍᴀʀʀᴇʀ' if settings["botpm"] else 'Aᴜᴛᴏ',
                                        callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Sᴇ́ᴄᴜʀɪᴛᴇ́ ᴅᴇꜱ ꜰɪᴄʜɪᴇʀꜱ',
                                        callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Aᴄᴛɪᴠᴇʀ' if settings["file_secure"] else 'Dᴇ́ꜱᴀᴄᴛɪᴠᴇʀ',
                                        callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Aꜰꜰɪᴄʜᴇ Iᴍᴅʙ', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Aᴄᴛɪᴠᴇʀ' if settings["imdb"] else 'Dᴇ́ꜱᴀᴄᴛɪᴠᴇʀ',
                                        callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Vᴇ́ʀɪꜰɪᴄᴀᴛɪᴏɴ ᴏʀᴛʜᴏɢʀᴀᴘʜɪϙᴜᴇ',
                                        callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Aᴄᴛɪᴠᴇʀ' if settings["spell_check"] else 'Dᴇ́ꜱᴀᴄᴛɪᴠᴇʀ',
                                        callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Mᴇꜱꜱᴀɢᴇ ᴅᴇ ʙɪᴇɴᴠᴇɴᴜᴇ', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Aᴄᴛɪᴠᴇʀ' if settings["welcome"] else 'Dᴇ́ꜱᴀᴄᴛɪᴠᴇʀ',
                                        callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Sᴜᴘᴘʀᴇꜱꜱɪᴏɴ ᴀᴜᴛᴏᴍᴀᴛɪϙᴜᴇ',
                                        callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Aᴄᴛɪᴠᴇʀ' if settings["auto_delete"] else 'Dᴇ́ꜱᴀᴄᴛɪᴠᴇʀ',
                                        callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Fɪʟᴛʀᴇ ᴀᴜᴛᴏᴍᴀᴛɪϙᴜᴇ',
                                        callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Aᴄᴛɪᴠᴇʀ' if settings["auto_ffilter"] else 'Dᴇ́ꜱᴀᴄᴛɪᴠᴇʀ',
                                        callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Bᴏᴜᴛᴏɴꜱ ᴍᴀx',
                                        callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                    InlineKeyboardButton('10' if settings["max_btn"] else f'{MAX_B_TN}',
                                        callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Lɪᴇɴ ᴄᴏᴜʀᴛ',
                                        callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Aᴄᴛɪᴠᴇʀ' if settings["is_shortlink"] else 'Dᴇ́ꜱᴀᴄᴛɪᴠᴇʀ',
                                        callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('⇋ Fᴇʀᴍᴇʀ ʟᴇ ᴍᴇɴᴜ ᴅᴇꜱ ᴘᴀʀᴀᴍᴇ̀ᴛʀᴇꜱ ⇋', 
                                        callback_data='close_data'
                                        )
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_text(
                text=f"<b>Mᴏᴅɪꜰɪᴇᴢ ʟᴇꜱ ᴘᴀʀᴀᴍᴇ̀ᴛʀᴇꜱ ᴅᴇ {title} ᴄᴏᴍᴍᴇ ᴠᴏᴜꜱ ꜱᴏᴜʜᴀɪᴛᴇᴢ ⚙</b>",
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML
            )
            await query.message.edit_reply_markup(reply_markup)
            
    elif query.data.startswith("opnsetpm"):
        ident, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        st = await client.get_chat_member(grp_id, userid)
        if (
                st.status != enums.ChatMemberStatus.ADMINISTRATOR
                and st.status != enums.ChatMemberStatus.OWNER
                and str(userid) not in ADMINS
        ):
            await query.answer("Vᴏᴜs ɴ'ᴀᴠᴇᴢ ᴘᴀs ʟᴇs ᴅʀᴏɪᴛs ɴᴇ́ᴄᴇssᴀɪʀᴇs !", show_alert=True)
            return
        title = query.message.chat.title
        settings = await get_settings(grp_id)
        btn2 = [[
                 InlineKeyboardButton("ᴠᴇ́ʀɪғ. ᴍᴇs ᴅᴍ 🗳️", url=f"telegram.me/{temp.U_NAME}")
               ]]
        reply_markup = InlineKeyboardMarkup(btn2)
        await query.message.edit_text(f"<b>ᴠᴏs ᴘᴀʀᴀᴍᴇ̀ᴛʀᴇs ᴘᴏᴜʀ {title} ᴏɴᴛ ᴇ́ᴛᴇ́ ᴇɴᴠᴏʏᴇ́s ᴇɴ ᴅᴍ.</b>")
        await query.message.edit_reply_markup(reply_markup)
        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('ᴘᴀɢᴇ ʀᴇ́ꜱᴜʟᴛᴀᴛs',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ʙᴏᴜᴛᴏɴ' if settings["button"] else 'ᴛᴇxᴛᴇ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ᴍᴏᴅᴇ ᴇɴᴠᴏɪ ᴅᴜ ᴇxᴛʀᴀɪᴛ', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴍᴀɴᴜᴇʟ' if settings["botpm"] else 'ᴀᴜᴛᴏ',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('sᴇ́ᴄᴜʀɪᴛᴇ́ ᴅᴜ ᴇxᴛʀᴀɪᴛ',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴀᴄᴛɪᴠᴇʀ' if settings["file_secure"] else 'ᴅᴇ́sᴀᴄᴛɪᴠᴇʀ',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ᴀғғɪᴄʜᴇ ɪᴍᴅʙ', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴀᴄᴛɪᴠᴇʀ' if settings["imdb"] else 'ᴅᴇ́sᴀᴄᴛɪᴠᴇʀ',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ᴠᴇ́ʀɪғ. ᴏʀᴛᴏɢʀᴀᴘʜᴇ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴀᴄᴛɪᴠᴇʀ' if settings["spell_check"] else 'ᴅᴇ́sᴀᴄᴛɪᴠᴇʀ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ᴍsɢ ʙɪᴇɴᴠᴇɴᴜᴇ', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴀᴄᴛɪᴠᴇʀ' if settings["welcome"] else 'ᴅᴇ́sᴀᴄᴛɪᴠᴇʀ',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('sᴜᴘᴘʀ. ᴀᴜᴛᴏ',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴀᴄᴛɪᴠᴇʀ' if settings["auto_delete"] else 'ᴅᴇ́sᴀᴄᴛɪᴠᴇʀ',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ғɪʟᴛʀᴇ ᴀᴜᴛᴏ',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴀᴄᴛɪᴠᴇʀ' if settings["auto_ffilter"] else 'ᴅᴇ́sᴀᴄᴛɪᴠᴇʀ',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ʙᴏᴜᴛᴏɴs ᴍᴀx',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                    InlineKeyboardButton('10' if settings["max_btn"] else f'{MAX_B_TN}',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ʟɪᴇɴs ᴄᴏᴜʀᴛs',
                                         callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴀᴄᴛɪᴠᴇʀ' if settings["is_shortlink"] else 'ᴅᴇ́sᴀᴄᴛɪᴠᴇʀ',
                                         callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('⇋ ғᴇʀᴍᴇʀ ᴍᴇɴᴜ ⇋', 
                                         callback_data='close_data'
                                         )
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await client.send_message(
                chat_id=userid,
                text=f"<b>ᴍᴏᴅɪғɪᴇᴢ ʟᴇs ᴘᴀʀᴀᴍᴇ̀ᴛʀᴇs ᴅᴇ {title} ᴀ̀ ᴠᴏᴛʀᴇ ɢᴜɪsᴇ ⚙</b>",
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
                reply_to_message_id=query.message.id
            )

    elif query.data.startswith("show_option"):
        ident, from_user = query.data.split("#")
        btn = [[
                InlineKeyboardButton("⚠️ INDISPONIBLE ⚠️", callback_data=f"unavailable#{from_user}"),
                InlineKeyboardButton("🟢 TÉLÉVERSÉ 🟢", callback_data=f"uploaded#{from_user}")
             ],[
                InlineKeyboardButton("♻️ DÉJÀ DISPONIBLE ♻️", callback_data=f"already_available#{from_user}")
              ]]
        btn2 = [[
                 InlineKeyboardButton("ᴠᴏɪʀ ʟᴇ ꜱᴛᴀᴛᴜᴛ", url=f"{query.message.link}")
               ]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Voici les options !")
        else:
            await query.answer("Vous n'avez pas les droits suffisants pour faire cela !", show_alert=True)
        
    elif query.data.startswith("unavailable"):
        ident, from_user = query.data.split("#")
        btn = [[
                InlineKeyboardButton("⚠️ INDISPONIBLE ⚠️", callback_data=f"unalert#{from_user}")
              ]]
        btn2 = [[
                 InlineKeyboardButton('Rejoindre le canal', url=link.invite_link),
                 InlineKeyboardButton("ᴠᴏɪʀ ʟᴇ ꜱᴛᴀᴛᴜᴛ", url=f"{query.message.link}")
               ]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Défini comme Indisponible !")
            try:
                await client.send_message(chat_id=int(from_user), text=f"<b>Hey {user.mention}, Désolé, votre demande est indisponible. Nos modérateurs ne peuvent donc pas la téléverser.</b>", reply_markup=InlineKeyboardMarkup(btn2))
            except UserIsBlocked:
                await client.send_message(chat_id=int(SUPPORT_CHAT_ID), text=f"<b>Hey {user.mention}, Désolé, votre demande est indisponible. Nos modérateurs ne peuvent donc pas la téléverser.\n\nNote : Ce message est envoyé à ce groupe car vous avez bloqué le bot. Pour recevoir ce message en MP, vous devez débloquer le bot.</b>", reply_markup=InlineKeyboardMarkup(btn2))
        else:
            await query.answer("Vous n'avez pas les droits suffisants pour faire cela !", show_alert=True)

    elif query.data.startswith("uploaded"):
        ident, from_user = query.data.split("#")
        btn = [[
                InlineKeyboardButton("🟢 TÉLÉVERSÉ 🟢", callback_data=f"upalert#{from_user}")
              ]]
        btn2 = [[
                 InlineKeyboardButton('Rejoindre le canal', url=link.invite_link),
                 InlineKeyboardButton("ᴠᴏɪʀ ʟᴇ ꜱᴛᴀᴛᴜᴛ", url=f"{query.message.link}")
               ],[
                 InlineKeyboardButton("🔍 Rechercher ici 🔎", url="https://t.me/tout_manga_confondu")
               ]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Défini comme Téléversé !")
            try:
                await client.send_message(chat_id=int(from_user), text=f"<b>Hey {user.mention}, Votre demande a été téléversée par nos modérateurs. Veuillez la rechercher dans notre groupe.</b>", reply_markup=InlineKeyboardMarkup(btn2))
            except UserIsBlocked:
                await client.send_message(chat_id=int(SUPPORT_CHAT_ID), text=f"<b>Hey {user.mention}, Votre demande a été téléversée par nos modérateurs. Veuillez la rechercher dans notre groupe.\n\nNote : Ce message est envoyé à ce groupe car vous avez bloqué le bot. Pour recevoir ce message en MP, vous devez débloquer le bot.</b>", reply_markup=InlineKeyboardMarkup(btn2))
        else:
            await query.answer("Vous n'avez pas les droits suffisants pour faire cela !", show_alert=True)

    elif query.data.startswith("already_available"):
        ident, from_user = query.data.split("#")
        btn = [[
                InlineKeyboardButton("♻️ DÉJÀ DISPONIBLE ♻️", callback_data=f"alalert#{from_user}")
              ]]
        btn2 = [[
                 InlineKeyboardButton('Rejoindre le canal', url=link.invite_link),
                 InlineKeyboardButton("ᴠᴏɪʀ ʟᴇ ꜱᴛᴀᴛᴜᴛ", url=f"{query.message.link}")
               ],[
                 InlineKeyboardButton("🔍 Rechercher ici 🔎", url="https://t.me/tout_manga_confondu")
               ]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Défini comme Déjà Disponible !")
            try:
                await client.send_message(chat_id=int(from_user), text=f"<b>Hey {user.mention}, Votre demande est déjà disponible dans la base de données de notre bot. Veuillez la rechercher dans notre groupe.</b>", reply_markup=InlineKeyboardMarkup(btn2))
            except UserIsBlocked:
                await client.send_message(chat_id=int(SUPPORT_CHAT_ID), text=f"<b>Hey {user.mention}, Votre demande est déjà disponible dans la base de données de notre bot. Veuillez la rechercher dans notre groupe.\n\nNote : Ce message est envoyé à ce groupe car vous avez bloqué le bot. Pour recevoir ce message en MP, vous devez débloquer le bot.</b>", reply_markup=InlineKeyboardMarkup(btn2))
        else:
            await query.answer("Vous n'avez pas les droits suffisants pour faire cela !", show_alert=True)

    elif query.data.startswith("alalert"):
        ident, from_user = query.data.split("#")
        if int(query.from_user.id) == int(from_user):
            user = await client.get_users(from_user)
            await query.answer(f"Hey {user.first_name}, Votre demande est déjà disponible !", show_alert=True)
        else:
            await query.answer("Vous n'avez pas les droits suffisants pour faire cela !", show_alert=True)

    elif query.data.startswith("upalert"):
        ident, from_user = query.data.split("#")
        if int(query.from_user.id) == int(from_user):
            user = await client.get_users(from_user)
            await query.answer(f"Hey {user.first_name}, Votre demande a été téléversée !", show_alert=True)
        else:
            await query.answer("Vous n'avez pas les droits suffisants pour faire cela !", show_alert=True)
        
    elif query.data.startswith("unalert"):
        ident, from_user = query.data.split("#")
        if int(query.from_user.id) == int(from_user):
            user = await client.get_users(from_user)
            await query.answer(f"Hey {user.first_name}, Votre demande est indisponible !", show_alert=True)
        else:
            await query.answer("Vous n'avez pas les droits suffisants pour faire cela !", show_alert=True)

    elif lazyData.startswith("generate_stream_link"):
        _, file_id = lazyData.split(":")
        try:
            user_id = query.from_user.id
            username = query.from_user.mention 
            log_msg = await client.send_cached_media(
                chat_id=LOG_CHANNEL,
                file_id=file_id,
            )
            fileName = {quote_plus(get_name(log_msg))}
            lazy_stream = f"{URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
            lazy_download = f"{URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
            hp_link = await get_shortlink(lazy_download)
            ph_link = await get_shortlink(lazy_stream)
            buttons = []
            if await db.has_premium_access(user_id):                               
                buttons = [[
                    InlineKeyboardButton("• Téléchargement rapide", url=lazy_download),
                    InlineKeyboardButton("Regarder en ligne •", url=lazy_stream)
                ],[
                    InlineKeyboardButton("• Regarder dans l'application web •", web_app=WebAppInfo(url=lazy_stream))
                ]]
            else:
                await query.answer("🚸 Note :\nLe service sans publicité est réservé aux utilisateurs premium.\n\nPour en savoir plus, consultez les plans.", show_alert=True)
                await query.message.reply_text(
                text="<b>‼️ Vous souhaitez supprimer les publicités ?\n\n✅ Achetez un abonnement premium et profitez d'une expérience sans publicité.</b>",
                quote=True,
                disable_web_page_preview=True,                  
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💸 Voir les plans premium 💸", callback_data='seeplans')]]))
                buttons = [[
                    InlineKeyboardButton("• Téléchargement rapide", url=hp_link),
                    InlineKeyboardButton("Regarder en ligne •", url=ph_link)
                ],[
                    InlineKeyboardButton("• Regarder dans l'application web •", web_app=WebAppInfo(url=ph_link))
                ],[
                    InlineKeyboardButton('❗Comment ouvrir le lien❗', url=STREAMHTO)
                ]]
    
            query.message.reply_markup = query.message.reply_markup or []
            query.message.reply_markup.inline_keyboard.pop(0)
            query.message.reply_markup.inline_keyboard.insert(0, buttons)
            await query.message.edit_reply_markup(InlineKeyboardMarkup(buttons))
            await log_msg.reply_text(
                    text=f"#LienGénéré\n\nID : <code>{user_id}</code>\nNom d'utilisateur : {username}\n\nNom : {fileName}",
                    quote=True,
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("• Téléchargement rapide", url=hp_link),
                                                        InlineKeyboardButton('Regarder en ligne •', url=ph_link)]]))  
        except Exception as e:
            print(e)  # Afficher le message d'erreur
            await query.answer(f"⚠️ Quelque chose ne va pas \n\n{e}", show_alert=True)
            return

    # Ne modifiez rien sans me contacter @cryxelys

    elif query.data == "pagesn1":
        await query.answer(text=script.PAGE_TXT, show_alert=True)

    elif query.data == "reqinfo":
        await query.answer(text=script.REQINFO, show_alert=True)

    elif query.data == "select":
        await query.answer(text=script.SELECT, show_alert=True)

    elif query.data == "sinfo":
        await query.answer(text=script.SINFO, show_alert=True)

    elif query.data == "start":
        buttons = [[
                    InlineKeyboardButton(text="🏡", callback_data="start"),
                    InlineKeyboardButton(text="🛡", callback_data="group_info"),
                    InlineKeyboardButton(text="💳", callback_data="about"),
                    InlineKeyboardButton(text="💸", callback_data="shortlink_info"),
                    InlineKeyboardButton(text="🖥", callback_data="main"),
                ],[
                    InlineKeyboardButton('Ajoutez-moi à votre groupe', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                ],[
                    InlineKeyboardButton('• Commandes •', callback_data='main'),
                    InlineKeyboardButton('• Gagner de l\'argent •', callback_data='shortlink_info')
                ],[
                    InlineKeyboardButton('• Premium •', callback_data='premium_info'),
                    InlineKeyboardButton('• À propos •', callback_data='about')
                  ]]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        current_time = datetime.now(pytz.timezone(TIMEZONE))
        curr_time = current_time.hour        
        if curr_time < 12:
            gtxt = "Bonjour 👋" 
        elif curr_time < 17:
            gtxt = "Bon après-midi 👋" 
        elif curr_time < 21:
            gtxt = "Bonsoir 👋"
        else:
            gtxt = "Bonne nuit 👋"
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, gtxt, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        await query.answer(MSG_ALRT)
        
    elif query.data == "filters":
        buttons = [[
            InlineKeyboardButton('Filtres manuels', callback_data='manuelfilter'),
            InlineKeyboardButton('Filtres automatiques', callback_data='autofilter')
        ],[
            InlineKeyboardButton('⇇ Retour', callback_data='help'),
            InlineKeyboardButton('Filtres globaux', callback_data='global_filters')
        ]]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.ALL_FILTERS.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "global_filters":
        buttons = [[
            InlineKeyboardButton('• Retour •', callback_data='filters')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.GFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "main":
        buttons = [[
            InlineKeyboardButton('• Commandes administrateur du bot •', callback_data='adminx')
        ], [
            InlineKeyboardButton('• Utilisateur •', callback_data='users'),
            InlineKeyboardButton('• Groupe •', callback_data='group')
        ], [
            InlineKeyboardButton('• IA •', callback_data='aihelp'),
            InlineKeyboardButton('• Plus •', callback_data='help')
        ], [
            InlineKeyboardButton('• Gestion •', callback_data='management')
        ], [
            InlineKeyboardButton('⇋ Retour à l\'accueil ⇋', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        await query.message.edit_text(
            text=script.MAIN_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('Filtres', callback_data='filters'),
            InlineKeyboardButton('Stockage', callback_data='store_file'),
            InlineKeyboardButton('Telegraph', callback_data='tele')     
        ], [
            InlineKeyboardButton('Paramètres', callback_data='settings'),
            InlineKeyboardButton('Connexion', callback_data='coct'),
            InlineKeyboardButton('Extra', callback_data='extra')
        ], [
            InlineKeyboardButton('Police', callback_data='font'),
            InlineKeyboardButton('Autocollants', callback_data='sticker'),
            InlineKeyboardButton('Règles', callback_data='rule')
        ], [
            InlineKeyboardButton('Miniature YouTube', callback_data='ytthumb'),
            InlineKeyboardButton('Vidéo YouTube', callback_data='video'),
            InlineKeyboardButton('Tags YouTube', callback_data='yttags')
        ], [
            InlineKeyboardButton('Propriétaire', callback_data='mikey'),
            InlineKeyboardButton('Donation', callback_data='donate'),
            InlineKeyboardButton('GitHub', callback_data='github')
        ], [
            InlineKeyboardButton('Précédent', callback_data='main'),
            InlineKeyboardButton('Page', callback_data='page'),
            InlineKeyboardButton('Suivant', callback_data='help1')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "help1":
        buttons = [[
            InlineKeyboardButton('Kang', callback_data='kang'),
            InlineKeyboardButton('Rapport', callback_data='report'),
            InlineKeyboardButton('Générer mot de passe', callback_data='gen_pass')
        ], [
            InlineKeyboardButton('OpenAI', callback_data='opnai'),
            InlineKeyboardButton('Song', callback_data='song'),
            InlineKeyboardButton('Purger', callback_data='purge')
        ], [
            InlineKeyboardButton('Ping', callback_data='alive'),
            InlineKeyboardButton('Anime', callback_data='anime'),
            InlineKeyboardButton('Dépôt', callback_data='repo')
         ], [
            InlineKeyboardButton('Jeux', callback_data='games'),
            InlineKeyboardButton('Mute', callback_data='restrict'),
            InlineKeyboardButton('Expulser', callback_data='kick')
        ], [
            InlineKeyboardButton('JSON', callback_data='json'),
            InlineKeyboardButton('Paroles', callback_data='lyrics'),
            InlineKeyboardButton('Raccourcisseur', callback_data='shortner')
         ], [
            InlineKeyboardButton('Retour', callback_data='help'),
            InlineKeyboardButton('Page', callback_data='page'),
            InlineKeyboardButton('Suivant', callback_data='help2')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        
    elif query.data == "help2":
        buttons = [[
            InlineKeyboardButton('ᴏᴜᴛɪʟs ᴄᴄ', callback_data='cc'),
            InlineKeyboardButton('ғsᴜʙ', callback_data='fsub'),
            InlineKeyboardButton('ᴛᴏʀʀᴇɴᴛ', callback_data='torrent')
        ], [
            InlineKeyboardButton('ᴠsᴏɴɢ', callback_data='vsong'),
            InlineKeyboardButton('ᴄʜᴀᴛɢᴘᴛ', callback_data='gpt'),
            InlineKeyboardButton('ᴄʜɪғғʀᴇᴍᴇɴᴛs', callback_data='encrypt')
        ], [
            InlineKeyboardButton('ʀᴇᴄʜᴇʀᴄʜᴇ ʏᴛ', callback_data='ytsearch'),
            InlineKeyboardButton('ғɪɢʟᴇᴛ', callback_data='figletx'),
            InlineKeyboardButton('ғᴏɴᴅ ᴅ\'ᴇ́ᴄʀᴀɴ', callback_data='wall')
        ], [
            InlineKeyboardButton('ɪɴғᴏ ɢʀᴏᴜᴘᴇ', callback_data='grpinfo'),
            InlineKeyboardButton('ᴛᴀɢᴜᴇʀ ᴛᴏᴜs', callback_data='tagall'),
            InlineKeyboardButton('sᴜᴘᴘʀɪᴍᴇʀ ᴀʀʀɪᴇʀᴇ-ᴘʟᴀɴ', callback_data='bgremove')
        ], [
            InlineKeyboardButton('sᴏɴɴᴇʀɪᴇ', callback_data='ringtune'),
            InlineKeyboardButton('ᴀᴍᴜsᴀɴᴛ', callback_data='fun'),
            InlineKeyboardButton('ᴍᴏɴɢᴏ', callback_data='mongochk')
        ], [
            InlineKeyboardButton('ʀᴇᴛᴏᴜʀ', callback_data='help1'),
            InlineKeyboardButton('ᴘᴀɢᴇ', callback_data='page'),
            InlineKeyboardButton('ᴘʟᴜs »', callback_data='special')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.SPECIAL_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "special":
        buttons = [[
            InlineKeyboardButton('sᴘᴇ́ᴄɪᴀʟ', callback_data='special_mod1'),
            InlineKeyboardButton('sᴘᴇ́ᴄɪᴀʟ', callback_data='special_mod2')
        ], [
            InlineKeyboardButton('ғᴏɴᴄᴛɪᴏɴɴᴀʟɪᴛᴇ́s ᴇxᴛʀᴀ', callback_data='extra_mod')
        ], [
            InlineKeyboardButton('• ʀᴇᴛᴏᴜʀ •', callback_data='help2')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text="● ◌ ◌"
        )
        await query.message.edit_text(
            text="● ● ◌"
        )
        await query.message.edit_text(
            text="● ● ●"
        )
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.SPECIAL_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "special_mod1":
        buttons = [[
            InlineKeyboardButton('• ʀᴇᴛᴏᴜʀ •', callback_data='special')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text="● ◌ ◌"
        )
        await query.message.edit_text(
            text="● ● ◌"
        )
        await query.message.edit_text(
            text="● ● ●"
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.SPECIAL_MOD1,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "special_mod2":
        buttons = [[
            InlineKeyboardButton('• ʀᴇᴛᴏᴜʀ •', callback_data='special')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text="● ◌ ◌"
        )
        await query.message.edit_text(
            text="● ● ◌"
        )
        await query.message.edit_text(
            text="● ● ●"
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.SPECIAL_MOD2,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        
    elif query.data == "extra_mod":
        buttons = [[
            InlineKeyboardButton('• ʙᴀᴄᴋ •', callback_data='special')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text="● ◌ ◌"
        )
        await query.message.edit_text(
            text="● ● ◌"
        )
        await query.message.edit_text(
            text="● ● ●"
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.EXTRA_MOD,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "subscription":
        buttons = [[
            InlineKeyboardButton('• ʀᴇᴛᴏᴜʀ', callback_data='start'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ •', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.SUBSCRIPTION_TXT.format(REFERAL_PREMEIUM_TIME, temp.U_NAME, query.from_user.id, REFERAL_COUNT),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "purchase":
        buttons = [[
            InlineKeyboardButton('💵 ᴘᴀʏᴇʀ ᴠɪᴀ ᴜᴘɪ ɪᴅ 💵', callback_data='upi_info')
        ],[
            InlineKeyboardButton('📸 ꜱᴄᴀɴɴᴇʀ ʟᴇ ǫʀ ᴄᴏᴅᴇ 📸', callback_data='qr_info')
        ],[
            InlineKeyboardButton('• ʀᴇᴛᴏᴜʀ •', callback_data='premium_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.PURCHASE_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "upi_info":
        buttons = [[
            InlineKeyboardButton('📲 ᴇɴᴠᴏʏᴇʀ �ᴜɴ ᴄᴀᴘᴛᴜʀᴇ ᴅᴇ ᴘᴀɪᴇᴍᴇɴᴛ ɪᴄɪ', user_id=int(5814104129))
        ],[
            InlineKeyboardButton('• ʀᴇᴛᴏᴜʀ •', callback_data='purchase')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.UPI_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "qr_info":
        buttons = [[
            InlineKeyboardButton('📲 ᴇɴᴠᴏʏᴇʀ ᴜɴᴇ ᴄᴀᴘᴛᴜʀᴇ ᴅᴇ ᴘᴀɪᴇᴍᴇɴᴛ ɪᴄɪ', user_id=int(5814104129))
        ],[
            InlineKeyboardButton('• ʀᴇᴛᴏᴜʀ •', callback_data='purchase')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.QR_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )       

    elif query.data == "seeplans":
        btn = [[
            InlineKeyboardButton('📲 ᴇɴᴠᴏʏᴇʀ ᴜɴᴇ ᴄᴀᴘᴛᴜʀᴇ ᴅᴇ ᴘᴀɪᴇᴍᴇɴᴛ', user_id=int(5814104129))
        ],[
            InlineKeyboardButton('❌ ғᴇʀᴍᴇʀ ❌', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(btn)
        await query.message.reply_photo(
            photo=(SUBSCRIPTION),
            caption=script.PREPLANS_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "give_trial":
        user_id = query.from_user.id
        has_free_trial = await db.check_trial_status(user_id)
        if has_free_trial:
            await query.answer("🚸 Vous avez déjà utilisé votre essai gratuit !\n\n📌 Consultez nos offres avec : /plan", show_alert=True)
            return
        else:            
            await db.give_free_trial(user_id)
            await query.message.reply_text(
                text="<b>🥳 Félicitations\n\n🎉 Vous pouvez utiliser l'essai gratuit pendant <u>5 minutes</u> à partir de maintenant !</b>",
                quote=False,
                disable_web_page_preview=True,                  
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💸 Découvrez nos offres premium 💸", callback_data='seeplans')]]))
            return    

    elif query.data == "premium_info":
        buttons = [[
            InlineKeyboardButton('• Essai gratuit •', callback_data='free')
        ],[
            InlineKeyboardButton('• Bronze •', callback_data='broze'),
            InlineKeyboardButton('• Argent •', callback_data='silver')
        ],[
            InlineKeyboardButton('• Or •', callback_data='gold'),
            InlineKeyboardButton('• Platine •', callback_data='platinum')
        ],[
            InlineKeyboardButton('• Diamant •', callback_data='diamond'),
            InlineKeyboardButton('• Autre •', callback_data='other')
        ],[ 
            InlineKeyboardButton('• Lien de parrainage •', callback_data='reffff')
        ],[         
            InlineKeyboardButton('⇋ Retour à l\'accueil ⇋', callback_data='start')
        ]]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.PLAN_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "free":
        buttons = [[
            InlineKeyboardButton('⚜️ Cliquez ici pour obtenir un essai gratuit', callback_data="give_trial")
        ],[
            InlineKeyboardButton('⋞ Retour', callback_data='other'),
            InlineKeyboardButton('1 / 7', callback_data='pagesn1'),
            InlineKeyboardButton('Suivant ⋟', callback_data='broze')
        ],[
            InlineKeyboardButton('⇋ Retour ⇋', callback_data='premium_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.FREE_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    
    elif query.data == "broze":
        buttons = [[
            InlineKeyboardButton('🔐 Cliquez ici pour acheter le premium', callback_data='purchase')
        ],[
            InlineKeyboardButton('⋞ Retour', callback_data='free'),
            InlineKeyboardButton('2 / 7', callback_data='pagesn1'),
            InlineKeyboardButton('Suivant ⋟', callback_data='silver')
        ],[
            InlineKeyboardButton('⇋ Retour ⇋', callback_data='premium_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.BRONZE_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "silver":
        buttons = [[
            InlineKeyboardButton('🔐 Cliquez ici pour acheter Premium', callback_data='purchase')
        ],[
            InlineKeyboardButton('⋞ Retour', callback_data='broze'),
            InlineKeyboardButton('3 / 7', callback_data='pagesn1'),
            InlineKeyboardButton('Suivant ⋟', callback_data='gold')
        ],[
            InlineKeyboardButton('⇋ Retour ⇋', callback_data='premium_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.SILVER_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "gold":
        buttons = [[
            InlineKeyboardButton('🔐 Cliquez ici pour acheter Premium', callback_data='purchase')
        ],[
            InlineKeyboardButton('⋞ Retour', callback_data='silver'),
            InlineKeyboardButton('4 / 7', callback_data='pagesn1'),
            InlineKeyboardButton('Suivant ⋟', callback_data='platinum')
        ],[
            InlineKeyboardButton('⇋ Retour ⇋', callback_data='premium_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.GOLD_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "platinum":
        buttons = [[
            InlineKeyboardButton('🔐 Cliquez ici pour acheter Premium', callback_data='purchase')
        ],[
            InlineKeyboardButton('⋞ Retour', callback_data='gold'),
            InlineKeyboardButton('5 / 7', callback_data='pagesn1'),
            InlineKeyboardButton('Suivant ⋟', callback_data='diamond')
        ],[
            InlineKeyboardButton('⇋ Retour ⇋', callback_data='premium_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.PLATINUM_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "diamond":
        buttons = [[
            InlineKeyboardButton('🔐 Cliquez ici pour acheter Premium', callback_data='purchase')
        ],[
            InlineKeyboardButton('⋞ Retour', callback_data='platinum'),
            InlineKeyboardButton('6 / 7', callback_data='pagesn1'),
            InlineKeyboardButton('Suivant ⋟', callback_data='other')
        ],[
            InlineKeyboardButton('⇋ Retour ⇋', callback_data='premium_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.DIAMOND_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "other":
        buttons = [[
            InlineKeyboardButton('☎️ Contactez le propriétaire pour en savoir plus', user_id=int(5814104129))
        ],[
            InlineKeyboardButton('⋞ Retour', callback_data='diamond'),
            InlineKeyboardButton('7 / 7', callback_data='pagesn1'),
            InlineKeyboardButton('Suivant ⋟', callback_data='free')
        ],[
            InlineKeyboardButton('⇋ Retour ⇋', callback_data='premium_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.OTHER_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "group_info":
        buttons = [[
            InlineKeyboardButton('× Tous nos liens ×', url="https://t.me/hyoshcoder/33")
        ],[
            InlineKeyboardButton('• Groupe •', url="t.me/tout_manga_confondu"),
            InlineKeyboardButton('• Mises à jour •', url="t.me/hyoshcoder")
        ],[
            InlineKeyboardButton('• Series •', url="https://t.me/hyoshmangavf"),
            InlineKeyboardButton('• Movie •', url="https://t.me/hyoshmangavf")
        ],[
            InlineKeyboardButton('• Anime •', url="https://t.me/hyoshmangavf")
        ],[ 
            InlineKeyboardButton('• Retour •', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CHANNELS.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "users":
        buttons = [[
            InlineKeyboardButton('Retour', callback_data='main'),
            InlineKeyboardButton('Support', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.USERS_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "group":
        buttons = [[
            InlineKeyboardButton('Retour', callback_data='main'),
            InlineKeyboardButton('Support', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.GROUP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "adminx":
        buttons = [[
            InlineKeyboardButton('Retour', callback_data='main'),
            InlineKeyboardButton('Support', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ADMINS_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "helps":
        buttons = [[
            InlineKeyboardButton('• Commandes Admin du Bot •', callback_data='admins')
        ], [
            InlineKeyboardButton('• Utilisateur •', callback_data='users'),
            InlineKeyboardButton('• Groupe •', callback_data='group')
        ], [
            InlineKeyboardButton('⇋ Retour à l\'accueil ⇋', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "about":
        buttons = [[
            InlineKeyboardButton('‼️ Avertissement ‼️', callback_data='disclaimer'),
        ], [
            InlineKeyboardButton('• Visitez notre communauté •', url="t.me/tout_manga_confondu"),
        ], [
            InlineKeyboardButton('• Propriétaire •', user_id=int(5814104129)),
            InlineKeyboardButton('• Source •', callback_data='source')
        ], [
            InlineKeyboardButton('🛰️ État du rendu ☁️', callback_data='rendr')
        ], [
            InlineKeyboardButton('⇋ Retour à l\'accueil ⇋', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ABOUT_TXT.format(temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "rendr":
        await query.answer("⚡️ État du système en direct ⚡️\n\n❂ RAM ●●●●●●●◌◌◌\n✇ CPU ●●●●●●●◌◌◌\n✪ Trafic de données ●●●●◌◌◌◌◌◌ 🛰\n\nv4.4 [stable] """, show_alert=True)

    elif query.data == "sticker":
        buttons = [[
            InlineKeyboardButton("Retour", callback_data="help"),
            InlineKeyboardButton('Support', callback_data='group_info')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=(script.STICKER_TXT),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "source":
        buttons = [[
            InlineKeyboardButton("Retour", callback_data="about"),
            InlineKeyboardButton('Support', callback_data='group_info')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=(script.SOURCE_TXT),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )  
    elif query.data == "manuelfilter":
        buttons = [[
            InlineKeyboardButton('⇇ Retour', callback_data='filters'),
            InlineKeyboardButton('Boutons', callback_data='button')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.MANUELFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "button":
        buttons = [[
            InlineKeyboardButton('⇋ Retour ⇋', callback_data='manuelfilter')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.BUTTON_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "autofilter":
        buttons = [[
            InlineKeyboardButton('⇋ Retour ⇋', callback_data='filters')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.AUTOFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "coct":
        buttons = [[
            InlineKeyboardButton('Retour', callback_data='help'),
            InlineKeyboardButton('Support', callback_data='group_info')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "extra":
        buttons = [[
            InlineKeyboardButton('⇇ Retour', callback_data='help'),
            InlineKeyboardButton('Admin', callback_data='admin')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.EXTRAMOD_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "store_file":
        buttons = [[
            InlineKeyboardButton('Retour', callback_data='help'),
            InlineKeyboardButton('Support', callback_data='group_info')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.FILE_STORE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    
    elif query.data == "admin":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='extra'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ADMIN_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "tele":
            buttons = [[
                    InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="help"),
                    InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
                  ]]
            await client.edit_message_media(
                query.message.chat.id, 
                query.message.id, 
                InputMediaPhoto(random.choice(PICS))
            )
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_text(
                text=(script.TELEGRAPH_TXT),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
    elif query.data == "settings":
            buttons = [[
                    InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="help"),
                    InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
                  ]]
            await client.edit_message_media(
                query.message.chat.id, 
                query.message.id, 
                InputMediaPhoto(random.choice(PICS))
            )
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_text(
                text=(script.SETTINGS_TXT),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
    elif query.data == "rule":
            buttons = [[
                    InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="help"),
                    InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
                  ]]
            await client.edit_message_media(
                query.message.chat.id, 
                query.message.id, 
                InputMediaPhoto(random.choice(PICS))
            )
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_text(
                text=(script.RULE_TXT),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
    elif query.data == "ytthumb":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.YTTHUMB,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "video":
            buttons = [[
                    InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="help"),
                    InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
                  ]]
            await client.edit_message_media(
                query.message.chat.id, 
                query.message.id, 
                InputMediaPhoto(random.choice(PICS))
            )
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_text(
                text=(script.VIDEO_TXT),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
    elif query.data == "yttags":
            buttons = [[
                    InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="help"),
                    InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
                  ]]
            await client.edit_message_media(
                query.message.chat.id, 
                query.message.id, 
                InputMediaPhoto(random.choice(PICS))
            )
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_text(
                text=(script.YTTAGS),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
    elif query.data == "mikey":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('ᴏᴡɴᴇʀ', url="t.me/hyoshcoder")
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.ADMINS,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "donate":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.DONATE,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "github":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.GITHUB,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "kang":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text="● ◌ ◌"
        )
        await query.message.edit_text(
            text="● ● ◌"
        )
        await query.message.edit_text(
            text="● ● ●"
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.KANG,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "report":
            buttons = [[
                    InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="help"),
                    InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
                  ]]
            await client.edit_message_media(
                query.message.chat.id, 
                query.message.id, 
                InputMediaPhoto(random.choice(PICS))
            )
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_text(
                text=(script.REPORT),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
    elif query.data == "gen_pass":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.GEN_PASS,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "opnai":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help1'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.OPNAI_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "song":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help1'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.SONG_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "purge":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help1'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.PURGE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "alive":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help2'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.ALIVE,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "anime":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help1'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.ANIME_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "repo":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help2'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.REPO,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "json":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help2'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.JSON_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "lyrics":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help2'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.LYRICS,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "shortner":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help2'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.SHORTNER,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "torrent":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help2'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text="● ◌ ◌"
        )
        await query.message.edit_text(
            text="● ● ◌"
        )
        await query.message.edit_text(
            text="● ● ●"
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.TORRENT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "games":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help1'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text="● ◌ ◌"
        )
        await query.message.edit_text(
            text="● ● ◌"
        )
        await query.message.edit_text(
            text="● ● ●"
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.GAME_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "restrict":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help2'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text="● ◌ ◌"
        )
        await query.message.edit_text(
            text="● ● ◌"
        )
        await query.message.edit_text(
            text="● ● ●"
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.RESTRIC_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "kick":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help2'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text="● ◌ ◌"
        )
        await query.message.edit_text(
            text="● ● ◌"
        )
        await query.message.edit_text(
            text="● ● ●"
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.ZOMBIES_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "management":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='main'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text="● ◌ ◌"
        )
        await query.message.edit_text(
            text="● ● ◌"
        )
        await query.message.edit_text(
            text="● ● ●"
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.MANAGEMENT_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "basic_help":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='main'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text="● ◌ ◌"
        )
        await query.message.edit_text(
            text="● ● ◌"
        )
        await query.message.edit_text(
            text="● ● ●"
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.BASIC_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "aihelp":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='main'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text="● ◌ ◌"
        )
        await query.message.edit_text(
            text="● ● ◌"
        )
        await query.message.edit_text(
            text="● ● ●"
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.EXPERT_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "cc":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help2'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text="● ◌ ◌"
        )
        await query.message.edit_text(
            text="● ● ◌"
        )
        await query.message.edit_text(
            text="● ● ●"
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.CC_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "fsub":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help2'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text="● ◌ ◌"
        )
        await query.message.edit_text(
            text="● ● ◌"
        )
        await query.message.edit_text(
            text="● ● ●"
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.FSUB_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "vsong":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help2'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text="● ◌ ◌"
        )
        await query.message.edit_text(
            text="● ● ◌"
        )
        await query.message.edit_text(
            text="● ● ●"
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.VSONG,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "gpt":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help2'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text="● ◌ ◌"
        )
        await query.message.edit_text(
            text="● ● ◌"
        )
        await query.message.edit_text(
            text="● ● ●"
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.CHATAI,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "encrypt":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help2'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text="● ◌ ◌"
        )
        await query.message.edit_text(
            text="● ● ◌"
        )
        await query.message.edit_text(
            text="● ● ●"
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.ENCRYPT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "ytsearch":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help2'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text="● ◌ ◌"
        )
        await query.message.edit_text(
            text="● ● ◌"
        )
        await query.message.edit_text(
            text="● ● ●"
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.YTSEARCH,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "figletx":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help2'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text="● ◌ ◌"
        )
        await query.message.edit_text(
            text="● ● ◌"
        )
        await query.message.edit_text(
            text="● ● ●"
        )
        
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        
        await query.message.edit_text(
            text=script.FIGLET_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        
    elif query.data == "wall":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help2'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text="● ◌ ◌"
        )
        await query.message.edit_text(
            text="● ● ◌"
        )
        await query.message.edit_text(
            text="● ● ●"
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.WALL,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "grpinfo":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help2'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text="● ◌ ◌"
        )
        await query.message.edit_text(
            text="● ● ◌"
        )
        await query.message.edit_text(
            text="● ● ●"
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.GROUPDATA,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "tagall":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help2'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text="● ◌ ◌"
        )
        await query.message.edit_text(
            text="● ● ◌"
        )
        await query.message.edit_text(
            text="● ● ●"
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.TAGALL,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "bgremove":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help2'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text="● ◌ ◌"
        )
        await query.message.edit_text(
            text="● ● ◌"
        )
        await query.message.edit_text(
            text="● ● ●"
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.BG_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "ringtune":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help2'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text="● ◌ ◌"
        )
        await query.message.edit_text(
            text="● ● ◌"
        )
        await query.message.edit_text(
            text="● ● ●"
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.RING_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "fun":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help2'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text="● ◌ ◌"
        )
        await query.message.edit_text(
            text="● ● ◌"
        )
        await query.message.edit_text(
            text="● ● ●"
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.FUN_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "mongochk":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help2'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', callback_data='group_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text="● ◌ ◌"
        )
        await query.message.edit_text(
            text="● ● ◌"
        )
        await query.message.edit_text(
            text="● ● ●"
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.MONGO_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    
    elif query.data == "stats":
        buttons = [[
            InlineKeyboardButton('⇇ ʙᴀᴄᴋ', callback_data='about'),
            InlineKeyboardButton('⟲ ʀᴇғʀᴇsʜ', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "rfrsh":
        await query.answer("ꜰᴇᴛᴄʜɪɴɢ ᴍᴏɴɢᴏ-ᴅʙ ᴅᴀᴛᴀʙᴀꜱᴇ...")
        buttons = [[
            InlineKeyboardButton('⇇ ʙᴀᴄᴋ', callback_data='about'),
            InlineKeyboardButton('⟲ ʀᴇғʀᴇsʜ', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "shortlink_info":
            btn = [[
            InlineKeyboardButton("1 / 3", callback_data="pagesn1"),
            InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data="shortlink_info2")
            ],[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ⇋', callback_data='start')
            ]]
            reply_markup = InlineKeyboardMarkup(btn)
            await query.message.edit_text(
                text=(script.SHORTLINK_INFO),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )   
    elif query.data == "shortlink_info2":
            btn = [[
            InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data="shortlink_info"),
            InlineKeyboardButton("2 / 3", callback_data="pagesn1"),
            InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data="shortlink_info3")
            ],[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ⇋', callback_data='start')
            ]]
            reply_markup = InlineKeyboardMarkup(btn)
            await query.message.edit_text(
                text=(script.SHORTLINK_INFO2),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
    elif query.data == "shortlink_info3":
            btn = [[
            InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data="shortlink_info2"),
            InlineKeyboardButton("3 / 3", callback_data="pagesn1")
            ],[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ⇋', callback_data='start')
            ]]
            reply_markup = InlineKeyboardMarkup(btn)
            await query.message.edit_text(
                text=(script.SHORTLINK_INFO3),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )   
    
    elif query.data == "disclaimer":
            btn = [[
                    InlineKeyboardButton("⇋ ʙᴀᴄᴋ ⇋", callback_data="about")
                  ]]
            reply_markup = InlineKeyboardMarkup(btn)
            await query.message.edit_text(
                text=(script.DISCLAIMER_TXT),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML 
            )
    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))

        if str(grp_id) != str(grpid):
            await query.message.edit("Vᴏᴛʀᴇ Cᴏɴɴᴇxɪᴏɴ Aᴄᴛɪᴠᴇ A Éᴛé Mᴏᴅɪғɪéᴇ. Aʟʟᴇᴢ ᴅᴀɴs /connections ᴘᴏᴜʀ ᴄʜᴀɴɢᴇʀ ᴠᴏᴛʀᴇ ᴄᴏɴɴᴇxɪᴏɴ ᴀᴄᴛɪᴠᴇ.")
            return await query.answer(MSG_ALRT)

        if set_type == 'is_shortlink' and query.from_user.id not in ADMINS:
            return await query.answer(text=f"Hᴇʏ {query.from_user.first_name}, Vᴏᴜs ɴᴇ ᴘᴏᴜᴠᴇᴢ ᴘᴀs ᴍᴏᴅɪғɪᴇʀ ʟᴇs ᴘᴀʀᴀᴍèᴛʀᴇs ᴅᴇ ʟɪᴇɴs ᴄᴏᴜʀᴛs ᴘᴏᴜʀ ᴠᴏᴛʀᴇ ɢʀᴏᴜᴘᴇ !\n\nC'ᴇsᴛ ᴜɴ ᴘᴀʀᴀᴍèᴛʀᴇ ʀéꜱᴇʀᴠé ᴀᴜx ᴀᴅᴍɪɴɪꜱᴛʀᴀᴛᴇᴜʀs !", show_alert=True)

        if status == "True":
            await save_group_settings(grpid, set_type, False)
        else:
            await save_group_settings(grpid, set_type, True)

        settings = await get_settings(grpid)

        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('ᴘᴀɢᴇ ᴅᴇ ʀéꜱᴜʟᴛᴀᴛꜱ',
                                        callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ʙᴏᴜᴛᴏɴ' if settings["button"] else 'ᴛᴇxᴛ',
                                        callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ᴍᴏᴅᴇ ᴇɴᴠᴏɪ ᴅᴇ ꜰɪᴄʜɪᴇʀ', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴅéᴍᴀʀʀᴇʀ' if settings["botpm"] else 'ᴀᴜᴛᴏ',
                                        callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ꜱéᴄᴜʀɪᴛé ᴅᴇꜱ ꜰɪᴄʜɪᴇʀꜱ',
                                        callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴀᴄᴛɪᴠᴇʀ' if settings["file_secure"] else 'ᴅéꜱᴀᴄᴛɪᴠᴇʀ',
                                        callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ᴀꜰꜰɪᴄʜᴇ IMDB', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴀᴄᴛɪᴠᴇʀ' if settings["imdb"] else 'ᴅéꜱᴀᴄᴛɪᴠᴇʀ',
                                        callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ᴠéʀɪꜰɪᴄᴀᴛɪᴏɴ ᴏʀᴛʜᴏɢʀᴀᴘʜɪǫᴜᴇ',
                                        callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴀᴄᴛɪᴠᴇʀ' if settings["spell_check"] else 'ᴅéꜱᴀᴄᴛɪᴠᴇʀ',
                                        callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ᴍᴇꜱꜱᴀɢᴇ ᴅᴇ ʙɪᴇɴᴠᴇɴᴜᴇ', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴀᴄᴛɪᴠᴇʀ' if settings["welcome"] else 'ᴅéꜱᴀᴄᴛɪᴠᴇʀ',
                                        callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ꜱᴜᴘᴘʀᴇꜱꜱɪᴏɴ ᴀᴜᴛᴏᴍᴀᴛɪǫᴜᴇ',
                                        callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴀᴄᴛɪᴠᴇʀ' if settings["auto_delete"] else 'ᴅéꜱᴀᴄᴛɪᴠᴇʀ',
                                        callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ꜰɪʟᴛʀᴇ ᴀᴜᴛᴏᴍᴀᴛɪǫᴜᴇ',
                                        callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴀᴄᴛɪᴠᴇʀ' if settings["auto_ffilter"] else 'ᴅéꜱᴀᴄᴛɪᴠᴇʀ',
                                        callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ɴᴏᴍʙʀᴇ ᴍᴀx ᴅᴇ ʙᴏᴜᴛᴏɴꜱ',
                                        callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                    InlineKeyboardButton('10' if settings["max_btn"] else f'{MAX_B_TN}',
                                        callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ʟɪᴇɴꜱ ᴄᴏᴜʀᴛꜱ',
                                        callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴀᴄᴛɪᴠᴇʀ' if settings["is_shortlink"] else 'ᴅéꜱᴀᴄᴛɪᴠᴇʀ',
                                        callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('⇋ ꜰᴇʀᴍᴇʀ ʟᴇ ᴍᴇɴᴜ ᴅᴇꜱ ᴘᴀʀᴀᴍèᴛʀᴇꜱ ⇋', 
                                        callback_data='close_data'
                                        )
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)
        await query.answer(MSG_ALRT)
    
async def auto_filter(client, msg, spoll=False):
    curr_time = datetime.now(pytz.timezone('Africa/kinshasa')).time()
    # reqstr1 = msg.from_user.id if msg.from_user else 0
    # reqstr = await client.get_users(reqstr1)
    
    if not spoll:
        message = msg
        if message.text.startswith("/"): return  # ignore commands
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if len(message.text) < 100:
            search = message.text
            m=await message.reply_text(f"🔎")
            search = search.lower()
            find = search.split("ᴡᴀɪᴛ ʙʀᴏ..")
            search = ""
            removes = ["in","upload", "series", "full", "horror", "thriller", "mystery", "print", "file"]
            for x in find:
                # if x == "in" or x == "upload" or x == "series" or x == "full" or x == "horror" or x == "thriller" or x == "mystery" or x == "print" or x == "subtitle" or x == "subtitles":
                #     continue
                if x in removes:
                    continue
                else:
                    search = search + x + " "
            search = re.sub(r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|bro|bruh|broh|helo|that|find|dubbed|link|venum|iruka|pannunga|pannungga|anuppunga|anupunga|anuppungga|anupungga|film|undo|kitti|kitty|tharu|kittumo|kittum|movie|any(one)|with\ssubtitle(s)?)", "", search, flags=re.IGNORECASE)
            search = re.sub(r"\s+", " ", search).strip()
            search = search.replace("-", " ")
            search = search.replace(":","")
            files, offset, total_results = await get_search_results(message.chat.id ,search, offset=0, filter=True)
            settings = await get_settings(message.chat.id)
            if not files:
                await m.delete()
                if settings["spell_check"]:
                    return await advantage_spell_chok(client, msg)
                else:
                    # if NO_RESULTS_MSG:
                    #     await client.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, search)))
                    return
        else:
            return
    else:
        message = msg.message.reply_to_message  # msg will be callback query
        search, files, offset, total_results = spoll
        m=await message.reply_text(f"🔎")
        settings = await get_settings(message.chat.id)
        await msg.message.delete()
    # if 'is_shortlink' in settings.keys():
    #     ENABLE_SHORTLINK = settings['is_shortlink']
    # else:
    #     await save_group_settings(message.chat.id, 'is_shortlink', False)
    #     ENABLE_SHORTLINK = False
    # if 'is_tutorial' in settings.keys():
    #     ENABLE_TUTORIAL = settings['is_tutorial']
    # else:
    #     await save_group_settings(message.chat.id, 'is_tutorial', False)
    #     ENABLE_TUTORIAL = False
    pre = 'filep' if settings['file_secure'] else 'file'
    key = f"{message.chat.id}-{message.id}"
    FRESH[key] = search
    temp.GETALL[key] = files
    temp.SHORT[message.from_user.id] = message.chat.id
    if settings["button"]:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"[{get_size(file.file_size)}] {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'), file.file_name.split()))}", callback_data=f'{pre}#{file.file_id}'
                ),
            ]
            for file in files
        ]
    # else:
    #     btn = [
    #         [
    #             InlineKeyboardButton(
    #                 text=f"{' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'), file.file_name.split()))}",
    #                 callback_data=f'{pre}#{file.file_id}',
    #             ),
    #             InlineKeyboardButton(
    #                 text=f"{get_size(file.file_size)}",
    #                 callback_data=f'{pre}#{file.file_id}',
    #             ),
    #         ]
    #         for file in files
    #     ]
        btn.insert(0, 
            [
                InlineKeyboardButton("⇈ ꜱᴇʟᴇᴄᴛ ᴏᴘᴛɪᴏɴꜱ ʜᴇʀᴇ ⇈", 'reqinfo')
            ]
        )
        btn.insert(0, 
            [
                InlineKeyboardButton(f'ǫᴜᴀʟɪᴛʏ', callback_data=f"qualities#{key}"),
                InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}"),
                InlineKeyboardButton("ꜱᴇᴀsᴏɴ",  callback_data=f"seasons#{key}")
            ]
        )
        btn.insert(0, [
            InlineKeyboardButton("ᴘʀᴇᴍɪᴜᴍ", url=f"https://t.me/hyoshcoder"),
            InlineKeyboardButton("sᴇɴᴅ ᴀʟʟ", callback_data=f"sendfiles#{key}")
        ])

    else:
        btn = []
        btn.insert(0, 
            [
                InlineKeyboardButton("⇈ ꜱᴇʟᴇᴄᴛ ᴏᴘᴛɪᴏɴꜱ ʜᴇʀᴇ ⇈", 'reqinfo')
            ]
        )
        btn.insert(0, 
            [
                InlineKeyboardButton(f'ǫᴜᴀʟɪᴛʏ', callback_data=f"qualities#{key}"),
                InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}"),
                InlineKeyboardButton("ꜱᴇᴀsᴏɴ",  callback_data=f"seasons#{key}")
            ]
        )
        btn.insert(0, [
            InlineKeyboardButton("ᴘʀᴇᴍɪᴜᴍ", url=f"https://t.me/hyoshcoder"),
            InlineKeyboardButton("sᴇɴᴅ ᴀʟʟ", callback_data=f"sendfiles#{key}")
        ])

    if offset != "":
        req = message.from_user.id if message.from_user else 0
        try:
            if settings['max_btn']:
                btn.append(
                    [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⇛",callback_data=f"next_{req}_{key}_{offset}")]
                )
            else:
                btn.append(
                    [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⇛",callback_data=f"next_{req}_{key}_{offset}")]
                )
        except KeyError:
            await save_group_settings(message.chat.id, 'max_btn', True)
            btn.append(
                [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⇛",callback_data=f"next_{req}_{key}_{offset}")]
            )
    else:
        btn.append(
            [InlineKeyboardButton(text="↭ ɴᴏ ᴍᴏʀᴇ ᴘᴀɢᴇꜱ ᴀᴠᴀɪʟᴀʙʟᴇ ↭",callback_data="pages")]
        )
    imdb = await get_poster(search, file=(files[0]).file_name) if settings["imdb"] else None
    cur_time = datetime.now(pytz.timezone('Africa/kinshasa')).time()
    time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
    remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
    TEMPLATE = script.IMDB_TEMPLATE_TXT
    if imdb:
        cap = TEMPLATE.format(
            query=search,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            **locals()
        )
        if not settings["button"]:
            cap+="<b>\n\n<u>❍ Requested Files 👇</u></b>\n"
            for file in files:
                cap += f"<b>\n❍ <a href='https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}'>[{get_size(file.file_size)}] {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'), file.file_name.split()))}\n</a></b>"
    else:
        if settings["button"]:
            cap = f"<b>• ᴛɪᴛʟᴇ : <code>{search}</code>\n\n• ᴛᴏᴛᴀʟ ꜰɪʟᴇꜱ : <code>{total_results}</code>\n• ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ : {message.from_user.mention}\n• ʀᴇsᴜʟᴛ ɪɴ : <code>{remaining_seconds} Sᴇᴄᴏɴᴅs</code>\n\n• ᴘᴏᴡᴇʀᴇᴅ ʙʏ : {message.chat.title} \n\n</b>"
        else:
            # cap = f"<b>Hᴇʏ {message.from_user.mention}, Hᴇʀᴇ ɪs ᴛʜᴇ ʀᴇsᴜʟᴛ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {search} \n\n</b>"
            cap = f"<b>• ᴛɪᴛʟᴇ : <code>{search}</code>\n\n• ᴛᴏᴛᴀʟ ꜰɪʟᴇꜱ : <code>{total_results}</code>\n• ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ : {message.from_user.mention}\n• ʀᴇsᴜʟᴛ ɪɴ : <code>{remaining_seconds} Sᴇᴄᴏɴᴅs</code>\n\n• ᴘᴏᴡᴇʀᴇᴅ ʙʏ : {message.chat.title} \n\n</b>"
            cap+="<b><u>❍ Requested Files 👇</u></b>\n\n"
            for file in files:
                cap += f"<b>❍ <a href='https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}'>[{get_size(file.file_size)}] {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'), file.file_name.split()))}\n\n</a></b>"

    if imdb and imdb.get('poster'):
        try:
            hehe = await message.reply_photo(photo=imdb.get('poster'), caption=cap, reply_markup=InlineKeyboardMarkup(btn))
            await m.delete()
            try:
                if settings['auto_delete']:
                    await asyncio.sleep(300)
                    await hehe.delete()
                    await message.delete()
            except KeyError:
                await save_group_settings(message.chat.id, 'auto_delete', True)
                await asyncio.sleep(300)
                await hehe.delete()
                await message.delete()
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg") 
            hmm = await message.reply_photo(photo=poster, caption=cap, reply_markup=InlineKeyboardMarkup(btn))
            await m.delete()
            try:
               if settings['auto_delete']:
                    await asyncio.sleep(300)
                    m=await message.reply_text("🔎")
                    await hmm.delete()
                    await message.delete()
            except KeyError:
                await save_group_settings(message.chat.id, 'auto_delete', True)
                await asyncio.sleep(300)
                await hmm.delete()
                await message.delete()
        except Exception as e:
            logger.exception(e)
            m=await message.reply_text("🔎") 
            fek = await message.reply_text(text=cap, reply_markup=InlineKeyboardMarkup(btn))
            await m.delete()
            try:
                if settings['auto_delete']:
                    await asyncio.sleep(300)
                    await fek.delete()
                    await message.delete()
            except KeyError:
                await save_group_settings(message.chat.id, 'auto_delete', True)
                await asyncio.sleep(300)
                await fek.delete()
                await message.delete()
    else:
        fuk = await message.reply_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        await m.delete()
        try:
            if settings['auto_delete']:
                await asyncio.sleep(300)
                await fuk.delete()
                await message.delete()
        except KeyError:
            await save_group_settings(message.chat.id, 'auto_delete', True)
            await asyncio.sleep(300)
            await fuk.delete()
            await message.delete()
    # if spoll:
    #     await msg.message.delete()


async def advantage_spell_chok(client, msg):
    mv_id = msg.id
    mv_rqst = msg.text
    reqstr1 = msg.from_user.id if msg.from_user else 0
    reqstr = await client.get_users(reqstr1)
    settings = await get_settings(msg.chat.id)
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", msg.text, flags=re.IGNORECASE)  # plis contribute some common words
    query = query.strip() + " movie"
    try:
        movies = await get_poster(mv_rqst, bulk=True)
    except Exception as e:
        logger.exception(e)
        reqst_gle = mv_rqst.replace(" ", "+")
        button = [[
                   InlineKeyboardButton("ɢᴏᴏɢʟᴇ ᴋᴀʀᴏ ʙʜᴀɪ", url=f"https://www.google.com/search?q={reqst_gle}")
        ]]
        if NO_RESULTS_MSG:
            await client.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, mv_rqst)))
        k = await msg.reply_photo(
            photo=SPELL_IMG, 
            caption=script.I_CUDNT.format(mv_rqst),
            reply_markup=InlineKeyboardMarkup(button)
        )
        await asyncio.sleep(30)
        await k.delete()
        return
    movielist = []
    if not movies:
        reqst_gle = mv_rqst.replace(" ", "+")
        button = [[
                   InlineKeyboardButton("ɢᴏᴏɢʟᴇ ᴋᴀʀᴏ ʙʜᴀɪ", url=f"https://www.google.com/search?q={reqst_gle}")
        ]]
        if NO_RESULTS_MSG:
            await client.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, mv_rqst)))
        k = await msg.reply_photo(
            photo=SPELL_IMG, 
            caption=script.I_CUDNT.format(mv_rqst),
            reply_markup=InlineKeyboardMarkup(button)
        )
        await asyncio.sleep(30)
        await k.delete()
        return
    movielist += [movie.get('title') for movie in movies]
    movielist += [f"{movie.get('title')} {movie.get('year')}" for movie in movies]
    SPELL_CHECK[mv_id] = movielist
    btn = [
        [
            InlineKeyboardButton(
                text=movie_name.strip(),
                callback_data=f"spol#{reqstr1}#{k}",
            )
        ]
        for k, movie_name in enumerate(movielist)
    ]
    btn.append([InlineKeyboardButton(text="Close", callback_data=f'spol#{reqstr1}#close_spellcheck')])
    spell_check_del = await msg.reply_photo(
        photo=(SPELL_IMG),
        caption=(script.CUDNT_FND.format(mv_rqst)),
        reply_markup=InlineKeyboardMarkup(btn)
    )
    try:
        if settings['auto_delete']:
            await asyncio.sleep(600)
            await spell_check_del.delete()
    except KeyError:
            grpid = await active_connection(str(msg.from_user.id))
            await save_group_settings(grpid, 'auto_delete', True)
            settings = await get_settings(msg.chat.id)
            if settings['auto_delete']:
                await asyncio.sleep(600)
                await spell_check_del.delete()


async def manual_filters(client, message, text=False):
    settings = await get_settings(message.chat.id)
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            joelkb = await client.send_message(
                                group_id, 
                                reply_text, 
                                disable_web_page_preview=True,
                                protect_content=True if settings["file_secure"] else False,
                                reply_to_message_id=reply_id
                            )
                            try:
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                                    try:
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                else:
                                    try:
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)

                        else:
                            button = eval(btn)
                            joelkb = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                protect_content=True if settings["file_secure"] else False,
                                reply_to_message_id=reply_id
                            )
                            try:
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                                    try:
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                else:
                                    try:
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)

                    elif btn == "[]":
                        joelkb = await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            protect_content=True if settings["file_secure"] else False,
                            reply_to_message_id=reply_id
                        )
                        try:
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)
                                try:
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                            else:
                                try:
                                    if settings['auto_delete']:
                                        await asyncio.sleep(600)
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await asyncio.sleep(600)
                                        await joelkb.delete()
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, 'auto_ffilter', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)

                    else:
                        button = eval(btn)
                        joelkb = await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                        try:
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)
                                try:
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                            else:
                                try:
                                    if settings['auto_delete']:
                                        await asyncio.sleep(600)
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await asyncio.sleep(600)
                                        await joelkb.delete()
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, 'auto_ffilter', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)

                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False

async def global_filters(client, message, text=False):
    settings = await get_settings(message.chat.id)
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_gfilters('gfilters')
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_gfilter('gfilters', keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            joelkb = await client.send_message(
                                group_id, 
                                reply_text, 
                                disable_web_page_preview=True,
                                reply_to_message_id=reply_id
                            )
                            manual = await manual_filters(client, message)
                            if manual == False:
                                settings = await get_settings(message.chat.id)
                                try:
                                    if settings['auto_ffilter']:
                                        await auto_filter(client, message)
                                        try:
                                            if settings['auto_delete']:
                                                await joelkb.delete()
                                        except KeyError:
                                            grpid = await active_connection(str(message.from_user.id))
                                            await save_group_settings(grpid, 'auto_delete', True)
                                            settings = await get_settings(message.chat.id)
                                            if settings['auto_delete']:
                                                await joelkb.delete()
                                    else:
                                        try:
                                            if settings['auto_delete']:
                                                await asyncio.sleep(600)
                                                await joelkb.delete()
                                        except KeyError:
                                            grpid = await active_connection(str(message.from_user.id))
                                            await save_group_settings(grpid, 'auto_delete', True)
                                            settings = await get_settings(message.chat.id)
                                            if settings['auto_delete']:
                                                await asyncio.sleep(600)
                                                await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_ffilter', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_ffilter']:
                                        await auto_filter(client, message) 
                            else:
                                try:
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                            
                        else:
                            button = eval(btn)
                            joelkb = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id=reply_id
                            )
                            manual = await manual_filters(client, message)
                            if manual == False:
                                settings = await get_settings(message.chat.id)
                                try:
                                    if settings['auto_ffilter']:
                                        await auto_filter(client, message)
                                        try:
                                            if settings['auto_delete']:
                                                await joelkb.delete()
                                        except KeyError:
                                            grpid = await active_connection(str(message.from_user.id))
                                            await save_group_settings(grpid, 'auto_delete', True)
                                            settings = await get_settings(message.chat.id)
                                            if settings['auto_delete']:
                                                await joelkb.delete()
                                    else:
                                        try:
                                            if settings['auto_delete']:
                                                await asyncio.sleep(600)
                                                await joelkb.delete()
                                        except KeyError:
                                            grpid = await active_connection(str(message.from_user.id))
                                            await save_group_settings(grpid, 'auto_delete', True)
                                            settings = await get_settings(message.chat.id)
                                            if settings['auto_delete']:
                                                await asyncio.sleep(600)
                                                await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_ffilter', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_ffilter']:
                                        await auto_filter(client, message) 
                            else:
                                try:
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await joelkb.delete()

                    elif btn == "[]":
                        joelkb = await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id=reply_id
                        )
                        manual = await manual_filters(client, message)
                        if manual == False:
                            settings = await get_settings(message.chat.id)
                            try:
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                                    try:
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                else:
                                    try:
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message) 
                        else:
                            try:
                                if settings['auto_delete']:
                                    await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_delete', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_delete']:
                                    await joelkb.delete()

                    else:
                        button = eval(btn)
                        joelkb = await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                        manual = await manual_filters(client, message)
                        if manual == False:
                            settings = await get_settings(message.chat.id)
                            try:
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                                    try:
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                else:
                                    try:
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message) 
                        else:
                            try:
                                if settings['auto_delete']:
                                    await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_delete', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_delete']:
                                    await joelkb.delete()

                                
                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False
        movielist += [movie.get('title') for movie in movies]
        movielist += [f"{movie.get('title')} {movie.get('year')}" for movie in movies]
        SPELL_CHECK[mv_id] = movielist
        btn = [
            [
                InlineKeyboardButton(
                    text=movie_name.strip(),
                    callback_data=f"spol#{reqstr1}#{k}",
                )
            ]
            for k, movie_name in enumerate(movielist)
        ]
        btn.append([InlineKeyboardButton(text="↭ ᴄʟᴏꜱᴇ ↭", callback_data=f'spol#{reqstr1}#close_spellcheck')])
        spell_check_del = await msg.reply_text(
            text=script.CUDNT_FND.format(mv_rqst),
            reply_markup=InlineKeyboardMarkup(btn)
        )
        try:
            if settings['auto_delete']:
                await asyncio.sleep(600)
                await spell_check_del.delete()
        except KeyError:
                grpid = await active_connection(str(msg.from_user.id))
                await save_group_settings(grpid, 'auto_delete', True)
                settings = await get_settings(msg.chat.id)
                if settings['auto_delete']:
                    await asyncio.sleep(600)
                    await spell_check_del.delete()
 

async def manual_filters(client, message, text=False):
    settings = await get_settings(message.chat.id)
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            joelkb = await client.send_message(
                                group_id, 
                                reply_text, 
                                disable_web_page_preview=True,
                                protect_content=True if settings["file_secure"] else False,
                                reply_to_message_id=reply_id
                            )
                            try:
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                                    try:
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                else:
                                    try:
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)

                        else:
                            button = eval(btn)
                            joelkb = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                protect_content=True if settings["file_secure"] else False,
                                reply_to_message_id=reply_id
                            )
                            try:
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                                    try:
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                else:
                                    try:
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)

                    elif btn == "[]":
                        joelkb = await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            protect_content=True if settings["file_secure"] else False,
                            reply_to_message_id=reply_id
                        )
                        try:
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)
                                try:
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                            else:
                                try:
                                    if settings['auto_delete']:
                                        await asyncio.sleep(600)
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await asyncio.sleep(600)
                                        await joelkb.delete()
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, 'auto_ffilter', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)

                    else:
                        button = eval(btn)
                        joelkb = await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                        try:
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)
                                try:
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                            else:
                                try:
                                    if settings['auto_delete']:
                                        await asyncio.sleep(600)
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await asyncio.sleep(600)
                                        await joelkb.delete()
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, 'auto_ffilter', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)

                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False

async def global_filters(client, message, text=False):
    settings = await get_settings(message.chat.id)
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_gfilters('gfilters')
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_gfilter('gfilters', keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            joelkb = await client.send_message(
                                group_id, 
                                reply_text, 
                                disable_web_page_preview=True,
                                reply_to_message_id=reply_id
                            )
                            manual = await manual_filters(client, message)
                            if manual == False:
                                settings = await get_settings(message.chat.id)
                                try:
                                    if settings['auto_ffilter']:
                                        await auto_filter(client, message)
                                        try:
                                            if settings['auto_delete']:
                                                await joelkb.delete()
                                        except KeyError:
                                            grpid = await active_connection(str(message.from_user.id))
                                            await save_group_settings(grpid, 'auto_delete', True)
                                            settings = await get_settings(message.chat.id)
                                            if settings['auto_delete']:
                                                await joelkb.delete()
                                    else:
                                        try:
                                            if settings['auto_delete']:
                                                await asyncio.sleep(600)
                                                await joelkb.delete()
                                        except KeyError:
                                            grpid = await active_connection(str(message.from_user.id))
                                            await save_group_settings(grpid, 'auto_delete', True)
                                            settings = await get_settings(message.chat.id)
                                            if settings['auto_delete']:
                                                await asyncio.sleep(600)
                                                await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_ffilter', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_ffilter']:
                                        await auto_filter(client, message) 
                            else:
                                try:
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                            
                        else:
                            button = eval(btn)
                            joelkb = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id=reply_id
                            )
                            manual = await manual_filters(client, message)
                            if manual == False:
                                settings = await get_settings(message.chat.id)
                                try:
                                    if settings['auto_ffilter']:
                                        await auto_filter(client, message)
                                        try:
                                            if settings['auto_delete']:
                                                await joelkb.delete()
                                        except KeyError:
                                            grpid = await active_connection(str(message.from_user.id))
                                            await save_group_settings(grpid, 'auto_delete', True)
                                            settings = await get_settings(message.chat.id)
                                            if settings['auto_delete']:
                                                await joelkb.delete()
                                    else:
                                        try:
                                            if settings['auto_delete']:
                                                await asyncio.sleep(600)
                                                await joelkb.delete()
                                        except KeyError:
                                            grpid = await active_connection(str(message.from_user.id))
                                            await save_group_settings(grpid, 'auto_delete', True)
                                            settings = await get_settings(message.chat.id)
                                            if settings['auto_delete']:
                                                await asyncio.sleep(600)
                                                await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_ffilter', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_ffilter']:
                                        await auto_filter(client, message) 
                            else:
                                try:
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await joelkb.delete()

                    elif btn == "[]":
                        joelkb = await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id=reply_id
                        )
                        manual = await manual_filters(client, message)
                        if manual == False:
                            settings = await get_settings(message.chat.id)
                            try:
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                                    try:
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                else:
                                    try:
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message) 
                        else:
                            try:
                                if settings['auto_delete']:
                                    await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_delete', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_delete']:
                                    await joelkb.delete()

                    else:
                        button = eval(btn)
                        joelkb = await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                        manual = await manual_filters(client, message)
                        if manual == False:
                            settings = await get_settings(message.chat.id)
                            try:
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                                    try:
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                else:
                                    try:
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message) 
                        else:
                            try:
                                if settings['auto_delete']:
                                    await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_delete', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_delete']:
                                    await joelkb.delete()

                                
                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False