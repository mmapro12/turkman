#!/bin/bash

# Turkman .deb paketi oluşturma scripti
# Bu script, Python projesini .deb paketine dönüştürür

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Turkman .deb paketi oluşturuluyor...${NC}"

VERSION=$(python3 -c "import sys; sys.path.insert(0, 'src'); from turkman.version import __version__; print(__version__)")
PACKAGE_NAME="turkman"
ARCHITECTURE="all"
MAINTAINER="mmapro12 <asia172007@gmail.com>"

echo -e "${YELLOW}📦 Paket: ${PACKAGE_NAME} v${VERSION}${NC}"

rm -rf build/ dist/ debian/ *.deb

mkdir -p debian/DEBIAN
mkdir -p debian/usr/local/bin
mkdir -p debian/usr/local/lib/python3/dist-packages/turkman
mkdir -p debian/usr/share/doc/turkman
mkdir -p debian/usr/share/man/man1

# Control dosyasını oluştur
cat > debian/DEBIAN/control << EOF
Package: ${PACKAGE_NAME}
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: ${ARCHITECTURE}
Maintainer: ${MAINTAINER}
Depends: python3 (>= 3.8), python3-pip, python3-requests, python3-typer, manpages-tr
Suggests: curl, git
Homepage: https://github.com/mmapro12/turkman
Description: Linux komutları için Türkçe man sayfaları
 Turkman, Linux komutlarının man sayfalarını Türkçeye çevirir ve 
 kullanıcıların ana dillerinde sistem dokümantasyonuna erişmesini sağlar.
 .
 Özellikler:
  - Çoklu kaynak desteği (yerel, veritabanı, GitHub)
  - SQLite tabanlı önbellekleme
  - Otomatik güncelleme sistemi
  - Kolay kullanımlı CLI arayüzü
EOF

# Postinst script (kurulum sonrası)
cat > debian/DEBIAN/postinst << 'EOF'
#!/bin/bash
set -e

echo "🔧 Turkman kurulum sonrası yapılandırma..."

# Gerçek kullanıcıyı ve home dizinini tespit et
get_real_user_info() {
    # Eğer SUDO_USER varsa, bu gerçek kullanıcıdır
    if [ -n "$SUDO_USER" ] && [ "$SUDO_USER" != "root" ]; then
        REAL_USER="$SUDO_USER"
        REAL_HOME=$(getent passwd "$SUDO_USER" | cut -d: -f6)
    # Eğer SUDO_UID varsa, bu yöntemi kullan
    elif [ -n "$SUDO_UID" ] && [ "$SUDO_UID" != "0" ]; then
        REAL_USER=$(getent passwd "$SUDO_UID" | cut -d: -f1)
        REAL_HOME=$(getent passwd "$SUDO_UID" | cut -d: -f6)
    # Son çare olarak, tty'nin sahibini kontrol et
    else
        TTY_OWNER=$(stat -c '%U' "$(tty 2>/dev/null)" 2>/dev/null || echo "")
        if [ -n "$TTY_OWNER" ] && [ "$TTY_OWNER" != "root" ]; then
            REAL_USER="$TTY_OWNER"
            REAL_HOME=$(getent passwd "$TTY_OWNER" | cut -d: -f6)
        else
            # Hiçbiri işe yaramazsa, varsayılan değerler
            REAL_USER=""
            REAL_HOME=""
        fi
    fi
}

# Kullanıcı bilgilerini al
get_real_user_info

if command -v turkman >/dev/null 2>&1; then
    if [ -n "$REAL_USER" ] && [ -n "$REAL_HOME" ] && [ -d "$REAL_HOME" ]; then
        echo "👤 Gerçek kullanıcı tespit edildi: $REAL_USER ($REAL_HOME)"
        
        # Kullanıcının UID ve GID'sini al
        USER_UID=$(id -u "$REAL_USER")
        USER_GID=$(id -g "$REAL_USER")
        
        echo "📊 Veritabanı başlatılıyor..."
        # Gerçek kullanıcı olarak turkman komutlarını çalıştır
        sudo -u "$REAL_USER" -H bash -c "
            export HOME='$REAL_HOME'
            cd '$REAL_HOME'
            turkman db init
        " || true
        
        echo "🔄 Çeviriler senkronize ediliyor..."
        sudo -u "$REAL_USER" -H bash -c "
            export HOME='$REAL_HOME'
            cd '$REAL_HOME'
            turkman db sync
        " || true
        
        # .turkmandb dizininin doğru sahiplik ve izinlerini ayarla
        TURKMAN_DB_DIR="$REAL_HOME/.turkmandb"
        if [ -d "$TURKMAN_DB_DIR" ]; then
            echo "🔐 Dizin izinleri düzenleniyor..."
            chown -R "$USER_UID:$USER_GID" "$TURKMAN_DB_DIR"
            chmod -R 755 "$TURKMAN_DB_DIR"
        fi
        
    else
        echo "⚠️  Gerçek kullanıcı tespit edilemedi, sistem geneli kurulum yapılıyor..."
        echo "📊 Veritabanı başlatılıyor..."
        turkman db init || true
        
        echo "🔄 Çeviriler senkronize ediliyor..."
        turkman db sync || true
        
        echo "💡 Not: Lütfen ilk kullanımdan önce 'turkman db init' komutunu çalıştırın."
    fi
