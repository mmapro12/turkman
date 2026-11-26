import sqlite3
import requests
import os


TRPATH = "/usr/share/man/tr/"
GITHUB_REPO = "mmapro12/turkmandb"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/refs/heads/main/pages/"

HOME_DIR = os.path.expanduser("~")
PAGES_LIST_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/refs/heads/main/pages.txt"
REQUEST_TIMEOUT = 10
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
    """Tüm çevirileri indirir; eksik kalan olursa RuntimeError fırlatır."""
    try:
        response = requests.get(PAGES_LIST_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Çeviri listesi alınamadı: {e}") from e

    commands = [line.strip() for line in response.text.splitlines() if line.strip()]
    failed = []
    for cmd in commands:
        try:
            page = requests.get(f"{GITHUB_RAW_URL}{cmd}", timeout=REQUEST_TIMEOUT)
            page.raise_for_status()
        except requests.RequestException:
            print(f"turkmandb: {cmd} komutu için çevrili man sayfası alınamadı.")
            failed.append(cmd)
            continue
        if not add_translation(command=cmd, translated=page.text):
            failed.append(cmd)

    if failed:
        raise RuntimeError(f"{len(failed)}/{len(commands)} sayfa alınamadı: {', '.join(failed)}")


if __name__ == "__main__":
    print("turkmandb")


