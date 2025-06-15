import sqlite3
import requests
import os


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
    if not command or not translated:
        print("❌ Komut ve çeviri boş olamaz!")
        return False
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO man_pages (command, translated) VALUES (?, ?)", (command, translated))
        conn.commit()
        print(f"[✓] '{command}' komutu veritabanına eklendi.")
        return True
    except sqlite3.IntegrityError:
        cursor.execute("UPDATE man_pages SET translated = ? WHERE command = ?", (translated, command))
        conn.commit()
        print(f"[~] '{command}' zaten vardı, açıklama güncellendi.")
        return True
    except Exception as e:
        print(f"❌ Veritabanı hatası: {e}")
        return False
    finally:
        conn.close()


def get_translation(command):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT translated FROM man_pages WHERE command = ?", (command,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


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