else
    echo "❌ turkman komutu bulunamadı!"
    exit 1
fi

echo "✅ Turkman başarıyla kuruldu!"
echo "💡 Kullanım: turkman <komut_adı>"
echo "📖 Yardım: turkman --help"

# Eğer gerçek kullanıcı tespit edildiyse, onu bilgilendir
if [ -n "$REAL_USER" ]; then
    echo "🏠 Veritabanı konumu: $REAL_HOME/.turkmandb"
fi

exit 0
EOF

cat > debian/DEBIAN/prerm << 'EOF'
#!/bin/bash
set -e

echo "🗑️  Turkman kaldırılıyor..."

# Kullanıcı veritabanını koru (isteğe bağlı)
if [ -d "$HOME/.turkmandb" ]; then
    echo "💾 Veritabanı korunuyor: $HOME/.turkmandb"
    echo "🔍 Manuel olarak kaldırmak için: rm -rf ~/.turkmandb"
fi

exit 0
EOF

chmod 755 debian/DEBIAN/postinst
chmod 755 debian/DEBIAN/prerm

# Python dosyalarını kopyala
echo -e "${YELLOW}📁 Python dosyaları kopyalanıyor...${NC}"
cp -r src/turkman/* debian/usr/local/lib/python3/dist-packages/turkman/

# Ana executable script oluştur
cat > debian/usr/local/bin/turkman << 'EOF'
#!/usr/bin/env python3
import sys
import os

# Turkman'ı Python path'ine ekle
sys.path.insert(0, '/usr/local/lib/python3/dist-packages')

try:
    from turkman.turkman import main
    main()
except ImportError as e:
    print(f"❌ Turkman modülleri yüklenemedi: {e}")
    print("🔧 Paket yeniden kurulumu gerekebilir: sudo apt reinstall turkman")
    sys.exit(1)
except Exception as e:
    print(f"❌ Beklenmeyen hata: {e}")
    sys.exit(1)
EOF

chmod +x debian/usr/local/bin/turkman

# Dokümantasyon dosyalarını kopyala
echo -e "${YELLOW}📚 Dokümantasyon kopyalanıyor...${NC}"
cp README.md debian/usr/share/doc/turkman/
cp LICENSE debian/usr/share/doc/turkman/ 2>/dev/null || echo "LICENSE dosyası bulunamadı"

# Man sayfası oluştur
cp -r ./docs/man/man1/turkman.1  debian/usr/share/man/man1/turkman.1

# Man sayfasını sıkıştır
gzip -9 debian/usr/share/man/man1/turkman.1

# .deb paketini oluştur
echo -e "${YELLOW}📦 .deb paketi oluşturuluyor...${NC}"
PACKAGE_FILE="${PACKAGE_NAME}_${VERSION}_${ARCHITECTURE}.deb"

dpkg-deb --build debian "${PACKAGE_FILE}"

# Paket bilgilerini göster
echo -e "${GREEN}✅ Paket başarıyla oluşturuldu!${NC}"
echo -e "${BLUE}📦 Paket dosyası: ${PACKAGE_FILE}${NC}"
echo -e "${BLUE}📊 Paket boyutu: $(du -h ${PACKAGE_FILE} | cut -f1)${NC}"

# Paket içeriğini kontrol et
echo -e "${YELLOW}📋 Paket içeriği:${NC}"
dpkg-deb --contents "${PACKAGE_FILE}"

# Kurulum talimatları
echo -e "${GREEN}🚀 Kurulum için:${NC}"
echo -e "${BLUE}   sudo dpkg -i ${PACKAGE_FILE}${NC}"
echo -e "${BLUE}   sudo apt-get install -f  # Bağımlılık sorunları varsa${NC}"

# Temizlik seçeneği
read -p "🧹 Geçici dosyaları temizle? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf debian/
    echo -e "${GREEN}✅ Temizlik tamamlandı!${NC}"
fi

echo -e "${GREEN}🎉 Turkman .deb paketi hazır!${NC}"
