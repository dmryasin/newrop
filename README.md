# Gayrimenkul Değerleme Rapor Sistemi

AI destekli otomatik gayrimenkul değerleme raporu oluşturma sistemi.

## Özellikler

- 📄 **Otomatik Belge Analizi**: Tapu, imar, TAKBIS belgelerini AI ile analiz eder
- 🖼️ **Görsel İşleme**: Gayrimenkul fotoğraflarını ve mimari projeleri değerlendirir
- 📊 **Emsal Analizi**: Benzer gayrimenkul verilerini karşılaştırır
- 📑 **PDF Rapor Üretimi**: AREA formatında profesyonel değerleme raporu oluşturur
- 🎯 **Dinamik Hesaplama**: Alan bilgileri ve emsal verilerinden otomatik değer hesaplama

## Kurulum

### 1. Gereksinimler

```bash
pip install anthropic pillow reportlab python-docx
```

### 2. API Anahtarı Yapılandırması

Anthropic API anahtarınızı yapılandırmak için iki yöntem:

**Yöntem 1: Environment Variable (Önerilen)**
```bash
# Windows
set ANTHROPIC_API_KEY=sk-ant-api03-your_key_here

# Linux/Mac
export ANTHROPIC_API_KEY=sk-ant-api03-your_key_here
```

**Yöntem 2: .env Dosyası**
```bash
# .env.example dosyasını kopyalayın
cp .env.example .env

# .env dosyasını düzenleyin ve API anahtarınızı ekleyin
ANTHROPIC_API_KEY=sk-ant-api03-your_key_here
```

## Kullanım

```bash
python main.py
```

### Adımlar

1. **Dosya Yükleme**: Tapu, imar, TAKBIS belgeleri ve gayrimenkul fotoğraflarını yükleyin
2. **Emsal Ekleme**: Benzer gayrimenkul ilanlarını veya belgelerini ekleyin
3. **Sınıflandırma**: "Dosyaları Sınıflandır ve Analiz Et" butonuna tıklayın
4. **Rapor Bilgileri**: Manuel olarak rapor bilgilerini (talep eden kurum, uzman bilgileri vb.) girin
5. **Rapor Oluştur**: "Rapor Oluştur" butonuna tıklayın

## Proje Yapısı

```
├── main.py                      # Ana GUI uygulaması
├── config.py                    # Yapılandırma ve API key yönetimi
├── ai_processor.py              # AI belge işleme
├── area_report_generator.py    # AREA formatında rapor üretimi
├── takbis_processor.py          # TAKBIS belgesi analizi
├── emsal_processor.py           # Emsal değerleme işlemleri
├── ocr_processor.py             # OCR ve görsel işleme
└── raporlar/                    # Oluşturulan raporlar
```

## Önemli Notlar

- API anahtarınızı **asla** kod içine yazmayın
- `.env` dosyası `.gitignore` ile korunmaktadır
- Tüm raporlar `raporlar/` dizinine kaydedilir
- Desteklenen dosya formatları: PDF, JPG, JPEG, PNG, TIFF

## Lisans

Bu proje özel kullanım için geliştirilmiştir.
