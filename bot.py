import sys
from pyromod import listen
import glob
import importlib
from pathlib import Path
from pyrogram import idle
import logging
import logging.config

logging.config.fileConfig('logging.conf')

# Configurer les niveaux de log des bibliothèques
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)


from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from database.ia_filterdb import Media
from database.users_chats_db import db
from info import *
from utils import temp
from typing import Union, Optional, AsyncGenerator
from pyrogram import types
from Script import script 
from datetime import date, datetime 
import pytz
from aiohttp import web
from plugins import web_server

import asyncio
from pyrogram import idle
from hisocode import hyoshcoder
from util.keepalive import ping_server
from hisocode.clients import initialize_clients

ppath = "plugins/*.py"
files = glob.glob(ppath)

async def Lazy_start():
    print('\n')
    print('Initializing hisocode Bot')
    
    await hyoshcoder.start()
    
    bot_info = await hyoshcoder.get_me()
    hyoshcoder.username = bot_info.username
    
    await initialize_clients()
    
    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"plugins/{plugin_name}.py")
            import_path = "plugins.{}".format(plugin_name)
            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules["plugins." + plugin_name] = load 
            print("Hokage Imported => " + plugin_name)
    
    if ON_HEROKU:
        asyncio.create_task(ping_server())
    
    b_users, b_chats = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats
    
    await Media.ensure_indexes()
    
    me = await hyoshcoder.get_me()
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    hyoshcoder.username = '@' + me.username
    
    logging.info(f"{me.first_name} with for Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
    logging.info(LOG_STR)
    logging.info(script.LOGO)
    
    tz = pytz.timezone('Africa/kinshasa')
    today = date.today()
    now = datetime.now(tz)
    time = now.strftime("%H:%M:%S %p")
    
    try:
        await hyoshcoder.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(today, time))
    except Exception as e:
        logging.error(f"Failed to send message to LOG_CHANNEL: {e}")
    
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, PORT).start()
    
    await idle()

if __name__ == '__main__':
    loop = asyncio.get_event_loop() 
    try:
        loop.run_until_complete(Lazy_start()) 
    except KeyboardInterrupt:
        logging.info('Service Stopped Bye 👋')
    finally:
        loop.close()  