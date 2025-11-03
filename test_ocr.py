"""
OCR + AI Test Scripti
"""

from ocr_processor import OCRProcessor, tesseract_yuklu_mu, tesseract_kurulum_yardimi
import os

def test_ocr():
    """OCR sistemini test et"""
    
    print("="*60)
    print("OCR + AI DOĞRULAMA SİSTEMİ TEST")
    print("="*60)
    
    # 1. Tesseract kontrolü
    print("\n1️⃣ Tesseract OCR Kontrolü:")
    if tesseract_yuklu_mu():
        print("  ✅ Tesseract yüklü!")
    else:
        print("  ❌ Tesseract yüklü değil!")
        print("\n" + tesseract_kurulum_yardimi())
        return
    
    # 2. OCR Processor oluştur
    print("\n2️⃣ OCR Processor Oluşturuluyor:")
    try:
        ocr = OCRProcessor()
        print("  ✅ OCR Processor hazır!")
    except Exception as e:
        print(f"  ❌ Hata: {e}")
        return
    
    # 3. Test dosyası kontrol
    print("\n3️⃣ Test Dosyası:")
    test_dosyalari = []
    
    # Desktop'ta test dosyaları ara
    desktop = os.path.expanduser("~/Desktop")
    for dosya in ['tapu.jpg', 'tapu.png', 'test.jpg', 'belge.jpg']:
        yol = os.path.join(desktop, dosya)
        if os.path.exists(yol):
            test_dosyalari.append(yol)
    
    if not test_dosyalari:
        print("  ⚠️ Test dosyası bulunamadı!")
        print("  💡 Desktop'a 'tapu.jpg' veya 'test.jpg' koyun")
        return
    
    test_dosya = test_dosyalari[0]
    print(f"  ✅ Test dosyası: {os.path.basename(test_dosya)}")
    
    # 4. OCR Testi
    print("\n4️⃣ OCR Testi:")
    print("  📄 Metin çıkarılıyor...")
    
    try:
        ocr_metin = ocr.ocr_calistir(test_dosya)
        print(f"  ✅ OCR tamamlandı ({len(ocr_metin)} karakter)")
        print(f"\n  📋 OCR Çıktısı:")
        print("  " + "-"*50)
        print("  " + ocr_metin[:200].replace('\n', '\n  '))
        if len(ocr_metin) > 200:
            print(f"  ... (toplam {len(ocr_metin)} karakter)")
        print("  " + "-"*50)
    except Exception as e:
        print(f"  ❌ OCR Hatası: {e}")
        return
    
    # 5. AI Doğrulama Testi
    print("\n5️⃣ AI Doğrulama Testi:")
    print("  🤖 AI düzeltme yapılıyor...")
    
    try:
        ai_sonuc = ocr.ai_dogrula_ve_duzenle(ocr_metin, "Tapu Belgesi")
        print("  ✅ AI doğrulama tamamlandı!")
        
        if 'duzeltilmis_metin' in ai_sonuc:
            print(f"\n  📋 Düzeltilmiş Metin:")
            print("  " + "-"*50)
            print("  " + ai_sonuc['duzeltilmis_metin'][:200].replace('\n', '\n  '))
            print("  " + "-"*50)
        
        if 'onemli_bilgiler' in ai_sonuc:
            print(f"\n  📊 Çıkarılan Bilgiler:")
            for key, value in ai_sonuc['onemli_bilgiler'].items():
                if value and value != "null":
                    print(f"    • {key}: {value}")
        
        if 'duzeltme_notlari' in ai_sonuc:
            print(f"\n  📝 Düzeltme Notları:")
            print(f"    {ai_sonuc['duzeltme_notlari']}")
            
    except Exception as e:
        print(f"  ❌ AI Doğrulama Hatası: {e}")
        return
    
    # 6. Tam İşlem Testi
    print("\n6️⃣ Tam İşlem Testi:")
    try:
        sonuc = ocr.dosya_isle(test_dosya, "Tapu Belgesi")
        
        if sonuc['basarili']:
            print("  ✅ Tüm işlemler başarılı!")
        else:
            print("  ⚠️ Bazı hatalar oluştu")
            
    except Exception as e:
        print(f"  ❌ Hata: {e}")
    
    print("\n" + "="*60)
    print("TEST TAMAMLANDI!")
    print("="*60)
    
    print("\n💡 Sonraki Adımlar:")
    print("  1. OCR kalitesini artırmak için görseli iyileştirin")
    print("  2. Ana programda OCR kullanın")
    print("  3. Sonuçları manuel kontrol edin")


if __name__ == "__main__":
    test_ocr()
