#!/usr/bin/env python3

import os
import requests
import subprocess 
import sys

INSTALL_PATH = "/opt/turkman"
TRPATH = "/usr/share/man/tr/"
GITHUB_REPO = "mmapro12/turkman-pretest"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/"

def check_local_translation(command):
    """Yerel Türkçe man sayfasını kontrol eder."""
    command_path = subprocess.run(["man", "-w", "-L", "tr", command], capture_output=True, text=True)
    if command_path.stdout.strip():  # Eğer çıktı boş değilse
        result = subprocess.run(["man", "-L", "tr", command])
        return result.returncode == 0
    return False

def check_github_translation(command):
    """GitHub deposunda çeviri olup olmadığını kontrol eder."""
    url = f"{GITHUB_RAW_URL}{command}.1"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    return None

def turkman(command):
    """Ana akış."""
    if check_local_translation(command):
        return
    
    github_translation = check_github_translation(command)
    if github_translation:
        with open("./buffer_github", "w") as file:
            file.write(github_translation)
        subprocess.run(["less", "./buffer_github"])
        return
    
    print("Çeviri bulunamadı. Yapay zeka ile çeviri test aşamasında...")

def get_version():
    try:
        with open(f"{INSTALL_PATH}/version.txt", "r") as f:
            return f.readline().strip()
    except FileNotFoundError:
        return "0.0.0"


def run_script(script_name):
    script_path = os.path.join(INSTALL_PATH, script_name)
    if not os.path.exists(script_path):
        print(f"❌ Hata: {script_name} bulunamadı!")
        sys.exit(1)

    try:
        subprocess.run(["sudo", script_path], check=True)
    except subprocess.CalledProcessError:
        print(f"❌ {script_name} çalıştırılırken hata oluştu!")

def check_command(command):
    """Man sayfasının olup olmadığını kontrol eder."""
    path = subprocess.run(["man", "-w", command], capture_output=True, text=True)
    return bool(path.stdout.strip()) and os.path.exists(path.stdout.strip())

def check_update(p=False):
    v = get_version()
    url = f"https://raw.githubusercontent.com/mmapro12/turkman/main/version.txt"
    response = requests.get(url)
    if response.status_code == 200 and response.text.strip() != v:
        i = input(f"Turkman eski sürümde ({v} -> {response.text.strip()}). Güncellemek ister misiniz? (y/n) ")
        if i.lower() == "y":
            run_script("update.sh")
    elif p:
        print("Turkman en son sürümde.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanım: turkman <komut>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "uninstall":
        run_script("uninstall.sh")
        sys.exit(0)
    elif command == "update":
        check_update(True)
        sys.exit(0)
    
    check_update()
    
    if command in ["-h", "-?", "--help"]:
        subprocess.run(["less", "./docs/man/man1/turkman.1"])
    elif command in ["-trl", "--trless"]:
        subprocess.run(["less", "./docs/yardim/yardim.txt"])
    elif command in ["-y", "--yardım", "--yardim"]:
        turkman("turkman")
    elif command in ["-v", "--version"]:
        print(f"Turkman {get_version()}")
        sys.exit(0)
    elif check_command(command):
        turkman(command)
    else:
        print(f"'{command}' adlı bir uygulama bulunamadı.")
        sys.exit(1)

