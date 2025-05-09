from pyrogram import filters, Client
import bs4, requests, re, asyncio
import os, traceback, random
from info import LOG_CHANNEL as DUMP_GROUP
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
#    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Length": "99",
    "Origin": "https://saveig.app",
    "Connection": "keep-alive",
    "Referer": "https://saveig.app/en",
}
@Client.on_message(filters.regex(r'https?://.*instagram[^\s]+') & filters.incoming)
async def link_handler(Mbot, message):
    link = message.matches[0].group(0)
    global headers
    try:
        m = await message.reply_sticker("CAACAgUAAxkBAAITAmWEcdiJs9U2WtZXtWJlqVaI8diEAAIBAAPBJDExTOWVairA1m8eBA")
        url= link.replace("instagram.com","ddinstagram.com")
        url=url.replace("==","%3D%3D")
        if url.endswith("="):
           dump_file=await message.reply_video(url[:-1],caption="Téléchargé par @HokageMovie_bot")
        else:
            dump_file=await message.reply_video(url,caption="Téléchargé par @HokageMovie_bot")
        if 'dump_file' in locals():
           await dump_file.forward(DUMP_GROUP)
        await m.delete()
    except Exception as e:
        try:
            if "/reel/" in url:
               ddinsta=True 
               getdata = requests.get(url).text
               soup = bs4.BeautifulSoup(getdata, 'html.parser')
               meta_tag = soup.find('meta', attrs={'property': 'og:video'})
               try:
                  content_value =f"https://ddinstagram.com{meta_tag['content']}"
               except:
                   pass 
               if not meta_tag:
                  ddinsta=False
                  meta_tag = requests.post("https://saveig.app/api/ajaxSearch", data={"q": link, "t": "media", "lang": "en"}, headers=headers)
             
                  if meta_tag.ok:
                     res=meta_tag.json()
               
                #     await message.reply(res)
                     meta=re.findall(r'href="(https?://[^"]+)"', res['data']) 
                     content_value = meta[0]
                  else:
                      return await message.reply("Oups, quelque chose s'est mal passé")
               try:
                   if ddinsta:
                      dump_file=await message.reply_video(content_value,caption="Téléchargé par @HokageMovie_bot")
                   else:
                       dump_file=await message.reply_video(content_value, caption="Téléchargé par @HokageMovie_bot")
               except:
                   downfile=f"{os.getcwd()}/{random.randint(1,10000000)}"
                   with open(downfile,'wb') as x:
                       headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                       x.write(requests.get(content_value,headers=headers).content)
                   dump_file=await message.reply_video(downfile,caption="Téléchargé par @HokageMovie_bot") 
            elif "/p/" in url:
                  meta_tag = requests.post("https://saveig.app/api/ajaxSearch", data={"q": link, "t": "media", "lang": "en"}, headers=headers)
                  if meta_tag.ok:
                     res=meta_tag.json()
                     meta=re.findall(r'href="(https?://[^"]+)"', res['data']) 
                  else:
                      return await message.reply("Oups, quelque chose s'est mal passé")
              #    await message.reply(meta)
                  for i in range(len(meta) - 1):
                     com=await message.reply_text(meta[i])
                     await asyncio.sleep(1)
                     try:
                        dump_file=await message.reply_video(com.text,caption="Téléchargé par @HokageMovie_bot")
                        await com.delete()
                     except:
                         pass 
            elif "stories" in url:
                  meta_tag = requests.post("https://saveig.app/api/ajaxSearch", data={"q": link, "t": "media", "lang": "en"}, headers=headers)
                  if meta_tag.ok:
                     res=meta_tag.json()
                     meta=re.findall(r'href="(https?://[^"]+)"', res['data']) 
                  else:
                      return await message.reply("Oups, quelque chose s'est mal passé")
                  try:
                     dump_file=await message.reply_video(meta[0], caption="Téléchargé par @HokageMovie_bot")
                  except:
                      com=await message.reply(meta[0])
                      await asyncio.sleep(1)
                      try:
                          dump_file=await message.reply_video(com.text,caption="Téléchargé par @HokageMovie_bot")
                          await com.delete()
                      except:
                          pass

        except KeyError:
            await message.reply(f"400: Désolé, impossible de le trouver. Assurez-vous qu'il est publiquement disponible :)")
        except Exception as e:
          #  await message.reply_text(f"https://ddinstagram.com{content_value}")
            if DUMP_GROUP:
               await Mbot.send_message(DUMP_GROUP,f"Instagram {e} {link}")
               await Mbot.send_message(DUMP_GROUP, traceback.format_exc())
          #     await message.reply(tracemsg)
            ##optinal 
            await message.reply(f"400: Désolé, impossible de le trouver. Essayez un autre ou signalez-le à @VeldXd ou au chat de support https://t.me/promo_prenium_groupe")

        finally:
            if 'dump_file' in locals():
               if DUMP_GROUP:
                  await dump_file.copy(DUMP_GROUP)
            await m.delete()
            if 'downfile' in locals():
                os.remove(downfile)
            await message.reply("<a href='https://t.me/HokageMovie_bot'>Utilisez les nouvelles fonctionnalités</a>")
