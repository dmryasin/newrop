import os
import re
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.utils import ImageReader



class SPKRaporOlusturucu:
    """SPK standartlarına tam uyumlu gayrimenkul değerleme raporu oluşturur."""


    def __init__(self) -> None:
        self.output_dir = Path(__file__).parent / "raporlar"
        self.output_dir.mkdir(exist_ok=True)

        self.font_name = "Helvetica"
        self.font_bold = "Helvetica-Bold"

        try:
            font_path = Path("C:/Windows/Fonts/arial.ttf")
            font_bold_path = Path("C:/Windows/Fonts/arialbd.ttf")

            if font_path.exists():
                pdfmetrics.registerFont(TTFont("Turkish", str(font_path)))
                self.font_name = "Turkish"

            if font_bold_path.exists():
                pdfmetrics.registerFont(TTFont("TurkishBold", str(font_bold_path)))
                self.font_bold = "TurkishBold"
        except Exception:
            pass


    def stil_olustur(self):
        styles = getSampleStyleSheet()

        return {
            "kapak_baslik": ParagraphStyle(
                "KapakBaslik",
                fontName=self.font_bold,
                fontSize=20,
                textColor=colors.HexColor("#1a1a1a"),
                spaceAfter=20,
                alignment=1,
                leading=26,
            ),
            "bolum_baslik": ParagraphStyle(
                "BolumBaslik",
                fontName=self.font_bold,
                fontSize=14,
                textColor=colors.HexColor("#0b3d91"),
                spaceAfter=12,
                spaceBefore=12,
                leading=18,
            ),
            "alt_baslik": ParagraphStyle(
                "AltBaslik",
                fontName=self.font_bold,
                fontSize=12,
                textColor=colors.HexColor("#333333"),
                spaceAfter=8,
                spaceBefore=8,
            ),
            "metin": ParagraphStyle(
                "Metin",
                fontName=self.font_name,
                fontSize=10,
                textColor=colors.black,
                leading=14,
                alignment=4,
                spaceAfter=6,
            ),
            "tablo_baslik": ParagraphStyle(
                "TabloBaslik",
                fontName=self.font_bold,
                fontSize=9,
                textColor=colors.white,
                alignment=1,
            ),
        }


    def tablo_olustur(self, baslik, satirlar, col_widths=None, extra_styles=None):
        """Standart tablo formatı oluşturur ve aynı sayfada kalmasını sağlar."""
        # Satırlardaki uzun metinleri Paragraph ile sar (text wrapping için)
        veri = [[Paragraph(baslik, self.stil_olustur()["tablo_baslik"]), ""]]

        for satir in satirlar:
            wrapped_satir = []
            for idx, hucre in enumerate(satir):
                # Uzun metinleri Paragraph ile sar
                if isinstance(hucre, str) and len(hucre) > 40:
                    # Metin stilini kullan
                    p = Paragraph(hucre, self.stil_olustur()["metin"])
                    wrapped_satir.append(p)
                else:
                    wrapped_satir.append(hucre)
            veri.append(wrapped_satir)

        col_widths = col_widths or [7 * cm, 9 * cm]
        tablo = Table(veri, colWidths=col_widths)

        style = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b3d91")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), self.font_bold),
            ("FONTSIZE", (0, 0), (-1, 0), 11),
            ("SPAN", (0, 0), (-1, 0)),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 14),
            ("TOPPADDING", (0, 0), (-1, 0), 14),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),  # MIDDLE yerine TOP - text wrapping için daha iyi
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ]

        if len(veri) > 1:
            style.extend([
                ("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#f0f0f0")),
                ("FONTNAME", (0, 1), (0, -1), self.font_bold),
                ("FONTNAME", (1, 1), (-1, -1), self.font_name),
                ("FONTSIZE", (0, 1), (-1, -1), 10),
                ("ALIGN", (0, 1), (0, -1), "LEFT"),
                ("ALIGN", (1, 1), (-1, -1), "LEFT"),
                ("TOPPADDING", (0, 1), (-1, -1), 8),  # Biraz artırdık text wrapping için
                ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#c2c2c2")),
                ("BOX", (0, 0), (-1, -1), 1.2, colors.HexColor("#0b3d91")),
            ])

        if extra_styles:
            style.extend(extra_styles)

        tablo.setStyle(TableStyle(style))
        return KeepTogether([tablo])


    @staticmethod
    def _temiz_ifade(value, default="-"):
        if value is None:
            return default
        text = str(value).strip()
        return text if text else default

    @staticmethod
    def _safe_float(value):
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)

        text = str(value).strip()
        if not text:
            return None

        temiz = re.sub(r"[^0-9,.-]", "", text)
        if temiz.count(",") > 1 and "." not in temiz:
            temiz = temiz.replace(",", "")
        if temiz.count(".") > 1 and "," not in temiz:
            temiz = temiz.replace(".", "")

        if "," in temiz and "." in temiz:
            if temiz.rfind(",") > temiz.rfind("."):
                temiz = temiz.replace(".", "")
                temiz = temiz.replace(",", ".")
            else:
                temiz = temiz.replace(",", "")
        else:
            temiz = temiz.replace(",", ".")

        try:
            return float(temiz)
        except ValueError:
            return None

    def _format_tl(self, value, decimals=0, suffix=" TL"):
        sayi = self._safe_float(value)
        if sayi is None:
            return "-"
        formatted = f"{sayi:,.{decimals}f}"
        formatted = formatted.replace(",", "_").replace(".", ",").replace("_", ".")
        return formatted + suffix

    def _format_m2(self, value, decimals=2):
        sayi = self._safe_float(value)
        if sayi is None:
            return "-"
        formatted = f"{sayi:,.{decimals}f}"
        formatted = formatted.replace(",", "_").replace(".", ",").replace("_", ".")
        return f"{formatted} m2"

    def _format_percent(self, value, decimals=1):
        sayi = self._safe_float(value)
        if sayi is None:
            return "-"
        formatted = f"{sayi:.{decimals}f}"
        formatted = formatted.replace(".", ",")
        return f"%{formatted}"


    def _icindekiler_basliklari(self):
        return [
            "1. DEĞERLEMEYE İLİŞKİN BİLGİLER",
            "2. GAYRİMENKULE İLİŞKİN BİLGİLER",
            "3. GAYRİMENKULUN TAPU BİLGİLERİ",
            "4. YASAL KISITLAMALAR (Şerh, Rehin, Beyan, İpotek, Haciz ve Diğer Haklar)",
            "5. RUHSAT, MİMARİ PROJE VE YASAL İZİNLER",
            "6. DEĞERLENDİRİLEN BAĞIMSIZ BÖLÜMÜN BULUNDUĞU ANA GAYRİMENKULUN ÖZELLİKLERİ",
            "7. DEĞERLENDİRİLEN BAĞIMSIZ BÖLÜMÜN ÖZELLİKLERİ",
            "8. GAYRİMENKULUN DEĞERİNE ETKİ EDEN FAKTÖRLER",
            "9. EKSPERİN SATIŞA İLİŞKİN KANAATİ",
            "10. ANALİZLER VE SONUÇLARIN DEĞERLENDİRİLMESİ İLE HESAPLAMALAR",
            "11. DEĞERLEME",
            "12. ONAY BÖLÜMÜ",
            "13. DEĞERLEMEDE DİKKATE ALINAN EMSALLER, ÖZELLİKLER VE AÇIKLAMALAR",
            "14. RAPORUN DAĞITIMI / YAYINLANMASI YASAĞI",
            "15. DEĞERLEMEYI YAPAN PERSONEL BİLGİLERİ",
            "16. FİRMA TARAFINDAN AYNI GAYRİMENKULE İLİŞKİN DAHA ÖNCE DÜZENLENEN RAPOR BİLGİLERİ",
        ]







    def _fotograf_hucresi(self, yol, indeks, stiller, max_genislik, max_yukseklik):
        try:
            reader = ImageReader(yol)
            genislik, yukseklik = reader.getSize()
            genislik = float(genislik)
            yukseklik = float(yukseklik)
            if genislik <= 0 or yukseklik <= 0:
                raise ValueError("gecerli olmayan boyut")

            # Boyutları cm cinsinden sınırla (pixel değil)
            max_gen_pt = max_genislik
            max_yuk_pt = max_yukseklik

            olcek = min(max_gen_pt / genislik, max_yuk_pt / yukseklik)
            # Ölçeği 1.0'dan küçük tut
            if olcek > 1.0:
                olcek = 1.0

            hedef_genislik = genislik * olcek
            hedef_yukseklik = yukseklik * olcek

            # Güvenlik kontrolü - maksimum boyutları aşmayalım
            if hedef_genislik > max_gen_pt:
                hedef_genislik = max_gen_pt
            if hedef_yukseklik > max_yuk_pt:
                hedef_yukseklik = max_yuk_pt

            img = Image(yol, width=hedef_genislik, height=hedef_yukseklik)

            # KeepTogether yerine direkt liste döndür - tablo içinde sorun çıkarıyor
            return [
                img,
                Spacer(1, 0.15 * cm),
                Paragraph(f"<para align='center'><b>Fotoğraf {indeks}</b></para>", stiller["metin"]),
            ]
        except Exception as exc:
            return [Paragraph(
                f"<para align='center'>Fotoğraf {indeks} gösterilemedi ({exc})</para>",
                stiller["metin"],
            )]
    
    def _deger_faktorleri(self, veri, emsaller):
        faktorler = []

        lokasyon = ", ".join([
            parca
            for parca in [
                self._temiz_ifade(veri.get("mahalle"), ""),
                self._temiz_ifade(veri.get("ilce"), ""),
                self._temiz_ifade(veri.get("il"), ""),
            ]
            if parca
        ])
        if lokasyon:
            faktorler.append(
                f"Lokasyon: {lokasyon} adresinde yer alması, bölgesel erişim ve arz-talep seviyesini doğrudan etkilemektedir."
            )

        nitelik = self._temiz_ifade(veri.get("nitelik"), "Gayrimenkul")
        kullanim = self._temiz_ifade(veri.get("kullanim_amaci"), "mevcut kullanım")
        faktorler.append(
            f"Nitelik: Taşınmaz {nitelik.lower()} niteliğinde olup {kullanim.lower()} kapsamında değerlendirilmektedir."
        )

        alan_text = self._format_m2(veri.get("net_alan") or veri.get("brut_alan"))
        if alan_text != "-":
            faktorler.append(
                f"Alan: Bağımsız bölümün faydalı alanı {alan_text} ve değer hesaplamalarında temel girdidir."
            )

        if veri.get("yapilanma_kosullari"):
            faktorler.append(
                f"İmar Durumu: İlgili imar planında tanımlanan '{self._temiz_ifade(veri.get('yapilanma_kosullari'))}' koşulları yapılaşmanın hak ve sınırlarını belirlemektedir."
            )

        if veri.get("enerji_sinifi"):
            faktorler.append(
                f"Enerji Performansı: Enerji kimlik belgesine göre sınıf {self._temiz_ifade(veri.get('enerji_sinifi'))} olup işletme giderleri üzerinde etkili olacaktır."
            )

        gecerli_emsal_sayisi = len([e for e in emsaller if not e.get("hata")])
        if gecerli_emsal_sayisi:
            faktorler.append(
                f"Piyasa Verisi: Analiz, {gecerli_emsal_sayisi} adet güncel emsal üzerinden gerçekleştirilmiştir; fiyat aralığı bölgedeki değer trendini yansıtmaktadır."
            )

        if not faktorler:
            faktorler.append(
                "Raporlama için yeterli veri sağlanamadığından değer faktörleri genel piyasa kabulleri ile sınırlıdır."
            )

        return faktorler

    def _uzman_kanaati_metni(self, veri, degerleme, emsaller, rapor_tarihi):
        cumleler = []

        lokasyon_parcalari = [
            self._temiz_ifade(veri.get("mahalle"), ""),
            self._temiz_ifade(veri.get("sokak"), ""),
            self._temiz_ifade(veri.get("ilce"), ""),
            self._temiz_ifade(veri.get("il"), ""),
        ]
        lokasyon = ", ".join([parca for parca in lokasyon_parcalari if parca])

        nitelik = self._temiz_ifade(veri.get("nitelik"), "gayrimenkul")
        cumleler.append(
            f"Rapor {rapor_tarihi} tarihinde tamamlanmış olup incelemeye konu {nitelik.lower()} {lokasyon if lokasyon else 'belirtilen adreste'} konumlanmaktadır."
        )

        kullanim = self._temiz_ifade(veri.get("kullanim_amaci"), "mevcut kullanım")
        cumleler.append(f"Taşınmazın hâlihazırdaki kullanım şekli '{kullanim}' olarak teyit edilmiştir.")

        alan = self._format_m2(veri.get("net_alan") or veri.get("brut_alan"))
        if alan != "-":
            cumleler.append(f"Bağımsız bölümün faydalı alanı {alan} olup değerlemede bu metraj esas alınmıştır.")

        gecerli_emsaller = [e for e in emsaller if not e.get("hata")]
        if gecerli_emsaller:
            ort_birim = degerleme.get("ortalama_birim_fiyat") if degerleme else None
            if ort_birim:
                cumleler.append(
                    f"Piyasa araştırmasında kullanılan {len(gecerli_emsaller)} adet emsalin ortalama birim değeri {self._format_tl(ort_birim, 2, ' TL/m2')} seviyesindedir."
                )

        tahmini_deger = degerleme.get("tahmini_deger") if degerleme else None
        if tahmini_deger:
            cumleler.append(
                f"Analiz sonucunda taşınmazın piyasa değeri {self._format_tl(tahmini_deger, 0)} olarak takdir edilmiştir."
            )

        cumleler.append(
            "Değerleme çalışması Sermaye Piyasası Kurulu düzenlemeleri, Uluslararası Değerleme Standartları ve mesleki etik kurallar çerçevesinde yürütülmüştür."
        )

        return " ".join(cumleler)

    def rapor_olustur(self, veri: dict) -> str:
        """SPK standartlarına uygun tam kapsamlı değerleme raporu oluştur."""
        simdi = datetime.now()
        dosya_adi = f"SPK_Degerleme_Raporu_{simdi.strftime('%Y%m%d_%H%M%S')}.pdf"
        dosya_yolu = self.output_dir / dosya_adi

        doc = SimpleDocTemplate(
            str(dosya_yolu),
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        stiller = self.stil_olustur()
        rapor_tarihi = simdi.strftime("%d.%m.%Y")

        emsal_verisi = veri.get("emsal_degerleme") or {}
        degerleme_sonucu = emsal_verisi.get("degerleme_sonucu") or {}
        emsaller = emsal_verisi.get("emsal_analizleri") or []

        story = []

        def paragraf(text, style_key="metin", space_cm=0.4):
            if not text:
                return
            story.append(Paragraph(text, stiller[style_key]))
            if space_cm:
                story.append(Spacer(1, space_cm * cm))

        def tablo_ekle(baslik, satirlar, col_widths=None, extra_styles=None, space_cm=0.6):
            if not satirlar:
                return
            tablo_flow = self.tablo_olustur(baslik, satirlar, col_widths=col_widths, extra_styles=extra_styles)
            story.append(tablo_flow)
            if space_cm:
                story.append(Spacer(1, space_cm * cm))

        # Kapak
        story.append(Spacer(1, 4 * cm))
        story.append(Paragraph("GAYRİMENKUL DEĞERLEME RAPORU", stiller["kapak_baslik"]))
        story.append(Spacer(1, 0.8 * cm))
        story.append(Paragraph("Sermaye Piyasası Kurulu (SPK) Standartlarına Uygun Raporlama", stiller["metin"]))
        story.append(Spacer(1, 2.2 * cm))

        kapak_satirlar = [
            ["Talep Eden Kurum:", self._temiz_ifade(veri.get("talep_eden_kurum") or veri.get("talep_eden_birim"))],
            ["Talep Eden Şube/Birim:", self._temiz_ifade(veri.get("talep_eden_sube") or veri.get("talep_eden_kisi"))],
            ["Rapor Tarihi:", rapor_tarihi],
            [
                "Gayrimenkul:",
                self._temiz_ifade(
                    veri.get("adres")
                    or ", ".join(
                        parca
                        for parca in [
                            veri.get("mahalle"),
                            veri.get("sokak"),
                            veri.get("ilce"),
                            veri.get("il"),
                        ]
                        if parca
                    )
                    or veri.get("kullanim_amaci")
                ),
            ],
        ]
        tablo_ekle("KAPAK BİLGİLERİ", kapak_satirlar, space_cm=0)
        story.append(PageBreak())

        # İçindekiler
        story.append(Paragraph("İÇİNDEKİLER", stiller["bolum_baslik"]))
        story.append(Spacer(1, 0.4 * cm))
        for madde in self._icindekiler_basliklari():
            story.append(Paragraph(madde, stiller["metin"]))
        story.append(PageBreak())

        # 1. Değerlemeye ilişkin bilgiler
        story.append(Paragraph("1. DEĞERLEMEYE İLİŞKİN BİLGİLER", stiller["bolum_baslik"]))
        bolum1_satirlar = [
            ["Talep Tarihi:", self._temiz_ifade(veri.get("talep_tarihi"))],
            ["Talep Eden Kurum:", self._temiz_ifade(veri.get("talep_eden_kurum") or veri.get("talep_eden_birim"))],
            ["Talep Eden Müşteri/Şube:", self._temiz_ifade(veri.get("talep_eden_sube") or veri.get("talep_eden_kisi"))],
            ["Rapor No (Firma):", self._temiz_ifade(veri.get("rapor_no_firma"))],
            ["Rapor Referans No (Talep Eden):", self._temiz_ifade(veri.get("rapor_no_talep"))],
            ["Değerleme Tarihi:", self._temiz_ifade(veri.get("degerleme_tarihi") or rapor_tarihi)],
            ["Ekspertiz Tarihi:", self._temiz_ifade(veri.get("ekspertiz_tarihi") or rapor_tarihi)],
            ["Değerleme Türü:", self._temiz_ifade(veri.get("degerleme_turu") or "Satış ve Kira")],
            ["Değerleme Uzmanı:", self._temiz_ifade(veri.get("degerleme_uzmani"))],
            ["Uzman Sicil No:", self._temiz_ifade(veri.get("uzman_sicil_no"))],
            ["Kontrol Uzmanı:", self._temiz_ifade(veri.get("kontrol_uzmani"))],
            ["Kontrol Uzmanı Sicil No:", self._temiz_ifade(veri.get("kontrol_uzmani_sicil"))],
            ["Değerleme Şirketi:", self._temiz_ifade(veri.get("degerleme_sirketi") or "A.R.E.A. Gayrimenkul Değerleme ve Danışmanlık A.Ş.")],
        ]
        tablo_ekle("DEĞERLEMEYE İLİŞKİN TEMEL VERİLER", bolum1_satirlar)
        paragraf(
            "Bu bölümde raporun talep eden kurum, dayanak tarihleri ve değerleme sürecinde görev alan uzmanlara ilişkin temel bilgiler sunulmaktadır.",
            space_cm=0.6,
        )

        # 2. Gayrimenkule ilişkin bilgiler
        story.append(Paragraph("2. GAYRİMENKULE İLİŞKİN BİLGİLER", stiller["bolum_baslik"]))
        konum_satirlar = [
            ["Tam Adres:", self._temiz_ifade(veri.get("adres"))],
            ["İl:", self._temiz_ifade(veri.get("il"))],
            ["İlçe:", self._temiz_ifade(veri.get("ilce"))],
            ["Mahalle/Köy:", self._temiz_ifade(veri.get("mahalle"))],
            ["Sokak/Cadde:", self._temiz_ifade(veri.get("sokak"))],
            ["Bina No:", self._temiz_ifade(veri.get("bina_no"))],
            ["Daire No:", self._temiz_ifade(veri.get("daire_no"))],
            ["Posta Kodu:", self._temiz_ifade(veri.get("posta_kodu"))],
            ["Mevcut Kullanım Durumu:", self._temiz_ifade(veri.get("kullanim_amaci"))],
        ]
        tablo_ekle("KONUM VE KULLANIM BİLGİLERİ", konum_satirlar)

        lokasyon_cumlesi = ", ".join(
            [
                parca
                for parca in [
                    self._temiz_ifade(veri.get("mahalle"), ""),
                    self._temiz_ifade(veri.get("sokak"), ""),
                    self._temiz_ifade(veri.get("ilce"), ""),
                    self._temiz_ifade(veri.get("il"), ""),
                ]
                if parca
            ]
        )
        paragraf(
            f"Taşınmaz {lokasyon_cumlesi if lokasyon_cumlesi else 'belirtilen adreste'} konumlu olup ulaşım ana arterlerden özel araç ile sağlanabilmektedir.",
            space_cm=0.6,
        )

        # 3. Tapu bilgileri
        story.append(Paragraph("3. GAYRİMENKULUN TAPU BİLGİLERİ", stiller["bolum_baslik"]))
        tapu_satirlar = [
            ["İl:", self._temiz_ifade(veri.get("il"))],
            ["İlçe:", self._temiz_ifade(veri.get("ilce"))],
            ["Mahalle/Köy:", self._temiz_ifade(veri.get("mahalle"))],
            ["Ada:", self._temiz_ifade(veri.get("ada"))],
            ["Parsel:", self._temiz_ifade(veri.get("parsel"))],
            ["Pafta:", self._temiz_ifade(veri.get("pafta"))],
            ["Nitelik:", self._temiz_ifade(veri.get("nitelik"))],
            ["Tapu Türü:", self._temiz_ifade(veri.get("tapu_turu"))],
            ["Arsa Payı:", self._temiz_ifade(veri.get("arsa_payi"))],
            ["Malik:", self._temiz_ifade(veri.get("malik"))],
            ["Hisse:", self._temiz_ifade(veri.get("hisse"))],
        ]
        tablo_ekle("TAPU SİCİL BİLGİLERİ", tapu_satirlar)

        # 4. Yasal kısıtlamalar
        story.append(Paragraph("4. YASAL KISITLAMALAR (Şerh, Rehin, Beyan, İpotek, Haciz ve Diğer Haklar)", stiller["bolum_baslik"]))
        yasal = veri.get("yasal_kisitlamalar")
        if isinstance(yasal, list):
            for madde in yasal:
                paragraf(f"- {self._temiz_ifade(madde)}", space_cm=0.3)
        elif yasal:
            paragraf(self._temiz_ifade(yasal))
        else:
            paragraf(
                "Tapu müdürlüğünden alınan güncel takyidat belgesi paylaşılmamış olup, rapor tarihinde kısıtlılık bilgisi doğrulanamamıştır. Talep eden kurumun tapu kayıtlarını ayrıca teyit etmesi önerilir."
            )

        # 5. Ruhsat ve yasal izinler
        story.append(Paragraph("5. RUHSAT, MİMARİ PROJE VE YASAL İZİNLER", stiller["bolum_baslik"]))
        ruhsat_satirlar = [
            ["İmar Durumu:", self._temiz_ifade(veri.get("imar_durumu"))],
            ["İmar Planı Mevcudiyeti:", self._temiz_ifade(veri.get("imar_plani_mevcudiyet"))],
            ["Yapılanma Koşulları:", self._temiz_ifade(veri.get("yapilanma_kosullari"))],
            ["Emsal (KAKS):", self._temiz_ifade(veri.get("kaks"))],
            ["TAKS:", self._temiz_ifade(veri.get("taks"))],
            ["Gabari / Yükseklik:", self._temiz_ifade(veri.get("gabari"))],
            ["Ruhsat Durumu:", self._temiz_ifade(veri.get("ruhsat_durumu"))],
        ]
        tablo_ekle("YASAL İZİN VE İMAR BİLGİLERİ", ruhsat_satirlar)

        # 6. Ana gayrimenkul özellikleri
        story.append(Paragraph("6. DEĞERLENDİRİLEN BAĞIMSIZ BÖLÜMÜN BULUNDUĞU ANA GAYRİMENKULUN ÖZELLİKLERİ", stiller["bolum_baslik"]))
        ana_satirlar = [
            ["Arsa Alanı:", self._temiz_ifade(veri.get("arsa_alani"))],
            ["İmar Parseli Alanı:", self._temiz_ifade(veri.get("imar_parseli_alani"))],
            ["Brüt İnşaat Alanı:", self._temiz_ifade(veri.get("brut_alan"))],
            ["Net Kullanım Alanı:", self._temiz_ifade(veri.get("net_alan"))],
            ["Toplam Kat Sayısı:", self._temiz_ifade(veri.get("kat_sayisi"))],
            ["Yapı Durumu:", self._temiz_ifade(veri.get("yapit_durumu"))],
            ["Bina Yaşı / İnşaat Yılı:", self._temiz_ifade(veri.get("bina_yasi"))],
        ]
        tablo_ekle("ANA GAYRİMENKUL BİLGİLERİ", ana_satirlar)

        # 7. Bağımsız bölüm özellikleri
        story.append(Paragraph("7. DEĞERLENDİRİLEN BAĞIMSIZ BÖLÜMÜN ÖZELLİKLERİ", stiller["bolum_baslik"]))
        bagimsiz_satirlar = [
            ["Bulunduğu Kat:", self._temiz_ifade(veri.get("bulundugu_kat"))],
            ["Oda Sayısı:", self._temiz_ifade(veri.get("oda_sayisi"))],
            ["Kullanım Amacı:", self._temiz_ifade(veri.get("kullanim_amaci"))],
            ["Cephe Yönü:", self._temiz_ifade(veri.get("cephe_yonu"))],
            ["Manzara:", self._temiz_ifade(veri.get("manzara"))],
            ["Isıtma Sistemi:", self._temiz_ifade(veri.get("isitma_tipi"))],
            ["Soğutma Sistemi:", self._temiz_ifade(veri.get("sogutma_tipi"))],
            ["Enerji Sınıfı:", self._temiz_ifade(veri.get("enerji_sinifi"))],
        ]
        tablo_ekle("BAĞIMSIZ BÖLÜM DETAYLARI", bagimsiz_satirlar)

        if veri.get("enerji_belgesi_mevcut") == "Evet":
            enerji_satirlar = [
                ["Enerji Tüketimi:", self._temiz_ifade(veri.get("enerji_tuketimi"))],
                ["CO2 Salımı:", self._temiz_ifade(veri.get("enerji_co2_salimi"))],
            ]
            tablo_ekle("ENERJİ KİMLİK BELGESİ", enerji_satirlar)

        # 8. Değere etki eden faktörler
        story.append(Paragraph("8. GAYRİMENKULUN DEĞERİNE ETKİ EDEN FAKTÖRLER", stiller["bolum_baslik"]))
        for faktor in self._deger_faktorleri(veri, emsaller):
            paragraf(f"- {faktor}", space_cm=0.3)

        # 9. Eksper kanaati
        story.append(Paragraph("9. EKSPERİN SATIŞA İLİŞKİN KANAATİ", stiller["bolum_baslik"]))
        paragraf(self._uzman_kanaati_metni(veri, degerleme_sonucu, emsaller, rapor_tarihi))

        # 10. Analiz ve hesaplamalar
        story.append(Paragraph("10. ANALİZLER VE SONUÇLARIN DEĞERLENDİRİLMESİ İLE HESAPLAMALAR", stiller["bolum_baslik"]))
        analiz_satirlar = [
            ["Analiz Tarihi:", rapor_tarihi],
            ["Kullanılan Emsal Sayısı:", str(len([e for e in emsaller if not e.get("hata")]))],
            ["Ortalama Birim Fiyat:", self._format_tl(degerleme_sonucu.get("ortalama_birim_fiyat"), 2, " TL/m2")],
            ["Minimum Birim Fiyat:", self._format_tl(degerleme_sonucu.get("min_birim_fiyat"), 2, " TL/m2")],
            ["Maksimum Birim Fiyat:", self._format_tl(degerleme_sonucu.get("max_birim_fiyat"), 2, " TL/m2")],
            ["Güven Seviyesi:", self._temiz_ifade(degerleme_sonucu.get("guven_seviyesi"), "Orta")],
        ]
        tablo_ekle("ANALİZ ÖZETİ", analiz_satirlar)

        # 11. Değerleme
        story.append(Paragraph("11. DEĞERLEME", stiller["bolum_baslik"]))
        deger_satirlar = [
            ["Gayrimenkul Alanı:", self._format_m2(veri.get("net_alan") or veri.get("brut_alan"), decimals=2)],
            ["Tahmini Piyasa Değeri:", self._format_tl(degerleme_sonucu.get("tahmini_deger"), 0)],
            ["Değer Aralığı (Min):", self._format_tl(degerleme_sonucu.get("deger_araligi_min"), 0)],
            ["Değer Aralığı (Max):", self._format_tl(degerleme_sonucu.get("deger_araligi_max"), 0)],
        ]
        tablo_ekle("DEĞERLEME SONUÇ TABLOSU", deger_satirlar)
        paragraf(
            "Not: Belirtilen değerler rapor tarihindeki piyasa koşullarına göre takdir edilmiş olup ekonomik değişimler karşısında revizyon gerektirebilir.",
            space_cm=0.6,
        )

        # 12. Onay bölümü
        story.append(Paragraph("12. ONAY BÖLÜMÜ", stiller["bolum_baslik"]))
        imza_tablo = Table(
            [
                ["Değerleme Uzmanı", "Kontrol"],
                ["", ""],
                [
                    f"Ad Soyad: {self._temiz_ifade(veri.get('degerleme_uzmani'), '__________________')}",
                    f"Ad Soyad: {self._temiz_ifade(veri.get('kontrol_uzmani'), '__________________')}",
                ],
                [
                    f"Lisans No: {self._temiz_ifade(veri.get('uzman_sicil_no'), '____________')}",
                    f"Ünvan: {self._temiz_ifade(veri.get('kontrol_uzmani_unvan'), '____________')}",
                ],
                ["İmza:", "İmza:"],
            ],
            colWidths=[8 * cm, 8 * cm],
        )
        imza_tablo.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), self.font_name),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 1), (-1, 1), 24),
                    ("BOTTOMPADDING", (0, 1), (-1, 1), 24),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#b0b0b0")),
                ]
            )
        )
        story.append(KeepTogether([imza_tablo]))
        story.append(Spacer(1, 0.8 * cm))

        # 13. Emsal bilgileri
        story.append(Paragraph("13. DEĞERLEMEDE DİKKATE ALINAN EMSALLER, ÖZELLİKLER VE AÇIKLAMALAR", stiller["bolum_baslik"]))
        gecerli_emsaller = [emsal for emsal in emsaller if not emsal.get("hata")]
        if gecerli_emsaller:
            emsal_tablo_data = [
                [
                    Paragraph("<b>No</b>", stiller["tablo_baslik"]),
                    Paragraph("<b>Adres</b>", stiller["tablo_baslik"]),
                    Paragraph("<b>Alan</b>", stiller["tablo_baslik"]),
                    Paragraph("<b>Fiyat</b>", stiller["tablo_baslik"]),
                    Paragraph("<b>Birim Fiyat</b>", stiller["tablo_baslik"]),
                    Paragraph("<b>Not</b>", stiller["tablo_baslik"]),
                ]
            ]

            for emsal in gecerli_emsaller:
                # Adres ve not alanlarını Paragraph ile sar (text wrapping için)
                adres_text = self._temiz_ifade(emsal.get("adres"))
                not_text = self._temiz_ifade(emsal.get("aciklama") or emsal.get("not"))

                emsal_tablo_data.append(
                    [
                        str(emsal.get("emsal_no") or len(emsal_tablo_data)),
                        Paragraph(adres_text, stiller["metin"]),  # Text wrapping
                        self._format_m2(emsal.get("alan_m2"), decimals=2),
                        self._format_tl(emsal.get("fiyat"), 0),
                        Paragraph(self._format_tl(emsal.get("birim_fiyat"), 2, " TL/m²"), stiller["metin"]),
                        Paragraph(not_text, stiller["metin"]),  # Text wrapping
                    ]
                )

            emsal_tablo = Table(
                emsal_tablo_data,
                colWidths=[1.2 * cm, 4.8 * cm, 2.2 * cm, 2.8 * cm, 2.8 * cm, 3.2 * cm],  # Kolon genişlikleri ayarlandı
            )
            emsal_tablo.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b3d91")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), self.font_bold),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),  # MIDDLE yerine TOP - text wrapping için
                        ("GRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#c2c2c2")),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f7f7")]),
                        ("LEFTPADDING", (0, 0), (-1, -1), 6),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, -1), 8),  # Padding artırıldı
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ]
                )
            )
            story.append(KeepTogether([emsal_tablo]))
            story.append(Spacer(1, 0.6 * cm))
        else:
            paragraf("Emsal verisi paylaşılmamış veya analizde kullanılabilecek nitelikte veri bulunmamaktadır.")

        # 14. Raporun dağıtımı / yayınlanması yasağı
        story.append(Paragraph("14. RAPORUN DAĞITIMI / YAYINLANMASI YASAĞI", stiller["bolum_baslik"]))
        paragraf(
            "Bu rapor yalnızca talep eden kurumun kullanımına sunulmuştur. Üçüncü kişilerle paylaşılması, çoğaltılması veya kamuya açıklanması değerleme şirketinin yazılı onayına tabidir."
        )

        # 15. Personel bilgileri
        story.append(Paragraph("15. DEĞERLEMEYI YAPAN PERSONEL BİLGİLERİ", stiller["bolum_baslik"]))
        personel_satirlar = [
            ["Değerleme Uzmanı:", self._temiz_ifade(veri.get("degerleme_uzmani"))],
            ["Uzman Sicil No:", self._temiz_ifade(veri.get("uzman_sicil_no"))],
            ["Kontrol Uzmanı:", self._temiz_ifade(veri.get("kontrol_uzmani"))],
            ["Kontrol Uzmanı Sicil No:", self._temiz_ifade(veri.get("kontrol_uzmani_sicil"))],
            ["Raporu Hazırlayan Ekip:", self._temiz_ifade(veri.get("hazirlayan_ekip"))],
        ]
        tablo_ekle("UZMAN KADRO BİLGİLERİ", personel_satirlar)

        # 16. Önceki rapor bilgileri
        story.append(Paragraph("16. FİRMA TARAFINDAN AYNI GAYRİMENKULE İLİŞKİN DAHA ÖNCE DÜZENLENEN RAPOR BİLGİLERİ", stiller["bolum_baslik"]))
        onceki = veri.get("onceki_rapor_bilgileri")
        if isinstance(onceki, list):
            for rapor in onceki:
                paragraf(f"- {self._temiz_ifade(rapor)}", space_cm=0.3)
        elif onceki:
            paragraf(self._temiz_ifade(onceki))
        else:
            paragraf("Şirketimiz tarafından aynı gayrimenkule ilişkin daha önce düzenlenen rapor bilgisi paylaşılmamıştır.")

        # Fotograflar
        fotograflar = []
        for foto_yolu in (veri.get("fotograflar") or []):
            if os.path.exists(foto_yolu):
                fotograflar.append(foto_yolu)


        if fotograflar:
            story.append(PageBreak())
            story.append(Paragraph("EKLER - GAYRİMENKUL FOTOĞRAFLARI", stiller["bolum_baslik"]))
            story.append(Spacer(1, 0.4 * cm))
        
            max_genislik = 8 * cm
            max_yukseklik = 5.5 * cm
            bos_hucre_yuksekligi = max_yukseklik + 0.3 * cm
        
            numarali = list(enumerate(fotograflar, start=1))
            foto_gruplari = [numarali[i : i + 4] for i in range(0, len(numarali), 4)]
        
            for grup_index, grup in enumerate(foto_gruplari):
                satirlar = [[], []]
                for local_idx in range(4):
                    if local_idx < len(grup):
                        idx, yol = grup[local_idx]
                        foto_elemanlari = self._fotograf_hucresi(yol, idx, stiller, max_genislik, max_yukseklik)
                        # Tablo hücresine direkt liste koyamayız, Flowable gerekir
                        # Boş Paragraph ekleyerek liste yerine tek eleman kullan
                        if isinstance(foto_elemanlari, list) and len(foto_elemanlari) > 0:
                            # İlk eleman image, diğerleri spacer ve text
                            # Hepsini birleştiren bir tablo oluştur
                            mini_tablo_data = [[elem] for elem in foto_elemanlari]
                            mini_tablo = Table(mini_tablo_data, colWidths=[max_genislik])
                            mini_tablo.setStyle(TableStyle([
                                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ]))
                            hucre = mini_tablo
                        else:
                            hucre = foto_elemanlari[0] if isinstance(foto_elemanlari, list) else foto_elemanlari
                    else:
                        hucre = Spacer(1, bos_hucre_yuksekligi)

                    hedef_satir = 0 if local_idx < 2 else 1
                    satirlar[hedef_satir].append(hucre)

                for satir in satirlar:
                    while len(satir) < 2:
                        satir.append(Spacer(1, bos_hucre_yuksekligi))

                foto_tablo = Table(satirlar, colWidths=[max_genislik, max_genislik])
                foto_tablo.setStyle(
                    TableStyle(
                        [
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#3a3a3a")),
                            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#8c8c8c")),
                            ("LEFTPADDING", (0, 0), (-1, -1), 6),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                            ("TOPPADDING", (0, 0), (-1, -1), 6),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                        ]
                    )
                )
                story.append(foto_tablo)

                if grup_index < len(foto_gruplari) - 1:
                    story.append(PageBreak())
        doc.build(story)
        return str(dosya_yolu)
