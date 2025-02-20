
# Turkman (Linux için Türkçe Man sayfaları çevirisi ve zenginleştirme uygulaması)

Windows 10un desteğinin sona ermesiyle, Windows 11e geçiş yapamayan birçok kullanıcının Linuxa geçişi zor olacakken, Turkman bu geçişi kolaylaştırmak amacıyla tasarlanmıştır. Uygulama, Linux komutlarının man sayfalarını Türkçeye çevirir ve zenginleştirir. Turkman, Türkçe içerik eksikliğini gidererek, Linux kullanıcıları için daha erişilebilir bir deneyim sunmayı hedefler.




## Kurulum

Not: Turkman şimdilik sadece Debian tabanlı distrolarda çalışmaktadır.

Pojeyi $HOME (cd ~)'da indirmenizi tavsiye ederiz. 
Turkmanı indirmek için:

```bash
git clone https://github.com/mmapro12/turkman.git
cd turkman
chmod +x install.sh turkman.py
./install.sh
```
Not: İndirdikten sonra lütfen "turkman" dizinini silmeyiniz!

Turkmanı kullanmak için:
```bash
turkman <komut>
```
Yardım için:
```bash
turkman -h
```

## Güncelleme
Turkmanı güncellemek için(İlk olarak turkman'ın bulunduğu dizine gidiniz):
```bash
chmod +x upadate.sh
turkman-update
```
## Kaldırma
Turkmanı kaldırmak için(İlk olarak turkman'ın bulunduğu dizine gidiniz):
```bash
chmod +x uninstall.sh
turkman-uninstall
```
## Üzerinde çalıştıklarımız

- Yapay zeka ile man dosyalarının çevirme (Test aşamasında)
- Rich ile man dosyalarına daha iyi bir görünüm verme (Kodu yazılıyor)
- less menüsünü Türkçeye çevirme (Çeviriliyor)
- Otomatik güncelleme sistemi (Son adımlar)
- Lokalden git reposuna çevrilmiş man dosyasını ekleme (Plan aşamasında)
