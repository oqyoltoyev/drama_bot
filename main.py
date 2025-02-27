from telebot import types
from config import *
import time
import os
from datetime import  datetime, timedelta
import random
import traceback
from telebot import types
import traceback
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

conn.commit()
b_url = "https://t.me/Drama_uzbbot?start=s"

@bot.message_handler(commands=['start'])
def welcome(msg):
    cid = msg.chat.id
    text = msg.text
    btn = ReplyKeyboardMarkup(resize_keyboard=True)
    btn.add(KeyboardButton(text="🤝 Reklama hizmati"))
    kl=bot.send_message(cid, f"𝘗𝘙𝘌𝘚𝘚 ➺ /start ....", reply_markup=btn)
    check = cursor.execute(f"SELECT * FROM users WHERE chat_id={cid}").fetchone()
    if check is None:
      cursor.execute(f"INSERT INTO users(chat_id) VALUES({cid})")

    elif text=='/start' and len(text)==6:
      bot.delete_message(cid,kl.message_id)
      bot.delete_message(cid,msg.message_id)

      p = bot.send_message(cid, f"""
<b>👋 Assalomu alaykum {msg.from_user.first_name}, botimizga xush kelibsiz!</b>

🔥 Drama Tv - boti orqali siz eng so‘ngi hamda eng yangi film,
serial va doramalarni ko‘rishingiz mumkin.

<blockquote>Menga shunchaki film kodini yuboring!</blockquote>
""", reply_markup=start_btn(), parse_mode="HTML")



    elif text.split(" ")[0] and len(text)>5:
      code = text.split(" ")[1]
      if 's' in code  and join(cid):
        code = code.replace("s","")
        all = cursor.execute(f"SELECT * FROM serial WHERE id={code}").fetchone()
        if all:
          name = all[1]
          json = cursor.execute(f"SELECT * FROM movies WHERE serial='{name}'").fetchall()
          c = 0
          key = InlineKeyboardMarkup(row_width=4)
          m = []
          for i in json:
            c+=1
            m.append(InlineKeyboardButton(text=f"{c}",callback_data=f'yukla-{i[0]}'))
          key.add(*m)
          sent=bot.send_photo(cid,photo=all[2],caption=f"<b>⛩ : {name} \n\n🎬 Qisimlar: {len(json)}</b>",reply_markup=key)
          bot.pin_chat_message(cid, sent.message_id)
      elif 'f' in code  and join(cid):
        code = code.replace("f","")
        check = cursor.execute(f"SELECT * FROM kino WHERE id={code}").fetchone()
        if check:
          json = cursor.execute(f"SELECT * FROM kino WHERE id={code}").fetchone()
          bot.send_video(cid,json[1],caption=json[2].replace("'","'"),reply_markup=share_button(),protect_content=True)


@bot.callback_query_handler(func=lambda call: call.data == "search")
def search_callback(call):
    # Foydalanuvchidan qidiruv so'rovini olish
    bot.answer_callback_query(call.id, text="Qidiruv olib borilmoqda...")
    
    # Tugma bosilganda bot xabarini tahrirlash
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="<b>Shunchaki kino nomini yuboring . . .</b>")
    
    bot.register_next_step_handler(call.message, process_search)

def process_search(msg):
  cid = msg.chat.id
  series_name = msg.text
  search_results = search_series(series_name)
  if search_results:
      keyboard = telebot.types.InlineKeyboardMarkup(row_width=3)
      for result in search_results:
          if len(result['name']) > 20:  # Seriya nomlari 27 harfdan uzun bo'lsa
              short_name = result['name'][:20]   # Faqat 27 harfdan iborat qismini olib qo'yamiz
          else:
              short_name = result['name']  # Aks holda, to'liq nomni qo'yamiz
          keyboard.add(telebot.types.InlineKeyboardButton(short_name, url=b_url + str(result['id'])))
      
      bot.reply_to(msg, '✅ Film topildi . Quidagi natijalardan birini tanlang', reply_markup=keyboard,reply_to_message_id=msg.message_id)
  else:
      m=bot.reply_to(msg, "📛 Natijalar topilmadi...\n\n<blockquote>Qaytadan urinib ko'ring  | kino nominidagi aynan bir so'zni kiritb ko'ring</blockquote>", parse_mode="html",reply_markup=start_btn())


