#database.py
import sqlite3

conn = sqlite3.connect('database.db',
                       check_same_thread=False,
                       isolation_level=None)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,chat_id INTIGER UNIQUE)")

cursor.execute("CREATE TABLE IF NOT EXISTS serial(id INTEGER PRIMARY KEY,name TEXT,file_id TEXT)")

cursor.execute("CREATE TABLE IF NOT EXISTS movies(id INTEGER PRIMARY KEY,file_id TEXT,caption TEXT,serial TEXT)")

cursor.execute("CREATE TABLE IF NOT EXISTS kino(id INTEGER PRIMARY KEY,file_id TEXT,caption TEXT)")

cursor.execute("CREATE TABLE IF NOT EXISTS channels(id INTEGER PRIMARY KEY, channel_name TEXT UNIQUE)")

cursor.execute("CREATE TABLE IF NOT EXISTS admins(id INTEGER PRIMARY KEY, admin_id INTIGER UNIQUE)")


conn.commit()

