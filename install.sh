#!/bin/bash

DISTRO_FAMILY=$(grep '^ID_LIKE=' /etc/os-release | cut -d= -f2 | tr -d '"')
VERSION=$(python3 -c "import sys; sys.path.insert(0, 'src'); from turkman.version import __version__; print(__version__)")
PACKAGE_NAME="turkman"
PACKAGE_FILE="${PACKAGE_NAME}_${VERSION}_${ARCHITECTURE}.deb"
ARCHITECTURE="all"

./build_bin.sh
if echo "$DISTRO_FAMILY" | grep -qi debian; then
    echo "Debian için yapılandırma dosyası oluşturuluyor:"
    ./build_deb.sh
    
    echo ".deb dosyası indiriliyor"
    sudo dpkg -i "${PACKAGE_FILE}"
    sudo apt install -f 
else
    echo "Diğer dağıtımlar için dosyalar kopyalanıyor:"
    sudo cp -r dist/turkman /usr/local/bin/turkman
    chmod +x /usr/local/bin/turkman
    cp -r docs/man/man1/turkman.1  /usr/share/man/man1/turkman.1
    man-db
    turkman db init
    turkman db sync

    echo "manpages-tr kurulumu yapılıyor:"
    git clone https://github.com/TLBP/manpages-tr.git /tmp/manpages-tr/
    cd /tmp/manpages-tr
    make
    sudo make install
    man-db
    rm -rf /tmp/turkman/
fi

echo "Kurulum tamamlandı."
