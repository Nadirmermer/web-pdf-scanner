import os
import subprocess
import shutil
import sys

def main():
    print("Ekran Tarayıcı Derleme Aracı")
    print("-" * 30)
    
    # Gerekli kütüphanelerin yüklü olduğunu kontrol et
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller yüklü değil. Yükleniyor...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Önceki derleme klasörlerini temizle
    print("Önceki derleme dosyaları temizleniyor...")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    # İkon dosyasının varlığını kontrol et
    icon_path = "icon.ico"
    icon_param = []
    if os.path.exists(icon_path):
        icon_param = [f"--icon={icon_path}", f"--add-data={icon_path};."]
    
    # PyInstaller ile uygulamayı derle
    print("Uygulama derleniyor...")
    cmd = [
        "pyinstaller",
        "--name=Ekran_Tarayici",
        "--onefile",
        "--windowed",
        "ekran_tarayici.py"
    ]
    
    # İkon parametresini ekle (varsa)
    if icon_param:
        cmd.extend(icon_param)
        print("İkon dosyası bulundu ve eklendi.")
    else:
        print("İkon dosyası bulunamadı. İkonsuz derleniyor...")
    
    subprocess.check_call(cmd)
    
    # Derleme sonrası işlemler
    print("Derleme tamamlandı!")
    print(f"Çıktı dosyası: {os.path.abspath('dist/Ekran_Tarayici.exe')}")
    
    # screenshots klasörü oluştur
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")
        print("'screenshots' klasörü oluşturuldu. Uygulama ekran görüntülerini buraya ekleyebilirsiniz.")
    
    print("\nKullanım:")
    print("1. Uygulamayı çalıştırmak için: dist/Ekran_Tarayici.exe")
    print("2. Yayın için dist klasöründeki dosyaları paketleyebilirsiniz.")

if __name__ == "__main__":
    main() 