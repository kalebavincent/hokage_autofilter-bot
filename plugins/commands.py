# credit @hyoshcoder

import os
import logging
import random
import asyncio
import pytz
from database.refer import referdb
from Script import Script
from datetime import datetime
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import *
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id, get_bad_files
from database.users_chats_db import db, delete_all_referal_users, get_referal_users_count, get_referal_all_users, referal_add_user
from info import *
from utils import get_settings, get_size, is_req_subscribed, save_group_settings, temp, verify_user, check_token, check_verification, get_token, get_shortlink, get_tutorial
from database.connections_mdb import active_connection
# from plugins.pm_filter import ENABLE_SHORTLINK
import re, asyncio, os, sys
import json
import base64
logger = logging.getLogger(__name__)

TIMEZONE = "UTC"
BATCH_FILES = {}

@Client.on_message(filters.command("gsend") & filters.user(ADMINS))
async def send_chatmsg(bot, message):
    if message.reply_to_message:
        target_id = message.text
        command = ["/gsend"]
        for cmd in command:
            if cmd in target_id:
                target_id = target_id.replace(cmd, "")
        success = False
        try:
            chat = await bot.get_chat(int(target_id))
            await message.reply_to_message.copy(int(chat.id))
            success = True
        except Exception as e:
            await message.reply_text(f"Erreur : <code>{e}</code>")
        if success:
            await message.reply_text(f"Votre message a été envoyé avec succès à {chat.id}.")
        else:
            await message.reply_text("Une erreur est survenue !")
    else:
        await message.reply_text("Commande incomplète...")

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    # try:
    #     await message.react(emoji=random.choice(REACTIONS), big=True)
    # except:
    #     await message.react(emoji="⚡️", big=True)
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [[
                    InlineKeyboardButton('• Ajouter moi à votre chat •', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                ],[
                    InlineKeyboardButton('• Master •', url="https://t.me/hyoshcoder"),
                    InlineKeyboardButton('• Support •', url='https://t.me/hyoshcoder')
                ],[
                    InlineKeyboardButton('• Rejoindre le canal des mises à jour •', url="https://t.me/hyoshcoder")
                  ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply(Script.GSTART_TXT.format(message.from_user.mention if message.from_user else message.chat.title, temp.U_NAME, temp.B_NAME), reply_markup=reply_markup, disable_web_page_preview=True)
        await asyncio.sleep(2) # 😢 https://github.com/EvamariaTG/EvaMaria/blob/master/plugins/p_ttishow.py#L17 😬 wait a bit, before checking.
        if not await db.get_chat(message.chat.id):
            total=await client.get_chat_members_count(message.chat.id)
            await client.send_message(LOG_CHANNEL, Script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown"))       
            await db.add_chat(message.chat.id, message.chat.title)
        return 
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, Script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))
    if len(message.command) != 2:
        buttons = [[
                    InlineKeyboardButton(text="🏡", callback_data="start"),
                    InlineKeyboardButton(text="🛡", callback_data="group_info"),
                    InlineKeyboardButton(text="💳", callback_data="about"),
                    InlineKeyboardButton(text="💸", callback_data="shortlink_info"),
                    InlineKeyboardButton(text="🖥", callback_data="main"),
                ],[
                    InlineKeyboardButton('Ajouter moi à votre groupe', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
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
            gtxt = "Bon après midi 👋"
        elif curr_time < 21:
            gtxt = "Bonsoir 👋"
        else:
            gtxt = "Bonne nuit 👋"
        m=await message.reply_text("salut baby, \nPatiencez un instant...")
        await asyncio.sleep(0.4)
        await m.edit_text("🎊")
        await asyncio.sleep(0.5)
        await m.edit_text("⚡")
        await asyncio.sleep(0.5)
        await m.edit_text("Demmarage en cours...")
        await asyncio.sleep(0.4)
        await m.delete()        
        m=await message.reply_sticker("CAACAgEAAxkBAAICL2ezspj07GuYLxHBn2JhmwMnRMtYAALJBwAC43gEAAGESQ6JsVOaWx4E") 
        await asyncio.sleep(1)
        await m.delete()
        m = await message.reply_photo(
            photo=random.choice(PICS),
            caption=Script.START_TXT.format(message.from_user.mention, gtxt, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
            has_spoiler=True  
        )
        try:
            await message.react(emoji=random.choice(REACTIONS), big=True)
        except:
            await message.react(emoji="⚡️", big=True)
        return
        
    if AUTH_CHANNEL and not await is_req_subscribed(client, message):
        try:
            invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL), creates_join_request=True)
        except ChatAdminRequired:
            logger.error("Make sure Bot is admin in Forcesub channel")
            return
        btn = [
                [
                    InlineKeyboardButton(
                        "• Rejoindre le canal •", url=invite_link.invite_link
                    ),
                    InlineKeyboardButton(
                        text="• Mises à jour •",
                        url="https://t.me/hyoshcoder"
                    ),
                ]
                
            ]

        if message.command[1] != "subscribe":
            try:
                kk, file_id = message.command[1].split("_", 1)
                btn.append([InlineKeyboardButton("• Essayer à nouveau •", callback_data=f"checksub#{kk}#{file_id}")])
            except (IndexError, ValueError):
                btn.append([InlineKeyboardButton("• Essayer à nouveau •", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])
            await client.send_photo(
                chat_id=message.from_user.id,
                photo="https://graph.org/file/9649c1dcbae09f2e7700e.jpg",
                caption="Rejoignez notre canal de mises à jour et cliquez ensuite sur 'Essayer à nouveau' pour obtenir votre fichier demandé.",
                reply_markup=InlineKeyboardMarkup(btn),
                parse_mode=enums.ParseMode.MARKDOWN
            )
            return

    if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
        buttons = [[
                    InlineKeyboardButton(text="🏡", callback_data="start"),
                    InlineKeyboardButton(text="🛡", callback_data="group_info"),
                    InlineKeyboardButton(text="💳", callback_data="about"),
                    InlineKeyboardButton(text="💸", callback_data="shortlink_info"),
                    InlineKeyboardButton(text="🖥", callback_data="main"),
                ],[
                    InlineKeyboardButton('Ajoute-moi à ton groupe', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                ],[
                    InlineKeyboardButton('• Commandes •', callback_data='main'),
                    InlineKeyboardButton('• Gagne de l\'argent •', callback_data='shortlink_info')
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
        m=await message.reply_text("Salut, comment ça va ? \nAttends un instant...")
        await asyncio.sleep(0.4)
        await m.edit_text("🎊")
        await asyncio.sleep(0.5)
        await m.edit_text("⚡")
        await asyncio.sleep(0.5)
        await m.edit_text("Démarrage en cours...")
        await asyncio.sleep(0.4)
        await m.delete()        
        m=await message.reply_sticker("CAACAgUAAxkBAAECroBmQKMAAQ-Gw4nibWoj_pJou2vP1a4AAlQIAAIzDxlVkNBkTEb1Lc4eBA") 
        await asyncio.sleep(1)
        await m.delete()
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=Script.START_TXT.format(message.from_user.mention, gtxt, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return

    if message.command[1].startswith("reff_"):
        try:
            user_id = int(message.command[1].split("_")[1])
        except ValueError:
            await message.reply_text("Référent invalide !")
            return
        if user_id == message.from_user.id:
            await message.reply_text("Hé mec, tu ne peux pas te référer toi-même 🤣!\n\nPartage le lien avec tes amis et obtiens 10 points de parrainage. Si tu collectes 100 points de parrainage, tu peux obtenir 1 mois d'abonnement Premium gratuit.")
            return
        if referdb.is_user_in_list(message.from_user.id):
            await message.reply_text("Tu as déjà été invité ❗")
            return
        try:
            uss = await client.get_users(user_id)
        except Exception:
            return
        referdb.add_user(message.from_user.id)
        fromuse = referdb.get_refer_points(user_id) + 10
        if fromuse == 100:
            referdb.add_refer_points(user_id, 0) 
            await message.reply_text(f"🎉 Félicitations ! Tu as gagné 10 points de parrainage parce que tu as été invité avec succès ☞ {uss.mention}!")		    
            await message.reply_text(user_id, f"Tu as été invité avec succès par {message.from_user.mention}!") 	
            seconds = 2592000
            if seconds > 0:
                expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
                user_data = {"id": user_id, "expiry_time": expiry_time}  # Utilisation de "id" au lieu de "user_id"  
                await db.update_user(user_data)  # Utiliser la méthode update_user pour mettre à jour ou insérer les données utilisateur		    
                await client.send_message(
                chat_id=user_id,
                text=f"<b>Hé {uss.mention}\n\nTu as gagné 1 mois d'abonnement Premium en invitant 10 utilisateurs ❗", disable_web_page_preview=True              
                )
            for admin in ADMINS:
                await client.send_message(chat_id=admin, text=f"Tâche réussie complétée par cet utilisateur :\n\nNom d'utilisateur : {uss.mention}\n\nID utilisateur : {uss.id}!")	
        else:
            referdb.add_refer_points(user_id, fromuse)
            await message.reply_text(f"Tu as été invité avec succès par {uss.mention}!")
            await client.send_message(user_id, f"Félicitations ! Tu as gagné 10 points de parrainage parce que tu as été invité avec succès ☞{message.from_user.mention}!")
        return
        
    if len(message.command) == 2 and message.command[1] in ["premium"]:
        buttons = [[
                    InlineKeyboardButton('📲 Envoyer une capture d\'écran de paiement', user_id=int(6497757690))
                ],[ 
                    InlineKeyboardButton('❌ Fermer ❌', callback_data='close_data')
                ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=(SUBSCRIPTION),
            caption=Script.PREPLANS_TXT.format(message.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return  

    data = message.command[1]
    try:
        pre, file_id = data.split('_', 1)
    except:
        file_id = data
        pre = ""

    if data.split("-", 1)[0] == "BATCH":
        sts = await message.reply("<b>Veuillez patienter...</b>")
        file_id = data.split("-", 1)[1]
        msgs = BATCH_FILES.get(file_id)
        if not msgs:
            file = await client.download_media(file_id)
            try: 
                with open(file) as file_data:
                    msgs = json.loads(file_data.read())
            except:
                await sts.edit("ÉCHEC")
                return await client.send_message(LOG_CHANNEL, "IMPOSSIBLE D'OUVRIR LE FICHIER.")
            os.remove(file)
            BATCH_FILES[file_id] = msgs
        
        for msg in msgs:
            title = msg.get("title")
            size = get_size(int(msg.get("size", 0)))
            f_caption = msg.get("caption", "")
            if BATCH_FILE_CAPTION:
                try:
                    f_caption = BATCH_FILE_CAPTION.format(file_name='' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                except Exception as e:
                    logger.exception(e)
                    f_caption = f_caption
            if f_caption is None:
                f_caption = f"{title}"
            try:
                await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False),
                    reply_markup=InlineKeyboardMarkup(
                        [
                        [
                        InlineKeyboardButton('• Diffusion', callback_data=f'generate_stream_link:{file_id}'),
                        InlineKeyboardButton('Mises à jour •', url=GRP_LNK)
                        ]
                        ]
                    )
                )
            except FloodWait as e:
                await asyncio.sleep(e.x)
                logger.warning(f"Attente en raison du FloodWait de {e.x} sec.")
                await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False),
                    reply_markup=InlineKeyboardMarkup(
                        [
                        [
                        InlineKeyboardButton('• Diffusion', callback_data=f'generate_stream_link:{file_id}'),
                        InlineKeyboardButton('Mises à jour •', url=GRP_LNK)
                        ]
                        ]
                    )
                )
            except Exception as e:
                logger.warning(e, exc_info=True)
                continue
            await asyncio.sleep(1) 
        await sts.delete()
        return
    
    elif data.split("-", 1)[0] == "DSTORE":
        sts = await message.reply("<b>Veuillez patienter...</b>")
        b_string = data.split("-", 1)[1]
        decoded = (base64.urlsafe_b64decode(b_string + "=" * (-len(b_string) % 4))).decode("ascii")
        try:
            f_msg_id, l_msg_id, f_chat_id, protect = decoded.split("_", 3)
        except:
            f_msg_id, l_msg_id, f_chat_id = decoded.split("_", 2)
            protect = "/pbatch" if PROTECT_CONTENT else "batch"
        diff = int(l_msg_id) - int(f_msg_id)
        async for msg in client.iter_messages(int(f_chat_id), int(l_msg_id), int(f_msg_id)):
            if msg.media:
                media = getattr(msg, msg.media.value)
                if BATCH_FILE_CAPTION:
                    try:
                        f_caption = BATCH_FILE_CAPTION.format(file_name=getattr(media, 'file_name', ''), file_size=getattr(media, 'file_size', ''), file_caption=getattr(msg, 'caption', ''))
                    except Exception as e:
                        logger.exception(e)
                        f_caption = getattr(msg, 'caption', '')
                else:
                    media = getattr(msg, msg.media.value)
                    file_name = getattr(media, 'file_name', '')
                    f_caption = getattr(msg, 'caption', file_name)
                try:
                    await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                except Exception as e:
                    logger.exception(e)
                    continue
            elif msg.empty:
                continue
            else:
                try:
                    await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                except Exception as e:
                    logger.exception(e)
                    continue
            await asyncio.sleep(1) 
        return await sts.delete()

    elif data.split("-", 1)[0] == "verify":
        userid = data.split("-", 2)[1]
        token = data.split("-", 3)[2]
        if str(message.from_user.id) != str(userid):
            return await message.reply_text(
                text="<b>Lien invalide ou lien expiré !</b>",
                protect_content=True
            )
        is_valid = await check_token(client, userid, token)
        if is_valid == True:
            await message.reply_text(
                text=f"<b>Salut {message.from_user.mention}, vous êtes vérifié avec succès !\nVous avez maintenant un accès illimité à tous les films jusqu'à minuit ce soir.</b>",
                protect_content=True
            )
            await verify_user(client, userid, token)
        else:
            return await message.reply_text(
                text="<b>Lien invalide ou lien expiré !</b>",
                protect_content=True
            )
    if data.startswith("sendfiles"):
        protect_content = True
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
        chat_id = int("-" + file_id.split("-")[1])
        userid = message.from_user.id if message.from_user else None
        g = await get_shortlink(chat_id, f"https://telegram.me/{temp.U_NAME}?start=allfiles_{file_id}")
        k = await client.send_message(chat_id=message.from_user.id, text=f"<b>🫂 Salut {message.from_user.mention}, {gtxt}\n\n‼️ Obtenez tous les fichiers dans un seul lien ‼️\n\n✅ Votre lien est prêt, veuillez cliquer sur le bouton de téléchargement.\n\n</b>", reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('📁 Télécharger 📁', url=g)
                ], [
                    InlineKeyboardButton('⚡ Comment télécharger ⚡', url=await get_tutorial(chat_id))
                ], [
                    InlineKeyboardButton('✨ Acheter un abonnement : Supprimer les publicités ✨', callback_data="seeplans")                        
                ]
            ]
        ))
        await asyncio.sleep(300)
        await k.edit("<b>Votre message est supprimé !\nVeuillez rechercher à nouveau.</b>")
        return
        
    elif data.startswith("short"):
        protect_content = True
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
        user_id = message.from_user.id
        chat_id = temp.SHORT.get(user_id)
        files_ = await get_file_details(file_id)
        files = files_[0]
        g = await get_shortlink(chat_id, f"https://telegram.me/{temp.U_NAME}?start=file_{file_id}")
        k = await client.send_message(
            chat_id=user_id,
            text=f"<b>🫂 Salut {message.from_user.mention}, {gtxt}\n\n✅ Votre lien est prêt, veuillez cliquer sur le bouton de téléchargement.\n\n⚠️ Nom du fichier : <code>{files.file_name}</code> \n\n📥 Taille du fichier : <code>{get_size(files.file_size)}</code>\n\n</b>",
            reply_markup=InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton('📁 Télécharger 📁', url=g)
                ], [
                    InlineKeyboardButton('⚡ Comment télécharger ⚡', url=await get_tutorial(chat_id))
                ], [
                    InlineKeyboardButton('✨ Acheter un abonnement : supprimer les publicités ✨', callback_data="seeplans")
                ]]
            )
        )
        await asyncio.sleep(600)
        await k.edit("<b>Votre message a été supprimé ! Veuillez rechercher à nouveau.</b>")
        return

    elif data.startswith("all"):
        protect_content = True
        user_id = message.from_user.id
        files = temp.GETALL.get(file_id)
        if not files:
            return await message.reply('<b><i>Aucun fichier de ce type n\'existe !</b></i>')
        filesarr = []
        for file in files:
            file_id = file.file_id
            files_ = await get_file_details(file_id)
            files1 = files_[0]
            title = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), files1.file_name.split()))
            size = get_size(files1.file_size)
            f_caption = files1.caption
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                except Exception as e:
                    logger.exception(e)
                    f_caption = f_caption
            if f_caption is None:
                f_caption = f"{' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), files1.file_name.split()))}"

            if not await check_verification(client, message.from_user.id) and VERIFY == True:
                btn = [[
                    InlineKeyboardButton("♻️ Cliquez ici pour vérifier ♻️", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start="))
                ], [
                    InlineKeyboardButton("⁉️ Comment vérifier ⁉️", url=HOWTOVERIFY)
                ]]
                await message.reply_text(
                    text="<b>👋 Salut {message.from_user.mention}, vous êtes maintenant vérifié ✅\n\nMaintenant vous avez un accès illimité jusqu'à la prochaine vérification 🎉</b>",
                    protect_content=True,
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                return
            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                caption=f_caption,
                protect_content=True if pre == 'filep' else False,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton('• Stream', callback_data=f'generate_stream_link:{file_id}'),
                            InlineKeyboardButton('Mises à jour •', url=GRP_LNK)
                        ]
                    ]
                )
            )
            filesarr.append(msg)
        k = await client.send_message(
            chat_id=message.from_user.id,
            text=f"<b>❗️ <u>Important</u> ❗️</b>\n\n<b>Ces vidéos/fichiers seront supprimés dans</b> <b><u>10 minutes</u></b> <b>(en raison de problèmes de copyright).</b>\n\n<b><i>📌 Veuillez transférer ces vidéos/fichiers ailleurs et commencer à les télécharger là-bas.</i></b>"
        )
        await asyncio.sleep(600)
        for x in filesarr:
            await x.delete()
        await k.edit_text("<b>Vos vidéos/fichiers ont été supprimés avec succès ! Veuillez rechercher à nouveau.</b>")
        return
        
    elif data.startswith("files"):
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
        user_id = message.from_user.id
        if temp.SHORT.get(user_id)==None:
            return await message.reply_text(text="<b>Veuillez rechercher à nouveau dans le groupe</b>")
        else:
            chat_id = temp.SHORT.get(user_id)
        settings = await get_settings(chat_id)
        if not await db.has_premium_access(user_id) and settings['is_shortlink']: 
            files_ = await get_file_details(file_id)
            files = files_[0]
            g = await get_shortlink(chat_id, f"https://telegram.me/{temp.U_NAME}?start=file_{file_id}")
            k = await client.send_message(chat_id=message.from_user.id, text=f"🫂 Salut {message.from_user.mention}, {gtxt}\n\n✅ Ton lien est prêt, clique sur le bouton de téléchargement.\n\n⚠️ Nom du fichier : <code>{files.file_name}</code>\n\n📥 Taille du fichier : <code>{get_size(files.file_size)}</code>\n\n", reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton('📁 Télécharger 📁', url=g)
                    ], [
                        InlineKeyboardButton('⚡ Comment télécharger ⚡', url=await get_tutorial(chat_id))
                    ], [
                        InlineKeyboardButton('✨ Acheter un abonnement : Enlever les publicités ✨', callback_data="seeplans")                            
                    ]
                ]
            )
            )
            await asyncio.sleep(600)
            await k.edit("<b>Ton message a été supprimé !\nMerci de rechercher à nouveau.</b>")
            return
    user = message.from_user.id
    files_ = await get_file_details(file_id)           
    if not files_:
        pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
        try:
            if not await check_verification(client, message.from_user.id) and VERIFY == True:
                btn = [[
                    InlineKeyboardButton("♻️ Clique ici pour vérifier ♻️", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start="))
                ],[
                    InlineKeyboardButton("⁉️ Comment vérifier ⁉️", url=HOWTOVERIFY)
                ]]
                await message.reply_text(
                    text="<b>👋 Salut,\n\n📌 <u>Tu n'es pas vérifié aujourd'hui, merci de vérifier et d'obtenir un accès illimité jusqu'à la prochaine vérification</u>.</b>",
                    protect_content=True,
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                return
            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                protect_content=True if pre == 'filep' else False,
                reply_markup=InlineKeyboardMarkup(
                        [
                        [
                        InlineKeyboardButton('• Diffuser', callback_data=f'generate_stream_link:{file_id}'),
                        InlineKeyboardButton('Mises à jour •', url=GRP_LNK)
                        ]
                        ]
                    )
                )
            filetype = msg.media
            file = getattr(msg, filetype.value)
            title = '' + ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), file.file_name.split()))
            size = get_size(file.file_size)
            f_caption = f"<code>{title}</code>"
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title, file_size='' if size is None else size, file_caption='')
                except:
                    return
            await msg.edit_caption(f_caption)
            btn = [[
                InlineKeyboardButton("❗ Obtenir à nouveau le fichier ❗", callback_data=f'delfile#{file_id}')
            ]]
            k = await client.send_message(chat_id=message.from_user.id, text=f"<b>❗️ <u>Important</u> ❗️</b>\n\n<b>Ce fichier vidéo sera supprimé dans</b> <b><u>10 minutes</u></b><b> (en raison de problèmes de droits d'auteur).</b>\n\n<b><i>📌 Merci de transférer ce fichier ailleurs et commence à le télécharger là-bas.</i></b>")
            await asyncio.sleep(600)
            await msg.delete()
            await k.edit_text("<b>Ton fichier a bien été supprimé !!\n\nClique sur le bouton ci-dessous pour obtenir ton fichier supprimé 👇</b>", reply_markup=InlineKeyboardMarkup(btn))
            return
        except:
            pass
        return await message.reply('Aucun fichier trouvé !')
    files = files_[0]
    title = '' + ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), files.file_name.split()))
    size=get_size(files.file_size)
    f_caption=files.caption
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption = CUSTOM_FILE_CAPTION.format(
                file_name='' if title is None else title,
                file_size='' if size is None else size,
                file_caption='' if f_caption is None else f_caption
            )
        except Exception as e:
            logger.exception(e)
            f_caption = f_caption

    if f_caption is None:
        f_caption = f" {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), files.file_name.split()))}"

    if not await check_verification(client, message.from_user.id) and VERIFY == True:
        btn = [[
            InlineKeyboardButton("♻️ Cliquez ici pour vérifier ♻️", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start="))
        ],[
            InlineKeyboardButton("⁉️ Comment vérifier ⁉️", url=HOWTOVERIFY)
        ]]
        await message.reply_text(
            text="<b>👋 Salut,\n\n📌 <u>Tu n'es pas vérifié aujourd'hui, s'il te plaît vérifie et obtient un accès illimité jusqu'à la prochaine vérification</u>.</b>",
            protect_content=True,
            reply_markup=InlineKeyboardMarkup(btn)
        )
        return

    msg = await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        protect_content=True if pre == 'filep' else False,
        reply_markup=InlineKeyboardMarkup(
                        [
                        [
                        InlineKeyboardButton('• Streaming', callback_data=f'generate_stream_link:{file_id}'),
                        InlineKeyboardButton('Mises à jour •', url=GRP_LNK)
                        ]
                        ]
                    )
                )
    btn = [[
        InlineKeyboardButton("❗ Récupérer à nouveau le fichier ❗", callback_data=f'delfile#{file_id}')
    ]]
    k = await client.send_message(
        chat_id=message.from_user.id, 
        text=f"<b>❗️ <u>Important</u> ❗️</b>\n\n<b>Ce vidéo / fichier sera supprimé dans</b> <b><u>10 minutes</u></b> <b>(en raison des problèmes de droits d'auteur).</b>\n\n<b><i>📌 Merci de transférer cette vidéo / fichier ailleurs et commencer à le télécharger là-bas.</i></b>"
    )
    await asyncio.sleep(600)
    await msg.delete()
    await k.edit_text("<b>Ton vidéo / fichier a été supprimé avec succès !!\n\nClique sur le bouton ci-dessous pour récupérer ton vidéo / fichier supprimé 👇</b>", reply_markup=InlineKeyboardMarkup(btn))
    return
    

