#!/bin/bash
set -euo pipefail

echo "TURKMAN KURULUM SCRIPT"

# Debian'ın kendisinde ID_LIKE yoktur, bu yüzden ID de okunur
DISTRO_FAMILY=$(grep -E '^(ID|ID_LIKE)=' /etc/os-release | cut -d= -f2 | tr -d '"')
VERSION=$(python3 -c "import sys; sys.path.insert(0, 'src'); from turkman.version import __version__; print(__version__)")
PACKAGE_NAME="turkman"
ARCHITECTURE="all"
PACKAGE_FILE="${PACKAGE_NAME}_${VERSION}_${ARCHITECTURE}.deb"

./build_bin.sh
if echo "$DISTRO_FAMILY" | grep -qi debian; then
    sudo apt update
    sudo apt install python3 python3-pip curl manpages-tr
    echo "Debian için yapılandırma dosyası oluşturuluyor:"
    ./build_deb.sh
    
    echo ".deb dosyası indiriliyor"
    # Eksik bağımlılık varsa dpkg hata verir; apt bunları tamamlar
    sudo dpkg -i "${PACKAGE_FILE}" || sudo apt install -f
else
    echo "Diğer dağıtımlar için dosyalar kopyalanıyor:"
    sudo install -Dm755 dist/turkman /usr/local/bin/turkman
    sudo install -Dm644 docs/man/man1/turkman.1 /usr/share/man/man1/turkman.1

    echo "manpages-tr kurulumu yapılıyor:"
    TEMP_DIR=$(mktemp -d)
    trap 'rm -rf "$TEMP_DIR"' EXIT
    git clone https://github.com/TLBP/manpages-tr.git "$TEMP_DIR/manpages-tr"
    (
        cd "$TEMP_DIR/manpages-tr"
        make
        sudo make install
    )
    sudo mandb
fi

turkman db sync || echo "Veritabanı güncellenemedi. Daha sonra 'turkman db sync' çalıştırın."

echo "Kurulum tamamlandı."
