# OCR + AI Doğrulama Sistemi - Kurulum ve Kullanım

## 🎯 Özellikler

### OCR (Optical Character Recognition)
- ✅ Taranmış belgelerden metin çıkarma
- ✅ Türkçe + İngilizce dil desteği
- ✅ Tesseract OCR motoru

### AI Doğrulama
- ✅ OCR hatalarını otomatik düzeltme
- ✅ Mahalle/adres isimlerini kontrol etme
- ✅ Sayıları doğru formata çevirme
- ✅ Yapılandırılmış veri çıkarma

## 📦 Kurulum

### Adım 1: Tesseract OCR Yükleyin

**Windows:**
1. İndirin: https://github.com/UB-Mannheim/tesseract/wiki
2. Kurulum sırasında:
   - ✅ "Additional language data (download)" → **Turkish** seçin
   - ✅ Varsayılan konum: `C:\Program Files\Tesseract-OCR\`

**macOS:**
```bash
brew install tesseract
brew install tesseract-lang  # Türkçe için
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-tur  # Türkçe için
```

### Adım 2: Python Paketleri

```bash
pip install pytesseract pillow
```

### Adım 3: Kontrol Edin

```bash
python test_ocr.py
```

## 🚀 Kullanım

### Basit OCR

```python
from ocr_processor import OCRProcessor

# OCR processor oluştur
ocr = OCRProcessor()

# Dosyayı işle
sonuc = ocr.dosya_isle('tapu.jpg', dosya_tipi='Tapu Belgesi')

# Sonuçları göster
print("OCR Metin:", sonuc['ocr_metin'])
print("AI Düzeltme:", sonuc['ai_duzeltme'])
```

### Ana Programda Kullanım

OCR sistemi ana programa entegre edildi:

1. **Dosya Yükle** → OCR otomatik çalışır
2. **OCR Metin Çıkarır** → Ham metin
3. **AI Doğrular** → Düzeltilmiş metin
4. **Form Doldurulur** → Temiz veri

### Örnek Çıktı

```json
{
  "ocr_metin": "MAH4LLE: 8EŞEVLEk\nADA: l23\nPARSEL: 45",
  "ai_duzeltme": {
    "duzeltilmis_metin": "MAHALLE: BEŞEVLER\nADA: 123\nPARSEL: 45",
    "onemli_bilgiler": {
      "mahalle": "BEŞEVLER",
      "ada": "123",
      "parsel": "45"
    },
    "duzeltme_notlari": "4→A, 8→B, k→R, l→1 düzeltildi"
  }
}
```

## 🔧 Yapılandırma

### Tesseract Yolu (Windows)

Eğer farklı bir konuma yüklediyseniz, `ocr_processor.py` dosyasında:

```python
tesseract_yolu = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### OCR Dili

Varsayılan: Türkçe + İngilizce (`tur+eng`)

Değiştirmek için:
```python
metin = pytesseract.image_to_string(img, lang='tur')  # Sadece Türkçe
```

## 📊 OCR Kalitesini Artırma

### 1. Görsel Ön İşleme

```python
from PIL import Image, ImageEnhance

img = Image.open('belge.jpg')

# Kontrast artır
enhancer = ImageEnhance.Contrast(img)
img = enhancer.enhance(2.0)

# Netlik artır
enhancer = ImageEnhance.Sharpness(img)
img = enhancer.enhance(2.0)

# OCR
metin = pytesseract.image_to_string(img, lang='tur+eng')
```

### 2. Görsel Kalitesi

- ✅ En az 300 DPI çözünürlük
- ✅ Net, bulanık olmayan görüntü
- ✅ İyi ışıklandırma
- ✅ Düz (eğik olmayan) belge

### 3. Belge Tipi

OCR en iyi şunlarda çalışır:
- ✅ Taranmış belgeler
- ✅ Fotoğraflanmış belgeler
- ✅ Düz metin içeren görseller

OCR gerekli OLMAYAN:
- ❌ Dijital PDF'ler (zaten metin içerir)
- ❌ Word/Excel dosyaları

## 🐛 Sorun Giderme

### "Tesseract bulunamadı" Hatası

**Çözüm:**
```python
# Windows için tam yol belirtin
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### OCR Çıktısı Boş

**Nedenler:**
- Görsel çok bulanık
- Yazı çok küçük
- Dil paketi eksik

**Çözüm:**
- Görseli büyütün/netleştirin
- Türkçe dil paketini yükleyin
- Kontrast/parlaklık ayarlayın

### OCR Yanlış Okuma Yapıyor

**Normal!** Bu yüzden AI doğrulama var:
1. OCR ham metin çıkarır (hatalarla)
2. AI düzeltir ve doğrular
3. Temiz veri elde edilir

### "pytesseract yüklü değil"

```bash
pip install pytesseract
```

## 📝 Gelişmiş Kullanım

### Özel OCR Ayarları

```python
# PSM (Page Segmentation Mode) ayarı
custom_config = r'--oem 3 --psm 6'
metin = pytesseract.image_to_string(img, lang='tur+eng', config=custom_config)
```

**PSM Modları:**
- 3: Otomatik sayfa segmentasyonu
- 6: Tek düzgün metin bloğu
- 11: Seyrek metin

### Sadece Sayılar

```python
custom_config = r'--psm 6 outputbase digits'
sayi = pytesseract.image_to_string(img, config=custom_config)
```

## 🎯 En İyi Pratikler

1. **Yüksek Kalite Görsel:**
   - 300+ DPI
   - PNG veya TIFF formatı
   - Sıkıştırmasız

2. **Ön İşleme:**
   - Gri tonlamaya çevir
   - Kontrast artır
   - Gürültü azalt

3. **Doğrulama:**
   - Her zaman AI doğrulaması kullan
   - Manuel kontrol yap
   - Kritik verileri çift kontrol et

4. **Performans:**
   - Küçük görseller daha hızlı
   - Çok sayfa varsa toplu işle
   - Gereksiz OCR yapma (dijital PDF'ler)

## 📞 Destek

OCR sorunları için:
1. `test_ocr.py` scriptini çalıştırın
2. Test çıktısını kontrol edin
3. Hata mesajlarını inceleyin

AI doğrulama sorunları için:
1. API key'iniz aktif mi kontrol edin
2. İnternet bağlantınızı kontrol edin
3. API limitlerini kontrol edin

---

**🎉 OCR + AI ile artık taranmış belgeler de otomatik işleniyor!**
