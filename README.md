
# Turkman: Linux için Türkçe Man sayfaları çevirisi ve zenginleştirme uygulaması

Windows 10'un desteğinin sona ermesiyle, Windows 11'e geçiş yapamayan birçok kullanıcının Linuxa geçişi zor olacakken, Turkman bu geçişi kolaylaştırmak amacıyla tasarlanmıştır. Uygulama, Linux komutlarının man sayfalarını Türkçeye çevirir ve zenginleştirir. Turkman, Türkçe içerik eksikliğini gidererek, Linux kullanıcıları için daha erişilebilir bir deneyim sunmayı hedefler.




## Kurulum

Not: Turkman şimdilik sadece Debian tabanlı distrolarda çalışmaktadır.

Pojeyi $HOME (cd ~)'da indirmenizi tavsiye ederiz. 
Turkman'ı indirmek için:

```bash
git clone https://github.com/mmapro12/turkman.git
cd turkman
chmod +x install.sh turkman.py
./install.sh
```
Not: İndirdikten sonra lütfen "turkman" dizinini silmeyiniz!

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
turkman turkman
```

## Güncelleme
Turkman'ı güncellemek için(İlk olarak turkman'ın bulunduğu dizine gidiniz):
```bash
chmod +x upadate.sh
turkman-update
```
## Kaldırma
Turkman'ı kaldırmak için(İlk olarak turkman'ın bulunduğu dizine gidiniz):
```bash
chmod +x uninstall.sh
turkman-uninstall
```
## Üzerinde çalıştıklarımız (TODO List)

- Yapay zeka ile man dosyalarının çevirme (Test aşamasında)
- Rich ile man dosyalarına daha iyi bir görünüm verme (Kodu yazılıyor)
- less menüsünü Türkçeye çevirme (Çeviriliyor)
- Otomatik güncelleme sistemi (Son adımlar)
- Lokalden git reposuna çevrilmiş man dosyasını ekleme (Plan aşamasında)
- Turkman'ı tüm distrolarla uyumlu yapmak (Plan aşamasında)
- Genel düzenleme(mna sayfası, komutlar, genel dosyalar vb.)
- "Nasıl çalışır?" sayfası
