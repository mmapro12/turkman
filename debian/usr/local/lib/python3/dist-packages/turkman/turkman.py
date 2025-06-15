#!/usr/bin/env python3

import sys
import os
import requests
import subprocess
import typer
import turkman.db as turkmandb
import turkman.utils as utils

turkmandb.init_db()
app = typer.Typer()
db_app = typer.Typer()

TURKMAN_COMMANDS = ["db", "update", "uninstall", "version", "--help", "manpage"]
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
def uninstall():
    """Turkman'ı sistemden kaldırır."""
    subprocess.run(["sudo", "apt", "remove", "turkman"], check=True)


@app.command()
def update():
    """Turkman'ı günceller."""
    pass


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


