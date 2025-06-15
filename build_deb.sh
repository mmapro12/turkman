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

if command -v turkman >/dev/null 2>&1; then
    echo "📊 Veritabanı başlatılıyor..."
    turkman db init || true
    
    echo "🔄 Çeviriler senkronize ediliyor..."
    turkman db sync || true
fi

echo "✅ Turkman başarıyla kuruldu!"
echo "💡 Kullanım: turkman <komut_adı>"
echo "📖 Yardım: turkman --help"

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
