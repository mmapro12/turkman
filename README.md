<div align="right">

🇹🇷 [Türkçe](README.md) | [English](README.en.md)

</div>

# Turkman - Linux için Türkçe Man Sayfaları

<div align="center">

<img src="./images/banner.png" width="700"/>

[![Version](https://img.shields.io/badge/version-0.8.0-blue.svg)](https://github.com/mmapro12/turkman/releases)
[![License](https://img.shields.io/badge/license-GPL--3.0-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-yellow.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-linux-lightgrey.svg)](https://github.com/mmapro12/turkman)

**Linux komutlarının man sayfalarını Türkçeye çevirir ve ana dilinizde sistem dokümantasyonuna erişmenizi sağlar.**

[🚀 Hızlı Kurulum](#-hızlı-kurulum) • [📖 Kullanım](#-kullanım) • [🤝 Katkıda Bulun](#-katkıda-bulunma) • [📚 Dokümantasyon](#-dokümantasyon)

</div>

---

## ✨ Özellikler

🌐 **Çoklu Kaynak Desteği** - Yerel man sayfaları, SQLite veritabanı ve GitHub deposundan çeviriler  
📊 **Akıllı Önbellekleme** - Hızlı erişim için SQLite tabanlı yerel önbellek  
🔄 **Otomatik Güncelleme** - GitHub deposundan güncel çevirileri otomatik senkronizasyon  
🎯 **Akıllı Arama** - Yerel → Veritabanı → GitHub sıralamasıyla optimize edilmiş arama  
🖥️ **Modern CLI** - Typer tabanlı kullanıcı dostu komut satırı arayüzü  
⚡ **Hızlı ve Hafif** - Minimal sistem kaynağı kullanımı

---

## 🚀 Hızlı Kurulum

### 📦 APT ile Kurulum (stable)

Ubuntu(24+), ZorinOS, Pardus gibi dağıtımlar kullanıyorsanız aşağıdaki test edilmiş .deb'i indirebilirsiniz:

```bash
# .deb paketini indirin
curl -L -o turkman_0.8.0_all.deb https://github.com/mmapro12/turkman/releases/latest/download/turkman_0.8.0_all.deb

sudo dpkg -i turkman_*_all.deb # hata verebilir aldırış etmeyin sonraki adıma geçin:
sudo apt install -f  # Bağımlılıkları çözün
turkman db sync # Veritabanını güncelleyin
```

### 🔧 Script ile Kurulum (dev)

Yukarıdaki .deb ile problem yaşıyorsanız aşağıdaki script ile sisteminize uygun bir .deb oluşturup yükleyebilirsiniz. Aynı zamanda bu script ile herhangi bir dağıtımda turkman'ı kurabilirsiniz:

```bash
git clone https://github.com/mmapro12/turkman.git
cd turkman 
python3 -m venv venv 
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
chmod +x install.sh
./install.sh
cd ..
rm -rf turkman
```

### 📋 Sistem Gereksinimleri

- **İşletim Sistemi**: Tüm Linux işletim sistemleri desteklidir.
- **Python**: 3.10 veya üzeri
- **Bağımlılıklar**: `manpages-tr`, `curl`, `python3`, `python3-pip`
- Turkman'ı install.sh script'tinden indiriyorsanız manpages-tr'ı indirmenize gerek yok. Otomatikmen kurulur.

Tüm bağımlılıkları indirmek için:
```bash
sudo apt update
sudo apt install python3 python3-pip curl manpages-tr
```

---

## 📖 Kullanım

### 🎯 Temel Komutlar

```bash
# Herhangi bir komutun Türkçe man sayfasını görüntüle
turkman ls
turkman clear

# Sürüm bilgisini kontrol et
turkman version

# Çeviri veritabanını güncelle
turkman db sync
```

### 🔍 Çalışma Prensibi

Turkman, bir komut için çeviri ararken şu **sıralamayı** takip eder:

```
1️⃣ Yerel Tüürkçe Man Sayfaları (/usr/share/man/tr/)
    ↓ (Bulunamadıysa)
2️⃣ Yerel SQLite Veritabanı (~/.turkmandb/)
    ↓ (Bulunamadıysa)  
3️⃣ Yapay zeka ile çevirme (Geliştirme aşamasında)
    ↓ (Yapılamazsa)
4️⃣ Orijinall İngilizce Man Sayfası (Yönlendirme)
```

### 📊 Komut Referansı

| Komut | Açıklama |
|-------|----------|
| `turkman <komut>` | Belirtilen komutun Türkçe man sayfasını göster |
| `turkman version` | Sürüm bilgilerini göster |
| `turkman update` | Turkman'ı güncelle |
| `turkman db init` | Veritabanını oluştur |
| `turkman db sync` | Çevirileri senkronize et |
| `turkman uninstall` | Turkman'ı kaldır |
| `turkman --help` | Yardım menüsünü göster |

---

## 🛠️ Gelişmiş Kullanım

### 🔄 Veritabanı Yönetimi

```bash
# Veritabanını sıfırla ve yeniden başlat
rm -rf ~/.turkmandb
turkman db init
turkman db sync
```

### 🌐 Çevrimdışı Kullanım

Turkman, çevirileri yerel olarak önbelleğe aldığından internet bağlantısı olmadan da çalışabilir:

```bash
# İlk seferinde çevirileri indir
turkman db sync

# Artık çevrimdışı kullanabilirsiniz
turkman ani-cli  # Yerel önbellekten gösterir
```

---

## 🏗️ Proje Mimarisi

### 📊 Sistem Mimarisi

```mermaid
graph TD
    A[Kullanıcı] -->|turkman ls| B[Turkman CLI]
    B --> C{Çeviri Var mı?}
    C -->|Evet| D[Yerel Man Sayfaları]
    C -->|Hayır| E[SQLite Veritabanı]
    E --> F{DB'de Var mı?}
    F -->|Evet| G[Çeviriyi Göster]
    F -->|Hayır| H[GitHub Deposu]
    H --> I{GitHub'da Var mı?}
    I -->|Evet| J[İndir ve Göster]
    I -->|Hayır| K[Orijinal Man]
    
    D --> G
    J --> L[DB'ye Kaydet]
    L --> G
```

### 🗂️ Proje Yapısı

```
turkman/
├── src/turkman/
│   ├── __init__.py
│   ├── turkman.py         # Ana CLI uygulaması
│   ├── db.py              # Veritabanı yönetimi
│   ├── utils.py           # Yardımcı fonksiyonlar
│   └── version.py         # Sürüm bilgisi
├── build_deb.sh           # .deb paketi oluşturma
├── build_bin.sh           # bin dosyasını oluşturma
├── install.sh             # .deb paketi oluşturma ve indirme
├── setup.py               # Python paketi yapılandırması
├── README.md              # Bu dosya
├── version.txt            # Sürüm bilgisi
└── LICENSE                # GPL-3.0 lisansı
```

---

## 🤝 Katkıda Bulunma

### 🎯 Katkı Türleri

- 🌍 **Yeni Çeviriler**: Man sayfalarını Türkçeye çevirin
- 🔧 **Hata Düzeltmeleri**: Mevcut sorunları çözün  
- ⚡ **Özellik Geliştirme**: Yeni fonksiyonlar ekleyin
- 📚 **Dokümantasyon**: Belgeleri iyileştirin
- 🐛 **Hata Raporlama**: Sorunları bildirin

### 📝 Çeviri Katkısı

1. **Turkmandb deposunu fork edin**: [github.com/mmapro12/turkmandb](https://github.com/mmapro12/turkmandb)

2. **Yeni çeviri ekleyin**:
```bash
cd turkmandb/pages/
# Man formatında çeviri yazın
echo "MAN_SAYFASI_İÇERİĞİ" > yeni_komut
```

3. **Çeviri listesini güncelleyin**:
```bash
echo "yeni_komut" >> ../pages.txt
```

4. **Pull request gönderin**

### 💻 Kod Katkısı

```bash
# Projeyi fork edin ve klonlayın
git clone https://github.com/mmapro12/turkman.git
cd turkman

# Geliştirme ortamını kurun
python -m venv venv
source venv/bin/activate
pip install -e .
pip install -r requirements.txt

# Değişikliklerinizi yapın ve test edin
python -m turkman.turkman ls

# Commit edin ve push edin
git add .
git commit -m "feat: yeni özellik eklendi"
git push origin main
```

---

## 🔧 Sorun Giderme

### ❗ Yaygın Problemler

#### "Komut bulunamadı" Hatası
```bash
# Komutun sistem üzerinde olup olmadığını kontrol edin
which komut_adı
man komut_adı
```

#### "Çeviri bulunamadı" Hatası
```bash
# Veritabanını güncelleyin
turkman db sync

# Yerel Türkçe man sayfalarını kontrol edin
man -L tr komut_adı
```

#### Veritabanı Sorunları
```bash
# Veritabanını sıfırlayın
rm -rf ~/.turkmandb
turkman db init
turkman db sync
```

### 📞 Destek

Sorunlarınız devam ederse:
- 🐛 **GitHub Issues**: [Sorun bildir](https://github.com/mmapro12/turkman/issues)

---


## 🎯 Gelecek Planları

- 🤖 **AI Destekli Çeviri**: AI tabanlı otomatik çeviri sistemi
- 📱 **GUI Arayüzü**: Masaüstü uygulaması geliştirme
- 📖 **Python Dokümantasyonu**: Python kütüphanesi dokümantasyon desteği

---

## 📄 Lisans

Bu proje [GPL-3.0](LICENSE) lisansı altında lisanslanmıştır.

---

## 🔗 Bağlantılar

<div align="center">

[![GitHub](https://img.shields.io/badge/GitHub-turkman-black?logo=github)](https://github.com/mmapro12/turkman)
[![Çeviri Deposu](https://img.shields.io/badge/GitHub-turkmandb-green?logo=github)](https://github.com/mmapro12/turkmandb)
[![Releases](https://img.shields.io/badge/Releases-latest-blue?logo=github)](https://github.com/mmapro12/turkman/releases)
[![Issues](https://img.shields.io/badge/Issues-report-red?logo=github)](https://github.com/mmapro12/turkman/issues)

</div>

---

## 🙏 Teşekkürler

- 🌟 **Katkıda Bulunanlar**: Tüm çevirmenlere ve geliştiricilere teşekkürler
- 📖 **Topluluk**: Linux Türkiye topluluğuna destekleri için teşekkürler
- 🛠️ **Araçlar**: Python, SQLite, GitHub ve açık kaynak ekosisteme teşekkürler



*Sevgi ile Maraş'ta yapıldı.* 