@bot.message_handler(commands=['ad'])
def add_admin(message):
    if message.from_user.id == ADMIN_ID[0]:  # Bosh admin tekshiriladi
        try:
            new_admin_id = int(message.text.split()[1])  # Foydalanuvchi tomonidan kiritilgan yangi admin ID'si
            if new_admin_id not in ADMIN_ID:  # Agar yangi admin ro'yxatda bo'lmasa
                ADMIN_ID.append(new_admin_id)  # Yangi adminni ro'yxatga qo'shamiz
                bot.send_message(new_admin_id, "Siz Admin bo'ldingiz!\n\n /panel  - sinab ko'rin")
                bot.send_message(message.chat.id, f"[{new_admin_id}](tg://user?id={new_admin_id}) raqami adminlar ro'yxatiga qo'shildi.",parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, "Bu foydalanuvchi allaqachon admin.")
        except (IndexError, ValueError):
            bot.send_message(message.chat.id, "To'g'ri formatda ID kiriting. Masalan: /add_admin 123456789")
    else:
        bot.send_message(message.chat.id, "Sizda bosh adminlik huquqi yo'q!\n\nTushunyabsizmi Ega emassiz ):")

@bot.message_handler(commands=['del'])
def delete_admin(message):
    if message.from_user.id == ADMIN_ID[0]:  # Bosh admin tekshiriladi
        try:
            removed_admin_id = int(message.text.split()[1])  # Foydalanuvchi tomonidan kiritilgan o'chiriladigan admin ID'si
            if removed_admin_id in ADMIN_ID:  # Agar o'chiriladigan admin ro'yxatda bo'lsa
                ADMIN_ID.remove(removed_admin_id)  # Adminni ro'yxatdan o'chiramiz
                bot.send_message(removed_admin_id, "Siz Adminlikdan olindingiz \n\nSababini men qayerdan bilay ):")
                bot.send_message(message.chat.id, f"[{removed_admin_id}](tg://user?id={removed_admin_id}) raqami adminlar ro'yxatidan o'chirildi.")
            else:
                bot.send_message(message.chat.id, "Bu foydalanuvchi allaqachon chopilgan")
        except (IndexError, ValueError):
            bot.send_message(message.chat.id, "To'g'ri formatda ID kiriting. Masalan: /del 123456789")
    else:
        bot.send_message(message.chat.id, "Sizda bosh adminlik huquqi yo'q!")

@bot.message_handler(commands=['adm'])
def list_admins(message):
    if message.from_user.id == ADMIN_ID[0]:  # Bosh admin tekshiriladi
        admins_list = "\n".join([f"{i+1}. [{admin_id}](tg://user?id={admin_id})" for i, admin_id in enumerate(ADMIN_ID)])
        bot.send_message(message.chat.id, f"Adminlar ro'yxati:\n\n{admins_list}", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "Sizda bosh adminlik huquqi yo'q!")


      
      
