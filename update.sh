#!/bin/bash

echo "Uygulama güncelleniyor..."
git pull origin main 
sudo rm -f /usr/share/man/man1/myapp.1.gz
sudo cp ./docs/man/man1/myapp.1 /usr/share/man/man1/
sudo gzip /usr/share/man/man1/turkman.1
sudo mandb
echo "Uygulama başarıyla güncellendi!"

