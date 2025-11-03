import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import json

class GayrimenkulDegerlemeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gayrimenkul Değerleme Rapor Sistemi")
        self.root.geometry("1000x750")

        self.tum_dosyalar = []
        self.analiz_sonuclari = {}
        self.emsal_dosyalar = []
        self.emsal_degerleme = {}

        self.setup_ui()

    def setup_ui(self):
        # Ana frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Başlık
        title_label = ttk.Label(main_frame, text="Gayrimenkul Değerleme Rapor Sistemi",
                                font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Dosya Yükleme
        dosya_frame = ttk.LabelFrame(main_frame, text="Dosya Yükleme", padding="10")
        dosya_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        ttk.Button(dosya_frame, text="Dosya Ekle (Belge/Fotoğraf)",
                   command=self.dosya_ekle, width=30).grid(row=0, column=0, padx=5, pady=5)
        
        ttk.Button(dosya_frame, text="Emsal Ekle (İlan/Fotoğraf)",
                   command=self.emsal_ekle, width=30).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(dosya_frame, text="AI otomatik olarak belge türünü tespit edecektir - Alanlar düzenlenebilir",
                  font=('Arial', 9, 'italic')).grid(row=1, column=0, columnspan=2, pady=5)

        # Form - DÜZENLENEBİLİR ENTRY'LER
        form_frame = ttk.LabelFrame(main_frame, text="Gayrimenkul Bilgileri (Düzenlenebilir)", padding="10")
        form_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        # SOL SÜTUN - Entry widget'ları
        row_idx = 0
        ttk.Label(form_frame, text="Adres:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=0, sticky=tk.W, pady=3, padx=(5, 5))
        self.adres_entry = ttk.Entry(form_frame, width=35)
        self.adres_entry.grid(row=row_idx, column=1, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1

        ttk.Label(form_frame, text="İl:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=0, sticky=tk.W, pady=3, padx=(5, 5))
        self.il_entry = ttk.Entry(form_frame, width=35)
        self.il_entry.grid(row=row_idx, column=1, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1

        ttk.Label(form_frame, text="İlçe:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=0, sticky=tk.W, pady=3, padx=(5, 5))
        self.ilce_entry = ttk.Entry(form_frame, width=35)
        self.ilce_entry.grid(row=row_idx, column=1, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1

        ttk.Label(form_frame, text="Mahalle:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=0, sticky=tk.W, pady=3, padx=(5, 5))
        self.mahalle_entry = ttk.Entry(form_frame, width=35)
        self.mahalle_entry.grid(row=row_idx, column=1, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1

        ttk.Label(form_frame, text="Sokak/Cadde:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=0, sticky=tk.W, pady=3, padx=(5, 5))
        self.sokak_entry = ttk.Entry(form_frame, width=35)
        self.sokak_entry.grid(row=row_idx, column=1, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1

        ttk.Label(form_frame, text="Bina No:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=0, sticky=tk.W, pady=3, padx=(5, 5))
        self.bina_no_entry = ttk.Entry(form_frame, width=35)
        self.bina_no_entry.grid(row=row_idx, column=1, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1

        ttk.Label(form_frame, text="Daire No:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=0, sticky=tk.W, pady=3, padx=(5, 5))
        self.daire_no_entry = ttk.Entry(form_frame, width=35)
        self.daire_no_entry.grid(row=row_idx, column=1, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1

        ttk.Label(form_frame, text="Ada:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=0, sticky=tk.W, pady=3, padx=(5, 5))
        self.ada_entry = ttk.Entry(form_frame, width=35)
        self.ada_entry.grid(row=row_idx, column=1, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1

        ttk.Label(form_frame, text="Parsel:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=0, sticky=tk.W, pady=3, padx=(5, 5))
        self.parsel_entry = ttk.Entry(form_frame, width=35)
        self.parsel_entry.grid(row=row_idx, column=1, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1

        ttk.Label(form_frame, text="Tapu Türü:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=0, sticky=tk.W, pady=3, padx=(5, 5))
        self.tapu_turu_entry = ttk.Entry(form_frame, width=35)
        self.tapu_turu_entry.grid(row=row_idx, column=1, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1

        ttk.Label(form_frame, text="Malik:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=0, sticky=tk.W, pady=3, padx=(5, 5))
        self.malik_entry = ttk.Entry(form_frame, width=35)
        self.malik_entry.grid(row=row_idx, column=1, pady=3, padx=5, sticky=(tk.W, tk.E))

        # SAĞ SÜTUN
        row_idx = 0
        ttk.Label(form_frame, text="Arsa Alanı:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=2, sticky=tk.W, pady=3, padx=(15, 5))
        self.arsa_alani_entry = ttk.Entry(form_frame, width=35)
        self.arsa_alani_entry.grid(row=row_idx, column=3, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1

        ttk.Label(form_frame, text="Brüt Alan:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=2, sticky=tk.W, pady=3, padx=(15, 5))
        self.brut_alan_entry = ttk.Entry(form_frame, width=35)
        self.brut_alan_entry.grid(row=row_idx, column=3, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1

        ttk.Label(form_frame, text="Net Alan:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=2, sticky=tk.W, pady=3, padx=(15, 5))
        self.net_alan_entry = ttk.Entry(form_frame, width=35)
        self.net_alan_entry.grid(row=row_idx, column=3, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1

        ttk.Label(form_frame, text="Oda Sayısı:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=2, sticky=tk.W, pady=3, padx=(15, 5))
        self.oda_sayisi_entry = ttk.Entry(form_frame, width=35)
        self.oda_sayisi_entry.grid(row=row_idx, column=3, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1

        ttk.Label(form_frame, text="Kat Sayısı:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=2, sticky=tk.W, pady=3, padx=(15, 5))
        self.kat_sayisi_entry = ttk.Entry(form_frame, width=35)
        self.kat_sayisi_entry.grid(row=row_idx, column=3, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1

        ttk.Label(form_frame, text="Bulunduğu Kat:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=2, sticky=tk.W, pady=3, padx=(15, 5))
        self.bulundugu_kat_entry = ttk.Entry(form_frame, width=35)
        self.bulundugu_kat_entry.grid(row=row_idx, column=3, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1

        ttk.Label(form_frame, text="Bina Yaşı:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=2, sticky=tk.W, pady=3, padx=(15, 5))
        self.bina_yasi_entry = ttk.Entry(form_frame, width=35)
        self.bina_yasi_entry.grid(row=row_idx, column=3, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1

        ttk.Label(form_frame, text="İmar Durumu:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=2, sticky=tk.W, pady=3, padx=(15, 5))
        self.imar_durumu_entry = ttk.Entry(form_frame, width=35)
        self.imar_durumu_entry.grid(row=row_idx, column=3, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1

        ttk.Label(form_frame, text="Kullanım Amacı:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=2, sticky=tk.W, pady=3, padx=(15, 5))
        self.kullanim_amaci_entry = ttk.Entry(form_frame, width=35)
        self.kullanim_amaci_entry.grid(row=row_idx, column=3, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1
        
        ttk.Label(form_frame, text="Enerji Sınıfı:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=2, sticky=tk.W, pady=3, padx=(15, 5))
        self.enerji_sinifi_entry = ttk.Entry(form_frame, width=35)
        self.enerji_sinifi_entry.grid(row=row_idx, column=3, pady=3, padx=5, sticky=(tk.W, tk.E))

        # Dosya Listesi
        liste_frame = ttk.LabelFrame(main_frame, text="Yüklenen Dosyalar", padding="10")
        liste_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)

        columns = ('Dosya Adı', 'Tür', 'Durum')
        self.dosya_tree = ttk.Treeview(liste_frame, columns=columns, show='headings', height=6)

        self.dosya_tree.heading('Dosya Adı', text='Dosya Adı')
        self.dosya_tree.heading('Tür', text='Belge Türü')
        self.dosya_tree.heading('Durum', text='Durum')

        self.dosya_tree.column('Dosya Adı', width=350)
        self.dosya_tree.column('Tür', width=200)
        self.dosya_tree.column('Durum', width=150)

        self.dosya_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        scrollbar = ttk.Scrollbar(liste_frame, orient=tk.VERTICAL, command=self.dosya_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.dosya_tree.configure(yscrollcommand=scrollbar.set)

        # İşlem Butonları
        islem_frame = ttk.Frame(main_frame)
        islem_frame.grid(row=4, column=0, columnspan=2, pady=20)

        ttk.Button(islem_frame, text="Dosyaları Analiz Et (AI)",
                   command=self.dosyalari_siniflandir, width=25).grid(row=0, column=0, padx=10)
        ttk.Button(islem_frame, text="Rapor Oluştur (Emsal Yok)",
                   command=lambda: self.rapor_olustur(emsal_dahil=False), width=25).grid(row=0, column=1, padx=10)
        ttk.Button(islem_frame, text="Rapor Oluştur (Emsal Dahil)",
                   command=lambda: self.rapor_olustur(emsal_dahil=True), width=25).grid(row=0, column=2, padx=10)

        # Durum
        self.durum_label = ttk.Label(main_frame, text="Hazır", relief=tk.SUNKEN)
        self.durum_label.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

    def dosya_ekle(self):
        dosyalar = filedialog.askopenfilenames(
            title="Dosya Seç",
            filetypes=[
                ("Desteklenen Dosyalar", "*.pdf *.jpg *.jpeg *.png *.tif *.tiff"),
                ("Tüm Dosyalar", "*.*")
            ]
        )

        for dosya in dosyalar:
            dosya_info = {
                "yol": dosya,
                "isim": Path(dosya).name,
                "tip": "Bilinmiyor",
                "durum": "Sınıflandırılmamış"
            }
            self.tum_dosyalar.append(dosya_info)
            self.dosya_tree.insert('', 'end', values=(Path(dosya).name, "Bilinmiyor", "Sınıflandırılmamış"))

        self.durum_label.config(text=f"{len(dosyalar)} dosya eklendi.")

    def emsal_ekle(self):
        dosyalar = filedialog.askopenfilenames(
            title="Emsal Dosyaları Seç",
            filetypes=[("Resim Dosyaları", "*.jpg *.jpeg *.png"), ("Tüm Dosyalar", "*.*")]
        )

        for dosya in dosyalar:
            self.emsal_dosyalar.append(dosya)
            self.dosya_tree.insert('', 'end', values=(Path(dosya).name, "Emsal", "Analiz Bekliyor"))

        self.durum_label.config(text=f"{len(dosyalar)} emsal eklendi.")

    def dosyalari_siniflandir(self):
        if not self.tum_dosyalar:
            messagebox.showwarning("Uyarı", "Lütfen dosya yükleyin!")
            return

        self.durum_label.config(text="Dosyalar analiz ediliyor...")
        self.root.update()

        from ai_processor_gelismis import GelismisAIBelgeIsleyici

        try:
            isleyici = GelismisAIBelgeIsleyici()

            for item in self.dosya_tree.get_children():
                self.dosya_tree.delete(item)

            # Dosya sınıflandırma için eski AI processor kullanılıyor
            from ai_processor import AIBelgeIsleyici
            siniflandirici = AIBelgeIsleyici()
            
            for idx, dosya in enumerate(self.tum_dosyalar):
                self.durum_label.config(text=f"Dosya {idx+1}/{len(self.tum_dosyalar)}: {dosya['isim']}")
                self.root.update()

                try:
                    dosya_turu = siniflandirici.dosya_turu_belirle(dosya['yol'])
                    dosya['tip'] = dosya_turu
                    dosya['durum'] = "Sınıflandırıldı" if "hata" not in dosya_turu.lower() else "Hata"
                    self.dosya_tree.insert('', 'end', values=(dosya['isim'], dosya_turu, dosya['durum']))
                except Exception as e:
                    dosya['tip'] = f"Hata: {str(e)[:30]}"
                    dosya['durum'] = "Hata"
                    self.dosya_tree.insert('', 'end', values=(dosya['isim'], dosya['tip'], "Hata"))

            # Belgeleri analiz et
            belgeler = [d for d in self.tum_dosyalar if d['tip'] not in ['Fotoğraf', 'Bilinmiyor', 'Emsal']]

            if belgeler:
                self.durum_label.config(text="Belgelerden veri çıkarılıyor...")
                self.root.update()
                
                sonuclar = isleyici.belgeleri_analiz_et(belgeler)
                
                # Entry'lere doldur - None değerlerini boş string'e çevir
                def doldur(entry, deger):
                    entry.delete(0, tk.END)
                    entry.insert(0, str(deger) if deger is not None and str(deger) != 'null' else "")
                
                doldur(self.adres_entry, sonuclar.get("adres"))
                doldur(self.il_entry, sonuclar.get("il"))
                doldur(self.ilce_entry, sonuclar.get("ilce"))
                doldur(self.mahalle_entry, sonuclar.get("mahalle"))
                doldur(self.sokak_entry, sonuclar.get("sokak"))
                doldur(self.bina_no_entry, sonuclar.get("bina_no"))
                doldur(self.daire_no_entry, sonuclar.get("daire_no"))
                doldur(self.ada_entry, sonuclar.get("ada"))
                doldur(self.parsel_entry, sonuclar.get("parsel"))
                doldur(self.tapu_turu_entry, sonuclar.get("tapu_turu"))
                doldur(self.malik_entry, sonuclar.get("malik"))
                doldur(self.arsa_alani_entry, sonuclar.get("arsa_alani"))
                doldur(self.brut_alan_entry, sonuclar.get("brut_alan"))
                doldur(self.net_alan_entry, sonuclar.get("net_alan"))
                doldur(self.oda_sayisi_entry, sonuclar.get("oda_sayisi"))
                doldur(self.kat_sayisi_entry, sonuclar.get("kat_sayisi"))
                doldur(self.bulundugu_kat_entry, sonuclar.get("bulundugu_kat"))
                doldur(self.bina_yasi_entry, sonuclar.get("bina_yasi"))
                doldur(self.imar_durumu_entry, sonuclar.get("imar_durumu"))
                doldur(self.kullanim_amaci_entry, sonuclar.get("kullanim_amaci"))
                doldur(self.enerji_sinifi_entry, sonuclar.get("enerji_sinifi"))
                
                self.analiz_sonuclari = sonuclar
                
                # Gelişmiş analiz sonuçlarını göster
                gelismis_bilgi = []
                
                if sonuclar.get("kat_plani_mevcut") == "Evet":
                    gelismis_bilgi.append("\n✅ KAT PLANI ANALİZİ:")
                    if sonuclar.get("kat_plani_daire_no"):
                        gelismis_bilgi.append(f"  - Daire No: {sonuclar['kat_plani_daire_no']}")
                    if sonuclar.get("kat_plani_oda_sayisi"):
                        gelismis_bilgi.append(f"  - Oda sayısı: {sonuclar['kat_plani_oda_sayisi']}")
                    if sonuclar.get("kat_plani_toplam_net_m2"):
                        gelismis_bilgi.append(f"  - Toplam net alan: {sonuclar['kat_plani_toplam_net_m2']} m²")
                    if sonuclar.get("kat_plani_hesaplamalar"):
                        gelismis_bilgi.append("  - Ölçü Hesaplamaları:")
                        for hesap in sonuclar['kat_plani_hesaplamalar']:
                            gelismis_bilgi.append(f"    * {hesap}")
                    elif sonuclar.get("kat_plani_odalar"):
                        gelismis_bilgi.append("  - Odalar:")
                        for oda in sonuclar['kat_plani_odalar']:
                            gelismis_bilgi.append(f"    * {oda}")
                
                if sonuclar.get("m2_tablosu_mevcut") == "Evet":
                    gelismis_bilgi.append("\n✅ m² TABLOSU ANALİZİ:")
                    if sonuclar.get("m2_tablosu_brut"):
                        gelismis_bilgi.append(f"  - Brüt alan: {sonuclar['m2_tablosu_brut']} m²")
                    if sonuclar.get("m2_tablosu_net"):
                        gelismis_bilgi.append(f"  - Net alan: {sonuclar['m2_tablosu_net']} m²")
                    if sonuclar.get("m2_tablosu_ortak_alan"):
                        gelismis_bilgi.append(f"  - Ortak alan: {sonuclar['m2_tablosu_ortak_alan']} m²")
                
                if sonuclar.get("enerji_belgesi_mevcut") == "Evet":
                    gelismis_bilgi.append("\n✅ ENERJİ BELGESİ ANALİZİ:")
                    if sonuclar.get("enerji_sinifi"):
                        gelismis_bilgi.append(f"  - Enerji sınıfı: {sonuclar['enerji_sinifi']}")
                    if sonuclar.get("enerji_tuketimi"):
                        gelismis_bilgi.append(f"  - Yıllık tüketim: {sonuclar['enerji_tuketimi']} kWh/yıl")
                    if sonuclar.get("enerji_co2_salimi"):
                        gelismis_bilgi.append(f"  - CO2 salımı: {sonuclar['enerji_co2_salimi']} kg/yıl")
                    if sonuclar.get("isitma_tipi"):
                        gelismis_bilgi.append(f"  - Isıtma: {sonuclar['isitma_tipi']}")
                    if sonuclar.get("sogutma_tipi"):
                        gelismis_bilgi.append(f"  - Soğutma: {sonuclar['sogutma_tipi']}")
                
                if gelismis_bilgi:
                    bilgi_mesaji = "\n".join(gelismis_bilgi)
                    messagebox.showinfo(
                        "Gelişmiş Analiz Sonuçları",
                        f"AI aşağıdaki ek bilgileri tespit etti:{bilgi_mesaji}\n\nBu bilgiler raporda kullanılacak."
                    )

            self.durum_label.config(text="Analiz tamamlandı!")
            messagebox.showinfo("Başarılı", "Dosyalar analiz edildi. Verileri kontrol edip düzeltebilirsiniz!")

        except Exception as e:
            self.durum_label.config(text=f"Hata: {str(e)}")
            messagebox.showerror("Hata", f"Analiz hatası:\n{str(e)}")

    def rapor_olustur(self, emsal_dahil=False):
        if not self.tum_dosyalar:
            messagebox.showwarning("Uyarı", "Lütfen dosya yükleyin!")
            return

        # Entry'lerden güncel verileri al
        rapor_verisi = {
            'adres': self.adres_entry.get(),
            'il': self.il_entry.get(),
            'ilce': self.ilce_entry.get(),
            'mahalle': self.mahalle_entry.get(),
            'sokak': self.sokak_entry.get(),
            'bina_no': self.bina_no_entry.get(),
            'daire_no': self.daire_no_entry.get(),
            'ada': self.ada_entry.get(),
            'parsel': self.parsel_entry.get(),
            'tapu_turu': self.tapu_turu_entry.get(),
            'malik': self.malik_entry.get(),
            'arsa_alani': self.arsa_alani_entry.get(),
            'brut_alan': self.brut_alan_entry.get(),
            'net_alan': self.net_alan_entry.get(),
            'oda_sayisi': self.oda_sayisi_entry.get(),
            'kat_sayisi': self.kat_sayisi_entry.get(),
            'bulundugu_kat': self.bulundugu_kat_entry.get(),
            'bina_yasi': self.bina_yasi_entry.get(),
            'imar_durumu': self.imar_durumu_entry.get(),
            'kullanim_amaci': self.kullanim_amaci_entry.get(),
            'enerji_sinifi': self.enerji_sinifi_entry.get()
        }
        
        # Gelişmiş analiz sonuçlarını da ekle
        if hasattr(self, 'analiz_sonuclari'):
            # Kat planı, m² tablosu, enerji belgesi vb. gelişmiş verileri ekle
            for key in ['kat_plani_mevcut', 'kat_plani_odalar', 'kat_plani_toplam_net_m2',
                        'm2_tablosu_mevcut', 'm2_tablosu_brut', 'm2_tablosu_net',
                        'enerji_belgesi_mevcut', 'enerji_tuketimi', 'enerji_co2_salimi',
                        'isitma_tipi', 'sogutma_tipi']:
                if key in self.analiz_sonuclari:
                    rapor_verisi[key] = self.analiz_sonuclari[key]

        belgeler = [d for d in self.tum_dosyalar if d['tip'] not in ['Fotoğraf', 'Bilinmiyor', 'Emsal']]
        fotograflar = [d['yol'] for d in self.tum_dosyalar if d['tip'] == 'Fotoğraf']

        rapor_verisi['belgeler'] = belgeler
        rapor_verisi['fotograflar'] = fotograflar
        rapor_verisi['tum_dosyalar'] = self.tum_dosyalar

        if emsal_dahil and self.emsal_dosyalar:
            self.durum_label.config(text="Emsaller analiz ediliyor (bu biraz sürebilir)...")
            self.root.update()
            
            try:
                from emsal_processor import EmsalIsleyici
                emsal_isleyici = EmsalIsleyici()
                
                # TIMEOUT kontrolü için her emsal için max 30 saniye
                import threading
                import time
                
                def emsal_isle_timeout():
                    try:
                        self.emsal_degerleme = emsal_isleyici.emsalleri_toplu_isle(
                            self.emsal_dosyalar,
                            rapor_verisi
                        )
                    except Exception as e:
                        self.emsal_degerleme = {'hata': str(e)}
                
                thread = threading.Thread(target=emsal_isle_timeout)
                thread.daemon = True
                thread.start()
                
                # Max 5 dakika bekle
                timeout = 300  # 5 dakika
                start_time = time.time()
                
                while thread.is_alive() and (time.time() - start_time) < timeout:
                    self.durum_label.config(text=f"Emsaller analiz ediliyor... ({int(time.time() - start_time)}s)")
                    self.root.update()
                    time.sleep(1)
                
                if thread.is_alive():
                    messagebox.showwarning("Uyarı", "Emsal analizi çok uzun sürdü. Emsal olmadan devam edilecek.")
                    rapor_verisi['emsal_degerleme'] = {}
                else:
                    rapor_verisi['emsal_degerleme'] = self.emsal_degerleme
                    
                for item in self.dosya_tree.get_children():
                    values = self.dosya_tree.item(item)['values']
                    if values[1] == 'Emsal':
                        self.dosya_tree.item(item, values=(values[0], 'Emsal', 'Analiz Edildi'))
                        
            except Exception as e:
                messagebox.showwarning("Uyarı", f"Emsal analizi hatası: {str(e)}\n\nEmsal olmadan devam edilecek.")
                rapor_verisi['emsal_degerleme'] = {}
        else:
            rapor_verisi['emsal_degerleme'] = {}

        self.durum_label.config(text="Rapor PDF oluşturuluyor...")
        self.root.update()

        from spk_report_generator import SPKRaporOlusturucu

        try:
            olusturucu = SPKRaporOlusturucu()
            rapor_dosyasi = olusturucu.rapor_olustur(rapor_verisi)

            self.durum_label.config(text=f"Rapor oluşturuldu: {rapor_dosyasi}")
            messagebox.showinfo("Başarılı", f"Rapor oluşturuldu:\n{rapor_dosyasi}")

        except IndexError as e:
            self.durum_label.config(text=f"Hata: Liste indeks hatası")
            messagebox.showerror("Hata", f"Rapor oluşturma hatası:\n\nListe indeks hatası - muhtemelen bir veri eksik.\nLütfen tüm alanların dolu olduğundan emin olun.\n\nDetay: {str(e)}")
        except Exception as e:
            self.durum_label.config(text=f"Hata: {str(e)}")
            messagebox.showerror("Hata", f"Rapor oluşturma hatası:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = GayrimenkulDegerlemeApp(root)
    root.mainloop()