@bot.message_handler(func=lambda message: message.text.isdigit())
def serial_search(msg):
    cid = msg.chat.id
    reply_to_user_id = msg.reply_to_message.from_user.id if msg.reply_to_message else None
    serial_id = int(msg.text)

    # Group yoki supergroupdagi xabar
    if msg.chat.type in ['group', 'supergroup']:
        # Database'da serial mavjudligini tekshirish
        serial = cursor.execute("SELECT * FROM serial WHERE id=?", (serial_id,)).fetchone()
        
        if serial:
            # Serial topilganda nomi va rasmi bilan yuborish
            name = serial[1]
            image = serial[2]  # Serialning rasmi (URL yoki path)
            btn = InlineKeyboardMarkup(row_width=1)
            btn.add(InlineKeyboardButton(text="👀 Tomosha qilish", url=f"https://t.me/Drama_uzbbot?start=s{serial_id}"))
            
            # Serialning rasmi va nomi bilan yuborish
            bot.send_photo(cid, photo=image, caption=f"<b>[✨] : {name}</b>", reply_markup=btn,reply_to_message_id=msg.reply_to_message.message_id if reply_to_user_id else msg.message_id)
        # Agar serial topilmasa, hech qanday javob bermaslik
        else:
            return
    # Private chat uchun
    elif msg.chat.type == 'private':
        # Private chatda botga qo'shilganligini tekshirish
        if not join(cid):
            return

        # Database'da serial mavjudligini tekshirish
        serial = cursor.execute("SELECT * FROM serial WHERE id=?", (serial_id,)).fetchone()

        if serial:
            name = serial[1]
            json = cursor.execute(f"SELECT * FROM movies WHERE serial='{name}'").fetchall()
            c = 0
            key = InlineKeyboardMarkup(row_width=4)
            m = []
            for i in json:
                c += 1
                m.append(InlineKeyboardButton(text=f"{c}", callback_data=f'yukla-{i[0]}'))
            key.add(*m)
            bot.delete_message(cid, msg.message_id)
            sent = bot.send_photo(cid, photo=serial[2], caption=f"<b>[✨] : {name} \n\n🎬 Qisimlar: {len(json)}</b>", reply_markup=key)
            bot.pin_chat_message(cid, sent.message_id)
        else:
            bot.reply_to(msg, f"""
😢 <code>{serial_id}</code><b> kodga tegshli film topilmadi 😢
Boshqa kodni yoki film nomini kiritib ko'ring...</b>""", reply_markup=main_btn())


 

@bot.message_handler(func=lambda message: message.text.lower() == "🤝 reklama hizmati")
def about(message):
    cid = message.chat.id
    bot.reply_to(
        message,
        """**⚡️ Reklama hizmati bo'yicha ma'lumot olish uchun pasdagi tugmani bosing**
            """,
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton(text="🛒 Bot Buyurtma qilish", url="tg://user?id=5921733345")
        ).add(
            InlineKeyboardButton(text="🔥 Reklama haqida", url="https://t.me/Seriallar_malikasi")
        ),
        parse_mode="MarkdownV2",
        disable_web_page_preview=True
    )



@bot.message_handler(content_types=['video'])
def add_video(msg):
    if msg.chat.id in ADMIN_ID:
        cid = msg.chat.id
        file_id = msg.video.file_id
        caption = msg.caption
        FILE_ID['id'] = file_id
        CAPTION['text'] = caption
        total_serials = len(cursor.execute("SELECT * FROM serial").fetchall())

        # Sahifalash
        page_size = 40  # Har bir sahifadagi elementlar soni
        total_pages = (total_serials - 1) // page_size + 1  # Umumiy sahifalar soni

        # Sahifalarni chiqarish
        for page_number in range(1, total_pages + 1):
            start_index = (page_number - 1) * page_size
            end_index = min(page_number * page_size, total_serials)
            serials_on_page = cursor.execute("SELECT * FROM serial LIMIT ? OFFSET ?", (page_size, start_index)).fetchall()

            # Yangi klaviatura yaratish
            key = InlineKeyboardMarkup()

            # Sahifadagi har bir serial uchun tugmalar
            for serial in serials_on_page:
                # Agar serial nomi 17 harfdan uzun bo'lsa, faqatgina 17 harfni olib yuborish
                if len(serial[1]) > 15:
                    display_name = serial[1][:15]
                else:
                    display_name = serial[1]

                key.add(InlineKeyboardButton(text=f"{display_name}", callback_data=f"newserial-{serial[0]}"))

            # Agar keyingi sahifa mavjud bo'lsa, "Keyingi sahifa" tugmasini qo'shish
            if page_number < total_pages:
                key.add(InlineKeyboardButton(text="Keyingi sahifa", callback_data=f"next_page-{page_number + 1}"))

            # Xabarni jo'natish
            bot.reply_to(msg, "Qo'shmoqchi bo'lgan Film tanlang", reply_markup=key)



