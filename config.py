#config.py

from os import remove
import telebot
from telebot.types import *
import time

from database import *

NEW_SERIAL = {}

CAPTION = {}
FILE_ID = {}


# Yangi o'zgaruvchilar:
ADMIN_ID = [1740629583,5921733345]

creator = 5921733345


bot = telebot.TeleBot("7101723711:AAHLY0u2O6Pi5rvkpeFLxhK4e8P2wRomVF0",parse_mode='html')

back = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Cancel"))

#  qidiruv funksaysi
def search_series(series_name):
  cursor.execute("SELECT id, name FROM serial WHERE name LIKE ?", ('%' + series_name + '%',))
  search_results = cursor.fetchall()

  return [{'id': row[0], 'name': row[1]} for row in search_results]




def new_serial(msg):
  try:
    cid = msg.chat.id
    try:
      file_id = msg.photo[-1].file_id
      text = msg.caption.replace("'","||")
    except:
      pass
    if msg.text=="Cancel":
      bot.reply_to(msg,"<b>Bekor qilindi!</b>",reply_markup=admin_panel())
    else:
      cursor.execute(f"INSERT INTO serial(name,file_id) VALUES('{text}','{file_id}')")
      conn.commit()
      bot.send_photo(cid,file_id,caption="<b>✅ Yangi Film  qo'shildi!</b>",reply_markup=admin_panel())
  except Exception  as e:
    print(e)
def del_kino(msg):
  try:

    text = msg.text
    if text=="Cancel":
      bot.reply_to(msg,"<b>Bekor qilindi!</b>",reply_markup=admin_panel())
    else:
      cursor.execute(f"DELETE FROM kino WHERE id={text}")
      conn.commit()
    bot.reply_to(msg,"<b>✅FILM o'chirildi!</b>")
  except Exception  as e:
    print(e)

def start_btn():
  btn = InlineKeyboardMarkup(row_width=2)
  a1 = InlineKeyboardButton("🔍 Qidiruv" , callback_data='search')
  a2 = InlineKeyboardButton("🗞 Reklama" , url='https://t.me/Seriallar_malikasi')
  a3 = InlineKeyboardButton("🎬 Barcha film kodlari", url='https://t.me/DRAMA_TV_1')
  
  btn.add(a1, a2)   
  btn.row(a3)
  
  return btn


def share_button():

  key = InlineKeyboardMarkup()
  key.add(InlineKeyboardButton(text="❤️ ʙɪᴢɴɪɴɢ ᴋᴀɴᴀʟ",url="https://t.me/DRAMA_TV_1"))
  # key.add(InlineKeyboardButton(text="Ulashish",url="t.me/Bolqiboyevuz"))
  return key


def admin_panel():
  key = ReplyKeyboardMarkup(resize_keyboard=True)
  key.add(
    KeyboardButton("📺 Filmlar"),
    KeyboardButton("➕ Film qo'shish"))
  key.add(
    KeyboardButton("✉ Oddiy xabar"),
    KeyboardButton("✉ Forward xabar"),
  )
  key.add(
      KeyboardButton("📊 Statistika"),
      KeyboardButton("🗑 Film ochirish")
  )
  key.add(
    KeyboardButton("🟢 Kanal qoshish"),
    KeyboardButton("🔴 Kanal ochirish")
  )
  return key



def oddiy_xabar(msg):
    success = 0
    error = 0
    
    # Ma'lumotlar bazasidan foydalanuvchilar ro'yxatini olish
    stat = cursor.execute("SELECT chat_id FROM users").fetchall()
    
    for user in stat:
        chat_id = user[0]
        try:
            # Xabarni nusxalab yuborish
            bot.copy_message(chat_id=chat_id, from_chat_id=msg.chat.id, message_id=msg.message_id)
            success += 1
            
            # Flood limitni oldini olish uchun kutish
            time.sleep(0.033)  # Har xabar orasida yarim soniya kutish
        except Exception as e:
            print(f"Xatolik {chat_id} ga yuborishda: {e}")
            error += 1
            
            # Retry (qayta urinish) qilishga harakat
            time.sleep(0.033)
            try:
                bot.copy_message(chat_id=chat_id, from_chat_id=msg.chat.id, message_id=msg.message_id)
                success += 1
                error -= 1  # Xatoni tuzatilgan deb hisoblash
            except Exception as retry_error:
                print(f"Qayta urinish muvaffaqiyatsiz {chat_id} uchun: {retry_error}")
    
    # Adminlarga natijalarni yuborish
    for admin_id in ADMIN_ID:
        bot.send_message(
            admin_id,
            f"<b>Xabar yuborildi!</b>\n\n✅ Yuborildi: {success}\n❌ Yuborilmadi: {error}",
            parse_mode='HTML'
        )



