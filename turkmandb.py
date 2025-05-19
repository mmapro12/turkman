import sqlite3
import subprocess
import requests
import os
from datetime import datetime


INSTALL_PATH = "/opt/turkman"
TRPATH = "/usr/share/man/tr/"
GITHUB_REPO = "mmapro12/turkmandb"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/refs/heads/main/pages/"

HOME_DIR = os.path.expanduser("~")
DB_DIR = os.path.join(HOME_DIR, ".turkmandb")
DB_PATH = os.path.join(DB_DIR, "turkman.db")

def init_db():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS man_pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command TEXT UNIQUE NOT NULL,
            translated TEXT NOT NULL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def add_translation(command, translated):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO man_pages (command, translated) VALUES (?, ?)", (command, translated))
        conn.commit()
        print(f"[✓] '{command}' komutu veritabanına eklendi.")
    except sqlite3.IntegrityError:
        print(f"[!] '{command}' zaten eklenmiş.")
    conn.close()


def get_translation(command):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT translated FROM man_pages WHERE command = ?", (command,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def update_translation(command, new_translation):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE man_pages
        SET translated = ?, last_updated = ?
        WHERE command = ?
    """, (new_translation, datetime.now(), command))
    conn.commit()
    conn.close()
    print(f"[✓] '{command}' çevirisi güncellendi.")


def get_turkmandb():
    response = requests.get("https://raw.githubusercontent.com/mmapro12/turkmandb/refs/heads/main/pages.txt")
    if response.status_code == 200:
        allpages = response.text
        for cmd in allpages.splitlines():
            url = f"{GITHUB_RAW_URL}{cmd}"
            cmd_req = requests.get(url)
            if cmd_req.status_code == 200:
                add_translation(command=cmd, translated=cmd_req.text)
            else:
                print(f"turkmandb: {cmd} komutu için çevrili man sayfası alınamadı.")
    return False


if __name__ == "__main__":
    print("turkmandb")
