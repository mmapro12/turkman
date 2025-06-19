#!/usr/bin/env python3

import sys
import os
import requests
import subprocess
import typer
import tempfile
import shutil
from pathlib import Path
import json
import re
import turkman.db as turkmandb
import turkman.utils as utils

turkmandb.init_db()
app = typer.Typer()
db_app = typer.Typer()

TURKMAN_COMMANDS = ["db", "update", "uninstall", "version", "--help", "manpage"]
TRPATH = "/usr/share/man/tr/"
GITHUB_REPO = "mmapro12/turkmandb"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/refs/heads/main/pages/"
GITHUB_API_URL = "https://api.github.com/repos/mmapro12/turkman"


def check_local_translation(command: str) -> bool:
    """Yerel Türkçe man sayfasını kontrol eder."""
    try:
        command_path = subprocess.run(["man", "-w", "-L", "tr", command], capture_output=True, text=True)
        if command_path.returncode == 0 and TRPATH in command_path.stdout.strip():
            result = subprocess.run(["man", "-L", "tr", command], stdin=subprocess.DEVNULL)
            return result.returncode == 0
    except Exception as e:
        typer.echo(f"Yerel çeviri kontrolünde hata: {e}", err=True)
    return False


def check_github_translation(command: str) -> str | None:
    """GitHub deposunda çeviri olup olmadığını kontrol eder."""
    try:
        url = f"{GITHUB_RAW_URL}{command}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        typer.echo(f"GitHub çeviri kontrolünde hata: {e}", err=True)
    return None


def check_db_translation(command: str) -> str | None:
    """Turkmandb'de çeviri olup olmadığını kontrol eder."""
    try:
        return turkmandb.get_translation(command)
    except Exception as e:
        typer.echo(f"Veritabanı çeviri kontrolünde hata: {e}", err=True)
    return None


def check_command(command: str) -> bool:
    """Man sayfasının olup olmadığını kontrol eder."""
    try:
        path = subprocess.run(["man", "-w", command], capture_output=True, text=True, timeout=10)
        if path.returncode != 0 or not path.stdout.strip():
            return False
        
        man_path = path.stdout.strip()
        
        if not os.path.exists(man_path):
            typer.echo(f"Man sayfası dosyası bulunamadı: {man_path}", err=True)
            return False
        
        if os.path.getsize(man_path) == 0:
            typer.echo(f"Man sayfası dosyası boş: {man_path}", err=True)
            return False
        
        test_result = subprocess.run(
            ["man", command], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            stdin=subprocess.DEVNULL,
            timeout=5
        )
        
        return test_result.returncode == 0 and len(test_result.stdout) > 0
        
    except subprocess.TimeoutExpired:
        typer.echo(f"Man komutu zaman aşımına uğradı: {command}", err=True)
        return False
    except Exception as e:
        typer.echo(f"Komut kontrolünde hata: {e}", err=True)
        return False


def safe_man_display(content: str, command: str) -> bool:
    """Man sayfasını güvenli bir şekilde gösterir."""
    try:
        import tempfile
        
        # Geçici dosya oluştur
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{command}.man', delete=False) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        os.chmod(temp_path, 0o644)
        result = subprocess.run(["man", temp_path], stdin=subprocess.DEVNULL)
        os.unlink(temp_path)

        return result.returncode == 0
        
    except Exception as e:
        typer.echo(f"Man sayfası gösteriminde hata: {e}", err=True)
        return False


