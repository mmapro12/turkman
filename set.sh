#!/bin/bash

FILE="version.txt"

if [[ -z "$1" ]]; then
    echo "❌ Kullanım: ./set \"yeni sürüm\""
    exit 1
fi

echo "$1" > "$FILE"
echo "✅ '$FILE' güncellendi: $1"

