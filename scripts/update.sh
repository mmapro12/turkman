#!/bin/bash

INSTALL_DIR="/opt/turkman"
BACKUP_DIR="$INSTALL_DIR.bak"

echo "Turkman güncelleme başlatılıyor..."

if [[ $EUID -ne 0 ]]; then
    echo "❌ Lütfen root olarak çalıştırın: sudo ./update.sh"
    exit 1
fi

if [[ ! -d "$INSTALL_DIR" ]]; then
    echo "❌ Turkman bulunamadı! Önce 'sudo ./install.sh' ile yükleyin."
    exit 1
fi

echo "Yedekleme yapılıyor..."
mv "$INSTALL_DIR" "$BACKUP_DIR"

echo "En son sürüm indiriliyor..."
git clone https://github.com/mmapro12/turkman.git "$INSTALL_DIR" || {
    echo "❌ Git klonlama başarısız oldu! Yedek geri yükleniyor..."
    mv "$BACKUP_DIR" "$INSTALL_DIR"
    exit 1
}

cd "$INSTALL_DIR"



chmod +x scripts/install.sh
sudo scripts/install.sh || {
    echo "❌ Kurulum betiği başarısız oldu! Yedek geri yükleniyor..."
    rm -rf "$INSTALL_DIR"
    mv "$BACKUP_DIR" "$INSTALL_DIR"
    exit 1
}

rm -rf "$BACKUP_DIR"

echo "✅ Turkman başarıyla güncellendi!"