def get_latest_release_info():
    """GitHub'dan en son sürüm bilgilerini alır."""
    try:
        response = requests.get(f"{GITHUB_API_URL}/releases/latest", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            typer.echo(f"❌ GitHub API'den sürüm bilgisi alınamadı: {response.status_code}", err=True)
            return None
    except Exception as e:
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


@app.command()
def uninstall(
    force: bool = typer.Option(False, "--force", "-f", help="Zorla kaldır, onay isteme"),
    keep_data: bool = typer.Option(False, "--keep-data", help="Kullanıcı verilerini sakla")
):
    """Turkman'ı sistemden kaldırır."""
    typer.echo("🗑️  Turkman Kaldırma İşlemi")
    typer.echo("=" * 40)
    
    # Kurulum türünü tespit et
    apt_installed = is_installed_via_apt()
    pip_installed = is_installed_via_pip()
    executable_path = get_turkman_executable_path()
    
    if not apt_installed and not pip_installed and not executable_path:
        typer.echo("❌ Turkman kurulu görünmüyor!")
        raise typer.Exit(code=1)
    
    # Kurulum bilgilerini göster
    typer.echo("📋 Kurulum Durumu:")
    if apt_installed:
        typer.echo("   • APT paketi: ✅ Kurulu")
    if pip_installed:
        typer.echo("   • Python paketi: ✅ Kurulu")
    if executable_path:
        typer.echo(f"   • Executable: {executable_path}")
    
    # Kullanıcı verilerini kontrol et
    home_dir = Path.home()
    turkmandb_path = home_dir / ".turkmandb"
    has_user_data = turkmandb_path.exists()
    
    if has_user_data:
        typer.echo(f"📁 Kullanıcı verileri: {turkmandb_path}")
        if not keep_data:
            typer.echo("⚠️  Kullanıcı verileri de silinecek!")
    
    # Onay al
    if not force:
        confirm = typer.confirm("Turkman'ı kaldırmak istediğinizden emin misiniz?")
        if not confirm:
            typer.echo("❌ İşlem iptal edildi.")
            raise typer.Exit(code=0)
    
    typer.echo("\n🔄 Kaldırma işlemi başlatılıyor...")
    
    if apt_installed:
        try:
            typer.echo("📦 APT paketi kaldırılıyor...")
            subprocess.run(["sudo", "apt", "remove", "-y", "turkman"], check=True)
            typer.echo("✅ APT paketi kaldırıldı!")
        except subprocess.CalledProcessError as e:
            typer.echo(f"❌ APT paketi kaldırma hatası: {e}", err=True)
        except Exception as e:
            typer.echo(f"❌ Beklenmeyen hata: {e}", err=True)
    
    # Python paketini kaldır
    if pip_installed:
        try:
            typer.echo("🐍 Python paketi kaldırılıyor...")
            subprocess.run(["pip", "uninstall", "-y", "turkman"], check=True)
            typer.echo("✅ Python paketi kaldırıldı!")
        except subprocess.CalledProcessError as e:
            typer.echo(f"❌ Python paketi kaldırma hatası: {e}", err=True)
        except Exception as e:
            typer.echo(f"❌ Beklenmeyen hata: {e}", err=True)
    
    # Manuel yükleme dosyalarını kaldır
    if executable_path and "/usr/local/bin" in executable_path:
        try:
            typer.echo("🗂️  Manuel yükleme dosyaları kaldırılıyor...")
            os.remove(executable_path)
            typer.echo("✅ Manuel yükleme dosyaları kaldırıldı!")
        except Exception as e:
            typer.echo(f"❌ Manuel dosya kaldırma hatası: {e}", err=True)
    
    # Kullanıcı verilerini kaldır
    if has_user_data and not keep_data:
        try:
            typer.echo("🗄️  Kullanıcı verileri kaldırılıyor...")
            shutil.rmtree(turkmandb_path)
            typer.echo("✅ Kullanıcı verileri kaldırıldı!")
        except Exception as e:
            typer.echo(f"❌ Kullanıcı verisi kaldırma hatası: {e}", err=True)
    elif has_user_data and keep_data:
        typer.echo(f"💾 Kullanıcı verileri korundu: {turkmandb_path}")
    
    typer.echo("\n🎉 Turkman başarıyla kaldırıldı!")
    if keep_data and has_user_data:
        typer.echo("💡 Verilerinizi tekrar kullanmak için Turkman'ı yeniden yükleyebilirsiniz.")


@app.command()
def update(
    force: bool = typer.Option(False, "--force", "-f", help="Zorla güncelle, sürüm kontrolü yapma"),
    check_only: bool = typer.Option(False, "--check", "-c", help="Sadece güncelleme kontrolü yap")
):
    """Turkman'ı günceller."""
    typer.echo("🔄 Turkman Güncelleme İşlemi")
    typer.echo("=" * 40)
    
    # Mevcut sürümü al
    current_version = utils.get_version()
    typer.echo(f"📋 Mevcut sürüm: {current_version}")
    
    # En son sürümü kontrol et
    typer.echo("🔍 En son sürüm kontrol ediliyor...")
    release_info = get_latest_release_info()
    
    if not release_info:
        typer.echo("❌ Sürüm bilgisi alınamadı. İnternet bağlantınızı kontrol edin.")
        raise typer.Exit(code=1)
    
    latest_version = release_info["tag_name"]
    typer.echo(f"🆕 En son sürüm: {latest_version}")
    
    # Sürüm karşılaştırması
    needs_update = compare_versions(current_version, latest_version)
    
    if not needs_update and not force:
        typer.echo("✅ Turkman zaten en son sürümde!")
        if check_only:
            raise typer.Exit(code=0)
        
        update_anyway = typer.confirm("Yine de güncelleme yapmak istiyor musunuz?")
        if not update_anyway:
            raise typer.Exit(code=0)
    
    if check_only:
        if needs_update:
            typer.echo("🔔 Güncelleme mevcut!")
            typer.echo(f"💡 Güncellemek için: turkman update")
        else:
            typer.echo("✅ Güncelleme gerekmiyor.")
        raise typer.Exit(code=0)
    
    # Güncelleme bilgilerini göster
    if needs_update or force:
        typer.echo("\n📄 Sürüm Notları:")
        body = release_info.get("body", "Sürüm notları mevcut değil.")
        # Markdown'ı basit metne çevir
        clean_body = re.sub(r'[#*`]', '', body)
        typer.echo(clean_body[:500] + "..." if len(clean_body) > 500 else clean_body)
    
    # Kurulum türünü tespit et
    apt_installed = is_installed_via_apt()
    pip_installed = is_installed_via_pip()
    
    # Onay al
    if not force:
        confirm = typer.confirm(f"\n{latest_version} sürümüne güncellemek istiyor musunuz?")
        if not confirm:
            typer.echo("❌ Güncelleme iptal edildi.")
            raise typer.Exit(code=0)
    
    typer.echo("\n🚀 Güncelleme başlatılıyor...")
    
    # APT ile güncelleme
    if apt_installed:
        try:
            typer.echo("📦 APT ile güncelleme yapılıyor...")
            
            # .deb dosyasını bul
            deb_asset = None
            for asset in release_info.get("assets", []):
                if asset["name"].endswith(".deb"):
                    deb_asset = asset
                    break
            
            if not deb_asset:
                typer.echo("❌ .deb dosyası bulunamadı!", err=True)
                raise typer.Exit(code=1)
            
            # Geçici dizin oluştur
            with tempfile.TemporaryDirectory() as temp_dir:
                deb_path = os.path.join(temp_dir, deb_asset["name"])
                
                # .deb dosyasını indir
                if not download_file(deb_asset["browser_download_url"], deb_path):
                    raise typer.Exit(code=1)
                
                # Paketi yükle
                typer.echo("📦 Paket yükleniyor...")
                subprocess.run(["sudo", "dpkg", "-i", deb_path], check=True)
                subprocess.run(["sudo", "apt", "install", "-f", "-y"], check=True)
                
                typer.echo("✅ APT güncelleme tamamlandı!")
        
        except subprocess.CalledProcessError as e:
            typer.echo(f"❌ APT güncelleme hatası: {e}", err=True)
            raise typer.Exit(code=1)
        except Exception as e:
            typer.echo(f"❌ Beklenmeyen hata: {e}", err=True)
            raise typer.Exit(code=1)
    
    # Python paketi ile güncelleme
    elif pip_installed:
        try:
            typer.echo("🐍 Python paketi güncelleniyor...")
            subprocess.run(["pip", "install", "--upgrade", "turkman"], check=True)
            typer.echo("✅ Python paketi güncelleme tamamlandı!")
        except subprocess.CalledProcessError as e:
            typer.echo(f"❌ Python paketi güncelleme hatası: {e}", err=True)
            raise typer.Exit(code=1)
        except Exception as e:
            typer.echo(f"❌ Beklenmeyen hata: {e}", err=True)
            raise typer.Exit(code=1)
    
    # Manuel kurulum güncelleme
    else:
        try:
            typer.echo("🔧 Manuel güncelleme yapılıyor...")
            typer.echo("💡 En iyi deneyim için APT ile yeniden kurulum önerilir:")
            typer.echo("   wget -qO- https://github.com/mmapro12/turkman/releases/latest/download/turkman_0.6.3_all.deb | sudo dpkg -i -")
            
            # Script ile güncelleme seçeneği sun
            script_update = typer.confirm("Script ile güncelleme yapmak ister misiniz?")
            if script_update:
                # Install script'i çalıştır
                install_script_url = "https://raw.githubusercontent.com/mmapro12/turkman/main/install.sh"
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    script_path = os.path.join(temp_dir, "install.sh")
                    
                    if download_file(install_script_url, script_path):
                        os.chmod(script_path, 0o755)
                        subprocess.run([script_path], check=True)
                        typer.echo("✅ Script güncelleme tamamlandı!")
                    else:
                        raise Exception("Install script indirilemedi")
            else:
                typer.echo("💡 Manuel güncelleme için:")
                typer.echo("   git clone https://github.com/mmapro12/turkman.git")
                typer.echo("   cd turkman && ./install.sh")
        
        except Exception as e:
            typer.echo(f"❌ Manuel güncelleme hatası: {e}", err=True)
            raise typer.Exit(code=1)
    
    # Veritabanını güncelle
    try:
        typer.echo("🗄️  Veritabanı güncelleniyor...")
        turkmandb.get_turkmandb()
        typer.echo("✅ Veritabanı güncellendi!")
    except Exception as e:
        typer.echo(f"⚠️  Veritabanı güncelleme hatası: {e}", err=True)
        typer.echo("💡 'turkman db sync' komutunu daha sonra çalıştırabilirsiniz.")
    
    # Güncelleme sonrası doğrulama
    try:
        new_version = utils.get_version()
        typer.echo(f"\n🎉 Güncelleme tamamlandı!")
        typer.echo(f"📋 Eski sürüm: {current_version}")
        typer.echo(f"📋 Yeni sürüm: {new_version}")
        
        if new_version != current_version:
            typer.echo("✅ Sürüm başarıyla güncellendi!")
        else:
            typer.echo("⚠️  Sürüm numarası değişmedi, kontrol edin.")
    
    except Exception as e:
        typer.echo(f"❌ Sürüm doğrulama hatası: {e}", err=True)


@app.command()
def version():
    """Turkman sürümünü gösterir."""
    typer.echo(f"Turkman CLI {utils.get_version()}")
    typer.echo(f"En yeni sürüm: {utils.get_latest_version()}")


@app.command()
def manpage(command: str):
    """Belirtilen komut için Türkçe man sayfasını gösterir."""
    # Önce yerel çeviriyi kontrol et
    if check_local_translation(command):
        return
    
    # Sonra veritabanını kontrol et
    db_translation = check_db_translation(command)
    if db_translation:
        typer.echo(f"📖 '{command}' için Türkçe man sayfası gösteriliyor (veritabanından)...")
        if safe_man_display(db_translation, command):
            return
        else:
            typer.echo("Man sayfası gösteriminde sorun oluştu.", err=True)
            return
    
    # GitHub'dan kontrol et (yedek olarak)
    github_translation = check_github_translation(command)
    if github_translation:
        typer.echo(f"📖 '{command}' için Türkçe man sayfası gösteriliyor (GitHub'dan)...")
        if safe_man_display(github_translation, command):
            return
        else:
            typer.echo("Man sayfası gösteriminde sorun oluştu, ham içerik gösteriliyor:", err=True)
            typer.echo(github_translation)
            return

    typer.echo(f"❌ '{command}' için Türkçe çeviri bulunamadı.", err=True)
    typer.echo(f"💡 Orijinal İngilizce man sayfasını görmek için: man {command}")


@db_app.command()
def sync():
    """Turkmandb'nin en yeni sürümünü getirir."""
    try:
        turkmandb.init_db()
        typer.echo("🔄 Veritabanı senkronize ediliyor...")
        turkmandb.get_turkmandb()
        typer.echo("✅ Veritabanı senkronizasyonu tamamlandı!")
    except Exception as e:
        typer.echo(f"❌ Veritabanı senkronizasyonunda hata: {e}", err=True)


@db_app.command()
def init():
    """Turkmandb'yi .turkmandb dizini altında oluşturur."""
    try:
        turkmandb.init_db()
        typer.echo("✅ Veritabanı başlatıldı!")
    except Exception as e:
        typer.echo(f"❌ Veritabanı başlatmada hata: {e}", err=True)


def handle_man_command(command: str):
    """Man sayfası komutunu işler."""
    typer.echo(f"🔍 '{command}' komutu araştırılıyor...")
    
    if check_command(command):
        manpage(command)
    else:
        typer.echo(f"❌ '{command}' adında bir komut bulunamadı veya man sayfası okunamıyor.", err=True)
        
        try:
            result = subprocess.run(["man", "-w", command], capture_output=True, text=True)
            if result.returncode == 0:
                typer.echo(f"🔧 Debug: Man sayfası yolu bulundu ama okunamıyor: {result.stdout.strip()}")
            else:
                typer.echo(f"🔧 Debug: Man sayfası yolu bulunamadı")
        except Exception as e:
            typer.echo(f"🔧 Debug: Komut kontrolünde hata: {e}")
        
        typer.echo(f"💡 Alternatif çözümler:")
        typer.echo(f"   • Orijinal man sayfasını deneyin: man {command}")
        typer.echo(f"   • Komut doğru yazıldı mı kontrol edin")
        typer.echo(f"   • Man sayfaları güncel mi kontrol edin: sudo mandb")
        
        raise typer.Exit(code=1)


def main():
    """Ana akış."""
    try:
        if len(sys.argv) > 1:
            utils.check_updates(sys.argv[1])
        
        if len(sys.argv) > 1:
            first_arg = sys.argv[1]
            if first_arg in TURKMAN_COMMANDS:
                app()
            else:
                handle_man_command(first_arg)
        else:
            app()
    except KeyboardInterrupt:
        typer.echo("\n🚫 İşlem kullanıcı tarafından iptal edildi.")
        sys.exit(1)
    except Exception as e:
        typer.echo(f"❌ Beklenmeyen hata: {e}", err=True)
        sys.exit(1)


app.add_typer(db_app, name="db")

if __name__ == "__main__":
    main()
