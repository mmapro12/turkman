#!/bin/bash

INSTALL_DIR="/opt/turkman"
BACKUP_DIR="$INSTALL_DIR.bak"
VENV_DIR="$INSTALL_DIR/venv"
BIN_PATH="/usr/local/bin/turkman"
MAN_PATH="/usr/share/man/man1/turkman.1"
GIT_REPO="https://github.com/mmapro12/turkman.git"

# bash <(wget -qO- https://raw.githubusercontent.com/mmapro12/turkman/main/install.sh)

echo "Turkman güncelleme başlatılıyor..."
if [[ $EUID -ne 0 ]]; then
    echo "❌ Lütfen root olarak çalıştırın: sudo ./update.sh"
    exit 1
fi

if [[ ! -d "$INSTALL_DIR" ]]; then
    echo "❌ Turkman bulunamadı! Önce 'https://github.com/mmapro12/turkman' web sitesinden yükleyin."
    echo "Veya şu komutu deneyin:\nbash <(wget -qO- https://raw.githubusercontent.com/mmapro12/turkman/main/install.sh)"
    exit 1
fi

echo "Yedekleme yapılıyor..."
mv "$INSTALL_DIR" "$BACKUP_DIR"

echo "En son sürüm indiriliyor..."

wget -O turkman_install.sh https://raw.githubusercontent.com/mmapro12/turkman/main/install.sh) || {
    echo "❌ Indirme başarısız oldu! Yedek geri yükleniyor..."
    mv "$BACKUP_DIR" "$INSTALL_DIR"
    exit 1
}

chmod +x turkman_install.sh 
sudo ./turkman_install.sh

rm -rf "$BACKUP_DIR"
echo "✅ Turkman başarıyla güncellendi!"
