#!/bin/bash

INSTALL_DIR="/opt/turkman"
BIN_PATH="/usr/local/bin/turkman"
MAN_PATH="/usr/local/share/man/man1/turkman.1"

echo "⚠️ Turkman kaldırılacak. Emin misiniz? (y/n)"
read -r response
response=$(echo "$response" | tr '[:upper:]' '[:lower:]') 
if [[ "$response" != "y" && "$response" != "yes" ]]; then
    echo "❌ İşlem iptal edildi."
    exit 0
fi

if [[ $EUID -ne 0 ]]; then
   echo "❌ Lütfen root olarak çalıştırın: sudo ./uninstall.sh"
   exit 1
fi

if [ -d "$INSTALL_DIR" ]; then
    echo "🗑️ Turkman kaldırılıyor..."
    rm -rf "$INSTALL_DIR"
    echo "📂 '$INSTALL_DIR' kaldırıldı."
else
    echo "⚠️ Uyarı: '$INSTALL_DIR' dizini zaten yok."
fi

if [ -L "$BIN_PATH" ] || [ -f "$BIN_PATH" ]; then
    rm -f "$BIN_PATH"
    echo "📌 '$BIN_PATH' kaldırıldı."
else
    echo "⚠️ Uyarı: '$BIN_PATH' zaten yok."
fi

if [ -d "$INSTALL_DIR/venv" ]; then
    echo "🐍 Virtualenv kaldırılıyor..."
    rm -rf "$INSTALL_DIR/venv"
    echo "📂 Virtualenv temizlendi."
fi

if [ -f "$MAN_PATH" ]; then
    rm -f "$MAN_PATH"
    echo "📖 Man sayfası kaldırıldı."
else
    echo "⚠️ Uyarı: Man sayfası zaten yok."
fi

if mandb &>/dev/null; then
    echo "📖 Man sayfası veritabanı güncellendi!"
else
    echo "⚠️ 'mandb' çalıştırılırken hata oluştu!"
fi

echo "✅ Turkman tamamen kaldırıldı!"
