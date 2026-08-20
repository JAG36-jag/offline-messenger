import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.getcwd(), 'chat_history_v2.db')
class DatabaseManager:
    def __init__(self):
        # check_same_thread=False দেওয়া হয়েছে যাতে অন্য থ্রেড (যেমন নেটওয়ার্ক থ্রেড) থেকে অনায়াসে ডাটাবেজ এক্সেস করা যায়
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        """ডাটাবেজ এবং টেবিল তৈরি করার মেথড"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT,
                receiver TEXT,
                content TEXT,
                msg_type TEXT,
                status TEXT DEFAULT 'sent',  -- sent, seen, unseen
                timestamp TEXT
            )
        ''')
        self.conn.commit()

    def save_message(self, sender, receiver, content, msg_type="text", status="unseen"):
        """নতুন মেসেজ ডাটাবেজে সেভ করার মেথড"""
        now_time = datetime.now().strftime("%I:%M %p") # Example: 02:15 PM
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO messages (sender, receiver, content, msg_type, status, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (sender, receiver, content, msg_type, status, now_time))
        self.conn.commit()
        return now_time

    def mark_messages_as_seen(self, peer_name):
        """চ্যাট ওপেন করলে আনসিন মেসেজগুলো সিন (seen) মার্ক করার মেথড"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE messages SET status = 'seen' 
            WHERE sender = ? AND status = 'unseen'
        ''', (peer_name,))
        self.conn.commit()

    def get_messages_for_peer(self, peer_name):
        """নির্দিষ্ট একজন ইউজারের সাথে হওয়া সব মেসেজ হিস্ট্রি বের করার মেথড"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT sender, content, msg_type, status, timestamp FROM messages
            WHERE sender = ? OR receiver = ?
            ORDER BY id ASC
        ''', (peer_name, peer_name))
        return cursor.fetchall()

    def get_recent_chats(self):
        """
        প্রত্যেক ইউজারের সাথে হওয়া সর্বশেষ মেসেজটি (Recent Chat) বের করে আনবে।
        এটি ChatsScreen-এ লিস্ট দেখানোর জন্য ব্যবহার করা হয়।
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT 
                CASE WHEN sender = 'Me' THEN receiver ELSE sender END AS peer,
                content, 
                timestamp, 
                status
            FROM messages
            WHERE id IN (
                SELECT MAX(id)
                FROM messages
                GROUP BY CASE WHEN sender = 'Me' THEN receiver ELSE sender END
            )
            ORDER BY id DESC
        ''')
        return cursor.fetchall()