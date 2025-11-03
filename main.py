# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import json
import sys

# Windows encoding fix - Python 3.13 uyumlu
if sys.platform == 'win32':
    try:
        import codecs
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'ignore')
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'ignore')
    except (AttributeError, TypeError):
        pass  # Encoding zaten düzgün veya gerek yok

class GayrimenkulDegerlemeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gayrimenkul Değerleme Rapor Sistemi")
        self.root.geometry("900x700")

        self.tum_dosyalar = []  # Tüm yüklenen dosyalar (belge + fotoğraf)
        self.analiz_sonuclari = {}  # AI analiz sonuçları
        self.emsal_dosyalar = []  # Emsal fotoğrafları/belgeleri
        self.emsal_degerleme = {}  # Emsal değerleme sonuçları

        self.setup_ui()

    def setup_ui(self):
        # Ana frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Başlık
        title_label = ttk.Label(main_frame, text="Gayrimenkul Değerleme Rapor Sistemi",
                                font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Dosya Yükleme Bölümü (Tek alan - AI otomatik sınıflandıracak)
        dosya_frame = ttk.LabelFrame(main_frame, text="Dosya Yükleme", padding="10")
        dosya_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        # Pencere boyutunu genişlet
        self.root.geometry("900x850")

        ttk.Button(dosya_frame, text="Dosya Ekle (Belge/Fotoğraf)",
                   command=self.dosya_ekle, width=30).grid(row=0, column=0, padx=5, pady=5)
        
        ttk.Button(dosya_frame, text="Emsal Ekle (İlan/Fotoğraf)",
                   command=self.emsal_ekle, width=30).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(dosya_frame, text="AI otomatik olarak belge türünü tespit edecektir",
                  font=('Arial', 9, 'italic')).grid(row=1, column=0, columnspan=2, pady=5)

        # Form Bilgileri Bölümü (AI Tarafından Doldurulacak) - İKİ SÜTUN
        form_frame = ttk.LabelFrame(main_frame, text="Gayrimenkul Bilgileri (AI tarafından otomatik doldurulur)", padding="10")
        form_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        # Bilgi gösterimi için label'lar (sadece okuma)
        bilgi_style = {'background': '#f0f0f0', 'relief': 'sunken', 'width': 30, 'anchor': 'w'}

        # SOL SÜTUN
        row_idx = 0
        ttk.Label(form_frame, text="Adres:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=0, sticky=tk.W, pady=3, padx=(5, 5))
        self.adres_label = ttk.Label(form_frame, text="-", **bilgi_style)
        self.adres_label.grid(row=row_idx, column=1, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1

        ttk.Label(form_frame, text="İl:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=0, sticky=tk.W, pady=3, padx=(5, 5))
        self.il_label = ttk.Label(form_frame, text="-", **bilgi_style)
        self.il_label.grid(row=row_idx, column=1, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1

        ttk.Label(form_frame, text="İlçe:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=0, sticky=tk.W, pady=3, padx=(5, 5))
        self.ilce_label = ttk.Label(form_frame, text="-", **bilgi_style)
        self.ilce_label.grid(row=row_idx, column=1, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1

        ttk.Label(form_frame, text="Mahalle:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=0, sticky=tk.W, pady=3, padx=(5, 5))
        self.mahalle_label = ttk.Label(form_frame, text="-", **bilgi_style)
        self.mahalle_label.grid(row=row_idx, column=1, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1

        ttk.Label(form_frame, text="Ada:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=0, sticky=tk.W, pady=3, padx=(5, 5))
        self.ada_label = ttk.Label(form_frame, text="-", **bilgi_style)
        self.ada_label.grid(row=row_idx, column=1, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1

        ttk.Label(form_frame, text="Parsel:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=0, sticky=tk.W, pady=3, padx=(5, 5))
        self.parsel_label = ttk.Label(form_frame, text="-", **bilgi_style)
        self.parsel_label.grid(row=row_idx, column=1, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1

        ttk.Label(form_frame, text="Tapu Türü:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=0, sticky=tk.W, pady=3, padx=(5, 5))
        self.tapu_turu_label = ttk.Label(form_frame, text="-", **bilgi_style)
        self.tapu_turu_label.grid(row=row_idx, column=1, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1

        ttk.Label(form_frame, text="Malik:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=0, sticky=tk.W, pady=3, padx=(5, 5))
        self.malik_label = ttk.Label(form_frame, text="-", **bilgi_style)
        self.malik_label.grid(row=row_idx, column=1, pady=3, padx=5, sticky=(tk.W, tk.E))

        # SAĞ SÜTUN
        row_idx = 0
        ttk.Label(form_frame, text="Arsa Alanı:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=2, sticky=tk.W, pady=3, padx=(15, 5))
        self.arsa_alani_label = ttk.Label(form_frame, text="-", **bilgi_style)
        self.arsa_alani_label.grid(row=row_idx, column=3, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1

        ttk.Label(form_frame, text="Brüt Alan:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=2, sticky=tk.W, pady=3, padx=(15, 5))
        self.brut_alan_label = ttk.Label(form_frame, text="-", **bilgi_style)
        self.brut_alan_label.grid(row=row_idx, column=3, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1

        ttk.Label(form_frame, text="Net Alan:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=2, sticky=tk.W, pady=3, padx=(15, 5))
        self.net_alan_label = ttk.Label(form_frame, text="-", **bilgi_style)
        self.net_alan_label.grid(row=row_idx, column=3, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1

        ttk.Label(form_frame, text="Oda Sayısı:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=2, sticky=tk.W, pady=3, padx=(15, 5))
        self.oda_sayisi_label = ttk.Label(form_frame, text="-", **bilgi_style)
        self.oda_sayisi_label.grid(row=row_idx, column=3, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1

        ttk.Label(form_frame, text="Kat Sayısı:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=2, sticky=tk.W, pady=3, padx=(15, 5))
        self.kat_sayisi_label = ttk.Label(form_frame, text="-", **bilgi_style)
        self.kat_sayisi_label.grid(row=row_idx, column=3, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1

        ttk.Label(form_frame, text="Bina Yaşı:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=2, sticky=tk.W, pady=3, padx=(15, 5))
        self.bina_yasi_label = ttk.Label(form_frame, text="-", **bilgi_style)
        self.bina_yasi_label.grid(row=row_idx, column=3, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1

        ttk.Label(form_frame, text="İmar Durumu:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=2, sticky=tk.W, pady=3, padx=(15, 5))
        self.imar_durumu_label = ttk.Label(form_frame, text="-", **bilgi_style)
        self.imar_durumu_label.grid(row=row_idx, column=3, pady=3, padx=5, sticky=(tk.W, tk.E))
        row_idx += 1

        ttk.Label(form_frame, text="Kullanım Amacı:", font=('Arial', 9, 'bold')).grid(row=row_idx, column=2, sticky=tk.W, pady=3, padx=(15, 5))
        self.kullanim_amaci_label = ttk.Label(form_frame, text="-", **bilgi_style)
        self.kullanim_amaci_label.grid(row=row_idx, column=3, pady=3, padx=5, sticky=(tk.W, tk.E))

        # Manuel Veri Giriş Bölümü (Rapor Bilgileri)
        manuel_frame = ttk.LabelFrame(main_frame, text="Rapor Bilgileri (Manuel Giriş)", padding="10")
        manuel_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        form_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        # Manuel giriş alanları için Entry widgets
        entry_width = 28

        # SOL SÜTUN - Manuel veriler
        man_row = 0
        ttk.Label(manuel_frame, text="Talep Eden Kurum:", font=('Arial', 9, 'bold')).grid(row=man_row, column=0, sticky=tk.W, pady=3, padx=(5, 5))
        self.talep_kurum_entry = ttk.Entry(manuel_frame, width=entry_width)
        self.talep_kurum_entry.grid(row=man_row, column=1, pady=3, padx=5, sticky=(tk.W, tk.E))
        man_row += 1

        ttk.Label(manuel_frame, text="Talep Eden Şube:", font=('Arial', 9, 'bold')).grid(row=man_row, column=0, sticky=tk.W, pady=3, padx=(5, 5))
        self.talep_sube_entry = ttk.Entry(manuel_frame, width=entry_width)
        self.talep_sube_entry.grid(row=man_row, column=1, pady=3, padx=5, sticky=(tk.W, tk.E))
        man_row += 1

        ttk.Label(manuel_frame, text="Talep Tarihi:", font=('Arial', 9, 'bold')).grid(row=man_row, column=0, sticky=tk.W, pady=3, padx=(5, 5))
        self.talep_tarihi_entry = ttk.Entry(manuel_frame, width=entry_width)
        self.talep_tarihi_entry.grid(row=man_row, column=1, pady=3, padx=5, sticky=(tk.W, tk.E))
        man_row += 1

        ttk.Label(manuel_frame, text="Rapor No (Firma):", font=('Arial', 9, 'bold')).grid(row=man_row, column=0, sticky=tk.W, pady=3, padx=(5, 5))
        self.rapor_no_firma_entry = ttk.Entry(manuel_frame, width=entry_width)
        self.rapor_no_firma_entry.grid(row=man_row, column=1, pady=3, padx=5, sticky=(tk.W, tk.E))
        man_row += 1

        ttk.Label(manuel_frame, text="Rapor Ref No (Talep):", font=('Arial', 9, 'bold')).grid(row=man_row, column=0, sticky=tk.W, pady=3, padx=(5, 5))
        self.rapor_ref_no_entry = ttk.Entry(manuel_frame, width=entry_width)
        self.rapor_ref_no_entry.grid(row=man_row, column=1, pady=3, padx=5, sticky=(tk.W, tk.E))

        # SAĞ SÜTUN - Uzman bilgileri
        man_row = 0
        ttk.Label(manuel_frame, text="Değerleme Uzmanı:", font=('Arial', 9, 'bold')).grid(row=man_row, column=2, sticky=tk.W, pady=3, padx=(15, 5))
        self.degerleme_uzmani_entry = ttk.Entry(manuel_frame, width=entry_width)
        self.degerleme_uzmani_entry.grid(row=man_row, column=3, pady=3, padx=5, sticky=(tk.W, tk.E))
        man_row += 1

        ttk.Label(manuel_frame, text="Uzman Sicil No:", font=('Arial', 9, 'bold')).grid(row=man_row, column=2, sticky=tk.W, pady=3, padx=(15, 5))
        self.uzman_sicil_entry = ttk.Entry(manuel_frame, width=entry_width)
        self.uzman_sicil_entry.grid(row=man_row, column=3, pady=3, padx=5, sticky=(tk.W, tk.E))
        man_row += 1

        ttk.Label(manuel_frame, text="Kontrol Uzmanı:", font=('Arial', 9, 'bold')).grid(row=man_row, column=2, sticky=tk.W, pady=3, padx=(15, 5))
        self.kontrol_uzmani_entry = ttk.Entry(manuel_frame, width=entry_width)
        self.kontrol_uzmani_entry.grid(row=man_row, column=3, pady=3, padx=5, sticky=(tk.W, tk.E))
        man_row += 1

        ttk.Label(manuel_frame, text="Kontrol Uzmanı Sicil:", font=('Arial', 9, 'bold')).grid(row=man_row, column=2, sticky=tk.W, pady=3, padx=(15, 5))
        self.kontrol_sicil_entry = ttk.Entry(manuel_frame, width=entry_width)
        self.kontrol_sicil_entry.grid(row=man_row, column=3, pady=3, padx=5, sticky=(tk.W, tk.E))
        man_row += 1

        ttk.Label(manuel_frame, text="Bağımsız Bölüm No:", font=('Arial', 9, 'bold')).grid(row=man_row, column=2, sticky=tk.W, pady=3, padx=(15, 5))
        self.bagimsiz_bolum_entry = ttk.Entry(manuel_frame, width=entry_width)
        self.bagimsiz_bolum_entry.insert(0, "10")  # Default değer
        self.bagimsiz_bolum_entry.grid(row=man_row, column=3, pady=3, padx=5, sticky=(tk.W, tk.E))

        # Dosya Listesi
        liste_frame = ttk.LabelFrame(main_frame, text="Yüklenen Dosyalar", padding="10")
        liste_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)

        # Treeview ile sınıflandırılmış dosyalar
        columns = ('Dosya Adı', 'Tür', 'Durum')
        self.dosya_tree = ttk.Treeview(liste_frame, columns=columns, show='headings', height=8)

        self.dosya_tree.heading('Dosya Adı', text='Dosya Adı')
        self.dosya_tree.heading('Tür', text='Belge Türü')
        self.dosya_tree.heading('Durum', text='Durum')

        self.dosya_tree.column('Dosya Adı', width=300)
        self.dosya_tree.column('Tür', width=200)
        self.dosya_tree.column('Durum', width=150)

        self.dosya_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # Scrollbar
        scrollbar = ttk.Scrollbar(liste_frame, orient=tk.VERTICAL, command=self.dosya_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.dosya_tree.configure(yscrollcommand=scrollbar.set)

        # İşlem Butonları
        islem_frame = ttk.Frame(main_frame)
        islem_frame.grid(row=5, column=0, columnspan=2, pady=20)

        ttk.Button(islem_frame, text="Dosyaları Sınıflandır ve Analiz Et (AI)",
                   command=self.dosyalari_siniflandir, width=35).grid(row=0, column=0, padx=10)
        ttk.Button(islem_frame, text="Rapor Oluştur",
                   command=self.rapor_olustur, width=20).grid(row=0, column=1, padx=10)

        # Durum çubuğu
        self.durum_label = ttk.Label(main_frame, text="Hazır", relief=tk.SUNKEN)
        self.durum_label.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

    def dosya_ekle(self):
        """Tüm dosyaları (belge + fotoğraf) tek bir yerden yükle"""
        dosyalar = filedialog.askopenfilenames(
            title="Dosya Seç (Belge/Fotoğraf)",
            filetypes=[
                ("Desteklenen Dosyalar", "*.pdf *.jpg *.jpeg *.png *.tif *.tiff"),
                ("PDF Dosyaları", "*.pdf"),
                ("Resim Dosyaları", "*.jpg *.jpeg *.png *.tif *.tiff"),
                ("Tüm Dosyalar", "*.*")
            ]
        )

        for dosya in dosyalar:
            dosya_info = {
                "yol": dosya,
                "isim": Path(dosya).name,
                "tip": "Bilinmiyor",  # AI belirleyecek
                "durum": "Sınıflandırılmamış"
            }
            self.tum_dosyalar.append(dosya_info)

            # Listeye ekle
            self.dosya_tree.insert('', 'end', values=(
                Path(dosya).name,
                "Bilinmiyor",
                "Sınıflandırılmamış"
            ))

        self.durum_label.config(text=f"{len(dosyalar)} dosya eklendi. Lütfen 'Sınıflandır ve Analiz Et' butonuna tıklayın.")

    def emsal_ekle(self):
        """Emsal dosyalarını yükle (satış ilanları, benzer gayrimenkul fotoğrafları)"""
        dosyalar = filedialog.askopenfilenames(
            title="Emsal Dosyaları Seç",
            filetypes=[
                ("Resim Dosyaları", "*.jpg *.jpeg *.png"),
                ("Tüm Dosyalar", "*.*")
            ]
        )

        for dosya in dosyalar:
            self.emsal_dosyalar.append(dosya)
            # Listeye emsal olarak ekle
            self.dosya_tree.insert('', 'end', values=(
                Path(dosya).name,
                "Emsal",
                "Analiz Bekliyor"
            ))

        self.durum_label.config(text=f"{len(dosyalar)} emsal dosyası eklendi.")

    def dosyalari_siniflandir(self):
        """AI ile dosyaları sınıflandır ve analiz et"""
        if not self.tum_dosyalar:
            messagebox.showwarning("Uyarı", "Lütfen önce dosya yükleyin!")
            return

        self.durum_label.config(text="Dosyalar AI ile sınıflandırılıyor ve analiz ediliyor...")
        self.root.update()

        from ai_processor import AIBelgeIsleyici

        try:
            isleyici = AIBelgeIsleyici()

            # Treeview'i temizle
            for item in self.dosya_tree.get_children():
                self.dosya_tree.delete(item)

            # Her dosyayı sınıflandır
            for idx, dosya in enumerate(self.tum_dosyalar):
                self.durum_label.config(text=f"Dosya {idx+1}/{len(self.tum_dosyalar)} işleniyor: {dosya['isim']}")
                self.root.update()

                try:
                    # AI ile dosya türünü belirle
                    dosya_turu = isleyici.dosya_turu_belirle(dosya['yol'])
                    dosya['tip'] = dosya_turu

                    # Hata mesajı içeriyorsa durumu güncelle
                    if "çok büyük" in dosya_turu.lower() or "sınıflandırılamadı" in dosya_turu.lower():
                        dosya['durum'] = "Hata"
                    else:
                        dosya['durum'] = "Sınıflandırıldı"

                    # Treeview'e ekle
                    self.dosya_tree.insert('', 'end', values=(
                        dosya['isim'],
                        dosya_turu,
                        dosya['durum']
                    ))

                except Exception as e:
                    dosya['tip'] = f"Hata: {str(e)[:30]}"
                    dosya['durum'] = "Hata"
                    self.dosya_tree.insert('', 'end', values=(
                        dosya['isim'],
                        dosya['tip'],
                        "Hata"
                    ))

            # Belgeleri analiz et ve form doldur
            self.durum_label.config(text="Belgelerden veri çıkarılıyor...")
            self.root.update()

            belgeler = [d for d in self.tum_dosyalar if d['tip'] not in ['Fotoğraf', 'Bilinmiyor', 'Emsal']]

            if belgeler:
                sonuclar = isleyici.belgeleri_isle(belgeler)

                # Analiz sonuçlarını tüm label'lara doldur
                self.adres_label.config(text=sonuclar.get("adres", "-"))
                self.il_label.config(text=sonuclar.get("il", "-"))
                self.ilce_label.config(text=sonuclar.get("ilce", "-"))
                self.mahalle_label.config(text=sonuclar.get("mahalle", "-"))
                self.ada_label.config(text=sonuclar.get("ada", "-"))
                self.parsel_label.config(text=sonuclar.get("parsel", "-"))
                self.tapu_turu_label.config(text=sonuclar.get("tapu_turu", "-"))
                self.malik_label.config(text=sonuclar.get("malik", "-"))
                self.arsa_alani_label.config(text=sonuclar.get("arsa_alani", "-"))
                self.brut_alan_label.config(text=sonuclar.get("brut_alan", "-"))
                self.net_alan_label.config(text=sonuclar.get("net_alan", "-"))
                self.oda_sayisi_label.config(text=sonuclar.get("oda_sayisi", "-"))
                self.kat_sayisi_label.config(text=sonuclar.get("kat_sayisi", "-"))
                self.bina_yasi_label.config(text=sonuclar.get("bina_yasi", "-"))
                self.imar_durumu_label.config(text=sonuclar.get("imar_durumu", "-"))
                self.kullanim_amaci_label.config(text=sonuclar.get("kullanim_amaci", "-"))

                # Sonuçları sakla (rapor için)
                self.analiz_sonuclari = sonuclar

            # Emsalleri analiz et
            if self.emsal_dosyalar:
                self.durum_label.config(text="Emsaller analiz ediliyor...")
                self.root.update()
                
                from emsal_processor import EmsalIsleyici
                emsal_isleyici = EmsalIsleyici()
                
                self.emsal_degerleme = emsal_isleyici.emsalleri_toplu_isle(
                    self.emsal_dosyalar,
                    self.analiz_sonuclari
                )
                
                # Emsal tree'sini güncelle
                for item in self.dosya_tree.get_children():
                    values = self.dosya_tree.item(item)['values']
                    if values[1] == 'Emsal':
                        self.dosya_tree.item(item, values=(values[0], 'Emsal', 'Analiz Edildi'))

            # Hatalı dosya sayısını kontrol et
            hatali_dosyalar = [d for d in self.tum_dosyalar if d['durum'] == 'Hata']

            if hatali_dosyalar:
                self.durum_label.config(text=f"Tamamlandı - {len(hatali_dosyalar)} dosyada hata var")
                messagebox.showwarning(
                    "Kısmen Başarılı",
                    f"{len(self.tum_dosyalar) - len(hatali_dosyalar)} dosya başarıyla işlendi.\n\n"
                    f"{len(hatali_dosyalar)} dosyada hata oluştu (muhtemelen dosya boyutu çok büyük).\n\n"
                    "İpucu: Büyük dosyaları küçültmeyi deneyin veya farklı format kullanın."
                )
            else:
                self.durum_label.config(text="Sınıflandırma ve analiz tamamlandı!")
                messagebox.showinfo("Başarılı", f"{len(self.tum_dosyalar)} dosya başarıyla sınıflandırıldı ve analiz edildi!")

        except Exception as e:
            self.durum_label.config(text=f"Hata: {str(e)}")
            messagebox.showerror("Hata", f"Sınıflandırma sırasında hata oluştu:\n{str(e)}")

    def _alan_degerini_cikar(self, alan_str):
        """Alan değerini string'den regex ile çıkar ve sayıya çevirir"""
        import re
        if not alan_str or alan_str == '-':
            return None
        # Sayı pattern: virgül veya nokta ile ayrılmış sayılar (ör: "140 m²", "140,5", "140.5 m2")
        pattern = r'(\d+[.,]?\d*)'
        match = re.search(pattern, str(alan_str))
        if match:
            deger = match.group(1).replace(',', '.')
            try:
                return float(deger)
            except:
                return None
        return None

    def _hazirla_emsal_ozeti(self, veri):
        """Emsal değerleme bilgilerini özet olarak hazırlar"""
        ozet = {
            'emsal_sayisi': 0,
            'min_fiyat': None,
            'max_fiyat': None,
            'ortalama_fiyat': None,
            'emsal_listesi': []
        }

        emsal_degerleme = veri.get('emsal_degerleme', {})
        if emsal_degerleme and isinstance(emsal_degerleme, dict):
            emsaller = emsal_degerleme.get('emsaller', [])
            if emsaller:
                ozet['emsal_sayisi'] = len(emsaller)

                # Fiyat bilgilerini topla
                fiyatlar = []
                for emsal in emsaller:
                    if 'birim_fiyat' in emsal and emsal['birim_fiyat']:
                        fiyatlar.append(emsal['birim_fiyat'])
                    ozet['emsal_listesi'].append(emsal)

                if fiyatlar:
                    ozet['min_fiyat'] = min(fiyatlar)
                    ozet['max_fiyat'] = max(fiyatlar)
                    ozet['ortalama_fiyat'] = sum(fiyatlar) / len(fiyatlar)

        return ozet

    def rapor_olustur(self):
        if not self.tum_dosyalar:
            messagebox.showwarning("Uyarı", "Lütfen dosya yükleyin!")
            return

        self.durum_label.config(text="Rapor oluşturuluyor...")
        self.root.update()

        from area_report_generator import AREARaporOlusturucu
        from takbis_processor import TAKBISIsleyici

        try:
            # Belgeleri ve fotoğrafları ayır
            belgeler = [d for d in self.tum_dosyalar if d['tip'] not in ['Fotoğraf', 'Bilinmiyor']]
            fotograflar = [d['yol'] for d in self.tum_dosyalar if d['tip'] == 'Fotoğraf']

            # TAKBIS belgelerini işle
            takbis_verisi = None
            takbis_belgeleri = [d['yol'] for d in self.tum_dosyalar if 'takbis' in d['tip'].lower() or 'tapu' in d['tip'].lower()]

            if takbis_belgeleri:
                self.durum_label.config(text="TAKBIS belgeleri işleniyor...")
                self.root.update()

                takbis_isleyici = TAKBISIsleyici()
                if len(takbis_belgeleri) > 1:
                    takbis_verisi = takbis_isleyici.coklu_sayfa_takbis_isle(takbis_belgeleri)
                else:
                    takbis_verisi = takbis_isleyici.takbis_isle(takbis_belgeleri[0])

                print("✅ TAKBIS verileri çıkarıldı")

            # AI'dan alınan tüm verileri rapor için hazırla
            rapor_verisi = self.analiz_sonuclari.copy()

            # Alan değerlerini sayıya çevir
            rapor_verisi['net_alan_rakam'] = self._alan_degerini_cikar(rapor_verisi.get('net_alan'))
            rapor_verisi['brut_alan_rakam'] = self._alan_degerini_cikar(rapor_verisi.get('brut_alan'))
            rapor_verisi['arsa_alani_rakam'] = self._alan_degerini_cikar(rapor_verisi.get('arsa_alani'))

            rapor_verisi['fotograflar'] = fotograflar
            rapor_verisi['belgeler'] = belgeler
            rapor_verisi['tum_dosyalar'] = self.tum_dosyalar
            rapor_verisi['emsal_dosyalar'] = self.emsal_dosyalar
            rapor_verisi['emsal_degerleme'] = self.emsal_degerleme

            # Emsal özetini hazırla
            rapor_verisi['_emsal_ozeti'] = self._hazirla_emsal_ozeti(rapor_verisi)

            # Manuel girilen verileri ekle
            rapor_verisi['talep_eden_kurum'] = self.talep_kurum_entry.get() or None
            rapor_verisi['talep_eden_sube'] = self.talep_sube_entry.get() or None
            rapor_verisi['talep_tarihi'] = self.talep_tarihi_entry.get() or None
            rapor_verisi['rapor_no_firma'] = self.rapor_no_firma_entry.get() or None
            rapor_verisi['rapor_no_talep'] = self.rapor_ref_no_entry.get() or None
            rapor_verisi['degerleme_uzmani'] = self.degerleme_uzmani_entry.get() or None
            rapor_verisi['uzman_sicil_no'] = self.uzman_sicil_entry.get() or None
            rapor_verisi['kontrol_uzmani'] = self.kontrol_uzmani_entry.get() or None
            rapor_verisi['kontrol_uzmani_sicil'] = self.kontrol_sicil_entry.get() or None
            rapor_verisi['bagimsiz_bolum_no'] = self.bagimsiz_bolum_entry.get() or '10'

            # AREA formatında rapor oluştur
            self.durum_label.config(text="AREA formatında rapor oluşturuluyor...")
            self.root.update()

            olusturucu = AREARaporOlusturucu()
            rapor_dosyasi = olusturucu.rapor_olustur(rapor_verisi, takbis_verisi)

            self.durum_label.config(text=f"Rapor oluşturuldu: {rapor_dosyasi}")
            messagebox.showinfo("Başarılı", f"AREA formatında rapor başarıyla oluşturuldu:\n{rapor_dosyasi}")

        except Exception as e:
            self.durum_label.config(text=f"Hata: {str(e)}")
            messagebox.showerror("Hata", f"Rapor oluşturma sırasında hata oluştu:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = GayrimenkulDegerlemeApp(root)
    root.mainloop()
