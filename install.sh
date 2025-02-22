#!/bin/bash

INSTALL_DIR="/opt/turkman"
BIN_PATH="/usr/local/bin/turkman"
MAN_PATH="/usr/local/share/man/man1/turkman.1"

echo "🔧 Turkman indiriliyor..."

if [[ $EUID -ne 0 ]]; then
    echo "❌ Lütfen root olarak çalıştırın: sudo ./install.sh"
    exit 1
fi

if ! dpkg -s manpages-tr &>/dev/null; then
    echo "📦 'manpages-tr' paketi eksik. Yükleniyor..."
    apt update && apt install -y manpages-tr || { echo "❌ Paket yüklenemedi!"; exit 1; }
else
    echo "✅ 'manpages-tr' zaten yüklü."
fi

if command -v python3 &>/dev/null; then
    echo "🐍 Python 3 bulundu. Gerekli paketler yükleniyor..."
    python3 -m pip install --upgrade pip
    if [[ -f requirements.txt ]]; then
        python3 -m pip install -r requirements.txt || { echo "❌ Python bağımlılıkları yüklenemedi!"; exit 1; }
    else
        echo "⚠️ 'requirements.txt' bulunamadı. Bağımlılıklar yüklenemedi!"
    fi
else
    echo "❌ Python 3 yüklü değil! Lütfen önce Python 3 yükleyin."
    exit 1
fi

echo "📂 Uygulama '$INSTALL_DIR' dizinine kopyalanıyor..."
mkdir -p "$INSTALL_DIR" || { echo "❌ Dizin oluşturulamadı!"; exit 1; }
cp -r * "$INSTALL_DIR" || { echo "❌ Dosyalar kopyalanırken hata oluştu!"; exit 1; }

if [[ -f "$INSTALL_DIR/turkman.py" ]]; then
    chmod +x "$INSTALL_DIR/turkman.py"
    ln -sf "$INSTALL_DIR/turkman.py" "$BIN_PATH"
else
    echo "❌ Hata: 'turkman.py' bulunamadı! Kurulum başarısız."
    exit 1
fi

if [[ -f "$INSTALL_DIR/docs/man/man1/turkman.1" ]]; then
    ln -sf "$INSTALL_DIR/docs/man/man1/turkman.1" "$MAN_PATH"
    echo "📖 Man sayfası başarıyla eklendi!"
else
    echo "⚠️ Uyarı: Man sayfası bulunamadı. 'man turkman' çalışmayabilir."
fi

if mandb &>/dev/null; then
    echo "📖 Man sayfası dizini güncellendi!"
else
    echo "⚠️ 'mandb' çalıştırılırken hata oluştu!"
fi

echo "✅ Turkman başarıyla kuruldu!"
echo "🔹 Kullanmak için: turkman <komut>"
echo "🔹 Yardım için: turkman -h"
