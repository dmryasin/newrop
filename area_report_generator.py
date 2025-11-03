# -*- coding: utf-8 -*-
"""
AREA Gayrimenkul Değerleme A.Ş. TAM KAPSAMLI Rapor Oluşturucu
Örnek rapordaki TÜM bölümleri eksiksiz içerir
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                 Table, TableStyle, PageBreak, KeepTogether, Frame, PageTemplate)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
from pathlib import Path
import os


class AREARaporOlusturucu:
    """AREA formatında TAM KAPSAMLI rapor oluşturan sınıf"""

    def __init__(self):
        self.output_dir = Path(__file__).parent / "raporlar"
        self.output_dir.mkdir(exist_ok=True)

        # Türkçe karakter desteği için font
        try:
            font_path = "C:/Windows/Fonts/arial.ttf"
            font_bold_path = "C:/Windows/Fonts/arialbd.ttf"

            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Arial', font_path))
                self.font_name = 'Arial'
            else:
                self.font_name = 'Helvetica'

            if os.path.exists(font_bold_path):
                pdfmetrics.registerFont(TTFont('Arial-Bold', font_bold_path))
                self.font_bold = 'Arial-Bold'
            else:
                self.font_bold = 'Helvetica-Bold'
        except:
            self.font_name = 'Helvetica'
            self.font_bold = 'Helvetica-Bold'

        # AREA renk teması
        self.mavi_renk = colors.HexColor('#2E5C8A')
        self.acik_mavi = colors.HexColor('#E8F1F8')
        self.gri_renk = colors.HexColor('#F0F0F0')

    def header_footer(self, canvas, doc):
        """Her sayfaya header ve footer ekle"""
        canvas.saveState()

        # HEADER - Üst kısım
        canvas.setFont(self.font_name, 8)
        canvas.setFillColor(colors.grey)
        header_text = "Bu belge 5070 sayılı Elektronik İmza Kanunu çerçevesinde e-imza ile imzalanmıştır."
        canvas.drawCentredString(A4[0] / 2, A4[1] - 1*cm, header_text)

        # AREA Logosu - sol üst (her sayfada)
        canvas.setFont(self.font_bold, 10)
        canvas.setFillColor(self.mavi_renk)
        canvas.drawString(2*cm, A4[1] - 1.5*cm, "AREA")
        canvas.setFont(self.font_name, 7)
        canvas.drawString(2*cm, A4[1] - 1.8*cm, "GAYRİMENKUL DEĞERLEME A.Ş.")

        # FOOTER - Sayfa numarası
        canvas.setFont(self.font_name, 9)
        canvas.setFillColor(colors.black)
        page_num = canvas.getPageNumber()
        canvas.drawCentredString(A4[0] / 2, 1.5*cm, str(page_num))

        # Alt kısım bilgi
        canvas.setFont(self.font_name, 8)
        canvas.setFillColor(colors.grey)
        canvas.drawCentredString(A4[0] / 2, 1*cm,
                                "AREA Gayrimenkul Değerleme ve Danışmanlık A.Ş.")

        canvas.restoreState()

    def stil_olustur(self):
        """Rapor için stil şablonları"""
        styles = {}

        # Ana başlık (kapak)
        styles['KapakBaslik'] = ParagraphStyle(
            'KapakBaslik',
            fontName=self.font_bold,
            fontSize=18,
            textColor=colors.black,
            alignment=TA_CENTER,
            spaceAfter=10,
            leading=22
        )

        # Bölüm başlıkları (1., 2., 3. vb.)
        styles['BolumBaslik'] = ParagraphStyle(
            'BolumBaslik',
            fontName=self.font_bold,
            fontSize=14,
            textColor=colors.black,
            spaceAfter=12,
            spaceBefore=12,
            leading=16
        )

        # Alt başlıklar (2.1, 2.2 vb.)
        styles['AltBaslik'] = ParagraphStyle(
            'AltBaslik',
            fontName=self.font_bold,
            fontSize=11,
            textColor=colors.black,
            spaceAfter=8,
            spaceBefore=8,
            leading=14
        )

        # Normal metin
        styles['Normal'] = ParagraphStyle(
            'Normal',
            fontName=self.font_name,
            fontSize=10,
            textColor=colors.black,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
            leading=14
        )

        # Küçük metin (tablo içi) - WORD WRAP için
        styles['TabloMetin'] = ParagraphStyle(
            'TabloMetin',
            fontName=self.font_name,
            fontSize=8,
            textColor=colors.black,
            leading=10,
            wordWrap='CJK'  # Word wrap etkinleştir
        )

        styles['TabloMetinBold'] = ParagraphStyle(
            'TabloMetinBold',
            fontName=self.font_bold,
            fontSize=8,
            textColor=colors.black,
            leading=10,
            wordWrap='CJK'
        )

        return styles

    def _p(self, text, stil):
        """Paragraph oluştur helper"""
        return Paragraph(text, stil)

    def _format_tl(self, tutar, yazili=False):
        """
        Tutarı TL formatında gösterir
        Args:
            tutar: Sayı (float veya int)
            yazili: True ise yazılı haliyle de gösterir
        Returns:
            Formatlı string
        """
        if tutar is None:
            return "-"

        try:
            tutar = float(tutar)
            # Rakamları formatla: 5.300.000
            formatted = "{:,.0f}".format(tutar).replace(',', '.')

            if yazili:
                # Yazılı hali için basit bir çevirici (geliştirilmeli)
                return f"{formatted} TL ({self._sayi_yaziya(tutar)} Türk Lirası)"
            else:
                return f"{formatted} TL"
        except:
            return str(tutar)

    def _sayi_yaziya(self, sayi):
        """Sayıyı yazıya çevirir (basit versiyon)"""
        try:
            sayi = int(sayi)
            # Basit bir yazıya çevirme (gerçek uygulamada num2words kullanılabilir)
            birler = ["", "Bir", "İki", "Üç", "Dört", "Beş", "Altı", "Yedi", "Sekiz", "Dokuz"]
            onlar = ["", "On", "Yirmi", "Otuz", "Kırk", "Elli", "Altmış", "Yetmiş", "Seksen", "Doksan"]

            if sayi == 0:
                return "Sıfır"

            milyonlar = sayi // 1000000
            binler = (sayi % 1000000) // 1000
            yuzler = sayi % 1000

            sonuc = []

            if milyonlar > 0:
                if milyonlar == 1:
                    sonuc.append("Bir Milyon")
                else:
                    sonuc.append(self._yuz_cikar(milyonlar) + " Milyon")

            if binler > 0:
                if binler == 1:
                    sonuc.append("Bin")
                else:
                    sonuc.append(self._yuz_cikar(binler) + " Bin")

            if yuzler > 0:
                sonuc.append(self._yuz_cikar(yuzler))

            return " ".join(sonuc)
        except:
            return str(sayi)

    def _yuz_cikar(self, sayi):
        """0-999 arası sayıyı yazıya çevirir"""
        birler = ["", "Bir", "İki", "Üç", "Dört", "Beş", "Altı", "Yedi", "Sekiz", "Dokuz"]
        onlar = ["", "On", "Yirmi", "Otuz", "Kırk", "Elli", "Altmış", "Yetmiş", "Seksen", "Doksan"]

        yuzler = sayi // 100
        kalanlar = sayi % 100
        onlar_basamak = kalanlar // 10
        birler_basamak = kalanlar % 10

        sonuc = []

        if yuzler > 0:
            if yuzler == 1:
                sonuc.append("Yüz")
            else:
                sonuc.append(birler[yuzler] + " Yüz")

        if onlar_basamak > 0:
            sonuc.append(onlar[onlar_basamak])

        if birler_basamak > 0:
            sonuc.append(birler[birler_basamak])

        return " ".join(sonuc)

    def kapak_sayfasi_olustur(self, story, veri, stiller):
        """Kapak sayfası - Örnek rapor formatında"""

        story.append(Spacer(1, 2*cm))

        # Başlık
        story.append(self._p("<b>GAYRİMENKUL DEĞERLEME RAPORU</b>", stiller['KapakBaslik']))
        story.append(Spacer(1, 1*cm))

        # Müşteri adı (büyük)
        musteri = veri.get('talep_eden_kurum', 'SERDAR GENEK')
        story.append(self._p(f"<b>{musteri}</b>", stiller['KapakBaslik']))
        story.append(Spacer(1, 0.5*cm))

        # Gayrimenkul bilgisi
        il = veri.get('il', 'MUĞLA')
        ilce = veri.get('ilce', 'MENTEŞE')
        mahalle = veri.get('mahalle', 'EMİRBEYAZIT')
        ada = veri.get('ada', '546')
        parsel = veri.get('parsel', '29')
        bagimsiz_bolum = veri.get('bagimsiz_bolum_no', '10')

        konum_text = f"{il.upper()} İLİ, {ilce.upper()} İLÇESİ<br/>{mahalle.upper()} MAHALLESİ<br/>{ada} ADA - {parsel} PARSEL<br/>{bagimsiz_bolum} BAĞIMSIZ BÖLÜM NUMARALI TAŞINMAZ"
        story.append(self._p(konum_text, ParagraphStyle(
            'Konum',
            fontName=self.font_name,
            fontSize=12,
            alignment=TA_CENTER,
            leading=16
        )))

        story.append(Spacer(1, 1*cm))

        # Fotoğraf ve imza bloğunu KeepTogether içinde tut
        fotograf_imza_elemanlari = []

        # Fotoğraf varsa ekle
        if veri.get('fotograflar') and len(veri['fotograflar']) > 0:
            try:
                foto_yolu = veri['fotograflar'][0]
                # Fotoğraf yüksekliği 9.5 cm'e düşürüldü
                img = Image(foto_yolu, width=14*cm, height=9.5*cm, kind='proportional')
                fotograf_imza_elemanlari.append(img)
            except:
                pass

        # Fotoğraf ve imza arası Spacer küçültüldü (1.0 cm)
        fotograf_imza_elemanlari.append(Spacer(1, 1.0*cm))

        # HAZIRLAYAN bilgisi
        fotograf_imza_elemanlari.append(self._p("<b>HAZIRLAYAN</b>", ParagraphStyle(
            'Hazirlayan',
            fontName=self.font_bold,
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=10
        )))

        # AREA logosu ve şirket bilgisi
        fotograf_imza_elemanlari.append(self._p("<b>A.R.E.A. GAYRİMENKUL DEĞERLEME ve DANIŞMANLIK A.Ş.</b>",
                              ParagraphStyle(
            'Sirket',
            fontName=self.font_bold,
            fontSize=11,
            alignment=TA_CENTER
        )))

        fotograf_imza_elemanlari.append(Spacer(1, 0.3*cm))
        fotograf_imza_elemanlari.append(self._p("Hilal Mahallesi, Hollanda Caddesi, No: 9/6 ÇANKAYA/ANKARA",
                            ParagraphStyle('SirketAdres', fontName=self.font_name, fontSize=9, alignment=TA_CENTER)))
        fotograf_imza_elemanlari.append(Spacer(1, 0.5*cm))

        # Uzman bilgileri
        degerleme_uzmani = veri.get('degerleme_uzmani', 'EMRAH YÜCE')
        uzman_sicil = veri.get('uzman_sicil_no', '411210')
        kontrol_uzmani = veri.get('kontrol_uzmani', 'MELİH ŞENTÜRK')
        kontrol_sicil = veri.get('kontrol_uzmani_sicil', '405654')

        tarih = datetime.now().strftime("Tarih: %d/%m/%Y<br/>%H:%M")

        uzman_text = f"""<b>EMRAH YÜCE</b><br/>
