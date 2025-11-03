"""
Yapılandırma Dosyası
Program ayarları ve sabitler
"""

import os
from pathlib import Path

# Proje dizinleri
BASE_DIR = Path(__file__).parent
TEMP_DIR = BASE_DIR / "temp"
OUTPUT_DIR = BASE_DIR / "output"
SAMPLE_DIR = BASE_DIR / "ornekrapor"

# Dizinleri oluştur
TEMP_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Claude API ayarları
CLAUDE_MODEL = "claude-sonnet-4-5-20250929"
MAX_TOKENS = 4096

def get_anthropic_api_key():
    """
    Anthropic API anahtarını döndürür
    Öncelik sırası:
    1. Environment variable (ANTHROPIC_API_KEY)
    2. .env dosyası
    """
    # Environment variable'dan kontrol et
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if api_key:
        return api_key

    # .env dosyasından oku
    env_path = BASE_DIR / '.env'
    if env_path.exists():
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        if key.strip() == 'ANTHROPIC_API_KEY':
                            return value.strip()
        except Exception as e:
            print(f"⚠️ .env dosyası okunamadı: {e}")

    # Hiçbir yerde bulunamadıysa hata ver
    raise ValueError(
        "❌ Anthropic API anahtarı bulunamadı!\n\n"
        "Lütfen aşağıdaki yöntemlerden birini kullanın:\n"
        "1. Environment variable ayarlayın: ANTHROPIC_API_KEY=your_key_here\n"
        "2. .env dosyası oluşturun (.env.example'dan kopyalayın)\n"
        "\nÖrnek .env içeriği:\n"
        "ANTHROPIC_API_KEY=sk-ant-api03-your_key_here\n"
    )

# Görsel işleme ayarları
IMAGE_MAX_WIDTH = 1920
IMAGE_MAX_HEIGHT = 1080
IMAGE_QUALITY = 85

# Desteklenen dosya formatları
SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
SUPPORTED_DOC_FORMATS = ['.pdf']

# Rapor ayarları
DEFAULT_FONT = "Calibri"
DEFAULT_FONT_SIZE = 11
HEADING_FONT_SIZE = 14

# Firma varsayılan bilgileri
DEFAULT_COMPANY = {
    'name': 'A.R.E.A. GAYRİMENKUL DEĞERLEME ve DANIŞMANLIK A.Ş.',
    'address': 'Hilal Mahallesi, Hollanda Caddesi, No: 9/6 Çankaya/ANKARA',
    'phone': '+90 312 443 01 00',
    'email': 'bilgi@areadegerleme.com',
    'website': 'www.areadegerleme.com'
}

# Analiz prompt şablonları
PROPERTY_ANALYSIS_PROMPT = """
Lütfen bu gayrimenkul görsellerini detaylı olarak analiz edin ve aşağıdaki bilgileri çıkarın:

1. Gayrimenkulün Fiziksel Özellikleri
   - Bağımsız bölüm numarası
   - Alan bilgileri (net m2, brüt m2)
   - Oda sayısı ve dağılımı
   - Yapı malzemeleri
   - İnşaat kalitesi

2. Konum ve Çevre Özellikleri
   - Kat bilgisi
   - Görünüm/yönelim
   - Çevre düzeni

3. Genel Durum Değerlendirmesi
   - Bakım durumu
   - Kullanım durumu
   - Eksiklikler veya hasarlar

4. Değerleme Açısından Önemli Noktalar
   - Değeri artıran özellikler
   - Değeri düşüren faktörler

ÖNEMLİ: Eğer görsellerde m2 tablosu varsa, gayrimenkul numarasını bulup m2 bilgisini oradan alın.
Eğer mimari proje görseli varsa, ölçüleri kullanarak m2 hesabı yapın.

Profesyonel bir gayrimenkul değerleme uzmanı gibi detaylı ve objektif bir analiz yapın.
Türkçe olarak yanıt verin.
"""

