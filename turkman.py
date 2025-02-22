#!/usr/bin/env python3

import os
import requests
import subprocess 

INSTALL_PATH = "/opt/turkman"
TRPATH = "/usr/share/man/tr/"

GITHUB_REPO = "mmapro12/turkman-pretest"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/"

# Yapay Zeka API Bilgileri.Şimdilik çalışmıyor.Test aşamasında
# AI_API_KEY = os.getenv("AI_API_KEY")
# MODEL = None 
# def tarnslate_with_ai(text, api_key, model):
#     """AI_API_KEY kullanarak ingilizce man dosyasını türkçeye çevirir.Şimdilik çalışmıyor.Geliştirme aşamasında."""
#     return None
# 
#
# def request_upload_to_github(command, translation):
#     """Kullanıcı onay verirse çeviriyi GitHub’a yüklemek için istek atar.Şimdilik çalışmıyor.Geliştirme aşamasında."""
#     return None


def check_local_translation(command):
    """Yerel Türkçe man sayfasını kontrol eder."""
    command_path = subprocess.run(["man", "-w", "-L", "tr", command], capture_output=True, text=True)
    if TRPATH in command_path.stdout:
        result = subprocess.run(["man", "-L", "tr", command], capture_output=True, text=True)
        if result.returncode == 0:
            return True 
    return None


def check_github_translation(command):
    """GitHub deposunda çeviri olup olmadığını kontrol eder."""
    url = f"{GITHUB_RAW_URL}{command}.1"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    return None


def turkman(command):
    """Ana akış."""

    # 1. Yerel kontrol
    local_translation = check_local_translation(command)
    if local_translation:
        subprocess.run(["man", "-L", "tr", command])
        return

    # 2. GitHub deposunda arama
    github_translation = check_github_translation(command)
    if github_translation:
        with open("./buffer_github", "w") as file:
            file.write(github_translation)
        subprocess.run(["man", "./buffer_github"])
        return
    print("Çeviri bulunamadı.Yapay zeka ile çevirme hala çalışmıyor.Test aşamasında...")

    # 3. AI ile çeviri.Şimdilik çalışmıyor.Hala test aşamasında.
    # print("Çeviri bulunamadı, yapay zeka ile çeviri yapılıyor...")
    # original_man_path = subprocess.run(["man", "-w", command, "|", "col", "-bx"], capture_output=True, text=True).stdout
    # original_man = subprocess.run(["zcat", original_man_path], capture_output=True, text=True).stdout
    # if not original_man:
    #     print("Komut için orijinal man sayfası bulunamadı!")
    #     return
    # translated_man = translate_with_ai(original_man, AI_API_KEY, MODEL)


def get_version():
    with open(f"{INSTALL_PATH}/version.txt", "r") as f:
        version = f.readline()
        return version


def update():
    """Update scriptini çalıştırır"""
    script_path = os.path.join(INSTALL_PATH, "update.sh")
    if os.path.exists(script_path):
        subprocess.run(["sudo", script_path], check=True)
    else:
        print("❌ Güncelleme komutu bulunamadı!")


def uninstall():
    """Uninstall scriptini çalıştırır"""
    script_path = os.path.join(INSTALL_PATH, "uninstall.sh")
    if os.path.exists(script_path):
        subprocess.run(["sudo", script_path], check=True)
    else:
        print("❌ Kaldırma komutu bulunamadı!")


def check_command(command):
    path = subprocess.run(["man", "-w", command], capture_output=True, text=True)
    if os.path.exists(path.stdout):
        return True
    return False


def check_update(p=False):
    v = get_version()
    url = f"https://raw.githubusercontent.com/mmapro12/turkman/main/version.txt"
    response = requests.get(url)
    if response.status_code == 200:
        if response.text != v:
            i = input(f"Turkman eski sürümde({v} -> {response.text}).Güncellemek istermisiniz? (y/n) ")
            if i.lower() == "y":
                update()
        else:
            if p: print("Turkman en son sürümde.")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Kullanım: turkman <komut>")
        sys.exit(1)
    command = sys.argv[1]

    if command == "uninstall":
        uninstall()
        sys.exit(0)

    if command == "update":
        check_update(True)
        sys.exit(0)

    check_update()
    if command in ["-h", "-?", "--help"]:
        subprocess.run(["man", "./docs/man/man1/turkman.1"])
    elif command in ["-trl", "--trless"]:
        subprocess.run(["less", "./docs/yardim/yardim.txt"])
    elif command in ["-y", "--yardım", "--yardim"]:
        turkman("turkman")
    elif command in ["-v", "--version"]:
        version = get_version()
        print(f"Turkman {version}")
        sys.exit(0)
    elif check_command(command):
        turkman(command)
    else:
        print(f"'{command}' adlı bir uygulama bulunmamakta.")
        sys.exit(1)


