import pandas as pd
import json
import os

def export_data():
    csv_path = 'data/gercek_temizlenmis_test_veri.csv'
    
    if not os.path.exists(csv_path):
        print(f"Hata: {csv_path} bulunamadı.")
        return
        
    print(f"{csv_path} okunuyor...")
    df = pd.read_csv(csv_path)
    
    # 1. JSON olarak kaydet
    json_path = 'data/gercek_temizlenmis_test_veri.json'
    # 'records' formatı Excel derdi olmadan okumayı sağlar 
    # (Örnek: [{"cleaned_text": "...", "toxic": 0, ...}, ...])
    df.to_json(json_path, orient='records', force_ascii=False, indent=4)
    print(f"JSON formatında kaydedildi: {json_path}")
    
    # 2. Sadece metinleri içeren basit bir TXT olarak kaydet (Kopyalaması en kolayı)
    txt_path = 'data/test_yorumlari_sadece_metin.txt'
    with open(txt_path, 'w', encoding='utf-8') as f:
        for text in df['cleaned_text']:
            # Satır sonlarını boşlukla değiştirerek tek bir metni tek satırda tutalım
            clean_line = str(text).replace('\n', ' ').replace('\r', ' ')
            f.write(f"{clean_line}\n")
    print(f"Sadece metinler TXT formatında kaydedildi: {txt_path}")

if __name__ == "__main__":
    export_data()
