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

TURKMAN_COMMANDS = ["db", "update", "uninstall", "version"]
INSTALL_PATH = "/opt/turkman"
TRPATH = "/usr/share/man/tr/"
GITHUB_REPO = "mmapro12/turkmandb"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/refs/heads/main/pages/"


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


def check_db_translation(command: str) -> str | None:
    """Turkmandb'de çeviri olup olmadığını kontrol eder."""
    return turkmandb.get_translation(command) 


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
    # github_translation = check_github_translation(command)
    # if github_translation:
    #     buffer_path = f"/tmp/{command}.man"
    #     with open(buffer_path, "w") as file:
    #         file.write(github_translation)
    #     subprocess.run(["man", buffer_path])
    #     return

    db_translation = check_db_translation(command)
    if db_translation:
        buffer_path = f"/tmp/{command}.man"
        with open(buffer_path, "w") as file:
            file.write(db_translation)
        subprocess.run(["man", buffer_path])
        return

    typer.echo(f"'{command}' için çeviri bulunamadı.", err=True)


@db_app.command()
def sync():
    """Turkmandb'nin en yeni sürümünü getirir."""
    turkmandb.init_db()
    turkmandb.get_turkmandb()


@db_app.command()
def init():
    """Turkmandb'yi .turkmandb dizini altında oluşturur."""
    turkmandb.init_db()


@app.command()
def main(command: str):
    """Gelen komuta göre man sayfasını veya ilgili işlemi çalıştırır."""
    if check_command(command):
        manpage(command)
    else:
        typer.echo(f"'{command}' adında bir komut bulunamadı.", err=True)
        raise typer.Exit(code=1)


def handle_man_command(command: str):
    """Man sayfası komutunu işler."""
    if check_command(command):
        manpage(command)
    else:
        typer.echo(f"'{command}' adında bir komut bulunamadı.", err=True)
        raise typer.Exit(code=1)


app.add_typer(db_app, name="db")
if __name__ == "__main__":
    check_updates(sys.argv[1])
    if len(sys.argv) > 1:
        first_arg = sys.argv[1]
        if first_arg in TURKMAN_COMMANDS:
            app()
        else:
            handle_man_command(first_arg)
    else:
        app()
