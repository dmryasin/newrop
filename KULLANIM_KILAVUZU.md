# Gayrimenkul Değerleme Rapor Sistemi - Kullanım Kılavuzu

## 🎯 Sistem Özellikleri

Bu sistem, SPK standartlarına uygun gayrimenkul değerleme raporları oluşturur ve **yapay zeka ile emsal analizi** yaparak gayrimenkulün piyasa değerini hesaplar.

### Temel Özellikler:
- ✅ Otomatik belge sınıflandırma (Tapu, İmar, Takbis, Enerji Kimlik Belgesi, vb.)
- ✅ AI ile belge analizi ve veri çıkarma
- ✅ **Emsal karşılaştırma ve değerleme**
- ✅ **AI tabanlı birim m² değeri hesaplama**
- ✅ SPK standartlarına uygun PDF rapor oluşturma
- ✅ Profesyonel rapor formatı (örnek rapor şablonu kullanılır)

---

## 📋 Kullanım Adımları

### 1. Gayrimenkul Belgelerini Yükleyin

**"Dosya Ekle (Belge/Fotoğraf)"** butonuna tıklayın ve şu belgeleri yükleyin:
- 📄 Tapu senedi
- 📄 İmar durumu belgesi
- 📄 Takbis (kadastral harita)
- 📄 Enerji kimlik belgesi
- 📄 Yapı ruhsatı
- 📸 Gayrimenkul fotoğrafları (iç/dış mekan)

**Desteklenen formatlar:** PDF, JPG, PNG, TIFF

---

### 2. Emsal Ekleyin (Yeni Özellik!)

**"Emsal Ekle (İlan/Fotoğraf)"** butonuna tıklayın ve emsal verileri yükleyin:

#### Emsal Olarak Kabul Edilenler:
1. **Satış İlanı Ekran Görüntüleri**
   - sahibinden.com ekran görüntüleri
   - hurriyetemlak.com ilanları
   - emlakjet, zingat vb. platformlardan ilanlar
   
2. **Emsal Gayrimenkul Bilgileri**
   - Fiyat, alan (m²), konum içeren görseller
   - Benzer gayrimenkul fotoğrafları + bilgi notu
   
3. **Emsal Değerleme Belgeleri**
   - Başka değerleme raporlarından sayfalar

#### Emsal Örnekleri:
```
✅ İyi Emsal Örneği:
   - Ekran görüntüsünde açıkça görünen:
     * Adres: Çankaya, Ankara
     * Alan: 120 m²
     * Fiyat: 2.500.000 TL
     * Özellikler: 3+1, 5. kat, Site içi

✅ İyi Emsal Örneği:
   - Manuel not eklenmiş fotoğraf:
     * Benzer gayrimenkul
     * "Bu gayrimenkul 140 m², 3.200.000 TL'ye satıldı"
     
❌ Kötü Emsal Örneği:
   - Sadece gayrimenkul fotoğrafı (fiyat/alan bilgisi yok)
   - Bulanık, okunamayan ilanlar
```

**Not:** En az 3-5 emsal yüklemek, daha güvenilir değerleme için önerilir.

---

### 3. Belgeleri Analiz Edin

**"Dosyaları Sınıflandır ve Analiz Et (AI)"** butonuna tıklayın.

Sistem şunları yapar:
1. ✅ Tüm belgeleri otomatik olarak sınıflandırır
2. ✅ Belgelerden gayrimenkul bilgilerini çıkarır (adres, ada, parsel, alan, vb.)
3. ✅ **Emsalleri analiz eder** (her emsalden fiyat, alan, konum bilgisi çıkarır)
4. ✅ **Emsal karşılaştırma yapar** (benzerlik analizi, düzeltme katsayıları)
5. ✅ **Tahmini değer hesaplar** (ağırlıklı ortalama birim m² fiyatı × alan)
6. ✅ Form alanlarını otomatik doldurur

---

### 4. Raporu Oluşturun

**"Rapor Oluştur"** butonuna tıklayın.

Oluşturulan rapor şunları içerir:
- 📋 Kapak sayfası
- 📋 Yönetici özeti
- 📋 Rapor bilgileri ve kapsam
- 📋 Gayrimenkul tanımı ve konum
- 📋 Tapu bilgileri
- 📋 Fiziksel özellikler
- 📋 İmar durumu
- 📸 Gayrimenkul fotoğrafları (AI açıklamalı)
- 📊 **EMSAL KARŞILAŞTIRMA VE DEĞERLEME**
  - Emsal analiz tablosu
  - Birim fiyat karşılaştırmaları
  - Benzerlik puanları
  - Düzeltme katsayıları
  - **TAHMİNİ DEĞER ve değer aralığı**
  - Emsal fotoğrafları
- 📋 Değerleme yöntemi ve analiz
- 📋 Genel değerlendirme ve sonuç

