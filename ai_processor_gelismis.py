"""
Geliştirilmiş AI Belge İşleyici
Kat planı, m² tablosu ve enerji belgesi analizi dahil
"""

import os
import json
from pathlib import Path
import base64
from typing import List, Dict
import anthropic
from PIL import Image
import io
import re


class GelismisAIBelgeIsleyici:
    """Geliştirilmiş AI ile belge işleme - Kat planı, m² tablosu analizi dahil"""

    def __init__(self):
        # API anahtarı direkt olarak sisteme entegre edildi
        from config import get_anthropic_api_key
        self.api_key = get_anthropic_api_key()

        if not self.api_key:
            raise ValueError("API anahtarı bulunamadı!")

        self.client = anthropic.Anthropic(api_key=self.api_key)

    def resim_base64(self, dosya_yolu: str) -> str:
        """Resmi optimize edip base64'e çevir"""
        try:
            img = Image.open(dosya_yolu)
            
            # RGBA ise RGB'ye çevir
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if img.mode in ('RGBA', 'LA'):
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img)
                img = background
            
            # RGB'ye çevir (emin olmak için)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Boyutu küçült
            max_dimension = 1600
            img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
            
            # JPEG olarak kaydet
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=75, optimize=True)
            buffer.seek(0)
            
            return base64.standard_b64encode(buffer.getvalue()).decode('utf-8')
            
        except Exception as e:
            print(f"❌ Resim optimizasyon hatası ({Path(dosya_yolu).name}): {e}")
            raise Exception(f"Resim işlenemedi: {Path(dosya_yolu).name}")

    def pdf_base64(self, dosya_yolu: str, max_boyut_mb: float = 5.0) -> str:
        """PDF'i base64'e çevir - boyut kontrolü ile"""
        dosya_boyutu = os.path.getsize(dosya_yolu) / (1024 * 1024)
        
        if dosya_boyutu > max_boyut_mb:
            raise ValueError(f"PDF çok büyük ({dosya_boyutu:.1f}MB). Max {max_boyut_mb}MB olmalı.")
        
        with open(dosya_yolu, 'rb') as f:
            return base64.standard_b64encode(f.read()).decode('utf-8')

    def medya_turu(self, dosya_yolu: str) -> str:
        """Medya türünü belirle"""
        uzanti = Path(dosya_yolu).suffix.lower()
        return {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.pdf': 'application/pdf'
        }.get(uzanti, 'application/octet-stream')
    
    def _ocr_metinlerini_formatla(self, ocr_metinleri: Dict) -> str:
        """OCR metinlerini formatlı string olarak döndür"""
        if not ocr_metinleri:
            return ""
        
        formatli = []
        for dosya, metin in ocr_metinleri.items():
            formatli.append(f"\n📄 DOSYA: {dosya}")
            formatli.append("-" * 40)
            formatli.append(metin[:1000])  # İlk 1000 karakter
            if len(metin) > 1000:
                formatli.append("... (devamı var)")
            formatli.append("")  # Boş satır
        
        return "\n".join(formatli)

    def belgeleri_analiz_et(self, belgeler: List[Dict], ocr_kullan: bool = True) -> Dict:
        """
        KAPSAMLI BELGE ANALİZİ - OCR İLE GÜCLENDIRİLMİŞ
        
        Args:
            belgeler: Belge listesi
            ocr_kullan: OCR kullanılsın mı? (varsayılan: True)
        
        Returns:
            Çıkarılan veri dict
        """
        
        # Belge sayısını sınırla (API limiti için)
        MAX_BELGELER = 10
        if len(belgeler) > MAX_BELGELER:
            print(f"\n⚠️ Uyarı: {len(belgeler)} belge var, ilk {MAX_BELGELER} analiz edilecek.")
            belgeler = belgeler[:MAX_BELGELER]
        
        # OCR TARAMASı (eğer aktifse)
        ocr_metinleri = {}
        if ocr_kullan:
            try:
                from ocr_processor import OCRIsleyici
                ocr = OCRIsleyici()
                
                if ocr.ocr_reader:  # OCR başarıyla yüklendiyse
                    ocr_sonuclari = ocr.belgeleri_ocr_tara(belgeler)
                    
                    for sonuc in ocr_sonuclari:
                        if sonuc['basarili']:
                            ocr_metinleri[sonuc['dosya']] = sonuc['ocr_metin']
                else:
                    print("⚠️ OCR kullanılamadı, sadece AI görsel analizi yapılacak")
                    
            except Exception as e:
                print(f"⚠️ OCR hatası: {str(e)[:100]}")
                print("Sadece AI görsel analizi yapılacak")

        ocr_bilgisi = self._ocr_metinlerini_formatla(ocr_metinleri) if ocr_metinleri else '⚠️ OCR metni yok, sadece görsel analiz yapılacak'

        prompt = f"""
Sen SPK onaylı gayrimenkul değerleme uzmanısın. Verilen belgeleri ÇOK DİKKATLE analiz et.

{'='*60}
🔍 OCR İLE ÖNDEN OKUNAN METİNLER:
{'='*60}

{ocr_bilgisi}

{'='*60}

🔴 KRİTİK KURALLAR:
1. MAHALLE/KÖY adını YANLIŞ OKUMA! Çok dikkatli oku, harf harf kontrol et
2. KAT PLANI varsa:
   - DAİRE NUMARASINI tespit et (projede yazıyor, dikkatli bak!)
   - Planda verilen ÖLÇÜ KOTLARINI oku (örn: 3.50, 4.20 gibi metre cinsinden)
   - Her odanın boyutlarını ölç (genişlik x uzunluk)
   - Her odanın m²'sini HESAPLA (genişlik x uzunluk = m²)
   - Toplam net alanı hesapla (tüm odaların m²'lerini topla)
   - Oda sayısını say (yatak odası + salon = X+1 formatında)
3. m² TABLOSU varsa: Tüm alanları buradan al (brüt, net, kat alanları)
4. ENERJİ KİMLİK BELGESİ varsa: Sınıf, tüketim, ısıtma sistemi vb. TÜM bilgileri çıkar
5. Rakamları tam oku - virgül/nokta karışıklığı yapma
6. Aynı bilgi birden fazla yerde varsa EN GÜVENİLİR kaynağı seç

📋 ÇIKARILACAK BİLGİLER (JSON):

```json
{{
  "adres": "Tam adres",
  "il": "İl",
  "ilce": "İlçe",
  "mahalle": "MAHALLE ADI - YANLIŞ OKUMA YASAK!",
  "sokak": "Sokak/Cadde",
  "bina_no": "Bina no",
  "daire_no": "Daire no",
  "posta_kodu": "Posta kodu",

  "ada": "Ada no",
  "parsel": "Parsel no",
  "nitelik": "Nitelik",
  "tapu_turu": "Tapu türü",
  "malik": "Malik adı",
  "hisse": "Hisse oranı",

  "arsa_alani": "Arsa alanı m²",
  "brut_alan": "Brüt alan m² (m² tablosundan)",
  "net_alan": "Net alan m² (KAT PLANINDAN HESAPLA veya m² tablosundan)",
  "kat_sayisi": "Toplam kat",
  "bulundugu_kat": "Bulunduğu kat",
  "oda_sayisi": "Oda sayısı (KAT PLANINDAN SAY: yatak odası + salon = X+1)",
  "bina_yasi": "Bina yaşı/yıl",

  "kat_plani_mevcut": "Evet/Hayır",
  "kat_plani_daire_no": "DAİRE NUMARASI (plandan oku!)",
  "kat_plani_olculer": {{"salon": "3.50x4.20", "yatak_odasi_1": "3.00x3.50"}},
  "kat_plani_odalar": ["Salon: 3.50x4.20 = 14.70 m²", "Yatak odası 1: 3.00x3.50 = 10.50 m²"],
  "kat_plani_hesaplamalar": ["Salon: 3.50 x 4.20 = 14.70 m²", "Yatak 1: 3.00 x 3.50 = 10.50 m²"],
  "kat_plani_toplam_net_m2": "Hesaplanan toplam net m² (odaların toplamı)",
  "kat_plani_oda_sayisi": "Sayılan oda sayısı (örn: 2+1)",

  "m2_tablosu_mevcut": "Evet/Hayır",
  "m2_tablosu_brut": "Brüt m²",
  "m2_tablosu_net": "Net m²",
  "m2_tablosu_ortak_alan": "Ortak alan m²",

  "enerji_belgesi_mevcut": "Evet/Hayır",
  "enerji_sinifi": "Enerji sınıfı (A+, A, B, C, D, E, F, G)",
  "enerji_tuketimi": "Yıllık enerji tüketimi (kWh/yıl)",
  "enerji_co2_salimi": "CO2 salımı (kg/yıl)",
  "isitma_tipi": "Isıtma sistemi",
  "sogutma_tipi": "Soğutma sistemi",

  "imar_durumu": "İmar durumu",
  "imar_emsal": "Emsal",
  "taks": "TAKS",
  "kaks": "KAKS",

  "kullanim_amaci": "Kullanım amacı",
  "cephe_yonu": "Cephe yönü",
  "diger_bilgiler": "Diğer önemli notlar"
}}
```

🎯 ÖNCELİK SIRASI:
1. Mahalle/adres: Harf harf kontrol et
2. Kat planı varsa:
   a) DAİRE NUMARASINI bul (genelde plana yazılmıştır)
   b) ÖLÇÜ KOTLARINI oku (3.50, 4.20 gibi metre değerleri)
   c) Her oda için: genişlik x uzunluk ile m² hesapla
   d) Hesaplamaları göster: "Salon: 3.50 x 4.20 = 14.70 m²"
   e) Tüm odaları topla
3. m² tablosu varsa: Alan bilgilerini buradan al
4. Enerji belgesi varsa: Tüm teknik detayları çıkar

⚠️ ÖNEMLİ: Kat planında ölçü kotları varsa MUTLAKA oku ve hesapla!
Örnek: Eğer planda "3.50" ve "4.20" yazıyorsa → 3.50 x 4.20 = 14.70 m²

SADECE JSON döndür. Yoksa null yaz, tahmin yapma!
"""

        # Belgeleri hazırla
        content = []
        toplam_boyut = 0
        MAX_TOPLAM_MB = 15  # Toplam max boyut
        
        for idx, belge in enumerate(belgeler):
            dosya_yolu = belge["yol"]
            uzanti = Path(dosya_yolu).suffix.lower()
            
            try:
                dosya_boyutu_mb = os.path.getsize(dosya_yolu) / (1024 * 1024)
                
                if uzanti in ['.jpg', '.jpeg', '.png']:
                    print(f"  [{idx+1}/{len(belgeler)}] {Path(dosya_yolu).name} işleniyor...")
                    base64_data = self.resim_base64(dosya_yolu)
                    # Tüm görseller JPEG'e çevriliyor, media type her zaman image/jpeg
                    content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",  # Her zaman JPEG
                            "data": base64_data
                        }
                    })
                    toplam_boyut += dosya_boyutu_mb
                    
                elif uzanti == '.pdf':
                    print(f"  [{idx+1}/{len(belgeler)}] {Path(dosya_yolu).name} işleniyor (PDF)...")
                    
                    if dosya_boyutu_mb > 5:
                        print(f"    ⚠️ PDF çok büyük ({dosya_boyutu_mb:.1f}MB), atlanıyor...")
                        continue
                        
                    base64_data = self.pdf_base64(dosya_yolu)
                    content.append({
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": base64_data
                        }
                    })
                    toplam_boyut += dosya_boyutu_mb
                
                # Toplam boyut kontrolü
                if toplam_boyut > MAX_TOPLAM_MB:
                    print(f"\n⚠️ Toplam dosya boyutu {toplam_boyut:.1f}MB'yi geçti. Kalan dosyalar atlanıyor.")
                    break
                    
            except Exception as e:
                print(f"    ❌ Hata: {Path(dosya_yolu).name} - {str(e)[:50]}")
                continue

        content.append({"type": "text", "text": prompt})
        
        if len(content) == 1:  # Sadece prompt var, hiç belge yüklenememiş
            raise Exception("Hiçbir belge işlenemedi. Dosya boyutlarını kontrol edin.")

        # AI'ya gönder
        print(f"\n🤖 AI'ya {len(content)-1} belge gönderiliyor...")
        
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                messages=[{"role": "user", "content": content}]
            )

            yanit = message.content[0].text
            print("✅ AI analizi tamamlandı!\n")
            
            # JSON çıkar
            json_match = re.search(r'\{[\s\S]*\}', yanit)
            if json_match:
                veri = json.loads(json_match.group())
                return veri
            else:
                return {"ham_veri": yanit}

        except Exception as e:
            error_msg = str(e)
            
            # Hata türüne göre kullanıcı dostu mesaj
            if "413" in error_msg or "too_large" in error_msg or "request_too_large" in error_msg:
                raise Exception(
                    "Dosyalar çok büyük! \u00c7özüm:\n"
                    "1. Daha az dosya yükleyin (max 5-6 belge)\n"
                    "2. PDF'leri küçültün (max 5MB)\n"
                    "3. Görselleri düşük çözünürlükte kaydedin"
                )
            elif "rate_limit" in error_msg:
                raise Exception("API limiti aşıldı. Lütfen 1 dakika bekleyip tekrar deneyin.")
            else:
                raise Exception(f"AI analiz hatası: {error_msg[:200]}")
