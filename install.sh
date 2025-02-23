#!/bin/bash

INSTALL_DIR="/opt/turkman"
VENV_DIR="$INSTALL_DIR/venv"
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

if ! command -v python3 &>/dev/null; then
    echo "❌ Python 3 yüklü değil! Lütfen önce Python 3 yükleyin."
    exit 1
fi

echo "🐍 Python 3 bulundu. Sanal ortam oluşturuluyor..."

mkdir -p "$INSTALL_DIR" || { echo "❌ Dizin oluşturulamadı!"; exit 1; }

cp -r * "$INSTALL_DIR" || { echo "❌ Dosyalar kopyalanırken hata oluştu!"; exit 1; }

if [[ ! -d "$VENV_DIR" ]]; then
    echo "🐍 Sanal ortam oluşturuluyor..."
    python3 -m venv "$VENV_DIR"
fi

echo "📌 Python bağımlılıkları yükleniyor..."
"$VENV_DIR/bin/pip" install --upgrade pip
if [[ -f "$INSTALL_DIR/requirements.txt" ]]; then
    "$VENV_DIR/bin/pip" install -r "$INSTALL_DIR/requirements.txt" || { echo "❌ Python bağımlılıkları yüklenemedi!"; exit 1; }
else
    echo "⚠️ 'requirements.txt' bulunamadı. Bağımlılıklar yüklenemedi!"
fi

echo "🚀 Çalıştırılabilir dosya oluşturuluyor..."
cat << EOF > "$BIN_PATH"
#!/bin/bash
source "$VENV_DIR/bin/activate"
python "$INSTALL_DIR/turkman.py" "\$@"
EOF

chmod +x "$BIN_PATH"

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