@bot.message_handler(content_types=['text'])
def custom(msg):
  cid = msg.chat.id
  text = msg.text
  if text=='/admin' and cid in ADMIN_ID:
    bot.reply_to(msg,f"""
🪐 ᴀᴅᴍɪɴ ᴘᴀɴᴇʟɪɢᴀ ʜᴜsʜ ᴋᴇʟɪʙsɪᴢ !


Qandaydir savol tug'lsa : @pyfotuz""",reply_markup=admin_panel())
  try:
    if text=="📊 Statistika":
      try:
        count_serial = cursor.execute("SELECT COUNT(id) FROM serial").fetchone()[0]
        count_movie = cursor.execute("SELECT COUNT(id) FROM movies").fetchone()[0]      
        users = cursor.execute("SELECT COUNT(id) FROM users").fetchone()[0]
        kino = cursor.execute("SELECT COUNT(id) FROM kino").fetchone()[0]
        txt = f"""<b>
Bot statistikasi 📊

👤 Obunachilar: {users} ta  

📺 Filmlar: {count_serial} ta
🎬 Film qismi: {count_movie} ta

</b>
      """
        bot.send_message(cid,txt)
      except Exception as e:
        print(e)


    if text=="✉ Oddiy xabar" and cid in ADMIN_ID:
      a = bot.send_message(cid,"<b>Xabar matnini kiriting: </b>")
      bot.register_next_step_handler(a,oddiy_xabar)
    elif text=="✉ Forward xabar" and cid in ADMIN_ID:
      a = bot.send_message(cid,"<b>Xabar matnini yuboring: </b>")
      bot.register_next_step_handler(a,forward_xabar)
    elif text=="➕ Film qo'shish" and cid in ADMIN_ID:
      a = bot.send_message(cid,"<b>Film rasmi va  nomini yuboring!</b>",reply_markup=back)
      bot.register_next_step_handler(a,new_serial)
    elif text=="🗑 Film ochirish" and cid in ADMIN_ID:
      a = bot.send_message(cid,"<b>🎥 Film kodini yuboring!</b>",reply_markup=back)
      bot.register_next_step_handler(a,del_kino)
    elif text == "🟢 Kanal qoshish" and cid in ADMIN_ID:
      a = bot.send_message(cid, "<b>Kanal qoshish usernamesini o'zini \n\n pymoviee - misol uchun</b>\n\n@pymoviee va t.me/ - ko'rinishida yubormang❌")
      bot.register_next_step_handler(a, add_channel)
    elif text == "🔴 Kanal ochirish" and cid in ADMIN_ID:
      a = bot.send_message(cid, "<b>Kanal ochrish usernamesini o'zini\n\n pymoviee - misol uchun\n\n@pymoviee va t.me/ - ko'rinishida yubormang</b>❌")
      bot.register_next_step_handler(a, remove_channel)
    elif text == "📺 Filmlar" and cid in ADMIN_ID:
      total_serials = len(cursor.execute("SELECT * FROM serial").fetchall())

    # Sahifalash
      page_size = 40  # Har bir sahifadagi elementlar soni
      total_pages = (total_serials - 1) // page_size + 1  # Umumiy sahifalar soni

    # Sahifalarni chiqarish
      for page_number in range(1, total_pages + 1):
          start_index = (page_number - 1) * page_size
          end_index = min(page_number * page_size, total_serials)
          serials_on_page = cursor.execute("SELECT * FROM serial LIMIT ? OFFSET ?", (page_size, start_index)).fetchall()

        # Yangi klaviatura yaratish
          key = InlineKeyboardMarkup(row_width=3)

        # Sahifadagi har bir serial uchun tugmalar
          for serial in serials_on_page:
            # Agar serial nomi 17 harfdan uzun bo'lsa, faqatgina 17 harfni olib yuborish
              if len(serial[1]) > 15:
                  display_name = serial[1][:15]
              else:
                  display_name = serial[1]

              key.add(InlineKeyboardButton(text=f"{display_name}", callback_data=f"info-{serial[0]}"))

        # Agar keyingi sahifa mavjud bo'lsa, "Davomi ⬇️" tugmasini qo'shish
          if page_number < total_pages:
              key.add(InlineKeyboardButton(text="Davomi ⬇️", callback_data=f"next_page-{page_number + 1}"))

        # Xabarni jo'natish
          bot.reply_to(msg, "Film  nomini tanlang!", reply_markup=key)

  except:
    pass


