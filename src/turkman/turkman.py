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
from rich.console import Console

console = Console()
turkmandb.init_db()
app = typer.Typer()
db_app = typer.Typer()
test_app = typer.Typer()

TURKMAN_COMMANDS = ["db", "update", "uninstall", "version", "--help", "manpage", "test"]
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
        typer.echo(f"Yerel çeviri kontrolünde hata: {e}")
    return False


def check_github_translation(command: str) -> str | None:
    """GitHub deposunda çeviri olup olmadığını kontrol eder."""
    try:
        url = f"{GITHUB_RAW_URL}{command}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        typer.echo(f"GitHub çeviri kontrolünde hata: {e}")
    return None


def check_db_translation(command: str) -> str | None:
    """Turkmandb'de çeviri olup olmadığını kontrol eder."""
    try:
        return turkmandb.get_translation(command)
    except Exception as e:
        typer.echo(f"Veritabanı çeviri kontrolünde hata: {e}")
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


@app.command()
def uninstall(
    force: bool = typer.Option(False, "--force", "-f", help="Zorla kaldır, onay isteme"),
    keep_data: bool = typer.Option(False, "--keep-data", help="Kullanıcı verilerini sakla")
):
    """Turkman'ı sistemden kaldırır."""
    console.print("🗑️  Turkman Kaldırma İşlemi")
    console.print("=" * 40)
    
    # Kurulum türünü tespit et
    apt_installed = utils.is_installed_via_apt()
    pip_installed = utils.is_installed_via_pip()
    executable_path = utils.get_turkman_executable_path()
    
    if not apt_installed and not pip_installed and not executable_path:
        typer.echo("❌ Turkman kurulu görünmüyor!")
        raise typer.Exit(code=1)
    
    # Kurulum bilgilerini göster
    console.print("📋 Kurulum Durumu:")
    if apt_installed:
        console.print("   • APT paketi: ✅ Kurulu")
    if pip_installed:
        console.print("   • Python paketi: ✅ Kurulu")
    if executable_path:
        console.print(f"   • Executable: {executable_path}")
    
    # Kullanıcı verilerini kontrol et
    home_dir = Path.home()
    turkmandb_path = home_dir / ".turkmandb"
    has_user_data = turkmandb_path.exists()
    
    if has_user_data:
        console.print(f"📁 Kullanıcı verileri: {turkmandb_path}")
        if not keep_data:
            console.print("⚠️  Kullanıcı verileri de silinecek!")
    
    # Onay al
    if not force:
        confirm = typer.confirm("Turkman'ı kaldırmak istediğinizden emin misiniz?")
        if not confirm:
            console.print("❌ İşlem iptal edildi.")
            raise typer.Exit(code=0)
    
    console.print("\n🔄 Kaldırma işlemi başlatılıyor...")
    
    if apt_installed:
        try:
            console.print("📦 APT paketi kaldırılıyor...")
            subprocess.run(["sudo", "apt", "remove", "-y", "turkman"], check=True)
            console.print("✅ APT paketi kaldırıldı!")
        except subprocess.CalledProcessError as e:
            console.print(f"❌ APT paketi kaldırma hatası: {e}")
        except Exception as e:
            console.print(f"❌ Beklenmeyen hata: {e}")
    
    if pip_installed:
        try:
            console.print("🐍 Python paketi kaldırılıyor...")
            subprocess.run(["pip", "uninstall", "-y", "turkman"], check=True)
            console.print("✅ Python paketi kaldırıldı!")
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Python paketi kaldırma hatası: {e}")
        except Exception as e:
            console.print(f"❌ Beklenmeyen hata: {e}")
    
    # Manuel yükleme dosyalarını kaldır
    if executable_path and "/usr/local/bin" in executable_path:
        try:
            console.print("🗂️  Manuel yükleme dosyaları kaldırılıyor...")
            os.remove(executable_path)
            console.print("✅ Manuel yükleme dosyaları kaldırıldı!")
        except Exception as e:
            console.print(f"❌ Manuel dosya kaldırma hatası: {e}")
    
    # Kullanıcı verilerini kaldır
    if has_user_data and not keep_data:
        try:
            console.print("🗄️  Kullanıcı verileri kaldırılıyor...")
            shutil.rmtree(turkmandb_path)
            console.print("✅ Kullanıcı verileri kaldırıldı!")
        except Exception as e:
            console.print(f"❌ Kullanıcı verisi kaldırma hatası: {e}")
    elif has_user_data and keep_data:
        console.print(f"💾 Kullanıcı verileri korundu: {turkmandb_path}")
    
    console.print("\n🎉 Turkman başarıyla kaldırıldı!")
    if keep_data and has_user_data:
        console.print("💡 Verilerinizi tekrar kullanmak için Turkman'ı yeniden yükleyebilirsiniz.")


