#!/usr/bin/env python3

import sys
import os
import requests
import subprocess
import typer
import turkmandb
from common import *


turkmandb.init_db()
app = typer.Typer()
db_app = typer.Typer()

TURKMAN_COMMANDS = ["db", "update", "uninstall", "version", "--help", "manpage"]
INSTALL_PATH = "/opt/turkman"
TRPATH = "/usr/share/man/tr/"
GITHUB_REPO = "mmapro12/turkmandb"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/refs/heads/main/pages/"


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
        # Önce man -w ile yolu kontrol et
        path = subprocess.run(["man", "-w", command], capture_output=True, text=True, timeout=10)
        if path.returncode != 0 or not path.stdout.strip():
            return False
        
        man_path = path.stdout.strip()
        
        # Dosyanın var olup olmadığını kontrol et
        if not os.path.exists(man_path):
            typer.echo(f"Man sayfası dosyası bulunamadı: {man_path}", err=True)
            return False
        
        # Dosyanın boş olmadığını kontrol et
        if os.path.getsize(man_path) == 0:
            typer.echo(f"Man sayfası dosyası boş: {man_path}", err=True)
            return False
        
        # Man komutunun gerçekten çalışıp çalışmadığını test et
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
        
        # Dosya izinlerini ayarla
        os.chmod(temp_path, 0o644)
        
        # Man komutu ile göster
        result = subprocess.run(["man", temp_path], stdin=subprocess.DEVNULL)
        
        # Geçici dosyayı temizle
        try:
            os.unlink(temp_path)
        except:
            pass
            
        return result.returncode == 0
        
    except Exception as e:
        typer.echo(f"Man sayfası gösteriminde hata: {e}", err=True)
        return False


@app.command()
def uninstall():
    """Turkman'ı sistemden kaldırır."""
    script_path = os.path.join(INSTALL_PATH, "scripts", "uninstall.sh")
    if os.path.exists(script_path):
        subprocess.run(["sudo", script_path], check=True)
    else:
        typer.echo("Hata: uninstall.sh bulunamadı!", err=True)


@app.command()
def update():
    """Turkman'ı günceller."""
    script_path = os.path.join(INSTALL_PATH, "scripts", "update.sh")
    if os.path.exists(script_path):
        subprocess.run(["sudo", script_path], check=True)
    else:
        typer.echo("Hata: update.sh bulunamadı!", err=True)


@app.command()
def version():
    """Turkman sürümünü gösterir."""
    typer.echo(f"Turkman CLI {get_version()}")
    typer.echo(f"En yeni sürüm: {get_last_version()}")


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
            typer.echo("Man sayfası gösteriminde sorun oluştu, ham içerik gösteriliyor:", err=True)
            typer.echo(db_translation)
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


@app.command()
def main(command: str):
    """Gelen komuta göre man sayfasını veya ilgili işlemi çalıştırır."""
    if check_command(command):
        manpage(command)
    else:
        typer.echo(f"❌ '{command}' adında bir komut bulunamadı veya man sayfası okunamıyor.", err=True)
        typer.echo(f"💡 Komutun doğru yazıldığından emin olun: {command}")
        typer.echo(f"💡 Alternatif olarak orijinal man sayfasını deneyin: man {command}")
        raise typer.Exit(code=1)


def handle_man_command(command: str):
    """Man sayfası komutunu işler."""
    typer.echo(f"🔍 '{command}' komutu araştırılıyor...")
    
    if check_command(command):
        manpage(command)
    else:
        typer.echo(f"❌ '{command}' adında bir komut bulunamadı veya man sayfası okunamıyor.", err=True)
        
        # Debug bilgileri göster
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


app.add_typer(db_app, name="db")

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1:
            check_updates(sys.argv[1])
        
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
