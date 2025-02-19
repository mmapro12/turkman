import requests
import subprocess

TRPATH = "/usr/share/man/tr/"

# GitHub Depo Bilgileri
GITHUB_REPO = "mmapro12/turkman-pretest"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/"
GITHUB_TOKEN = "GITHUB_ACCESS_TOKEN"

# Yapay Zeka API Anahtarı
AI_API_KEY = "API_KEY"

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

def translate_with_ai(original_text):
    """Yapay zeka API kullanarak çeviri yapar."""
    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4",
        "prompt": f"Çeviri: {original_text}\nLütfen bu metni profesyonel bir şekilde Türkçeye çevir.",
        "max_tokens": 1000
    }
    response = requests.post(AI_API_KEY, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()["choices"][0]["text"]
    return None

def upload_to_github(command, translation):
    """Kullanıcı onay verirse çeviriyi GitHub’a yükler."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/manpages/{command}.txt"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    data = {
        "message": f"Add translated man page for {command}",
        "content": translation.encode('utf-8').decode('latin1').encode('base64').decode(),  # Base64 format
        "branch": "main"
    }
    response = requests.put(url, json=data, headers=headers)
    return response.status_code == 201


def turkman_test(command):
    """ Ana çalışma fonksiyonu """
    local_translation = check_local_translation(command)
    if local_translation:
        subprocess.run(["man", "-L", "tr", command])
        return

    github_translation = check_github_translation(command)
    if github_translation:
        with open("buffer_github", "w") as file:
            file.write(github_translation)
        subprocess.run(["man", "./buffer_github"])
        return
    
    print("Çeviri bulunamadı, yapay zeka ile çeviri yapılıyor...")

def turkman(command):
    """Ana çalışma akışı."""
    print(f"'{command}' için Türkçe man sayfası aranıyor...")

    # 1. Yerel kontrol
    local_translation = check_local_translation(command)
    if local_translation: 
        print(local_translation)
        return

    # 2. GitHub deposunda arama
    github_translation = check_github_translation(command)
    if github_translation:
        print(f"GITHUB'DAN ÇEVİRİ BULUNDU:\n{github_translation}")
        return

    # 3. AI ile çeviri
    print("Çeviri bulunamadı, yapay zeka ile çeviri yapılıyor...")
    original_man = subprocess.run(["man", command], capture_output=True, text=True).stdout
    if not original_man:
        print("Komut için orijinal man sayfası bulunamadı!")
        return

    translated_text = translate_with_ai(original_man)
    if translated_text:
        print(f"YAPAY ZEKA ÇEVİRİSİ:\n{translated_text}")

        # Kullanıcıya GitHub'a yükleyelim mi diye sor
        upload = input("Bu çeviriyi GitHub’a yüklemek ister misiniz? (evet/hayır): ")
        if upload.lower() in ["evet", "e"]:
            if upload_to_github(command, translated_text):
                print("Çeviri başarıyla GitHub’a yüklendi!")
            else:
                print("GitHub’a yükleme başarısız oldu.")
    else:
        print("Yapay zeka çevirisi başarısız!")



if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Kullanım: turkman <komut>")
    else:
        turkman_test(sys.argv[1])


