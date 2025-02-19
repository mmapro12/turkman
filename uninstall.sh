#!/bin/bash

echo "Turkman kaldırılıyor..."

if [ -f "/usr/local/bin/projem" ]; then
    sudo rm /usr/local/bin/turkman
else
    echo "Symbolic link bulunamadı."
fi

if [ -f "requirements.txt" ]; then
    pip3 uninstall -y -r requirements.txt
fi

read -p "Turkman dosyalarını da silmek istiyor musunuz? (y/n): " confirm
if [ "$confirm" == "y" ]; then
    cd ..
    rm -rf "$(basename "$PWD")"
    echo "Proje dosyaları silindi."
fi

sudo rm -f /usr/share/man/man1/turkman.1.gz
sudo mandb

echo "Kaldırma işlemi tamamlandı."

