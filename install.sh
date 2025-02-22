#!/bin/bash

INSTALL_DIR="/opt/turkman"
BIN_PATH="/usr/local/bin/turkman"
MAN_PATH="/usr/local/share/man/man1/turkman.1.gz"

echo "🔧 Turkman indiriliyor..."

if [[ $EUID -ne 0 ]]; then
   echo "❌ Lütfen root olarak çalıştırın: sudo ./install.sh"
   exit 1
fi

if ! dpkg -s manpages-tr &>/dev/null; then
    echo "📦 'manpages-tr' paketi eksik. Yükleniyor..."
    sudo apt update && sudo apt install -y manpages-tr
else
    echo "✅ 'manpages-tr' zaten yüklü."
fi

if command -v python3 &>/dev/null; then
    echo "🐍 Python 3 bulundu. Gerekli paketler yükleniyor..."
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt
else
    echo "❌ Python 3 yüklü değil! Lütfen önce Python 3 yükleyin."
    exit 1
fi

echo "📂 Uygulama '$INSTALL_DIR' dizinine kopyalanıyor..."
mkdir -p "$INSTALL_DIR"
cp -r * "$INSTALL_DIR"


chmod +x "$INSTALL_DIR/turkman.py"
ln -sf "$INSTALL_DIR/turkman.py" "$BIN_PATH"


if [[ -f "$INSTALL_DIR/docs/man/man1/turkman.1" ]]; then
    gzip -c "$INSTALL_DIR/docs/man/man1/turkman.1" > "$MAN_PATH"
    echo "📖 Man sayfası başarıyla eklendi!"
else
    echo "⚠️ Uyarı: Man sayfası bulunamadı!"
fi
mandb

echo "✅ Turkman başarıyla kuruldu!"
echo "🔹 Kullanmak için: turkman <komut>"
echo "🔹 Yardım için: turkman -h"