Rapor **`raporlar/`** klasörüne PDF olarak kaydedilir.

---

## 🎯 Emsal Değerleme Nasıl Çalışır?

### 1. Emsal Analizi
AI, her emsal görselden şu bilgileri çıkarır:
- Adres ve konum
- Alan (m²)
- Toplam fiyat
- Birim fiyat (TL/m²)
- Özellikler (oda sayısı, kat, yaş, vb.)

### 2. Benzerlik Analizi
Değerlenen gayrimenkul ile her emsal karşılaştırılır:
- Konum benzerliği
- Fiziksel özellik benzerliği
- Yaş farkı
- Kat farkı

### 3. Düzeltme Katsayıları
Farklılıklar için düzeltme uygulanır:
- Konum farkı: +/- %0-20
- Yaş farkı: +/- %0-15
- Kat farkı: +/- %0-10
- Özellik farkları: +/- %0-15

### 4. Değer Hesaplama
```
Tahmini Değer = Ortalama Düzeltilmiş Birim Fiyat × Alan
Değer Aralığı = [Min Birim Fiyat × Alan, Max Birim Fiyat × Alan]
```

**Örnek:**
```
Değerlenen Gayrimenkul: 120 m², Çankaya, 3+1, 10 yaşında

Emsal 1: 115 m², 2.400.000 TL → 20.870 TL/m², Benzerlik: %90
Emsal 2: 125 m², 2.750.000 TL → 22.000 TL/m², Benzerlik: %85
Emsal 3: 130 m², 2.600.000 TL → 20.000 TL/m², Benzerlik: %80

Düzeltmeler sonrası:
Ortalama Birim Fiyat: 21.200 TL/m²

TAHMİNİ DEĞER: 21.200 × 120 = 2.544.000 TL
Değer Aralığı: 2.400.000 - 2.640.000 TL
```

---

## 📁 Örnek Rapor Formatı

Sistem, `C:\Users\dmrya\Downloads\ilovepdf_pages-to-jpg` klasöründeki örnek rapor formatını referans alır.

Bu klasörde 30 sayfa örnek rapor bulunmaktadır:
- `ornekrapor_page-0001.jpg` → Kapak sayfası formatı
- `ornekrapor_page-0002.jpg` → İçindekiler
- `ornekrapor_page-0003.jpg` → Konum bilgileri
- ... (devam eden sayfalar)

AI, bu örnek formatı analiz ederek benzer stil ve yapıda raporlar oluşturur.

---

## ⚙️ Teknik Gereksinimler

### Gerekli Kütüphaneler
```bash
pip install anthropic reportlab Pillow
```

### API Key Ayarı
`config.json` dosyasına API key ekleyin:
```json
{
    "anthropic_api_key": "YOUR_API_KEY_HERE"
}
```

Veya environment variable olarak ayarlayın:
```bash
export ANTHROPIC_API_KEY="your_key_here"
```

---

## 🔧 İpuçları

### Emsal Seçimi
- ✅ Mümkün olduğunca yakın konumdan emsaller seçin
- ✅ Benzer özelliklere sahip gayrimenkuller tercih edin
- ✅ Güncel ilanlar kullanın (son 3-6 ay)
- ✅ En az 3-5 emsal yükleyin
- ❌ Çok farklı özelliklerdeki gayrimenkuller uygun değil

### Dosya Boyutları
- Resimler otomatik olarak optimize edilir
- Büyük PDF'ler (>10MB) hata verebilir - küçültmeyi deneyin
- Çok bulanık görseller AI tarafından okunamayabilir

### Veri Doğruluğu
- AI'ın çıkardığı verileri kontrol edin
- Gerekirse manuel düzeltme yapın
- Emsal sayısı arttıkça değerleme güvenilirliği artar

---

## 🆘 Sorun Giderme

### "API key bulunamadı" hatası
→ `config.json` dosyasını kontrol edin veya environment variable ayarlayın

### "Dosya çok büyük" hatası
→ Görselleri sıkıştırın veya daha küçük boyutta kaydedin

### Emsal analiz edilemedi
→ Görselin net ve okunabilir olduğundan emin olun
→ Fiyat ve alan bilgilerinin açıkça görünür olması gerekir

### Rapor oluşturulamadı
→ Tüm gerekli kütüphanelerin yüklü olduğunu kontrol edin
→ `raporlar/` klasörüne yazma izniniz olduğundan emin olun

---

## 📞 Ek Bilgi

- **Rapor Geçerliliği:** 6 ay
- **Değerleme Standardı:** SPK/TDUB/IVS
- **Rapor Formatı:** PDF (A4)
- **Dil:** Türkçe

---

**Not:** Bu sistem sadece teknik bir değerleme aracıdır. Resmi değerleme raporları için lisanslı değerleme uzmanı onayı gereklidir.