Gayrimenkul Değerleme Uzmanı<br/>
SPK LİSANS NO:{uzman_sicil}<br/>
e-imzalanmıştır.<br/>
{tarih}"""

        kontrol_text = f"""<b>MELİH ŞENTÜRK</b><br/>
Değerleme Uzmanı - Denetmen<br/>
SPK LİSANS NO: {kontrol_sicil}<br/>
e-imzalanmıştır.<br/>
{tarih}"""

        soruml_text = f"""<b>EMRE AKAR</b><br/>
Sorumlu Değerleme Uzmanı<br/>
SPK LİSANS NO: 401323<br/>
e-imzalanmıştır.<br/>
{tarih}"""

        uzman_data = [
            [self._p(uzman_text, stiller['TabloMetin']),
             self._p(kontrol_text, stiller['TabloMetin']),
             self._p(soruml_text, stiller['TabloMetin'])]
        ]

        uzman_tablo = Table(uzman_data, colWidths=[5.5*cm, 5.5*cm, 5.5*cm])
        uzman_tablo.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))

        fotograf_imza_elemanlari.append(uzman_tablo)

        # Fotoğraf + imza bloğunu KeepTogether ile sarmalayarak ilk sayfadan taşma ihtimalini azalt
        story.append(KeepTogether(fotograf_imza_elemanlari))
        story.append(PageBreak())

    def icindekiler_olustur(self, story, stiller):
        """İçindekiler sayfası"""

        story.append(Spacer(1, 1*cm))
        story.append(self._p("<b>İÇİNDEKİLER</b>", stiller['BolumBaslik']))
        story.append(Spacer(1, 0.5*cm))

        icindekiler_items = [
            ("1. RAPOR ÖZETİ", "3"),
            ("2. RAPOR BİLGİLERİ", "4"),
            ("   2.1. Rapor Tarihi ve Numarası", "4"),
            ("   2.2. Rapor Türü", "4"),
            ("   2.3. Raporu Hazırlayanlar", "4"),
            ("   2.4. Değerleme Tarihi", "4"),
            ("   2.5. Dayanak Sözleşmesi Tarihi ve Numarası", "4"),
            ("   2.6. Raporun Düzenlenme Amacı", "4"),
            ("3. ŞİRKET VE MÜŞTERİYİ TANITICI BİLGİLER", "5"),
            ("   3.1. Değerleme Şirketi Bilgileri", "5"),
            ("   3.2. Müşteri Bilgileri", "5"),
            ("   3.3. Müşteri Taleplerinin Kapsamı, Getirilen Sınırlamalar ve Varsayımlar", "5"),
            ("4. DEĞERLEME KONUSU GAYRİMENKULE İLİŞKİN BİLGİLER", "6"),
            ("   4.1. Gayrimenkulün Yeri, Konumu ve Ulaşım Durumu", "6"),
            ("   4.2. Tapu Sicilinde Tespit Edilen Tescil Durumuna İlişkin Bilgiler", "7"),
            ("   4.3. Resmi Kurum İncelemesi", "8"),
            ("   4.4. Gayrimenkulün Özellikleri", "8"),
            ("   4.5. 3 Bağımsız Bölüm Numaralı Taşınmaz", "8"),
            ("   4.6. Değerlemenin Tanımı, Standartları Ve Değerleme Yaklaşımları İle Bunların Seçilme Nedenleri", "9"),
            ("       4.6.1. Değerlemenin Tanım ve Kapsamı", "9"),
            ("       4.6.2. Değer Standartları (Esasları)", "9"),
            ("       4.6.3. Piyasa Değeri", "9"),
            ("       4.6.4. Piyasa Değeri (Satışların Karşılaştırılması) Yaklaşımı", "9"),
            ("       4.6.5. Maliyet (Yeniden İnşa Etme) Yaklaşımı", "10"),
            ("       4.6.6. Gelir Kapitalizasyon Yaklaşımı", "10"),
            ("       4.6.7. Uygulanan Değerleme Yaklaşımı", "10"),
            ("   4.7. Değerleme İşlemini Etkileyen Faktörler", "11"),
            ("   4.8. Değerlemede Kabul Edilen Varsayımlar", "11"),
            ("   4.9. En Etkin ve En Verimli Kullanım Analizi", "11"),
            ("   4.10. Piyasa Yaklaşımı, Benzer Satış Örnekleri ve Bunların Karşılaştırılması", "11"),
            ("   4.11. Proje Geliştirme & Gelir Yaklaşımı", "12"),
            ("   4.12. Maliyet Oluşumları Yaklaşımı", "12"),
            ("5. SONUÇ", "13"),
            ("   5.1. Sorumlu değerleme uzmanının sonuç cümlesi", "13"),
            ("   5.2. Sonuç", "13"),
            ("6. EKLER", "14"),
        ]

        ic_data = [[self._p(item[0], stiller['Normal']), item[1]] for item in icindekiler_items]

        ic_tablo = Table(ic_data, colWidths=[15*cm, 2*cm])
        ic_tablo.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))

        story.append(ic_tablo)
        story.append(PageBreak())

    def rapor_ozeti_olustur(self, story, veri, stiller):
        """1. RAPOR ÖZETİ"""

        story.append(Spacer(1, 0.5*cm))
        story.append(self._p("<b>1. RAPOR ÖZETİ</b>", stiller['BolumBaslik']))
        story.append(Spacer(1, 0.3*cm))

        # Özet tablosu 1
        rapor_tarihi = datetime.now().strftime("%d.%m.%Y")
        rapor_no = veri.get('rapor_no_firma', datetime.now().strftime("%d.%m.%Y/2025_ÖZL_061"))

        ozet_data1 = [
            [self._p("<b>Değerleme Talep Eden Kurum /Kişi</b>", stiller['TabloMetinBold']),
             self._p(veri.get('talep_eden_kurum', 'SERDAR GENEK'), stiller['TabloMetin'])],
            [self._p("<b>Dayanak Sözleşme Tarih ve No</b>", stiller['TabloMetinBold']),
             self._p(veri.get('talep_tarihi', '15.08.2025') + " / -", stiller['TabloMetin'])],
            [self._p("<b>Değerleme Konusu Gayrimenkul</b>", stiller['TabloMetinBold']),
             self._p(f"{veri.get('il', 'Muğla')} İli, {veri.get('ilce', 'Menteşe')} İlçesi, {veri.get('mahalle', 'Emirbeyazıt')} Mahallesi'nde {veri.get('ada', '546')} Ada - {veri.get('parsel', '29')} Parselde {veri.get('bagimsiz_bolum_no', '10')} no'lu mesken nitelikli taşınmaz", stiller['TabloMetin'])],
            [self._p("<b>Raporun Konusu</b>", stiller['TabloMetinBold']),
             self._p("Gayrimenkul Değerleme", stiller['TabloMetin'])],
            [self._p("<b>Rapor Tarihi ve No.su</b>", stiller['TabloMetinBold']),
             self._p(rapor_no, stiller['TabloMetin'])],
        ]

        tablo1 = Table(ozet_data1, colWidths=[6*cm, 11*cm])
        tablo1.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.gri_renk),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(tablo1)
        story.append(Spacer(1, 0.5*cm))

        # Özet tablosu 2 - Referanslar
        ref_data = [
            [self._p("<b>Gayrimenkul özellikleri</b>", stiller['TabloMetinBold']),
             self._p("Raporun 4.4. başlığı altında verilmiştir.", stiller['TabloMetin'])],
            [self._p("<b>Adresi</b>", stiller['TabloMetinBold']),
             self._p("2.6. başlığında belirtilmiştir.", stiller['TabloMetin'])],
            [self._p("<b>Tapu Bilgileri Özeti</b>", stiller['TabloMetinBold']),
             self._p("4.2. başlığında belirtilmiştir.", stiller['TabloMetin'])],
            [self._p("<b>Parsel Yüzölçümü</b>", stiller['TabloMetinBold']),
             self._p("4.2. başlığında belirtilmiştir.", stiller['TabloMetin'])],
            [self._p("<b>Tapu İncelemesi</b>", stiller['TabloMetinBold']),
             self._p("4.2. başlığında belirtilmiştir.", stiller['TabloMetin'])],
            [self._p("<b>İmar Durumu</b>", stiller['TabloMetinBold']),
             self._p("4.3. başlığında belirtilmiştir.", stiller['TabloMetin'])],
        ]

        tablo2 = Table(ref_data, colWidths=[6*cm, 11*cm])
        tablo2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.gri_renk),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(tablo2)
        story.append(Spacer(1, 0.5*cm))

        # Piyasa Değeri Tablosu
        piyasa_data = [
            [self._p("<b>Piyasa Değeri (TL)</b>", stiller['TabloMetinBold']),
             self._p(f"<b>Yasal Durum Değeri:</b> {veri.get('yasal_deger_tl', '5.300.000 TL (Beş Milyon Üç Yüz Bin Türk Lirası)')},<br/><b>Mevcut Durum Değeri:</b> {veri.get('mevcut_deger_tl', '5.600.000 TL (Beş Milyon Altı Yüz Bin Türk Lirası)')}", stiller['TabloMetin'])],
            [self._p("<b>Piyasa Değeri (USD)</b>", stiller['TabloMetinBold']),
             self._p(f"<b>Yasal Durum Değeri:</b> {veri.get('yasal_deger_usd', '129.641 USD (Yüz Yirmi Dokuz Bin Altı Yüz Kırk Bir Amerikan Doları)')},<br/><b>Mevcut Durum Değeri:</b> {veri.get('mevcut_deger_usd', '136.979 USD (Yüz Otuz Altı Bin Dokuz Yüz Yetmiş Dokuz Amerikan Doları)')}", stiller['TabloMetin'])],
        ]

        tablo3 = Table(piyasa_data, colWidths=[5*cm, 12*cm])
        tablo3.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.gri_renk),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(tablo3)

        story.append(PageBreak())

    def tapu_bilgileri_olustur(self, story, veri, stiller, takbis_verisi):
        """4.2. Tapu Sicilinde Tespit Edilen Tescil Durumuna İlişkin Bilgiler - DÜZELTME"""

        story.append(self._p("<b>4.2. Tapu Sicilinde Tespit Edilen Tescil Durumuna İlişkin Bilgiler</b>", stiller['AltBaslik']))

        giris_text = """Değerleme konusu taşınmazın tesciline ilişkin bilgiler Tapu Kadastro Genel Müdürlüğü - TAKBİS sistemi üzerinden
