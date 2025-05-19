
# Turkman: Linux için Türkçe Man sayfaları çevirisi ve zenginleştirme uygulaması

Turkman, Linux komutlarının man sayfalarını Türkçeye çevirir ve db'ye kaydeder. Türkçe içerik eksikliğini gidererek, Linux kullanıcıları için daha erişilebilir bir deneyim sunmayı hedefliyoruz.



## Güncellemeler 

### Son Eklenenler (v0.4.x) -> 20.05.2025 

- Turkmandb yeniden SQL sistemiyle yazıldı.
- Güncelleme önerme eklendi.
- Hata düzeltmeleri yapıldı.

### Üzerinde çalıştıklarımız

- Yapay zeka ile man dosyalarının çevirme sistemi.
- Detaylı dokümatasyon.
- Python dokümantasyonunu turkman'a ekleme.



## Kurulum

Not: Turkman şuan sadece Debian tabanlı dağıtımlarda (Pardus, Ubuntu, Linux Mint vb.) çalışmaktadır.

### Gereksinimler

- [manpages-tr](https://github.com/TLBP/manpages-tr/)
- `git`
- `curl`
- `python3`

Tüm gereksinimleri indirmek için:
```bash
sudo apt install manpages-tr git curl python3 python3-pip
```

### İndirme

Turkman'ı indirmek için:

```bash
curl -L https://raw.githubusercontent.com/mmapro12/turkman/refs/heads/main/install.sh | sudo bash
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
Türkçe yardım için:

```bash
turkman --help
```

Örnek kullanım:

```bash
turkman manpage brave-browser # Bu komut `brave-browser` uygulamasının man dosyasını Türkçe görüntüler.
```

### Görseller
Yakında...



## Lisans
Bu proje GPL3 ile lisanlanmıştır.Daha fazla bilgi için [LICENSE](./LICENSE) dosyasına bakabilirsiniz.