DOCUMENT_ANALYSIS_PROMPT = """
Lütfen bu belgeleri detaylı olarak analiz edin ve tüm önemli bilgileri çıkarın:

- Ada/Parsel bilgileri
- Malik (mülk sahibi) bilgileri
- Yüzölçüm bilgileri (m2)
  * Tapuda kayıtlı alan
  * Bağımsız bölüm alanı
  * Ortak alan payı
- Bağımsız bölüm numarası
- İmar durumu bilgileri
- Kısıtlamalar ve şerhler
- Tarih ve referans numaraları

ÖNEMLİ M2 BİLGİSİ ÇIKARMA:
1. Eğer belgede m2 tablosu varsa, gayrimenkul numarasını bulup ilgili satırdan m2 bilgisini alın
2. Eğer mimari proje/plan varsa, ölçülerden yararlanarak hesaplama yapın
3. Tapuda kayıtlı alan bilgisini mutlaka belirtin

Türkçe karakterleri doğru şekilde kullanın.
Türkçe olarak yanıt verin.
"""

COMPARABLE_ANALYSIS_PROMPT = """
Lütfen emsal gayrimenkul verilerini analiz edin ve karşılaştırma yapın:

Her bir emsal için:
1. Konum bilgileri
   - Mahalle/semt
   - İlçe
   - Mesafe

2. Fiziksel özellikler
   - Alan (m2) - MUTLAKA BELİRTİN
   - Oda sayısı
   - Kat bilgisi
   - Bina yaşı
   - Genel durum

3. Fiyat bilgileri
   - Toplam fiyat
   - Birim fiyat (TL/m2) - MUTLAKA HESAPLAYIN

4. Benzerlik ve farklılıklar
   - Ana gayrimenkul ile benzer yönler
   - Farklı yönler
   - Fiyat farkının nedenleri

ÖNEMLİ: Her emsal için m2 bilgisi MUTLAKA bulunmalı veya hesaplanmalıdır.
Birim fiyat hesabı için (Toplam Fiyat / m2) formülünü kullanın.

Profesyonel bir değerlendirme yapın.
Türkçe olarak yanıt verin.
"""

# M2 bilgisi çıkarma öncelikleri
M2_EXTRACTION_PRIORITY = """
M2 bilgisi aşağıdaki öncelik sırasına göre çıkarılmalıdır:
1. M2 tablosundan (gayrimenkul numarası ile eşleştirerek)
2. Tapu kaydından (resmi alan bilgisi)
3. Mimari projeden (ölçülerden hesaplama)
4. Emlak ilanından (beyan edilen alan)

Her durumda m2 bilgisinin kaynağı belirtilmelidir.
"""

# Log ayarları
LOG_LEVEL = "INFO"
LOG_FILE = BASE_DIR / "app.log"

# GUI ayarları
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
WINDOW_TITLE = "Gayrimenkul Değerleme Raporu Oluşturucu"

# Renk temaları
COLORS = {
    'primary': '#2C3E50',
    'secondary': '#3498DB',
    'success': '#27AE60',
    'warning': '#F39C12',
    'danger': '#E74C3C',
    'light': '#ECF0F1',
    'dark': '#34495E'
}

# API rate limiting
API_RATE_LIMIT = {
    'requests_per_minute': 50,
    'retry_delay': 60,  # saniye
    'max_retries': 3
}

# Hata mesajları
ERROR_MESSAGES = {
    'api_error': 'Claude API ile bağlantı hatası oluştu.',
    'file_not_found': 'Dosya bulunamadı.',
    'invalid_format': 'Geçersiz dosya formatı.',
    'processing_error': 'Veri işleme sırasında hata oluştu.',
    'm2_not_found': 'M2 bilgisi çıkarılamadı. Lütfen manuel olarak girin.'
}

# Başarı mesajları
SUCCESS_MESSAGES = {
    'report_generated': 'Rapor başarıyla oluşturuldu.',
    'data_extracted': 'Veriler başarıyla çıkarıldı.',
    'm2_calculated': 'M2 bilgisi başarıyla hesaplandı.'
}
