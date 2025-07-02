#!/bin/bash

# Turkman bin dosyası oluşturma scripti

set -e

rm -rf build/ dist/  *.spec

pyinstaller --onefile main.py

mv dist/main dist/turkman
rm -rf build/ *.spec

echo "Turkman bin dosyası: dist/turkman"

