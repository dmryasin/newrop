# -*- coding: utf-8 -*-
import os
import json
from pathlib import Path
import base64
from typing import List, Dict
import anthropic
from PIL import Image
import io
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

class AIBelgeIsleyici:
    """Yapay zeka ile belge işleme ve veri çıkarma modülü"""

    def __init__(self):
        # API anahtarı direkt olarak sisteme entegre edildi
        from config import get_anthropic_api_key
        self.api_key = get_anthropic_api_key()

        if not self.api_key:
            raise ValueError("API anahtarı bulunamadı!")

        self.client = anthropic.Anthropic(api_key=self.api_key)

    def dosya_oku(self, dosya_yolu: str) -> bytes:
        """Dosyayı binary olarak oku"""
        with open(dosya_yolu, 'rb') as f:
            return f.read()

    def resim_optimize_et(self, dosya_yolu: str, max_boyut_mb: float = 4.5) -> bytes:
        """
        Resmi optimize et - boyut çok büyükse küçült
        API limiti ~5MB, güvenli olması için 4.5MB'a sınırla
        """
        try:
            # Resmi aç
            img = Image.open(dosya_yolu)

            # RGBA ise RGB'ye çevir (JPEG için)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background

            # Önce orijinal dosyayı dene
            with open(dosya_yolu, 'rb') as f:
                original_data = f.read()

            original_size_mb = len(original_data) / (1024 * 1024)

            # Eğer dosya zaten küçükse direkt döndür
            if original_size_mb <= max_boyut_mb:
                return original_data

            # Dosya büyükse optimize et
            print(f"Dosya boyutu {original_size_mb:.2f}MB, optimize ediliyor...")

            # Kalite ve boyut ayarları
            quality = 85
            max_dimension = 2048

            # Boyutu küçült
            img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

            # Optimizasyon döngüsü
            while quality > 20:
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=quality, optimize=True)
                data = buffer.getvalue()
                size_mb = len(data) / (1024 * 1024)

                if size_mb <= max_boyut_mb:
                    print(f"Optimize edildi: {size_mb:.2f}MB (kalite: {quality})")
                    return data

                quality -= 10

            # Son çare: en düşük kalite
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=20, optimize=True)
            return buffer.getvalue()

        except Exception as e:
            print(f"Optimizasyon hatası: {e}, orijinal dosya kullanılıyor")
            with open(dosya_yolu, 'rb') as f:
                return f.read()

    def resim_base64_cevir(self, dosya_yolu: str) -> str:
        """Resmi optimize edip base64'e çevir"""
        dosya_icerik = self.resim_optimize_et(dosya_yolu)
        return base64.standard_b64encode(dosya_icerik).decode('utf-8')

    def medya_turu_belirle(self, dosya_yolu: str) -> str:
        """Dosya uzantısına göre medya türünü belirle"""
        uzanti = Path(dosya_yolu).suffix.lower()

        medya_turleri = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.tif': 'image/tiff',
            '.tiff': 'image/tiff',
            '.pdf': 'application/pdf'
        }

        return medya_turleri.get(uzanti, 'application/octet-stream')

    def pdf_base64_cevir(self, dosya_yolu: str, max_boyut_mb: float = 10.0) -> str:
        """
        PDF'i base64'e çevir, boyut kontrolü yap
        PDF'ler için limit daha yüksek (10MB)
        """
        dosya_icerik = self.dosya_oku(dosya_yolu)
        size_mb = len(dosya_icerik) / (1024 * 1024)

        if size_mb > max_boyut_mb:
            raise ValueError(f"PDF dosyası çok büyük ({size_mb:.2f}MB). Maksimum {max_boyut_mb}MB olmalıdır.")

        return base64.standard_b64encode(dosya_icerik).decode('utf-8')

    def dosya_turu_belirle(self, dosya_yolu: str) -> str:
        """
        AI ile dosyanın türünü belirle
        (Tapu, Takbis, İmar Durumu, Enerji Kimlik Belgesi, Fotoğraf vb.)
        """
        uzanti = Path(dosya_yolu).suffix.lower()

        # Resim dosyası ise AI'ya sor
        if uzanti in ['.jpg', '.jpeg', '.png', '.tif', '.tiff']:
            base64_data = self.resim_base64_cevir(dosya_yolu)
            medya_turu = self.medya_turu_belirle(dosya_yolu)

            prompt = """
            Bu görseli analiz et ve aşağıdaki kategorilerden hangisine ait olduğunu belirle:

            1. Tapu Belgesi (Tapu Senedi)
            2. Takbis (Kadastral harita, parselasyon planı)
            3. İmar Durumu Belgesi
            4. Enerji Kimlik Belgesi
            5. Yapı Ruhsatı
            6. İskân Ruhsatı
            7. Kat Mülkiyeti Belgesi
            8. Mimari Proje (Kat planı, vaziyet planı, kesit, görünüş vb.)
            9. Kroki / CBS Görseli (Koordinat, yön göstergeli teknik çizim)
            10. Vaziyet Planı (Gayrimenkulün konumunu gösteren plan)
            11. Fotoğraf (Gayrimenkul fotoğrafı, bina/daire/arsa fotoğrafı)
            12. Diğer Belge

            Sadece kategori adını döndür, başka açıklama yapma.
            Eğer bir bina/daire/arsa fotoğrafı ise sadece "Fotoğraf" yaz.
            """

            try:
                message = self.client.messages.create(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=100,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": medya_turu,
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

                dosya_turu = message.content[0].text.strip()
                return dosya_turu

            except Exception as e:
                error_msg = str(e)
                if "400" in error_msg or "413" in error_msg or "payload" in error_msg.lower():
                    return "Resim - Dosya çok büyük (otomatik optimizasyon başarısız)"
                return f"Resim - Sınıflandırılamadı ({error_msg[:50]})"

        elif uzanti == '.pdf':
            # PDF için
            base64_data = self.pdf_base64_cevir(dosya_yolu)

            prompt = """
            Bu PDF belgesini analiz et ve aşağıdaki kategorilerden hangisine ait olduğunu belirle:

            1. Tapu Belgesi (Tapu Senedi)
            2. Takbis (Kadastral harita, parselasyon planı)
            3. İmar Durumu Belgesi
            4. Enerji Kimlik Belgesi
            5. Yapı Ruhsatı
            6. İskân Ruhsatı
            7. Kat Mülkiyeti Belgesi
            8. Mimari Proje (Kat planı, vaziyet planı, kesit, görünüş vb.)
            9. Kroki / CBS Görseli
            10. Değerleme Raporu
            11. Diğer Belge

            Sadece kategori adını döndür, başka açıklama yapma.
            """

            try:
                message = self.client.messages.create(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=100,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "document",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "application/pdf",
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

                dosya_turu = message.content[0].text.strip()
                return dosya_turu

            except ValueError as e:
                # Dosya boyutu hatası
                return f"PDF - Dosya çok büyük"
            except Exception as e:
                error_msg = str(e)
                if "400" in error_msg or "413" in error_msg:
                    return "PDF - Dosya çok büyük"
                return f"PDF - Sınıflandırılamadı"

        else:
            return "Bilinmeyen Format"

    def belgeleri_isle(self, belgeler: List[Dict]) -> Dict:
        """
        Belgeleri AI ile işle ve veri çıkar

        Args:
            belgeler: Belge bilgilerini içeren liste

        Returns:
            Çıkarılan verileri içeren dict
        """

        # Prompt hazırla - SPK standartlarına uygun kapsamlı veri çıkarma
        prompt = """
        Sen bir SPK onaylı gayrimenkul değerleme uzmanısın. Sana verilen belgeleri (tapu, imar, takbis, enerji kimlik belgesi vb.)
        detaylı şekilde analiz edip SPK değerleme raporu için gerekli TÜM bilgileri çıkarmalısın.

        Aşağıdaki bilgileri JSON formatında döndür. Eğer bir bilgi belgede yoksa null değeri ver:

        **KONUM BİLGİLERİ:**
        - adres: Tam adres
        - il: İl adı
        - ilce: İlçe adı
        - mahalle: Mahalle/Köy adı
        - sokak: Sokak/Cadde adı
        - bina_no: Bina/Kapı numarası
        - daire_no: Daire numarası (varsa)
        - posta_kodu: Posta kodu (varsa)

        **TAPU BİLGİLERİ:**
        - ada: Ada numarası
        - parsel: Parsel numarası
        - nitelik: Arsa/Arazi niteliği
        - tapu_turu: Tapu türü (Kat mülkiyeti/Kat irtifakı/Arsa tapusu vb.)
        - malik: Malik/Mülk sahibi adı
        - hisse: Hisse oranı (varsa, örn: "1/1", "1/4")

        **YÜZÖLÇÜM VE FİZİKSEL ÖZELLİKLER:**

        ÖNEMLİ - M2 BİLGİSİ ÇIKARMA ÖNCELİĞİ:
        M2 bilgilerini aşağıdaki öncelik sırasına göre çıkar ve MUTLAKA KAYNAK BELİRT:
        1. M2 TABLOSU (varsa): Gayrimenkul numarasını bulup ilgili satırdan m2 bilgisini al
        2. TAPU BELGESİ: Tapuda kayıtlı resmi alan bilgisini al
        3. MİMARİ PROJE/KAT PLANI: Ölçü kotlarından yararlanarak hesaplama yap (uzunluk x genişlik)
        4. RUHSAT BELGELERİ: Yapı/İskan ruhsatında yazılı alan bilgisini al
        5. KAT MÜLKİYETİ BELGESİ: Bağımsız bölüm alanını ve ortak alan payını çıkar

        Her alan bilgisi için kaynağını parantez içinde belirt. Örnek: "125.50 m2 (Tapu)", "3+1 (Mimari Proje)"

        - bağımsız_bolum_no: Bağımsız bölüm numarası (Kat mülkiyeti belgesinden veya m2 tablosundan)
        - arsa_alani: Arsa alanı (m²) - KAYNAK BELİRT
        - imar_parseli_alani: İmar parseli alanı (m²) - KAYNAK BELİRT
        - brut_alan: Brüt inşaat alanı (m²) - KAYNAK BELİRT (önce m2 tablosuna bak, sonra tapuya, sonra mimari projeye)
        - net_alan: Net kullanılabilir alan (m²) - KAYNAK BELİRT (önce m2 tablosuna bak, sonra tapuya, sonra mimari projeye)
        - tapu_alani: Tapuda kayıtlı alan (m²) - Tapu belgesinden çıkar
        - ortak_alan_payi: Ortak alan payı (m² veya yüzde) - Kat mülkiyeti belgesinden
        - kat_sayisi: Toplam kat sayısı
        - bulundugu_kat: Değerlenen birimin bulunduğu kat
        - oda_sayisi: Oda sayısı (örn: "3+1", "2+1", "4+2" vb.) - KAYNAK BELİRT - Mimari proje, kat planı, bağımsız bölüm detay planı veya ruhsat belgelerinden çıkar. Eğer fotoğraflarda iç mekan görselleri varsa buradan da tahmin edebilirsin.
        - bina_yasi: Bina yaşı/İnşaat yılı
        - yapit_durumu: Yapı durumu (İnşaat halinde, Kullanımda, Yeni vb.)

        **İMAR BİLGİLERİ:**
        - imar_durumu: İmar durumu (İmarlı, İmarsız, Tarla, vb.)
        - imar_plani_mevcudiyet: İmar planı var mı? (Var/Yok)
        - yapilanma_kosullari: Yapılanma koşulları
        - emsal: İmar emsal değeri
        - gabari: Gabari/Yükseklik sınırı
        - taks: TAKS (Taban Alanı Katsayısı)
        - kaks: KAKS (Kat Alanları Katsayısı)

        **ENERJİ VE EK BİLGİLER:**
        - enerji_sinifi: Enerji kimlik belgesi sınıfı (A, B, C vb.)
        - isitma_tipi: Isıtma sistemi türü
        - cephe_yonu: Cephe yönü (Kuzey, Güney, Doğu, Batı, Güneydoğu vb.) - Kroki, CBS görseli, vaziyet planı veya mimari proje dosyalarından çıkar. Pusula işareti veya yön belirteci varsa kullan.
        - manzara: Manzara/Konum bilgisi - Gayrimenkulün hangi tür yola baktığını (ana cadde, ara sokak, bulvar vb.), deniz/göl/orman/şehir manzarası olup olmadığını, yeşil alan/park gibi özellikleri içerecek şekilde detaylı açıkla.

        **DİĞER:**
        - kullanim_amaci: Kullanım amacı (Konut, Ticari, Ofis, Arsa vb.)
        - diger_bilgiler: Diğer önemli notlar ve açıklamalar

        JSON formatı:
        {
            "adres": "...",
            "il": "...",
            "ilce": "...",
            "mahalle": "...",
            "sokak": "...",
            "bina_no": "...",
            "daire_no": "...",
            "posta_kodu": "...",
            "ada": "...",
            "parsel": "...",
            "nitelik": "...",
            "tapu_turu": "...",
            "malik": "...",
            "hisse": "...",
            "bağımsız_bolum_no": "...",
            "arsa_alani": "... m2 (KAYNAK)",
            "imar_parseli_alani": "... m2 (KAYNAK)",
            "brut_alan": "... m2 (KAYNAK)",
            "net_alan": "... m2 (KAYNAK)",
            "tapu_alani": "... m2 (Tapu)",
            "ortak_alan_payi": "...",
            "kat_sayisi": "...",
            "bulundugu_kat": "...",
            "oda_sayisi": "... (KAYNAK)",
            "bina_yasi": "...",
            "yapit_durumu": "...",
            "imar_durumu": "...",
            "imar_plani_mevcudiyet": "...",
            "yapilanma_kosullari": "...",
            "emsal": "...",
            "gabari": "...",
            "taks": "...",
            "kaks": "...",
            "enerji_sinifi": "...",
            "isitma_tipi": "...",
            "cephe_yonu": "...",
            "manzara": "...",
            "kullanim_amaci": "...",
            "diger_bilgiler": "..."
        }

        SADECE JSON döndür, başka açıklama yapma.
        """

        # Belgeleri içeriğe ekle
        content = []

        for belge in belgeler:
            dosya_yolu = belge["yol"]
            belge_tipi = belge["tip"]

            # Dosya türünü kontrol et
            uzanti = Path(dosya_yolu).suffix.lower()

            if uzanti in ['.jpg', '.jpeg', '.png', '.tif', '.tiff']:
                # Resim dosyası için
                base64_data = self.resim_base64_cevir(dosya_yolu)
                medya_turu = self.medya_turu_belirle(dosya_yolu)

                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": medya_turu,
                        "data": base64_data
                    }
                })

            elif uzanti == '.pdf':
                # PDF için - Claude Sonnet 4.5 PDF okuyabilir
                base64_data = self.pdf_base64_cevir(dosya_yolu)

                content.append({
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": base64_data
                    }
                })

        # Son prompt'u ekle
        content.append({
            "type": "text",
            "text": prompt
        })

        # Claude API'sine istek gönder
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2048,
                messages=[
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            )

            # Yanıtı parse et
            yanit_text = message.content[0].text

            # JSON'ı çıkar
            # Bazen AI açıklama yapar, JSON'ı bul
            import re
            json_match = re.search(r'\{[\s\S]*\}', yanit_text)

            if json_match:
                json_str = json_match.group()
                veri = json.loads(json_str)
                return veri
            else:
                # JSON bulunamadıysa raw yanıtı döndür
                return {"ham_veri": yanit_text}

        except Exception as e:
            raise Exception(f"AI işleme hatası: {str(e)}")

    def fotograf_acikla(self, fotograf_yolu: str) -> str:
        """Fotoğrafın açıklamasını AI ile oluştur"""

        base64_data = self.resim_base64_cevir(fotograf_yolu)
        medya_turu = self.medya_turu_belirle(fotograf_yolu)

        prompt = """
        Bu gayrimenkul fotoğrafını detaylı şekilde açıkla.
        Fotoğrafta görünen yapı özellikleri, çevre durumu, bina durumu gibi
        değerleme raporu için önemli olabilecek tüm detayları belirt.
        Açıklamayı Türkçe ve profesyonel bir dille yaz.
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
                                    "media_type": medya_turu,
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

            return message.content[0].text

        except Exception as e:
            return f"Açıklama oluşturulamadı: {str(e)}"
