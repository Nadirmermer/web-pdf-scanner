# GitHub'a Yükleme Adımları

Bu belgede "Ekran Tarayıcı" uygulamasını adım adım GitHub'a nasıl yükleyeceğinizi bulabilirsiniz.

## 1. GitHub Hesabınızda Yeni Bir Depo (Repository) Oluşturun

1. GitHub hesabınıza giriş yapın
2. Sağ üst köşedeki "+" simgesine tıklayın ve "New repository" (Yeni depo) seçeneğini seçin
3. Aşağıdaki bilgileri girin:
   - Repository name (Depo adı): `ekran-tarayici`
   - Description (Açıklama): `Web sayfalarını tarayıp PDF'e dönüştüren kullanıcı dostu masaüstü uygulaması`
   - Erişim türü: "Public" (Herkes erişebilir)
   - README dosyası ekleme seçeneğini işaretlemeyin (zaten bir README dosyamız var)
4. "Create repository" (Depo oluştur) düğmesine tıklayın

## 2. Yerel Deponuzu Hazırlayın

Terminal veya Komut İstemi'ni açın ve şu komutları çalıştırın:

```bash
# Mevcut klasörü git deposu olarak başlatın
git init

# Tüm dosyaları ekleyin
git add .

# İlk commit'i oluşturun
git commit -m "İlk sürüm: Ekran Tarayıcı uygulaması"
```

## 3. GitHub Deponuza Bağlanın ve Dosyaları Yükleyin

GitHub'da oluşturduğunuz deponun sayfasında "Code" (Kod) düğmesine tıklayarak HTTPS URL'sini kopyalayın, sonra şu komutları çalıştırın:

```bash
# GitHub deponuzu uzak depo (remote) olarak ekleyin
git remote add origin https://github.com/KULLANICI_ADINIZ/ekran-tarayici.git

# Dosyalarınızı GitHub'a gönderin
git push -u origin master
```

Not: `KULLANICI_ADINIZ` yerine kendi GitHub kullanıcı adınızı yazın.

## 4. Sürüm (Release) Oluşturun

1. GitHub'da deponuza gidin
2. "Releases" (Sürümler) sekmesine tıklayın
3. "Create a new release" (Yeni bir sürüm oluştur) düğmesine tıklayın
4. Bilgileri doldurun:
   - Tag version: `v1.0.0`
   - Release title: `Ekran Tarayıcı v1.0.0`
   - Açıklama: Uygulamanızın özelliklerini listeleyebilirsiniz
5. Derlenmiş uygulamanızı içeren ZIP dosyasını yükleyin (dist klasöründeki Ekran_Tarayici.exe dosyasını ZIP olarak sıkıştırabilirsiniz)
6. "Publish release" (Sürümü yayınla) düğmesine tıklayın

## 5. Yayınlama Sonrası

Artık herkes README.md dosyasında belirtilen bağlantıyı kullanarak uygulamanızı indirebilir.

**Not:** GitHub README.md dosyasında bulunan `https://github.com/KULLANICI_ADINIZ/ekran-tarayici/releases` bağlantısını kendi kullanıcı adınızla güncellemeyi unutmayın. 