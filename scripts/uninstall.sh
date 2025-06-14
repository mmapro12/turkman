#!/bin/bash

# Turkman Uninstaller
# Bu script Turkman'ı sistemden tamamen kaldırır

INSTALL_DIR="/opt/turkman"
VENV_DIR="$INSTALL_DIR/venv"
BIN_PATH="/usr/local/bin/turkman"
MAN_PATH="/usr/share/man/man1/turkman.1"

# Gerçek kullanıcıyı tespit et (sudo ile çalışıyorsa)
if [[ -n "$SUDO_USER" ]]; then
    REAL_USER="$SUDO_USER"
    REAL_HOME=$(eval echo "~$SUDO_USER")
else
    REAL_USER="$USER"
    REAL_HOME="$HOME"
fi

DB_DIR="$REAL_HOME/.turkmandb"

echo "🗑️ Turkman kaldırma işlemi başlatılıyor..."

# Root kontrolü
if [[ $EUID -ne 0 ]]; then
    echo "❌ Bu script root yetkisi gerektirir!"
    echo "   Kullanım: sudo ./uninstall.sh"
    exit 1
fi

# Turkman'ın kurulu olup olmadığını kontrol et
if [[ ! -d "$INSTALL_DIR" && ! -f "$BIN_PATH" ]]; then
    echo "⚠️ Turkman sistemde bulunamadı. Zaten kaldırılmış olabilir."
    exit 0
fi

# Kullanıcı onayı al
echo "📋 Kaldırılacak dosya ve dizinler:"
[[ -d "$INSTALL_DIR" ]] && echo "   • $INSTALL_DIR"
[[ -f "$BIN_PATH" ]] && echo "   • $BIN_PATH"
[[ -f "$MAN_PATH" ]] && echo "   • $MAN_PATH"
[[ -d "$DB_DIR" ]] && echo "   • $DB_DIR (kullanıcı veritabanı)"

echo ""
read -p "❓ Turkman'ı tamamen kaldırmak istediğinizden emin misiniz? (y/N): " -r confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "🚫 Kaldırma işlemi iptal edildi."
    exit 0
fi

echo "🔄 Kaldırma işlemi başlıyor..."

# Ana kurulum dizinini kaldır
if [[ -d "$INSTALL_DIR" ]]; then
    echo "📁 Kurulum dizini kaldırılıyor: $INSTALL_DIR"
    rm -rf "$INSTALL_DIR" && echo "   ✅ Başarılı" || echo "   ❌ Hata oluştu"
fi

# Binary dosyasını kaldır
if [[ -f "$BIN_PATH" ]]; then
    echo "🗂️ Çalıştırılabilir dosya kaldırılıyor: $BIN_PATH"
    rm -f "$BIN_PATH" && echo "   ✅ Başarılı" || echo "   ❌ Hata oluştu"
fi

# Man sayfasını kaldır
if [[ -f "$MAN_PATH" ]]; then
    echo "📖 Man sayfası kaldırılıyor: $MAN_PATH"
    rm -f "$MAN_PATH" && echo "   ✅ Başarılı" || echo "   ❌ Hata oluştu"
    
    # Man veritabanını güncelle
    echo "🔄 Man veritabanı güncelleniyor..."
    if mandb &>/dev/null; then
        echo "   ✅ Man veritabanı güncellendi"
    else
        echo "   ⚠️ Man veritabanı güncellenirken hata oluştu"
    fi
fi

# Kullanıcı veritabanını kaldır (kullanıcı onayı ile)
if [[ -d "$DB_DIR" ]]; then
    echo ""
    read -p "❓ Kullanıcı veritabanını da kaldırmak istiyor musunuz? ($DB_DIR) (y/N): " -r db_confirm
    if [[ "$db_confirm" =~ ^[Yy]$ ]]; then
        echo "🗄️ Kullanıcı veritabanı kaldırılıyor..."
        sudo -u "$REAL_USER" rm -rf "$DB_DIR" && echo "   ✅ Başarılı" || echo "   ❌ Hata oluştu"
    else
        echo "💾 Kullanıcı veritabanı korundu: $DB_DIR"
    fi
fi

# Temizlik kontrolü
remaining_files=()
[[ -d "$INSTALL_DIR" ]] && remaining_files+=("$INSTALL_DIR")
[[ -f "$BIN_PATH" ]] && remaining_files+=("$BIN_PATH")
[[ -f "$MAN_PATH" ]] && remaining_files+=("$MAN_PATH")

if [[ ${#remaining_files[@]} -eq 0 ]]; then
    echo ""
    echo "✅ Turkman başarıyla kaldırıldı!"
    echo "🙏 Turkman'ı kullandığınız için teşekkürler!"
else
    echo ""
    echo "⚠️ Bazı dosyalar kaldırılamadı:"
    printf '   • %s\n' "${remaining_files[@]}"
    echo "Manuel olarak kaldırmanız gerekebilir."
fi