@app.command()
def update(
    force: bool = typer.Option(False, "--force", "-f", help="Zorla güncelle, sürüm kontrolü yapma"),
    check_only: bool = typer.Option(False, "--check", "-c", help="Sadece güncelleme kontrolü yap")
):
    """Turkman'ı günceller."""
    console.print("🔄 Turkman Güncelleme İşlemi")
    console.print("=" * 40)
    
    # Mevcut sürümü al
    current_version = utils.get_version()
    console.print(f"📋 Mevcut sürüm: {current_version}")
    
    # En son sürümü kontrol et
    console.print("🔍 en son sürüm kontrol ediliyor...")
    release_info = utils.get_latest_release_info()
    
    if not release_info:
        console.print("❌ Sürüm bilgisi alınamadı. İnternet bağlantınızı kontrol edin.")
        raise typer.Exit(code=1)
    
    latest_version = release_info["tag_name"]
    console.print(f"🆕 En son sürüm: {latest_version}")
    
    # Sürüm karşılaştırması
    needs_update = utils.compare_versions(current_version, latest_version)
    
    if not needs_update and not force:
        console.print("✅ Turkman zaten en son sürümde!")
        if check_only:
            raise typer.Exit(code=0)
        
        update_anyway = typer.confirm("Yine de güncelleme yapmak istiyor musunuz?")
        if not update_anyway:
            raise typer.Exit(code=0)
    
    if check_only:
        if needs_update:
            console.print("🔔 Güncelleme mevcut!")
            console.print("💡 Güncellemek için: turkman update")
        else:
            console.print("✅ Güncelleme gerekmiyor.")
        raise typer.Exit(code=0)
    
    # Güncelleme bilgilerini göster
    if needs_update or force:
        console.print("\n📄 Sürüm Notları:")
        body = release_info.get("body", "Sürüm notları mevcut değil.")
        # Markdown'ı basit metne çevir
        clean_body = re.sub(r'[#*`]', '', body)
        console.print(clean_body[:500] + "..." if len(clean_body) > 500 else clean_body)
    
    # Kurulum türünü tespit et
    apt_installed = utils.is_installed_via_apt()
    pip_installed = utils.is_installed_via_pip()
    
    # Onay al
    if not force:
        confirm = typer.confirm(f"\n{latest_version} sürümüne güncellemek istiyor musunuz?")
        if not confirm:
            console.print("❌ Güncelleme iptal edildi.")
            raise typer.Exit(code=0)
    
    console.print("\n🚀 Güncelleme başlatılıyor...")
    
    # APT ile güncelleme
    if apt_installed:
        try:
            console.print("📦 APT ile güncelleme yapılıyor...")
            
            # .deb dosyasını bul
            deb_asset = None
            for asset in release_info.get("assets", []):
                if asset["name"].endswith(".deb"):
                    deb_asset = asset
                    break
            
            if not deb_asset:
                console.print("❌ .deb dosyası bulunamadı!")
                raise typer.Exit(code=1)
            
            # Geçici dizin oluştur
            with tempfile.TemporaryDirectory() as temp_dir:
                deb_path = os.path.join(temp_dir, deb_asset["name"])
                
                # .deb dosyasını indir
                if not utils.download_file(deb_asset["browser_download_url"], deb_path):
                    raise typer.Exit(code=1)
                
                # Paketi yükle
                console.print("📦 Paket yükleniyor...")
                subprocess.run(["sudo", "dpkg", "-i", deb_path], check=True)
                subprocess.run(["sudo", "apt", "install", "-f", "-y"], check=True)
                
                console.print("✅ APT güncelleme tamamlandı!")
        
        except subprocess.CalledProcessError as e:
            console.print(f"❌ APT güncelleme hatası: {e}")
            raise typer.Exit(code=1)
        except Exception as e:
            console.print(f"❌ Beklenmeyen hata: {e}")
            raise typer.Exit(code=1)
    
    # Python paketi ile güncelleme
    elif pip_installed:
        try:
            console.print("🐍 Python paketi güncelleniyor...")
            subprocess.run(["pip", "install", "--upgrade", "turkman"], check=True)
            console.print("✅ Python paketi güncelleme tamamlandı!")
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Python paketi güncelleme hatası: {e}")
            raise typer.Exit(code=1)
        except Exception as e:
            console.print(f"❌ Beklenmeyen hata: {e}")
            raise typer.Exit(code=1)
    
    else:
        try:
            console.print("🔧 Manuel güncelleme yapılıyor...")
            install_script = """
            git clone https://github.com/mmapro12/turkman.git /tmp/turkman/
            cd /tmp/turkman/ && ./install.sh
            rm -rf /tmp/turkman/
            """
            subprocess.run(install_script, shell=True, check=True)
            console.print("✅ Script güncelleme tamamlandı!")
        
        except Exception as e:
            console.print(f"❌ Manuel güncelleme hatası: {e}")
            raise typer.Exit(code=1)
    
    # Veritabanını güncelle
    try:
        console.print("🗄️  Veritabanı güncelleniyor...")
        turkmandb.get_turkmandb()
        console.print("✅ Veritabanı güncellendi!")
    except Exception as e:
        console.print(f"⚠️  Veritabanı güncelleme hatası: {e}")
        console.print("💡 'turkman db sync' komutunu daha sonra çalıştırabilirsiniz.")
    
    # Güncelleme sonrası doğrulama
    try:
        new_version = utils.get_version()
        console.print("\n🎉 Güncelleme tamamlandı!")
        console.print(f"📋 Eski sürüm: {current_version}")
        console.print(f"📋 Yeni sürüm: {new_version}")
        
        if new_version != current_version:
            console.print("✅ Sürüm başarıyla güncellendi!")
        else:
            console.print("⚠️  Sürüm numarası değişmedi, kontrol edin.")
    
    except Exception as e:
        console.print(f"❌ Sürüm doğrulama hatası: {e}")


