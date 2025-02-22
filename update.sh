#!/bin/bash

INSTALL_DIR="/opt/turkman"
BIN_PATH="/usr/local/bin/turkman"
MAN_PATH="/usr/local/share/man/man1/turkman.1.gz"

echo "🔄 Güncelleme başlatılıyor..."

if [[ $EUID -ne 0 ]]; then
   echo "❌ Lütfen root olarak çalıştırın: sudo ./update.sh"
   exit 1
fi

if [ -d "$INSTALL_DIR" ]; then
    cd "$INSTALL_DIR" || exit
    echo "📥 Güncellemeler kontrol ediliyor..."
    git pull origin main
else
    echo "❌Turkman bulunamadı! Önce 'sudo ./install.sh' ile yükleyin."
    exit 1
fi

find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

if [[ -f "$INSTALL_DIR/docs/man/man1/turkman.1" ]]; then
    gzip -c "$INSTALL_DIR/docs/man/man1/turkman.1" > "$MAN_PATH"
    echo "📖 Man sayfası güncellendi!"
fi
mandb

echo "✅ Güncelleme tamamlandı!"
echo "🔹 Kullanmak için: turkman <komut>"
echo "🔹 Yardım için: turkman -h"

