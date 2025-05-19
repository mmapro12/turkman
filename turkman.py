#!/usr/bin/env python3

import os
import requests
import subprocess
import typer
import turkmandb


turkmandb.init_db()
app = typer.Typer()

INSTALL_PATH = "/opt/turkman"
TRPATH = "/usr/share/man/tr/"
GITHUB_REPO = "mmapro12/turkmandb"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/refs/heads/main/pages/"


def get_version():
    """Turkman versiyonunu getirir."""
    with open(f"{INSTALL_PATH}/version.txt") as file:
        return file.readline()


def get_last_version():
    """Turkman'ın e güncel sürümünü getirir."""
    response = requests.get("https://raw.githubusercontent.com/mmapro12/turkman/refs/heads/main/version.txt")
    if response.status_code == 200:
        return response.text 
    return False


def check_local_translation(command: str) -> bool:
    """Yerel Türkçe man sayfasını kontrol eder."""
    command_path = subprocess.run(["man", "-w", "-L", "tr", command], capture_output=True, text=True)
    if TRPATH in command_path.stdout.strip():
        result = subprocess.run(["man", "-L", "tr", command])
        return result.returncode == 0
    return False


def check_github_translation(command: str) -> str | None:
    """GitHub deposunda çeviri olup olmadığını kontrol eder."""
    url = f"{GITHUB_RAW_URL}{command}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    return None


def check_command(command: str) -> bool:
    """Man sayfasının olup olmadığını kontrol eder."""
    path = subprocess.run(["man", "-w", command], capture_output=True, text=True)
    return bool(path.stdout.strip()) and os.path.exists(path.stdout.strip())


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
    typer.echo(f"Lastest version {get_last_version()}")


@app.command()
def manpage(command: str):
    """Belirtilen komut için Türkçe man sayfasını gösterir."""
    if check_local_translation(command):
        return
    github_translation = check_github_translation(command)
    if github_translation:
        buffer_path = f"/tmp/{command}.man"
        with open(buffer_path, "w") as file:
            file.write(github_translation)
        subprocess.run(["man", buffer_path])
        return
    typer.echo(f"'{command}' için çeviri bulunamadı.", err=True)


@app.command()
def db(command: str):
    """Turkmandb ile işlem yapmanızı sağlar."""
    if command == "update":
        turkmandb.init_db()
        turkmandb.get_turkmandb()
    elif command == "init":
        turkmandb.init_db()
    elif command == "test":
        print(turkmandb.get_translation("ani-cli"))
    else:
        typer.echo("turkmandb: yanlış kullanım.")


@app.command()
def main(command: str):
    """Gelen komuta göre man sayfasını veya ilgili işlemi çalıştırır."""
    if check_command(command):
        manpage(command)
    else:
        typer.echo(f"'{command}' adında bir komut bulunamadı.", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    v = get_version()
    lv = get_last_version()
    if v != lv:
        typer.echo(f"{v} -> {lv}")
        typer.echo("Turkman'ın yeni sürümü mevcut.Güncellemek için:\t$ turkman update")

    app()


