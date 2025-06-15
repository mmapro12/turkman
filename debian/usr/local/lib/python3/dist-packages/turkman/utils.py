import requests
import typer
from turkman.version import __version__ 

TRPATH = "/usr/share/man/tr/"
GITHUB_REPO = "mmapro12/turkmandb"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/refs/heads/main/pages/"

def get_version():
    """Turkman versiyonunu getirir."""
    return __version__


def get_latest_version() -> str | None:
    """Turkman'ın en güncel sürümünü getirir."""
    try:
        response = requests.get(
            f"https://raw.githubusercontent.com/mmapro12/turkman/main/version.txt",
            timeout=10
        )
        if response.status_code == 200:
            return response.text.strip()
    except requests.RequestException as e:
        typer.echo(f"Sürüm kontrol hatası: {e}", err=True)
    return None


def check_updates(current_command: str) -> None:
    """Güncelleme kontrolü yapar."""
    if current_command == "update":
        return
        
    current_version = get_version()
    latest_version = get_latest_version()
    
    if latest_version and current_version != latest_version:
        typer.echo(f"📦 Yeni sürüm mevcut: {current_version} → {latest_version}")
        typer.echo("🔄 Güncellemek için: turkman update")