@bot.callback_query_handler(func=lambda call:True)
def callback(call):
  cid = call.message.chat.id
  mid = call.message.id
  data = call.data
  if data=="member":
    bot.delete_message(cid,mid)
    if join(cid):
      bot.send_message(cid,f"""
🎉 ᴛᴀʙʀɪᴋʟᴀʏᴍᴀɴ

✅ sɪᴢ ᴋᴀɴᴀʟʟᴀʀɢᴀ ᴍᴜᴏғᴀǫʏᴀᴛʟɪ ᴏʙᴜɴᴀ ʙᴏ'ʟᴅɪɴɢɪᴢ ᴇɴᴅɪ ᴇsᴀ ᴋᴀɴᴀʟɢᴀ ᴏᴛɪʙ ʏᴜᴋʟᴀʙ ᴏʟɪsʜ ᴛᴜɢᴍᴀsɪɴɪ ǫᴀʏᴛᴀᴅᴀɴ ʙᴏsɪɴɢ\nʏᴏᴋɪ Film ᴋᴏᴅɪɴɪ ᴋɪʀɪᴛɪɴɢ  ᴋᴏᴅɪɴɪ ʙɪʟɪsʜ ᴜᴄʜᴜɴ ᴋᴀɴᴀʟɢᴀ ᴋʀɪɴɢ

Yoki Film kodini qaytadan yuboring""",reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text="🔎 Kanalimiz",url="https://t.me/DRAMA_TV_1")))


  if data=='solo':
    try:
      file_id = FILE_ID['id']
      caption =CAPTION['text'].replace("'","||")
      all = cursor.execute("SELECT * FROM kino").fetchall()
      if len(all)==0:
        code = 1
      else:
        code = all[-1][0]+1
      cursor.execute(f"INSERT INTO kino(file_id,caption) VALUES('{file_id}','{caption}')")
      bot.send_video(cid,video=file_id,caption=caption.replace("'","'"),reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text="📥 Yuklab olish",url=f"{b_url}?start=f{code}")))

    except Exception as e:
      print(e)
  elif "serial" in data:
    id  = data.split("-")[1]
    bot.delete_message(cid,mid)
    file_id = FILE_ID['id']
    caption =CAPTION['text'].replace("'","`")
    all = cursor.execute("SELECT * FROM movies").fetchall()
    if len(all)==0:
      code = 1
    else:
      code = all[-1][0]+1
    serial = cursor.execute(f"SELECT * FROM serial WHERE id={id}").fetchone()[1]
    cursor.execute(f"INSERT INTO movies(file_id,caption,serial) VALUES('{file_id}','{caption}','{serial}')")
    bot.send_video(cid,video=file_id,caption=caption.replace("'","'"),reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text="📥 Yuklab olish",url=f"{b_url}{id}")))

  elif "yukla" in data:
    id  = data.split("-")[1]
    json = cursor.execute(f"SELECT * FROM movies WHERE id={id}").fetchone()
    bot.send_video(cid,video=json[1],caption=json[2].replace("'","'"),protect_content=True)
  elif "info" in data:
    id  = data.split("-")[1]
    json = cursor.execute(f"SELECT * FROM serial WHERE id={id}").fetchone()
    get = cursor.execute(F"SELECT * FROM movies WHERE serial='{json[1]}'").fetchall()
    c = 0
    key = InlineKeyboardMarkup(row_width=4)
    m = []
    for i in get:
      c+=1
      m.append(InlineKeyboardButton(text=f"🗑 {c}",callback_data=f'del-{i[0]}'))
    key.add(*m)
    key.add(InlineKeyboardButton(text=f"❌ O'chrish",callback_data=f'remove-{id}'),InlineKeyboardButton(text=f"Kanalga yuborish",callback_data=f'share-{id}'))
    bot.send_photo(cid,photo=json[2],caption=f"<b>🎥 Animesi: {json[1]}\n\n📥 Yuklash: {b_url}{id}\n\n🎬 Qisimlar: {c}</b>",reply_markup=key)
  elif "del" in data:
    id  = data.split("-")[1]
    bot.delete_message(cid,mid)
    cursor.execute(f"DELETE FROM movies WHERE id={id}")
    js = cursor.execute("SELECT * FROM serial").fetchall()
    key = InlineKeyboardMarkup()
    for i in js:
      key.add(InlineKeyboardButton(text=f"{i[1]}",callback_data=f"info-{i[0]}"))
    bot.send_message(cid,"<b>❌ Film qismi o'chirildi!</b>",reply_markup=key)
  elif "remove" in data:
    id  = data.split("-")[1]
    bot.delete_message(cid,mid)
    cursor.execute(f"DELETE FROM serial WHERE id={id}")
    conn.commit()
    js = cursor.execute("SELECT * FROM serial").fetchall()
    key = InlineKeyboardMarkup()
    for i in js:
      key.add(InlineKeyboardButton(text=f"{i[1]}",callback_data=f"info-{i[0]}"))
    bot.send_message(cid,"<b>❌ Film o'chirildi!</b>",reply_markup=key)

  elif "share" in data:
      id  = data.split("-")[1]
      js = cursor.execute(F"SELECT * FROM serial WHERE id={id}").fetchall()
      bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="Post kanalga yuborilmoqda...")
      channel_id = -1002220051442  # Kanal identifikatori (negative qiymat)
      bot.send_chat_action(cid, 'upload_photo')  # Yuborish jarayonini bildirish
      bot.send_photo(channel_id, photo=js[0][2], caption=f"""
              <b>
──────⌑ ◌ ♡ ◌ ⌑──────
Nomi :  {js[0][1]}

Kodi : ☞ <code> {js[0][0]} </code>

<a href="https://t.me/DRAMA_TV_1"> Kanal  : DramaTV</a>
──────⌑ ◌ ♡ ◌ ⌑──────
✽ 𝓑𝓲𝔃𝓷𝓲 𝓴𝓪𝓷𝓪𝓵𝓭𝓪 𝓺𝓸𝓵𝓲𝓷𝓰 !
              </b>""",reply_markup=InlineKeyboardMarkup().add(
                  InlineKeyboardButton(text="📥 ʏᴜᴋʟᴀʙ ᴏʟɪꜱʜ", url=f"{b_url}{id}")))

      bot.send_message(cid, "✅ Post kanalga yuklandi")


def start_bot():
  try:
      bot.polling(none_stop=True)
  except Exception as e:
      bot.send_message(creator, f"""
Xatolik

<code>{e}</code>""")
      print(e)
      traceback.print_exc()
      start_bot()  # Botni qayta ishga tushurish


start_bot()