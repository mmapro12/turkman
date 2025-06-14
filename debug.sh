#!/bin/bash

echo "=== TURKMAN DEBUG SCRIPTI ==="
echo "OS Bilgisi:"
cat /etc/os-release | grep -E "(NAME|VERSION)"
echo ""

echo "=== MAN KOMUTU TESTLERI ==="
echo "1. ls man sayfası lokasyonu:"
man -w ls 2>/dev/null || echo "man -w ls başarısız"

echo ""
echo "2. ls man sayfası var mı?"
if man -w ls &>/dev/null; then
    ls_man_path=$(man -w ls)
    echo "   Yol: $ls_man_path"
    echo "   Dosya var mı: $(test -f "$ls_man_path" && echo "EVET" || echo "HAYIR")"
    if [[ -f "$ls_man_path" ]]; then
        echo "   Dosya boyutu: $(stat -c%s "$ls_man_path") bytes"
        echo "   Dosya türü: $(file "$ls_man_path")"
    fi
else
    echo "   ls man sayfası bulunamadı!"
fi

echo ""
echo "3. Normal man ls çalışıyor mu?"
if man ls >/dev/null 2>&1 < /dev/null; then
    echo "   man ls: ÇALIŞIYOR"
else
    echo "   man ls: ÇALIŞMIYOR"
fi

echo ""
echo "4. Man sistemi kontrolü:"
echo "   MANPATH: ${MANPATH:-"tanımlı değil"}"
echo "   man komutu: $(which man)"
echo "   Man dizinleri:"
manpath 2>/dev/null | tr ':' '\n' | while read dir; do
    echo "     $dir"
done

echo ""
echo "5. Türkçe man dizini kontrolü:"
TRPATH="/usr/share/man/tr/"
echo "   TR man dizini var mı: $(test -d "$TRPATH" && echo "EVET" || echo "HAYIR")"
if [[ -d "$TRPATH" ]]; then
    echo "   TR man dizinindeki dosyalar:"
    find "$TRPATH" -name "*ls*" 2>/dev/null | head -5
fi

echo ""
echo "6. ls komutu bilgileri:"
echo "   ls komutu yolu: $(which ls)"
echo "   ls komut türü: $(type ls)"

echo ""
echo "=== TURKMAN SPECIFIK TESTLER ==="
echo "7. Veritabanı durumu:"
if [[ -f "$HOME/.turkmandb/turkman.db" ]]; then
    echo "   Veritabanı var: EVET"
    echo "   Veritabanı boyutu: $(stat -c%s "$HOME/.turkmandb/turkman.db") bytes"
    
    # SQLite kontrolü
    if command -v sqlite3 &>/dev/null; then
        echo "   ls çevirisi var mı:"
        sqlite3 "$HOME/.turkmandb/turkman.db" "SELECT command FROM man_pages WHERE command='ls';" 2>/dev/null || echo "     Sorgu başarısız"
    else
        echo "   sqlite3 yüklü değil"
    fi
else
    echo "   Veritabanı var: HAYIR"
fi

echo ""
echo "8. Python ve modül kontrolleri:"
python3 -c "
try:
    import sqlite3
    print('   sqlite3 modülü: OK')
except ImportError:
    print('   sqlite3 modülü: HATA')

try:
    import requests
    print('   requests modülü: OK')
except ImportError:
    print('   requests modülü: HATA')

try:
    import typer
    print('   typer modülü: OK')
except ImportError:
    print('   typer modülü: HATA')
"

echo ""
echo "9. /tmp dosya izinleri:"
echo "   /tmp dizini yazılabilir mi: $(test -w /tmp && echo "EVET" || echo "HAYIR")"

echo ""
echo "=== SON TEST ==="
echo "10. Manuel man sayfası oluşturup test edelim:"
cat << 'EOF' > /tmp/test_ls.man
.TH LS 1 "Test" "Test Man Page"
.SH NAME
ls \- test man sayfası
.SH DESCRIPTION
Bu bir test man sayfasıdır.
EOF

echo "    Test man sayfası oluşturuldu"
if man /tmp/test_ls.man >/dev/null 2>&1 < /dev/null; then
    echo "    Test man sayfası çalışıyor: EVET"
else
    echo "    Test man sayfası çalışıyor: HAYIR"
fi

rm -f /tmp/test_ls.man

echo ""
echo "=== DEBUG TAMAMLANDI ==="
