#!/bin/bash

INSTALL_DIR="/opt/turkman"
BIN_PATH="/usr/local/bin/turkman"
MAN_PATH="/usr/local/share/man/man1/turkman.1"

echo "🔄 Güncelleme başlatılıyor..."

if [[ $EUID -ne 0 ]]; then
   echo "❌ Lütfen root olarak çalıştırın: sudo ./update.sh"
   exit 1
fi

if [ -d "$INSTALL_DIR" ]; then
    cd "$INSTALL_DIR" || exit
    echo "📥 Güncellemeler kontrol ediliyor..."
    
    if [ -d ".git" ]; then
        git pull origin main || { echo "❌ Güncelleme başarısız!"; exit 1; }
    else
        echo "❌ Turkman bir Git deposu değil! Elle güncelleyiniz."
        exit 1
    fi
else
    echo "❌ Turkman bulunamadı! Önce 'sudo ./install.sh' ile yükleyin."
    exit 1
fi

find . -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

if [[ -f "$INSTALL_DIR/docs/man/man1/turkman.1" ]]; then
    ln -sf "$INSTALL_DIR/docs/man/man1/turkman.1" "$MAN_PATH"
    echo "📖 Man sayfası güncellendi!"
else
    echo "⚠️ Uyarı: Man sayfası bulunamadı. 'man turkman' çalışmayabilir."
fi

if mandb &>/dev/null; then
    echo "📖 Man sayfası dizini güncellendi!"
else
    echo "⚠️ 'mandb' çalıştırılırken hata oluştu!"
fi

echo "✅ Güncelleme tamamlandı!"
echo "🔹 Kullanmak için: turkman <komut>"
echo "🔹 Yardım için: turkman -h"
