import subprocess
import requests
import typer
from turkman.version import __version__ 

TRPATH = "/usr/share/man/tr/"
GITHUB_REPO = "mmapro12/turkmandb"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/refs/heads/main/pages/"
GITHUB_API_URL = "https://api.github.com/repos/mmapro12/turkman"

def get_latest_release_info(timeout: float = 10, quiet: bool = False):
    """GitHub'dan en son sürüm bilgilerini alır."""
    try:
        response = requests.get(f"{GITHUB_API_URL}/releases/latest", timeout=timeout)
        if response.status_code == 200:
            return response.json()
        elif not quiet:
            typer.echo(f"❌ GitHub API'den sürüm bilgisi alınamadı: {response.status_code}", err=True)
        return None
    except Exception as e:
        if not quiet:
            typer.echo(f"❌ GitHub API hatası: {e}", err=True)
        return None


def compare_versions(current: str, latest: str) -> bool:
    """Sürüm karşılaştırması yapar. True döndürürse güncelleme gerekir."""
    try:
        def version_tuple(version):
            # v.6.2 -> (0, 6, 2)
            clean_version = version.lstrip('v')
            return tuple(map(int, clean_version.split('.')))
        
        current_tuple = version_tuple(current)
        latest_tuple = version_tuple(latest)
        
        return latest_tuple > current_tuple
    except Exception as e:
        typer.echo(f"❌ Sürüm karşılaştırma hatası: {e}", err=True)
        return False


def download_file(url: str, filepath: str) -> bool:
    """Dosya indirir."""
    try:
        typer.echo(f"📥 İndiriliyor: {url}")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\r📊 İlerleme: {progress:.1f}%", end='', flush=True)
        
        print()  # Yeni satır
        typer.echo("✅ İndirme tamamlandı!")
        return True
    except Exception as e:
        typer.echo(f"❌ İndirme hatası: {e}", err=True)
        return False


def is_installed_via_apt() -> bool:
    """Turkman'ın apt ile kurulu olup olmadığını kontrol eder."""
    try:
        result = subprocess.run(
            ["dpkg", "-l", "turkman"], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        return result.returncode == 0 and "ii" in result.stdout
    except Exception:
        return False


def is_installed_via_pip() -> bool:
    """Turkman'ın pip ile kurulu olup olmadığını kontrol eder."""
    try:
        result = subprocess.run(
            ["pip", "show", "turkman"], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def get_turkman_executable_path() -> str | None:
    """Turkman executable'ının yolunu bulur."""
    try:
        result = subprocess.run(
            ["which", "turkman"], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


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
    # Güncelleme kontrolü isteğe bağlıdır: başarısız olursa komut çalışmaya devam eder
    release_info = get_latest_release_info(timeout=2, quiet=True)
    
    if not release_info:
        return
    
    latest_version = release_info["tag_name"]
    needs_update = compare_versions(current_version, latest_version)
    
    if needs_update:
        typer.echo(f"📦 Yeni sürüm mevcut: {current_version} → {latest_version}")
        typer.echo("🔄 Güncellemek için: turkman update")


