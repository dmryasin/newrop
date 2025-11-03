# OCR Özelliği - Kullanım Kılavuzu

## 🎯 OCR Nedir?

**Optical Character Recognition (Optik Karakter Tanıma):** Görsellerdeki ve PDF'lerdeki yazıları okuyup dijital metne çevirir.

## ✨ Neden OCR?

1. **Daha Doğru Okuma**: AI önce OCR ile metni okur, sonra görsel ile doğrular
2. **Mahalle İsimlerinde Hata Azalır**: OCR metin olarak okur, AI doğrular
3. **Rakamlar Daha Net**: OCR sayıları kesin okur
4. **Hızlı Analiz**: OCR + AI = Çift kontrol

## 📦 Kurulum

### Seçenek 1: EasyOCR (Önerilen - Kolay)

```bash
pip install easyocr
```

**Avantajlar:**
- ✅ Sadece pip install yeterli
- ✅ Türkçe desteği çok iyi
- ✅ GPU olmadan da çalışır

**Dezavantajlar:**
- ⚠️ İlk kullanımda model indirir (~500MB, 1-2 dakika)
- ⚠️ Biraz yavaş (belge başına 5-10 saniye)

### Seçenek 2: Tesseract OCR (Hızlı)

```bash
pip install pytesseract
pip install pdf2image
```

**Tesseract Binary Kurulumu:**
1. İndir: https://github.com/UB-Mannheim/tesseract/wiki
2. Kur: `tesseract-ocr-w64-setup-5.x.x.exe`
3. Yolu not et: `C:\Program Files\Tesseract-OCR\tesseract.exe`

**Türkçe Dil Paketi:**
1. Tesseract kurulumunda "Turkish" seçeneğini işaretle
2. Veya sonradan indir: https://github.com/tesseract-ocr/tessdata

**Poppler (PDF için):**
1. İndir: https://github.com/oschwartz10612/poppler-windows/releases
2. Klasörü aç, `bin` klasörünü PATH'e ekle

## 🚀 Kullanım

### Otomatik OCR (Varsayılan)

```bash
python main_duzenlenebilir.py
```

OCR otomatik aktif! Analiz ederken:
```
🔍 OCR TARAMASI BAŞLIYOR - 6 belge
====================================

[1/6] 🔍 OCR: tapu.jpg
  ✅ 1523 karakter okundu
  
[2/6] 🔍 OCR: katplani.png
  ✅ 245 karakter okundu
  
🤖 AI'ya 6 belge gönderiliyor...
✅ AI analizi tamamlandı!
```

### OCR'ı Kapatmak İsterseniz

`ai_processor_gelismis.py` dosyasında:

```python
def belgeleri_analiz_et(self, belgeler: List[Dict], ocr_kullan: bool = False):  # False yapın
```

## 📊 Nasıl Çalışır?

### Adım 1: OCR Taraması
```
Belge (tapu.jpg) → OCR → "T.C. TAPU SENEDI
                          İL: ANKARA
                          İLÇE: ÇANKAYA
                          MAHALLE: KIZIL AY
                          ADA: 1234
                          PARSEL: 56"
```

### Adım 2: AI Doğrulama
```
AI: OCR okudu: "KIZIL AY"
    Görselde kontrol: ✅ Doğru
    
AI: OCR okudu: "1234"
    Görselde kontrol: ✅ Doğru
```

### Adım 3: Yapılandırma
```json
{
  "mahalle": "Kızılay",
  "ada": "1234",
  "parsel": "56"
}
```

## 🎯 OCR Yöntemi Değiştirme

`ocr_processor.py` dosyasında:

```python
# Satır 11:
OCR_METHOD = "easyocr"  # veya "pytesseract"
```

**EasyOCR için:**
```python
OCR_METHOD = "easyocr"
```

**Tesseract için:**
```python
OCR_METHOD = "pytesseract"
```

## ⚡ Performans

### EasyOCR
- Belge başına: ~5-10 saniye
- İlk kullanım: +2 dakika (model indirme)
- Doğruluk: ⭐⭐⭐⭐⭐ (Mükemmel)

### Tesseract
- Belge başına: ~1-3 saniye
- İlk kullanım: Hemen hazır
- Doğruluk: ⭐⭐⭐⭐ (Çok iyi)

## 🐛 Sorun Giderme

### "easyocr kurulu değil"
```bash
pip install easyocr
```

### "pytesseract kurulu değil"
```bash
pip install pytesseract
pip install pdf2image
```
+ Tesseract binary kurulumu gerekli!

### "OCR kullanılamadı"
- Hiçbir OCR yöntemi kurulmamış
- Program sadece AI görsel analizi yapacak
- OCR kurmak opsiyonel, sistem yine çalışır

### EasyOCR İlk Kullanımda Çok Uzun Sürüyor
- Normal! İlk seferde model indiriyor (~500MB)
- Sabırla bekleyin, sadece 1 kere olacak
- Sonraki kullanımlarda hızlı

### Tesseract "Türkçe karakterler yanlış"
- Türkçe dil paketi kurulu mu kontrol edin
- Tesseract kurulumda "Turkish" seçeneğini işaretleyin

## 📈 OCR vs OCR'sız Karşılaştırma

### OCR'sız (Sadece AI Görsel)
```
Mahalle: Beşevler
AI Okuması: "Başevler" ❌ (Görsel benzerlik)
```

### OCR ile (OCR + AI)
```
OCR: "Beşevler"
AI Kontrol: Görselde "Beşevler" ✅
Sonuç: "Beşevler" ✅ DOĞRU
```

## 🎉 Sonuç

OCR kullanmak:
- ✅ Daha doğru sonuçlar
- ✅ Mahalle/rakam hatalarını azaltır
- ✅ İki katmanlı doğrulama (OCR + AI)
- ⚠️ Biraz daha yavaş
- ⚠️ Ek kurulum gerekebilir

**Öneri:** EasyOCR kurun, çok daha doğru sonuçlar alırsınız!

```bash
pip install easyocr
python main_duzenlenebilir.py
```

---

**🔥 OCR + AI = En Doğru Gayrimenkul Değerleme!**
