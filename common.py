import requests
import typer

INSTALL_PATH = "/opt/turkman"
TRPATH = "/usr/share/man/tr/"
GITHUB_REPO = "mmapro12/turkmandb"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/refs/heads/main/pages/"

def get_version():
    """Turkman versiyonunu getirir."""
    with open(f"{INSTALL_PATH}/version.txt") as file:
        return file.readline().replace("\n", "")


def get_last_version():
    """Turkman'ın en güncel sürümünü getirir."""
    try:
        response = requests.get("https://raw.githubusercontent.com/mmapro12/turkman/refs/heads/main/version.txt", timeout=10)
        if response.status_code == 200:
            return response.text.replace("\n", "")
    except requests.RequestException as e:
        print(f"Sürüm kontrol hatası: {e}")
    return False


def check_updates(arg: str):
    v = get_version()
    lv = get_last_version()
    if v != lv and arg != "update":
        typer.echo(f"{v} -> {lv}")
        typer.echo("Turkman'ın yeni sürümü mevcut. Güncellemek için:\n\t $ turkman update")