@app.command()
def version():
    """Turkman sürümünü gösterir."""
    console.print(f"Turkman CLI {utils.get_version()}")
    console.print(f"En yeni sürüm: {utils.get_latest_version()}")


@app.command()
def manpage(command: str):
    """Belirtilen komut için Türkçe man sayfasını gösterir."""
    # Önce yerel çeviriyi kontrol et
    if check_local_translation(command):
        return
    
    # Sonra veritabanını kontrol et
    db_translation = check_db_translation(command)
    if db_translation:
        console.print(f"📖 '{command}' için Türkçe man sayfası gösteriliyor (veritabanından)...")
        if safe_man_display(db_translation, command):
            return
        else:
            console.print("Man sayfası gösteriminde sorun oluştu.")
            return
    
    # GitHub'dan kontrol et (yedek olarak)
    github_translation = check_github_translation(command)
    if github_translation:
        console.print(f"📖 '{command}' için Türkçe man sayfası gösteriliyor (GitHub'dan)...")
        if safe_man_display(github_translation, command):
            return
        else:
            console.print("Man sayfası gösteriminde sorun oluştu, ham içerik gösteriliyor:")
            console.print(github_translation)
            return

    console.print(f"❌ '{command}' için Türkçe çeviri bulunamadı.")
    console.print(f"💡 Orijinal İngilizce man sayfasını görmek için: man {command}")


@db_app.command()
def sync():
    """Turkmandb'nin en yeni sürümünü getirir."""
    try:
        turkmandb.init_db()
        console.print("🔄 Veritabanı senkronize ediliyor...")
        turkmandb.get_turkmandb()
        console.print("✅ Veritabanı senkronizasyonu tamamlandı!")
    except Exception as e:
        console.print(f"❌ Veritabanı senkronizasyonunda hata: {e}")


@db_app.command()
def init():
    """Turkmandb'yi .turkmandb dizini altında oluşturur."""
    try:
        turkmandb.init_db()
        console.print("✅ Veritabanı başlatıldı!")
    except Exception as e:
        console.print(f"❌ Veritabanı başlatmada hata: {e}")


@test_app.command()
def push():
    """Bu bir test komutudur."""
    typer.echo("Merhaba ertu kardeş.")


def handle_man_command(command: str):
    """Man sayfası komutunu işler."""
    console.print(f"🔍 '{command}' komutu araştırılıyor...")
    
    if check_command(command):
        manpage(command)
    else:
        console.print(f"❌ '{command}' adında bir komut bulunamadı veya man sayfası okunamıyor.")
        
        try:
            result = subprocess.run(["man", "-w", command], capture_output=True, text=True)
            if result.returncode == 0:
                console.print(f"🔧 Debug: Man sayfası yolu bulundu ama okunamıyor: {result.stdout.strip()}")
            else:
                console.print(f"🔧 Debug: Man sayfası yolu bulunamadı")
        except Exception as e:
            console.print(f"🔧 Debug: Komut kontrolünde hata: {e}")
        
        console.print(f"💡 Alternatif çözümler:")
        console.print(f"   • Orijinal man sayfasını deneyin: man {command}")
        console.print(f"   • Komut doğru yazıldı mı kontrol edin")
        console.print(f"   • Man sayfaları güncel mi kontrol edin: sudo mandb")
        
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
        console.print("\n🚫 İşlem kullanıcı tarafından iptal edildi.")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ Beklenmeyen hata: {e}")
        sys.exit(1)


app.add_typer(db_app, name="db")
app.add_typer(test_app, name="test")

if __name__ == "__main__":
    main()


