#!/bin/bash

echo "Turkman kurulumu başlıyor..."

if command -v pip3 &>/dev/null; then
    pip3 install -r requirements.txt
else
    echo "pip3 yüklü değil, lütfen manuel yükleyin."
    exit 1
fi

sudo apt install manpages-tr -y
if command -v manpages-tr &>/dev/null; then
    echo "manpages-tr başarıyla yüklendi!"
else
    echo "manpages-tr yüklenirken bir hata oluştu."
fi

chmod +x turkman.py
sudo ln -sf "$(pwd)/turkman.py" /usr/local/bin/turkman

sudo cp ./docs/man/man1/turkman.1 /usr/share/man/man1/
sudo gzip /usr/share/man/man1/turkman.1
sudo mandb

echo "Kurulum tamamlandı. 'turkman' komutu ile çalıştırabilirsiniz."
echo "Yardım için 'turkman -h' komutunu kullanabilirsiniz."

