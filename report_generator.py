from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
from pathlib import Path
import os

class RaporOlusturucu:
    """SPK formatında gayrimenkul değerleme raporu oluşturur"""

    def __init__(self):
        self.output_dir = Path(__file__).parent / "raporlar"
        self.output_dir.mkdir(exist_ok=True)

        # Türkçe karakter desteği için font kaydet (eğer varsa)
        try:
            # Windows için varsayılan Türkçe destekli font
            font_path = "C:/Windows/Fonts/arial.ttf"
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Turkish', font_path))
                self.font_name = 'Turkish'
            else:
                self.font_name = 'Helvetica'
        except:
            self.font_name = 'Helvetica'

    def stil_olustur(self):
        """Rapor için stil şablonları oluştur"""
        styles = getSampleStyleSheet()

        # Başlık stili
        baslik_stil = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName=self.font_name,
            fontSize=16,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=1  # Center
        )

        # Alt başlık stili
        altbaslik_stil = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontName=self.font_name,
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        )

        # Normal metin stili
        metin_stil = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontName=self.font_name,
            fontSize=11,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
            leading=16
        )

        return {
            'baslik': baslik_stil,
            'altbaslik': altbaslik_stil,
            'metin': metin_stil
        }

    def rapor_olustur(self, veri: dict) -> str:
        """
        SPK formatında rapor oluştur

        Args:
            veri: Rapor için gerekli tüm veriler

        Returns:
            Oluşturulan PDF dosyasının yolu
        """

        # Dosya adı oluştur
        tarih = datetime.now().strftime("%Y%m%d_%H%M%S")
        dosya_adi = f"degerleme_raporu_{tarih}.pdf"
        dosya_yolu = self.output_dir / dosya_adi

        # PDF oluştur
        doc = SimpleDocTemplate(
            str(dosya_yolu),
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        # İçerik listesi
        story = []
        stiller = self.stil_olustur()

        # KAPAK SAYFASI
        story.append(Spacer(1, 3*cm))
        story.append(Paragraph("GAYRİMENKUL DEĞERLEME RAPORU", stiller['baslik']))
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(f"SPK Formatında Hazırlanmıştır", stiller['metin']))
        story.append(Spacer(1, 2*cm))

        # Tarih bilgisi
        rapor_tarihi = datetime.now().strftime("%d.%m.%Y")
        story.append(Paragraph(f"Rapor Tarihi: {rapor_tarihi}", stiller['metin']))

        story.append(PageBreak())

        # 1. BÖLÜM: GENEL BİLGİLER
        story.append(Paragraph("1. GENEL BİLGİLER", stiller['altbaslik']))

        genel_bilgiler = [
            ['Gayrimenkulün Adresi:', veri.get('adres', '-')],
            ['İl:', veri.get('il', '-')],
            ['İlçe:', veri.get('ilce', '-')],
            ['Mahalle:', veri.get('mahalle', '-')],
            ['Ada/Parsel:', veri.get('ada_parsel', '-')],
        ]

        tablo = Table(genel_bilgiler, colWidths=[6*cm, 11*cm])
        tablo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
        ]))

        story.append(tablo)
        story.append(Spacer(1, 1*cm))

        # 2. BÖLÜM: TAPU BİLGİLERİ
        story.append(Paragraph("2. TAPU BİLGİLERİ", stiller['altbaslik']))

        tapu_bilgileri = [
            ['Yüzölçümü:', veri.get('yuzolcumu', '-')],
            ['İmar Durumu:', veri.get('imar_durumu', '-')],
            ['Malik/Mülk Sahibi:', veri.get('malik', '-')],
            ['Tapu Türü:', veri.get('tapu_turu', '-')],
        ]

        tablo2 = Table(tapu_bilgileri, colWidths=[6*cm, 11*cm])
        tablo2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
        ]))

        story.append(tablo2)
        story.append(Spacer(1, 1*cm))

        # 3. BÖLÜM: DİĞER BİLGİLER
        if veri.get('diger_bilgiler'):
            story.append(Paragraph("3. DİĞER BİLGİLER", stiller['altbaslik']))
            story.append(Paragraph(veri['diger_bilgiler'], stiller['metin']))
            story.append(Spacer(1, 1*cm))

        # 4. BÖLÜM: FOTOĞRAFLAR
        if veri.get('fotograflar'):
            story.append(PageBreak())
            story.append(Paragraph("4. FOTOĞRAFLAR VE GÖRSELLER", stiller['altbaslik']))
            story.append(Spacer(1, 0.5*cm))

            from ai_processor import AIBelgeIsleyici

            ai_isleyici = AIBelgeIsleyici()

            for idx, foto_yolu in enumerate(veri['fotograflar'], 1):
                try:
                    # Fotoğrafı ekle
                    img = Image(foto_yolu, width=15*cm, height=10*cm, kind='proportional')
                    story.append(img)

                    # AI ile fotoğraf açıklaması oluştur
                    aciklama = ai_isleyici.fotograf_acikla(foto_yolu)
                    story.append(Paragraph(f"<b>Fotoğraf {idx}:</b> {aciklama}", stiller['metin']))
                    story.append(Spacer(1, 1*cm))

                except Exception as e:
                    story.append(Paragraph(f"Fotoğraf {idx} eklenemedi: {str(e)}", stiller['metin']))

        # 5. BÖLÜM: DEĞERLEME METODOLOJİSİ (Şablon)
        story.append(PageBreak())
        story.append(Paragraph("5. DEĞERLEME METODOLOJİSİ", stiller['altbaslik']))
        story.append(Paragraph(
            "Gayrimenkulün değerlemesi SPK'nın belirlediği standartlar ve "
            "uluslararası değerleme standartlarına uygun olarak gerçekleştirilmiştir. "
            "Değerlemede emsal karşılaştırma, gelir kapitalizasyonu ve maliyet yöntemleri "
            "kullanılmıştır.",
            stiller['metin']
        ))
        story.append(Spacer(1, 1*cm))

        # 6. BÖLÜM: SONUÇ VE DEĞERLENDİRME (Şablon)
        story.append(Paragraph("6. SONUÇ VE DEĞERLENDİRME", stiller['altbaslik']))
        story.append(Paragraph(
            "Değerleme çalışması sonucunda elde edilen bulgular ve analizler "
            "doğrultusunda gayrimenkulün değeri belirlenmiştir. Raporda yer alan "
            "tüm bilgiler ve değerlendirmeler değerleme tarihindeki piyasa koşulları "
            "ve mevcut verilere göre hazırlanmıştır.",
            stiller['metin']
        ))

        # PDF'i oluştur
        doc.build(story)

        return str(dosya_yolu)
