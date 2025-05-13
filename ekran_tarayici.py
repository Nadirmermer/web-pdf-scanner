import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyautogui
import time
import keyboard
import os
from PIL import Image, ImageTk, ImageGrab
import threading
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
        self.max_bekleme_suresi = 5       # Maksimum yüklenme süresi (5 saniye) - arttırıldı 
        self.sayfa_gecis_gecikmesi = 1.5  # Sayfa geçiş gecikmesi (1.5 saniye) - arttırıldı
        
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
            # Önce klasördeki mevcut sayfa dosyalarını kontrol et
            self.mevcut_sayfa_durumunu_tespit_et()
            
            if os.path.exists(self.ilerleme_dosyasi):
                with open(self.ilerleme_dosyasi, 'r') as f:
                    ilerleme = json.load(f)
                    self.toplam_sayfa = ilerleme.get('toplam_sayfa', 1)
                    
                    # Toplam sayfayı mevcut en yüksek sayfa ile karşılaştır
                    if self.sayfa_no > self.toplam_sayfa:
                        self.toplam_sayfa = self.sayfa_no
                    
                    self.log_ekle(f"İlerleme dosyası yüklendi. Sonraki sayfa: {self.sayfa_no}")
                
                # Sayfa numarası alanını güncelle
                if hasattr(self, 'baslangic_sayfa_entry'):
                    self.baslangic_sayfa_entry.delete(0, tk.END)
                    self.baslangic_sayfa_entry.insert(0, str(self.sayfa_no))
                
                # Sayfa bilgisi etiketlerini güncelle
                self.sayfa_bilgisi_guncelle()
                
        except Exception as e:
            self.log_ekle(f"İlerleme yüklenirken hata: {e}")
    
    def mevcut_sayfa_durumunu_tespit_et(self):
        """Klasördeki mevcut son sayfa numarasını tespit eder ve taramaya oradan devam eder"""
        try:
            if not self.aktif_kitap or not os.path.exists(self.kayit_klasoru):
                self.sayfa_no = 1
                return
                
            # Sayfaları bul ve en yüksek sayfa numarasını tespit et
            en_yuksek_sayfa = 0
            sayfa_dosyalari = []
            
            # Klasördeki tüm sayfa_X.png dosyalarını bul
            for dosya in os.listdir(self.kayit_klasoru):
                if dosya.startswith("sayfa_") and dosya.endswith(".png"):
                    sayfa_dosyalari.append(dosya)
            
            # Sayfa numaralarını çıkar
            for dosya in sayfa_dosyalari:
                try:
                    # sayfa_X.png formatındaki dosya adından X'i çıkar
                    sayfa_no_str = dosya.replace("sayfa_", "").replace(".png", "")
                    sayfa_no = int(sayfa_no_str)
                    if sayfa_no > en_yuksek_sayfa:
                        en_yuksek_sayfa = sayfa_no
                except ValueError:
                    continue
            
            # En yüksek sayfa numarasından sonraki sayfadan devam et
            if en_yuksek_sayfa > 0:
                self.sayfa_no = en_yuksek_sayfa + 1
                # Toplam sayfa numarasını da güncelle
                self.toplam_sayfa = max(self.toplam_sayfa, en_yuksek_sayfa)
                self.log_ekle(f"Klasördeki en yüksek sayfa numarası: {en_yuksek_sayfa}, tarama {self.sayfa_no}. sayfadan devam edecek")
            else:
                self.sayfa_no = 1
                self.log_ekle("Klasörde sayfa bulunamadı, tarama 1. sayfadan başlayacak")
                
            # Sayfa bilgisi etiketlerini güncelle
            self.sayfa_bilgisi_guncelle()
                
        except Exception as e:
            self.log_ekle(f"Sayfa durumu tespit edilirken hata: {e}")
            self.sayfa_no = 1
    
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
        # Ana çerçeve - maksimum kompaktlık için padding azaltıldı
        main_frame = ttk.Frame(self.root, padding="2")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Ana içerik frame
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tarama sekmesini yapılandır
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(4, weight=1)
        
        # ======= KİTAP SEÇİMİ =======
        kitap_frame = ttk.LabelFrame(content_frame, text="1. Kitap Seçimi", padding="2")
        kitap_frame.grid(row=0, column=0, sticky="ew", pady=2)
        kitap_frame.columnconfigure(1, weight=1)
        
        # Tek satırda kitap seçimi
        self.kitap_combobox = ttk.Combobox(kitap_frame, width=40, state="readonly")
        self.kitap_combobox.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.kitap_combobox.bind("<<ComboboxSelected>>", lambda e: self.kitap_sec())
        
        # Butonları yan yana yerleştir
        buton_frame = ttk.Frame(kitap_frame)
        buton_frame.pack(side=tk.RIGHT, padx=2, pady=2)
        
        ttk.Button(buton_frame, text="Yeni", command=self.yeni_kitap_ekle,
                 width=5).pack(side=tk.LEFT, padx=1)
                 
        ttk.Button(buton_frame, text="Sil", command=self.kitap_sil,
                 width=5).pack(side=tk.LEFT, padx=1)
                 
        # PDF butonu - pack yerine aynı hizalama mekanizmasını kullan
        self.pdf_button = ttk.Button(buton_frame, text="PDF", 
                                   command=self.secili_klasordeki_goruntuleri_birlestir,
                                   width=5)
        self.pdf_button.pack(side=tk.LEFT, padx=1)
        # Başlangıçta gizlemek yerine görünmez yapma
        self.pdf_button_visible = False  # Butonun görünürlüğünü takip etmek için flag ekle
        
        # ======= TARAMA MODU =======
        tarama_modu_frame = ttk.LabelFrame(content_frame, text="2. Tarama Modu", padding="2")
        tarama_modu_frame.grid(row=1, column=0, sticky="ew", pady=2)
        
        # Tarama modları - Tek satırda
        self.tarama_modu_var = tk.StringVar(value=self.tarama_modu)
        
        # Modları yatay düzenle
        modu_frame = ttk.Frame(tarama_modu_frame)
        modu_frame.pack(fill=tk.X, padx=2, pady=2)
        
        # Nobel modu (daha kompakt)
        ttk.Radiobutton(modu_frame, text="Nobel (Sayfa Kaydırma)", 
                       value="Nobel", variable=self.tarama_modu_var,
                       command=self.tarama_modu_degisti).pack(side=tk.LEFT, padx=10)
        
        # Turcademy modu (daha kompakt)
        ttk.Radiobutton(modu_frame, text="Turcademy (Tek Sayfa)", 
                       value="Turcademy", variable=self.tarama_modu_var,
                       command=self.tarama_modu_degisti).pack(side=tk.LEFT, padx=10)
        
        # ======= AYARLAR =======
        ayarlar_frame = ttk.LabelFrame(content_frame, text="3. Tarama Ayarları", padding="2")
        ayarlar_frame.grid(row=2, column=0, sticky="ew", pady=2)
        
        # Daha kompakt ayarlar
        ayarlar_ic_frame = ttk.Frame(ayarlar_frame)
        ayarlar_ic_frame.pack(fill=tk.X, padx=2, pady=2)
        
        # Sol taraf - Tarama alanı
        sol_frame = ttk.Frame(ayarlar_ic_frame)
        sol_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        ttk.Button(sol_frame, text="Tarama Alanı Seç", 
                  command=self.tarama_alani_sec, 
                  width=15).pack(side=tk.TOP, pady=1)
        
        self.koordinat_label = ttk.Label(sol_frame, 
                             text=f"({self.tarama_alani['x1']},{self.tarama_alani['y1']})-({self.tarama_alani['x2']},{self.tarama_alani['y2']})",
                             style='Info.TLabel', font=('Segoe UI', 8))
        self.koordinat_label.pack(side=tk.TOP)
        
        # Sağ taraf - Tıklama noktası
        sag_frame = ttk.Frame(ayarlar_ic_frame)
        sag_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        
        ttk.Button(sag_frame, text="Sayfa Geçiş Noktası", 
                  command=self.tikla_nokta_sec, 
                  width=15).pack(side=tk.TOP, pady=1)
        
        self.nokta_label = ttk.Label(sag_frame, 
                         text=f"({self.tiklanacak_nokta['x']},{self.tiklanacak_nokta['y']})",
                         style='Info.TLabel', font=('Segoe UI', 8))
        self.nokta_label.pack(side=tk.TOP)
        
        # ======= SAYFA BİLGİSİ =======
        sayfa_frame = ttk.LabelFrame(content_frame, text="4. Sayfa Bilgisi", padding="2")
        sayfa_frame.grid(row=3, column=0, sticky="ew", pady=2)
        
        # Sayfa bilgileri kompakt alanda
        sayfa_bilgi_frame = ttk.Frame(sayfa_frame)
        sayfa_bilgi_frame.pack(fill=tk.X, padx=2, pady=2)
        
        # Tek satırda tüm bilgiler
        ttk.Label(sayfa_bilgi_frame, text="Başlangıç:").pack(side=tk.LEFT, padx=2)
        self.baslangic_sayfa_var = tk.StringVar(value=str(self.sayfa_no))
        self.baslangic_sayfa_entry = ttk.Entry(sayfa_bilgi_frame, textvariable=self.baslangic_sayfa_var, width=4, state='readonly')
        self.baslangic_sayfa_entry.pack(side=tk.LEFT)
        
        ttk.Button(sayfa_bilgi_frame, text="Düzenle", command=self.sayfa_numarasi_duzenle, 
                 width=6).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(sayfa_bilgi_frame, text="Şu anki:").pack(side=tk.LEFT, padx=(10, 2))
        self.sayfa_label = ttk.Label(sayfa_bilgi_frame, text=str(self.sayfa_no), font=('Segoe UI', 9, 'bold'))
        self.sayfa_label.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(sayfa_bilgi_frame, text="Toplam:").pack(side=tk.LEFT, padx=(10, 2))
        self.toplam_sayfa_label = ttk.Label(sayfa_bilgi_frame, text=str(self.toplam_sayfa), font=('Segoe UI', 9, 'bold'))
        self.toplam_sayfa_label.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(sayfa_bilgi_frame, text="Hedef:").pack(side=tk.LEFT, padx=(10, 2))
        self.hedef_sayfa_var = tk.StringVar(value=str(self.hedef_sayfa_sayisi))
        self.hedef_sayfa_entry = ttk.Entry(sayfa_bilgi_frame, textvariable=self.hedef_sayfa_var, width=4)
        self.hedef_sayfa_entry.pack(side=tk.LEFT)
        self.hedef_sayfa_entry.bind("<Return>", lambda e: self.hedef_sayfasini_guncelle())
        
        ttk.Button(sayfa_bilgi_frame, text="Ayarla", 
                  command=self.hedef_sayfasini_guncelle, 
                  width=6).pack(side=tk.LEFT, padx=2)
        
        # İkinci satır - klasör bilgisi
        klasor_bilgi_frame = ttk.Frame(sayfa_frame)
        klasor_bilgi_frame.pack(fill=tk.X, padx=2, pady=(0, 2))
        
        ttk.Label(klasor_bilgi_frame, text="Klasör:", 
                style='Info.TLabel', font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=2)
        
        self.klasor_label = ttk.Label(klasor_bilgi_frame, text=self.kayit_klasoru, 
                                   style='Info.TLabel', font=('Segoe UI', 8))
        self.klasor_label.pack(side=tk.LEFT, padx=2)
        
        # ======= TARAMA KONTROL =======
        kontrol_frame = ttk.LabelFrame(content_frame, text="5. Tarama Kontrol", padding="2")
        kontrol_frame.grid(row=4, column=0, sticky="ew", pady=2)
        
        # Butonlar ve otomatik PDF seçeneği - tek satırda
        buton_frame = ttk.Frame(kontrol_frame)
        buton_frame.pack(fill=tk.X, padx=2, pady=2)
        
        # Sol taraf - butonlar
        baslat_frame = ttk.Frame(buton_frame)
        baslat_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.baslat_btn = ttk.Button(baslat_frame, text="▶️ BAŞLAT", 
                                    command=self.taramayi_baslat)
        self.baslat_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        self.durdur_btn = ttk.Button(baslat_frame, text="⏹️ DURDUR", 
                                    command=self.taramayi_durdur, 
                                    state=tk.DISABLED)
        self.durdur_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # Sağ taraf - PDF seçeneği
        pdf_frame = ttk.Frame(buton_frame)
        pdf_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Checkbutton(pdf_frame, text="Tarama sonrası PDF oluştur", 
                      variable=self.otomatik_pdf, 
                      command=self.ayarlari_kaydet).pack(side=tk.RIGHT, padx=2)
        
        # Kısa bilgi
        ttk.Label(kontrol_frame, text="ESC tuşu: Taramayı durdur", 
                 style='Info.TLabel', font=('Segoe UI', 8)).pack(pady=(0, 2))
        
        # ======= İŞLEM GÜNLÜĞÜ =======
        log_frame = ttk.LabelFrame(content_frame, text="İşlem Günlüğü", padding="2")
        log_frame.grid(row=5, column=0, sticky="nsew", pady=2)
        content_frame.rowconfigure(5, weight=1)
        
        # Log metni - scrollbar eklenmiş
        log_container = ttk.Frame(log_frame)
        log_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        self.log_text = tk.Text(log_container, height=5, wrap=tk.WORD, font=('Segoe UI', 8))
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        log_scrollbar = ttk.Scrollbar(log_container, orient="vertical", command=self.log_text.yview)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        # Klavye kısayolları
        self.root.bind("<Escape>", lambda e: self.taramayi_durdur())
    
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
                
                # Koordinat etiketini güncelle - daha kompakt
                self.koordinat_label.config(
                    text=f"({x1},{y1})-({x2},{y2})"
                )
                
                select_window.destroy()
                self.root.deiconify()  # Ana pencereyi geri getir
                self.log_ekle(f"Tarama alanı: ({x1},{y1})-({x2},{y2})")
                
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
            self.log_ekle(f"Tarama alanı seçilirken hata: {e}")
    
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
                
                # Nokta koordinat etiketini güncelle - daha kompakt
                self.nokta_label.config(
                    text=f"({x},{y})"
                )
                
                time.sleep(0.5)  # Noktayı görmesi için bekle
                select_window.destroy()
                self.root.deiconify()  # Ana pencereyi geri getir
                self.log_ekle(f"Tıklama noktası: ({x},{y})")
                
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
            self.log_ekle(f"Tıklama noktası seçilirken hata: {e}")
    
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
        self.kontrol_panel.title("")  # Başlık yok
        self.kontrol_panel.geometry("50x120")  # Çok dar panel (50 piksel)
        self.kontrol_panel.resizable(False, False)
        self.kontrol_panel.attributes('-topmost', True)  # Her zaman üstte göster
        
        # Ekranın sağ üst köşesine konumlandır
        ekran_genislik = self.kontrol_panel.winfo_screenwidth()
        ekran_yukseklik = self.kontrol_panel.winfo_screenheight()
        x = ekran_genislik - 60
        y = 10
        self.kontrol_panel.geometry(f"50x120+{x}+{y}")
        
        # Panel stilleri - minimum padding
        panel_frame = ttk.Frame(self.kontrol_panel, padding="2")
        panel_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sayfa numarası etiketi - yalnızca mevcut sayfa
        self.panel_sayfa_label = ttk.Label(panel_frame, text=f"S:{self.sayfa_no}", 
                                          font=('Segoe UI', 8))
        self.panel_sayfa_label.pack(pady=(0, 1))
        
        # Butonları alt alta düzenle - çok dar
        self.panel_duraklat_btn = ttk.Button(panel_frame, text="⏸️", 
                                          command=self.taramayi_duraklat, 
                                          width=3)
        self.panel_duraklat_btn.pack(pady=1)
        
        self.panel_devam_btn = ttk.Button(panel_frame, text="▶️", 
                                       command=self.taramayi_devam_ettir, 
                                       width=3, state=tk.DISABLED)
        self.panel_devam_btn.pack(pady=1)
        
        self.panel_iptal_btn = ttk.Button(panel_frame, text="⏹️", 
                                       command=self.taramayi_durdur, 
                                       width=3)
        self.panel_iptal_btn.pack(pady=1)
        
        # Panel kapatıldığında taramayı durdur
        self.kontrol_panel.protocol("WM_DELETE_WINDOW", self.taramayi_durdur)
        
        # ESC tuşuna basıldığında taramayı durdur
        self.kontrol_panel.bind("<Escape>", lambda e: self.taramayi_durdur())
    
    def taramayi_duraklat(self):
        """Taramayı duraklatır"""
        if not self.tarama_duraklatildi:
            self.tarama_duraklatildi = True
            self.log_ekle("Tarama duraklatıldı. Devam etmek için '▶️' butonuna tıklayın.")
            
            # Butonların durumlarını güncelle
            self.panel_duraklat_btn.config(state=tk.DISABLED)
            self.panel_devam_btn.config(state=tk.NORMAL)
            
            # Durum bilgisini güncelle
            if hasattr(self, 'panel_sayfa_label') and self.panel_sayfa_label.winfo_exists():
                self.panel_sayfa_label.config(text="⏸️ DURAKLATILDI")
    
    def taramayi_devam_ettir(self):
        """Taramayı kaldığı yerden devam ettirir"""
        if self.tarama_duraklatildi:
            self.tarama_duraklatildi = False
            self.log_ekle("Tarama devam ediyor...")
            
            # Butonların durumlarını güncelle
            self.panel_duraklat_btn.config(state=tk.NORMAL)
            self.panel_devam_btn.config(state=tk.DISABLED)
            
            # Durum bilgisini güncelle
            if hasattr(self, 'panel_sayfa_label') and self.panel_sayfa_label.winfo_exists():
                self.panel_sayfa_label.config(text=f"S:{self.sayfa_no}")
                
            # Kontrol panelini güncelle
            self.kontrol_paneli_guncelle()
    
    def tarama_islemi(self):
        # Taramadan önce pencereyi küçült
        self.root.iconify()
        time.sleep(1)  # Hazırlanma süresi
        
        try:
            # Bellek kontrolü - uzun taramalar sırasında
            self.sayfa_parcalari = []  # Önceki parçaları temizle
            gc.collect()  # Çöp toplayıcıyı çağır
            
            # Klavye kısayolu - ESC tuşu ile tarama durdurma
            keyboard.add_hotkey('esc', self.taramayi_durdur)
            
            while self.devam_ediyor:
                # ESC tuşuna basıldı mı kontrol et
                if keyboard.is_pressed('esc'):
                    self.log_ekle("ESC tuşuna basıldı. Tarama durduruluyor...")
                    self.taramayi_durdur()
                    break
                    
                # Periyodik ilerleme kaydetme
                self.ilerleme_kaydet()
                
                # Kontrol panelini güncelle - ana thread üzerinden çağır
                if self.kontrol_panel and self.kontrol_panel.winfo_exists():
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
                    
                    # Tıklama sonrası kısa bekleme - sayfa geçişi için
                    time.sleep(0.5)  # Tıklama sonrası kısa bekleme ekle
                    
                    # Sayfa yüklenme beklemesi
                    sayfa_yuklendi = self.sayfa_yuklenmesini_bekle(True)
                    
                    # Yeni sayfa başlangıç gecikmesi - Turcademy için daha uygun bekle
                    if self.tarama_modu == "Turcademy":
                        # Turcademy için optimize edilmiş bekleme süresi
                        time.sleep(self.sayfa_gecis_gecikmesi * self.turcademy_gecis_carpani)
                    else:
                        # Nobel için ek bekleme süresi 
                        time.sleep(self.sayfa_gecis_gecikmesi)
                        
                        # Nobel için sayfa içeriğinin tamamen görünür olması için biraz daha bekle
                        time.sleep(1.0)  # Nobel modu için ekstra bekleme
                    
                    # Sayfa yüklenme bilgisi
                    if sayfa_yuklendi:
                        self.log_ekle("Yeni sayfa yüklendi.")
                    else:
                        self.log_ekle("Yeni sayfa yüklenme zaman aşımı. Devam ediliyor.")
                        # Sayfanın yüklenmesi için ek bekleme
                        time.sleep(1.0)
                        
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
                self.kontrol_panel = None  # Referansı temizle
            
            # Ana pencereyi göster
            self.root.deiconify()
            
            # Eğer otomatik PDF oluşturma seçiliyse ve tarama tamamlandıysa
            if self.otomatik_pdf.get() and self.pdf_butonunu_goster():
                self.log_ekle("Otomatik PDF oluşturma başlatılıyor...")
                self.root.after(1000, self.secili_klasordeki_goruntuleri_birlestir)
        
        return False  # Event handler'ın normal işleyişini devam ettir

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
                    if dosya.lower().endswith(".png") and dosya.startswith("sayfa_"):
                        tam_yol = os.path.join(kitap_klasoru, dosya)
                        goruntu_dosyalari.append(tam_yol)
                
                if not goruntu_dosyalari:
                    self.root.after(0, lambda: messagebox.showinfo("Bilgi", "Kitap klasöründe görüntü dosyası bulunamadı."))
                    progress_window.destroy()
                    return
                
                # ÖNEMLİ: Dosyaları sayfa numarasına göre doğru sırala
                self.log_ekle(f"PDF oluşturma için görüntüler sıralanıyor (toplam {len(goruntu_dosyalari)} dosya)")
                goruntu_dosyalari = self.goruntu_dosyalarini_sirala(goruntu_dosyalari)
                
                # Sıralanmış dosyaların sayfa numaralarını kontrol et ve göster
                sayfa_numaralari = []
                for dosya in goruntu_dosyalari[:20]:  # İlk 20 dosyayı göster
                    dosya_adi = os.path.basename(dosya)
                    sayfa_no_str = dosya_adi[len("sayfa_"):-len(".png")]
                    try:
                        sayfa_no = int(sayfa_no_str)
                        sayfa_numaralari.append(sayfa_no)
                    except ValueError:
                        sayfa_numaralari.append("?")
                
                self.log_ekle(f"Sıralanmış sayfa numaraları (ilk 20): {sayfa_numaralari}")
                
                # İlerleme bilgisi için
                toplam_dosya = len(goruntu_dosyalari)
                
                # PILLOW KULLANARAK DOĞRUDAN PDF OLUŞTUR
                goruntu_listesi = []
                
                for i, dosya in enumerate(goruntu_dosyalari):
                    # İlerleme göstergesini güncelle
                    ilerleme_yuzdesi = (i + 1) / toplam_dosya * 50  # İlk %50 yükleme için
                    self.root.after(0, lambda p=ilerleme_yuzdesi: progress_var.set(p))
                    
                    # Dosya adını ve ilerlemeyi göster
                    dosya_adi = os.path.basename(dosya)
                    self.root.after(0, lambda d=dosya_adi, i=i+1, t=toplam_dosya: 
                                 progress_label.config(text=f"Yükleniyor: {i}/{t} - {d}"))
                    
                    try:
                        img = Image.open(dosya)
                        goruntu_listesi.append(img.convert('RGB'))  # RGB formatına dönüştür
                        self.log_ekle(f"Yükleniyor ({i+1}/{toplam_dosya}): {dosya_adi}")
                    except Exception as e:
                        self.log_ekle(f"Dosya yüklenirken hata: {dosya_adi} - {e}")
                
                # Görüntü boyutlarını kontrol et
                if goruntu_listesi:
                    self.log_ekle(f"İlk görüntü boyutu: {goruntu_listesi[0].width}x{goruntu_listesi[0].height}")
                    
                    # İlk görüntüyü ayır
                    ilk_goruntu = goruntu_listesi[0]
                    diger_goruntuler = goruntu_listesi[1:] if len(goruntu_listesi) > 1 else []
                    
                    # Doğrudan save ile PDF oluştur
                    self.log_ekle("PDF oluşturuluyor...")
                    self.root.after(0, lambda: progress_label.config(text="PDF oluşturuluyor... Lütfen bekleyin..."))
                    self.root.after(0, lambda: progress_var.set(75))  # %75 ilerleme
                    
                    ilk_goruntu.save(
                        dosya_yolu, 
                        save_all=True, 
                        append_images=diger_goruntuler,
                        resolution=100.0,
                        format="PDF"
                    )
                    
                    # PDF oluşturma tamamlandı
                    self.log_ekle(f"{toplam_dosya} görüntü PDF'e dönüştürüldü: {dosya_yolu}")
                    self.root.after(0, lambda: progress_var.set(100))
                    
                    # Tamamlama mesajı göster
                    self.root.after(0, lambda: messagebox.showinfo("Başarılı", 
                        f"PDF dosyası oluşturuldu: {dosya_yolu}\n{toplam_dosya} sayfa işlendi."))
                    
                    # Kitap bilgilerini kaydet
                    kitap_bilgisi = {
                        'kitap_adi': self.aktif_kitap,
                        'sayfa_sayisi': toplam_dosya,
                        'son_islem_tarihi': time.strftime("%Y-%m-%d %H:%M:%S"),
                        'pdf_dosyasi': dosya_yolu
                    }
                    
                    self.kitap_bilgisi_kaydet(kitap_klasoru, kitap_bilgisi)
                else:
                    self.log_ekle("Yüklenecek görüntü bulunamadı!")
                    self.root.after(0, lambda: messagebox.showinfo("Bilgi", "Hiçbir görüntü yüklenemedi."))
                
            except Exception as e:
                self.log_ekle(f"PDF oluşturulurken hata: {e}")
                self.root.after(0, lambda: messagebox.showerror("Hata", f"PDF oluşturulurken hata: {e}"))
            finally:
                # Belleği temizle
                try:
                    if 'goruntu_listesi' in locals():
                        del goruntu_listesi
                    if 'ilk_goruntu' in locals():
                        del ilk_goruntu
                    if 'diger_goruntuler' in locals():
                        del diger_goruntuler
                    gc.collect()
                except:
                    pass
                
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
        
        # Mevcut sayfa durumunu tespit et ve ilerlemeyi yükle
        self.mevcut_sayfa_durumunu_tespit_et()
        self.ilerleme_yukle()
        
        self.log_ekle(f"Aktif kitap: {secilen}")
        
        # Sayfa bilgisini güncelle
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
            if png_var and not self.pdf_button_visible:
                self.pdf_button.pack(side=tk.LEFT, padx=1)
                self.pdf_button_visible = True
            elif not png_var and self.pdf_button_visible:
                self.pdf_button.pack_forget()
                self.pdf_button_visible = False
                
            return png_var
        except Exception as e:
            self.log_ekle(f"PDF butonu kontrolünde hata: {e}")
            if self.pdf_button_visible:
                self.pdf_button.pack_forget()
                self.pdf_button_visible = False
            return False
    
    def goruntu_dosyalarini_sirala(self, dosya_listesi):
        """Görüntü dosyalarını sayfa numarasına göre sıralar"""
        try:
            self.log_ekle("Görüntü dosyaları sıralanıyor...")
            
            # Dosya yollarını ve sayfa numaralarını içeren liste oluştur
            dosya_bilgileri = []
            
            for dosya_yolu in dosya_listesi:
                try:
                    # Dosya adını al
                    dosya_adi = os.path.basename(dosya_yolu)
                    
                    # Sadece geçerli sayfa dosyalarını işle
                    if not dosya_adi.startswith("sayfa_") or not dosya_adi.endswith(".png"):
                        continue
                    
                    # Sayfa numarasını çıkar
                    sayfa_no_str = dosya_adi[len("sayfa_"):-len(".png")]
                    
                    try:
                        # Sayfa numarasını tamsayıya dönüştür (sayısal sıralama için)
                        sayfa_no = int(sayfa_no_str)
                        
                        # Bilgiyi ekle
                        dosya_bilgileri.append({
                            "dosya_yolu": dosya_yolu,
                            "sayfa_no": sayfa_no,
                            "dosya_adi": dosya_adi
                        })
                    except ValueError:
                        # Sayfa numarası alınamadıysa, en sona koy
                        self.log_ekle(f"Uyarı: Sayfa numarası çözümlenemedi: {dosya_adi}")
                        dosya_bilgileri.append({
                            "dosya_yolu": dosya_yolu,
                            "sayfa_no": float('inf'),  # Sonsuz değerle sona koy
                            "dosya_adi": dosya_adi
                        })
                except Exception as e:
                    self.log_ekle(f"Dosya işlenirken hata: {e}")
                    continue
            
            # Sayfa numarasına göre (sayısal olarak) sırala
            dosya_bilgileri.sort(key=lambda x: x["sayfa_no"])
            
            # Sıralama sonrası bilgileri göster
            self.log_ekle(f"Toplam {len(dosya_bilgileri)} dosya sıralandı.")
            
            if len(dosya_bilgileri) > 0:
                ilk_10_dosya = [f"{bilgi['dosya_adi']}({bilgi['sayfa_no']})" for bilgi in dosya_bilgileri[:10]]
                self.log_ekle(f"İlk 10 dosya: {', '.join(ilk_10_dosya)}")
                
                if len(dosya_bilgileri) > 20:
                    son_10_dosya = [f"{bilgi['dosya_adi']}({bilgi['sayfa_no']})" for bilgi in dosya_bilgileri[-10:]]
                    self.log_ekle(f"Son 10 dosya: {', '.join(son_10_dosya)}")
            
            # Sadece dosya yollarını döndür
            return [bilgi["dosya_yolu"] for bilgi in dosya_bilgileri]
        
        except Exception as e:
            self.log_ekle(f"Dosyalar sıralanırken hata: {e}")
            # Hata durumunda orijinal listeyi döndür
            return dosya_listesi
    
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
        """Sayfa bilgisi etiketlerini ve ilerleme bilgisini günceller"""
        self.sayfa_label.config(text=str(self.sayfa_no))
        self.toplam_sayfa_label.config(text=str(self.toplam_sayfa))
        
        # Klasördeki gerçek dosya sayısını kontrol et ve güncelle
        try:
            if os.path.exists(self.kayit_klasoru):
                klasor_sayfa_sayisi = 0
                for dosya in os.listdir(self.kayit_klasoru):
                    if dosya.startswith("sayfa_") and dosya.endswith(".png"):
                        klasor_sayfa_sayisi += 1
                
                # Kullanıcıya bilgi ver
                bilgi_metni = f"S:{self.sayfa_no}/{self.toplam_sayfa} (K:{klasor_sayfa_sayisi}/H:{self.hedef_sayfa_sayisi})"
                self.log_ekle(bilgi_metni)
                
                # Tarama esnasında kontrol paneli varsa orada da göster
                if self.kontrol_panel and self.kontrol_panel.winfo_exists():
                    for child in self.kontrol_panel.winfo_children():
                        if isinstance(child, ttk.Frame):
                            for label in child.winfo_children():
                                if isinstance(label, ttk.Label):
                                    label.config(text=bilgi_metni)
                                    break
                            break
        except Exception as e:
            # Hata durumunda normal sayfa bilgisini göster
            pass
    
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
                
                # Girişi tekrar readonly yap
                self.baslangic_sayfa_entry.config(state='readonly')
            else:
                messagebox.showwarning("Uyarı", "Sayfa numarası 1 veya daha büyük olmalıdır.")
        except ValueError:
            messagebox.showwarning("Uyarı", "Geçerli bir sayfa numarası girin.")
        
        # Her durumda readonly yap
        self.baslangic_sayfa_entry.config(state='readonly')

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

    def kontrol_paneli_guncelle(self):
        """Kontrol panelindeki sayfa ve durum bilgilerini günceller"""
        try:
            if self.kontrol_panel and self.kontrol_panel.winfo_exists():
                # Klasördeki sayfa sayısını hesapla
                klasor_sayfa_sayisi = 0
                if os.path.exists(self.kayit_klasoru):
                    for dosya in os.listdir(self.kayit_klasoru):
                        if dosya.startswith("sayfa_") and dosya.endswith(".png"):
                            klasor_sayfa_sayisi += 1
                
                # Kısa bilgi metni oluştur
                bilgi_metni = f"S:{self.sayfa_no}/{self.toplam_sayfa}"
                
                # Panel etiketini güncelle
                if hasattr(self, 'panel_sayfa_label') and self.panel_sayfa_label.winfo_exists():
                    self.panel_sayfa_label.config(text=bilgi_metni)
        except Exception as e:
            # Hata durumunda sessizce devam et
            pass

    def sayfa_numarasi_duzenle(self):
        """Sayfa numarasını manuel olarak düzenlemeye izin verir"""
        # Readonly durumunu kaldır
        self.baslangic_sayfa_entry.config(state='normal')
        
        # Kullanıcıya uyarı ver
        self.log_ekle("Sayfa numarasını manuel olarak düzenleyebilirsiniz. Değiştirdikten sonra Enter tuşuna basın.")
        
        # Enter tuşuna basıldığında çağrılacak handler
        self.baslangic_sayfa_entry.bind("<Return>", lambda e: self.baslangic_sayfasini_guncelle())

if __name__ == "__main__":
    root = tk.Tk()
    app = EkranTarayici(root)
    root.mainloop() 