alınmış olup, sicil bilgileri aşağıdaki tablolarda gösterildiği şekilde tespit edilmiştir. (Bkz. Rapor Eki - TAKBİS Kayıtları)"""

        story.append(self._p(giris_text, stiller['Normal']))
        story.append(Spacer(1, 0.5*cm))

        # TAKBIS TAPU KAYIT TABLOSU - WORD WRAP İLE
        story.append(self._p("<b>TAPU KAYIT TABLOSU</b>", ParagraphStyle(
            'TakbisBaslik',
            fontName=self.font_bold,
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=6
        )))

        # TAKBIS verilerini kullan veya default değerler
        if takbis_verisi and not takbis_verisi.get('hata'):
            genel = takbis_verisi.get('genel_bilgiler', {})
            ana_tas = takbis_verisi.get('ana_tasinmaz', {})
            bagim_bol = takbis_verisi.get('bagimsiz_bolum', {})
        else:
            genel = {}
            ana_tas = {}
            bagim_bol = {}

        # Bağımsız bölüm no düzeltmesi - veri'den al
        bagimsiz_bolum_no = veri.get('bagimsiz_bolum_no', bagim_bol.get('bolum_no', '10'))

        # Ana tablo - HER HÜCRE PARAGRAPH
        takbis_data = [
            [self._p("<b>İLİ</b>", stiller['TabloMetinBold']),
             self._p(genel.get('il', veri.get('il', 'MUĞLA')), stiller['TabloMetin']),
             self._p("<b>ANA TAŞINMAZ NİTELİĞİ</b>", stiller['TabloMetinBold']),
             self._p("<b>BİR BODRUM BİR ZEMİN DÖRT NORMAL KATLI (1) NUMARALI KATI APARTMAN</b>", stiller['TabloMetinBold'])],

            [self._p("<b>İLÇESİ</b>", stiller['TabloMetinBold']),
             self._p(genel.get('ilce', veri.get('ilce', 'MENTEŞE')), stiller['TabloMetin']),
             self._p("<b>YÜZÖLÇÜMÜ (m²)</b>", stiller['TabloMetinBold']),
             self._p(genel.get('yuzolcumu', veri.get('yuzolcumu', '522,56')), stiller['TabloMetin'])],

            [self._p("<b>MAHALLESİ</b>", stiller['TabloMetinBold']),
             self._p(genel.get('mahalle', veri.get('mahalle', 'EMİRBEYAZIT')), stiller['TabloMetin']),
             self._p("<b>TAPU TARİHİ</b>", stiller['TabloMetinBold']),
             self._p(genel.get('tapu_tarihi', '13/04/2018'), stiller['TabloMetin'])],

            [self._p("<b>BUCAĞI</b>", stiller['TabloMetinBold']),
             self._p("-", stiller['TabloMetin']),
             self._p("<b>YEVMİYE NO</b>", stiller['TabloMetinBold']),
             self._p(ana_tas.get('yevmiye_no', '3770'), stiller['TabloMetin'])],

            [self._p("<b>KÖYÜ</b>", stiller['TabloMetinBold']),
             self._p("-", stiller['TabloMetin']),
             self._p("<b>CİLT NO</b>", stiller['TabloMetinBold']),
             self._p(ana_tas.get('cilt_no', '4'), stiller['TabloMetin'])],

            [self._p("<b>SOKAĞI</b>", stiller['TabloMetinBold']),
             self._p("-", stiller['TabloMetin']),
             self._p("<b>SAHİFE NO</b>", stiller['TabloMetinBold']),
             self._p(ana_tas.get('sahife_no', '326'), stiller['TabloMetin'])],

            [self._p("<b>MEVKİİ</b>", stiller['TabloMetinBold']),
             self._p(genel.get('mevkii', '-'), stiller['TabloMetin']),
             self._p("<b>TAPU TESCİL ŞEKLİ</b>", stiller['TabloMetinBold']),
             self._p("☐ ARSA/CİNS TASHİHLİ<br/>☐ KAT İRTİFAKI<br/>☑ KAT MÜLKİYETİ<br/>☐ DEVRE MÜLK", stiller['TabloMetin'])],

            [self._p("<b>PAFTA NO</b>", stiller['TabloMetinBold']),
             self._p(genel.get('pafta_no', '-'), stiller['TabloMetin']),
             self._p("<b>B.BÖLÜM ARSA PAYI</b>", stiller['TabloMetinBold']),
             self._p(bagim_bol.get('bagimsiz_bolum_arsa_payi', '172/1820'), stiller['TabloMetin'])],

            [self._p("<b>ADA NO</b>", stiller['TabloMetinBold']),
             self._p(genel.get('ada_no', veri.get('ada', '546')), stiller['TabloMetin']),
             self._p("<b>TAŞINMAZ ID</b>", stiller['TabloMetinBold']),
             self._p(bagim_bol.get('tasinmaz_id', '18447484'), stiller['TabloMetin'])],

            [self._p("<b>PARSEL NO</b>", stiller['TabloMetinBold']),
             self._p(genel.get('parsel_no', veri.get('parsel', '29')), stiller['TabloMetin']),
             self._p("<b>B. BÖLÜM NİTELİK</b>", stiller['TabloMetinBold']),
             self._p(bagim_bol.get('nitelik', 'Mesken'), stiller['TabloMetin'])],

            [self._p("<b>B. BÖLÜM KAT NO</b>", stiller['TabloMetinBold']),
             self._p(bagim_bol.get('kat_no', '10'), stiller['TabloMetin']),
             "", ""],

            [self._p("<b>B. BÖLÜM NO</b>", stiller['TabloMetinBold']),
             self._p(bagimsiz_bolum_no, stiller['TabloMetin']),
             "", ""],
        ]

        takbis_tablo = Table(takbis_data, colWidths=[3.5*cm, 4*cm, 4*cm, 5.5*cm])
        takbis_tablo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.acik_mavi),
            ('BACKGROUND', (2, 0), (2, -1), self.acik_mavi),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))

        story.append(takbis_tablo)
        story.append(Spacer(1, 0.5*cm))

        # Malik/Hisse Tablosu
        malik_data = [
            [self._p("<b>MALİK</b>", stiller['TabloMetinBold']),
             self._p("<b>HİSSE</b>", stiller['TabloMetinBold']),
             self._p("<b>EDİNME SEBEBİ</b>", stiller['TabloMetinBold'])],
            [self._p("SERMAYE PAZAR DEĞERİ", stiller['TabloMetin']),
             self._p("1/1", stiller['TabloMetin']),
             self._p("SATIŞ VE İPOTEK", stiller['TabloMetin'])],
        ]

        # TAKBIS'ten malik bilgilerini ekle
        if takbis_verisi and not takbis_verisi.get('hata'):
            malik_listesi = takbis_verisi.get('malik_bilgileri', [])
            if malik_listesi:
                for malik in malik_listesi:
                    malik_data.append([
                        self._p(malik.get('malik_adi', '-'), stiller['TabloMetin']),
                        self._p(malik.get('hisse', '-'), stiller['TabloMetin']),
                        self._p(malik.get('edinme_sebebi', '-'), stiller['TabloMetin'])
                    ])

        malik_tablo = Table(malik_data, colWidths=[7*cm, 3*cm, 7*cm])
        malik_tablo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.acik_mavi),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))

        story.append(malik_tablo)
        story.append(Spacer(1, 0.3*cm))

        # BEYAN bölümü
        if takbis_verisi and not takbis_verisi.get('hata'):
            beyan = takbis_verisi.get('beyan', {})
            if beyan.get('tarih'):
                beyan_text = f"""<b>BEYAN</b><br/>
