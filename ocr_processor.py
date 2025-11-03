"""
OCR + AI Doğrulama Sistemi
Önce OCR ile metin çıkarılır, sonra AI ile doğrulanır
"""

import os
from pathlib import Path
from typing import Dict, List
import json

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("⚠️ Uyarı: pytesseract yüklü değil. OCR devre dışı.")

import anthropic


class OCRProcessor:
    """OCR + AI Doğrulama İşleyicisi"""
    
    def __init__(self):
        # API anahtarı direkt olarak sisteme entegre edildi
        from config import get_anthropic_api_key
        self.api_key = get_anthropic_api_key()

        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        
        # Tesseract yolu (Windows için)
        if TESSERACT_AVAILABLE:
            tesseract_yolu = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            if os.path.exists(tesseract_yolu):
                pytesseract.pytesseract.tesseract_cmd = tesseract_yolu
    
    def ocr_calistir(self, dosya_yolu: str) -> str:
        """
        OCR ile metin çıkar
        """
        if not TESSERACT_AVAILABLE:
            return "[OCR kullanılamıyor - pytesseract yüklü değil]"
        
        try:
            img = Image.open(dosya_yolu)
            
            # Türkçe + İngilizce OCR
            metin = pytesseract.image_to_string(img, lang='tur+eng')
            
            return metin.strip()
            
        except Exception as e:
            return f"[OCR hatası: {str(e)}]"
    
    def ai_dogrula_ve_duzenle(self, ocr_metni: str, dosya_tipi: str = "Genel Belge") -> Dict:
        """
        OCR metnini AI ile doğrula ve düzenle
        
        Args:
            ocr_metni: OCR'dan çıkan ham metin
            dosya_tipi: Belge türü (Tapu, İmar, vb.)
        
        Returns:
            Düzeltilmiş ve yapılandırılmış veri
        """
        
        if not self.api_key:
            return {"ham_metin": ocr_metni, "hata": "AI doğrulama yapılamadı - API key yok"}
        
        prompt = f"""
Sen bir belge okuma ve düzeltme uzmanısın. Sana OCR ile okunmuş bir metin verildi.
Bu metin "{dosya_tipi}" türünde bir belgeden geliyor.

OCR METNİ:
{ocr_metni}

GÖREV:
1. OCR hatalarını düzelt (yanlış okunan harfler, eksik karakterler)
2. Metni anlamlı hale getir
3. Önemli bilgileri yapılandır

Özellikle şunlara dikkat et:
- Mahalle/köy isimleri doğru olmalı
- Sayılar tam ve doğru olmalı
- Adres bilgileri eksiksiz olmalı

ÇIKTI:
JSON formatında döndür:
{{
    "duzeltilmis_metin": "Düzeltilmiş tam metin",
    "onemli_bilgiler": {{
        "adres": "...",
        "mahalle": "...",
        "ada": "...",
        "parsel": "...",
        "diger": {{}}
    }},
    "duzeltme_notlari": "Yapılan düzeltmeler"
}}

SADECE JSON döndür.
"""
        
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2048,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            yanit = message.content[0].text
            
            # JSON çıkar
            import re
            json_match = re.search(r'\{[\s\S]*\}', yanit)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"ham_metin": ocr_metni, "ai_yanit": yanit}
                
        except Exception as e:
            return {"ham_metin": ocr_metni, "hata": f"AI doğrulama hatası: {str(e)}"}
    
    def dosya_isle(self, dosya_yolu: str, dosya_tipi: str = "Genel Belge") -> Dict:
        """
        Tam işlem: OCR + AI Doğrulama
        
        Returns:
            {
                'ocr_metin': str,
                'ai_duzeltme': dict,
                'basarili': bool
            }
        """
        
        print(f"\n📄 OCR işleniyor: {Path(dosya_yolu).name}")
        
        # 1. OCR ile metin çıkar
        ocr_metin = self.ocr_calistir(dosya_yolu)
        print(f"  ✅ OCR tamamlandı ({len(ocr_metin)} karakter)")
        
        # 2. AI ile doğrula
        print(f"  🤖 AI doğrulama yapılıyor...")
        ai_sonuc = self.ai_dogrula_ve_duzenle(ocr_metin, dosya_tipi)
        print(f"  ✅ AI doğrulama tamamlandı")
        
        return {
            'ocr_metin': ocr_metin,
            'ai_duzeltme': ai_sonuc,
            'basarili': 'hata' not in ai_sonuc
        }


def tesseract_yuklu_mu() -> bool:
    """Tesseract OCR yüklü mü kontrol et"""
    return TESSERACT_AVAILABLE


def tesseract_kurulum_yardimi():
    """Tesseract kurulum talimatları"""
    return """
    📋 TESSERACT OCR KURULUMU

    1. İndirin:
       https://github.com/UB-Mannheim/tesseract/wiki
       
    2. Yükleyin:
       Varsayılan konuma: C:\\Program Files\\Tesseract-OCR\\
       
    3. Türkçe dil paketi:
       Kurulum sırasında "Additional language data" seçeneğinde
       Turkish'i seçin
       
    4. Python paketi:
       pip install pytesseract pillow
       
    5. Programı yeniden başlatın
    """
