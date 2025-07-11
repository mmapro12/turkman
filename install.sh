#!/bin/bash

echo "TURKMAN KURULUM SCRIPT"

DISTRO_FAMILY=$(grep '^ID_LIKE=' /etc/os-release | cut -d= -f2 | tr -d '"')
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
    sudo dpkg -i "${PACKAGE_FILE}"
    sudo apt install -f 
else
    echo "Diğer dağıtımlar için dosyalar kopyalanıyor:"
    sudo cp -r dist/turkman /usr/local/bin/
    chmod +x /usr/local/bin/turkman
    cp -r docs/man/man1/turkman.1  /usr/share/man/man1/turkman.1

    echo "manpages-tr kurulumu yapılıyor:"
    git clone https://github.com/TLBP/manpages-tr.git /tmp/manpages-tr/
    cd /tmp/manpages-tr
    make
    sudo make install
    rm -rf /tmp/turkman/
    man-db 
fi

turkman db sync

echo "Kurulum tamamlandı."