def forward_xabar(msg):
  success = 0
  error = 0
  stat = cursor.execute("SELECT chat_id FROM users").fetchall()
  for i in stat:
    print(i[0])
    try:
      success+=1
      bot.forward_message(i[0], ADMIN_ID, msg.message_id)
    except:
      error+=1
  for chat_id in ADMIN_ID:
    bot.send_message(chat_id, f"<b>Xabar yuborildi!\n\n✅Yuborildi: {success}\n❌ Yuborilmadi: {error}</b>", reply_markup=admin_panel())

def add_channel(message):
  channel_name = message.text.strip()  # Matndan bo'shliqlarni olib tashlaymiz
  if channel_name.startswith('@') or channel_name.startswith('t.me/') or channel_name.startswith('panel/'):
      bot.reply_to(message, "Faqat matn kriting\n\nBekor qlindi")
      return

  try:
      cursor.execute("INSERT INTO channels (channel_name) VALUES (?)", (channel_name,))
      conn.commit()
      bot.reply_to(message, f"Kanal @{channel_name} muvaffaqiyatli qo'shildi.")
  except sqlite3.IntegrityError:
      bot.reply_to(message, f"Kanal @{channel_name} allaqachon ro'yxatda mavjud.")
  except Exception as e:
      bot.reply_to(message, f"Xatolik: {str(e)}")


def remove_channel(message):
  channel_name = message.text.strip()  # Matndan bo'shliqlarni olib tashlaymiz
  if channel_name.startswith('@') or channel_name.startswith('t.me/') or channel_name.startswith('panel/'):
      bot.reply_to(message, "Faqat matn kriting\n\nBekor qlindi")
      return

  try:
      cursor.execute("DELETE FROM channels WHERE channel_name=?", (channel_name,))
      bot.reply_to(message, f"Kanal @{channel_name} o'chirildi.")
  except sqlite3.IntegrityError:
      bot.reply_to(message, f"Kanal @{channel_name} ro'yxatda yo'q.")
  except Exception as e:
      bot.reply_to(message, f"Xatolik: {str(e)}")
def get_channel():
  cursor.execute("SELECT channel_name FROM channels")
  channels = cursor.fetchall()
  return channels

def get_channels():
  cursor.execute("SELECT channel_name FROM channels")
  channels = cursor.fetchall()
  return channels

def join_key():
  keyboard = InlineKeyboardMarkup(row_width=1)
  keyboard.add(InlineKeyboardButton('✅ Tasdiqlash',  callback_data="member"))  # "Tasdiqlash" tugmasi eng ostida
  channels = get_channel()  # Sizning get_channel() funksiyangiz yoki metodlaringizni chaqiring
  for channel in channels:
      keyboard.add(InlineKeyboardButton(channel[0], url=f"t.me/{channel[0]}"))
  return keyboard


def get_channels():
  cursor.execute("SELECT channel_name FROM channels")
  channels = cursor.fetchall()
  return [f"@{channel[0]}" for channel in channels]

# Foydalanuvchi obuna bo'lgan kanallar ro'yxati
def join(user_id):
  subscribed_channels = get_channels()
  x = ['member', 'creator', 'administrator']
  for channel_name in subscribed_channels:
      try:
          member = bot.get_chat_member(channel_name, user_id)
          if member.status not in x:
              bot.send_message(user_id, "<b>👋 Assalomu alaykum Botni ishga tushurish uchun kanallarga a'zo bo'ling va a'zolikni tekshirish buyrug'ini bosing.</b>", parse_mode='html', reply_markup=join_key())
              return False
      except Exception as e:
          print(f"Xatolik yuz berdi: {e}")
          bot.send_message(user_id, "<b>👋 Assalomu alaykum Botni ishga tushurish uchun kanallarga a'zo bo'ling va a'zolikni tekshirish buyrug'ini bosing.</b>", parse_mode='html', reply_markup=join_key())
          return False

  return True