- {beyan.get('tarih', '')} TARİHLİ YÖNETİM PLANI<br/>
- 3402 Sayılı Kanunun 22. maddesinin 2. fıkrasının (a) bendi uygulamasına tabidir.( Şablon: 3402 Sayılı Kadastro
Kanunun 22. Md. Fıkrasının (a) Bendi Gereği Belirtme ) (20/08/2024 – 1/97) )"""

                story.append(self._p(beyan_text, stiller['Normal']))
                story.append(Spacer(1, 0.3*cm))

        # Ek bilgi
        ek_bilgi = """TKGİM bilgi sisteminden alınan TAKBİS belgesine göre değerleme konusu taşınmazın tapu kaydı yukanda belirtildiği
gibidir.

Değerleme konusu taşınmazların mevcut durumu, piyasa değeri ve kullanım kabiliyetleri birlikte
değerlendirildiğinde taşınmazların satış kabiliyeti "SATILABIL İR" olarak belirlenmiştir."""

        story.append(self._p(ek_bilgi, stiller['Normal']))

        story.append(PageBreak())

    def rapor_bilgileri_olustur(self, story, veri, stiller):
        """2. RAPOR BİLGİLERİ - TAM"""

        story.append(Spacer(1, 0.5*cm))
        story.append(self._p("<b>2. RAPOR BİLGİLERİ</b>", stiller['BolumBaslik']))

        # 2.1
        story.append(self._p("<b>2.1. Rapor Tarihi ve Numarası</b>", stiller['AltBaslik']))
        rapor_no = veri.get('rapor_no_firma', datetime.now().strftime("%d.%m.%Y/2025_ÖZL_061"))
        story.append(self._p(rapor_no, stiller['Normal']))
        story.append(Spacer(1, 0.3*cm))

        # 2.2
        story.append(self._p("<b>2.2. Rapor Türü</b>", stiller['AltBaslik']))
        rapor_turu = """Rapor içerisinde belirtilen gayrimenkulün değerleme tarihindeki "adil piyasa" değerinin Türk Lirası ve döviz
cinsinden belirlenmesi amacıyla hazırlanan değerleme raporudur.

Rapor, gayrimenkulün tamamını ve bağlı olan tüm hakları kapsamaktadır."""
        story.append(self._p(rapor_turu, stiller['Normal']))
        story.append(Spacer(1, 0.3*cm))

        # 2.3
        story.append(self._p("<b>2.3. Raporu Hazırlayanlar</b>", stiller['AltBaslik']))
        uzman_text = f"""<b>EMRE AKAR</b><br/>
Sorumlu Değerleme Uzmanı<br/>
SPK LİSANS NO: 401323<br/><br/>

<b>{veri.get('kontrol_uzmani', 'MELİH ŞENTÜRK')}</b><br/>
Değerleme Uzmanı - Denetmen<br/>
SPK LİSANS NO: {veri.get('kontrol_uzmani_sicil', '405654')}<br/><br/>

<b>{veri.get('degerleme_uzmani', 'EMRAH YÜCE')}</b><br/>
Gayrimenkul Değerleme Uzmanı<br/>
SPK LİSANS NO:{veri.get('uzman_sicil_no', '411210')}"""
        story.append(self._p(uzman_text, stiller['Normal']))
        story.append(Spacer(1, 0.5*cm))

        # 2.4
        story.append(self._p("<b>2.4. Değerleme Tarihi</b>", stiller['AltBaslik']))
        degerleme_tarihi = datetime.now().strftime("%d.%m.%Y")
        story.append(self._p(f"Değerleme çalışması {degerleme_tarihi} tarihinde yapılmıştır.", stiller['Normal']))
        story.append(Spacer(1, 0.3*cm))

        # 2.5
        story.append(self._p("<b>2.5. Dayanak Sözleşmesi Tarihi ve Numarası</b>", stiller['AltBaslik']))
        dayanak = veri.get('talep_tarihi', '15.08.2025')
        story.append(self._p(f"Bu rapor {dayanak} tarihli sözleşmeye istinaden hazırlanmıştır.", stiller['Normal']))
        story.append(Spacer(1, 0.3*cm))

        # 2.6
        story.append(self._p("<b>2.6. Raporun Düzenlenme Amacı</b>", stiller['AltBaslik']))
        amac = f"""** Müşteri talebi kapsamında; tarafımıza iletilen tapu kayıtlarına göre {veri.get('il', 'Muğla')} İli, {veri.get('ilce', 'Menteşe')} İlçesi, {veri.get('mahalle', 'Emirbeyazıt')}
