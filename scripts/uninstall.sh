#!/bin/bash

INSTALL_DIR="/opt/turkman"
VENV_DIR="$INSTALL_DIR/venv"
BIN_PATH="/usr/local/bin/turkman"
MAN_PATH="/usr/share/man/man1/turkman.1"
GIT_REPO="https://github.com/mmapro12/turkman.git"

echo "Turkman kaldırılıyor..."

if [[ $EUID -ne 0 ]]; then
    echo "❌ Lütfen root olarak çalıştırın: sudo ./uninstall.sh"
    exit 1
fi

read -p "Turkman'ı kaldırmak istediğinizden emin misiniz? (y/n): " confirm
if [[ "$confirm" != "y" ]]; then
    echo " Kaldırma işlemi iptal edildi."
    exit 1
fi

if [[ -d "$INSTALL_DIR" ]]; then
    rm -rf "$INSTALL_DIR"
    echo " Dizin kaldırıldı: $INSTALL_DIR"
else
    echo " Dizin bulunamadı: $INSTALL_DIR"
fi

if [[ -f "$BIN_PATH" ]]; then
    rm -f "$BIN_PATH"
    echo " Dosya kaldırıldı: $BIN_PATH"
else
    echo " Dosya bulunamadı: $BIN_PATH"
fi

if [[ -f "$MAN_PATH" ]]; then
    rm -f "$MAN_PATH"
    echo " Dosya kaldırıldı: $MAN_PATH"
else
    echo " Dosya bulunamadı: $MAN_PATH"
fi

mandb &>/dev/null && echo " Man sayfası dizini güncellendi!" || echo "⚠️ 'mandb' çalıştırılırken hata oluştu!"

echo "✅ Turkman başarıyla kaldırıldı!"
