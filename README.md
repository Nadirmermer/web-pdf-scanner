# Ekran Tarayıcı

Web sayfalarını tarayıp PDF dosyasına dönüştüren kullanıcı dostu bir masaüstü uygulaması.

![Ekran Tarayıcı](screenshots/ekran_tarayici.png)

## Özellikler

- **Nobel Modu**: Uzun sayfaları kaydırarak tarar ve birleştirir
- **Turcademy Modu**: Her sayfayı tek görüntü olarak alır
- Tarama alanını ve sayfa geçiş noktasını görsel olarak seçme
- İşlem sırasında taramayı duraklatma/devam ettirme
- Hedef sayfa sayısı belirleme ve otomatik durdurma
- Tarama sonrası otomatik PDF oluşturma
- Kitapları yönetme (ekleme, silme)
- İlerleme otomatik kaydedilir, daha sonra kaldığınız yerden devam edebilirsiniz

## Kurulum

### Hazır Derlenmiş Sürüm

1. [Releases](https://github.com/KULLANICI_ADINIZ/ekran-tarayici/releases) sayfasından son sürümü indirin
2. İndirilen ZIP dosyasını çıkarın ve `Ekran_Tarayici.exe` dosyasını çalıştırın

### Kaynak Koddan Çalıştırma

Gereksinimler:
- Python 3.7 veya üzeri

```bash
# Gerekli kütüphaneleri yükleyin
pip install -r requirements.txt

# Uygulamayı çalıştırın
python ekran_tarayici.py
```

## Kullanım

1. **Kitap Seçimi**: Yeni bir kitap oluşturun veya mevcut birini seçin
2. **Tarama Modu**: Nobel veya Turcademy modunu seçin
3. **Tarama Ayarları**: Tarama alanını ve sayfa geçiş noktasını belirleyin
4. **Sayfa Bilgisi**: Başlangıç ve hedef sayfa sayısını ayarlayın
5. **Tarama Kontrol**: Taramayı başlatın ve kontrol paneli ile yönetin

### Kısayollar

- **ESC**: Taramayı durdur

## Ekran Görüntüleri

Uygulama ekran görüntüsünü görmek için:

1. Uygulamayı çalıştırın ve ekran görüntüsü alın
2. Görüntüyü `screenshots` klasörüne `ekran_tarayici.png` adıyla kaydedin

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylı bilgi için [LICENSE](LICENSE) dosyasına bakınız. 