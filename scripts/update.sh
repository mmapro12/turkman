#!/bin/bash

# Turkman Updater
# Bu script Turkman'ı en son sürüme günceller

INSTALL_DIR="/opt/turkman"
BACKUP_DIR="$INSTALL_DIR.backup.$(date +%Y%m%d_%H%M%S)"
VENV_DIR="$INSTALL_DIR/venv"
BIN_PATH="/usr/local/bin/turkman"
MAN_PATH="/usr/share/man/man1/turkman.1"
GIT_REPO="https://github.com/mmapro12/turkman.git"
INSTALL_SCRIPT_URL="https://raw.githubusercontent.com/mmapro12/turkman/refs/heads/main/install.sh"

# Gerçek kullanıcıyı tespit et
if [[ -n "$SUDO_USER" ]]; then
    REAL_USER="$SUDO_USER"
    REAL_HOME=$(eval echo "~$SUDO_USER")
else
    REAL_USER="$USER"
    REAL_HOME="$HOME"
fi

DB_DIR="$REAL_HOME/.turkmandb"

echo "🔄 Turkman güncelleme işlemi başlatılıyor..."

# Root kontrolü
if [[ $EUID -ne 0 ]]; then
    echo "❌ Bu script root yetkisi gerektirir!"
    echo "   Kullanım: sudo ./update.sh"
    exit 1
fi

# Turkman'ın kurulu olup olmadığını kontrol et
if [[ ! -d "$INSTALL_DIR" ]]; then
    echo "❌ Turkman sistemde bulunamadı!"
    echo "📥 Önce Turkman'ı yüklemeniz gerekiyor:"
    echo "   curl -L $INSTALL_SCRIPT_URL | sudo bash"
    exit 1
fi

# Mevcut sürümü göster
echo "📊 Mevcut kurulum bilgileri:"
echo "   • Kurulum dizini: $INSTALL_DIR"
echo "   • Binary dosyası: $BIN_PATH"
if [[ -f "$BIN_PATH" ]]; then
    echo "   • Mevcut sürüm: $($BIN_PATH version 2>/dev/null | head -1 || echo 'Bilinmiyor')"
fi

# İnternet bağlantısını kontrol et
echo "🌐 İnternet bağlantısı kontrol ediliyor..."
if ! curl -s --connect-timeout 10 "$INSTALL_SCRIPT_URL" > /dev/null; then
    echo "❌ İnternet bağlantısı bulunamadı veya GitHub'a erişilemiyor!"
    echo "   Lütfen internet bağlantınızı kontrol edin ve tekrar deneyin."
    exit 1
fi
echo "   ✅ İnternet bağlantısı başarılı"

# Kullanıcı onayı
echo ""
read -p "❓ Turkman'ı güncellemek istediğinizden emin misiniz? (y/N): " -r confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "🚫 Güncelleme işlemi iptal edildi."
    exit 0
fi

# Kullanıcı veritabanını yedekle
if [[ -d "$DB_DIR" ]]; then
    echo "💾 Kullanıcı veritabanı yedekleniyor..."
    DB_BACKUP="$DB_DIR.backup.$(date +%Y%m%d_%H%M%S)"
    sudo -u "$REAL_USER" cp -r "$DB_DIR" "$DB_BACKUP" && echo "   ✅ Yedek oluşturuldu: $DB_BACKUP" || echo "   ⚠️ Veritabanı yedeklenemedi"
fi

# Mevcut kurulumu yedekle
echo "📦 Mevcut kurulum yedekleniyor..."
if cp -r "$INSTALL_DIR" "$BACKUP_DIR" 2>/dev/null; then
    echo "   ✅ Yedek oluşturuldu: $BACKUP_DIR"
else
    echo "   ⚠️ Yedekleme başarısız! Devam edilsin mi? (y/N)"
    read -r backup_confirm
    if [[ ! "$backup_confirm" =~ ^[Yy]$ ]]; then
        echo "🚫 Güncelleme iptal edildi."
        exit 1
    fi
fi

# Rollback fonksiyonu
rollback() {
    echo "🔄 Eski sürüm geri yükleniyor..."
    if [[ -d "$BACKUP_DIR" ]]; then
        rm -rf "$INSTALL_DIR"
        mv "$BACKUP_DIR" "$INSTALL_DIR"
        echo "   ✅ Eski sürüm geri yüklendi"
    else
        echo "   ❌ Yedek bulunamadı! Manuel müdahale gerekebilir."
    fi
}

# Güncelleme işlemi
echo "⬇️ En son sürüm indiriliyor ve kuruluyor..."

# Geçici script dosyası
TEMP_INSTALL="/tmp/turkman_install_$(date +%s).sh"

# Install script'i indir
if curl -L -o "$TEMP_INSTALL" "$INSTALL_SCRIPT_URL"; then
    chmod +x "$TEMP_INSTALL"
    echo "   ✅ Install script indirildi"
else
    echo "   ❌ Install script indirilemedi!"
    rollback
    exit 1
fi

# Mevcut kurulumu kaldır
rm -rf "$INSTALL_DIR"

# Yeni sürümü kur
echo "🔧 Yeni sürüm kuruluyor..."
if "$TEMP_INSTALL"; then
    echo "   ✅ Yeni sürüm başarıyla kuruldu"
    
    # Geçici dosyayı temizle
    rm -f "$TEMP_INSTALL"
    
    # Eski yedegi temizle
    if [[ -d "$BACKUP_DIR" ]]; then
        rm -rf "$BACKUP_DIR"
        echo "   🗑️ Eski yedek temizlendi"
    fi
    
    echo ""
    echo "✅ Turkman başarıyla güncellendi!"
    
    # Yeni sürüm bilgisini göster
    if [[ -f "$BIN_PATH" ]]; then
        echo "🎉 Yeni sürüm: $($BIN_PATH version 2>/dev/null | head -1 || echo 'Bilinmiyor')"
    fi
    
    echo "🚀 Kullanmaya devam edebilirsiniz: turkman --help"
    
else
    echo "   ❌ Yeni sürüm kurulumu başarısız!"
    rm -f "$TEMP_INSTALL"
    rollback
    echo "❌ Güncelleme başarısız! Eski sürüm geri yüklendi."
    exit 1
fi
