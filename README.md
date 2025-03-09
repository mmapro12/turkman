
# Turkman: Linux için Türkçe Man sayfaları çevirisi ve zenginleştirme uygulaması

Windows 10'un desteğinin sona ermesiyle, Windows 11'e geçiş yapamayan birçok kullanıcının Linuxa geçişi zor olacakken, Turkman bu geçişi kolaylaştırmak amacıyla tasarlanmıştır. Uygulama, Linux komutlarının man sayfalarını Türkçeye çevirir ve zenginleştirir. Turkman, Türkçe içerik eksikliğini gidererek, Linux kullanıcıları için daha erişilebilir bir deneyim sunmayı hedefler.



## Güncellemeler 
Güncellemeler her 2 haftada gelir.Hata düzltmeleri ve planlanıp da gecikmiş özelliklerin eklenmesi ise anında yapılır.

### Son Eklenenler (v0.2.0) -> 09.03.2025 

- Hata düzeltmeleri.
- İndirme, kaldırma sisteminde köklü değişiklikler yapıldı.
- Güncelleme sistemi eklendi.
- Dokümantasyon tekrardan yazıldı.
- Turkman veri tabanı güncellendi.

### Üzerinde çalıştıklarımız

- Yapay zeka ile man dosyalarının çevirme sistemi.
- Typer ile CLI desteği.
- Detaylı dokümatasyon.
- Otomatik guncelleme sistemi.



## Kurulum

Not: Turkman şimdilik sadece Debian ve Debian tabanlı distrolarda çalışmaktadır.

### Gereksinimler

- [manpages-tr](https://github.com/TLBP/manpages-tr/)
- `git`, `wget`

Tüm gereksinimleri indirmek için:
```bash
sudo apt install manpages-tr git wget
```

### İndirme

Turkman'ı indirmek için:

```bash
bash <(wget -qO- https://raw.githubusercontent.com/mmapro12/turkman/main/install.sh)
```

### Güncelleme

Turkman'ı güncellemek için:

```bash
turkman update
```

### Kaldırma 

Turkman'ı kaldırmak için:

```bash
turkman uninstall
```



## Kullanım 
Turkman'ı kullanmak için:

```bash
turkman <komut>
```
Yardım için:

```bash
turkman -h
```
Türkçe yardım için:

```bash
turkman -y
```

Örnek kullanım:

```bash
turkman brave-browser # Bu komut `brave-browser` uygulamasının man dosyasını Türkçe görüntüler.
```

### Görseller
Yakında...



## Lisans
Bu proje GPL3 ile lisanlanmıştır.Daha fazla bilgi için [LICENSE](./LICENSE) dosyasına bakabilirsin.
