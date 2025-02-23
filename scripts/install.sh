#!/bin/bash

INSTALL_DIR="/opt/turkman"
VENV_DIR="$INSTALL_DIR/venv"
BIN_PATH="/usr/local/bin/turkman"
MAN_PATH="/usr/share/man/man1/turkman.1"

echo " Turkman kuruluyor..."

if [[ $EUID -ne 0 ]]; then
    echo "❌ Lütfen root olarak çalıştırın: sudo ./install.sh"
    exit 1
fi

if ! command -v python3 &>/dev/null; then
    echo "❌ Python 3 yüklü değil! Lütfen önce Python 3 yükleyin."
    exit 1
fi

rm -rf "$INSTALL_DIR"
rm -f "$BIN_PATH"
rm -f "$MAN_PATH"

mkdir -p "$INSTALL_DIR" || { echo "❌ $INSTALL_DIR dizini oluşturulamadı!"; exit 1; }

cp -r * "$INSTALL_DIR" || { echo "❌ Dosyalar kopyalanırken hata oluştu!"; exit 1; }

if [[ ! -d "$VENV_DIR" ]]; then
    echo " Sanal ortam oluşturuluyor..."
    python3 -m venv "$VENV_DIR" || { echo "❌ Sanal ortam oluşturulamadı!"; exit 1; }
fi

echo " Python bağımlılıkları yükleniyor..."
"$VENV_DIR/bin/pip" install --upgrade pip
if [[ -f "$INSTALL_DIR/requirements.txt" ]]; then
    "$VENV_DIR/bin/pip" install -r "$INSTALL_DIR/requirements.txt" || { echo "❌ Python bağımlılıkları yüklenemedi!"; exit 1; }
else
    echo "⚠️ 'requirements.txt' bulunamadı. Bağımlılıklar yüklenemedi!"
fi

echo " Çalıştırılabilir dosya oluşturuluyor..."
cat << EOF > "$BIN_PATH"
#!/bin/bash
source "$VENV_DIR/bin/activate"
python "$INSTALL_DIR/turkman.py" "\$@"
EOF

chmod +x "$BIN_PATH"

if [[ -f "$INSTALL_DIR/docs/man/man1/turkman.1" ]]; then
    ln -sf "$INSTALL_DIR/docs/man/man1/turkman.1" "$MAN_PATH" || { echo "❌ Man sayfası oluşturulamadı!"; exit 1; }
    echo " Man sayfası başarıyla eklendi!"
    mandb &>/dev/null && echo " Man sayfası dizini güncellendi!" || echo "⚠️ 'mandb' çalıştırılırken hata oluştu!"
else
    echo "⚠️ Uyarı: Man sayfası bulunamadı. 'man turkman' çalışmayabilir."
fi

echo "✅ Turkman başarıyla kuruldu!"
echo " Kullanmak için: turkman <komut>"
echo " Yardım için: turkman -h"