Mahallesi, {veri.get('ada', '546')} Ada - {veri.get('parsel', '29')} Parselde konumlu, {veri.get('bagimsiz_bolum_no', '10')} no'lu mesken nitelikli taşınmaz değerleme tarihindeki
muhtemel değerinin bağımsız ve tarafsız olarak takdiri ve raporlanması talep edilmiştir."""
        story.append(self._p(amac, stiller['Normal']))

        story.append(PageBreak())

    def sirket_bilgileri_olustur(self, story, veri, stiller):
        """3. ŞİRKET VE MÜŞTERİYİ TANITICI BİLGİLER - TAM"""

        story.append(Spacer(1, 0.5*cm))
        story.append(self._p("<b>3. ŞİRKET VE MÜŞTERİYİ TANITICI BİLGİLER</b>", stiller['BolumBaslik']))

        # 3.1
        story.append(self._p("<b>3.1. Değerleme Şirketi Bilgileri</b>", stiller['AltBaslik']))

        sirket_giris = """A.R.E.A. Gayrimenkul Değerleme ve Danışmanlık A.Ş. firması Sermaye Piyasası Kurulu'nun 06.10.2010 tarih ve
29/878 sayılı kararı ile sermaye piyasası mevzuatı kapsamında değerleme hizmeti vermek üzere
lisanslandırılmış olup, şirketin tescil bilgileri aşağıda verilmiştir."""
        story.append(self._p(sirket_giris, stiller['Normal']))
        story.append(Spacer(1, 0.3*cm))

        sirket_data = [
            [self._p("<b>Ünvan</b>", stiller['TabloMetinBold']),
             self._p("A.R.E.A. Gayrimenkul Değerleme ve Danışmanlık A.Ş.", stiller['TabloMetin'])],
            [self._p("<b>Merkez</b>", stiller['TabloMetinBold']),
             self._p("Çankaya, Ankara", stiller['TabloMetin'])],
            [self._p("<b>Adres</b>", stiller['TabloMetinBold']),
             self._p("Hilal Mahallesi, Hollanda Caddesi, No: 9/6 Çankaya/ANKARA", stiller['TabloMetin'])],
            [self._p("<b>Kuruluş Tarihi</b>", stiller['TabloMetinBold']),
             self._p("25.01.2010", stiller['TabloMetin'])],
            [self._p("<b>Ticaret Siciline Tescil Tarihi</b>", stiller['TabloMetinBold']),
             self._p("25.01.2010", stiller['TabloMetin'])],
            [self._p("<b>Ticaret Sicil Numarası</b>", stiller['TabloMetinBold']),
             self._p("275561", stiller['TabloMetin'])],
            [self._p("<b>Sermayesi</b>", stiller['TabloMetinBold']),
             self._p("1.000.000,00 TL", stiller['TabloMetin'])],
            [self._p("<b>Kayıtlı Vergi Dairesi/V.No</b>", stiller['TabloMetinBold']),
             self._p("Seğmenler Vergi Dairesi / 0010670569", stiller['TabloMetin'])],
        ]

        sirket_tablo = Table(sirket_data, colWidths=[6*cm, 11*cm])
        sirket_tablo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.gri_renk),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(sirket_tablo)
        story.append(Spacer(1, 0.5*cm))

        # Faaliyet konusu
        faaliyet = """<b>Faaliyet konusu:</b> Yürürlükte bulunan hukuki düzenlemeler kapsamında kamu ve özel, gerçek
ve tüzel kişi kurum ve kuruluşlara ait bir gayrimenkulün, gayrimenkul
projesinin veya bir gayrimenkule bağlı hak ve faydaların belli bir tarihteki
muhtemel değerinin bağımsız ve tarafsız olarak takdiri, gayrimenkül ile ilgili
piyasa araştırması, fizibilite çalışmaları, gayrimenkuller ve bunlara bağlı
hakların hukuki durumunun belirlenmesi, gayrimenkuller ve
gayrimenkullerle ilgili yatırım, proje değeri ve en iyi kullanım değeri analizi,
geliştirilmiş proje değeri analizi, eski eser gayrimenkullerin restorasyon-
restitüsyon proje değeri analizi, gibi konularda değerleme ve danışmanlık
hizmeti vermektir."""
        story.append(self._p(faaliyet, stiller['Normal']))
        story.append(Spacer(1, 0.5*cm))

        # 3.2
        story.append(self._p("<b>3.2. Müşteri Bilgileri</b>", stiller['AltBaslik']))

        musteri_data = [
            [self._p("<b>Müşteri Unvanı</b>", stiller['TabloMetinBold']),
             self._p(veri.get('talep_eden_kurum', 'SERDAR GENEK'), stiller['TabloMetin'])],
            [self._p("<b>Müşteri Adresi</b>", stiller['TabloMetinBold']),
             self._p("", stiller['TabloMetin'])],
            [self._p("<b>Müşteri Vergi Dairesi Adı ve VKN</b>", stiller['TabloMetinBold']),
             self._p("", stiller['TabloMetin'])],
            [self._p("<b>Müşteri Tel</b>", stiller['TabloMetinBold']),
             self._p("", stiller['TabloMetin'])],
            [self._p("<b>Müşteri E-Posta</b>", stiller['TabloMetinBold']),
             self._p("", stiller['TabloMetin'])],
        ]

        musteri_tablo = Table(musteri_data, colWidths=[7*cm, 10*cm])
        musteri_tablo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.gri_renk),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(musteri_tablo)
        story.append(Spacer(1, 0.5*cm))

        # 3.3
        story.append(self._p("<b>3.3. Müşteri Taleplerinin Kapsamı, Getirilen Sınırlamalar ve Varsayımlar</b>", stiller['AltBaslik']))

        talep = f"""Müşteri; tarafımıza iletilen tapu kayıtlarına göre {veri.get('il', 'Muğla')} İli, {veri.get('ilce', 'Menteşe')} İlçesi, {veri.get('mahalle', 'Emirbeyazıt')} Mahallesi, {veri.get('ada', '546')} Ada - {veri.get('parsel', '29')}
Parselde konumlu, {veri.get('bagimsiz_bolum_no', '10')} no'lu mesken nitelikli taşınmazın değerleme tarihindeki muhtemel değerinin bağımsız
ve tarafsız olarak takdiri ve raporlanmasını talep etmiştir."""
        story.append(self._p(talep, stiller['Normal']))

        story.append(PageBreak())

    def gayrimenkul_yeri_olustur(self, story, veri, stiller):
        """4.1. Gayrimenkulün Yeri, Konumu ve Ulaşım Durumu"""

        story.append(Spacer(1, 0.5*cm))
        story.append(self._p("<b>4. DEĞERLEME KONUSU GAYRİMENKULE İLİŞKİN BİLGİLER</b>", stiller['BolumBaslik']))

        story.append(self._p("<b>4.1. Gayrimenkulün Yeri, Konumu ve Ulaşım Durumu</b>", stiller['AltBaslik']))

        konum = f"""Değerlemeye konu taşınmaz, {veri.get('il', 'Muğla')} İli, {veri.get('ilce', 'Menteşe')} İlçesi, {veri.get('mahalle', 'Emirbeyazıt')} Mahallesi, Avcılar 1. Sokak, Gökova Apartmanı, No:
44 Kat:4 Daire:{veri.get('bagimsiz_bolum_no', '10')} (UYAT NO: 1337862900) posta adresi yerde bulunmaktadır. Değerlemeye konu taşınmaza ulaşım
yolu taşınma alanlarından başlamaktadır.

Taşınmaz kentsel ölçekte yüksek düzeyde tanınmış bölgede, şehir merkezinde yer almaktadır. Taşınmaz bölgenin ana
arterlerinden olan Atatürk Bulvarına ve Zübeyde Hanım Caddesine yakın mesafede bulunmaktadır. Taşınmazın çevresinde
konut ve ticaret alanları bulunmaktadır. Bölgenin alt yapısı tam olup ulaşım imkanları iyi koşullardır.

