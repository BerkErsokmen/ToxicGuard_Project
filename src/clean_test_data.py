import pandas as pd
import os
from src.data_cleaning import clean_text

def clean_kaggle_test_data():
    """
    Kaggle'dan gelen test.csv ve test_labels.csv dosyalarını birleştirir,
    kullanılmayan (-1 etiketli) verileri atar ve metinleri temizler.
    """
    print("Test verileri yükleniyor...")
    test_path = 'datasset/test.csv'
    labels_path = 'datasset/test_labels.csv'
    
    if not os.path.exists(test_path) or not os.path.exists(labels_path):
        print("Hata: test.csv veya test_labels.csv bulunamadı.")
        return
        
    df_test = pd.read_csv(test_path)
    df_labels = pd.read_csv(labels_path)
    
    print(f"Orijinal test verisi boyutu: {len(df_test)}")
    
    # İki veri setini birleştir
    df_merged = pd.merge(df_test, df_labels, on='id')
    
    # Kaggle test setinde '-1' etiketine sahip olan satırlar değerlendirmede kullanılmıyor
    # Bunları filtrele
    df_valid = df_merged[df_merged['toxic'] != -1].copy()
    print(f"Kullanılabilir (-1 olmayan) test verisi boyutu: {len(df_valid)}")
    
    print("\n--- Test Verisi Temizleniyor ---")
    print("Bu işlem biraz sürebilir, arka planda çalışıyor...")
    
    # Temizleme işlemini uygula
    df_valid['cleaned_text'] = df_valid['comment_text'].apply(clean_text)
    
    # Boş kalan satırları temizle
    df_valid = df_valid[df_valid['cleaned_text'].str.strip() != ""]
    
    # Sadece gerekli sütunları tut
    label_columns = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']
    df_final = df_valid[['cleaned_text'] + label_columns]
    
    # Çıktıyı kaydet
    output_dir = 'data'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'gercek_temizlenmis_test_veri.csv')
    
    df_final.to_csv(output_file, index=False)
    
    print(f"\nİşlem tamam!")
    print(f"Temiz test verisi '{output_file}' dosyasına kaydedildi.")
    print(f"Toplam temizlenen test kaydı sayısı: {len(df_final)}")
    print("\nİlk 3 satır örnek:")
    print(df_final.head(3).to_string())

if __name__ == "__main__":
    clean_kaggle_test_data()
