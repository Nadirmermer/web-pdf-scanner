import os
import zipfile
import shutil
from datetime import datetime

def create_release_zip():
    """GitHub Release için gerekli dosyaları içeren ZIP oluşturur"""
    print("Ekran Tarayıcı Release ZIP Oluşturucu")
    print("-" * 40)
    
    # Sürüm numarası için tarih formatı
    tarih = datetime.now().strftime("%Y%m%d")
    surum = f"v1.0.0-{tarih}"
    
    # ZIP dosya adı
    zip_adi = f"Ekran_Tarayici_{surum}.zip"
    
    # Dist klasörü kontrolü
    if not os.path.exists("dist") or not os.path.exists("dist/Ekran_Tarayici.exe"):
        print("HATA: dist klasöründe Ekran_Tarayici.exe bulunamadı.")
        print("Lütfen önce 'python build.py' komutunu çalıştırarak uygulamayı derleyin.")
        return False
    
    print(f"Sürüm: {surum}")
    print(f"ZIP dosyası: {zip_adi}")
    
    try:
        # Geçici klasör oluştur
        temp_klasor = "temp_release"
        if os.path.exists(temp_klasor):
            shutil.rmtree(temp_klasor)
        os.makedirs(temp_klasor)
        
        # EXE dosyasını kopyala
        shutil.copy("dist/Ekran_Tarayici.exe", f"{temp_klasor}/Ekran_Tarayici.exe")
        
        # README ve LICENSE dosyalarını kopyala
        shutil.copy("README.md", f"{temp_klasor}/README.md")
        shutil.copy("LICENSE", f"{temp_klasor}/LICENSE")
        
        # Icon varsa kopyala
        if os.path.exists("icon.ico"):
            shutil.copy("icon.ico", f"{temp_klasor}/icon.ico")
        
        # Screenshots klasörü varsa kopyala
        if os.path.exists("screenshots"):
            shutil.copytree("screenshots", f"{temp_klasor}/screenshots")
        else:
            # Screenshots klasörünü oluştur
            os.makedirs(f"{temp_klasor}/screenshots")
            print("Not: 'screenshots' klasörü bulunamadı, boş klasör eklendi.")
            print("Lütfen uygulamanın ekran görüntüsünü ekleyin.")
        
        # ZIP dosyasını oluştur
        with zipfile.ZipFile(zip_adi, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(temp_klasor):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(
                        file_path, 
                        os.path.relpath(file_path, temp_klasor)
                    )
        
        # Geçici klasörü temizle
        shutil.rmtree(temp_klasor)
        
        print(f"\nBaşarılı! '{zip_adi}' dosyası oluşturuldu.")
        print(f"Boyut: {os.path.getsize(zip_adi) / (1024*1024):.2f} MB")
        print("\nBu ZIP dosyasını GitHub Release olarak yükleyebilirsiniz.")
        return True
        
    except Exception as e:
        print(f"Hata: {e}")
        return False

if __name__ == "__main__":
    create_release_zip() 