Değerlemesi yapılan {veri.get('bagimsiz_bolum_no', '10')} nolu bağımsız bölümün bulunduğu {veri.get('ada', '546')} Ada - {veri.get('parsel', '29')} Parsel sayılı 522.56 m² alanlı taşınmaz üzerinde;
kat mülkiyeti tesisli, ayrık nizamda, betonarme yapı tarzında, 3/A yapı grubunda 1 adet bina bulunmaktadır."""

        story.append(self._p(konum, stiller['Normal']))
        story.append(Spacer(1, 0.5*cm))

        # Konum haritası varsa
        if veri.get('konum_haritasi'):
            try:
                img = Image(veri['konum_haritasi'], width=15*cm, height=10*cm, kind='proportional')
                story.append(img)
                story.append(Spacer(1, 0.5*cm))
            except:
                pass

        story.append(PageBreak())

    def _hesapla_piyasa_degeri(self, veri):
        """Emsal ve alan bilgilerinden piyasa değerini hesaplar"""
        # Önce veri'den hazır değerleri kontrol et
        yasal_deger = veri.get('yasal_deger_tl_rakam')
        mevcut_deger = veri.get('mevcut_deger_tl_rakam')

        # Eğer yoksa emsal özetinden hesapla
        if not yasal_deger or not mevcut_deger:
            emsal_ozeti = veri.get('_emsal_ozeti', {})
            brut_alan = veri.get('brut_alan_rakam')
            net_alan = veri.get('net_alan_rakam')

            # Alan bilgisi varsa ve emsal ortalama fiyat varsa
            if brut_alan and emsal_ozeti.get('ortalama_fiyat'):
                ort_birim_fiyat = emsal_ozeti['ortalama_fiyat']

                # Yasal durum değeri (ortalamadan %5 düşük)
                yasal_deger = brut_alan * ort_birim_fiyat * 0.95
                # Mevcut durum değeri (ortalamadan %5 yüksek)
                mevcut_deger = brut_alan * ort_birim_fiyat * 1.05

        return yasal_deger, mevcut_deger

    def sonuc_olustur(self, story, veri, stiller):
        """5. SONUÇ"""

        story.append(Spacer(1, 0.5*cm))
        story.append(self._p("<b>5. SONUÇ</b>", stiller['BolumBaslik']))

        # Değerleri hesapla
        yasal_deger, mevcut_deger = self._hesapla_piyasa_degeri(veri)

        # Varsayılan değerler (eğer hesaplanamazsa)
        yasal_deger_str = self._format_tl(yasal_deger, yazili=True) if yasal_deger else "5.300.000 TL (Beş Milyon Üç Yüz Bin Türk Lirası)"
        mevcut_deger_str = self._format_tl(mevcut_deger, yazili=True) if mevcut_deger else "5.600.000 TL (Beş Milyon Altı Yüz Bin Türk Lirası)"

        # USD değerleri (basit kur ile, gerçek uygulamada API'den alınmalı)
        usd_kur = 40.88  # Örnek kur
        yasal_deger_usd = int(yasal_deger / usd_kur) if yasal_deger else 129641
        mevcut_deger_usd = int(mevcut_deger / usd_kur) if mevcut_deger else 136979

        # 5.1
        story.append(self._p("<b>5.1. Sorumlu değerleme uzmanının sonuç cümlesi</b>", stiller['AltBaslik']))

        sonuc1 = f"""Taşınmazın piyasa değeri, emsal bilgileri kapsamında yapılan mukayeseler, olumlu ve olumsuz özellikleri ile
yukarıda değerli doğrultusunda düzeltilererek taşınmazın yasal durum değeri {yasal_deger_str} olarak,
mevcut durum değeri {mevcut_deger_str} olarak tahmin ve takdir edilmiştir.

Bu takdir, taşınmaz ile ilgili herhangi bir hukuksal sorun bulunmadığı kabulüne dayalıdır.

Raporun planlanan kullanımı Sermaye Piyasası Kurulu düzenlemeleri dışındadır.

Rapor özel mülkiyet kapsamında hazırlanmış olup banka teminatı ve şartname özel uygulamalar kapsamı
dışındadır."""
        story.append(self._p(sonuc1, stiller['Normal']))
        story.append(Spacer(1, 0.5*cm))

        # 5.2
        story.append(self._p("<b>5.2. Sonuç</b>", stiller['AltBaslik']))

        sonuc2 = f"""Raporda çerçevede bilgileri verilen gayrimenkulün bulunduğu yer ve konumu, ulaşım imkanları, büyüklüğü ve
değerine etki edecek diğer özellikleri dikkate alınarak değerleme tarihi itibariyle piyasa değeri;

<b>KDV Hariç Yasal Durum Değeri; {yasal_deger_str},
KDV Hariç Mevcut Durum Değeri; {mevcut_deger_str}
KDV Hariç Yasal Durum Değeri; {self._format_tl(yasal_deger_usd, yazili=False).replace(' TL', ' USD')}
KDV Hariç Mevcut Durum Değeri: {self._format_tl(mevcut_deger_usd, yazili=False).replace(' TL', ' USD')},</b> olarak tahmin ve takdir edilmiştir."""
        story.append(self._p(sonuc2, stiller['Normal']))
        story.append(Spacer(1, 0.5*cm))

        # İmza tablosu
        imza_data = [[
            self._p(f"<b>{veri.get('degerleme_uzmani', 'Emrah YÜCE')}</b><br/>Gayrimenkul Değerleme Uzmanı<br/>SPK LİSANS NO: {veri.get('uzman_sicil_no', '411210')}", stiller['TabloMetin']),
            self._p(f"<b>{veri.get('kontrol_uzmani', 'Melih ŞENTÜRK')}</b><br/>Değerleme Uzmanı - Denetmen<br/>SPK LİSANS NO: {veri.get('kontrol_uzmani_sicil', '405654')}", stiller['TabloMetin']),
            self._p("<b>Emre AKAR</b><br/>Sorumlu Değerleme Uzmanı<br/>SPK LİSANS NO: 401323", stiller['TabloMetin']),
        ]]

        imza_tablo = Table(imza_data, colWidths=[5.5*cm, 5.5*cm, 5.5*cm])
        imza_tablo.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ]))
        story.append(imza_tablo)

        story.append(PageBreak())

    def resmi_kurum_incelemesi_olustur(self, story, veri, stiller):
        """4.3. Resmi Kurum İncelemesi"""

        story.append(self._p("<b>4.3. Resmi Kurum İncelemesi</b>", stiller['AltBaslik']))

        imar_text = f"""Değerleme konusu taşınmazın imar durumu {veri.get('il', 'Muğla')} Büyükşehir Belediyesi İmar ve Şehircilik Daire Başkanlığından temin edilen
imar durum belgesine göre; 1/1000 ölçekli uygulama imar planında "Konut Alanı" olarak planlanmış olup, {veri.get('ada', '546')} ada {veri.get('parsel', '29')} parsel
sayılı parselde imar planına göre Emsal: 1.50, Yençok (Hmax): 15.50 m., yapı nizamı: Ayrık nizam, Taks: 0.30 olarak belirlenmiştir.

İlgili mevzuata göre yapılaşma koşulları aşağıda verilmiştir."""

        story.append(self._p(imar_text, stiller['Normal']))
        story.append(Spacer(1, 0.3*cm))

        # İmar bilgileri tablosu
        imar_data = [
            [self._p("<b>İmar Planı</b>", stiller['TabloMetinBold']),
             self._p("1/1000 Ölçekli Uygulama İmar Planı", stiller['TabloMetin'])],
            [self._p("<b>Fonksiyon</b>", stiller['TabloMetinBold']),
             self._p("Konut Alanı", stiller['TabloMetin'])],
            [self._p("<b>TAKS</b>", stiller['TabloMetinBold']),
             self._p("0.30", stiller['TabloMetin'])],
            [self._p("<b>KAKS (Emsal)</b>", stiller['TabloMetinBold']),
             self._p("1.50", stiller['TabloMetin'])],
            [self._p("<b>Yençok (Hmax)</b>", stiller['TabloMetinBold']),
             self._p("15.50 m.", stiller['TabloMetin'])],
            [self._p("<b>Yapı Nizamı</b>", stiller['TabloMetinBold']),
             self._p("Ayrık Nizam", stiller['TabloMetin'])],
        ]

        imar_tablo = Table(imar_data, colWidths=[5*cm, 12*cm])
        imar_tablo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.gri_renk),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(imar_tablo)
        story.append(PageBreak())

    def gayrimenkul_ozellikleri_olustur(self, story, veri, stiller):
        """4.4. Gayrimenkulün Özellikleri"""

        story.append(self._p("<b>4.4. Gayrimenkulün Özellikleri</b>", stiller['AltBaslik']))

        ozellik_text = f"""Değerleme konusu {veri.get('bagimsiz_bolum_no', '10')} bağımsız bölüm numaralı taşınmaz, {veri.get('il', 'Muğla')} İli, {veri.get('ilce', 'Menteşe')} İlçesi,
{veri.get('mahalle', 'Emirbeyazıt')} Mahallesi, {veri.get('ada', '546')} ada {veri.get('parsel', '29')} parsel üzerinde inşa edilmiş betonarme karkas yapı sistemine sahip,
ayrık nizamda, 1 bodrum + 1 zemin + 4 normal kattan oluşan apartman bloğunun 4. normal katında yer almaktadır.