@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
    """Envoyer des informations de base sur le canal"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("Type inattendu pour les canaux.")

    text = '📑 **Liste des canaux / groupes indexés :**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Total :** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)
    
@Client.on_message(filters.command('groups') & filters.user(ADMINS))
async def groupe_info(bot, message):
    GROUPE = await db.get_all_chats()
    
    if not GROUPE:
        await message.reply("❌ Aucun groupe indexé trouvé.")
        return

    text = '📑 **Liste des Groupes :**\n\n'
    for groupe in GROUPE:
        groupe_id = groupe.get('id', 'N/A')
        groupe_title = groupe.get('title', 'N/A')
        chat_status = groupe.get('chat_status', {})
        is_disabled = chat_status.get('is_disabled', False)
        reason = chat_status.get('reason', 'Aucune raison spécifiée')

        text += (
            f"🆔 **ID :** `{groupe_id}`\n"
            f"📛 **Titre :** {groupe_title}\n"
            f"🔒 **Statut :** {'Désactivé' if is_disabled else 'Activé'}\n"
            f"📝 **Raison :** {reason}\n\n"
        )

    text += f"**Total :** {len(GROUPE)}"

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'all_groupes.txt'
        try:
            with open(file, 'w', encoding='utf-8') as f:
                f.write(text)
            await message.reply_document(file)
        finally:
            if os.path.exists(file):
                os.remove(file)


@Client.on_message(filters.command('logs') & filters.user(ADMINS))
async def log_file(bot, message):
    """Envoyer le fichier des logs"""
    try:
        await message.reply_document('TELEGRAM BOT.LOG')
    except Exception as e:
        await message.reply(str(e))


@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Supprimer le fichier de la base de données"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("Traitement en cours...⏳", quote=True)
    else:
        await message.reply('Répondez au fichier avec /delete que vous souhaitez supprimer de la base de données.', quote=True)
        return

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('Ce format de fichier n\'est pas supporté.')
        return
    
    file_id, file_ref = unpack_new_file_id(media.file_id)

    result = await Media.collection.delete_one({
        '_id': file_id,
    })
    if result.deleted_count:
        await msg.edit('Le fichier a été supprimé avec succès de la base de données ✅')
    else:
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        result = await Media.collection.delete_many({
            'file_name': file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
            })
        if result.deleted_count:
            await msg.edit('Le fichier a été supprimé avec succès de la base de données ✅')
        else:
            result = await Media.collection.delete_many({
                'file_name': media.file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
            })
            if result.deleted_count:
                await msg.edit('Le fichier a été supprimé avec succès de la base de données ✅')
            else:
                await msg.edit('Le fichier n\'a pas été trouvé dans la base de données ❌')


@Client.on_message(filters.command('deleteall') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    await message.reply_text(
        'Cela supprimera tous vos fichiers indexés !\nSouhaitez-vous continuer ?',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="⚠️ Oui ⚠️", callback_data="autofilter_delete"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="❌ Non ❌", callback_data="close_data"
                    )
                ],
            ]
        ),
        quote=True,
    )


@Client.on_callback_query(filters.regex(r'^autofilter_delete'))
async def delete_all_index_confirm(bot, message):
    await Media.collection.drop()
    await message.answer('Maintenu par : Hyosh Coder')
    await message.message.edit('Tous les fichiers indexés ont été supprimés avec succès ✅')

@Client.on_message(filters.command('settings'))
async def settings(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"Vous êtes un administrateur anonyme.\nUtilisez /connect {message.chat.id} en privé.")
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Assurez-vous que je suis présent dans votre groupe !!", quote=True)
                return
        else:
            await message.reply_text("Je ne suis connecté à aucun groupe !", quote=True)
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
    ):
        return
    
    settings = await get_settings(grp_id)

    try:
        if settings['max_btn']:
            settings = await get_settings(grp_id)
    except KeyError:
        await save_group_settings(grp_id, 'max_btn', False)
        settings = await get_settings(grp_id)
    if 'is_shortlink' not in settings.keys():
        await save_group_settings(grp_id, 'is_shortlink', False)
    else:
        pass

    if settings is not None:
        buttons = [        
                [
                InlineKeyboardButton(
                    'Page de résultats',
                    callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    'Bouton' if settings["button"] else 'Texte',
                    callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Mode d\'envoi de fichier',
                    callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    'Démarrer' if settings["botpm"] else 'Automatique',
                    callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Fichier sécurisé',
                    callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    'Activer' if settings["file_secure"] else 'Désactiver',
                    callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Poster IMDb',
                    callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    'Activer' if settings["imdb"] else 'Désactiver',
                    callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Vérification orthographique',
                    callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    'Activer' if settings["spell_check"] else 'Désactiver',
                    callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Message de bienvenue',
                    callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    'Activer' if settings["welcome"] else 'Désactiver',
                    callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Suppression automatique',
                    callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    'Activer' if settings["auto_delete"] else 'Désactiver',
                    callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Filtre automatique',
                    callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    'Activer' if settings["auto_ffilter"] else 'Désactiver',
                    callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Max Boutons',
                    callback_data=f'setgs#max_btn#{settings["max_btn"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '10' if settings["max_btn"] else f'{MAX_B_TN}',
                    callback_data=f'setgs#max_btn#{settings["max_btn"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Lien court',
                    callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    'Activer' if settings["is_shortlink"] else 'Désactiver',
                    callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton('⇋ Fermer le menu des paramètres ⇋', 
                                     callback_data='close_data'
                                     )
            ]
        ]
        

        btn = [[
                InlineKeyboardButton("👤 Ouvrir en chat privé 👤", callback_data=f"opnsetpm#{grp_id}")
              ],[
                InlineKeyboardButton("👥 Ouvrir ici 👥", callback_data=f"opnsetgrp#{grp_id}")
              ]]

        reply_markup = InlineKeyboardMarkup(buttons)
        if chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            await message.reply_text(
                text="<b>Où voulez-vous ouvrir le menu des paramètres ? ⚙️</b>",
                reply_markup=InlineKeyboardMarkup(btn),
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
                reply_to_message_id=message.id
            )
        else:
            await message.reply_text(
                text=f"<b>Modifiez vos paramètres pour {title} comme vous le souhaitez ⚙</b>",
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
                reply_to_message_id=message.id
            )

@Client.on_message(filters.command('set_template')  & filters.user(ADMINS))
async def save_template(client, message):
    sts = await message.reply("Vérification du modèle...")
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"Vous êtes un administrateur anonyme.\nUtilisez /connect {message.chat.id} en message privé.")
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Assurez-vous que je sois présent dans votre groupe !!", quote=True)
                return
        else:
            await message.reply_text("Je ne suis connecté à aucun groupe !", quote=True)
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
    ):
        return

    if len(message.command) < 2:
        return await sts.edit("Aucun input !")
    template = message.text.split(" ", 1)[1]
    await save_group_settings(grp_id, 'template', template)
    await sts.edit(f"✅ Modèle changé avec succès pour <code>{title}</code> en\n\n{template}")

@Client.on_message((filters.command(["request", "Request"]) | filters.regex("#request") | filters.regex("#Request")) & filters.group)
async def requests(bot, message):
    if REQST_CHANNEL is None or SUPPORT_CHAT_ID is None: return  # Vous devez ajouter REQST_CHANNEL et SUPPORT_CHAT_ID pour utiliser cette fonctionnalité
    if message.reply_to_message and SUPPORT_CHAT_ID == message.chat.id:
        chat_id = message.chat.id
        reporter = str(message.from_user.id)
        mention = message.from_user.mention
        success = True
        content = message.reply_to_message.text
        try:
            if REQST_CHANNEL is not None:
                btn = [[
                        InlineKeyboardButton('Voir la demande', url=f"{message.reply_to_message.link}"),
                        InlineKeyboardButton('Afficher les options', callback_data=f'show_option#{reporter}')
                      ]]
                reported_post = await bot.send_message(chat_id=REQST_CHANNEL, text=f"<b>📝 Demande : <u>{content}</u>\n\n📚 Rapporté par : {mention}\n📖 ID du rapporteur : {reporter}\n\n©️ Hokage Robot™</b>", reply_markup=InlineKeyboardMarkup(btn))
                success = True
            elif len(content) >= 3:
                for admin in ADMINS:
                    btn = [[
                        InlineKeyboardButton('Voir la demande', url=f"{message.reply_to_message.link}"),
                        InlineKeyboardButton('Afficher les options', callback_data=f'show_option#{reporter}')
                      ]]
                    reported_post = await bot.send_message(chat_id=admin, text=f"<b>📝 Demande : <u>{content}</u>\n\n📚 Rapporté par : {mention}\n📖 ID du rapporteur : {reporter}\n\n©️ Hokage Robot™</b>", reply_markup=InlineKeyboardMarkup(btn))
                    success = True
            else:
                if len(content) < 3:
                    await message.reply_text("<b>Vous devez taper au moins 3 caractères pour votre demande. Les demandes ne peuvent pas être vides.</b>")
            if len(content) < 3:
                success = False
        except Exception as e:
            await message.reply_text(f"Erreur : {e}")
            pass

    elif SUPPORT_CHAT_ID == message.chat.id:
        chat_id = message.chat.id
        reporter = str(message.from_user.id)
        mention = message.from_user.mention
        success = True
        content = message.text
        keywords = ["#request", "/request", "#Request", "/Request"]
        for keyword in keywords:
            if keyword in content:
                content = content.replace(keyword, "")
        try:
            if REQST_CHANNEL is not None and len(content) >= 3:
                btn = [[
                        InlineKeyboardButton('Voir la demande', url=f"{message.link}"),
                        InlineKeyboardButton('Afficher les options', callback_data=f'show_option#{reporter}')
                      ]]
                reported_post = await bot.send_message(chat_id=REQST_CHANNEL, text=f"<b>📝 Demande : <u>{content}</u>\n\n📚 Rapporté par : {mention}\n📖 ID du rapporteur : {reporter}\n\n©️ Hokage Robot™</b>", reply_markup=InlineKeyboardMarkup(btn))
                success = True
            elif len(content) >= 3:
                for admin in ADMINS:
                    btn = [[
                        InlineKeyboardButton('Voir la demande', url=f"{message.link}"),
                        InlineKeyboardButton('Afficher les options', callback_data=f'show_option#{reporter}')
                      ]]
                    reported_post = await bot.send_message(chat_id=admin, text=f"<b>📝 Demande : <u>{content}</u>\n\n📚 Rapporté par : {mention}\n📖 ID du rapporteur : {reporter}\n\n©️ Hokage Robot™</b>", reply_markup=InlineKeyboardMarkup(btn))
                    success = True
            else:
                if len(content) < 3:
                    await message.reply_text("<b>Vous devez taper au moins 3 caractères pour votre demande. Les demandes ne peuvent pas être vides.</b>")
            if len(content) < 3:
                success = False
        except Exception as e:
            await message.reply_text(f"Erreur : {e}")
            pass
     
    elif SUPPORT_CHAT_ID == message.chat.id:
        chat_id = message.chat.id
        reporter = str(message.from_user.id)
        mention = message.from_user.mention
        success = True
        content = message.text
        keywords = ["#request", "/request", "#Request", "/Request"]
        for keyword in keywords:
            if keyword in content:
                content = content.replace(keyword, "")
        try:
            if REQST_CHANNEL is not None and len(content) >= 3:
                btn = [[
                        InlineKeyboardButton('Voir la demande', url=f"{message.link}"),
                        InlineKeyboardButton('Afficher les options', callback_data=f'show_option#{reporter}')
                      ]]
                reported_post = await bot.send_message(chat_id=REQST_CHANNEL, text=f"<b>📝 Demande : <u>{content}</u>\n\n📚 Rapporté par : {mention}\n📖 ID du rapporteur : {reporter}\n\n©️ Hokage Robot™</b>", reply_markup=InlineKeyboardMarkup(btn))
                success = True
            elif len(content) >= 3:
                for admin in ADMINS:
                    btn = [[
                        InlineKeyboardButton('Voir la demande', url=f"{message.link}"),
                        InlineKeyboardButton('Afficher les options', callback_data=f'show_option#{reporter}')
                      ]]
                    reported_post = await bot.send_message(chat_id=admin, text=f"<b>📝 Demande : <u>{content}</u>\n\n📚 Rapporté par : {mention}\n📖 ID du rapporteur : {reporter}\n\n©️ Hokage Robot™</b>", reply_markup=InlineKeyboardMarkup(btn))
                    success = True
            else:
                if len(content) < 3:
                    await message.reply_text("<b>Vous devez taper au moins 3 caractères pour votre demande. Les demandes ne peuvent pas être vides.</b>")
            if len(content) < 3:
                success = False
        except Exception as e:
            await message.reply_text(f"Erreur : {e}")
            pass

    else:
        success = False
    
    if success:
        '''if isinstance(REQST_CHANNEL, (int, str)):
            channels = [REQST_CHANNEL]
        elif isinstance(REQST_CHANNEL, list):
            channels = REQST_CHANNEL
        for channel in channels:
            chat = await bot.get_chat(channel)
        #chat = int(chat)'''
        link = await bot.create_chat_invite_link(int(REQST_CHANNEL))
        btn = [[
                InlineKeyboardButton('Rejoindre le canal', url=link.invite_link),
                InlineKeyboardButton('Voir la demande', url=f"{reported_post.link}")
              ]]
        await message.reply_text("<b>Votre demande a été envoyée avec succès. Vous pouvez la voir en cliquant sur le lien ci-dessous.</b>")
    
@Client.on_message(filters.command("deletefiles") & filters.user(ADMINS))
async def deletemultiplefiles(bot, message):

    chat_type = message.chat.type

    if chat_type != enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>Hé {message.from_user.mention},\nCette commande ne fonctionnera pas dans les groupes !\nElle fonctionne uniquement en privé avec moi.</b>")

    else:
        pass

    try:
        keyword = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text(f"<b>Hé {message.from_user.mention},\nDonne-moi un mot-clé avec cette commande pour supprimer des fichiers.</b>")

    btn = [[
        InlineKeyboardButton("⚠️ Oui, continuer ⚠️", callback_data=f"killfilesdq#{keyword}")
    ],[
        InlineKeyboardButton("❌ Non, annuler l'opération ❌", callback_data="close_data")
    ]]

    await message.reply_text(
        text="<b>Es-tu sûr de vouloir continuer ?\nAttention : cela pourrait être une décision destructive.</b>",
        reply_markup=InlineKeyboardMarkup(btn),
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(filters.command("set_shortlink"))
async def shortlink(bot, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"Vous êtes un administrateur anonyme, veuillez désactiver l'anonymat et réessayer cette commande.")
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>Hé {message.from_user.mention}, cette commande fonctionne uniquement dans les groupes !</b>")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    data = message.text
    userid = message.from_user.id
    user = await bot.get_chat_member(grpid, userid)
    if user.status != enums.ChatMemberStatus.ADMINISTRATOR and user.status != enums.ChatMemberStatus.OWNER and str(userid) not in ADMINS:
        return await message.reply_text("<b>Vous n'avez pas accès à cette commande !\nCette commande fonctionne uniquement pour les administrateurs du groupe.</b>")
    else:
        pass
    try:
        command, shortlink_url, api = data.split(" ")
    except:
        return await message.reply_text("<b>Commande incomplète !\nVeuillez fournir la commande avec le lien raccourci et l'API.\n\nFormat : <code>/set_shortlink shareus.io c8dacdff6e91a8e4b4f093fdb4d8ae31bc273c1a</code></b>")
    reply = await message.reply_text("<b>Veuillez patienter...</b>")
    shortlink_url = re.sub(r"https?://?", "", shortlink_url)
    shortlink_url = re.sub(r"[:/]", "", shortlink_url)
    await save_group_settings(grpid, 'shortlink', shortlink_url)
    await save_group_settings(grpid, 'shortlink_api', api)
    await save_group_settings(grpid, 'is_shortlink', True)
    await reply.edit_text(f"<b>✅ Lien raccourci ajouté avec succès pour <code>{title}</code>.\n\nSite Web raccourci : <code>{shortlink_url}</code>\nAPI raccourci : <code>{api}</code></b>")

@Client.on_message(filters.command("shortlinkoff") & filters.user(ADMINS))
async def offshortlink(bot, message):
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text("Cette commande fonctionne uniquement dans les groupes !")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    await save_group_settings(grpid, 'is_shortlink', False)
    ENABLE_SHORTLINK = False
    return await message.reply_text("Le lien raccourci a été désactivé avec succès.")

@Client.on_message(filters.command("shortlinkon") & filters.user(ADMINS))
async def onshortlink(bot, message):
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text("Cette commande fonctionne uniquement dans les groupes !")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    await save_group_settings(grpid, 'is_shortlink', True)
    ENABLE_SHORTLINK = True
    return await message.reply_text("Le lien raccourci a été activé avec succès.")

@Client.on_message(filters.command("shortlink_info"))
async def ginfo(bot, message):
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>{message.from_user.mention},\n\nUtilisez cette commande dans votre groupe.</b>")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    chat_id = message.chat.id
    userid = message.from_user.id
    user = await bot.get_chat_member(grpid, userid)
    
    if user.status != enums.ChatMemberStatus.ADMINISTRATOR and user.status != enums.ChatMemberStatus.OWNER and str(userid) not in ADMINS:
        return await message.reply_text("<b>Seul le propriétaire ou l'administrateur du groupe peut utiliser cette commande !</b>")
    else:
        settings = await get_settings(chat_id)  # récupération des paramètres du groupe
        if 'shortlink' in settings.keys() and 'tutorial' in settings.keys():
            su = settings['shortlink']
            sa = settings['shortlink_api']
            st = settings['tutorial']
            return await message.reply_text(f"<b><u>Statut actuel<u> 📊\n\nSite web : <code>{su}</code>\n\nAPI : <code>{sa}</code>\n\nTutoriel : {st}</b>", disable_web_page_preview=True)
        elif 'shortlink' in settings.keys() and 'tutorial' not in settings.keys():
            su = settings['shortlink']
            sa = settings['shortlink_api']
            return await message.reply_text(f"<b><u>Statut actuel<u> 📊\n\nSite web : <code>{su}</code>\n\nAPI : <code>{sa}</code>\n\nUtilisez la commande /set_tutorial pour définir votre tutoriel.")
        elif 'shortlink' not in settings.keys() and 'tutorial' in settings.keys():
            st = settings['tutorial']
            return await message.reply_text(f"<b>Tutoriel : <code>{st}</code>\n\nUtilisez la commande /shortlink pour connecter votre raccourcisseur d'URL</b>")
        else:
            return await message.reply_text("Le raccourcisseur d'URL et le tutoriel ne sont pas connectés.\n\nVérifiez les commandes /set_tutorial et /set_shortlink.")

@Client.on_message(filters.command("donate"))
async def donate_command(client, message):
    buttons = [
        [
            InlineKeyboardButton("• Faire un don •", url="https://t.me/OtakuFlix_Network/4640"),
            InlineKeyboardButton("• Support •", url="https://t.me/hyoshcoder")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text(text=Script.DONATION_TXT, reply_markup=reply_markup)

@Client.on_message(filters.command("help"))
async def help_command(client, message):
    buttons = [
        [
            InlineKeyboardButton("• Ouvrir en privé •", url="https://t.me/Hokage_Filter_bot?start=help"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text(text=Script.HELP_TXT, reply_markup=reply_markup)

@Client.on_message(filters.command("support"))
async def support_command(client, message):
    buttons = [
        [
            InlineKeyboardButton("Support", url="https://t.me/hyoshcoder"),
            InlineKeyboardButton("Mises à jour", url="https://t.me/hyoshcoder")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text(text=Script.SUPPORT_TXT, reply_markup=reply_markup)

@Client.on_message(filters.command("set_tutorial"))
async def settutorial(bot, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"Vous êtes un administrateur anonyme, désactivez l'option administrateur anonyme et réessayez cette commande.")
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text("Cette commande fonctionne uniquement dans les groupes !")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    userid = message.from_user.id
    user = await bot.get_chat_member(grpid, userid)
    if user.status != enums.ChatMemberStatus.ADMINISTRATOR and user.status != enums.ChatMemberStatus.OWNER and str(userid) not in ADMINS:
        return
    else:
        pass
    if len(message.command) == 1:
        return await message.reply("<b>Donne-moi un lien de tutoriel avec cette commande.\n\nUsage : /set_tutorial <code>https://t.me/How_to_Download_7x/32</code></b>")
    elif len(message.command) == 2:
        reply = await message.reply_text("<b>Veuillez patienter...</b>")
        tutorial = message.command[1]
        await save_group_settings(grpid, 'tutorial', tutorial)
        await save_group_settings(grpid, 'is_tutorial', True)
        await reply.edit_text(f"<b>✅ Tutoriel ajouté avec succès\n\nVotre groupe : {title}\n\nVotre tutoriel : <code>{tutorial}</code></b>")
    else:
        return await message.reply("<b>Format incorrect !\nFormat correct : /set_tutorial <code>https://t.me/How_to_Download_7x/32</code></b>")

@Client.on_message(filters.command("remove_tutorial"))
async def removetutorial(bot, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"Vous êtes un administrateur anonyme, désactivez l'option administrateur anonyme et réessayez cette commande.")
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text("Cette commande fonctionne uniquement dans les groupes !")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    userid = message.from_user.id
    user = await bot.get_chat_member(grpid, userid)
    if user.status != enums.ChatMemberStatus.ADMINISTRATOR and user.status != enums.ChatMemberStatus.OWNER and str(userid) not in ADMINS:
        return
    else:
        pass
    reply = await message.reply_text("<b>Veuillez patienter...</b>")
    await save_group_settings(grpid, 'is_tutorial', False)
    await reply.edit_text(f"<b>Tutoriel supprimé avec succès ✅</b>")

@Client.on_message(filters.command("refer"))
async def refer(bot, message):
    btn = [[
        InlineKeyboardButton('• Partager le lien', url=f'https://telegram.me/share/url?url=https://t.me/{bot.me.username}?start=reff_{message.from_user.id}&text=Hello! Expérience d\'un bot offrant une grande bibliothèque de films et séries. 😃'),
        InlineKeyboardButton(f'⏳ {referdb.get_refer_points(message.from_user.id)}', callback_data='ref_point'),
        InlineKeyboardButton('Fermer •', callback_data='close_data')
    ]]  
    reply_markup = InlineKeyboardMarkup(btn)
    await message.reply_photo(
            photo=random.choice(REFER_PICS),
            caption=f'<b>» Salut {message.from_user.mention},\n\nVoici ton lien de parrainage :\nhttps://t.me/{bot.me.username}?start=reff_{message.from_user.id}\n\nPartage ce lien avec tes amis, chaque fois qu\'ils rejoignent, tu recevras 10 points de parrainage et après 100 points, tu obtiendras 1 mois d\'abonnement premium.</b>',
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(filters.command("restart") & filters.user(ADMINS))
async def stop_button(bot, message):
    msg = await bot.send_message(text="<b><i>Le bot redémarre</i></b>", chat_id=message.chat.id)       
    await asyncio.sleep(3)
    await msg.edit("<b><i><u>Le bot a redémarré</u> ✅</i></b>")
    os.execl(sys.executable, sys.executable, *sys.argv)


