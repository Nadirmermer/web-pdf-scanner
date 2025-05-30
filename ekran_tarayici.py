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
from typing import Dict, List, Tuple, Optional, Callable, Any

class EkranTarayici:
    # --- Constants ---
    APP_TITLE: str = "Ekran Tarayıcı"
    ICON_FILE: str = "icon.ico"

    # Window dimensions
    MIN_WINDOW_WIDTH: int = 600
    MIN_WINDOW_HEIGHT: int = 500
    DEFAULT_WINDOW_WIDTH: int = 800
    DEFAULT_WINDOW_HEIGHT: int = 700

    # File names
    SETTINGS_FILE: str = "ayarlar.json"
    BOOK_INFO_FILE: str = "kitap_bilgisi.json"
    PROGRESS_FILE: str = "ilerleme.json"
    DEFAULT_BOOK_DIR_NAME: str = "Kitaplar"

    # UI Text
    LABEL_KITAP_SECIMI: str = "1. Kitap Seçimi"
    LABEL_TARAMA_MODU: str = "2. Tarama Modu"
    LABEL_TARAMA_AYARLARI: str = "3. Tarama Ayarları"
    LABEL_SAYFA_BILGISI: str = "4. Sayfa Bilgisi"
    LABEL_TARAMA_KONTROL: str = "5. Tarama Kontrol"
    LABEL_ISLEM_GUNLUGU: str = "İşlem Günlüğü"

    BUTTON_YENI: str = "Yeni"
    BUTTON_SIL: str = "Sil"
    BUTTON_PDF: str = "PDF"
    RADIO_NOBEL: str = "Nobel (Sayfa Kaydırma)"
    RADIO_TURCADEMY: str = "Turcademy (Tek Sayfa)"
    BUTTON_TARAMA_ALANI_SEC: str = "Tarama Alanı Seç"
    BUTTON_SAYFA_GECIS_NOKTASI: str = "Sayfa Geçiş Noktası"
    LABEL_BASLANGIC: str = "Başlangıç:"
    BUTTON_DUZENLE: str = "Düzenle"
    LABEL_SU_ANKI: str = "Şu anki:"
    LABEL_TOPLAM: str = "Toplam:"
    LABEL_HEDEF: str = "Hedef:"
    BUTTON_AYARLA: str = "Ayarla"
    LABEL_KLASOR: str = "Klasör:"
    BUTTON_BASLAT: str = "▶️ BAŞLAT"
    BUTTON_DURDUR: str = "⏹️ DURDUR"
    CHECKBOX_OTOMATIK_PDF: str = "Tarama sonrası PDF oluştur"
    INFO_ESC_DURDUR: str = "ESC tuşu: Taramayı durdur"

    # Keyboard keys
    KEY_ESC: str = "esc"

    # Log Messages (used in _tarama_sayfa_islemi and others)
    LOG_ESC_BASILDI: str = "ESC tuşuna basıldı. Tarama durduruluyor..."
    LOG_HEDEF_SAYFA_ULASILDI: str = "Hedef sayfa sayısına ({}) ulaşıldı. Tarama durduruluyor."
    LOG_YENI_SAYFA_YUKLENIYOR: str = "Yeni sayfa yükleniyor..."
    LOG_YENI_SAYFA_YUKLENDI: str = "Yeni sayfa yüklendi."
    LOG_YENI_SAYFA_ZAMAN_ASIMI: str = "Yeni sayfa yüklenme zaman aşımı. Devam ediliyor."
    LOG_SAYFA_TARAMA_HATASI: str = "Sayfa tarama hatası: {}. Sonraki sayfaya geçiliyor..."
    LOG_TARAMA_KRITIK_HATA: str = "Tarama sırasında kritik hata: {}"
    LOG_BILINMEYEN_TARAMA_MODU: str = "Bilinmeyen tarama modu: {}"
    DEFAULT_EKRAN_TARAMA_DIR: str = "Ekran_Tarama"

    # MessageBox Titles
    TITLE_UYARI: str = "Uyarı"
    TITLE_HATA: str = "Hata"
    TITLE_BILGI: str = "Bilgi"
    TITLE_ONAY: str = "Onay"
    TITLE_BASARILI: str = "Başarılı"

    # File Dialog
    FILETYPE_PDF: Tuple[str, str] = ("PDF Dosyaları", "*.pdf")
    DIALOG_TITLE_PDF_KAYDET: str = "PDF'i Kaydet"

    # PDF Creation
    PDF_PROGRESS_TITLE: str = "PDF Oluşturuluyor"
    PDF_PROGRESS_GEOMETRY: str = "400x150"
    PDF_PROGRESS_MAIN_LABEL: str = "PDF dosyası oluşturuluyor..."
    PDF_PROGRESS_PREPARING_LABEL: str = "Hazırlanıyor..."
    PDF_PROGRESS_LOADING_LABEL: str = "Yükleniyor: {}/{} - {}"
    PDF_PROGRESS_SAVING_LABEL: str = "PDF oluşturuluyor... Lütfen bekleyin..."
    LOG_PDF_IMAGE_LOADING: str = "Yükleniyor ({}/{}): {}"
    LOG_PDF_IMAGE_LOAD_ERROR: str = "Dosya yüklenirken hata: {} - {}"
    LOG_PDF_NO_IMAGES_TO_LOAD: str = "Yüklenecek görüntü bulunamadı!"
    LOG_PDF_SAVING_ERROR: str = "PDF kaydedilirken hata: {}"
    LOG_PDF_GENERAL_ERROR: str = "PDF oluşturulurken genel hata: {}"
    INFO_PDF_NO_IMAGES_FOUND_IN_DIR: str = "Kitap klasöründe görüntü dosyası bulunamadı."
    INFO_PDF_NO_IMAGES_LOADED: str = "Hiçbir görüntü yüklenemedi."
    LOG_PDF_IMAGES_SORTING: str = "PDF oluşturma için görüntüler sıralanıyor (toplam {} dosya)"
    LOG_PDF_FIRST_IMAGE_SIZE: str = "İlk görüntü boyutu: {}x{}"
    LOG_PDF_CREATING: str = "PDF oluşturuluyor..."
    LOG_PDF_SAVED_SUCCESS: str = "{} görüntü PDF'e dönüştürüldü: {}"
    INFO_PDF_SAVED_SUCCESS_MSG: str = "PDF dosyası oluşturuldu: {}\n{} sayfa işlendi."
    DATE_FORMAT_STANDARD: str = "%Y-%m-%d %H:%M:%S"
    IMAGE_FORMAT_RGB: str = "RGB"
    PDF_SAVE_FORMAT: str = "PDF"
    PDF_RESOLUTION: float = 100.0

    # File Handling
    IMAGE_FILE_EXTENSION: str = ".png"
    IMAGE_FILE_PREFIX: str = "sayfa_"
    DEFAULT_ENCODING: str = "utf-8"

    # Log Messages - General
    LOG_KITAP_BILGISI_KAYDEDILDI: str = "Kitap bilgileri kaydedildi."
    LOG_KITAP_BILGISI_KAYDETME_HATA: str = "Kitap bilgileri kaydedilirken hata: {}"
    LOG_KITAP_BILGILERI_OKUMA_HATA: str = "Kitap bilgileri okunurken hata: {}"
    ERROR_KITAP_KLASORU_BULUNAMADI: str = "Kitap klasörü bulunamadı."
    LOG_ILERLEME_YUKLENDI: str = "İlerleme dosyası yüklendi. Sonraki sayfa: {}"
    LOG_ILERLEME_YUKLEME_HATA: str = "İlerleme yüklenirken hata: {}"
    LOG_MEVCUT_SAYFA_TESPIT: str = "Klasördeki en yüksek sayfa numarası: {}, tarama {}. sayfadan devam edecek"
    LOG_MEVCUT_SAYFA_BULUNAMADI: str = "Klasörde sayfa bulunamadı, tarama 1. sayfadan başlayacak"
    LOG_SAYFA_DURUMU_TESPIT_HATA: str = "Sayfa durumu tespit edilirken hata: {}"
    LOG_ILERLEME_KAYDEDILDI: str = "İlerleme kaydedildi: {} - {}. sayfa"
    LOG_ILERLEME_KAYDETME_HATA: str = "İlerleme kaydedilirken hata: {}"
    LOG_AYAR_YUKLEME_HATA: str = "Ayarlar yüklenirken hata: {}"
    LOG_AYAR_KAYDETME_HATA: str = "Ayarlar kaydedilirken hata: {}"
    LOG_TARAMA_ALANI_SECILDI: str = "Tarama alanı: ({},{})-({},{})"
    LOG_TARAMA_ALANI_SECIM_HATA: str = "Tarama alanı seçilirken hata: {}"
    LOG_TIKLAMA_NOKTASI_SECILDI: str = "Tıklama noktası: ({},{})"
    LOG_TIKLAMA_NOKTASI_SECIM_HATA: str = "Tıklama noktası seçilirken hata: {}"
    LOG_GERI_SAYIM_BASLADI: str = "Tarama {} saniye içinde başlayacak..."
    LOG_TARAMA_MODU_BILGI: str = "Tarama modu: {}"
    LOG_GERI_SAYIM: str = "{}..."
    LOG_TARAMA_BASLATILIYOR: str = "Tarama başlatılıyor..."
    LOG_TARAMA_DURAKLATILDI: str = "Tarama duraklatıldı. Devam etmek için '▶️' butonuna tıklayın."
    LOG_TARAMA_DEVAM_ETTIRILIYOR: str = "Tarama devam ediyor..."
    LOG_SAYFA_SONUNA_ULASILDI: str = "Sayfanın sonuna ulaşıldı."
    LOG_KAYDIRMA_HATASI: str = "Kaydırma hatası: {}"
    LOG_SAYFA_TARANDI: str = "Sayfa {} tarandı."
    LOG_TARAMA_DURDURULUYOR: str = "Tarama durduruluyor..."
    LOG_OTOMATIK_PDF_OLUSTURULUYOR: str = "Otomatik PDF oluşturma başlatılıyor..."
    LOG_GORUNTU_SIRALANIYOR: str = "Görüntü dosyaları sıralanıyor..."
    LOG_GORUNTU_SIRALAMA_HATA: str = "Dosyalar sıralanırken hata: {}"
    LOG_SAYFA_NO_COZUMLEME_UYARI: str = "Uyarı: Sayfa numarası çözümlenemedi: {}"
    LOG_DOSYA_ISLEME_HATA: str = "Dosya işlenirken hata: {}"
    LOG_TOPLAM_DOSYA_SIRALANDI: str = "Toplam {} dosya sıralandı."
    LOG_ILK_10_DOSYA: str = "İlk 10 dosya: {}"
    LOG_SON_10_DOSYA: str = "Son 10 dosya: {}"
    LOG_YENI_KITAP_KLASORU_OLUSTURULDU: str = "Yeni kitap klasörü oluşturuldu: {}"
    LOG_TARAMA_MODU_DEGISTI: str = "Tarama modu değiştirildi: {}"
    LOG_SAYFA_YUKLEME_KONTROL_HATA: str = "Sayfa yüklenme kontrolünde hata: {}"
    LOG_EKRAN_GORUNTUSU_HATA: str = "Ekran görüntüsü alınırken hata: {}"
    LOG_SAYFA_KAYDET_HATA: str = "Sayfa kaydedilirken hata: {}"
    LOG_SAYFA_KAYDEDILDI: str = "Sayfa {} kaydedildi: {}"
    LOG_GORUNTU_BENZERLIK_HATA: str = "Görüntü benzerlik hesaplama hatası: {}"
    LOG_GORUNTU_BIRLESTIRME_HATA: str = "Görüntüler birleştirilirken hata: {}"
    LOG_BASLANGIC_SAYFA_GUNCELLENDI: str = "Başlangıç sayfa numarası {} olarak ayarlandı."
    LOG_OZEL_AYAR_KAYDETME_HATA: str = "Özel ayar kaydedilirken hata: {}"
    LOG_HEDEF_SAYFA_GUNCELLENDI: str = "Hedef sayfa sayısı {} olarak ayarlandı."
    LOG_SAYFA_NO_DUZENLEME_BILGI: str = "Sayfa numarasını manuel olarak düzenleyebilirsiniz. Değiştirdikten sonra Enter tuşuna basın."
    LOG_PDF_BUTON_KONTROL_HATA: str = "PDF butonu kontrolünde hata: {}"

    # Dialog Geometries & Widths
    YENI_KITAP_DIALOG_GEOMETRY: str = "400x150"
    YENI_KITAP_ADI_ENTRY_WIDTH: int = 30
    HOS_GELDINIZ_DIALOG_GEOMETRY: str = "550x400"
    HOS_GELDINIZ_TEXT_HEIGHT: int = 15
    INFO_LABEL_FONT: Tuple[str, int] = ('Segoe UI', 8)
    PAGE_INFO_FONT: Tuple[str, int, str] = ('Segoe UI', 9, 'bold')
    LOG_TEXT_FONT: Tuple[str, int] = ('Segoe UI', 8)
    CONTROL_PANEL_GEOMETRY_PARTS: str = "50x120"
    CONTROL_PANEL_OFFSET_X: int = 60
    CONTROL_PANEL_OFFSET_Y: int = 10
    CONTROL_PANEL_BUTTON_WIDTH: int = 3
    CONTROL_PANEL_PAUSE_ICON: str = "⏸️"
    CONTROL_PANEL_RESUME_ICON: str = "▶️"
    CONTROL_PANEL_STOP_ICON: str = "⏹️"
    CONTROL_PANEL_PAUSED_DISPLAY_TEXT: str = "⏸️ DURAKLATILDI"
    SIMILARITY_RESIZE_DIM: Tuple[int, int] = (50, 50)
    SIMILARITY_PIXEL_DIFF_THRESHOLD: int = 30
    PAGE_PART_OVERLAP_PIXELS: int = 50
    PAGE_PART_OVERLAP_RATIO: float = 0.1
    PAGE_PART_MATCH_SAMPLE_STEP_BIG: int = 10
    PAGE_PART_MATCH_SAMPLE_STEP_SMALL: int = 20
    SCROLL_KEY: str = "pagedown"
    # SCROLL_SLEEP_DURATION will be self.page_scroll_delay
    # SIMILARITY_THRESHOLD_HIGH will be self.similarity_threshold_nobel_end
    # SIMILARITY_THRESHOLD_LOW will be self.similarity_threshold_page_load_turcademy
    # SIMILARITY_THRESHOLD_NOBEL_LOAD will be self.similarity_threshold_page_load_nobel
    SIMILARITY_REPEAT_COUNT: int = 2
    PAGE_LOAD_STABILITY_COUNT_TURCADEMY: int = 1
    PAGE_LOAD_STABILITY_COUNT_NOBEL: int = 1
    CLICK_POST_SLEEP_DURATION: float = 0.5
    NOBEL_EXTRA_LOAD_SLEEP: float = 1.0
    ERROR_WAIT_SLEEP: float = 2.0
    GC_COLLECT_INTERVAL: int = 10
    AUTO_PDF_DELAY_MS: int = 1000
    BASLANGIC_BILGI_GOSTER_KEY: str = "baslangic_bilgi_goster"

    # Default values for configurable parameters
    DEFAULT_MAX_LOAD_WAIT_TIME: float = 5.0
    DEFAULT_PAGE_TRANSITION_DELAY: float = 1.5
    DEFAULT_TURCADEMY_DELAY_MULTIPLIER: float = 1.2
    DEFAULT_PAGE_SCROLL_DELAY: float = 0.3
    DEFAULT_SIMILARITY_THRESHOLD_NOBEL_END: int = 97
    DEFAULT_SIMILARITY_THRESHOLD_PAGE_LOAD_TURCADEMY: int = 85
    DEFAULT_SIMILARITY_THRESHOLD_PAGE_LOAD_NOBEL: int = 90

    # Tarama Modları
    TARAMA_MODU_NOBEL: str = "Nobel"
    TARAMA_MODU_TURCADEMY: str = "Turcademy"

    # Padding
    PAD_SMALL: int = 2
    PAD_MEDIUM: int = 5
    PAD_LARGE: int = 10
    PAD_XLARGE: int = 20

    def __init__(self, root: tk.Tk) -> None:
        self.root: tk.Tk = root
        self.root.title(self.APP_TITLE)
        # Minimum pencere boyutu belirle
        self.root.minsize(self.MIN_WINDOW_WIDTH, self.MIN_WINDOW_HEIGHT)
        # Dinamik pencere boyutu
        self.root.geometry(f"{self.DEFAULT_WINDOW_WIDTH}x{self.DEFAULT_WINDOW_HEIGHT}")
        # Pencerenin yeniden boyutlandırılmasına izin ver
        self.root.resizable(True, True)
        self.root.attributes('-topmost', True)
        
        # Program ikonu
        try:
            icon_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.ICON_FILE)
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass  # İkon yoksa geç
        
        # Ana değişkenler
        self.tarama_alani: Dict[str, int] = {'x1': 0, 'y1': 0, 'x2': 500, 'y2': 800}
        self.tiklanacak_nokta: Dict[str, int] = {'x': 500, 'y': 500}
        self.devam_ediyor: bool = False
        self.sayfa_no: int = 1
        self.toplam_sayfa: int = 1
        self.hedef_sayfa_sayisi: int = 300
        self.sayfa_parcalari: List[Image.Image] = [] # Assuming PIL.Image.Image
        self.son_goruntu: Optional[Image.Image] = None # Assuming PIL.Image.Image
        self.sayfa_sonu_bekleme_suresi: float = 0.3
        self.ayni_sayfa_sayisi: int = 0
        self.kayit_klasoru: str = os.path.join(os.path.expanduser("~"), self.DEFAULT_EKRAN_TARAMA_DIR)
        self.aktif_kitap: str = ""
        self.tarama_modu: str = self.TARAMA_MODU_NOBEL
        self.otomatik_pdf: tk.BooleanVar = tk.BooleanVar(value=False)
        self.kontrol_panel: Optional[tk.Toplevel] = None
        self.tarama_duraklatildi: bool = False

        # Configurable parameters with defaults from class constants
        self.max_load_wait_time: float = self.DEFAULT_MAX_LOAD_WAIT_TIME
        self.page_transition_delay: float = self.DEFAULT_PAGE_TRANSITION_DELAY
        self.turcademy_delay_multiplier: float = self.DEFAULT_TURCADEMY_DELAY_MULTIPLIER
        self.page_scroll_delay: float = self.DEFAULT_PAGE_SCROLL_DELAY
        self.similarity_threshold_nobel_end: int = self.DEFAULT_SIMILARITY_THRESHOLD_NOBEL_END
        self.similarity_threshold_page_load_turcademy: int = self.DEFAULT_SIMILARITY_THRESHOLD_PAGE_LOAD_TURCADEMY
        self.similarity_threshold_page_load_nobel: int = self.DEFAULT_SIMILARITY_THRESHOLD_PAGE_LOAD_NOBEL

        # The following were previously set directly, now using the configurable self.page_transition_delay
        # self.sayfa_gecis_gecikmesi: float = 1.5 # This is now self.page_transition_delay
        # self.turcademy_gecis_carpani: float = 1.2 # This is now self.turcademy_delay_multiplier

        self.kitaplar_klasoru: str = os.path.join(self.kayit_klasoru, self.DEFAULT_BOOK_DIR_NAME)
        if not os.path.exists(self.kitaplar_klasoru):
            os.makedirs(self.kitaplar_klasoru)
        
        # Kayıt klasörünü oluştur
        if not os.path.exists(self.kayit_klasoru):
            os.makedirs(self.kayit_klasoru)
        
        # Yapılandırma dosyası
        self.config_dosyasi: str = os.path.join(self.kayit_klasoru, self.SETTINGS_FILE)
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
        self.root.after(500, self.bilgi_kontrolu) # 500ms delay
    
    def set_styles(self) -> None:
        """Uygulamanın genel tema ve stil ayarlarını yapar"""
        style: ttk.Style = ttk.Style()
        
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
    
    def on_kapat(self) -> None:
        """Uygulama kapatılırken çağrılır"""
        if self.devam_ediyor:
            self.taramayi_durdur()
        self.ilerleme_kaydet()
        self.root.destroy()
    
    def ilerleme_yukle(self) -> None:
        """Önceki ilerlemeyi yükler"""
        try:
            # Önce klasördeki mevcut sayfa dosyalarını kontrol et
            self.mevcut_sayfa_durumunu_tespit_et()
            
            if hasattr(self, 'ilerleme_dosyasi') and os.path.exists(self.ilerleme_dosyasi):
                with open(self.ilerleme_dosyasi, 'r') as f:
                    ilerleme: Dict[str, Any] = json.load(f)
                    self.toplam_sayfa = ilerleme.get('toplam_sayfa', 1)
                    
                    if self.sayfa_no > self.toplam_sayfa:
                        self.toplam_sayfa = self.sayfa_no
                    
                    self.log_ekle(self.LOG_ILERLEME_YUKLENDI.format(self.sayfa_no))
                
                if hasattr(self, 'baslangic_sayfa_entry'):
                    self.baslangic_sayfa_entry.delete(0, tk.END)
                    self.baslangic_sayfa_entry.insert(0, str(self.sayfa_no))
                
                self.sayfa_bilgisi_guncelle()
                
        except Exception as e:
            self.log_ekle(self.LOG_ILERLEME_YUKLEME_HATA.format(e))
    
    def mevcut_sayfa_durumunu_tespit_et(self) -> None:
        """Klasördeki mevcut son sayfa numarasını tespit eder ve taramaya oradan devam eder"""
        try:
            if not self.aktif_kitap or not os.path.exists(self.kayit_klasoru):
                self.sayfa_no = 1
                return
                
            en_yuksek_sayfa: int = 0
            sayfa_dosyalari: List[str] = []
            
            for dosya in os.listdir(self.kayit_klasoru):
                if dosya.startswith(self.IMAGE_FILE_PREFIX) and dosya.endswith(self.IMAGE_FILE_EXTENSION):
                    sayfa_dosyalari.append(dosya)
            
            for dosya in sayfa_dosyalari:
                try:
                    sayfa_no_str: str = dosya.replace(self.IMAGE_FILE_PREFIX, "").replace(self.IMAGE_FILE_EXTENSION, "")
                    sayfa_no_int: int = int(sayfa_no_str)
                    if sayfa_no_int > en_yuksek_sayfa:
                        en_yuksek_sayfa = sayfa_no_int
                except ValueError:
                    continue
            
            if en_yuksek_sayfa > 0:
                self.sayfa_no = en_yuksek_sayfa + 1
                self.toplam_sayfa = max(self.toplam_sayfa, en_yuksek_sayfa)
                self.log_ekle(self.LOG_MEVCUT_SAYFA_TESPIT.format(en_yuksek_sayfa, self.sayfa_no))
            else:
                self.sayfa_no = 1
                self.log_ekle(self.LOG_MEVCUT_SAYFA_BULUNAMADI)
                
            self.sayfa_bilgisi_guncelle()
                
        except Exception as e:
            self.log_ekle(self.LOG_SAYFA_DURUMU_TESPIT_HATA.format(e))
            self.sayfa_no = 1
    
    def ilerleme_kaydet(self) -> None:
        """Mevcut ilerlemeyi kaydeder"""
        if not self.aktif_kitap:
            messagebox.showwarning(self.TITLE_UYARI, self.WARNING_KITAP_SECIMI_YOK)
            return
            
        if not hasattr(self, 'ilerleme_dosyasi'):
             self.ilerleme_dosyasi = os.path.join(self.kayit_klasoru, self.PROGRESS_FILE)

        try:
            with open(self.ilerleme_dosyasi, 'w') as f:
                json.dump({
                    'son_sayfa': self.sayfa_no - 1,
                    'toplam_sayfa': self.toplam_sayfa,
                    'kitap_adi': self.aktif_kitap,
                    'tarih': time.strftime(self.DATE_FORMAT_STANDARD)
                }, f)
            self.log_ekle(self.LOG_ILERLEME_KAYDEDILDI.format(self.aktif_kitap, self.sayfa_no - 1))
        except Exception as e:
            self.log_ekle(self.LOG_ILERLEME_KAYDETME_HATA.format(e))
    
    def ayarlari_yukle(self) -> None:
        try:
            if os.path.exists(self.config_dosyasi):
                with open(self.config_dosyasi, 'r', encoding=self.DEFAULT_ENCODING) as f: # Added encoding
                    ayarlar: Dict[str, Any] = json.load(f)
                    self.tarama_alani = ayarlar.get('tarama_alani', self.tarama_alani)
                    self.tiklanacak_nokta = ayarlar.get('tiklanacak_nokta', self.tiklanacak_nokta)
                    # self.sayfa_sonu_bekleme_suresi = float(ayarlar.get('sayfa_sonu_bekleme_suresi', self.sayfa_sonu_bekleme_suresi)) # Example if made configurable
                    self.tarama_modu = ayarlar.get('tarama_modu', self.tarama_modu)
                    self.otomatik_pdf.set(ayarlar.get('otomatik_pdf', self.otomatik_pdf.get())) # Keep current if not in file
                    self.hedef_sayfa_sayisi = int(ayarlar.get('hedef_sayfa_sayisi', self.hedef_sayfa_sayisi))

                    # Load new configurable parameters
                    self.max_load_wait_time = float(ayarlar.get('max_load_wait_time', self.DEFAULT_MAX_LOAD_WAIT_TIME))
                    self.page_transition_delay = float(ayarlar.get('page_transition_delay', self.DEFAULT_PAGE_TRANSITION_DELAY))
                    self.turcademy_delay_multiplier = float(ayarlar.get('turcademy_delay_multiplier', self.DEFAULT_TURCADEMY_DELAY_MULTIPLIER))
                    self.page_scroll_delay = float(ayarlar.get('page_scroll_delay', self.DEFAULT_PAGE_SCROLL_DELAY))
                    self.similarity_threshold_nobel_end = int(ayarlar.get('similarity_threshold_nobel_end', self.DEFAULT_SIMILARITY_THRESHOLD_NOBEL_END))
                    self.similarity_threshold_page_load_turcademy = int(ayarlar.get('similarity_threshold_page_load_turcademy', self.DEFAULT_SIMILARITY_THRESHOLD_PAGE_LOAD_TURCADEMY))
                    self.similarity_threshold_page_load_nobel = int(ayarlar.get('similarity_threshold_page_load_nobel', self.DEFAULT_SIMILARITY_THRESHOLD_PAGE_LOAD_NOBEL))

        except (IOError, json.JSONDecodeError) as e: # More specific exceptions
            print(self.LOG_AYAR_YUKLEME_HATA.format(f"Dosya/JSON Hatası: {e}"))
        except Exception as e: # General fallback
            print(self.LOG_AYAR_YUKLEME_HATA.format(e))
    
    def ayarlari_kaydet(self) -> None:
        try:
            config_data: Dict[str, Any] = {
                'tarama_alani': self.tarama_alani,
                'tiklanacak_nokta': self.tiklanacak_nokta,
                'sayfa_sonu_bekleme_suresi': self.sayfa_sonu_bekleme_suresi,
                'tarama_modu': self.tarama_modu,
                'otomatik_pdf': self.otomatik_pdf.get(),
                'hedef_sayfa_sayisi': self.hedef_sayfa_sayisi,
                # Save new configurable parameters
                'max_load_wait_time': self.max_load_wait_time,
                'page_transition_delay': self.page_transition_delay,
                'turcademy_delay_multiplier': self.turcademy_delay_multiplier,
                'page_scroll_delay': self.page_scroll_delay,
                'similarity_threshold_nobel_end': self.similarity_threshold_nobel_end,
                'similarity_threshold_page_load_turcademy': self.similarity_threshold_page_load_turcademy,
                'similarity_threshold_page_load_nobel': self.similarity_threshold_page_load_nobel,
            }
            with open(self.config_dosyasi, 'w', encoding=self.DEFAULT_ENCODING) as f: # Added encoding
                json.dump(config_data, f, indent=4)
        except (IOError, OSError) as e: # More specific exceptions
            print(self.LOG_AYAR_KAYDETME_HATA.format(f"Dosya Hatası: {e}"))
        except Exception as e: # General fallback
            print(self.LOG_AYAR_KAYDETME_HATA.format(e))
    
    def _create_kitap_secimi_widgets(self, parent_frame: ttk.Frame) -> None:
        kitap_frame: ttk.LabelFrame = ttk.LabelFrame(parent_frame, text=self.LABEL_KITAP_SECIMI, padding=self.PAD_SMALL)
        kitap_frame.grid(row=0, column=0, sticky="ew", pady=self.PAD_SMALL)
        kitap_frame.columnconfigure(1, weight=1)
        
        self.kitap_combobox: ttk.Combobox = ttk.Combobox(kitap_frame, width=40, state="readonly")
        self.kitap_combobox.pack(side=tk.LEFT, padx=self.PAD_SMALL, pady=self.PAD_SMALL, fill=tk.X, expand=True)
        self.kitap_combobox.bind("<<ComboboxSelected>>", lambda e: self.kitap_sec())
        
        buton_frame_kitap: ttk.Frame = ttk.Frame(kitap_frame)
        buton_frame_kitap.pack(side=tk.RIGHT, padx=self.PAD_SMALL, pady=self.PAD_SMALL)

        ttk.Button(buton_frame_kitap, text=self.BUTTON_YENI, command=self.yeni_kitap_ekle,
                 width=5).pack(side=tk.LEFT, padx=self.PAD_SMALL) # MODIFIED padx
        ttk.Button(buton_frame_kitap, text=self.BUTTON_SIL, command=self.kitap_sil,
                 width=5).pack(side=tk.LEFT, padx=self.PAD_SMALL) # MODIFIED padx
        self.pdf_button: ttk.Button = ttk.Button(buton_frame_kitap, text=self.BUTTON_PDF,
                                   command=self.secili_klasordeki_goruntuleri_birlestir,
                                   width=5)
        self.pdf_button.pack(side=tk.LEFT, padx=self.PAD_SMALL) # MODIFIED padx
        self.pdf_button_visible: bool = False
        if not self.pdf_button_visible:
            self.pdf_button.pack_forget()

    def _create_tarama_modu_widgets(self, parent_frame: ttk.Frame) -> None:
        tarama_modu_frame: ttk.LabelFrame = ttk.LabelFrame(parent_frame, text=self.LABEL_TARAMA_MODU, padding=self.PAD_SMALL)
        tarama_modu_frame.grid(row=1, column=0, sticky="ew", pady=self.PAD_SMALL)

        self.tarama_modu_var: tk.StringVar = tk.StringVar(value=self.tarama_modu)
        modu_frame: ttk.Frame = ttk.Frame(tarama_modu_frame)
        modu_frame.pack(fill=tk.X, padx=self.PAD_SMALL, pady=self.PAD_SMALL)

        ttk.Radiobutton(modu_frame, text=self.RADIO_NOBEL,
                       value=self.TARAMA_MODU_NOBEL, variable=self.tarama_modu_var,
                       command=self.tarama_modu_degisti).pack(side=tk.LEFT, padx=self.PAD_LARGE)
        ttk.Radiobutton(modu_frame, text=self.RADIO_TURCADEMY,
                       value=self.TARAMA_MODU_TURCADEMY, variable=self.tarama_modu_var,
                       command=self.tarama_modu_degisti).pack(side=tk.LEFT, padx=self.PAD_LARGE)

    def _create_ayarlar_widgets(self, parent_frame: ttk.Frame) -> None:
        ayarlar_frame: ttk.LabelFrame = ttk.LabelFrame(parent_frame, text=self.LABEL_TARAMA_AYARLARI, padding=self.PAD_SMALL)
        ayarlar_frame.grid(row=2, column=0, sticky="ew", pady=self.PAD_SMALL)

        ayarlar_ic_frame: ttk.Frame = ttk.Frame(ayarlar_frame)
        ayarlar_ic_frame.pack(fill=tk.X, padx=self.PAD_SMALL, pady=self.PAD_SMALL)

        sol_frame: ttk.Frame = ttk.Frame(ayarlar_ic_frame)
        sol_frame.pack(side=tk.LEFT, fill=tk.Y, padx=self.PAD_MEDIUM)
        ttk.Button(sol_frame, text=self.BUTTON_TARAMA_ALANI_SEC,
                  command=self.tarama_alani_sec,
                  width=15).pack(side=tk.TOP, pady=self.PAD_SMALL) # MODIFIED pady
        self.koordinat_label: ttk.Label = ttk.Label(sol_frame,
                             text=f"({self.tarama_alani['x1']},{self.tarama_alani['y1']})-({self.tarama_alani['x2']},{self.tarama_alani['y2']})",
                             style='Info.TLabel', font=('Segoe UI', 8))
        self.koordinat_label.pack(side=tk.TOP, pady=self.PAD_SMALL) # MODIFIED pady

        sag_frame: ttk.Frame = ttk.Frame(ayarlar_ic_frame)
        sag_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=self.PAD_MEDIUM)
        ttk.Button(sag_frame, text=self.BUTTON_SAYFA_GECIS_NOKTASI,
                  command=self.tikla_nokta_sec,
                  width=15).pack(side=tk.TOP, pady=self.PAD_SMALL) # MODIFIED pady
        self.nokta_label: ttk.Label = ttk.Label(sag_frame,
                         text=f"({self.tiklanacak_nokta['x']},{self.tiklanacak_nokta['y']})",
                         style='Info.TLabel', font=('Segoe UI', 8))
        self.nokta_label.pack(side=tk.TOP, pady=self.PAD_SMALL) # MODIFIED pady

    def _create_sayfa_bilgisi_widgets(self, parent_frame: ttk.Frame) -> None:
        sayfa_frame: ttk.LabelFrame = ttk.LabelFrame(parent_frame, text=self.LABEL_SAYFA_BILGISI, padding=self.PAD_SMALL)
        sayfa_frame.grid(row=3, column=0, sticky="ew", pady=self.PAD_SMALL)
        
        sayfa_bilgi_frame: ttk.Frame = ttk.Frame(sayfa_frame)
        sayfa_bilgi_frame.pack(fill=tk.X, padx=self.PAD_SMALL, pady=self.PAD_SMALL)
        
        ttk.Label(sayfa_bilgi_frame, text=self.LABEL_BASLANGIC).pack(side=tk.LEFT, padx=self.PAD_SMALL)
        self.baslangic_sayfa_var: tk.StringVar = tk.StringVar(value=str(self.sayfa_no))
        self.baslangic_sayfa_entry: ttk.Entry = ttk.Entry(sayfa_bilgi_frame, textvariable=self.baslangic_sayfa_var, width=4, state='readonly')
        self.baslangic_sayfa_entry.pack(side=tk.LEFT)
        ttk.Button(sayfa_bilgi_frame, text=self.BUTTON_DUZENLE, command=self.sayfa_numarasi_duzenle,
                 width=6).pack(side=tk.LEFT, padx=self.PAD_SMALL)
        
        ttk.Label(sayfa_bilgi_frame, text=self.LABEL_SU_ANKI).pack(side=tk.LEFT, padx=(self.PAD_LARGE, self.PAD_SMALL))
        self.sayfa_label: ttk.Label = ttk.Label(sayfa_bilgi_frame, text=str(self.sayfa_no), font=('Segoe UI', 9, 'bold'))
        self.sayfa_label.pack(side=tk.LEFT, padx=self.PAD_SMALL)
        
        ttk.Label(sayfa_bilgi_frame, text=self.LABEL_TOPLAM).pack(side=tk.LEFT, padx=(self.PAD_LARGE, self.PAD_SMALL))
        self.toplam_sayfa_label: ttk.Label = ttk.Label(sayfa_bilgi_frame, text=str(self.toplam_sayfa), font=('Segoe UI', 9, 'bold'))
        self.toplam_sayfa_label.pack(side=tk.LEFT, padx=self.PAD_SMALL)
        
        ttk.Label(sayfa_bilgi_frame, text=self.LABEL_HEDEF).pack(side=tk.LEFT, padx=(self.PAD_LARGE, self.PAD_SMALL))
        self.hedef_sayfa_var: tk.StringVar = tk.StringVar(value=str(self.hedef_sayfa_sayisi))
        self.hedef_sayfa_entry: ttk.Entry = ttk.Entry(sayfa_bilgi_frame, textvariable=self.hedef_sayfa_var, width=4)
        self.hedef_sayfa_entry.pack(side=tk.LEFT)
        self.hedef_sayfa_entry.bind("<Return>", lambda e: self.hedef_sayfasini_guncelle())
        ttk.Button(sayfa_bilgi_frame, text=self.BUTTON_AYARLA,
                  command=self.hedef_sayfasini_guncelle,
                  width=6).pack(side=tk.LEFT, padx=self.PAD_SMALL)

        klasor_bilgi_frame: ttk.Frame = ttk.Frame(sayfa_frame)
        klasor_bilgi_frame.pack(fill=tk.X, padx=self.PAD_SMALL, pady=(0, self.PAD_SMALL))
        ttk.Label(klasor_bilgi_frame, text=self.LABEL_KLASOR,
                style='Info.TLabel', font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=self.PAD_SMALL)
        self.klasor_label: ttk.Label = ttk.Label(klasor_bilgi_frame, text=self.kayit_klasoru,
                                   style='Info.TLabel', font=('Segoe UI', 8))
        self.klasor_label.pack(side=tk.LEFT, padx=self.PAD_SMALL)

    def _create_tarama_kontrol_widgets(self, parent_frame: ttk.Frame) -> None:
        kontrol_frame: ttk.LabelFrame = ttk.LabelFrame(parent_frame, text=self.LABEL_TARAMA_KONTROL, padding=self.PAD_SMALL)
        kontrol_frame.grid(row=4, column=0, sticky="ew", pady=self.PAD_SMALL)
        
        buton_kontrol_frame: ttk.Frame = ttk.Frame(kontrol_frame)
        buton_kontrol_frame.pack(fill=tk.X, padx=self.PAD_SMALL, pady=self.PAD_SMALL)
        
        baslat_frame: ttk.Frame = ttk.Frame(buton_kontrol_frame)
        baslat_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.baslat_btn: ttk.Button = ttk.Button(baslat_frame, text=self.BUTTON_BASLAT,
                                    command=self.taramayi_baslat)
        self.baslat_btn.pack(side=tk.LEFT, padx=self.PAD_SMALL, fill=tk.X, expand=True)
        self.durdur_btn: ttk.Button = ttk.Button(baslat_frame, text=self.BUTTON_DURDUR,
                                    command=self.taramayi_durdur,
                                    state=tk.DISABLED)
        self.durdur_btn.pack(side=tk.LEFT, padx=self.PAD_SMALL, fill=tk.X, expand=True)
        
        pdf_frame: ttk.Frame = ttk.Frame(buton_kontrol_frame)
        pdf_frame.pack(side=tk.RIGHT, fill=tk.Y)
        ttk.Checkbutton(pdf_frame, text=self.CHECKBOX_OTOMATIK_PDF,
                      variable=self.otomatik_pdf,
                      command=self.ayarlari_kaydet).pack(side=tk.RIGHT, padx=self.PAD_SMALL)
        
        ttk.Label(kontrol_frame, text=self.INFO_ESC_DURDUR,
                 style='Info.TLabel', font=('Segoe UI', 8)).pack(pady=(0, self.PAD_SMALL))

    def _create_log_widgets(self, parent_frame: ttk.Frame) -> None:
        log_frame: ttk.LabelFrame = ttk.LabelFrame(parent_frame, text=self.LABEL_ISLEM_GUNLUGU, padding=self.PAD_SMALL)
        log_frame.grid(row=5, column=0, sticky="nsew", pady=self.PAD_SMALL)
        
        log_container: ttk.Frame = ttk.Frame(log_frame)
        log_container.pack(fill=tk.BOTH, expand=True, padx=self.PAD_SMALL, pady=self.PAD_SMALL)
        
        self.log_text: tk.Text = tk.Text(log_container, height=5, wrap=tk.WORD, font=('Segoe UI', 8))
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        log_scrollbar: ttk.Scrollbar = ttk.Scrollbar(log_container, orient="vertical", command=self.log_text.yview)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)

    def create_widgets(self) -> None:
        # Ana çerçeve
        main_frame: ttk.Frame = ttk.Frame(self.root, padding=self.PAD_SMALL)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Ana içerik frame
        content_frame: ttk.Frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Sütun ve satır yapılandırması
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(5, weight=1)  # Log frame (row 5) should expand

        self._create_kitap_secimi_widgets(content_frame)
        self._create_tarama_modu_widgets(content_frame)
        self._create_ayarlar_widgets(content_frame)
        self._create_sayfa_bilgisi_widgets(content_frame)
        self._create_tarama_kontrol_widgets(content_frame)
        self._create_log_widgets(content_frame)
        
        # Klavye kısayolları
        self.root.bind(f"<{self.KEY_ESC.capitalize()}>", lambda e: self.taramayi_durdur())
    
    def log_ekle(self, mesaj: str) -> None:
        try:
            if hasattr(self, 'log_text'):
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, f"{mesaj}\n")
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
            else:
                print(f"Log: {mesaj}")
        except Exception as e:
            print(f"Log eklenirken hata: {e} - Mesaj: {mesaj}") # Should ideally use logging or a more robust error display
        
    def tarama_alani_sec(self) -> None:
        self.root.iconify()
        self.log_ekle(self.INFO_TARAMA_ALANI_SEC_LOG)
        
        time.sleep(0.5)
        
        try:
            region: Optional[Image.Image] = pyautogui.screenshot()
            if region is None: return # Handle case where screenshot fails

            region_tk: ImageTk.PhotoImage = ImageTk.PhotoImage(region)
            
            select_window: tk.Toplevel = tk.Toplevel(self.root)
            select_window.attributes('-fullscreen', True)
            select_window.attributes('-topmost', True)
            
            canvas: tk.Canvas = tk.Canvas(select_window, cursor="cross")
            canvas.pack(fill=tk.BOTH, expand=True)
            
            canvas.create_image(0, 0, image=region_tk, anchor=tk.NW)
            
            rect_id: Optional[int] = None
            start_x: int = 0
            start_y: int = 0
            
            def on_mouse_down(event: tk.Event) -> None:
                nonlocal start_x, start_y, rect_id
                start_x, start_y = event.x, event.y
                
                if rect_id:
                    canvas.delete(rect_id)
                
                rect_id = canvas.create_rectangle(
                    start_x, start_y, start_x, start_y,
                    outline='red', width=2
                )
            
            def on_mouse_move(event: tk.Event) -> None:
                nonlocal rect_id
                if rect_id:
                    canvas.coords(rect_id, start_x, start_y, event.x, event.y)
            
            def on_mouse_up(event: tk.Event) -> None:
                nonlocal start_x, start_y # Though not strictly needed due to nonlocal, good for clarity
                
                end_x, end_y = event.x, event.y
                
                x1: int = min(start_x, end_x)
                y1: int = min(start_y, end_y)
                x2: int = max(start_x, end_x)
                y2: int = max(start_y, end_y)
                
                self.tarama_alani = {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}
                
                self.koordinat_label.config(
                    text=f"({x1},{y1})-({x2},{y2})"
                )
                
                select_window.destroy()
                self.root.deiconify()
                self.log_ekle(self.LOG_TARAMA_ALANI_SECILDI.format(x1,y1,x2,y2))
                
                self.ayarlari_kaydet()
            
            def on_esc_press(event: tk.Event) -> None:
                select_window.destroy()
                self.root.deiconify()
            
            canvas.bind("<ButtonPress-1>", on_mouse_down)
            canvas.bind("<B1-Motion>", on_mouse_move)
            canvas.bind("<ButtonRelease-1>", on_mouse_up)
            select_window.bind("<Escape>", on_esc_press)
            
            # select_window.mainloop() # This might not be needed if the mainloop is already running
            
        except Exception as e:
            self.root.deiconify()
            self.log_ekle(self.LOG_TARAMA_ALANI_SECIM_HATA.format(e))
    
    def tikla_nokta_sec(self) -> None:
        self.root.iconify()
        self.log_ekle(self.INFO_TIKLAMA_NOKTASI_SEC_LOG)
        
        time.sleep(0.5)
        
        try:
            screen: Optional[Image.Image] = pyautogui.screenshot()
            if screen is None: return

            screen_tk: ImageTk.PhotoImage = ImageTk.PhotoImage(screen)
            
            select_window: tk.Toplevel = tk.Toplevel(self.root)
            select_window.attributes('-fullscreen', True)
            select_window.attributes('-topmost', True)
            
            canvas: tk.Canvas = tk.Canvas(select_window, cursor="cross")
            canvas.pack(fill=tk.BOTH, expand=True)
            
            canvas.create_image(0, 0, image=screen_tk, anchor=tk.NW)
            
            point_id: Optional[int] = None
            
            def on_click(event: tk.Event) -> None:
                nonlocal point_id
                x, y = event.x, event.y
                
                if point_id:
                    canvas.delete(point_id)
                
                point_id = canvas.create_oval(
                    x-5, y-5, x+5, y+5,
                    fill='red', outline='red'
                )
                
                self.tiklanacak_nokta = {'x': x, 'y': y}
                
                self.nokta_label.config(
                    text=f"({x},{y})"
                )
                
                time.sleep(0.5)
                select_window.destroy()
                self.root.deiconify()
                self.log_ekle(self.LOG_TIKLAMA_NOKTASI_SECILDI.format(x,y))
                
                self.ayarlari_kaydet()
            
            def on_esc_press(event: tk.Event) -> None:
                select_window.destroy()
                self.root.deiconify()
            
            canvas.bind("<ButtonPress-1>", on_click)
            select_window.bind("<Escape>", on_esc_press)
            
            # select_window.mainloop() # This might not be needed
            
        except Exception as e:
            self.root.deiconify()
            self.log_ekle(self.LOG_TIKLAMA_NOKTASI_SECIM_HATA.format(e))
    
    def ayarlari_guncelle(self) -> bool:
        # Tarama alanı ve tıklama noktası görsel olarak seçildiği için
        # burada özel bir güncelleme işlemi yapılmıyor
        return True
        
    def taramayi_baslat(self) -> None:
        if not self.aktif_kitap:
            messagebox.showwarning(self.TITLE_UYARI, self.WARNING_KITAP_SECIMI_YOK)
            return

        if not self.ayarlari_guncelle():
            return
        
        self.sayfa_parcalari = []
        
        self.baslat_btn.config(state=tk.DISABLED)
        self.durdur_btn.config(state=tk.NORMAL)
        
        self.devam_ediyor = True
        
        # Sayfa bilgisini güncelle
        self.sayfa_bilgisi_guncelle()
        
        # Geri sayım başlat (5 saniye)
        geri_sayim_saniye: int = 5
        self.log_ekle(self.LOG_GERI_SAYIM_BASLADI.format(geri_sayim_saniye))
        self.log_ekle(self.LOG_TARAMA_MODU_BILGI.format(self.tarama_modu))

        def geri_sayim_guncelle_ui() -> None:
            nonlocal geri_sayim_saniye
            if geri_sayim_saniye > 0:
                self.log_ekle(self.LOG_GERI_SAYIM.format(geri_sayim_saniye))
                geri_sayim_saniye -= 1
                self.root.after(1000, geri_sayim_guncelle_ui)
            else:
                self.log_ekle(self.LOG_TARAMA_BASLATILIYOR)

                self.kontrol_paneli_olustur()

                threading.Thread(target=self.tarama_islemi, daemon=True).start()

        geri_sayim_guncelle_ui()

    def kontrol_paneli_olustur(self) -> None:
        """Küçük bir kontrol paneli penceresi oluşturur"""
        if self.kontrol_panel and self.kontrol_panel.winfo_exists():
            self.kontrol_panel.destroy()

        self.kontrol_panel = tk.Toplevel(self.root)
        self.kontrol_panel.title(self.CONTROL_PANEL_TITLE)
        self.kontrol_panel.geometry(self.CONTROL_PANEL_GEOMETRY_PARTS)
        self.kontrol_panel.resizable(False, False)
        self.kontrol_panel.attributes('-topmost', True)

        ekran_genislik: int = self.kontrol_panel.winfo_screenwidth()
        x: int = ekran_genislik - self.CONTROL_PANEL_OFFSET_X
        y: int = self.CONTROL_PANEL_OFFSET_Y
        self.kontrol_panel.geometry(f"{self.CONTROL_PANEL_GEOMETRY_PARTS}+{x}+{y}")

        panel_frame: ttk.Frame = ttk.Frame(self.kontrol_panel, padding=self.PAD_SMALL)
        panel_frame.pack(fill=tk.BOTH, expand=True)

        self.panel_sayfa_label: ttk.Label = ttk.Label(panel_frame, text=f"S:{self.sayfa_no}",
                                          font=self.LOG_TEXT_FONT)
        self.panel_sayfa_label.pack(pady=(0, self.PAD_SMALL)) # MODIFIED pady

        self.panel_duraklat_btn: ttk.Button = ttk.Button(panel_frame, text=self.CONTROL_PANEL_PAUSE_ICON,
                                          command=self.taramayi_duraklat,
                                          width=self.CONTROL_PANEL_BUTTON_WIDTH)
        self.panel_duraklat_btn.pack(pady=self.PAD_SMALL) # MODIFIED pady

        self.panel_devam_btn: ttk.Button = ttk.Button(panel_frame, text=self.CONTROL_PANEL_RESUME_ICON,
                                       command=self.taramayi_devam_ettir,
                                       width=self.CONTROL_PANEL_BUTTON_WIDTH, state=tk.DISABLED)
        self.panel_devam_btn.pack(pady=self.PAD_SMALL) # MODIFIED pady

        self.panel_iptal_btn: ttk.Button = ttk.Button(panel_frame, text=self.CONTROL_PANEL_STOP_ICON,
                                       command=self.taramayi_durdur,
                                       width=self.CONTROL_PANEL_BUTTON_WIDTH)
        self.panel_iptal_btn.pack(pady=self.PAD_SMALL) # MODIFIED pady

        self.kontrol_panel.protocol("WM_DELETE_WINDOW", self.taramayi_durdur)

        self.kontrol_panel.bind(f"<{self.KEY_ESC.capitalize()}>", lambda e: self.taramayi_durdur())

    def taramayi_duraklat(self) -> None:
        """Taramayı duraklatır"""
        if not self.tarama_duraklatildi:
            self.tarama_duraklatildi = True
            self.log_ekle(self.LOG_TARAMA_DURAKLATILDI)

            if hasattr(self, 'panel_duraklat_btn') and self.panel_duraklat_btn.winfo_exists():
                self.panel_duraklat_btn.config(state=tk.DISABLED)
            if hasattr(self, 'panel_devam_btn') and self.panel_devam_btn.winfo_exists():
                self.panel_devam_btn.config(state=tk.NORMAL)

            if hasattr(self, 'panel_sayfa_label') and self.panel_sayfa_label.winfo_exists():
                self.panel_sayfa_label.config(text=self.CONTROL_PANEL_PAUSED_DISPLAY_TEXT)

    def taramayi_devam_ettir(self) -> None:
        """Taramayı kaldığı yerden devam ettirir"""
        if self.tarama_duraklatildi:
            self.tarama_duraklatildi = False
            self.log_ekle(self.LOG_TARAMA_DEVAM_ETTIRILIYOR)

            if hasattr(self, 'panel_duraklat_btn') and self.panel_duraklat_btn.winfo_exists():
                self.panel_duraklat_btn.config(state=tk.NORMAL)
            if hasattr(self, 'panel_devam_btn') and self.panel_devam_btn.winfo_exists():
                self.panel_devam_btn.config(state=tk.DISABLED)

            if hasattr(self, 'panel_sayfa_label') and self.panel_sayfa_label.winfo_exists():
                self.panel_sayfa_label.config(text=f"S:{self.sayfa_no}") # TODO: Constant for "S:"

            self.kontrol_paneli_guncelle()

    def tarama_islemi(self) -> None:
        self.root.iconify()
        time.sleep(1)  # Hazırlanma süresi

        try:
            self.sayfa_parcalari = []
            gc.collect()

            keyboard.add_hotkey(self.KEY_ESC, self.taramayi_durdur)

            while self.devam_ediyor:
                if not self._tarama_sayfa_islemi():
                    break

        except Exception as e:
            self.log_ekle(self.LOG_TARAMA_KRITIK_HATA.format(e))
        finally:
            self.ilerleme_kaydet()
            if self.root.state() == 'iconic': self.root.deiconify()
            self.root.after(0, self.taramayi_durdur)

            self.root.after(0, self.pdf_butonunu_goster)

    def _tarama_sayfa_islemi(self) -> bool:
        """Tek bir sayfanın taranması ve sonraki sayfaya geçiş işlemlerini yürütür.
        Tarama devam edecekse True, duracaksa False döndürür."""
        if keyboard.is_pressed(self.KEY_ESC):
            self.log_ekle(self.LOG_ESC_BASILDI)
            self.taramayi_durdur()
            return False

        self.ilerleme_kaydet()

        if self.kontrol_panel and self.kontrol_panel.winfo_exists():
            self.root.after(0, self.kontrol_paneli_guncelle)

        while self.tarama_duraklatildi and self.devam_ediyor:
            time.sleep(0.1)
            if not self.devam_ediyor:
                return False

        if not self.devam_ediyor:
            return False

        if self.sayfa_no > self.hedef_sayfa_sayisi:
            self.log_ekle(self.LOG_HEDEF_SAYFA_ULASILDI.format(self.hedef_sayfa_sayisi))
            return False

        try:
            if self.tarama_modu == self.TARAMA_MODU_NOBEL:
                self.nobel_tarama_islemi()
            elif self.tarama_modu == self.TARAMA_MODU_TURCADEMY:
                self.turcademy_tarama_islemi()
            else:
                self.log_ekle(self.LOG_BILINMEYEN_TARAMA_MODU.format(self.tarama_modu))
                self.taramayi_durdur()
                return False

            if not self.devam_ediyor:
                return False

            pyautogui.click(self.tiklanacak_nokta['x'], self.tiklanacak_nokta['y'])

            self.log_ekle(self.LOG_YENI_SAYFA_YUKLENIYOR)

            time.sleep(self.CLICK_POST_SLEEP_DURATION)

            sayfa_yuklendi_flag: bool = self.sayfa_yuklenmesini_bekle(True) # Renamed

            if self.tarama_modu == self.TARAMA_MODU_TURCADEMY:
                time.sleep(self.page_transition_delay * self.turcademy_delay_multiplier) # MODIFIED
            elif self.tarama_modu == self.TARAMA_MODU_NOBEL:
                time.sleep(self.page_transition_delay) # MODIFIED
                time.sleep(self.NOBEL_EXTRA_LOAD_SLEEP) # Kept as class constant, not part of configurable set

            if sayfa_yuklendi_flag:
                self.log_ekle(self.LOG_YENI_SAYFA_YUKLENDI)
            else:
                self.log_ekle(self.LOG_YENI_SAYFA_ZAMAN_ASIMI)
                time.sleep(1.0)

            if self.sayfa_no % self.GC_COLLECT_INTERVAL == 0:
                gc.collect()

            return True

        except Exception as e:
            self.log_ekle(self.LOG_SAYFA_TARAMA_HATASI.format(e))
            time.sleep(self.ERROR_WAIT_SLEEP)

            self.sayfa_no += 1
            self.root.after(0, self.sayfa_bilgisi_guncelle)
            return True

    def nobel_tarama_islemi(self) -> None:
        """Nobel sitesi için kaydırmalı tarama işlemi"""
        parca_goruntuler: List[Image.Image] = []

        goruntu: Optional[Image.Image] = self.ekran_goruntusu_al()
        if goruntu:
            parca_goruntuler.append(goruntu)
            self.son_goruntu = goruntu.copy()

            kaydirma_devam: bool = True
            self.ayni_sayfa_sayisi = 0
            sayfa_sonu_sayisi: int = 0

            while kaydirma_devam and self.devam_ediyor:
                try:
                    pyautogui.press(self.SCROLL_KEY)

                    time.sleep(self.page_scroll_delay) # MODIFIED

                    yeni_goruntu: Optional[Image.Image] = self.ekran_goruntusu_al()

                    if yeni_goruntu:
                        if len(parca_goruntuler) > 0:
                            benzerlik: float = self.goruntu_benzerlik_yuzde(parca_goruntuler[-1], yeni_goruntu)

                            if benzerlik > self.similarity_threshold_nobel_end: # MODIFIED
                                sayfa_sonu_sayisi += 1

                                if sayfa_sonu_sayisi >= self.SIMILARITY_REPEAT_COUNT:
                                    kaydirma_devam = False
                                    self.log_ekle(self.LOG_SAYFA_SONUNA_ULASILDI)
                            else:
                                sayfa_sonu_sayisi = 0
                                parca_goruntuler.append(yeni_goruntu)
                                self.son_goruntu = yeni_goruntu.copy()
                        else:
                            parca_goruntuler.append(yeni_goruntu)
                            self.son_goruntu = yeni_goruntu.copy()

                except Exception as e:
                    self.log_ekle(self.LOG_KAYDIRMA_HATASI.format(e))
                    break

        if not self.devam_ediyor:
            return

        if parca_goruntuler:
            birlesik_goruntu: Optional[Image.Image] = self.parca_goruntulerini_birlestir(parca_goruntuler)
            if birlesik_goruntu:
                self.sayfa_kaydet(birlesik_goruntu, self.sayfa_no)

                self.sayfa_no += 1
                self.toplam_sayfa = max(self.toplam_sayfa, self.sayfa_no)

                self.root.after(0, self.sayfa_bilgisi_guncelle)

    def turcademy_tarama_islemi(self) -> None:
        """Turcademy sitesi için tam sayfa görüntü alma işlemi"""
        goruntu: Optional[Image.Image] = self.ekran_goruntusu_al()

        if goruntu and self.devam_ediyor:
            self.sayfa_kaydet(goruntu, self.sayfa_no)

            self.sayfa_no += 1
            self.toplam_sayfa = max(self.toplam_sayfa, self.sayfa_no)

            self.root.after(0, self.sayfa_bilgisi_guncelle)

            self.log_ekle(self.LOG_SAYFA_TARANDI.format(self.sayfa_no-1))

            time.sleep(self.page_scroll_delay) # MODIFIED: Replaced SCROLL_SLEEP_DURATION with its configurable counterpart

    def taramayi_durdur(self) -> bool:
        if self.devam_ediyor:
            self.devam_ediyor = False
            self.log_ekle(self.LOG_TARAMA_DURDURULUYOR)

            self.ilerleme_kaydet()

            if hasattr(self, 'baslat_btn'): self.baslat_btn.config(state=tk.NORMAL)
            if hasattr(self, 'durdur_btn'): self.durdur_btn.config(state=tk.DISABLED)

            if self.kontrol_panel and self.kontrol_panel.winfo_exists():
                self.kontrol_panel.destroy()
                self.kontrol_panel = None

            if self.root.state() == 'iconic': self.root.deiconify()

            if self.otomatik_pdf.get() and self.pdf_butonunu_goster():
                self.log_ekle(self.LOG_OTOMATIK_PDF_OLUSTURULUYOR)
                self.root.after(1000, self.secili_klasordeki_goruntuleri_birlestir)

        return False

    def _create_pdf_progress_window(self) -> Tuple[tk.Toplevel, tk.DoubleVar, ttk.Label]:
        """PDF oluşturma ilerleme penceresini oluşturur ve widget'larını döndürür."""
        progress_window: tk.Toplevel = tk.Toplevel(self.root)
        progress_window.title(self.PDF_PROGRESS_TITLE)
        progress_window.geometry(self.PDF_PROGRESS_GEOMETRY)
        progress_window.transient(self.root)
        progress_window.grab_set()

        progress_frame: ttk.Frame = ttk.Frame(progress_window, padding=self.PAD_XLARGE)
        progress_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(progress_frame, text=self.PDF_PROGRESS_MAIN_LABEL,
                 font=('Segoe UI', 10, 'bold')).pack(pady=(0, self.PAD_LARGE))

        progress_var: tk.DoubleVar = tk.DoubleVar()
        progress_bar: ttk.Progressbar = ttk.Progressbar(progress_frame, variable=progress_var, maximum=100)
        progress_bar.pack(fill=tk.X, pady=self.PAD_LARGE)

        progress_label: ttk.Label = ttk.Label(progress_frame, text=self.PDF_PROGRESS_PREPARING_LABEL)
        progress_label.pack(pady=self.PAD_MEDIUM)

        return progress_window, progress_var, progress_label

    def _load_images_for_pdf(self, image_files: List[str], progress_var: tk.DoubleVar, progress_label: ttk.Label) -> List[Image.Image]:
        """Görüntü dosyalarını yükler ve PDF için hazırlar."""
        goruntu_listesi: List[Image.Image] = []
        toplam_dosya: int = len(image_files)
        for i, dosya in enumerate(image_files):
            ilerleme_yuzdesi: float = (i + 1) / toplam_dosya * 50
            self.root.after(0, lambda p=ilerleme_yuzdesi: progress_var.set(p))

            dosya_adi: str = os.path.basename(dosya)
            self.root.after(0, lambda d=dosya_adi, current_idx=i+1, total=toplam_dosya:
                         progress_label.config(text=self.PDF_PROGRESS_LOADING_LABEL.format(current_idx, total, d)))

            try:
                img: Image.Image = Image.open(dosya)
                goruntu_listesi.append(img.convert(self.IMAGE_FORMAT_RGB))
                self.log_ekle(self.LOG_PDF_IMAGE_LOADING.format(i+1, toplam_dosya, dosya_adi))
            except Exception as e:
                self.log_ekle(self.LOG_PDF_IMAGE_LOAD_ERROR.format(dosya_adi, e))
        return goruntu_listesi

    def _save_images_to_pdf(self, images: List[Image.Image], output_path: str, progress_var: tk.DoubleVar, progress_label: ttk.Label) -> bool:
        """Görüntü listesini PDF olarak kaydeder."""
        if not images:
            self.log_ekle(self.LOG_PDF_NO_IMAGES_TO_LOAD)
            self.root.after(0, lambda: messagebox.showinfo(self.TITLE_BILGI, self.INFO_PDF_NO_IMAGES_LOADED))
            return False

        self.log_ekle(self.LOG_PDF_FIRST_IMAGE_SIZE.format(images[0].width, images[0].height))

        ilk_goruntu: Image.Image = images[0]
        diger_goruntuler: List[Image.Image] = images[1:] if len(images) > 1 else []

        self.log_ekle(self.LOG_PDF_CREATING)
        self.root.after(0, lambda: progress_label.config(text=self.PDF_PROGRESS_SAVING_LABEL))
        self.root.after(0, lambda: progress_var.set(75))

        try:
            ilk_goruntu.save(
                output_path,
                save_all=True,
                append_images=diger_goruntuler,
                resolution=self.PDF_RESOLUTION,
                format=self.PDF_SAVE_FORMAT
            )
            self.log_ekle(self.LOG_PDF_SAVED_SUCCESS.format(len(images), output_path))
            self.root.after(0, lambda: progress_var.set(100))
            return True
        except Exception as e:
            self.log_ekle(self.LOG_PDF_SAVING_ERROR.format(e))
            self.root.after(0, lambda: messagebox.showerror(self.TITLE_HATA, self.ERROR_PDF_OLUSTURMA.format(e)))
            return False

    def secili_klasordeki_goruntuleri_birlestir(self) -> None:
        """Aktif kitap klasöründeki tüm görüntüleri birleştirerek PDF oluşturur"""
        if not self.aktif_kitap:
            messagebox.showwarning(self.TITLE_UYARI, self.WARNING_KITAP_SECIMI_YOK)
            return

        kitap_klasoru: str = self.kayit_klasoru

        if not os.path.exists(kitap_klasoru):
            messagebox.showerror(self.TITLE_HATA, self.ERROR_KITAP_KLASORU_BULUNAMADI)
            return

        varsayilan_dosya_adi: str = f"{self.aktif_kitap}.pdf"
        dosya_yolu: str = filedialog.asksaveasfilename(
            initialdir=os.path.dirname(kitap_klasoru),
            initialfile=varsayilan_dosya_adi,
            defaultextension=".pdf",
            filetypes=[self.FILETYPE_PDF],
            title=self.DIALOG_TITLE_PDF_KAYDET
        )

        if not dosya_yolu:
            return

        progress_window, progress_var, progress_label = self._create_pdf_progress_window()

        def pdf_olustur_thread() -> None:
            try:
                goruntu_dosyalari: List[str] = []
                for dosya_item in os.listdir(kitap_klasoru): # Renamed
                    if dosya_item.lower().endswith(self.IMAGE_FILE_EXTENSION) and dosya_item.startswith(self.IMAGE_FILE_PREFIX):
                        tam_yol: str = os.path.join(kitap_klasoru, dosya_item)
                        goruntu_dosyalari.append(tam_yol)

                if not goruntu_dosyalari:
                    self.root.after(0, lambda: messagebox.showinfo(self.TITLE_BILGI, self.INFO_PDF_NO_IMAGES_FOUND_IN_DIR))
                    if progress_window.winfo_exists(): progress_window.destroy()
                    return

                self.log_ekle(self.LOG_PDF_IMAGES_SORTING.format(len(goruntu_dosyalari)))
                goruntu_dosyalari = self.goruntu_dosyalarini_sirala(goruntu_dosyalari)

                goruntu_listesi: List[Image.Image] = self._load_images_for_pdf(goruntu_dosyalari, progress_var, progress_label)

                if self._save_images_to_pdf(goruntu_listesi, dosya_yolu, progress_var, progress_label):
                    self.root.after(0, lambda: messagebox.showinfo(self.TITLE_BASARILI,
                        self.INFO_PDF_SAVED_SUCCESS_MSG.format(dosya_yolu, len(goruntu_listesi))))

                    kitap_bilgisi: Dict[str, Any] = {
                        'kitap_adi': self.aktif_kitap,
                        'sayfa_sayisi': len(goruntu_listesi),
                        'son_islem_tarihi': time.strftime(self.DATE_FORMAT_STANDARD),
                        'pdf_dosyasi': dosya_yolu
                    }
                    self.kitap_bilgisi_kaydet(kitap_klasoru, kitap_bilgisi)
            except Exception as e:
                self.log_ekle(self.LOG_PDF_GENERAL_ERROR.format(e))
                self.root.after(0, lambda: messagebox.showerror(self.TITLE_HATA, self.LOG_PDF_GENERAL_ERROR.format(e)))
            finally:
                try:
                    if 'goruntu_listesi' in locals() and goruntu_listesi is not None:
                         del goruntu_listesi
                    gc.collect()
                except NameError:
                    pass
                except Exception:
                    pass
                if progress_window.winfo_exists():
                    self.root.after(0, progress_window.destroy)

        threading.Thread(target=pdf_olustur_thread, daemon=True).start()

    def kitap_sil(self) -> None:
        """Seçili kitabı siler"""
        if not self.aktif_kitap or self.aktif_kitap == self.NEW_BOOK_OPTION:
            messagebox.showwarning(self.TITLE_UYARI, self.WARNING_KITAP_SEC_SIL)
            return

        onay: bool = messagebox.askyesno(self.TITLE_ONAY, self.CONFIRM_KITAP_SIL.format(self.aktif_kitap))
        if not onay:
            return

        try:
            import shutil
            kitap_klasoru_sil: str = os.path.join(self.kitaplar_klasoru, self.aktif_kitap)
            if os.path.exists(kitap_klasoru_sil):
                shutil.rmtree(kitap_klasoru_sil)
                self.log_ekle(self.LOG_KITAP_SILINDI.format(self.aktif_kitap))

                self.aktif_kitap = ""

                self.kitaplari_listele()

                if self.kitap_combobox['values']:
                    self.kitap_combobox.current(0)

                if self.pdf_button_visible:
                    self.pdf_button.pack_forget()
                    self.pdf_button_visible = False
        except Exception as e:
            messagebox.showerror(self.TITLE_HATA, self.ERROR_KITAP_SILME.format(e))
            self.log_ekle(self.LOG_KITAP_SILME_HATASI.format(e))

    def kitap_bilgisi_kaydet(self, kitap_klasoru: str, bilgiler: Dict[str, Any]) -> None:
        """Kitap bilgilerini JSON dosyasına kaydeder"""
        try:
            bilgi_dosyasi: str = os.path.join(kitap_klasoru, self.BOOK_INFO_FILE)
            with open(bilgi_dosyasi, 'w', encoding=self.DEFAULT_ENCODING) as f:
                json.dump(bilgiler, f, ensure_ascii=False, indent=4)
            self.log_ekle(self.LOG_KITAP_BILGISI_KAYDEDILDI)
        except Exception as e:
            self.log_ekle(self.LOG_KITAP_BILGISI_KAYDETME_HATA.format(e))

    def kitap_bilgilerini_oku(self, kitap_klasoru: str) -> Optional[Dict[str, Any]]:
        """Kitap bilgilerini okur"""
        try:
            bilgi_dosyasi: str = os.path.join(kitap_klasoru, self.BOOK_INFO_FILE)
            if os.path.exists(bilgi_dosyasi):
                with open(bilgi_dosyasi, 'r', encoding=self.DEFAULT_ENCODING) as f:
                    return json.load(f)
        except Exception as e:
            self.log_ekle(self.LOG_KITAP_BILGILERI_OKUMA_HATA.format(e))
        return None

    def yeni_kitap_ekle(self) -> None:
        """Yeni kitap ekleme penceresi gösterir"""
        dialog: tk.Toplevel = tk.Toplevel(self.root)
        dialog.title(self.TITLE_YENI_KITAP_EKLE)
        dialog.geometry(self.YENI_KITAP_DIALOG_GEOMETRY)
        dialog.transient(self.root)
        dialog.grab_set()  # Modal dialog

        ttk.Label(dialog, text=self.LABEL_KITAP_ADI, style='Title.TLabel').grid(row=0, column=0, padx=self.PAD_LARGE, pady=self.PAD_LARGE, sticky="w")

        kitap_adi_var: tk.StringVar = tk.StringVar()
        kitap_adi_entry: ttk.Entry = ttk.Entry(dialog, textvariable=kitap_adi_var, width=self.YENI_KITAP_ADI_ENTRY_WIDTH)
        kitap_adi_entry.grid(row=0, column=1, padx=self.PAD_LARGE, pady=self.PAD_LARGE, sticky="ew")
        kitap_adi_entry.focus_set()

        button_frame_yeni_kitap: ttk.Frame = ttk.Frame(dialog)
        button_frame_yeni_kitap.grid(row=1, column=0, columnspan=2, pady=self.PAD_XLARGE)

        def iptal_et() -> None:
            dialog.destroy()

        def kitap_ekle_action() -> None: # Renamed to avoid conflict with method
            kitap_adi: str = kitap_adi_var.get().strip()
            if kitap_adi:
                kitap_klasoru_yeni: Optional[str] = self.kitap_klasoru_olustur(kitap_adi)
                if kitap_klasoru_yeni:
                    self.kitaplari_listele()
                    kitap_adi_duzgun: str = self.dosya_adi_duzenle(kitap_adi)
                    self.kitap_combobox.set(kitap_adi_duzgun)
                    self.kitap_sec()
                    dialog.destroy()
            else:
                messagebox.showwarning(self.TITLE_UYARI, self.WARNING_KITAP_ADI_GIRIN)

        ttk.Button(button_frame_yeni_kitap, text=self.BUTTON_IPTAL, command=iptal_et).grid(row=0, column=0, padx=self.PAD_LARGE)
        ttk.Button(button_frame_yeni_kitap, text=self.BUTTON_EKLE, command=kitap_ekle_action, style='Accent.TButton').grid(row=0, column=1, padx=self.PAD_LARGE)

        # Enter tuşuna basıldığında ekleme işlemini gerçekleştir
        dialog.bind("<Return>", lambda e: kitap_ekle_action())
        dialog.bind("<Escape>", lambda e: iptal_et())

    def kitaplari_listele(self) -> None:
        """Mevcut kitapları listeleyip Combobox'a ekler"""
        if not hasattr(self, 'kitap_combobox'):
            return

        kitaplar: List[str] = []
        try:
            for item in os.listdir(self.kitaplar_klasoru):
                tam_yol: str = os.path.join(self.kitaplar_klasoru, item)
                if os.path.isdir(tam_yol):
                    kitaplar.append(item)
        except FileNotFoundError:
            pass

        kitaplar.sort()

        kitaplar_liste_cb: List[str] = [self.NEW_BOOK_OPTION] + kitaplar # Renamed for clarity

        self.kitap_combobox['values'] = kitaplar_liste_cb

        if len(kitaplar_liste_cb) == 1:
            self.kitap_combobox.current(0)

    def kitap_sec(self) -> None:
        """Seçilen kitabı aktif kitap olarak ayarlar"""
        secilen: str = self.kitap_combobox.get()
        
        if secilen == self.NEW_BOOK_OPTION:
            self.yeni_kitap_ekle()
            return

        self.aktif_kitap = secilen
        self.kayit_klasoru = os.path.join(self.kitaplar_klasoru, secilen)

        if not os.path.exists(self.kayit_klasoru):
            os.makedirs(self.kayit_klasoru)

        self.ilerleme_dosyasi = os.path.join(self.kayit_klasoru, self.PROGRESS_FILE)

        if hasattr(self, 'klasor_label'): self.klasor_label.config(text=self.kayit_klasoru)

        self.pdf_butonunu_goster()

        self.mevcut_sayfa_durumunu_tespit_et()
        self.ilerleme_yukle()

        self.log_ekle(self.LOG_AKTIF_KITAP.format(secilen))

        self.sayfa_bilgisi_guncelle()

    def pdf_butonunu_goster(self) -> bool:
        """PDF oluşturma butonunu gösterir veya gizler,
           PDF oluşturulacak görüntü varsa True döndürür"""
        try:
            png_var: bool = False
            if os.path.exists(self.kayit_klasoru):
                for dosya in os.listdir(self.kayit_klasoru):
                    if dosya.lower().endswith(self.IMAGE_FILE_EXTENSION):
                        png_var = True
                        break

            if png_var and not self.pdf_button_visible:
                self.pdf_button.pack(side=tk.LEFT, padx=1)
                self.pdf_button_visible = True
            elif not png_var and self.pdf_button_visible:
                self.pdf_button.pack_forget()
                self.pdf_button_visible = False

            return png_var
        except Exception as e:
            self.log_ekle(self.LOG_PDF_BUTON_KONTROL_HATA.format(e))
            if hasattr(self, 'pdf_button') and self.pdf_button_visible:
                self.pdf_button.pack_forget()
                self.pdf_button_visible = False
            return False

    def goruntu_dosyalarini_sirala(self, dosya_listesi: List[str]) -> List[str]:
        """Görüntü dosyalarını sayfa numarasına göre sıralar"""
        try:
            self.log_ekle(self.LOG_GORUNTU_SIRALANIYOR)

            dosya_bilgileri: List[Dict[str, Any]] = []

            for dosya_yolu in dosya_listesi:
                try:
                    dosya_adi: str = os.path.basename(dosya_yolu)

                    if not dosya_adi.startswith(self.IMAGE_FILE_PREFIX) or not dosya_adi.endswith(self.IMAGE_FILE_EXTENSION):
                        continue

                    sayfa_no_str: str = dosya_adi[len(self.IMAGE_FILE_PREFIX):-len(self.IMAGE_FILE_EXTENSION)]

                    try:
                        sayfa_no_int: int = int(sayfa_no_str)
                        dosya_bilgileri.append({
                            "dosya_yolu": dosya_yolu,
                            "sayfa_no": sayfa_no_int,
                            "dosya_adi": dosya_adi
                        })
                    except ValueError:
                        self.log_ekle(self.LOG_SAYFA_NO_COZUMLEME_UYARI.format(dosya_adi))
                        dosya_bilgileri.append({
                            "dosya_yolu": dosya_yolu,
                            "sayfa_no": float('inf'),
                            "dosya_adi": dosya_adi
                        })
                except Exception as e:
                    self.log_ekle(self.LOG_DOSYA_ISLEME_HATA.format(e))
                    continue

            dosya_bilgileri.sort(key=lambda x: x["sayfa_no"])

            self.log_ekle(self.LOG_TOPLAM_DOSYA_SIRALANDI.format(len(dosya_bilgileri)))

            if len(dosya_bilgileri) > 0:
                ilk_10_dosya_str: List[str] = [f"{bilgi['dosya_adi']}({bilgi['sayfa_no']})" for bilgi in dosya_bilgileri[:10]]
                self.log_ekle(self.LOG_ILK_10_DOSYA.format(', '.join(ilk_10_dosya_str)))

                if len(dosya_bilgileri) > 20:
                    son_10_dosya_str: List[str] = [f"{bilgi['dosya_adi']}({bilgi['sayfa_no']})" for bilgi in dosya_bilgileri[-10:]]
                    self.log_ekle(self.LOG_SON_10_DOSYA.format(', '.join(son_10_dosya_str)))

            return [bilgi["dosya_yolu"] for bilgi in dosya_bilgileri]

        except Exception as e:
            self.log_ekle(self.LOG_GORUNTU_SIRALAMA_HATA.format(e))
            return dosya_listesi

    def kitap_klasoru_olustur(self, kitap_adi: str) -> Optional[str]:
        """Kitap için klasör oluşturur"""
        if not kitap_adi:
            return None

        kitap_adi_duzgun: str = self.dosya_adi_duzenle(kitap_adi)
        kitap_klasoru_path: str = os.path.join(self.kitaplar_klasoru, kitap_adi_duzgun) # Renamed for clarity

        if not os.path.exists(kitap_klasoru_path):
            os.makedirs(kitap_klasoru_path)
            self.log_ekle(self.LOG_YENI_KITAP_KLASORU_OLUSTURULDU.format(kitap_adi))

        return kitap_klasoru_path

    def dosya_adi_duzenle(self, ad: str) -> str:
        """Dosya adı için uygun olmayan karakterleri değiştirir"""
        gecersiz_karakterler: str = r'[\\/*?:"<>|]'
        import re # Should be at the top
        duzgun_ad: str = re.sub(gecersiz_karakterler, "_", ad)
        return duzgun_ad

    def tarama_modu_degisti(self) -> None:
        """Tarama modu değiştiğinde yapılacak işlemler"""
        self.tarama_modu = self.tarama_modu_var.get()
        self.log_ekle(self.LOG_TARAMA_MODU_DEGISTI.format(self.tarama_modu))
        self.ayarlari_kaydet()

    def sayfa_yuklenmesini_bekle(self, yeni_sayfa: bool = False) -> bool:
        """Sayfanın yüklenmesini bekler, yüklendiyse True döndürür, aksi halde False"""
        try:
            baslangic_zamani: float = time.time()
            sayfa_yuklendi_flag: bool = False # Renamed to avoid conflict
            onceki_goruntu: Optional[Image.Image] = None
            kararlilik_sayaci: int = 0

            while time.time() - baslangic_zamani < self.max_load_wait_time and not sayfa_yuklendi_flag and self.devam_ediyor: # MODIFIED: self.max_bekleme_suresi -> self.max_load_wait_time
                time.sleep(0.05)

                goruntu_cek: Optional[Image.Image] = self.ekran_goruntusu_al() # Renamed

                if goruntu_cek and onceki_goruntu:
                    benzerlik_yuzdesi_val: float = self.goruntu_benzerlik_yuzde(onceki_goruntu, goruntu_cek) # Renamed

                    esik_degeri: int = self.similarity_threshold_page_load_turcademy if self.tarama_modu == self.TARAMA_MODU_TURCADEMY else self.similarity_threshold_page_load_nobel # MODIFIED

                    if benzerlik_yuzdesi_val > esik_degeri:
                        kararlilik_sayaci += 1
                    else:
                        kararlilik_sayaci = 0

                    # These PAGE_LOAD_STABILITY_COUNT constants are class-level, not instance variables loaded from json. This is consistent with the fact that they were not in the list of parameters to make configurable.
                    gereken_kararli_goruntu: int = self.PAGE_LOAD_STABILITY_COUNT_TURCADEMY if self.tarama_modu == self.TARAMA_MODU_TURCADEMY else self.PAGE_LOAD_STABILITY_COUNT_NOBEL
                    if kararlilik_sayaci >= gereken_kararli_goruntu:
                        sayfa_yuklendi_flag = True

                        if yeni_sayfa:
                            self.son_goruntu = goruntu_cek.copy()

                onceki_goruntu = goruntu_cek

            return sayfa_yuklendi_flag

        except Exception as e:
            self.log_ekle(self.LOG_SAYFA_YUKLEME_KONTROL_HATA.format(e))
            return False

    def ekran_goruntusu_al(self) -> Optional[Image.Image]:
        x1, y1, x2, y2 = self.tarama_alani['x1'], self.tarama_alani['y1'], self.tarama_alani['x2'], self.tarama_alani['y2']

        try:
            screenshot: Image.Image = pyautogui.screenshot(region=(x1, y1, x2-x1, y2-y1))
            return screenshot
        except Exception as e:
            self.log_ekle(self.LOG_EKRAN_GORUNTUSU_HATA.format(e))
            return None

    def sayfa_kaydet(self, goruntu: Image.Image, sayfa_no: int) -> Optional[str]:
        try:
            if not os.path.exists(self.kayit_klasoru):
                os.makedirs(self.kayit_klasoru)

            dosya_adi_kayit: str = f"{self.IMAGE_FILE_PREFIX}{sayfa_no}{self.IMAGE_FILE_EXTENSION}" # Renamed
            tam_yol_kayit: str = os.path.join(self.kayit_klasoru, dosya_adi_kayit) # Renamed
            goruntu.save(tam_yol_kayit)
            self.log_ekle(self.LOG_SAYFA_KAYDEDILDI.format(sayfa_no, dosya_adi_kayit))
            return tam_yol_kayit
        except Exception as e:
            self.log_ekle(self.LOG_SAYFA_KAYDET_HATA.format(e))
            return None

    def sayfa_bilgisi_guncelle(self) -> None:
        """Sayfa bilgisi etiketlerini ve ilerleme bilgisini günceller"""
        if hasattr(self, 'sayfa_label'): self.sayfa_label.config(text=str(self.sayfa_no))
        if hasattr(self, 'toplam_sayfa_label'): self.toplam_sayfa_label.config(text=str(self.toplam_sayfa))

        try:
            if os.path.exists(self.kayit_klasoru):
                klasor_sayfa_sayisi: int = 0
                for dosya_item in os.listdir(self.kayit_klasoru): # Renamed
                    if dosya_item.startswith(self.IMAGE_FILE_PREFIX) and dosya_item.endswith(self.IMAGE_FILE_EXTENSION):
                        klasor_sayfa_sayisi += 1

                bilgi_metni: str = f"S:{self.sayfa_no}/{self.toplam_sayfa} (K:{klasor_sayfa_sayisi}/H:{self.hedef_sayfa_sayisi})"
                self.log_ekle(bilgi_metni)

                # Removed the logic that directly updates self.panel_sayfa_label from here.
                # self.kontrol_paneli_guncelle() is responsible for updating the control panel's label
                # with a more compact format and is called at appropriate times during the scan.
        except Exception:
            pass

    def goruntu_benzerlik_yuzde(self, goruntu1: Image.Image, goruntu2: Image.Image) -> float:
        """İki görüntü arasındaki benzerlik yüzdesini hesaplar (0-100)"""
        try:
            img1_resized: Image.Image = goruntu1.resize(self.SIMILARITY_RESIZE_DIM) # Renamed
            img2_resized: Image.Image = goruntu2.resize(self.SIMILARITY_RESIZE_DIM) # Renamed

            img1_gray: Image.Image = img1_resized.convert('L') # Renamed
            img2_gray: Image.Image = img2_resized.convert('L') # Renamed

            farkli_piksel_sayisi: int = 0
            toplam_piksel_sayisi: int = self.SIMILARITY_RESIZE_DIM[0] * self.SIMILARITY_RESIZE_DIM[1] # Renamed
            piksel_fark_esik: int = self.SIMILARITY_PIXEL_DIFF_THRESHOLD # Renamed

            try:
                import numpy as np # Import moved to top later

                arr1: np.ndarray = np.array(img1_gray)
                arr2: np.ndarray = np.array(img2_gray)

                fark_arr: np.ndarray = np.abs(arr1 - arr2) # Renamed

                farkli_piksel_sayisi = np.sum(fark_arr > piksel_fark_esik)

            except ImportError:
                for x_coord in range(self.SIMILARITY_RESIZE_DIM[0]): # Renamed
                    for y_coord in range(self.SIMILARITY_RESIZE_DIM[1]): # Renamed
                        piksel1: int = img1_gray.getpixel((x_coord, y_coord))
                        piksel2: int = img2_gray.getpixel((x_coord, y_coord))
                        if abs(piksel1 - piksel2) > piksel_fark_esik:
                            farkli_piksel_sayisi += 1

            benzerlik: float = 100.0 - (farkli_piksel_sayisi * 100.0 / toplam_piksel_sayisi) # Ensure float division
            return benzerlik
        except Exception as e:
            self.log_ekle(self.LOG_GORUNTU_BENZERLIK_HATA.format(e))
            return 0.0 # Return float

    def parca_goruntulerini_birlestir(self, goruntuler: List[Image.Image]) -> Optional[Image.Image]:
        if not goruntuler:
            return None

        try:
            genislik: int = goruntuler[0].width

            ortusme_pikseli: int = min(self.PAGE_PART_OVERLAP_PIXELS, int(goruntuler[0].height * self.PAGE_PART_OVERLAP_RATIO))

            toplam_yukseklik: int = 0
            islenmis_goruntuler_list: List[Tuple[Image.Image, int]] = [] # Renamed

            islenmis_goruntuler_list.append((goruntuler[0], 0))
            toplam_yukseklik = goruntuler[0].height

            for i in range(1, len(goruntuler)):
                onceki_g: Image.Image = goruntuler[i-1] # Renamed
                simdiki_g: Image.Image = goruntuler[i] # Renamed

                onceki_alt_crop: Image.Image = onceki_g.crop((0, onceki_g.height - ortusme_pikseli,
                                                 genislik, onceki_g.height)) # Renamed

                simdiki_ust_crop: Image.Image = simdiki_g.crop((0, 0, genislik, ortusme_pikseli)) # Renamed

                onceki_alt_gri: Image.Image = onceki_alt_crop.convert('L') # Renamed
                simdiki_ust_gri: Image.Image = simdiki_ust_crop.convert('L') # Renamed

                en_iyi_offset_val: int = 0 # Renamed
                en_az_fark_val: float = float('inf') # Renamed

                adim_sayisi: int = max(1, ortusme_pikseli // self.PAGE_PART_MATCH_SAMPLE_STEP_BIG) # Renamed

                for offset_val in range(0, ortusme_pikseli, adim_sayisi): # Renamed
                    fark_toplami: int = 0 # Renamed
                    incelenen_piksel_sayisi: int = 0 # Renamed

                    ornekleme_araligi: int = max(1, genislik // self.PAGE_PART_MATCH_SAMPLE_STEP_SMALL) # Renamed

                    for x_coord_offset in range(0, genislik, ornekleme_araligi): # Renamed
                        for y_coord_offset in range(0, ortusme_pikseli - offset_val, adim_sayisi): # Renamed
                            try:
                                onceki_p: int = onceki_alt_gri.getpixel((x_coord_offset, y_coord_offset + offset_val)) # Renamed
                                simdiki_p: int = simdiki_ust_gri.getpixel((x_coord_offset, y_coord_offset)) # Renamed

                                fark_toplami += abs(onceki_p - simdiki_p)
                                incelenen_piksel_sayisi += 1
                            except IndexError:
                                pass

                    if incelenen_piksel_sayisi > 0:
                        ortalama_fark_val: float = fark_toplami / incelenen_piksel_sayisi # Renamed

                        if ortalama_fark_val < en_az_fark_val:
                            en_az_fark_val = ortalama_fark_val
                            en_iyi_offset_val = offset_val

                y_pozisyonu: int = toplam_yukseklik - (ortusme_pikseli - en_iyi_offset_val) # Renamed
                islenmis_goruntuler_list.append((simdiki_g, y_pozisyonu))

                toplam_yukseklik = y_pozisyonu + simdiki_g.height

            birlesik_resim: Image.Image = Image.new(self.IMAGE_FORMAT_RGB, (genislik, toplam_yukseklik)) # Renamed

            for goruntu_item, y_pos in islenmis_goruntuler_list: # Renamed
                birlesik_resim.paste(goruntu_item, (0, y_pos))

            del islenmis_goruntuler_list
            gc.collect()

            return birlesik_resim
        except Exception as e:
            self.log_ekle(self.LOG_GORUNTU_BIRLESTIRME_HATA.format(e))
            return None

    def baslangic_sayfasini_guncelle(self) -> None:
        """Başlangıç sayfa numarasını günceller"""
        try:
            yeni_sayfa: int = int(self.baslangic_sayfa_var.get())
            if yeni_sayfa > 0:
                self.sayfa_no = yeni_sayfa
                self.sayfa_bilgisi_guncelle()
                self.log_ekle(self.LOG_BASLANGIC_SAYFA_GUNCELLENDI.format(yeni_sayfa))

                self.baslangic_sayfa_entry.config(state='readonly')
            else:
                messagebox.showwarning(self.TITLE_UYARI, self.WARNING_SAYFA_NO_GECERSIZ)
        except ValueError:
            messagebox.showwarning(self.TITLE_UYARI, self.WARNING_GECERLI_SAYFA_NO_GIRIN)

        self.baslangic_sayfa_entry.config(state='readonly')

    def bilgi_kontrolu(self) -> None:
        """Ayarlara göre bilgi mesajının gösterilip gösterilmeyeceğini kontrol eder"""
        try:
            ayarlar: Dict[str, Any] = {}
            if os.path.exists(self.config_dosyasi):
                with open(self.config_dosyasi, 'r') as f:
                    ayarlar = json.load(f)

            if not ayarlar.get('baslangic_bilgi_goster', True) == False: # TODO: Constant for 'baslangic_bilgi_goster'
                self.baslangic_bilgi_goster()

        except Exception: # More general catch, as specific error isn't critical here
            self.baslangic_bilgi_goster()

    def baslangic_bilgi_goster(self) -> None:
        """Uygulama ilk açıldığında bilgi mesajı gösterir"""
        info_window: tk.Toplevel = tk.Toplevel(self.root)
        info_window.title(self.TITLE_HOS_GELDINIZ)
        info_window.geometry(self.HOS_GELDINIZ_DIALOG_GEOMETRY)
        info_window.transient(self.root)
        info_window.grab_set()

        info_frame: ttk.Frame = ttk.Frame(info_window, padding=self.PAD_XLARGE)
        info_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(info_frame, text=self.WELCOME_MESSAGE_HEADER,
                 font=('Segoe UI', 12, 'bold')).pack(pady=(0, self.PAD_LARGE))

        bilgi_text_content: str = self.WELCOME_MESSAGE_BODY # Renamed

        text_widget_info: tk.Text = tk.Text(info_frame, height=self.HOS_GELDINIZ_TEXT_HEIGHT, wrap=tk.WORD) # Renamed
        text_widget_info.pack(fill=tk.BOTH, expand=True, pady=self.PAD_LARGE)
        text_widget_info.insert(tk.END, bilgi_text_content)
        text_widget_info.config(state=tk.DISABLED)

        buton_frame_bilgi: ttk.Frame = ttk.Frame(info_frame)
        buton_frame_bilgi.pack(fill=tk.X, pady=self.PAD_LARGE)

        ttk.Button(buton_frame_bilgi, text=self.BUTTON_ACILISTA_GOSTERME,
                  command=lambda: self.ayarlari_kaydet_ozel("baslangic_bilgi_goster", False), # TODO: Constant for key
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=self.PAD_MEDIUM)

        ttk.Button(buton_frame_bilgi, text=self.BUTTON_BASLA, command=info_window.destroy,
                  style='Accent.TButton').pack(side=tk.RIGHT, padx=self.PAD_MEDIUM)

    def ayarlari_kaydet_ozel(self, anahtar: str, deger: bool) -> None:
        """Özel bir ayarı günceller ve kaydeder"""
        try:
            ayarlar_data: Dict[str, Any] = {} # Renamed
            if os.path.exists(self.config_dosyasi):
                with open(self.config_dosyasi, 'r') as f:
                    ayarlar_data = json.load(f)

            ayarlar_data[anahtar] = deger

            with open(self.config_dosyasi, 'w') as f:
                json.dump(ayarlar_data, f)

        except Exception as e:
            print(self.LOG_OZEL_AYAR_KAYDETME_HATA.format(e))

    def hedef_sayfasini_guncelle(self) -> None:
        """Hedef sayfa sayısını günceller"""
        try:
            yeni_hedef_sayi: int = int(self.hedef_sayfa_var.get()) # Renamed
            if yeni_hedef_sayi > 0:
                self.hedef_sayfa_sayisi = yeni_hedef_sayi
                self.log_ekle(self.LOG_HEDEF_SAYFA_GUNCELLENDI.format(yeni_hedef_sayi))
                self.ayarlari_kaydet()
            else:
                messagebox.showwarning(self.TITLE_UYARI, self.WARNING_HEDEF_SAYFA_GECERSIZ)
        except ValueError:
            messagebox.showwarning(self.TITLE_UYARI, self.WARNING_GECERLI_HEDEF_SAYFA_GIRIN)

    def kontrol_paneli_guncelle(self) -> None:
        """Kontrol panelindeki sayfa ve durum bilgilerini günceller"""
        try:
            if self.kontrol_panel and self.kontrol_panel.winfo_exists():
                klasor_sayfa_sayisi_guncel: int = 0 # Renamed
                if os.path.exists(self.kayit_klasoru):
                    for dosya_item_guncel in os.listdir(self.kayit_klasoru): # Renamed
                        if dosya_item_guncel.startswith(self.IMAGE_FILE_PREFIX) and dosya_item_guncel.endswith(self.IMAGE_FILE_EXTENSION):
                            klasor_sayfa_sayisi_guncel += 1

                bilgi_metni_guncel: str = f"S:{self.sayfa_no}/{self.toplam_sayfa}" # Renamed

                if hasattr(self, 'panel_sayfa_label') and self.panel_sayfa_label.winfo_exists():
                    self.panel_sayfa_label.config(text=bilgi_metni_guncel)
        except Exception:
            pass

    def sayfa_numarasi_duzenle(self) -> None:
        """Sayfa numarasını manuel olarak düzenlemeye izin verir"""
        self.baslangic_sayfa_entry.config(state='normal')

        self.log_ekle(self.LOG_SAYFA_NO_DUZENLEME_BILGI)

        self.baslangic_sayfa_entry.bind("<Return>", lambda e: self.baslangic_sayfasini_guncelle())

if __name__ == "__main__":
    root_tk: tk.Tk = tk.Tk() # Renamed
    app_instance: EkranTarayici = EkranTarayici(root_tk) # Renamed
    root_tk.mainloop()
            nonlocal geri_sayim
            if geri_sayim > 0:
                self.log_ekle(self.LOG_GERI_SAYIM.format(geri_sayim))
                geri_sayim -= 1
                self.root.after(1000, geri_sayim_guncelle)
            else:
                self.log_ekle(self.LOG_TARAMA_BASLATILIYOR)
                
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
            self.log_ekle(self.LOG_TARAMA_DURAKLATILDI)
            
            # Butonların durumlarını güncelle
            if hasattr(self, 'panel_duraklat_btn') and self.panel_duraklat_btn.winfo_exists(): # Check if exists
                self.panel_duraklat_btn.config(state=tk.DISABLED)
            self.panel_devam_btn.config(state=tk.NORMAL)
            
            # Durum bilgisini güncelle
            if hasattr(self, 'panel_sayfa_label') and self.panel_sayfa_label.winfo_exists():
                self.panel_sayfa_label.config(text="⏸️ DURAKLATILDI")
    
    def taramayi_devam_ettir(self):
        """Taramayı kaldığı yerden devam ettirir"""
        if self.tarama_duraklatildi:
            self.tarama_duraklatildi = False
            self.log_ekle(self.LOG_TARAMA_DEVAM_ETTIRILIYOR)
            
            # Butonların durumlarını güncelle
            if hasattr(self, 'panel_duraklat_btn') and self.panel_duraklat_btn.winfo_exists(): # Check if exists
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
            keyboard.add_hotkey(self.KEY_ESC, self.taramayi_durdur)
            
            while self.devam_ediyor:
                if not self._tarama_sayfa_islemi():
                    break
        
        except Exception as e:
            self.log_ekle(self.LOG_TARAMA_KRITIK_HATA.format(e))
        finally:
            # Tarama tamamlandığında ilerlemeyi kaydet
            self.ilerleme_kaydet()
            self.root.deiconify()  # Ana pencereyi geri getir
            self.root.after(0, self.taramayi_durdur)  # UI thread'inden çağır
            
            # Eğer tarama tamamlandıysa PDF oluşturma butonunu göster
            self.root.after(0, self.pdf_butonunu_goster)

    def _tarama_sayfa_islemi(self):
        """Tek bir sayfanın taranması ve sonraki sayfaya geçiş işlemlerini yürütür.
        Tarama devam edecekse True, duracaksa False döndürür."""
        # ESC tuşuna basıldı mı kontrol et
        if keyboard.is_pressed(self.KEY_ESC):
            self.log_ekle(self.LOG_ESC_BASILDI)
            self.taramayi_durdur()
            return False

        # Periyodik ilerleme kaydetme
        self.ilerleme_kaydet() # TODO: Consider moving this to be less frequent

        # Kontrol panelini güncelle - ana thread üzerinden çağır
        if self.kontrol_panel and self.kontrol_panel.winfo_exists():
            self.root.after(0, self.kontrol_paneli_guncelle)

        # Duraklatıldıysa bekle
        while self.tarama_duraklatildi and self.devam_ediyor:
            time.sleep(0.1)  # Duraklatıldığında kısa aralıklarla kontrol et
            if not self.devam_ediyor: # Check again if stopped during pause
                return False

        if not self.devam_ediyor: # Check if stopped
            return False

        # Hedef sayfa sayısına ulaşıldı mı kontrol et
        if self.sayfa_no > self.hedef_sayfa_sayisi:
            self.log_ekle(self.LOG_HEDEF_SAYFA_ULASILDI.format(self.hedef_sayfa_sayisi))
            return False

        try:
            if self.tarama_modu == self.TARAMA_MODU_NOBEL:
                # Nobel tarama modu (kaydırmalı sayfa tarama)
                self.nobel_tarama_islemi()
            elif self.tarama_modu == self.TARAMA_MODU_TURCADEMY:
                # Turcademy tarama modu (tam sayfa görüntü)
                self.turcademy_tarama_islemi()
            else:
                self.log_ekle(self.LOG_BILINMEYEN_TARAMA_MODU.format(self.tarama_modu))
                self.taramayi_durdur()
                return False

            # Eğer tarama durdurulmuşsa döngüden çık
            if not self.devam_ediyor:
                return False

            # Sonraki sayfaya geç
            pyautogui.click(self.tiklanacak_nokta['x'], self.tiklanacak_nokta['y'])

            # Yeni sayfanın yüklenmesini bekle
            self.log_ekle(self.LOG_YENI_SAYFA_YUKLENIYOR)

            # Tıklama sonrası kısa bekleme - sayfa geçişi için
            time.sleep(0.5)  # Tıklama sonrası kısa bekleme ekle # TODO: Constant for this sleep

            # Sayfa yüklenme beklemesi
            sayfa_yuklendi = self.sayfa_yuklenmesini_bekle(True)

            # Yeni sayfa başlangıç gecikmesi - Turcademy için daha uygun bekle
            if self.tarama_modu == self.TARAMA_MODU_TURCADEMY:
                # Turcademy için optimize edilmiş bekleme süresi
                time.sleep(self.sayfa_gecis_gecikmesi * self.turcademy_gecis_carpani)
            elif self.tarama_modu == self.TARAMA_MODU_NOBEL:
                # Nobel için ek bekleme süresi
                time.sleep(self.sayfa_gecis_gecikmesi)

                # Nobel için sayfa içeriğinin tamamen görünür olması için biraz daha bekle
                time.sleep(1.0)  # Nobel modu için ekstra bekleme # TODO: Constant for this sleep

            # Sayfa yüklenme bilgisi
            if sayfa_yuklendi:
                self.log_ekle(self.LOG_YENI_SAYFA_YUKLENDI)
            else:
                self.log_ekle(self.LOG_YENI_SAYFA_ZAMAN_ASIMI)
                # Sayfanın yüklenmesi için ek bekleme
                time.sleep(1.0) # TODO: Constant for this sleep

            # Bellek optimizasyonu
            if self.sayfa_no % 10 == 0:  # Her 10 sayfada bir # TODO: Constant for page interval
                gc.collect()  # Çöp toplayıcıyı çağır

            return True # Sayfa işlemi başarılı, devam et

        except Exception as e:
            # Sayfa tarama sırasında oluşabilecek hatayı yakala ve devam et
            self.log_ekle(self.LOG_SAYFA_TARAMA_HATASI.format(e))
            time.sleep(2)  # Hata sonrası bekle # TODO: Constant for this sleep

            # Sayfa numarasını yine de arttır
            self.sayfa_no += 1
            self.root.after(0, self.sayfa_bilgisi_guncelle)
            return True # Hata oluştu ama taramaya devam etmeyi dene
            
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
                    pyautogui.press('pagedown') # TODO: Constant for 'pagedown'
                    
                    # Kısa bir süre bekle
                    time.sleep(0.3) # TODO: Constant for sleep time
                    
                    # Sayfa değişimini kontrol et
                    yeni_goruntu = self.ekran_goruntusu_al()
                    
                    if yeni_goruntu:
                        # Son görüntüyle benzerliği kontrol et
                        if len(parca_goruntuler) > 0:
                            benzerlik = self.goruntu_benzerlik_yuzde(parca_goruntuler[-1], yeni_goruntu)
                            
                            # Görüntüler çok benzer ise (sayfa sonundayız)
                            if benzerlik > 97: # TODO: Constant for similarity threshold
                                sayfa_sonu_sayisi += 1
                                
                                # İki defa aynı görüntü alırsak, sayfa sonuna geldik demektir
                                if sayfa_sonu_sayisi >= 2: # TODO: Constant for count
                                    kaydirma_devam = False
                                    self.log_ekle(self.LOG_SAYFA_SONUNA_ULASILDI)
                            else:
                                sayfa_sonu_sayisi = 0
                                parca_goruntuler.append(yeni_goruntu)
                                self.son_goruntu = yeni_goruntu.copy()
                        else:
                            parca_goruntuler.append(yeni_goruntu)
                            self.son_goruntu = yeni_goruntu.copy()
                    
                except Exception as e:
                    self.log_ekle(self.LOG_KAYDIRMA_HATASI.format(e))
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
            
            self.log_ekle(self.LOG_SAYFA_TARANDI.format(self.sayfa_no-1))
            
            # Sayfanın tam olarak kaydedilmesi için kısa bir bekleme ekle (0.3 saniye)
            time.sleep(0.3) # TODO: Constant for sleep time
        
    def taramayi_durdur(self):
        if self.devam_ediyor:
            self.devam_ediyor = False
            self.log_ekle(self.LOG_TARAMA_DURDURULUYOR)
            
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
                self.log_ekle(self.LOG_OTOMATIK_PDF_OLUSTURULUYOR)
                self.root.after(1000, self.secili_klasordeki_goruntuleri_birlestir) # TODO: Constant for delay
        
        return False  # Event handler'ın normal işleyişini devam ettir

    def _create_pdf_progress_window(self):
        """PDF oluşturma ilerleme penceresini oluşturur ve widget'larını döndürür."""
        progress_window = tk.Toplevel(self.root)
        progress_window.title(self.PDF_PROGRESS_TITLE)
        progress_window.geometry(self.PDF_PROGRESS_GEOMETRY)
        progress_window.transient(self.root)
        progress_window.grab_set()

        progress_frame = ttk.Frame(progress_window, padding=self.PAD_XLARGE)
        progress_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(progress_frame, text=self.PDF_PROGRESS_MAIN_LABEL,
                 font=('Segoe UI', 10, 'bold')).pack(pady=(0, self.PAD_LARGE))

        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, maximum=100)
        progress_bar.pack(fill=tk.X, pady=self.PAD_LARGE)

        progress_label = ttk.Label(progress_frame, text=self.PDF_PROGRESS_PREPARING_LABEL)
        progress_label.pack(pady=self.PAD_MEDIUM)

        return progress_window, progress_var, progress_label

    def _load_images_for_pdf(self, image_files, progress_var, progress_label):
        """Görüntü dosyalarını yükler ve PDF için hazırlar."""
        goruntu_listesi = []
        toplam_dosya = len(image_files)
        for i, dosya in enumerate(image_files):
            ilerleme_yuzdesi = (i + 1) / toplam_dosya * 50  # İlk %50 yükleme için
            self.root.after(0, lambda p=ilerleme_yuzdesi: progress_var.set(p))

            dosya_adi = os.path.basename(dosya)
            self.root.after(0, lambda d=dosya_adi, i=i+1, t=toplam_dosya:
                         progress_label.config(text=self.PDF_PROGRESS_LOADING_LABEL.format(i, t, d)))

            try:
                img = Image.open(dosya)
                goruntu_listesi.append(img.convert(self.IMAGE_FORMAT_RGB))
                self.log_ekle(self.LOG_PDF_IMAGE_LOADING.format(i+1, toplam_dosya, dosya_adi))
            except Exception as e:
                self.log_ekle(self.LOG_PDF_IMAGE_LOAD_ERROR.format(dosya_adi, e))
        return goruntu_listesi

    def _save_images_to_pdf(self, images, output_path, progress_var, progress_label):
        """Görüntü listesini PDF olarak kaydeder."""
        if not images:
            self.log_ekle(self.LOG_PDF_NO_IMAGES_TO_LOAD)
            self.root.after(0, lambda: messagebox.showinfo(self.TITLE_BILGI, self.INFO_PDF_NO_IMAGES_LOADED))
            return False

        self.log_ekle(self.LOG_PDF_FIRST_IMAGE_SIZE.format(images[0].width, images[0].height))

        ilk_goruntu = images[0]
        diger_goruntuler = images[1:] if len(images) > 1 else []

        self.log_ekle(self.LOG_PDF_CREATING)
        self.root.after(0, lambda: progress_label.config(text=self.PDF_PROGRESS_SAVING_LABEL))
        self.root.after(0, lambda: progress_var.set(75))  # %75 ilerleme

        try:
            ilk_goruntu.save(
                output_path,
                save_all=True,
                append_images=diger_goruntuler,
                resolution=self.PDF_RESOLUTION,
                format=self.PDF_SAVE_FORMAT
            )
            self.log_ekle(self.LOG_PDF_SAVED_SUCCESS.format(len(images), output_path))
            self.root.after(0, lambda: progress_var.set(100))
            return True
        except Exception as e:
            self.log_ekle(self.LOG_PDF_SAVING_ERROR.format(e))
            self.root.after(0, lambda: messagebox.showerror(self.TITLE_HATA, self.ERROR_PDF_OLUSTURMA.format(e)))
            return False

    def secili_klasordeki_goruntuleri_birlestir(self):
        """Aktif kitap klasöründeki tüm görüntüleri birleştirerek PDF oluşturur"""
        if not self.aktif_kitap:
            messagebox.showwarning(self.TITLE_UYARI, self.WARNING_KITAP_SECIMI_YOK)
            return
            
        kitap_klasoru = self.kayit_klasoru
        
        if not os.path.exists(kitap_klasoru):
            messagebox.showerror(self.TITLE_HATA, self.ERROR_KITAP_KLASORU_BULUNAMADI)
            return
        
        varsayilan_dosya_adi = f"{self.aktif_kitap}.pdf"
        dosya_yolu = filedialog.asksaveasfilename(
            initialdir=os.path.dirname(kitap_klasoru),
            initialfile=varsayilan_dosya_adi,
            defaultextension=".pdf",
            filetypes=[self.FILETYPE_PDF],
            title=self.DIALOG_TITLE_PDF_KAYDET
        )
        
        if not dosya_yolu:
            return
        
        progress_window, progress_var, progress_label = self._create_pdf_progress_window()
        
        def pdf_olustur_thread():
            try:
                goruntu_dosyalari = []
                for dosya in os.listdir(kitap_klasoru):
                    if dosya.lower().endswith(self.IMAGE_FILE_EXTENSION) and dosya.startswith(self.IMAGE_FILE_PREFIX):
                        tam_yol = os.path.join(kitap_klasoru, dosya)
                        goruntu_dosyalari.append(tam_yol)
                
                if not goruntu_dosyalari:
                    self.root.after(0, lambda: messagebox.showinfo(self.TITLE_BILGI, self.INFO_PDF_NO_IMAGES_FOUND_IN_DIR))
                    if progress_window.winfo_exists(): progress_window.destroy() # Ensure window is destroyed
                    return
                
                self.log_ekle(self.LOG_PDF_IMAGES_SORTING.format(len(goruntu_dosyalari)))
                goruntu_dosyalari = self.goruntu_dosyalarini_sirala(goruntu_dosyalari)
                
                # Sıralanmış dosyaların sayfa numaralarını kontrol et ve göster (isteğe bağlı, log için)
                # ...

                goruntu_listesi = self._load_images_for_pdf(goruntu_dosyalari, progress_var, progress_label)
                
                if self._save_images_to_pdf(goruntu_listesi, dosya_yolu, progress_var, progress_label):
                    self.root.after(0, lambda: messagebox.showinfo(self.TITLE_BASARILI,
                        self.INFO_PDF_SAVED_SUCCESS_MSG.format(dosya_yolu, len(goruntu_listesi))))
                    
                    kitap_bilgisi = {
                        'kitap_adi': self.aktif_kitap,
                        'sayfa_sayisi': len(goruntu_listesi),
                        'son_islem_tarihi': time.strftime(self.DATE_FORMAT_STANDARD),
                        'pdf_dosyasi': dosya_yolu
                    }
                    self.kitap_bilgisi_kaydet(kitap_klasoru, kitap_bilgisi)
            except Exception as e:
                self.log_ekle(self.LOG_PDF_GENERAL_ERROR.format(e))
                self.root.after(0, lambda: messagebox.showerror(self.TITLE_HATA, self.LOG_PDF_GENERAL_ERROR.format(e)))
            finally:
                try:
                    # locals() check might be tricky with threading, ensure goruntu_listesi is defined
                    if 'goruntu_listesi' in locals() and goruntu_listesi is not None:
                         del goruntu_listesi
                    gc.collect()
                except NameError: # goruntu_listesi might not be defined if loading failed early
                    pass
                except Exception: # General catch for other potential cleanup errors
                    pass
                if progress_window.winfo_exists():
                    self.root.after(0, progress_window.destroy)
        
        threading.Thread(target=pdf_olustur_thread, daemon=True).start()

    def kitap_sil(self):
        """Seçili kitabı siler"""
        if not self.aktif_kitap or self.aktif_kitap == self.NEW_BOOK_OPTION: # Used constant
            messagebox.showwarning(self.TITLE_UYARI, self.WARNING_KITAP_SEC_SIL)
            return
            
        onay = messagebox.askyesno(self.TITLE_ONAY, self.CONFIRM_KITAP_SIL.format(self.aktif_kitap)) # Used constant
        if not onay:
            return
            
        try:
            # Kitap klasörünü sil
            import shutil # Already at top, but good to ensure it's noted if moved
            kitap_klasoru = os.path.join(self.kitaplar_klasoru, self.aktif_kitap)
            if os.path.exists(kitap_klasoru):
                shutil.rmtree(kitap_klasoru)
                self.log_ekle(self.LOG_KITAP_SILINDI.format(self.aktif_kitap))
                
                # Aktif kitabı temizle
                self.aktif_kitap = ""
                
                # Kitap listesini güncelle
                self.kitaplari_listele()
                
                # Combobox'ı sıfırla
                if self.kitap_combobox['values']:
                    self.kitap_combobox.current(0)
                
                # PDF butonunu gizle
                if self.pdf_button_visible: # Check before pack_forget
                    self.pdf_button.pack_forget()
                    self.pdf_button_visible = False
        except Exception as e:
            messagebox.showerror(self.TITLE_HATA, self.ERROR_KITAP_SILME.format(e))
            self.log_ekle(self.LOG_KITAP_SILME_HATASI.format(e))

    def kitap_bilgisi_kaydet(self, kitap_klasoru, bilgiler):
        """Kitap bilgilerini JSON dosyasına kaydeder"""
        try:
            bilgi_dosyasi = os.path.join(kitap_klasoru, self.BOOK_INFO_FILE)
            with open(bilgi_dosyasi, 'w', encoding=self.DEFAULT_ENCODING) as f:
                json.dump(bilgiler, f, ensure_ascii=False, indent=4)
            self.log_ekle(self.LOG_KITAP_BILGISI_KAYDEDILDI)
        except Exception as e:
            self.log_ekle(self.LOG_KITAP_BILGISI_KAYDETME_HATA.format(e))
            
    def kitap_bilgilerini_oku(self, kitap_klasoru):
        """Kitap bilgilerini okur"""
        try:
            bilgi_dosyasi = os.path.join(kitap_klasoru, self.BOOK_INFO_FILE)
            if os.path.exists(bilgi_dosyasi):
                with open(bilgi_dosyasi, 'r', encoding=self.DEFAULT_ENCODING) as f:
                    return json.load(f)
        except Exception as e:
            self.log_ekle(self.LOG_KITAP_BILGILERI_OKUMA_HATA.format(e))
        return None
        
    def yeni_kitap_ekle(self):
        """Yeni kitap ekleme penceresi gösterir"""
        dialog = tk.Toplevel(self.root)
        dialog.title(self.TITLE_YENI_KITAP_EKLE)
        dialog.geometry(self.YENI_KITAP_DIALOG_GEOMETRY)
        dialog.transient(self.root)
        dialog.grab_set()  # Modal dialog
        
        ttk.Label(dialog, text=self.LABEL_KITAP_ADI, style='Title.TLabel').grid(row=0, column=0, padx=self.PAD_LARGE, pady=self.PAD_LARGE, sticky="w")
        
        kitap_adi_var = tk.StringVar()
        kitap_adi_entry = ttk.Entry(dialog, textvariable=kitap_adi_var, width=self.YENI_KITAP_ADI_ENTRY_WIDTH)
        kitap_adi_entry.grid(row=0, column=1, padx=self.PAD_LARGE, pady=self.PAD_LARGE, sticky="ew")
        kitap_adi_entry.focus_set()
        
        button_frame_yeni_kitap = ttk.Frame(dialog)
        button_frame_yeni_kitap.grid(row=1, column=0, columnspan=2, pady=self.PAD_XLARGE)
        
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
                messagebox.showwarning(self.TITLE_UYARI, self.WARNING_KITAP_ADI_GIRIN)
        
        ttk.Button(button_frame_yeni_kitap, text=self.BUTTON_IPTAL, command=iptal_et).grid(row=0, column=0, padx=self.PAD_LARGE)
        ttk.Button(button_frame_yeni_kitap, text=self.BUTTON_EKLE, command=kitap_ekle, style='Accent.TButton').grid(row=0, column=1, padx=self.PAD_LARGE)
        
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
            self.log_ekle(self.LOG_GORUNTU_SIRALANIYOR)
            
            dosya_bilgileri = []
            
            for dosya_yolu in dosya_listesi:
                try:
                    dosya_adi = os.path.basename(dosya_yolu)
                    
                    if not dosya_adi.startswith(self.IMAGE_FILE_PREFIX) or not dosya_adi.endswith(self.IMAGE_FILE_EXTENSION):
                        continue
                    
                    sayfa_no_str = dosya_adi[len(self.IMAGE_FILE_PREFIX):-len(self.IMAGE_FILE_EXTENSION)]
                    
                    try:
                        sayfa_no = int(sayfa_no_str)
                        dosya_bilgileri.append({
                            "dosya_yolu": dosya_yolu,
                            "sayfa_no": sayfa_no,
                            "dosya_adi": dosya_adi
                        })
                    except ValueError:
                        self.log_ekle(self.LOG_SAYFA_NO_COZUMLEME_UYARI.format(dosya_adi))
                        dosya_bilgileri.append({
                            "dosya_yolu": dosya_yolu,
                            "sayfa_no": float('inf'),
                            "dosya_adi": dosya_adi
                        })
                except Exception as e:
                    self.log_ekle(self.LOG_DOSYA_ISLEME_HATA.format(e))
                    continue
            
            dosya_bilgileri.sort(key=lambda x: x["sayfa_no"])
            
            self.log_ekle(self.LOG_TOPLAM_DOSYA_SIRALANDI.format(len(dosya_bilgileri)))
            
            if len(dosya_bilgileri) > 0:
                ilk_10_dosya = [f"{bilgi['dosya_adi']}({bilgi['sayfa_no']})" for bilgi in dosya_bilgileri[:10]] # TODO: Constant for 10
                self.log_ekle(self.LOG_ILK_10_DOSYA.format(', '.join(ilk_10_dosya)))
                
                if len(dosya_bilgileri) > 20: # TODO: Constant for 20
                    son_10_dosya = [f"{bilgi['dosya_adi']}({bilgi['sayfa_no']})" for bilgi in dosya_bilgileri[-10:]] # TODO: Constant for 10
                    self.log_ekle(self.LOG_SON_10_DOSYA.format(', '.join(son_10_dosya)))
            
            return [bilgi["dosya_yolu"] for bilgi in dosya_bilgileri]
        
        except Exception as e:
            self.log_ekle(self.LOG_GORUNTU_SIRALAMA_HATA.format(e))
            return dosya_listesi
    
    def kitap_klasoru_olustur(self, kitap_adi):
        """Kitap için klasör oluşturur"""
        if not kitap_adi:
            return None
            
        kitap_adi_duzgun = self.dosya_adi_duzenle(kitap_adi)
        kitap_klasoru = os.path.join(self.kitaplar_klasoru, kitap_adi_duzgun)
        
        if not os.path.exists(kitap_klasoru):
            os.makedirs(kitap_klasoru)
            self.log_ekle(self.LOG_YENI_KITAP_KLASORU_OLUSTURULDU.format(kitap_adi))
        
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
        self.log_ekle(self.LOG_TARAMA_MODU_DEGISTI.format(self.tarama_modu))
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
            self.log_ekle(self.LOG_SAYFA_YUKLEME_KONTROL_HATA.format(e))
            return False
            
    def ekran_goruntusu_al(self):
        x1, y1, x2, y2 = self.tarama_alani['x1'], self.tarama_alani['y1'], self.tarama_alani['x2'], self.tarama_alani['y2']
        
        try:
            screenshot = pyautogui.screenshot(region=(x1, y1, x2-x1, y2-y1))
            return screenshot
        except Exception as e:
            self.log_ekle(self.LOG_EKRAN_GORUNTUSU_HATA.format(e))
            return None
    
    def sayfa_kaydet(self, goruntu, sayfa_no):
        try:
            if not os.path.exists(self.kayit_klasoru):
                os.makedirs(self.kayit_klasoru)
                
            dosya_adi = f"{self.IMAGE_FILE_PREFIX}{sayfa_no}{self.IMAGE_FILE_EXTENSION}"
            tam_yol = os.path.join(self.kayit_klasoru, dosya_adi)
            goruntu.save(tam_yol)
            self.log_ekle(self.LOG_SAYFA_KAYDEDILDI.format(sayfa_no, dosya_adi))
            return tam_yol
        except Exception as e:
            self.log_ekle(self.LOG_SAYFA_KAYDET_HATA.format(e))
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
                    if dosya.startswith(self.IMAGE_FILE_PREFIX) and dosya.endswith(self.IMAGE_FILE_EXTENSION):
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
            self.log_ekle(self.LOG_GORUNTU_BENZERLIK_HATA.format(e))
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
            self.log_ekle(self.LOG_GORUNTU_BIRLESTIRME_HATA.format(e))
            return None

    def baslangic_sayfasini_guncelle(self):
        """Başlangıç sayfa numarasını günceller"""
        try:
            yeni_sayfa = int(self.baslangic_sayfa_var.get())
            if yeni_sayfa > 0:
                self.sayfa_no = yeni_sayfa
                self.sayfa_bilgisi_guncelle()
                self.log_ekle(self.LOG_BASLANGIC_SAYFA_GUNCELLENDI.format(yeni_sayfa))
                
                self.baslangic_sayfa_entry.config(state='readonly')
            else:
                messagebox.showwarning(self.TITLE_UYARI, self.WARNING_SAYFA_NO_GECERSIZ)
        except ValueError:
            messagebox.showwarning(self.TITLE_UYARI, self.WARNING_GECERLI_SAYFA_NO_GIRIN)
        
        self.baslangic_sayfa_entry.config(state='readonly')

    def bilgi_kontrolu(self):
        """Ayarlara göre bilgi mesajının gösterilip gösterilmeyeceğini kontrol eder"""
        try:
            ayarlar = {}
            if os.path.exists(self.config_dosyasi):
                with open(self.config_dosyasi, 'r') as f:
                    ayarlar = json.load(f)
            
            if not ayarlar.get('baslangic_bilgi_goster', True) == False: # TODO: Constant for 'baslangic_bilgi_goster'
                self.baslangic_bilgi_goster()
                
        except Exception: # More general catch, as specific error isn't critical here
            self.baslangic_bilgi_goster()

    def baslangic_bilgi_goster(self):
        """Uygulama ilk açıldığında bilgi mesajı gösterir"""
        info_window = tk.Toplevel(self.root)
        info_window.title(self.TITLE_HOS_GELDINIZ)
        info_window.geometry(self.HOS_GELDINIZ_DIALOG_GEOMETRY)
        info_window.transient(self.root)
        info_window.grab_set()
        
        info_frame = ttk.Frame(info_window, padding=self.PAD_XLARGE)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(info_frame, text=self.WELCOME_MESSAGE_HEADER,
                 font=('Segoe UI', 12, 'bold')).pack(pady=(0, self.PAD_LARGE))

        bilgi_text = self.WELCOME_MESSAGE_BODY # Already a constant

        text_widget = tk.Text(info_frame, height=self.HOS_GELDINIZ_TEXT_HEIGHT, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, pady=self.PAD_LARGE)
        text_widget.insert(tk.END, bilgi_text)
        text_widget.config(state=tk.DISABLED)
        
        buton_frame_bilgi = ttk.Frame(info_frame)
        buton_frame_bilgi.pack(fill=tk.X, pady=self.PAD_LARGE)
        
        ttk.Button(buton_frame_bilgi, text=self.BUTTON_ACILISTA_GOSTERME,
                  command=lambda: self.ayarlari_kaydet_ozel("baslangic_bilgi_goster", False), # TODO: Constant for key
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=self.PAD_MEDIUM)
        
        ttk.Button(buton_frame_bilgi, text=self.BUTTON_BASLA, command=info_window.destroy,
                  style='Accent.TButton').pack(side=tk.RIGHT, padx=self.PAD_MEDIUM)
        
    def ayarlari_kaydet_ozel(self, anahtar, deger):
        """Özel bir ayarı günceller ve kaydeder"""
        try:
            ayarlar = {}
            if os.path.exists(self.config_dosyasi):
                with open(self.config_dosyasi, 'r') as f:
                    ayarlar = json.load(f)
            
            ayarlar[anahtar] = deger
            
            with open(self.config_dosyasi, 'w') as f:
                json.dump(ayarlar, f)
                
        except Exception as e:
            print(self.LOG_OZEL_AYAR_KAYDETME_HATA.format(e))

    def hedef_sayfasini_guncelle(self):
        """Hedef sayfa sayısını günceller"""
        try:
            yeni_hedef = int(self.hedef_sayfa_var.get())
            if yeni_hedef > 0:
                self.hedef_sayfa_sayisi = yeni_hedef
                self.log_ekle(self.LOG_HEDEF_SAYFA_GUNCELLENDI.format(yeni_hedef))
                self.ayarlari_kaydet()
            else:
                messagebox.showwarning(self.TITLE_UYARI, self.WARNING_HEDEF_SAYFA_GECERSIZ)
        except ValueError:
            messagebox.showwarning(self.TITLE_UYARI, self.WARNING_GECERLI_HEDEF_SAYFA_GIRIN)

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