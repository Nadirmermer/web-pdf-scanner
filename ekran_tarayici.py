import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyautogui
import time
import keyboard
import os
from PIL import Image, ImageTk, ImageGrab
import threading
from PyPDF2 import PdfWriter, PdfReader
from io import BytesIO
import json
import gc

class EkranTarayici:
    def __init__(self, root):
        self.root = root
        self.root.title("Ekran Tarayıcı")
        # Minimum pencere boyutu belirle
        self.root.minsize(600, 500)
        # Dinamik pencere boyutu
        self.root.geometry("800x700")
        # Pencerenin yeniden boyutlandırılmasına izin ver
        self.root.resizable(True, True)
        self.root.attributes('-topmost', True)
        
        # Program ikonu
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass  # İkon yoksa geç
        
        # Ana değişkenler
        self.tarama_alani = {'x1': 0, 'y1': 0, 'x2': 500, 'y2': 800}  # Varsayılan tarama alanı
        self.tiklanacak_nokta = {'x': 500, 'y': 500}  # Varsayılan tıklama noktası
        self.devam_ediyor = False
        self.sayfa_no = 1
        self.toplam_sayfa = 1
        self.hedef_sayfa_sayisi = 300  # Varsayılan hedef sayfa sayısı
        self.sayfa_parcalari = []
        self.son_goruntu = None
        self.sayfa_sonu_bekleme_suresi = 0.3
        self.ayni_sayfa_sayisi = 0
        self.kayit_klasoru = os.path.join(os.path.expanduser("~"), "Ekran_Tarama")
        self.aktif_kitap = ""  # Aktif kitap değişkeni
        self.tarama_modu = "Nobel"  # Varsayılan tarama modu: "Nobel" veya "Turcademy"
        self.otomatik_pdf = tk.BooleanVar(value=False)  # Tarama sonrası otomatik PDF oluşturma
        self.kontrol_panel = None  # Kontrol paneli penceresi
        self.tarama_duraklatildi = False  # Tarama duraklatıldı mı?
        
        # Sabit parametreler (kullanıcıdan alınmayacak)
        self.max_bekleme_suresi = 3       # Maksimum yüklenme süresi (3 saniye)
        self.sayfa_gecis_gecikmesi = 0.8  # Sayfa geçiş gecikmesi (0.8 saniye)
        
        # Turcademy modu için özel parametreler
        self.turcademy_gecis_carpani = 1.2  # Turcademy için gecikme çarpanı (1.2)
        
        # Kitaplar klasörünü oluştur
        self.kitaplar_klasoru = os.path.join(self.kayit_klasoru, "Kitaplar")
        if not os.path.exists(self.kitaplar_klasoru):
            os.makedirs(self.kitaplar_klasoru)
        
        # Kayıt klasörünü oluştur
        if not os.path.exists(self.kayit_klasoru):
            os.makedirs(self.kayit_klasoru)
        
        # Yapılandırma dosyası
        self.config_dosyasi = os.path.join(self.kayit_klasoru, "ayarlar.json")
        self.ayarlari_yukle()
        
        # Tema ve stil ayarları
        self.set_styles()
        
        # Arayüz oluştur
        self.create_widgets()
        
        # Beklenmedik kapanmalara karşı önlem
        self.root.protocol("WM_DELETE_WINDOW", self.on_kapat)
        
        # Kullanılabilir kitapları listele
        self.kitaplari_listele()
        
        # Başlangıçta bilgi mesajı göster
        self.root.after(500, self.bilgi_kontrolu)
    
    def set_styles(self):
        """Uygulamanın genel tema ve stil ayarlarını yapar"""
        style = ttk.Style()
        
        # Ana buton stili
        style.configure('Accent.TButton', font=('Segoe UI', 10, 'bold'))
        # İkincil buton stili
        style.configure('Secondary.TButton', font=('Segoe UI', 9))
        # Bilgi etiketi stili
        style.configure('Info.TLabel', font=('Segoe UI', 9), foreground='#555555')
        # Başlık stili
        style.configure('Title.TLabel', font=('Segoe UI', 11, 'bold'))
        # Adım etiketi stili
        style.configure('Step.TLabel', font=('Segoe UI', 9, 'bold'), foreground='#3366CC')
        # Büyük aksiyon butonu
        style.configure('BigAction.TButton', font=('Segoe UI', 12, 'bold'), padding=8)
    
    def on_kapat(self):
        """Uygulama kapatılırken çağrılır"""
        if self.devam_ediyor:
            self.taramayi_durdur()
        self.ilerleme_kaydet()
        self.root.destroy()
    
    def ilerleme_yukle(self):
        """Önceki ilerlemeyi yükler"""
        try:
            if os.path.exists(self.ilerleme_dosyasi):
                with open(self.ilerleme_dosyasi, 'r') as f:
                    ilerleme = json.load(f)
                    self.toplam_sayfa = ilerleme.get('toplam_sayfa', 1)
                    
                    # Kaydedilmiş son sayfa numarasını kontrol et
                    kayitli_sayfa = ilerleme.get('son_sayfa', 1)
                    if kayitli_sayfa > 1:
                        # En son sayfa numarasını ve toplam sayfa bilgisini güncelle
                        self.sayfa_no = kayitli_sayfa + 1  # Bir sonraki sayfadan başla
                        self.log_ekle(f"Kaydedilmiş ilerleme bulundu. Son işlenen sayfa: {kayitli_sayfa}, Sonraki sayfa: {self.sayfa_no}")
                    else:
                        self.sayfa_no = 1
                    
                    # Sayfa dosyalarını kontrol et
                    try:
                        sayfa_dosyalari = [f for f in os.listdir(self.kayit_klasoru) 
                                        if f.startswith("sayfa_") and f.endswith(".png")]
                        
                        if sayfa_dosyalari:
                            # En büyük sayfa numarasını bul
                            try:
                                en_buyuk_sayfa = max([int(os.path.basename(f).split('_')[1].split('.')[0]) 
                                                   for f in sayfa_dosyalari])
                                # İlerleme dosyasındaki son sayfa ile gerçek dosya durumunu karşılaştır
                                if en_buyuk_sayfa >= self.sayfa_no:
                                    self.sayfa_no = en_buyuk_sayfa + 1  # Bir sonraki sayfadan başla
                                    self.log_ekle(f"En son kaydedilen sayfa: {en_buyuk_sayfa}, Sonraki sayfa: {self.sayfa_no}")
                            except Exception as e:
                                self.log_ekle(f"Dosya kontrolünde hata: {e}")
                    except Exception as e:
                        self.log_ekle(f"Klasör okuma hatası: {e}")
                
                # Sayfa numarası alanını güncelle
                if hasattr(self, 'baslangic_sayfa_entry'):
                    self.baslangic_sayfa_entry.delete(0, tk.END)
                    self.baslangic_sayfa_entry.insert(0, str(self.sayfa_no))
                
                # Sayfa bilgisi etiketlerini güncelle
                self.sayfa_bilgisi_guncelle()
                
        except Exception as e:
            self.log_ekle(f"İlerleme yüklenirken hata: {e}")
    
    def ilerleme_kaydet(self):
        """Mevcut ilerlemeyi kaydeder"""
        # Aktif kitap seçili değilse uyarı ver
        if not self.aktif_kitap:
            messagebox.showwarning("Uyarı", "Lütfen önce bir kitap seçin veya oluşturun.")
            return
            
        try:
            with open(self.ilerleme_dosyasi, 'w') as f:
                json.dump({
                    'son_sayfa': self.sayfa_no - 1,  # Son tamamlanan sayfa
                    'toplam_sayfa': self.toplam_sayfa,
                    'kitap_adi': self.aktif_kitap,
                    'tarih': time.strftime("%Y-%m-%d %H:%M:%S")
                }, f)
            self.log_ekle(f"İlerleme kaydedildi: {self.aktif_kitap} - {self.sayfa_no - 1}. sayfa")
        except Exception as e:
            self.log_ekle(f"İlerleme kaydedilirken hata: {e}")
    
    def ayarlari_yukle(self):
        try:
            if os.path.exists(self.config_dosyasi):
                with open(self.config_dosyasi, 'r') as f:
                    ayarlar = json.load(f)
                    self.tarama_alani = ayarlar.get('tarama_alani', self.tarama_alani)
                    self.tiklanacak_nokta = ayarlar.get('tiklanacak_nokta', self.tiklanacak_nokta)
                    self.sayfa_sonu_bekleme_suresi = ayarlar.get('sayfa_sonu_bekleme_suresi', self.sayfa_sonu_bekleme_suresi)
                    self.tarama_modu = ayarlar.get('tarama_modu', self.tarama_modu)
                    self.otomatik_pdf.set(ayarlar.get('otomatik_pdf', False))
                    self.hedef_sayfa_sayisi = ayarlar.get('hedef_sayfa_sayisi', self.hedef_sayfa_sayisi)
        except Exception as e:
            print(f"Ayarlar yüklenirken hata: {e}")
    
    def ayarlari_kaydet(self):
        try:
            with open(self.config_dosyasi, 'w') as f:
                json.dump({
                    'tarama_alani': self.tarama_alani,
                    'tiklanacak_nokta': self.tiklanacak_nokta,
                    'sayfa_sonu_bekleme_suresi': self.sayfa_sonu_bekleme_suresi,
                    'tarama_modu': self.tarama_modu,
                    'otomatik_pdf': self.otomatik_pdf.get(),
                    'hedef_sayfa_sayisi': self.hedef_sayfa_sayisi
                }, f)
        except Exception as e:
            print(f"Ayarlar kaydedilirken hata: {e}")
    
    def create_widgets(self):
        # Ana çerçeve - pencere yeniden boyutlandırıldığında büyüyecek şekilde
        main_frame = ttk.Frame(self.root, padding="5")  # 10 yerine 5 padding
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Ana içerik frame
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tarama sekmesini yapılandır (grid layout kullanarak daha iyi yerleşim)
        content_frame.columnconfigure(0, weight=1)  # Sütunun genişlemesine izin ver
        content_frame.rowconfigure(4, weight=1)     # Log alanının genişlemesine izin ver
        
        # ======= ADIM 1: KİTAP SEÇİMİ =======
        kitap_frame = ttk.LabelFrame(content_frame, text="🔷 1. Adım: Kitap Seçimi", padding="5")  # 10 yerine 5 padding
        kitap_frame.grid(row=0, column=0, sticky="ew", pady=3)  # 5 yerine 3 padding
        kitap_frame.columnconfigure(1, weight=1)
        
        # Kitap seçim kontrollerini bir satır içinde düzenle
        kitap_sec_frame = ttk.Frame(kitap_frame)
        kitap_sec_frame.grid(row=0, column=0, sticky="ew", padx=3, pady=3)  # 5 yerine 3 padding
        kitap_sec_frame.columnconfigure(0, weight=1)
        
        # Kitap seçme combobox'ı
        self.kitap_combobox = ttk.Combobox(kitap_sec_frame, width=40, state="readonly")
        self.kitap_combobox.grid(row=0, column=0, padx=5, sticky="ew")
        self.kitap_combobox.bind("<<ComboboxSelected>>", lambda e: self.kitap_sec())
        
        # Butonları aynı satıra yerleştir
        ttk.Button(kitap_sec_frame, text="📚 Yeni Kitap", command=self.yeni_kitap_ekle,
                 style='Secondary.TButton').grid(row=0, column=1, padx=5)
                 
        # Kitap silme butonu ekle
        ttk.Button(kitap_sec_frame, text="🗑️ Kitabı Sil", command=self.kitap_sil,
                 style='Secondary.TButton').grid(row=0, column=2, padx=5)
                 
        self.pdf_button = ttk.Button(kitap_sec_frame, text="📄 PDF Oluştur", 
                                   command=self.secili_klasordeki_goruntuleri_birlestir,
                                   style='Secondary.TButton')
        self.pdf_button.grid(row=0, column=3, padx=5)
        self.pdf_button.grid_remove()  # Başlangıçta gizle
        
        # ======= ADIM 2: TARAMA MODU =======
        tarama_modu_frame = ttk.LabelFrame(content_frame, text="🔷 2. Adım: Tarama Modu Seçimi", padding="5")  # 10 yerine 5 padding
        tarama_modu_frame.grid(row=1, column=0, sticky="ew", pady=3)  # 5 yerine 3 padding
        
        # Tarama modları
        self.tarama_modu_var = tk.StringVar(value=self.tarama_modu)
        
        # Mod seçimine açıklayıcı ikonlar ekle
        modu_frame = ttk.Frame(tarama_modu_frame)
        modu_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Nobel modu (kaydırmalı sayfa tarama)
        nobel_frame = ttk.Frame(modu_frame)
        nobel_frame.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        nobel_rb = ttk.Radiobutton(nobel_frame, text="Nobel Modu", 
                                  value="Nobel", variable=self.tarama_modu_var,
                                  command=self.tarama_modu_degisti)
        nobel_rb.grid(row=0, column=0, sticky="w")
        ttk.Label(nobel_frame, text="📜 Sayfa kaydırmalı tarama", 
                 style='Info.TLabel').grid(row=1, column=0, sticky="w")
        
        # Turcademy modu (tam sayfa görüntü)
        turcademy_frame = ttk.Frame(modu_frame)
        turcademy_frame.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        turcademy_rb = ttk.Radiobutton(turcademy_frame, text="Turcademy Modu", 
                                      value="Turcademy", variable=self.tarama_modu_var,
                                      command=self.tarama_modu_degisti)
        turcademy_rb.grid(row=0, column=0, sticky="w")
        ttk.Label(turcademy_frame, text="📖 Tek sayfa görüntü tarama", 
                 style='Info.TLabel').grid(row=1, column=0, sticky="w")
        
        # ======= ADIM 3: AYARLAR =======
        ayarlar_frame = ttk.LabelFrame(content_frame, text="🔷 3. Adım: Tarama Ayarları", padding="5")  # 10 yerine 5 padding
        ayarlar_frame.grid(row=2, column=0, sticky="ew", pady=3)  # 5 yerine 3 padding
        ayarlar_frame.columnconfigure(0, weight=1)
        ayarlar_frame.columnconfigure(1, weight=1)
        
        # Tarama alanı ve sayfa geçiş noktası yan yana iki sütunda
        sol_frame = ttk.Frame(ayarlar_frame)
        sol_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Tarama Alanı Seçim Butonu
        alan_buton_frame = ttk.Frame(sol_frame)
        alan_buton_frame.grid(row=0, column=0, pady=5, sticky="w")
        
        ttk.Button(alan_buton_frame, text="📏 Tarama Alanı Seç", 
                  command=self.tarama_alani_sec, 
                  style='Accent.TButton').grid(row=0, column=0, padx=5)
        
        # Koordinat göstergesi
        self.koordinat_label = ttk.Label(sol_frame, 
                             text=f"Sol Üst: ({self.tarama_alani['x1']}, {self.tarama_alani['y1']}) - Sağ Alt: ({self.tarama_alani['x2']}, {self.tarama_alani['y2']})",
                             style='Info.TLabel')
        self.koordinat_label.grid(row=1, column=0, padx=5, pady=2, sticky="w")
        
        # Sağ taraf
        sag_frame = ttk.Frame(ayarlar_frame)
        sag_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Tıklama Noktası Seçim Butonu
        ttk.Button(sag_frame, text="👆 Sayfa Geçiş Noktası Seç", 
                  command=self.tikla_nokta_sec, 
                  style='Accent.TButton').grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Nokta koordinat göstergesi
        self.nokta_label = ttk.Label(sag_frame, 
                         text=f"Koordinat: ({self.tiklanacak_nokta['x']}, {self.tiklanacak_nokta['y']})",
                         style='Info.TLabel')
        self.nokta_label.grid(row=1, column=0, padx=5, pady=2, sticky="w")
        
        # ======= ADIM 4: SAYFA BİLGİSİ =======
        sayfa_frame = ttk.LabelFrame(content_frame, text="🔷 4. Adım: Sayfa Bilgisi", padding="5")  # 10 yerine 5 padding
        sayfa_frame.grid(row=3, column=0, sticky="ew", pady=3)  # 5 yerine 3 padding
        sayfa_frame.columnconfigure(1, weight=1)
        
        # Sayfa bilgileri tek satırda
        sayfa_bilgi_frame = ttk.Frame(sayfa_frame)
        sayfa_bilgi_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Başlangıç sayfa
        baslangic_frame = ttk.Frame(sayfa_bilgi_frame)
        baslangic_frame.grid(row=0, column=0, padx=10)
        
        ttk.Label(baslangic_frame, text="Başlangıç Sayfa:", 
                 style='Title.TLabel').grid(row=0, column=0, padx=5)
        
        self.baslangic_sayfa_var = tk.StringVar(value=str(self.sayfa_no))
        self.baslangic_sayfa_entry = ttk.Entry(baslangic_frame, textvariable=self.baslangic_sayfa_var, width=5)
        self.baslangic_sayfa_entry.grid(row=0, column=1, padx=5)
        self.baslangic_sayfa_entry.bind("<Return>", lambda e: self.baslangic_sayfasini_guncelle())
        
        ttk.Button(baslangic_frame, text="Ayarla", 
                  command=self.baslangic_sayfasini_guncelle, 
                  style='Secondary.TButton', width=5).grid(row=0, column=2, padx=5)
        
        # Aktif sayfa bilgisi
        sayfa_info_frame = ttk.Frame(sayfa_bilgi_frame)
        sayfa_info_frame.grid(row=0, column=1, padx=10)
        
        ttk.Label(sayfa_info_frame, text="Şu anki Sayfa:", 
                 style='Info.TLabel').grid(row=0, column=0, padx=5)
        self.sayfa_label = ttk.Label(sayfa_info_frame, text=str(self.sayfa_no), 
                                    style='Title.TLabel')
        self.sayfa_label.grid(row=0, column=1, padx=5)
        
        # Hedef sayfa sayısı
        hedef_frame = ttk.Frame(sayfa_bilgi_frame)
        hedef_frame.grid(row=0, column=2, padx=10)
        
        ttk.Label(hedef_frame, text="Hedef Sayfa Sayısı:", 
                style='Title.TLabel').grid(row=0, column=0, padx=5)
        
        self.hedef_sayfa_var = tk.StringVar(value=str(self.hedef_sayfa_sayisi))
        self.hedef_sayfa_entry = ttk.Entry(hedef_frame, textvariable=self.hedef_sayfa_var, width=5)
        self.hedef_sayfa_entry.grid(row=0, column=1, padx=5)
        self.hedef_sayfa_entry.bind("<Return>", lambda e: self.hedef_sayfasini_guncelle())
        
        ttk.Button(hedef_frame, text="Ayarla", 
                  command=self.hedef_sayfasini_guncelle, 
                  style='Secondary.TButton', width=5).grid(row=0, column=2, padx=5)
        
        ttk.Label(sayfa_info_frame, text="Toplam Sayfa:", 
                 style='Info.TLabel').grid(row=0, column=2, padx=5)
        self.toplam_sayfa_label = ttk.Label(sayfa_info_frame, text=str(self.toplam_sayfa), 
                                          style='Title.TLabel')
        self.toplam_sayfa_label.grid(row=0, column=3, padx=5)
        
        # Sayfa bilgisi çerçevesine bir de klasör bilgisi ekleyelim
        klasor_bilgi_frame = ttk.Frame(sayfa_frame)
        klasor_bilgi_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(klasor_bilgi_frame, text="Kayıt Klasörü:", 
                style='Info.TLabel').grid(row=0, column=0, padx=5, sticky="w")
        
        self.klasor_label = ttk.Label(klasor_bilgi_frame, text=self.kayit_klasoru, 
                                   style='Info.TLabel')
        self.klasor_label.grid(row=0, column=1, padx=5, sticky="w")
        
        # ======= ADIM 5: TARAMA KONTROL =======
        kontrol_frame = ttk.LabelFrame(content_frame, text="🔷 5. Adım: Tarama Kontrol", padding="5")  # 10 yerine 5 padding
        kontrol_frame.grid(row=4, column=0, sticky="ew", pady=3)  # 5 yerine 3 padding
        
        # Otomatik PDF seçeneği
        otomatik_pdf_frame = ttk.Frame(kontrol_frame)
        otomatik_pdf_frame.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(otomatik_pdf_frame, text="Tarama bittiğinde otomatik PDF oluştur", 
                      variable=self.otomatik_pdf, 
                      command=self.ayarlari_kaydet).pack(pady=5)
        
        buton_frame = ttk.Frame(kontrol_frame)
        buton_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Başlat/Durdur butonlarını daha görünür yap
        self.baslat_btn = ttk.Button(buton_frame, text="▶️ TARAMAYI BAŞLAT", 
                                    command=self.taramayi_baslat, 
                                    style='BigAction.TButton')
        self.baslat_btn.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        self.durdur_btn = ttk.Button(buton_frame, text="⏹️ TARAMAYI DURDUR", 
                                    command=self.taramayi_durdur, 
                                    style='BigAction.TButton', state=tk.DISABLED)
        self.durdur_btn.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        # Butonlara eşit genişlik ver
        buton_frame.columnconfigure(0, weight=1)
        buton_frame.columnconfigure(1, weight=1)
        
        # Kısayol bilgisi
        ttk.Label(kontrol_frame, text="Klavye kısayolu: Taramayı durdurmak için ESC tuşuna basın", 
                 style='Info.TLabel').pack(pady=5)
        
        # ======= İŞLEM GÜNLÜĞÜ =======
        log_frame = ttk.LabelFrame(content_frame, text="İşlem Günlüğü", padding="3")  # 5 yerine 3 padding
        log_frame.grid(row=5, column=0, sticky="nsew", pady=3)  # 5 yerine 3 padding
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        content_frame.rowconfigure(5, weight=1)  # Log alanının yüksekliğini de genişlemeye izin ver
        
        # Log metni - scrollbar eklenmiş
        log_container = ttk.Frame(log_frame)
        log_container.grid(row=0, column=0, sticky="nsew")
        log_container.columnconfigure(0, weight=1)
        log_container.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(log_container, height=8, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        self.log_text.config(state=tk.DISABLED)
        
        log_scrollbar = ttk.Scrollbar(log_container, orient="vertical", command=self.log_text.yview)
        log_scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        # Klavye kısayolları
        self.root.bind("<Escape>", lambda e: self.taramayi_durdur())
        
        # Yardım etiketi
        yardim_text = "Bu program, web sayfalarını otomatik olarak tarayıp PDF dosyasına dönüştürür.\n"
        yardim_text += "Her adımı yukarıdan aşağıya sırayla takip edin."
        
        ttk.Label(content_frame, text=yardim_text, style='Info.TLabel', 
                 wraplength=600, justify='center').grid(row=6, column=0, pady=5)
    
    def log_ekle(self, mesaj):
        try:
            if hasattr(self, 'log_text'):
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, f"{mesaj}\n")
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
            else:
                print(f"Log: {mesaj}")
        except Exception as e:
            print(f"Log eklenirken hata: {e} - Mesaj: {mesaj}")
        
    def tarama_alani_sec(self):
        self.root.iconify()  # Pencereyi simge durumuna küçült
        self.log_ekle("Lütfen taramak istediğiniz alanı seçin. 'Esc' tuşuna basarak iptal edebilirsiniz.")
        
        time.sleep(0.5)  # Kullanıcıya hazırlanma süresi ver
        
        try:
            region = pyautogui.screenshot()
            region_tk = ImageTk.PhotoImage(region)
            
            select_window = tk.Toplevel(self.root)
            select_window.attributes('-fullscreen', True)
            select_window.attributes('-topmost', True)
            
            canvas = tk.Canvas(select_window, cursor="cross")
            canvas.pack(fill=tk.BOTH, expand=True)
            
            canvas.create_image(0, 0, image=region_tk, anchor=tk.NW)
            
            rect_id = None
            start_x, start_y = 0, 0
            
            def on_mouse_down(event):
                nonlocal start_x, start_y, rect_id
                start_x, start_y = event.x, event.y
                
                if rect_id:
                    canvas.delete(rect_id)
                
                rect_id = canvas.create_rectangle(
                    start_x, start_y, start_x, start_y,
                    outline='red', width=2
                )
            
            def on_mouse_move(event):
                nonlocal rect_id
                if rect_id:
                    canvas.coords(rect_id, start_x, start_y, event.x, event.y)
            
            def on_mouse_up(event):
                nonlocal start_x, start_y
                
                end_x, end_y = event.x, event.y
                
                # Koordinatları düzenleme (sol üst, sağ alt)
                x1 = min(start_x, end_x)
                y1 = min(start_y, end_y)
                x2 = max(start_x, end_x)
                y2 = max(start_y, end_y)
                
                self.tarama_alani = {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}
                
                # Koordinat etiketini güncelle
                self.koordinat_label.config(
                    text=f"Sol Üst: ({x1}, {y1}) - Sağ Alt: ({x2}, {y2})"
                )
                
                select_window.destroy()
                self.root.deiconify()  # Ana pencereyi geri getir
                self.log_ekle(f"Tarama alanı seçildi: ({x1}, {y1}) - ({x2}, {y2})")
                
                # Ayarları kaydet
                self.ayarlari_kaydet()
            
            def on_esc_press(event):
                select_window.destroy()
                self.root.deiconify()  # Ana pencereyi geri getir
            
            canvas.bind("<ButtonPress-1>", on_mouse_down)
            canvas.bind("<B1-Motion>", on_mouse_move)
            canvas.bind("<ButtonRelease-1>", on_mouse_up)
            select_window.bind("<Escape>", on_esc_press)
            
            select_window.mainloop()
            
        except Exception as e:
            self.root.deiconify()  # Hata durumunda ana pencereyi geri getir
            self.log_ekle(f"Tarama alanı seçilirken hata oluştu: {e}")
    
    def tikla_nokta_sec(self):
        self.root.iconify()  # Pencereyi simge durumuna küçült
        self.log_ekle("Lütfen sayfa geçişi için tıklanacak noktayı seçin.")
        
        time.sleep(0.5)  # Kullanıcıya hazırlanma süresi ver
        
        try:
            screen = pyautogui.screenshot()
            screen_tk = ImageTk.PhotoImage(screen)
            
            select_window = tk.Toplevel(self.root)
            select_window.attributes('-fullscreen', True)
            select_window.attributes('-topmost', True)
            
            canvas = tk.Canvas(select_window, cursor="cross")
            canvas.pack(fill=tk.BOTH, expand=True)
            
            canvas.create_image(0, 0, image=screen_tk, anchor=tk.NW)
            
            point_id = None
            
            def on_click(event):
                nonlocal point_id
                x, y = event.x, event.y
                
                if point_id:
                    canvas.delete(point_id)
                
                point_id = canvas.create_oval(
                    x-5, y-5, x+5, y+5,
                    fill='red', outline='red'
                )
                
                self.tiklanacak_nokta = {'x': x, 'y': y}
                
                # Nokta koordinat etiketini güncelle
                self.nokta_label.config(
                    text=f"Koordinat: ({x}, {y})"
                )
                
                time.sleep(0.5)  # Noktayı görmesi için bekle
                select_window.destroy()
                self.root.deiconify()  # Ana pencereyi geri getir
                self.log_ekle(f"Tıklama noktası seçildi: ({x}, {y})")
                
                # Ayarları kaydet
                self.ayarlari_kaydet()
            
            def on_esc_press(event):
                select_window.destroy()
                self.root.deiconify()  # Ana pencereyi geri getir
            
            canvas.bind("<ButtonPress-1>", on_click)
            select_window.bind("<Escape>", on_esc_press)
            
            select_window.mainloop()
            
        except Exception as e:
            self.root.deiconify()  # Hata durumunda ana pencereyi geri getir
            self.log_ekle(f"Tıklama noktası seçilirken hata oluştu: {e}")
    
    def ayarlari_guncelle(self):
        # Tarama alanı ve tıklama noktası görsel olarak seçildiği için
        # burada özel bir güncelleme işlemi yapılmıyor
        return True
        
    def taramayi_baslat(self):
        # Aktif kitap seçili değilse uyarı ver
        if not self.aktif_kitap:
            messagebox.showwarning("Uyarı", "Lütfen önce bir kitap seçin veya oluşturun.")
            return
            
        if not self.ayarlari_guncelle():
            return
        
        self.sayfa_parcalari = []  # Önceki parçaları temizle
        
        # Butun durumlarını güncelle
        self.baslat_btn.config(state=tk.DISABLED)
        self.durdur_btn.config(state=tk.NORMAL)
        
        self.devam_ediyor = True
        
        # Sayfa bilgisini güncelle
        self.sayfa_bilgisi_guncelle()
        
        # Geri sayım başlat (5 saniye)
        geri_sayim = 5
        self.log_ekle(f"Tarama {geri_sayim} saniye içinde başlayacak...")
        self.log_ekle(f"Tarama modu: {self.tarama_modu}")
        
        def geri_sayim_guncelle():
            nonlocal geri_sayim
            if geri_sayim > 0:
                self.log_ekle(f"{geri_sayim}...")
                geri_sayim -= 1
                self.root.after(1000, geri_sayim_guncelle)
            else:
                self.log_ekle("Tarama başlatılıyor...")
                
                # Kontrol panelini oluştur
                self.kontrol_paneli_olustur()
                
                # Taramayı ayrı bir iş parçacığında başlat
                threading.Thread(target=self.tarama_islemi, daemon=True).start()
        
        geri_sayim_guncelle()
    
    def kontrol_paneli_olustur(self):
        """Küçük bir kontrol paneli penceresi oluşturur"""
        # Eğer zaten bir panel varsa kapat
        if self.kontrol_panel and self.kontrol_panel.winfo_exists():
            self.kontrol_panel.destroy()
            
        # Yeni kontrol paneli oluştur
        self.kontrol_panel = tk.Toplevel(self.root)
        self.kontrol_panel.title("Tarama Kontrol")
        self.kontrol_panel.geometry("300x120")  # Biraz daha yüksek
        self.kontrol_panel.resizable(False, False)
        self.kontrol_panel.attributes('-topmost', True)  # Her zaman üstte göster
        
        # Ekranın sağ üst köşesine konumlandır
        ekran_genislik = self.kontrol_panel.winfo_screenwidth()
        ekran_yukseklik = self.kontrol_panel.winfo_screenheight()
        x = ekran_genislik - 310
        y = 10
        self.kontrol_panel.geometry(f"300x120+{x}+{y}")
        
        # Panel stilleri
        panel_frame = ttk.Frame(self.kontrol_panel, padding="10")
        panel_frame.pack(fill=tk.BOTH, expand=True)
        
        # Başlık - durum bilgisi ile
        self.panel_baslik = ttk.Label(panel_frame, text="🔄 Tarama Devam Ediyor", 
                                     font=('Segoe UI', 10, 'bold'))
        self.panel_baslik.pack(pady=(0, 5))
        
        # Sayfa bilgisi
        bilgi_frame = ttk.Frame(panel_frame)
        bilgi_frame.pack(fill=tk.X, pady=3)
        
        # Sayfa bilgisi
        ttk.Label(bilgi_frame, text="Sayfa:").grid(row=0, column=0, padx=3)
        self.panel_sayfa_label = ttk.Label(bilgi_frame, text=str(self.sayfa_no), font=('Segoe UI', 9, 'bold'))
        self.panel_sayfa_label.grid(row=0, column=1, padx=3)
        
        ttk.Label(bilgi_frame, text="/").grid(row=0, column=2)
        
        ttk.Label(bilgi_frame, text="Hedef:").grid(row=0, column=3, padx=3)
        self.panel_hedef_label = ttk.Label(bilgi_frame, text=str(self.hedef_sayfa_sayisi), font=('Segoe UI', 9, 'bold'))
        self.panel_hedef_label.grid(row=0, column=4, padx=3)
        
        # Kitap bilgisi
        if self.aktif_kitap:
            ttk.Label(bilgi_frame, text="Kitap:").grid(row=0, column=5, padx=3)
            ttk.Label(bilgi_frame, text=self.aktif_kitap[:15] + "..." if len(self.aktif_kitap) > 15 else self.aktif_kitap,
                    font=('Segoe UI', 9)).grid(row=0, column=6, padx=3)
        
        # Buton çerçevesi
        buton_frame = ttk.Frame(panel_frame)
        buton_frame.pack(fill=tk.X, pady=3)
        
        # Durdurma ve devam butonları
        self.panel_duraklat_btn = ttk.Button(buton_frame, text="⏸️ DURAKLAT", 
                                          command=self.taramayi_duraklat, 
                                          style='Accent.TButton')
        self.panel_duraklat_btn.grid(row=0, column=0, padx=2, sticky="ew")
        
        self.panel_devam_btn = ttk.Button(buton_frame, text="▶️ DEVAM ET", 
                                       command=self.taramayi_devam_ettir, 
                                       style='Accent.TButton', state=tk.DISABLED)
        self.panel_devam_btn.grid(row=0, column=1, padx=2, sticky="ew")
        
        # İptal butonu
        self.panel_iptal_btn = ttk.Button(buton_frame, text="⏹️ İPTAL ET", 
                                       command=self.taramayi_durdur, 
                                       style='Secondary.TButton')
        self.panel_iptal_btn.grid(row=1, column=0, columnspan=2, pady=3, sticky="ew")
        
        # Butonlara eşit genişlik
        buton_frame.columnconfigure(0, weight=1)
        buton_frame.columnconfigure(1, weight=1)
        
        # Panel kapatıldığında taramayı durdur
        self.kontrol_panel.protocol("WM_DELETE_WINDOW", self.taramayi_durdur)
        
        # ESC tuşuna basıldığında taramayı durdur
        self.kontrol_panel.bind("<Escape>", lambda e: self.taramayi_durdur())
    
    def taramayi_duraklat(self):
        """Taramayı duraklatır"""
        if not self.tarama_duraklatildi:
            self.tarama_duraklatildi = True
            self.log_ekle("Tarama duraklatıldı. Devam etmek için 'DEVAM ET' butonuna tıklayın.")
            
            # Butonların durumlarını güncelle
            self.panel_duraklat_btn.config(state=tk.DISABLED)
            self.panel_devam_btn.config(state=tk.NORMAL)
            
            # Başlığı güncelle
            self.panel_baslik.config(text="⏸️ Tarama Duraklatıldı")
    
    def taramayi_devam_ettir(self):
        """Taramayı kaldığı yerden devam ettirir"""
        if self.tarama_duraklatildi:
            self.tarama_duraklatildi = False
            self.log_ekle("Tarama devam ediyor...")
            
            # Butonların durumlarını güncelle
            self.panel_duraklat_btn.config(state=tk.NORMAL)
            self.panel_devam_btn.config(state=tk.DISABLED)
            
            # Başlığı güncelle
            self.panel_baslik.config(text="🔄 Tarama Devam Ediyor")
    
    def tarama_islemi(self):
        # Taramadan önce pencereyi küçült
        self.root.iconify()
        time.sleep(1)  # Hazırlanma süresi
        
        try:
            # Bellek kontrolü - uzun taramalar sırasında
            self.sayfa_parcalari = []  # Önceki parçaları temizle
            gc.collect()  # Çöp toplayıcıyı çağır
            
            while self.devam_ediyor:
                # Periyodik ilerleme kaydetme
                self.ilerleme_kaydet()
                
                # Kontrol panelini güncelle
                self.root.after(0, self.kontrol_paneli_guncelle)
                
                # Duraklatıldıysa bekle
                while self.tarama_duraklatildi and self.devam_ediyor:
                    time.sleep(0.1)  # Duraklatıldığında kısa aralıklarla kontrol et
                    continue  # Duraklatma devam ediyorsa diğer işlemleri atla
                
                # Hedef sayfa sayısına ulaşıldı mı kontrol et
                if self.sayfa_no > self.hedef_sayfa_sayisi:
                    self.log_ekle(f"Hedef sayfa sayısına ({self.hedef_sayfa_sayisi}) ulaşıldı. Tarama durduruluyor.")
                    break
                
                try:
                    if self.tarama_modu == "Nobel":
                        # Nobel tarama modu (kaydırmalı sayfa tarama)
                        self.nobel_tarama_islemi()
                    else:
                        # Turcademy tarama modu (tam sayfa görüntü)
                        self.turcademy_tarama_islemi()
                        
                    # Eğer tarama durdurulmuşsa döngüden çık
                    if not self.devam_ediyor:
                        break
                        
                    # Sonraki sayfaya geç
                    pyautogui.click(self.tiklanacak_nokta['x'], self.tiklanacak_nokta['y'])
                    
                    # Yeni sayfanın yüklenmesini bekle
                    self.log_ekle("Yeni sayfa yükleniyor...")
                    sayfa_yuklendi = self.sayfa_yuklenmesini_bekle(True)
                    
                    # Yeni sayfa başlangıç gecikmesi - Turcademy için daha uygun bekle
                    if self.tarama_modu == "Turcademy":
                        # Turcademy için optimize edilmiş bekleme süresi
                        time.sleep(self.sayfa_gecis_gecikmesi * self.turcademy_gecis_carpani)
                    else:
                        # Nobel için normal bekleme süresi
                        time.sleep(self.sayfa_gecis_gecikmesi)
                    
                    # Sayfa yüklenme bilgisi
                    if sayfa_yuklendi:
                        self.log_ekle("Yeni sayfa yüklendi.")
                    else:
                        self.log_ekle("Yeni sayfa yüklenme zaman aşımı. Devam ediliyor.")
                        
                    # Bellek optimizasyonu
                    if self.sayfa_no % 10 == 0:  # Her 10 sayfada bir
                        gc.collect()  # Çöp toplayıcıyı çağır
                        
                except Exception as e:
                    # Sayfa tarama sırasında oluşabilecek hatayı yakala ve devam et
                    self.log_ekle(f"Sayfa tarama hatası: {e}. Sonraki sayfaya geçiliyor...")
                    time.sleep(2)  # Hata sonrası bekle
                    
                    # Sayfa numarasını yine de arttır
                    self.sayfa_no += 1
                    self.root.after(0, self.sayfa_bilgisi_guncelle)
        
        except Exception as e:
            self.log_ekle(f"Tarama sırasında kritik hata: {e}")
        finally:
            # Tarama tamamlandığında ilerlemeyi kaydet
            self.ilerleme_kaydet()
            self.root.deiconify()  # Ana pencereyi geri getir
            self.root.after(0, self.taramayi_durdur)  # UI thread'inden çağır
            
            # Eğer tarama tamamlandıysa PDF oluşturma butonunu göster
            self.root.after(0, self.pdf_butonunu_goster)
            
    def nobel_tarama_islemi(self):
        """Nobel sitesi için kaydırmalı tarama işlemi"""
        # Geçerli sayfa için görüntüler
        parca_goruntuler = []
        
        # İlk ekran görüntüsünü al
        goruntu = self.ekran_goruntusu_al()
        if goruntu:
            parca_goruntuler.append(goruntu)
            self.son_goruntu = goruntu.copy()
            
            # Sayfanın sonuna kadar kaydır ve ekran görüntüsü al
            kaydirma_devam = True
            self.ayni_sayfa_sayisi = 0
            sayfa_sonu_sayisi = 0
            
            while kaydirma_devam and self.devam_ediyor:
                try:
                    # PgDown tuşuna basarak aşağı kaydır
                    pyautogui.press('pagedown')
                    
                    # Kısa bir süre bekle
                    time.sleep(0.3)
                    
                    # Sayfa değişimini kontrol et
                    yeni_goruntu = self.ekran_goruntusu_al()
                    
                    if yeni_goruntu:
                        # Son görüntüyle benzerliği kontrol et
                        if len(parca_goruntuler) > 0:
                            benzerlik = self.goruntu_benzerlik_yuzde(parca_goruntuler[-1], yeni_goruntu)
                            
                            # Görüntüler çok benzer ise (sayfa sonundayız)
                            if benzerlik > 97:
                                sayfa_sonu_sayisi += 1
                                
                                # İki defa aynı görüntü alırsak, sayfa sonuna geldik demektir
                                if sayfa_sonu_sayisi >= 2:
                                    kaydirma_devam = False
                                    self.log_ekle("Sayfanın sonuna ulaşıldı.")
                            else:
                                sayfa_sonu_sayisi = 0
                                parca_goruntuler.append(yeni_goruntu)
                                self.son_goruntu = yeni_goruntu.copy()
                        else:
                            parca_goruntuler.append(yeni_goruntu)
                            self.son_goruntu = yeni_goruntu.copy()
                    
                except Exception as e:
                    self.log_ekle(f"Kaydırma hatası: {e}")
                    break
        
        if not self.devam_ediyor:
            return
        
        # Parçaları birleştir
        if parca_goruntuler:
            birlesik_goruntu = self.parca_goruntulerini_birlestir(parca_goruntuler)
            if birlesik_goruntu:
                self.sayfa_kaydet(birlesik_goruntu, self.sayfa_no)
                
                # Sayfa numarasını güncelle
                self.sayfa_no += 1
                self.toplam_sayfa = max(self.toplam_sayfa, self.sayfa_no)
                
                # UI güncelle
                self.root.after(0, self.sayfa_bilgisi_guncelle)
                
    def turcademy_tarama_islemi(self):
        """Turcademy sitesi için tam sayfa görüntü alma işlemi"""
        # Tek bir ekran görüntüsü al
        goruntu = self.ekran_goruntusu_al()
        
        if goruntu and self.devam_ediyor:
            # Görüntüyü kaydet
            self.sayfa_kaydet(goruntu, self.sayfa_no)
            
            # Sayfa numarasını güncelle
            self.sayfa_no += 1
            self.toplam_sayfa = max(self.toplam_sayfa, self.sayfa_no)
            
            # UI güncelle
            self.root.after(0, self.sayfa_bilgisi_guncelle)
            
            self.log_ekle(f"Sayfa {self.sayfa_no-1} tarandı.")
            
            # Sayfanın tam olarak kaydedilmesi için kısa bir bekleme ekle (0.3 saniye)
            time.sleep(0.3)
        
    def taramayi_durdur(self):
        if self.devam_ediyor:
            self.devam_ediyor = False
            self.log_ekle("Tarama durduruluyor...")
            
            # İlerlemeyi kaydet
            self.ilerleme_kaydet()
            
            # Butun durumlarını güncelle
            self.baslat_btn.config(state=tk.NORMAL)
            self.durdur_btn.config(state=tk.DISABLED)
            
            # Kontrol panelini kapat
            if self.kontrol_panel and self.kontrol_panel.winfo_exists():
                self.kontrol_panel.destroy()
            
            # Ana pencereyi göster
            self.root.deiconify()
            
            # Eğer otomatik PDF oluşturma seçiliyse ve tarama tamamlandıysa
            if self.otomatik_pdf.get() and self.pdf_butonunu_goster():
                self.log_ekle("Otomatik PDF oluşturma başlatılıyor...")
                self.root.after(1000, self.secili_klasordeki_goruntuleri_birlestir)

    def secili_klasordeki_goruntuleri_birlestir(self):
        """Aktif kitap klasöründeki tüm görüntüleri birleştirerek PDF oluşturur"""
        if not self.aktif_kitap:
            messagebox.showwarning("Uyarı", "Lütfen önce bir kitap seçin veya oluşturun.")
            return
            
        kitap_klasoru = self.kayit_klasoru
        
        if not os.path.exists(kitap_klasoru):
            messagebox.showerror("Hata", "Kitap klasörü bulunamadı.")
            return
        
        # PDF için varsayılan dosya adı
        varsayilan_dosya_adi = f"{self.aktif_kitap}.pdf"
        
        dosya_yolu = filedialog.asksaveasfilename(
            initialdir=os.path.dirname(kitap_klasoru),
            initialfile=varsayilan_dosya_adi,
            defaultextension=".pdf",
            filetypes=[("PDF Dosyaları", "*.pdf")],
            title="PDF'i Kaydet"
        )
        
        if not dosya_yolu:
            return
        
        # İlerleme göstergesini hazırla
        progress_window = tk.Toplevel(self.root)
        progress_window.title("PDF Oluşturuluyor")
        progress_window.geometry("400x150")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        progress_frame = ttk.Frame(progress_window, padding="20")
        progress_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(progress_frame, text="PDF dosyası oluşturuluyor...", 
                 font=('Segoe UI', 10, 'bold')).pack(pady=(0, 10))
        
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, maximum=100)
        progress_bar.pack(fill=tk.X, pady=10)
        
        progress_label = ttk.Label(progress_frame, text="Hazırlanıyor...")
        progress_label.pack(pady=5)
        
        # Arka planda PDF oluştur
        def pdf_olustur():
            try:
                # Klasördeki tüm PNG dosyalarını bul
                goruntu_dosyalari = []
                for dosya in os.listdir(kitap_klasoru):
                    if dosya.lower().endswith(".png"):
                        tam_yol = os.path.join(kitap_klasoru, dosya)
                        goruntu_dosyalari.append(tam_yol)
                
                if not goruntu_dosyalari:
                    self.root.after(0, lambda: messagebox.showinfo("Bilgi", "Kitap klasöründe görüntü dosyası bulunamadı."))
                    progress_window.destroy()
                    return
                
                # Dosyaları sayfa numarasına göre sırala
                goruntu_dosyalari = self.goruntu_dosyalarini_sirala(goruntu_dosyalari)
                
                # PDF oluştur
                pdf_writer = PdfWriter()
                
                # İlerleme bilgisi için
                toplam_dosya = len(goruntu_dosyalari)
                
                for i, dosya in enumerate(goruntu_dosyalari):
                    # İlerleme göstergesini güncelle
                    ilerleme_yuzdesi = (i + 1) / toplam_dosya * 100
                    self.root.after(0, lambda p=ilerleme_yuzdesi: progress_var.set(p))
                    self.root.after(0, lambda d=os.path.basename(dosya), i=i+1, t=toplam_dosya: 
                                 progress_label.config(text=f"İşleniyor: {i}/{t} - {d}"))
                    
                    self.log_ekle(f"İşleniyor ({i+1}/{toplam_dosya}): {os.path.basename(dosya)}")
                    
                    try:
                        # Belleği optimize etmek için işlenen dosyayı hemen serbest bırak
                        with Image.open(dosya) as img:
                            # Görüntüyü PDF sayfasına dönüştür
                            img_bytes = BytesIO()
                            img.convert('RGB').save(img_bytes, format='PDF')
                            img_bytes.seek(0)
                            
                            # PDF sayfasını ekle
                            pdf = PdfReader(img_bytes)
                            pdf_writer.add_page(pdf.pages[0])
                    except Exception as e:
                        self.log_ekle(f"Dosya işlenirken hata: {os.path.basename(dosya)} - {e}")
                
                # PDF'i kaydet
                with open(dosya_yolu, 'wb') as f:
                    pdf_writer.write(f)
                
                self.log_ekle(f"{toplam_dosya} görüntü birleştirildi: {dosya_yolu}")
                
                # Tamamlama mesajı göster
                self.root.after(0, lambda: messagebox.showinfo("Başarılı", f"PDF dosyası oluşturuldu: {dosya_yolu}"))
                
                # Kitap bilgilerini kaydet
                kitap_bilgisi = {
                    'kitap_adi': self.aktif_kitap,
                    'sayfa_sayisi': toplam_dosya,
                    'son_islem_tarihi': time.strftime("%Y-%m-%d %H:%M:%S"),
                    'pdf_dosyasi': dosya_yolu
                }
                
                self.kitap_bilgisi_kaydet(kitap_klasoru, kitap_bilgisi)
                
            except Exception as e:
                self.log_ekle(f"PDF oluşturulurken hata: {e}")
                self.root.after(0, lambda: messagebox.showerror("Hata", f"PDF oluşturulurken hata: {e}"))
            finally:
                self.root.after(0, progress_window.destroy)
        
        # PDF oluştur iş parçacığını başlat
        threading.Thread(target=pdf_olustur, daemon=True).start()

    def kitap_sil(self):
        """Seçili kitabı siler"""
        if not self.aktif_kitap or self.aktif_kitap == "-- Yeni Kitap Ekle --":
            messagebox.showwarning("Uyarı", "Lütfen silmek için bir kitap seçin.")
            return
            
        # Silme onayı
        onay = messagebox.askyesno("Kitap Sil", f"{self.aktif_kitap} kitabını ve tüm taranmış sayfalarını silmek istediğinize emin misiniz?")
        if not onay:
            return
            
        try:
            # Kitap klasörünü sil
            import shutil
            kitap_klasoru = os.path.join(self.kitaplar_klasoru, self.aktif_kitap)
            if os.path.exists(kitap_klasoru):
                shutil.rmtree(kitap_klasoru)
                self.log_ekle(f"{self.aktif_kitap} kitabı silindi.")
                
                # Aktif kitabı temizle
                self.aktif_kitap = ""
                
                # Kitap listesini güncelle
                self.kitaplari_listele()
                
                # Combobox'ı sıfırla
                if self.kitap_combobox['values']:
                    self.kitap_combobox.current(0)
                
                # PDF butonunu gizle
                self.pdf_button.grid_remove()
        except Exception as e:
            messagebox.showerror("Hata", f"Kitap silinirken hata oluştu: {e}")
            self.log_ekle(f"Kitap silme hatası: {e}")

    def kitap_bilgisi_kaydet(self, kitap_klasoru, bilgiler):
        """Kitap bilgilerini JSON dosyasına kaydeder"""
        try:
            bilgi_dosyasi = os.path.join(kitap_klasoru, "kitap_bilgisi.json")
            with open(bilgi_dosyasi, 'w', encoding='utf-8') as f:
                json.dump(bilgiler, f, ensure_ascii=False, indent=4)
            self.log_ekle("Kitap bilgileri kaydedildi.")
        except Exception as e:
            self.log_ekle(f"Kitap bilgileri kaydedilirken hata: {e}")
            
    def kitap_bilgilerini_oku(self, kitap_klasoru):
        """Kitap bilgilerini okur"""
        try:
            bilgi_dosyasi = os.path.join(kitap_klasoru, "kitap_bilgisi.json")
            if os.path.exists(bilgi_dosyasi):
                with open(bilgi_dosyasi, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.log_ekle(f"Kitap bilgileri okunurken hata: {e}")
        return None
        
    def yeni_kitap_ekle(self):
        """Yeni kitap ekleme penceresi gösterir"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Yeni Kitap Ekle")
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()  # Modal dialog
        
        ttk.Label(dialog, text="Kitap Adı:", style='Title.TLabel').grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        kitap_adi_var = tk.StringVar()
        kitap_adi_entry = ttk.Entry(dialog, textvariable=kitap_adi_var, width=30)
        kitap_adi_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        kitap_adi_entry.focus_set()
        
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=1, column=0, columnspan=2, pady=20)
        
        def iptal_et():
            dialog.destroy()
        
        def kitap_ekle():
            kitap_adi = kitap_adi_var.get().strip()
            if kitap_adi:
                # Kitap klasörünü oluştur
                kitap_klasoru = self.kitap_klasoru_olustur(kitap_adi)
                if kitap_klasoru:
                    # Kitapları yeniden listele ve yeni kitabı seç
                    self.kitaplari_listele()
                    # Kitap adını kombo kutusuna ekle
                    kitap_adi_duzgun = self.dosya_adi_duzenle(kitap_adi)
                    self.kitap_combobox.set(kitap_adi_duzgun)
                    # Kitabı seç
                    self.kitap_sec()
                    dialog.destroy()
            else:
                messagebox.showwarning("Uyarı", "Lütfen bir kitap adı girin.")
        
        ttk.Button(button_frame, text="İptal", command=iptal_et).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="Ekle", command=kitap_ekle, style='Accent.TButton').grid(row=0, column=1, padx=10)
        
        # Enter tuşuna basıldığında ekleme işlemini gerçekleştir
        dialog.bind("<Return>", lambda e: kitap_ekle())
        dialog.bind("<Escape>", lambda e: iptal_et())
    
    def kitaplari_listele(self):
        """Mevcut kitapları listeleyip Combobox'a ekler"""
        if not hasattr(self, 'kitap_combobox'):
            return
            
        kitaplar = []
        try:
            # Kitaplar klasöründeki tüm klasörleri listele
            for item in os.listdir(self.kitaplar_klasoru):
                tam_yol = os.path.join(self.kitaplar_klasoru, item)
                if os.path.isdir(tam_yol):
                    kitaplar.append(item)
        except FileNotFoundError:
            pass
        
        # Kitapları alfabetik sırala
        kitaplar.sort()
        
        # Yeni kitap ekleme seçeneğini en başa ekle
        kitaplar = ["-- Yeni Kitap Ekle --"] + kitaplar
        
        # Combobox'ı güncelle
        self.kitap_combobox['values'] = kitaplar
        
        # Eğer hiç kitap yoksa yeni kitap ekleme seçeneğini seç
        if len(kitaplar) == 1:
            self.kitap_combobox.current(0)
            
    def kitap_sec(self):
        """Seçilen kitabı aktif kitap olarak ayarlar"""
        secilen = self.kitap_combobox.get()
        
        # Eğer "Yeni Kitap Ekle" seçildiyse
        if secilen == "-- Yeni Kitap Ekle --":
            self.yeni_kitap_ekle()
            return
            
        # Kitap klasörünü ayarla
        self.aktif_kitap = secilen
        self.kayit_klasoru = os.path.join(self.kitaplar_klasoru, secilen)
        
        # Kitap klasörü yoksa oluştur
        if not os.path.exists(self.kayit_klasoru):
            os.makedirs(self.kayit_klasoru)
        
        # İlerleme dosyasını belirle
        self.ilerleme_dosyasi = os.path.join(self.kayit_klasoru, "ilerleme.json")
        
        # Klasör yolunu güncelle
        self.klasor_label.config(text=self.kayit_klasoru)
        
        # PDF oluşturma butonunu göster veya gizle
        self.pdf_butonunu_goster()
        
        # İlerlemeyi yükle
        self.ilerleme_yukle()
        
        self.log_ekle(f"Aktif kitap: {secilen}")
        
        # Sayfa bilgisini güncelle (eksik kısım eklendi)
        self.sayfa_bilgisi_guncelle()
    
    def pdf_butonunu_goster(self):
        """PDF oluşturma butonunu gösterir veya gizler, 
           PDF oluşturulacak görüntü varsa True döndürür"""
        try:
            # Kitap klasöründe herhangi bir PNG dosyası var mı kontrol et
            png_var = False
            if os.path.exists(self.kayit_klasoru):
                for dosya in os.listdir(self.kayit_klasoru):
                    if dosya.lower().endswith(".png"):
                        png_var = True
                        break
            
            # PNG dosyası varsa butonu göster, yoksa gizle
            if png_var:
                self.pdf_button.grid()
            else:
                self.pdf_button.grid_remove()
                
            return png_var
        except Exception as e:
            self.log_ekle(f"PDF butonu kontrolünde hata: {e}")
            self.pdf_button.grid_remove()
            return False
    
    def goruntu_dosyalarini_sirala(self, dosya_listesi):
        """Görüntü dosyalarını sayfa numarasına göre sıralar"""
        def sayfa_numarasi_getir(dosya_yolu):
            try:
                # sayfa_XX.png veya benzeri formatta dosya adından sayfa numarasını çıkar
                dosya_adi = os.path.basename(dosya_yolu)
                
                # sayfa_X.png, sayfa-X.png, sayfaX.png gibi çeşitli formatları destekle
                for ayirici in ['_', '-', ' ']:
                    parcalar = dosya_adi.split(ayirici)
                    if len(parcalar) >= 2:
                        try:
                            # Son parçadan .png'yi çıkar ve sayıya dönüştür
                            numara_kismi = parcalar[1].split('.')[0]
                            return int(numara_kismi)
                        except:
                            pass
                
                # Başka bir yöntem dene, dosya adındaki tüm sayıları çıkar
                import re
                sayilar = re.findall(r'\d+', dosya_adi)
                if sayilar:
                    return int(sayilar[0])
                
                # Hiçbir yöntem işe yaramazsa, dosya adını döndür (alfabetik sıralama için)
                return dosya_adi
            except:
                # Hata durumunda dosya adını döndür
                return os.path.basename(dosya_yolu)
        
        # Dosyaları sayfa numarasına göre sırala
        return sorted(dosya_listesi, key=sayfa_numarasi_getir)
    
    def kitap_klasoru_olustur(self, kitap_adi):
        """Kitap için klasör oluşturur"""
        if not kitap_adi:
            return None
            
        # Dosya adı uyumlu hale getir
        kitap_adi_duzgun = self.dosya_adi_duzenle(kitap_adi)
        kitap_klasoru = os.path.join(self.kitaplar_klasoru, kitap_adi_duzgun)
        
        # Klasör yoksa oluştur
        if not os.path.exists(kitap_klasoru):
            os.makedirs(kitap_klasoru)
            self.log_ekle(f"Yeni kitap klasörü oluşturuldu: {kitap_adi}")
        
        return kitap_klasoru
    
    def dosya_adi_duzenle(self, ad):
        """Dosya adı için uygun olmayan karakterleri değiştirir"""
        # Geçersiz dosya adı karakterlerini değiştir
        gecersiz_karakterler = r'[\\/*?:"<>|]'
        import re
        duzgun_ad = re.sub(gecersiz_karakterler, "_", ad)
        return duzgun_ad

    def tarama_modu_degisti(self):
        """Tarama modu değiştiğinde yapılacak işlemler"""
        self.tarama_modu = self.tarama_modu_var.get()
        self.log_ekle(f"Tarama modu değiştirildi: {self.tarama_modu}")
        self.ayarlari_kaydet()
        
    def sayfa_yuklenmesini_bekle(self, yeni_sayfa=False):
        """Sayfanın yüklenmesini bekler, yüklendiyse True döndürür, aksi halde False"""
        try:
            baslangic_zamani = time.time()
            sayfa_yuklendi = False
            onceki_goruntu = None
            kararlilik_sayaci = 0
            
            # Sayfa yüklenene kadar bekle
            while time.time() - baslangic_zamani < self.max_bekleme_suresi and not sayfa_yuklendi and self.devam_ediyor:
                # Kısa bir süre bekle - daha hızlı kontrol için
                time.sleep(0.05)  # 0.1 yerine 0.05 (daha hızlı kontrol)
                
                # Mevcut ekran görüntüsünü al
                goruntu = self.ekran_goruntusu_al()
                
                if goruntu and onceki_goruntu:
                    # İki görüntü arasındaki benzerliği kontrol et
                    benzerlik = self.goruntu_benzerlik_yuzde(onceki_goruntu, goruntu)
                    
                    # Eğer benzerlik belirli bir eşiğin üzerindeyse, sayfa istikrarlı demektir
                    # Turcademy için daha düşük eşik değeri (daha hızlı geçiş için)
                    esik_degeri = 85 if self.tarama_modu == "Turcademy" else 90
                    
                    if benzerlik > esik_degeri:
                        kararlilik_sayaci += 1
                    else:
                        kararlilik_sayaci = 0
                    
                    # Turcademy için daha az kararlılık kontrolü (daha hızlı yanıt)
                    gereken_kararli_goruntu = 1 if self.tarama_modu == "Turcademy" else 1
                    if kararlilik_sayaci >= gereken_kararli_goruntu:
                        sayfa_yuklendi = True
                        
                        # Eğer yeni bir sayfaya geçiyorsak, son görüntüyü güncelle
                        if yeni_sayfa:
                            self.son_goruntu = goruntu.copy()
                
                onceki_goruntu = goruntu
            
            return sayfa_yuklendi
        
        except Exception as e:
            self.log_ekle(f"Sayfa yüklenme kontrolünde hata: {e}")
            return False
            
    def ekran_goruntusu_al(self):
        x1, y1, x2, y2 = self.tarama_alani['x1'], self.tarama_alani['y1'], self.tarama_alani['x2'], self.tarama_alani['y2']
        
        try:
            screenshot = pyautogui.screenshot(region=(x1, y1, x2-x1, y2-y1))
            return screenshot
        except Exception as e:
            self.log_ekle(f"Ekran görüntüsü alınırken hata: {e}")
            return None
    
    def sayfa_kaydet(self, goruntu, sayfa_no):
        try:
            # Kitap klasörünün kontrolü
            if not os.path.exists(self.kayit_klasoru):
                os.makedirs(self.kayit_klasoru)
                
            dosya_adi = f"sayfa_{sayfa_no}.png"
            tam_yol = os.path.join(self.kayit_klasoru, dosya_adi)
            goruntu.save(tam_yol)
            self.log_ekle(f"Sayfa {sayfa_no} kaydedildi: {dosya_adi}")
            return tam_yol
        except Exception as e:
            self.log_ekle(f"Sayfa kaydedilirken hata: {e}")
            return None
    
    def sayfa_bilgisi_guncelle(self):
        self.sayfa_label.config(text=str(self.sayfa_no))
        self.toplam_sayfa_label.config(text=str(self.toplam_sayfa))
    
    def goruntu_benzerlik_yuzde(self, goruntu1, goruntu2):
        """İki görüntü arasındaki benzerlik yüzdesini hesaplar (0-100)"""
        try:
            # Görüntüleri küçült
            goruntu1 = goruntu1.resize((50, 50))  # 100x100 yerine 50x50 yaparak hızlandır
            goruntu2 = goruntu2.resize((50, 50))
            
            # Görüntüleri sadeleştir (gri tonlama)
            goruntu1 = goruntu1.convert('L')
            goruntu2 = goruntu2.convert('L')
            
            farklı_piksel_sayisi = 0
            toplam_piksel = 50 * 50  # Toplam piksel sayısı
            esik_degeri = 30  # Piksel farkı için eşik değeri
            
            # Daha hızlı karşılaştırma için numpy kullanabiliriz
            try:
                import numpy as np
                
                # Görüntüleri numpy dizilerine dönüştür
                arr1 = np.array(goruntu1)
                arr2 = np.array(goruntu2)
                
                # Farkı hesapla
                fark = np.abs(arr1 - arr2)
                
                # Eşik değerinden büyük farkları say
                farklı_piksel_sayisi = np.sum(fark > esik_degeri)
                
            except ImportError:
                # Numpy yoksa manuel olarak hesapla
                for x in range(50):
                    for y in range(50):
                        piksel1 = goruntu1.getpixel((x, y))
                        piksel2 = goruntu2.getpixel((x, y))
                        if abs(piksel1 - piksel2) > esik_degeri:
                            farklı_piksel_sayisi += 1
            
            benzerlik_yuzdesi = 100 - (farklı_piksel_sayisi * 100 / toplam_piksel)
            return benzerlik_yuzdesi
        except Exception as e:
            self.log_ekle(f"Görüntü benzerlik hesaplama hatası: {e}")
            return 0
    
    def parca_goruntulerini_birlestir(self, goruntuler):
        if not goruntuler:
            return None
        
        try:
            # İlk görüntünün genişliğini temel al
            genislik = goruntuler[0].width
            
            # Örtüşme tespiti için kullanılacak piksel sayısı
            ortusme_pikseli = min(50, int(goruntuler[0].height * 0.1))  # Görüntü yüksekliğine göre ayarla
            
            # Yeni birleşik görüntü için hazırlık
            toplam_yukseklik = 0
            islenmis_goruntuler = []
            
            # İlk görüntüyü doğrudan ekle
            islenmis_goruntuler.append((goruntuler[0], 0))
            toplam_yukseklik = goruntuler[0].height
            
            # Diğer görüntüleri analiz et ve örtüşme noktalarını bul
            for i in range(1, len(goruntuler)):
                onceki_goruntu = goruntuler[i-1]
                simdiki_goruntu = goruntuler[i]
                
                # Önceki görüntünün alt kısmı
                onceki_alt = onceki_goruntu.crop((0, onceki_goruntu.height - ortusme_pikseli, 
                                                 genislik, onceki_goruntu.height))
                
                # Şimdiki görüntünün üst kısmı
                simdiki_ust = simdiki_goruntu.crop((0, 0, genislik, ortusme_pikseli))
                
                # İki görüntüyü gri tonlamaya dönüştür (daha hızlı eşleşme için)
                onceki_alt = onceki_alt.convert('L')
                simdiki_ust = simdiki_ust.convert('L')
                
                # En iyi örtüşme pozisyonunu bul
                en_iyi_offset = 0
                en_az_fark = float('inf')
                
                # Adım boyutunu artırarak daha hızlı hesaplama (her pikseli değil, belli aralıklarla)
                adim = max(1, ortusme_pikseli // 10)
                
                # Farklı offset değerlerini dene
                for offset in range(0, ortusme_pikseli, adim):
                    fark = 0
                    piksel_sayisi = 0
                    
                    # Noktaları örnekle (tüm pikselleri değil, belli aralıklarla)
                    ornekleme = max(1, genislik // 20)
                    
                    # İki görüntü arasındaki farkı hesapla
                    for x in range(0, genislik, ornekleme):
                        for y in range(0, ortusme_pikseli - offset, adim):
                            try:
                                onceki_piksel = onceki_alt.getpixel((x, y + offset))
                                simdiki_piksel = simdiki_ust.getpixel((x, y))
                                
                                # Doğrudan gri ton farkı (RGB yerine)
                                fark += abs(onceki_piksel - simdiki_piksel)
                                piksel_sayisi += 1
                            except:
                                pass
                    
                    # Ortalama farkı hesapla
                    if piksel_sayisi > 0:
                        ortalama_fark = fark / piksel_sayisi
                        
                        if ortalama_fark < en_az_fark:
                            en_az_fark = ortalama_fark
                            en_iyi_offset = offset
                
                # Görüntüyü en iyi pozisyonda yerleştir
                y_pozisyon = toplam_yukseklik - (ortusme_pikseli - en_iyi_offset)
                islenmis_goruntuler.append((simdiki_goruntu, y_pozisyon))
                
                # Toplam yüksekliği güncelle
                toplam_yukseklik = y_pozisyon + simdiki_goruntu.height
            
            # Yeni birleşik görüntü oluştur
            birlesik = Image.new('RGB', (genislik, toplam_yukseklik))
            
            # Görüntüleri yerleştir
            for goruntu, y_pozisyon in islenmis_goruntuler:
                birlesik.paste(goruntu, (0, y_pozisyon))
            
            # Bellek temizliği
            del islenmis_goruntuler
            gc.collect()
            
            return birlesik
        except Exception as e:
            self.log_ekle(f"Görüntüler birleştirilirken hata: {e}")
            return None

    def baslangic_sayfasini_guncelle(self):
        """Başlangıç sayfa numarasını günceller"""
        try:
            yeni_sayfa = int(self.baslangic_sayfa_var.get())
            if yeni_sayfa > 0:
                self.sayfa_no = yeni_sayfa
                self.sayfa_bilgisi_guncelle()
                self.log_ekle(f"Başlangıç sayfa numarası {yeni_sayfa} olarak ayarlandı.")
            else:
                messagebox.showwarning("Uyarı", "Sayfa numarası 1 veya daha büyük olmalıdır.")
        except ValueError:
            messagebox.showwarning("Uyarı", "Geçerli bir sayfa numarası girin.")

    def bilgi_kontrolu(self):
        """Ayarlara göre bilgi mesajının gösterilip gösterilmeyeceğini kontrol eder"""
        try:
            ayarlar = {}
            if os.path.exists(self.config_dosyasi):
                with open(self.config_dosyasi, 'r') as f:
                    ayarlar = json.load(f)
            
            # Başlangıç bilgisi gösterilecek mi?
            if not ayarlar.get('baslangic_bilgi_goster', True) == False:
                self.baslangic_bilgi_goster()
                
        except Exception as e:
            # Hata oluşursa varsayılan olarak göster
            self.baslangic_bilgi_goster()

    def baslangic_bilgi_goster(self):
        """Uygulama ilk açıldığında bilgi mesajı gösterir"""
        # Kılavuz penceresi
        info_window = tk.Toplevel(self.root)
        info_window.title("Hoş Geldiniz")
        info_window.geometry("550x400")
        info_window.transient(self.root)
        info_window.grab_set()
        
        # İçerik frame
        info_frame = ttk.Frame(info_window, padding="20")
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        # Başlık
        ttk.Label(info_frame, text="Ekran Tarayıcı Uygulamasına Hoş Geldiniz!", 
                 font=('Segoe UI', 12, 'bold')).pack(pady=(0, 10))
        
        # Ana açıklama
        bilgi_text = "Bu uygulama web sayfalarındaki içerikleri PDF'e dönüştürmenize yardımcı olur.\n\n"
        bilgi_text += "📚 Nobel Modu: Uzun sayfaları kaydırarak tarar ve birleştirir.\n"
        bilgi_text += "📖 Turcademy Modu: Her sayfayı tek görüntü olarak alır.\n\n"
        bilgi_text += "🔹 KULLANIM ADIMLARI 🔹\n\n"
        bilgi_text += "1. Bir kitap seçin veya oluşturun\n"
        bilgi_text += "2. Tarama modunu seçin (Nobel veya Turcademy)\n"
        bilgi_text += "3. Tarama alanını belirleyin (buton ile ekrandan seçin)\n"
        bilgi_text += "4. Sayfa geçiş noktasını belirleyin (ileri butonu veya benzeri)\n"
        bilgi_text += "5. Başlangıç sayfa numarasını ve hedef sayfa sayısını girin\n"
        bilgi_text += "6. Taramayı başlatın\n\n"
        bilgi_text += "🔹 ÖNEMLİ BİLGİLER 🔹\n\n"
        bilgi_text += "- Tarama sırasında ESC tuşu ile durdurabilirsiniz\n"
        bilgi_text += "- Hedef sayfa sayısına ulaşıldığında tarama otomatik durur\n"
        bilgi_text += "- Tarama bittiğinde PDF oluşturma butonu otomatik görünür\n"
        bilgi_text += "- Otomatik PDF oluşturma seçeneğini işaretlerseniz tarama bittiğinde PDF otomatik oluşturulur\n"
        bilgi_text += "- İlerleme otomatik kaydedilir, daha sonra taramaya kaldığınız yerden devam edebilirsiniz"
        
        text_widget = tk.Text(info_frame, height=15, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, pady=10)
        text_widget.insert(tk.END, bilgi_text)
        text_widget.config(state=tk.DISABLED)
        
        # Buton çerçevesi
        buton_frame = ttk.Frame(info_frame)
        buton_frame.pack(fill=tk.X, pady=10)
        
        # Yardım/demo butonu
        ttk.Button(buton_frame, text="Açılışta Gösterme", 
                  command=lambda: self.ayarlari_kaydet_ozel("baslangic_bilgi_goster", False),
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=5)
        
        # Kapat butonu
        ttk.Button(buton_frame, text="Başla", command=info_window.destroy, 
                  style='Accent.TButton').pack(side=tk.RIGHT, padx=5)
        
    def ayarlari_kaydet_ozel(self, anahtar, deger):
        """Özel bir ayarı günceller ve kaydeder"""
        try:
            # Mevcut ayarları yükle
            ayarlar = {}
            if os.path.exists(self.config_dosyasi):
                with open(self.config_dosyasi, 'r') as f:
                    ayarlar = json.load(f)
            
            # Belirtilen ayarı güncelle
            ayarlar[anahtar] = deger
            
            # Ayarları kaydet
            with open(self.config_dosyasi, 'w') as f:
                json.dump(ayarlar, f)
                
        except Exception as e:
            print(f"Özel ayar kaydedilirken hata: {e}")

    def hedef_sayfasini_guncelle(self):
        """Hedef sayfa sayısını günceller"""
        try:
            yeni_hedef = int(self.hedef_sayfa_var.get())
            if yeni_hedef > 0:
                self.hedef_sayfa_sayisi = yeni_hedef
                self.log_ekle(f"Hedef sayfa sayısı {yeni_hedef} olarak ayarlandı.")
                self.ayarlari_kaydet()
            else:
                messagebox.showwarning("Uyarı", "Hedef sayfa sayısı 1 veya daha büyük olmalıdır.")
        except ValueError:
            messagebox.showwarning("Uyarı", "Geçerli bir sayfa sayısı girin.")

if __name__ == "__main__":
    root = tk.Tk()
    app = EkranTarayici(root)
    root.mainloop() 