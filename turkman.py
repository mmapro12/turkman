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
    if TRPATH in command_path.stdout.strip(): 
        result = subprocess.run(["man", "-L", "tr", command])
        return result.returncode == 0
    return False


def check_github_translation(command):
    """GitHub deposunda çeviri olup olmadığını kontrol eder."""
    url = f"{GITHUB_RAW_URL}{command}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    return None


def main(command):
    """Ana akış."""
    if check_local_translation(command):
        return
    
    github_translation = check_github_translation(command)
    if github_translation:
        with open(f"{INSTALL_PATH}/buffs/{command}", "w") as file:
            file.write(github_translation)
        subprocess.run(["man", f"{INSTALL_PATH}/buffs/{command}"])
        return
    
    print("Çeviri bulunamadı. Yapay zeka ile çeviri test aşamasında...")


def run_script(script_name):
    """Scriptleri çalıştırır."""
    script_path = os.path.join(INSTALL_PATH, "scripts", script_name)
    if not os.path.exists(script_path):
        print(f"Hata: {script_name} bulunamadı!")
        sys.exit(1)

    try:
        subprocess.run(["sudo", script_path], check=True)
    except subprocess.CalledProcessError:
        print(f"{script_name} çalıştırılırken hata oluştu!")


def check_command(command):
    """Man sayfasının olup olmadığını kontrol eder."""
    path = subprocess.run(["man", "-w", command], capture_output=True, text=True)
    return bool(path.stdout.strip()) and os.path.exists(path.stdout.strip())


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanım: turkman <komut>")
        sys.exit(1)
    command = sys.argv[1]
    
    if command == "uninstall":
        run_script("uninstall.sh")
        sys.exit(0)
    elif command == "update":
        run_script("update.sh")
        sys.exit(0)
    elif command in ["-h", "-?", "--help"]:
        subprocess.run(["less", f"{INSTALL_PATH}/docs/man/man1/turkman"])
    elif command in ["-trl", "--trless"]:
        subprocess.run(["less", f"{INSTALL_PATH}/docs/yardim/yardim.txt"])
    elif command in ["-l", "--less"]:
        subprocess.run(["less", "--help"])
    elif command in ["-y", "--yardım", "--yardim", "turkman"]:
        subprocess.run(["less", f"{INSTALL_PATH}/docs/tr/turkman"])
    elif command in ["-v", "--version"]:
        print("Turkman")
        sys.exit(0)
    elif check_command(command):
        main(command)
    else:
        print(f"'{command}' adında bir komut bulunamadı.")
        sys.exit(1)

