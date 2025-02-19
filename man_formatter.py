import subprocess
import re
import sys
from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.text import Text

console = Console()

def get_man_page(command):
    """Belirtilen komutun man sayfasını alır ve temizler."""
    try:
        result = subprocess.run(
            ["man", command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.stderr:
            console.print(f"[red]Hata:[/red] {result.stderr.strip()}")
            sys.exit(1)
        return result.stdout
    except Exception as e:
        console.print(f"[red]Bir hata oluştu:[/red] {e}")
        sys.exit(1)

def format_man_page(text):
    """Man sayfasını Rich kullanarak renklendirir ve biçimlendirir."""

    # SECTION başlıklarını renklendir
    text = re.sub(r"(^[A-Z ]+\n)", r"[bold cyan]\1[/bold cyan]", text, flags=re.MULTILINE)

    # Seçenekleri (örneğin: `-l, --long`) renklendir
    text = re.sub(r"(\n\s+-[a-zA-Z0-9, |]+)", r"[bold yellow]\1[/bold yellow]", text)

    # Kod bloklarını vurgula (örneğin: `ls -l`)
    text = re.sub(r"`([^`]+)`", r"[bold green]\1[/bold green]", text)

    return Markdown(text)

def main():
    """Komut satırından argüman alarak man sayfasını gösterir."""
    if len(sys.argv) < 2:
        console.print("[red]Kullanım:[/red] python man_formatter.py <komut>")
        sys.exit(1)

    command = sys.argv[1]
    man_page = get_man_page(command)

    if man_page:
        formatted_text = format_man_page(man_page)
        console.print(formatted_text)

if __name__ == "__main__":
    main()

