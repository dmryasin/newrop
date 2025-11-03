# -*- coding: utf-8 -*-
"""
TAKBIS Belge İşleyici
TAKBIS belgelerindeki tüm bilgileri çıkaran ve yapılandıran modül
"""

from pathlib import Path
from typing import Dict, List, Any
import json
import base64
import anthropic
import os


class TAKBISIsleyici:
    """TAKBIS belgelerinden tam veri çıkarımı yapan sınıf"""

    def __init__(self):
        """API anahtarı direkt olarak sisteme entegre edildi"""
        from config import get_anthropic_api_key
        self.api_key = get_anthropic_api_key()

        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)

    def takbis_isle(self, dosya_yolu: str) -> Dict[str, Any]:
        """
        TAKBIS belgesindeki TÜM bilgileri çıkar

        Args:
            dosya_yolu: TAKBIS belgesi yolu (PDF veya görsel)

        Returns:
            Dict içinde tam TAKBIS verileri
        """

        if not self.api_key:
            return {"hata": "API key bulunamadı"}

        # Dosyayı base64'e çevir
        with open(dosya_yolu, 'rb') as f:
            dosya_bytes = f.read()
            dosya_base64 = base64.standard_b64encode(dosya_bytes).decode('utf-8')

        # Dosya uzantısını belirle
        dosya_adi = Path(dosya_yolu).name.lower()
        if dosya_adi.endswith('.pdf'):
            media_type = "application/pdf"
        elif dosya_adi.endswith(('.jpg', '.jpeg')):
            media_type = "image/jpeg"
        elif dosya_adi.endswith('.png'):
            media_type = "image/png"
        else:
            media_type = "image/jpeg"

        prompt = """
Sen bir TAKBIS (Tapu Kadastro Bilgi Sistemi) belgesi okuma uzmanısın.

GÖREV: Bu TAKBIS belgesindeki TÜM bilgileri hiçbir eksik olmadan çıkar.

TAKBIS belgesi birden fazla sayfadan oluşuyorsa, HER SAYFADAKI TÜM BİLGİLERİ çıkar.

ÖNEMLİ KURALLAR:
1. Her satırdaki her bilgiyi kaydet
2. Tüm tabloları tam olarak çıkar
3. Tüm notları ve açıklamaları kaydet
4. Hiçbir bilgiyi atlama
5. Boş alanları "-" olarak işaretle
6. Sayısal değerleri olduğu gibi yaz

ÇIKARILACAK BİLGİLER:
- İL, İLÇE, MAHALLE bilgileri
- ANA TAŞINMAZ NİTELİĞİ (Yüzölçümü, Tapu Tarihi, vb.)
- BİR BODRUM BİR ZEMİN DÖRT NORMAL KATLI (1) NUMARALI KATI APARTMAN bilgisi varsa çıkar
- MEVKİİ, PAFTA NO, ADA NO, PARSEL NO
- B.BÖLÜM KAT NO, B.BÖLÜM NO, B.BÖLÜM NİTELİK
- TAŞINMAZ ID, CİLT NO, SAHFE NO
- MALIK/HİSSE/EDİNME SEBEBİ bilgileri
- SERMAYE PAZAR DEĞERİ tablosu
- BEYAN bölümü (tarihli yönetim planı bilgileri)
- ŞERHLer, İPOTEKLer, SATILABILIR, KAT İRTİFAKI, DEVRE MÜLK bilgileri
- TAKBIS sisteminden alınan tüm ek bilgiler

JSON formatında döndür:
{
    "genel_bilgiler": {
        "il": "",
        "ilce": "",
        "mahalle": "",
        "mevkii": "",
        "pafta_no": "",
        "ada_no": "",
        "parsel_no": "",
        "yuzolcumu": "",
        "tapu_tarihi": ""
    },
    "ana_tasinmaz": {
        "nitelik": "",
        "yuzolcumu": "",
        "cilt_no": "",
        "sahife_no": "",
        "yevmiye_no": "",
        "tasinmaz_id": ""
    },
    "bagimsiz_bolum": {
        "kat_no": "",
        "bolum_no": "",
        "nitelik": "",
        "tasinmaz_id": "",
        "bagimsiz_bolum_arsa_payi": "",
        "bagimsiz_bolum_nitelik": ""
    },
    "malik_bilgileri": [
        {
            "malik_adi": "",
            "hisse": "",
            "edinme_sebebi": ""
        }
    ],
    "sermaye_pazar": {
        "1_1": "",
        "hisse": "",
        "edinme_sebebi": ""
    },
    "beyan": {
        "tarih": "",
        "yonetim_plani": "",
        "madde": "",
        "fikra": "",
        "bent": "",
        "aciklama": ""
    },
    "kisitlamalar": {
        "serh": "",
        "ipotek": "",
        "satilabilir": "",
        "kat_irtifaki": "",
        "devre_mulk": ""
    },
    "takbis_ek_bilgiler": {
        "tum_notlar": [],
        "diger_bilgiler": {}
    },
    "ham_metin": "Belgeden okunan tam metin"
}

SADECE JSON döndür, başka hiçbir açıklama ekleme.
"""

        try:
            # AI'ya gönder
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=8192,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": dosya_base64
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )

            # Yanıtı al
            yanit = message.content[0].text

            # JSON'u çıkar
            import re
            json_match = re.search(r'\{[\s\S]*\}', yanit)
            if json_match:
                takbis_data = json.loads(json_match.group())
                return takbis_data
            else:
                return {"hata": "JSON çıkarılamadı", "ham_yanit": yanit}

        except Exception as e:
            return {"hata": f"TAKBIS işleme hatası: {str(e)}"}

    def coklu_sayfa_takbis_isle(self, dosya_yollari: List[str]) -> Dict[str, Any]:
        """
        Çok sayfalı TAKBIS belgelerini birleştirerek işle

        Args:
            dosya_yollari: TAKBIS sayfalarının yolları

        Returns:
            Birleştirilmiş TAKBIS verileri
        """

        tum_veriler = []

        for dosya in dosya_yollari:
            print(f"📄 TAKBIS sayfası işleniyor: {Path(dosya).name}")
            veri = self.takbis_isle(dosya)
            tum_veriler.append(veri)

        # Verileri birleştir
        birlesik_veri = self._verileri_birlestir(tum_veriler)

        return birlesik_veri

    def _verileri_birlestir(self, veri_listesi: List[Dict]) -> Dict:
        """Çoklu sayfa verilerini akıllıca birleştir"""

        if not veri_listesi:
            return {}

        # İlk veriyi temel al
        birlesik = veri_listesi[0].copy()

        # Diğer verileri üzerine ekle
        for veri in veri_listesi[1:]:
            if "hata" in veri:
                continue

            # Boş olmayan alanları güncelle
            for anahtar, deger in veri.items():
                if isinstance(deger, dict):
                    if anahtar not in birlesik:
                        birlesik[anahtar] = {}
                    for alt_anahtar, alt_deger in deger.items():
                        if alt_deger and alt_deger != "-":
                            birlesik[anahtar][alt_anahtar] = alt_deger
                elif isinstance(deger, list):
                    if anahtar not in birlesik:
                        birlesik[anahtar] = []
                    birlesik[anahtar].extend(deger)
                else:
                    if deger and deger != "-":
                        birlesik[anahtar] = deger

        return birlesik


if __name__ == "__main__":
    # Test kodu
    print("TAKBIS İşleyici Test")
    print("=" * 50)

    isleyici = TAKBISIsleyici()

    # Test dosyası varsa
    test_dosya = Path("test_takbis.pdf")
    if test_dosya.exists():
        sonuc = isleyici.takbis_isle(str(test_dosya))
        print(json.dumps(sonuc, indent=2, ensure_ascii=False))
    else:
        print("Test dosyası bulunamadı: test_takbis.pdf")
