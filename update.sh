#!/bin/bash

INSTALL_DIR="/opt/turkman"
VENV_DIR="$INSTALL_DIR/venv"
BIN_PATH="/usr/local/bin/turkman"
MAN_PATH="/usr/local/share/man/man1/turkman.1"

echo "\u0001F504 Turkman güncelleme başlatılıyor..."

if [[ $EUID -ne 0 ]]; then
   echo "❌ Lütfen root olarak çalıştırın: sudo ./update.sh"
   exit 1
fi

if [[ ! -d "$INSTALL_DIR" ]]; then
    echo "❌ Turkman bulunamadı! Önce 'sudo ./install.sh' ile yükleyin."
    exit 1
fi

cd "$INSTALL_DIR" || { echo "❌ Dizin değiştirilemedi!"; exit 1; }

if [[ -d ".git" ]]; then
    echo "📥 Güncellemeler kontrol ediliyor..."
    git pull origin main || { echo "❌ Güncelleme başarısız!"; exit 1; }
else
    echo "❌ Turkman bir Git deposu değil! Elle güncelleyiniz."
    exit 1
fi

find . -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

if [[ -d "$VENV_DIR" ]]; then
    echo "🐍 Python bağımlılıkları güncelleniyor..."
    "$VENV_DIR/bin/pip" install --upgrade pip
    if [[ -f "$INSTALL_DIR/requirements.txt" ]]; then
        "$VENV_DIR/bin/pip" install -r "$INSTALL_DIR/requirements.txt" || { echo "❌ Bağımlılıklar güncellenemedi!"; exit 1; }
    else
        echo "⚠️ 'requirements.txt' bulunamadı. Bağımlılıklar yüklenemedi!"
    fi
else
    echo "⚠️ Sanal ortam bulunamadı! 'sudo ./install.sh' ile tekrar kurabilirsiniz."
fi

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
