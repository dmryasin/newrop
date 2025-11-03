"""
Emsal Karşılaştırma Modülü
Gayrimenkul emsallerini analiz eder ve değerleme yapar
"""

import os
import json
from pathlib import Path
import base64
from typing import List, Dict, Optional
import anthropic
from PIL import Image
import io
import re
import statistics


class EmsalIsleyici:
    """Emsal fotoğraflarını AI ile analiz eder ve değerleme yapar"""

    def __init__(self):
        # API key'i config'den al
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            config_path = Path(__file__).parent / "config.json"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.api_key = config.get("anthropic_api_key")

        if not self.api_key:
            raise ValueError("API key bulunamadı!")

        self.client = anthropic.Anthropic(api_key=self.api_key)

    def _safe_float(self, value):
        if value is None:
            return None
        if isinstance(value, (int, float)):
            try:
                return float(value)
            except (TypeError, ValueError):
                return None
        text_val = str(value).replace('TL', '').replace('tl', '').replace('₺', '').replace(' ', '').replace(' ', ' ').strip()
        match = re.search(r'(\d+[\d.,]*)', text_val)
        if not match:
            return None
        number = match.group(1)
        if ',' in number:
            number = number.replace('.', '')
            number = number.replace(',', '.')
        else:
            if number.count('.') > 1:
                parts = number.split('.')
                number = ''.join(parts[:-1]) + '.' + parts[-1]
        try:
            return float(number)
        except (TypeError, ValueError):
            return None

    def _normalize_emsal(self, emsal):
        if not isinstance(emsal, dict):
            return emsal
        birim = self._safe_float(emsal.get('birim_fiyat_rakam') or emsal.get('duzeltilmis_birim_fiyat') or emsal.get('birim_fiyat'))
        alan = self._safe_float(emsal.get('alan_m2_rakam') or emsal.get('alan_m2'))
        fiyat = self._safe_float(emsal.get('fiyat_rakam') or emsal.get('fiyat'))
        if birim is None and fiyat is not None and alan not in (None, 0):
            birim = fiyat / alan if alan else None
        if birim is not None:
            emsal['birim_fiyat_rakam'] = birim
            emsal['birim_fiyat'] = birim
        if alan is not None:
            emsal['alan_m2_rakam'] = alan
            emsal['alan_m2'] = alan
        if fiyat is not None:
            emsal['fiyat_rakam'] = fiyat
        return emsal

    def _resolve_subject_area(self, gayrimenkul_verisi):
        alan_keys = ['net_alan_rakam', 'net_alan', 'brut_alan_rakam', 'brut_alan', 'arsa_alani_rakam', 'arsa_alani']
        for key in alan_keys:
            sayi = self._safe_float(gayrimenkul_verisi.get(key))
            if sayi:
                return sayi
        return None

    def _hesapla_ortalama_deger(self, gayrimenkul_verisi, emsaller):
        alan = self._resolve_subject_area(gayrimenkul_verisi)
        birimler = [self._safe_float(e.get('birim_fiyat_rakam') or e.get('birim_fiyat')) for e in emsaller if self._safe_float(e.get('birim_fiyat_rakam') or e.get('birim_fiyat'))]
        if alan is None or not birimler:
            return {}
        ort = statistics.mean(birimler)
        minimum = min(birimler)
        maksimum = max(birimler)
        tahmini = ort * alan
        return {
            'ortalama_birim_fiyat': ort,
            'min_birim_fiyat': minimum,
            'max_birim_fiyat': maksimum,
            'tahmini_deger': tahmini,
            'deger_araligi_min': minimum * alan,
            'deger_araligi_max': maksimum * alan,
            'kullanilan_alan_m2': alan
        }

    def resim_optimize_et(self, dosya_yolu: str, max_boyut_mb: float = 4.5) -> bytes:
        """Resmi optimize et - boyut çok büyükse küçült"""
        try:
            img = Image.open(dosya_yolu)

            # RGBA ise RGB'ye çevir
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background

            # Orijinal dosyayı kontrol et
            with open(dosya_yolu, 'rb') as f:
                original_data = f.read()

            original_size_mb = len(original_data) / (1024 * 1024)

            if original_size_mb <= max_boyut_mb:
                return original_data

            print(f"Emsal resmi optimize ediliyor: {original_size_mb:.2f}MB")

            # Boyutu küçült
            quality = 85
            max_dimension = 2048
            img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

            while quality > 20:
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=quality, optimize=True)
                data = buffer.getvalue()
                size_mb = len(data) / (1024 * 1024)

                if size_mb <= max_boyut_mb:
                    return data

                quality -= 10

            # Son çare
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=20, optimize=True)
            return buffer.getvalue()

        except Exception as e:
            print(f"Optimizasyon hatası: {e}")
            with open(dosya_yolu, 'rb') as f:
                return f.read()

    def emsal_analiz_et(self, emsal_yolu: str) -> Dict:
        """
        Tek bir emsal fotoğrafını/belgesini analiz et
        
        Emsal olarak şunlar kabul edilir:
        - Satış ilanı ekran görüntüleri (sahibinden.com, hurriyetemlak.com vb.)
        - Benzer gayrimenkul fotoğrafları + fiyat notu
        - Emsal değerleme belgeleri
        
        Returns:
            Dict: {
                'adres': str,
                'il': str,
                'ilce': str,
                'mahalle': str,
                'alan_m2': float,
                'fiyat': float,
                'birim_fiyat': float,
                'oda_sayisi': str,
                'kat': str,
                'bina_yasi': str,
                'ozellikler': str,
                'kaynak': str,
                'tarih': str
            }
        """
        
        # Resmi optimize et ve base64'e çevir
        resim_data = self.resim_optimize_et(emsal_yolu)
        base64_data = base64.standard_b64encode(resim_data).decode('utf-8')

        prompt = """
        Sen bir gayrimenkul değerleme uzmanısın. Bu görseli detaylıca analiz et.
        
        Bu görsel şunlardan biri olabilir:
        1. Satış ilanı ekran görüntüsü (sahibinden.com, hurriyetemlak.com, vb.)
        2. Gayrimenkul fotoğrafı + fiyat/bilgi notu
        3. Emsal değerleme belgesi
        4. Başka bir değerleme raporu sayfası
        
        Aşağıdaki bilgileri çıkar ve JSON formatında döndür:
        
        {
            "adres": "Tam adres veya sokak/mahalle bilgisi",
            "il": "İl",
            "ilce": "İlçe",
            "mahalle": "Mahalle/Semt",
            "alan_m2": "Alan bilgisi (sadece sayı, örn: 120)",
            "fiyat": "Toplam satış fiyatı (sadece sayı, TL olarak, örn: 2500000)",
            "oda_sayisi": "Oda sayısı (örn: 3+1, 2+1)",
            "kat": "Bulunduğu kat (örn: 5, Zemin, 3. kat)",
            "bina_yasi": "Bina yaşı veya yapım yılı",
            "ozellikler": "Öne çıkan özellikler (Site içi, Asansörlü, Otopark vb.)",
            "kaynak": "Kaynak bilgisi (sahibinden, emlakjet vb., veya bilinmiyor)",
            "tarih": "İlan tarihi veya değerleme tarihi (varsa)"
        }
        
        ÖNEMLİ KURALLAR:
        - Eğer bir bilgi görselde AÇIKÇA görünmüyorsa "null" yaz
        - Fiyatları sayısal değere çevir (1.500.000 TL → 1500000)
        - Alan bilgisini m² cinsinden sayıya çevir (120 m² → 120)
        - Tahmin yapma, sadece görselde NET olarak görünen bilgileri çıkar
        - JSON dışında hiçbir açıklama yapma, SADECE JSON döndür
        
        ÖRNEK ÇIKTI:
        {
            "adres": "Çankaya, Ankara",
            "il": "Ankara",
            "ilce": "Çankaya",
            "mahalle": "Kızılay",
            "alan_m2": "120",
            "fiyat": "2500000",
            "oda_sayisi": "3+1",
            "kat": "5",
            "bina_yasi": "10",
            "ozellikler": "Site içi, Asansörlü, Güvenlik",
            "kaynak": "sahibinden.com",
            "tarih": "2024-01-15"
        }
        """

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": base64_data
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

            yanit = message.content[0].text
            
            # JSON'ı çıkar
            json_match = re.search(r'\{[\s\S]*\}', yanit)
            if json_match:
                emsal_data = json.loads(json_match.group())
                
                # Birim fiyat hesapla
                if emsal_data.get('fiyat') and emsal_data.get('alan_m2'):
                    try:
                        fiyat = float(str(emsal_data['fiyat']).replace(',', '').replace('.', ''))
                        alan = float(str(emsal_data['alan_m2']).replace(',', '').replace('.', ''))
                        if alan > 0:
                            emsal_data['birim_fiyat'] = round(fiyat / alan, 2)
                        else:
                            emsal_data['birim_fiyat'] = None
                    except:
                        emsal_data['birim_fiyat'] = None
                else:
                    emsal_data['birim_fiyat'] = None
                
                return emsal_data
            else:
                return {
                    'hata': 'JSON parse edilemedi',
                    'ham_veri': yanit
                }

        except Exception as e:
            return {
                'hata': f'Analiz hatası: {str(e)}'
            }

    def emsalleri_karsilastir(self, gayrimenkul_verisi: Dict, emsal_listesi: List[Dict]) -> Dict:
        """
        Emsalleri karşılaştırıp değerlenen gayrimenkulün değerini hesapla
        
        Args:
            gayrimenkul_verisi: Değerlenen gayrimenkulün özellikleri
            emsal_listesi: Analiz edilmiş emsal listesi
            
        Returns:
            Dict: Değerleme sonuçları
        """
        
        # Geçerli emsalleri filtrele
        gecerli_emsaller = []
        for emsal in emsal_listesi:
            if emsal.get('birim_fiyat') and emsal.get('alan_m2'):
                gecerli_emsaller.append(emsal)
        
        if not gecerli_emsaller:
            return {
                'hata': 'Geçerli emsal bulunamadı',
                'toplam_emsal': len(emsal_listesi),
                'gecerli_emsal': 0
            }
        
        # AI ile karşılaştırma yap
        prompt = f"""
        Sen bir SPK onaylı gayrimenkul değerleme uzmanısın.
        
        DEĞERLENEN GAYRİMENKUL:
        {json.dumps(gayrimenkul_verisi, ensure_ascii=False, indent=2)}
        
        EMSALLER:
        {json.dumps(gecerli_emsaller, ensure_ascii=False, indent=2)}
        
        Yukarıdaki emsalleri kullanarak değerlenen gayrimenkulün piyasa değerini hesapla.
        
        YAPMAN GEREKENLER:
        1. Her emsalı değerlenen gayrimenkul ile karşılaştır
        2. Benzerlik derecesine göre ağırlık ver (konum, yaş, özellikler)
        3. Gerekli düzeltme katsayılarını uygula:
           - Konum farkı için (+/- %0-20)
           - Yaş farkı için (+/- %0-15)
           - Kat farkı için (+/- %0-10)
           - Özellik farkları için (+/- %0-15)
        4. Ağırlıklı ortalama birim m2 fiyatı hesapla
        5. Toplam değeri hesapla
        
        SONUCU ŞU FORMATTA DÖNDÜR:
        {{
            "emsal_analizi": [
                {{
                    "emsal_no": 1,
                    "adres": "emsal adresi",
                    "birim_fiyat": 15000,
                    "benzerlik_puani": 85,
                    "duzeltme_katsayisi": 1.05,
                    "duzeltilmis_birim_fiyat": 15750,
                    "aciklama": "Konum benzer, 2 yaş farkı var"
                }}
            ],
            "ortalama_birim_fiyat": 15500,
            "min_birim_fiyat": 14000,
            "max_birim_fiyat": 17000,
            "tahmini_deger": 1860000,
            "deger_araligi_min": 1680000,
            "deger_araligi_max": 2040000,
            "guven_seviyesi": "Yüksek / Orta / Düşük",
            "genel_degerlendirme": "Emsaller benzer özelliklere sahip, değerleme güvenilir..."
        }}
        
        SADECE JSON döndür, başka açıklama yapma.
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
            
            # JSON'ı çıkar
            json_match = re.search(r'\{[\s\S]*\}', yanit)
            if json_match:
                degerleme = json.loads(json_match.group())
                degerleme['toplam_emsal'] = len(emsal_listesi)
                degerleme['kullanilan_emsal'] = len(gecerli_emsaller)
                return degerleme
            else:
                return {
                    'hata': 'Değerleme parse edilemedi',
                    'ham_veri': yanit
                }
                
        except Exception as e:
            return {
                'hata': f'Değerleme hesaplama hatası: {str(e)}'
            }

    def emsalleri_toplu_isle(self, emsal_yollari: List[str], gayrimenkul_verisi: Dict) -> Dict:
        """
        Tüm emsalleri işle ve değerleme yap
        
        Args:
            emsal_yollari: Emsal dosya yolları listesi
            gayrimenkul_verisi: Değerlenen gayrimenkulün bilgileri
            
        Returns:
            Dict: Tüm emsal analizleri ve değerleme sonucu
        """
        
        emsal_analizleri = []
        
        print(f"\n{'='*60}")
        print(f"EMSAL ANALİZİ BAŞLIYOR - {len(emsal_yollari)} emsal işlenecek")
        print(f"{'='*60}\n")
        
        for idx, emsal_yolu in enumerate(emsal_yollari, 1):
            print(f"[{idx}/{len(emsal_yollari)}] İşleniyor: {Path(emsal_yolu).name}")
            
            try:
                emsal_data = self.emsal_analiz_et(emsal_yolu)
                emsal_data['dosya_yolu'] = emsal_yolu
                emsal_data['emsal_no'] = idx
                emsal_analizleri.append(emsal_data)
                
                if 'hata' not in emsal_data:
                    print(f"  ✓ Başarılı - Birim Fiyat: {emsal_data.get('birim_fiyat', 'N/A')} TL/m²")
                else:
                    print(f"  ✗ Hata: {emsal_data.get('hata')}")
                    
            except Exception as e:
                print(f"  ✗ İşleme hatası: {str(e)}")
                emsal_analizleri.append({
                    'emsal_no': idx,
                    'dosya_yolu': emsal_yolu,
                    'hata': str(e)
                })
        
        print(f"\n{'='*60}")
        print(f"EMSAL ANALİZİ TAMAMLANDI")
        print(f"{'='*60}\n")
        
        # Değerleme hesapla
        print("Değerleme hesaplanıyor...")
        degerleme_sonucu = self.emsalleri_karsilastir(gayrimenkul_verisi, emsal_analizleri)

        def _to_float(value):
            if value is None:
                return None
            if isinstance(value, (int, float)):
                try:
                    return float(value)
                except (TypeError, ValueError):
                    return None
            try:
                cleaned = str(value).replace('TL', '').replace('tl', '').replace(' ', '')
                cleaned = cleaned.replace('₺', '').replace('.', '').replace(',', '.')
                return float(cleaned)
            except (TypeError, ValueError):
                return None

        gecerli_emsaller = []
        for emsal in emsal_analizleri:
            if emsal.get('hata'):
                continue
            normalized = self._normalize_emsal(dict(emsal))
            emsal.update(normalized)
            birim = _to_float(normalized.get('birim_fiyat_rakam') or normalized.get('birim_fiyat'))
            alan = _to_float(normalized.get('alan_m2_rakam') or normalized.get('alan_m2'))
            if birim and alan:
                gecerli_emsaller.append((birim, alan))

        alan_adaylari = [
            gayrimenkul_verisi.get('net_alan_rakam'),
            gayrimenkul_verisi.get('net_alan'),
            gayrimenkul_verisi.get('brut_alan_rakam'),
            gayrimenkul_verisi.get('brut_alan'),
            gayrimenkul_verisi.get('arsa_alani_rakam'),
            gayrimenkul_verisi.get('arsa_alani'),
        ]
        subject_area = None
        for aday in alan_adaylari:
            subject_area = _to_float(aday)
            if subject_area:
                break

        if gecerli_emsaller:
            birimler = [b for b, _ in gecerli_emsaller]
            ortalama = statistics.mean(birimler)
            minimum = min(birimler)
            maksimum = max(birimler)
            tahmini = subject_area * ortalama if subject_area else None
            if isinstance(degerleme_sonucu, dict):
                degerleme_sonucu.setdefault('toplam_emsal', len(emsal_analizleri))
                degerleme_sonucu['kullanilan_emsal'] = len(birimler)
                degerleme_sonucu['ortalama_birim_fiyat'] = ortalama
                degerleme_sonucu['min_birim_fiyat'] = minimum
                degerleme_sonucu['max_birim_fiyat'] = maksimum
                degerleme_sonucu['kullanilan_alan_m2'] = subject_area
                if tahmini is not None:
                    degerleme_sonucu['tahmini_deger'] = tahmini
                    degerleme_sonucu['deger_araligi_min'] = minimum * subject_area
                    degerleme_sonucu['deger_araligi_max'] = maksimum * subject_area
                degerleme_sonucu.setdefault('hesaplama_yontemi', 'ortalama_birim_fiyat * alan')
            else:
                degerleme_sonucu = {
                    'toplam_emsal': len(emsal_analizleri),
                    'kullanilan_emsal': len(birimler),
                    'ortalama_birim_fiyat': ortalama,
                    'min_birim_fiyat': minimum,
                    'max_birim_fiyat': maksimum,
                    'kullanilan_alan_m2': subject_area,
                    'hesaplama_yontemi': 'ortalama_birim_fiyat * alan'
                }
                if tahmini is not None:
                    degerleme_sonucu['tahmini_deger'] = tahmini
                    degerleme_sonucu['deger_araligi_min'] = minimum * subject_area
                    degerleme_sonucu['deger_araligi_max'] = maksimum * subject_area

        return {
            'emsal_analizleri': emsal_analizleri,
            'degerleme_sonucu': degerleme_sonucu
        }