Taşınmaz mesken niteliğinde olup, bağımsız bölümün brüt alanı yaklaşık 140 m², net kullanım alanı yaklaşık 120 m² olarak tespit edilmiştir."""

        story.append(self._p(ozellik_text, stiller['Normal']))
        story.append(Spacer(1, 0.5*cm))

    def bagimsiz_bolum_olustur(self, story, veri, stiller):
        """4.5. Bağımsız Bölüm Numaralı Taşınmaz"""

        story.append(self._p(f"<b>4.5. {veri.get('bagimsiz_bolum_no', '10')} Bağımsız Bölüm Numaralı Taşınmaz</b>", stiller['AltBaslik']))

        bolum_text = f"""Değerleme konusu {veri.get('bagimsiz_bolum_no', '10')} numaralı bağımsız bölüm 4. normal katta konumlu olup, 3+1 daire tipindedir.
İçerisinde 1 salon, 3 yatak odası, 1 mutfak, 2 banyo/WC ve 1 balkon bulunmaktadır.

Bağımsız bölümde PVC doğrama, laminant parke zemin, iç cephe boya, dış cephe sıva ve boya kaplama bulunmaktadır.
Mutfak ve banyoda seramik kaplama mevcuttur. Isınma sistemi olarak kombi sistemi kullanılmaktadır."""

        story.append(self._p(bolum_text, stiller['Normal']))
        story.append(Spacer(1, 0.5*cm))

        # Bağımsız bölüm özellikleri tablosu
        bolum_data = [
            [self._p("<b>Bağımsız Bölüm No</b>", stiller['TabloMetinBold']),
             self._p(veri.get('bagimsiz_bolum_no', '10'), stiller['TabloMetin'])],
            [self._p("<b>Kat</b>", stiller['TabloMetinBold']),
             self._p("4. Normal Kat", stiller['TabloMetin'])],
            [self._p("<b>Daire Tipi</b>", stiller['TabloMetinBold']),
             self._p("3+1", stiller['TabloMetin'])],
            [self._p("<b>Brüt Alan</b>", stiller['TabloMetinBold']),
             self._p("140 m²", stiller['TabloMetin'])],
            [self._p("<b>Net Alan</b>", stiller['TabloMetinBold']),
             self._p("120 m²", stiller['TabloMetin'])],
            [self._p("<b>Cephe</b>", stiller['TabloMetinBold']),
             self._p("Güney", stiller['TabloMetin'])],
        ]

        bolum_tablo = Table(bolum_data, colWidths=[5*cm, 12*cm])
        bolum_tablo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.gri_renk),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(bolum_tablo)
        story.append(PageBreak())

    def degerleme_tanimi_olustur(self, story, veri, stiller):
        """4.6. Değerlemenin Tanımı, Standartları ve Değerleme Yaklaşımları"""

        story.append(self._p("<b>4.6. Değerlemenin Tanımı, Standartları Ve Değerleme Yaklaşımları İle Bunların Seçilme Nedenleri</b>", stiller['AltBaslik']))
        story.append(Spacer(1, 0.3*cm))

        # 4.6.1
        story.append(self._p("<b>4.6.1. Değerlemenin Tanım ve Kapsamı</b>", ParagraphStyle('AltBaslik2', parent=stiller['Normal'], fontName=self.font_bold, fontSize=10)))
        tanim_text = """Değerleme, bir varlığın ekonomik değerini tahmin etme işlemidir. Gayrimenkul değerlemesi ise bir gayrimenkulün
belirli bir tarihteki muhtemel değerinin bağımsız ve tarafsız olarak takdir edilmesidir."""
        story.append(self._p(tanim_text, stiller['Normal']))
        story.append(Spacer(1, 0.3*cm))

        # 4.6.2
        story.append(self._p("<b>4.6.2. Değer Standartları (Esasları)</b>", ParagraphStyle('AltBaslik2', parent=stiller['Normal'], fontName=self.font_bold, fontSize=10)))
        standart_text = """Bu değerleme çalışması Uluslararası Değerleme Standartları (IVS) ve Türkiye Değerleme Uzmanları Birliği (TDUB)
standartları çerçevesinde gerçekleştirilmiştir."""
        story.append(self._p(standart_text, stiller['Normal']))
        story.append(Spacer(1, 0.3*cm))

        # 4.6.3
        story.append(self._p("<b>4.6.3. Piyasa Değeri</b>", ParagraphStyle('AltBaslik2', parent=stiller['Normal'], fontName=self.font_bold, fontSize=10)))
        piyasa_text = """Piyasa değeri, bir varlığın değerleme tarihinde, istekli bir alıcı ile istekli bir satıcı arasında,
her ikisinin de bilgili, basiretli ve zorlama altında olmadan gerçekleştirdiği tarafsız bir işlemde el değiştirmesi
gereken tahmini tutardır."""
        story.append(self._p(piyasa_text, stiller['Normal']))
        story.append(Spacer(1, 0.3*cm))

        # 4.6.4
        story.append(self._p("<b>4.6.4. Piyasa Değeri (Satışların Karşılaştırılması) Yaklaşımı</b>", ParagraphStyle('AltBaslik2', parent=stiller['Normal'], fontName=self.font_bold, fontSize=10)))
        karsilastirma_text = """Bu yaklaşımda, değerlenecek gayrimenkulle benzer özelliklere sahip, yakın zamanda satılmış
emsal gayrimenkullerin satış fiyatları karşılaştırılarak değer tahmini yapılır."""
        story.append(self._p(karsilastirma_text, stiller['Normal']))
        story.append(Spacer(1, 0.3*cm))

        # 4.6.5
        story.append(self._p("<b>4.6.5. Maliyet (Yeniden İnşa Etme) Yaklaşımı</b>", ParagraphStyle('AltBaslik2', parent=stiller['Normal'], fontName=self.font_bold, fontSize=10)))
        maliyet_text = """Bu yaklaşımda, binanın yeniden inşa maliyeti hesaplanır ve amortisman düşülerek mevcut değeri
belirlenir. Arsa değeri ayrıca hesaplanarak toplam değer bulunur."""
        story.append(self._p(maliyet_text, stiller['Normal']))
        story.append(Spacer(1, 0.3*cm))

        # 4.6.6
        story.append(self._p("<b>4.6.6. Gelir Kapitalizasyon Yaklaşımı</b>", ParagraphStyle('AltBaslik2', parent=stiller['Normal'], fontName=self.font_bold, fontSize=10)))
        gelir_text = """Bu yaklaşımda, gayrimenkulün gelecekte elde edeceği gelir akışları bugünkü değere indirgen erek
gayrimenkulün değeri hesaplanır."""
        story.append(self._p(gelir_text, stiller['Normal']))
        story.append(Spacer(1, 0.3*cm))

        # 4.6.7
        story.append(self._p("<b>4.6.7. Uygulanan Değerleme Yaklaşımı</b>", ParagraphStyle('AltBaslik2', parent=stiller['Normal'], fontName=self.font_bold, fontSize=10)))
        uygulanan_text = """Bu değerleme çalışmasında, değerleme konusu gayrimenkulün niteliği ve piyasa koşulları dikkate
alınarak ağırlıklı olarak <b>Piyasa Değeri (Satışların Karşılaştırılması) Yaklaşımı</b> kullanılmıştır. Emsal satış
örnekleri incelenerek ve gerekli düzeltmeler yapılarak değer tahmini gerçekleştirilmiştir."""
        story.append(self._p(uygulanan_text, stiller['Normal']))
        story.append(PageBreak())

    def degerleme_faktorleri_olustur(self, story, veri, stiller):
        """4.7-4.12 Bölümleri"""

        # 4.7
        story.append(self._p("<b>4.7. Değerleme İşlemini Etkileyen Faktörler</b>", stiller['AltBaslik']))
        faktor_text = """Değerleme işlemini etkileyen başlıca faktörler:
• Gayrimenkulün konumu ve çevre özellikleri
• Ulaşım imkanları ve altyapı durumu
• İmar durumu ve yapılaşma hakları
• Gayrimenkulün fiziksel özellikleri (yaş, bakım durumu, kalite)
• Piyasa koşulları ve ekonomik durum
• Benzer gayrimenkullerin satış ve kira değerleri"""
        story.append(self._p(faktor_text, stiller['Normal']))
        story.append(Spacer(1, 0.5*cm))

        # 4.8
        story.append(self._p("<b>4.8. Değerlemede Kabul Edilen Varsayımlar</b>", stiller['AltBaslik']))
        varsayim_text = """Bu değerleme çalışmasında aşağıdaki varsayımlar kabul edilmiştir:
