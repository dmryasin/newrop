# Güncellenmiş Rapor Sistemi - Kullanım Kılavuzu

## 🔥 YENİ ÖZELLİKLER

### 1. Geliştirilmiş Veri Okuma
- ✅ **Kat Planı Analizi**: AI kat planından oda sayısı ve m² hesaplar
- ✅ **m² Tablosu**: Alan bilgilerini m² tablosundan doğru okur
- ✅ **Enerji Belgesi**: Enerji sınıfı, tüketim, CO2 salımı vb. tüm verileri çıkarır
- ✅ **Mahalle Doğruluğu**: Mahalle adını harf harf kontrol eder, yanlış okuma yapmaz

### 2. Test ve Kullanım

```bash
python test_gelismis_ai.py
```

Bu script ile:
- Kat planı analizi test edilir
- m² tablosu okuma test edilir  
- Enerji belgesi analizi test edilir
- Mahalle okuma doğruluğu kontrol edilir

### 3. Sorun Çözümleri

#### Mahalle Yanlış Okunuyor
**Çözüm:** AI'ya özel talimat verildi - mahalle adını 3 kere kontrol ediyor

#### Enerji Belgesi İşlenmemiş
**Çözüm:** Gelişmiş AI processor enerji belgelerini tam analiz ediyor:
- Enerji sınıfı
- Yıllık tüketim
- CO2 salımı
- Isıtma/soğutma sistemleri

#### Kat Planından m² Okumuyor
**Çözüm:** AI şimdi kat planını analiz edip:
- Her odayı tanımlıyor
- Her odanın m²'sini hesaplıyor
- Toplam net alanı hesaplıyor
- Oda sayısını (2+1, 3+1 vb.) belirliyor

#### m² Tablosu Kullanılmıyor
**Çözüm:** AI m² tablosunu öncelikli veri kaynağı olarak kullanıyor:
- Brüt alan
- Net alan
- Ortak alan payı
- Kat alanları

## 📊 Örnek Test Senaryosu

### Yüklediğiniz Dosyalar:
1. Tapu senedi → Ada, parsel, malik bilgileri
2. Kat planı → AI odalari sayıyor, m² hesaplıyor
3. m² tablosu → Brüt/net alan bilgileri
4. Enerji kimlik belgesi → Enerji sınıfı, tüketim
5. Gayrimenkul fotoğrafları → Raporda gösterilecek

### AI'nın Yapacakları:

**1. Kat Planı Analizi**
```
✅ Kat planında 3 oda tespit edildi
✅ Salon: 25 m²
✅ Yatak odası 1: 15 m²
✅ Yatak odası 2: 12 m²
✅ Mutfak: 10 m²
✅ Banyo: 6 m²
✅ Toplam net alan: 68 m²
✅ Oda sayısı: 2+1
```

**2. m² Tablosu Analizi**
```
✅ Brüt alan: 95 m²
✅ Net alan: 68 m²
✅ Ortak alan payı: 15 m²
✅ Balkon: 8 m²
```

**3. Enerji Belgesi Analizi**
```
✅ Enerji sınıfı: C
✅ Yıllık enerji tüketimi: 180 kWh/m²·yıl
✅ CO2 salımı: 35 kg/m²·yıl
✅ Isıtma: Doğalgaz kombi
✅ Soğutma: Klima
```

**4. Mahalle Kontrolü**
```
❌ YANLIŞ: "Beşevler" → "Başevler"
✅ DOĞRU: AI 3 kere kontrol etti → "Beşevler"
```

## 🎯 Kullanım

### Adım 1: Gelişmiş AI'yı Aktif Et

`main_duzenlenebilir.py` dosyasında:

```python
# ESKİ:
from ai_processor import AIBelgeIsleyici

# YENİ:
from ai_processor_gelismis import GelismisAIBelgeIsleyici as AIBelgeIsleyici
```

### Adım 2: Programı Çalıştır

```bash
python main_duzenlenebilir.py
```

### Adım 3: Dosyaları Yükle

1. Tapu senedi ✅
2. **Kat planı** ✅ (AI analiz edecek)
3. **m² tablosu** ✅ (AI öncelik verecek)
4. **Enerji kimlik belgesi** ✅ (AI tam analiz edecek)
5. İmar durumu ✅
6. Fotoğraflar ✅

### Adım 4: Analiz Et

"Dosyaları Analiz Et (AI)" → AI şimdi:
- Kat planından oda ve m² hesaplar
- m² tablosundan tüm alanları çıkarır
- Enerji belgesinden tüm verileri alır
- Mahalle adını 3 kere kontrol eder

### Adım 5: Kontrol Et

Tüm alanlar artık düzenlenebilir!
- Mahalle yanlış mı? → Düzelt!
- m² eksik mi? → Manuel gir!
- Enerji sınıfı yok mu? → Ekle!

### Adım 6: Rapor Oluştur

"Rapor Oluştur" → Tüm veriler raporda olacak:
- ✅ Kat planı analizi
- ✅ m² tablosu bilgileri
- ✅ Enerji belgesi detayları
- ✅ Doğru mahalle adı

## 🐛 Sorun Giderme

### Hala Mahalle Yanlış
1. Manuel düzeltin (artık düzenlenebilir!)
2. Tapu senedinde doğru yazıyor mu kontrol edin
3. AI log'larını kontrol edin

### Kat Planı Analiz Edilmedi
1. Kat planı resim formatında mı? (JPG, PNG)
2. Görselin kalitesi yeterli mi?
3. Oda isimleri ve m² değerleri okunabilir mi?

### m² Tablosu Kullanılmadı
1. Tablo net görülebiliyor mu?
2. Satır ve sütunlar düzgün mü?
3. Rakamlar okunabilir mi?

### Enerji Belgesi İşlenmedi
1. Belge formatı PDF veya resim mi?
2. Enerji sınıfı (A, B, C vb.) açıkça yazıyor mu?
3. Tüketim değerleri görülebiliyor mu?

## 📞 İletişim

Sorunlar devam ediyorsa:
1. `test_gelismis_ai.py` scriptini çalıştırın
2. Çıktıları kontrol edin
3. Hangi belge türünde sorun olduğunu tespit edin
4. Manuel düzeltme yapın (alanlar düzenlenebilir!)

---

**🎉 Gelişmiş AI ile artık daha doğru ve eksiksiz raporlar!**
