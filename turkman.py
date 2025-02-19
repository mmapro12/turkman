#!/usr/bin/env python3

import os
import requests
import subprocess
from dotenv import load_dotenv

load_dotenv()

TRPATH = "/usr/share/man/tr/"

# GitHub Depo Bilgileri
GITHUB_REPO = "mmapro12/turkman-pretest"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/"

# Yapay Zeka API Bilgileri.Şimdilik çalışmıyor.Geliştirme aşamasında
# AI_API_KEY = os.getenv("AI_API_KEY")
# MODEL = None 

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


# def tarnslate_with_ai(text, api_key, model):
#     """AI_API_KEY kullanarak ingilizce man dosyasını türkçeye çevirir.Şimdilik çalışmıyor.Geliştirme aşamasında."""
#     return None
# 
#
# def request_upload_to_github(command, translation):
#     """Kullanıcı onay verirse çeviriyi GitHub’a yüklemek için istek atar.Şimdilik çalışmıyor.Geliştirme aşamasında."""
#     return None


def turkman(command):
    """Ana çalışma akışı."""

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
    print("Çeviri bulunamadı, yapay zeka ile çeviri yapılıyor...")



    # 3. AI ile çeviri.Şimdilik çalışmıyor.Hala geliştirme aşamasında.
    # print("Çeviri bulunamadı, yapay zeka ile çeviri yapılıyor...")
    # original_man_path = subprocess.run(["man", "-w", command, "|", "col", "-bx"], capture_output=True, text=True).stdout
    # original_man = subprocess.run(["zcat", original_man_path], capture_output=True, text=True).stdout
    # if not original_man:
    #     print("Komut için orijinal man sayfası bulunamadı!")
    #     return
    # translated_man = translate_with_ai(original_man, AI_API_KEY, MODEL)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Kullanım: turkman <komut>")
    elif sys.argv[1] in ["-h", "-?", "--help"]:
        subprocess.run(["man", "./docs/man/man1/turkman.1"])
    elif sys.argv[1] in ["-trl", "--trless", "--yardim", "--yardım"]:
        subprocess.run(["less", "./docs/yardim/yardim.txt"])
    else:
        turkman(sys.argv[1])


