#!/bin/bash

INSTALL_DIR="/opt/turkman"
BIN_PATH="/usr/local/bin/turkman"
MAN_PATH="/usr/local/share/man/man1/turkman.1.gz"

echo "⚠️ Turkman kaldırılacak. Emin misiniz? (y/n)"
read -r response
if [[ "$response" != "y" ]]; then
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
else
    echo "❌ Turkman bulunamadı!"
fi

if [ -f "$BIN_PATH" ]; then
    rm -f "$BIN_PATH"
fi

if [ -f "$MAN_PATH" ]; then
    rm -f "$MAN_PATH"
fi
mandb
echo "✅ Turkman tamamen kaldırıldı!"