• Tapu kayıtlarının doğru olduğu
• Gayrimenkulün hukuki olarak temiz olduğu ve herhangi bir ipotek, haciz veya takyidat bulunmadığı
• İmar durumu belgesinin geçerli olduğu
• Yapının ruhsat ve iskan belgesine sahip olduğu
• Gayrimenkulün normal piyasa koşullarında satılabileceği"""
        story.append(self._p(varsayim_text, stiller['Normal']))
        story.append(Spacer(1, 0.5*cm))

        # 4.9
        story.append(self._p("<b>4.9. En Etkin ve En Verimli Kullanım Analizi</b>", stiller['AltBaslik']))
        verimli_text = """Değerleme konusu gayrimenkulün en etkin ve en verimli kullanımı mevcut durumu olan
<b>mesken (konut)</b> kullanımıdır. Gayrimenkulün konumu, imar durumu ve fiziksel özellikleri dikkate alındığında,
mevcut kullanım şeklinin devam ettirilmesi en uygun seçenektir."""
        story.append(self._p(verimli_text, stiller['Normal']))
        story.append(Spacer(1, 0.5*cm))

        # 4.10
        story.append(self._p("<b>4.10. Piyasa Yaklaşımı, Benzer Satış Örnekleri ve Bunların Karşılaştırılması</b>", stiller['AltBaslik']))

        # Emsal özetini kullan
        emsal_ozeti = veri.get('_emsal_ozeti', {})

        if emsal_ozeti and emsal_ozeti.get('emsal_sayisi', 0) > 0:
            # Dinamik emsal metni
            min_fiyat = emsal_ozeti.get('min_fiyat')
            max_fiyat = emsal_ozeti.get('max_fiyat')
            ort_fiyat = emsal_ozeti.get('ortalama_fiyat')

            if min_fiyat and max_fiyat:
                emsal_text = f"""Değerleme konusu gayrimenkul için benzer özelliklere sahip {emsal_ozeti['emsal_sayisi']} adet emsal satış örneği araştırılmış ve
incelenmiştir. Aynı mahalle ve çevrede, benzer büyüklük ve özelliklere sahip konutların m² satış fiyatları
{self._format_tl(min_fiyat)}/m² - {self._format_tl(max_fiyat)}/m² aralığında tespit edilmiştir.

Değerleme konusu gayrimenkulün özellikleri (kat, konumu, yaşı, durumu) dikkate alınarak gerekli düzeltmeler
yapılmış ve birim m² değeri <b>{self._format_tl(ort_fiyat)}/m²</b> olarak belirlenmiştir."""
            else:
                emsal_text = f"""Değerleme konusu gayrimenkul için {emsal_ozeti['emsal_sayisi']} adet emsal satış örneği incelenmiştir.
Emsal analizi sonucunda gayrimenkulün piyasa değeri tespit edilmiştir."""
        else:
            # Eğer emsal yoksa varsayılan metin
            emsal_text = """Değerleme konusu gayrimenkul için benzer özelliklere sahip emsal satış örnekleri araştırılmış ve
incelenmiştir. Aynı mahalle ve çevrede, benzer büyüklük ve özelliklere sahip konutların piyasa değerleri
analiz edilmiştir.

Değerleme konusu gayrimenkulün özellikleri (kat, konumu, yaşı, durumu) dikkate alınarak gerekli düzeltmeler
yapılmış ve piyasa değeri belirlenmiştir."""

        story.append(self._p(emsal_text, stiller['Normal']))
        story.append(Spacer(1, 0.5*cm))

        # 4.11
        story.append(self._p("<b>4.11. Proje Geliştirme & Gelir Yaklaşımı</b>", stiller['AltBaslik']))
        gelir_yak_text = """Bu değerleme çalışmasında gelir yaklaşımı ikincil olarak değerlendirilmiştir. Benzer konutların
aylık kira değerleri incelendiğinde, değerleme konusu gayrimenkulün aylık kira değerinin yaklaşık 15.000 TL - 18.000 TL
aralığında olabileceği tahmin edilmektedir."""
        story.append(self._p(gelir_yak_text, stiller['Normal']))
        story.append(Spacer(1, 0.5*cm))

        # 4.12
        story.append(self._p("<b>4.12. Maliyet Oluşumları Yaklaşımı</b>", stiller['AltBaslik']))
        maliyet_yak_text = """Maliyet yaklaşımında, arsa değeri ve yeniden inşa maliyeti ayrı ayrı hesaplanmaktadır.
Ancak bu yaklaşım, mevcut yapılar için piyasa değeri ve gelir yaklaşımları kadar güvenilir sonuçlar vermemektedir.
Bu nedenle bu yaklaşım destekleyici bir yöntem olarak kullanılmıştır."""
        story.append(self._p(maliyet_yak_text, stiller['Normal']))
        story.append(PageBreak())

    def ekler_olustur(self, story, veri, stiller):
        """6. EKLER - Fotoğraflar ve Belgeler"""

        story.append(Spacer(1, 0.5*cm))
        story.append(self._p("<b>6. EKLER</b>", stiller['BolumBaslik']))
        story.append(Spacer(1, 0.3*cm))

        # Taşınmaza Ait Fotoğraflar
        if veri.get('fotograflar'):
            story.append(self._p("<b>Taşınmaza Ait Fotoğraflar ve Resmi Belgeler</b>", stiller['AltBaslik']))
            story.append(Spacer(1, 0.3*cm))

            for i, foto in enumerate(veri['fotograflar']):
                try:
                    img = Image(foto, width=16*cm, height=12*cm, kind='proportional')
                    story.append(img)
                    story.append(Spacer(1, 0.5*cm))

                    if (i + 1) % 2 == 0:
                        story.append(PageBreak())
                except:
                    pass

    def rapor_olustur(self, veri: dict, takbis_verisi: dict = None) -> str:
        """
        AREA formatında TAM KAPSAMLI rapor oluştur

        Args:
            veri: Rapor verileri
            takbis_verisi: TAKBIS işleyiciden gelen tam veri

        Returns:
            Oluşturulan PDF yolu
        """

        # Bağımsız bölüm no'yu veri'ye ekle (eğer yoksa)
        if 'bagimsiz_bolum_no' not in veri:
            veri['bagimsiz_bolum_no'] = '10'  # Default

        # Dosya adı
        tarih = datetime.now().strftime("%Y%m%d_%H%M%S")
        dosya_adi = f"area_rapor_{tarih}.pdf"
        dosya_yolu = self.output_dir / dosya_adi

        # PDF oluştur
        doc = SimpleDocTemplate(
            str(dosya_yolu),
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2.5*cm,
            bottomMargin=2.5*cm
        )

        # Stiller
        stiller = self.stil_olustur()

        # İçerik
        story = []

        # Kapak sayfası
        self.kapak_sayfasi_olustur(story, veri, stiller)

        # İçindekiler
        self.icindekiler_olustur(story, stiller)

        # 1. Rapor Özeti
        self.rapor_ozeti_olustur(story, veri, stiller)

        # 2. Rapor Bilgileri
        self.rapor_bilgileri_olustur(story, veri, stiller)

        # 3. Şirket ve Müşteri Bilgileri
        self.sirket_bilgileri_olustur(story, veri, stiller)

        # 4.1. Gayrimenkulün Yeri
        self.gayrimenkul_yeri_olustur(story, veri, stiller)

        # 4.2 Tapu Bilgileri (TAKBIS TAM VERİ)
        self.tapu_bilgileri_olustur(story, veri, stiller, takbis_verisi)

        # 4.3. Resmi Kurum İncelemesi
        self.resmi_kurum_incelemesi_olustur(story, veri, stiller)

        # 4.4. Gayrimenkulün Özellikleri
        self.gayrimenkul_ozellikleri_olustur(story, veri, stiller)

        # 4.5. Bağımsız Bölüm
        self.bagimsiz_bolum_olustur(story, veri, stiller)

        # 4.6. Değerleme Tanımı ve Yaklaşımları
        self.degerleme_tanimi_olustur(story, veri, stiller)

        # 4.7-4.12. Diğer Değerleme Bölümleri
        self.degerleme_faktorleri_olustur(story, veri, stiller)

        # 5. Sonuç
        self.sonuc_olustur(story, veri, stiller)

        # 6. Ekler
        self.ekler_olustur(story, veri, stiller)

        # PDF oluştur
        doc.build(story, onFirstPage=self.header_footer, onLaterPages=self.header_footer)

        print(f"✅ AREA formatında rapor oluşturuldu: {dosya_yolu}")
        return str(dosya_yolu)
