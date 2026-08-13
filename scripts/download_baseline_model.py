"""
Baseline ToxicBERT modelini projeye kalıcı olarak indir.
Bunu BİR KEZ çalıştır: python scripts/download_baseline_model.py
Sonrasında internet olmasa da çalışır.
"""

import os
import sys

# Proje kökü
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_MODEL_DIR = os.path.join(PROJECT_ROOT, 'models', 'baseline_toxic_bert')

def download():
    print("=" * 60)
    print("ToxicBERT Baseline - Yerel Indirme")
    print("=" * 60)
    
    if os.path.exists(os.path.join(LOCAL_MODEL_DIR, 'config.json')):
        print("\n[OK] Model zaten mevcut: " + LOCAL_MODEL_DIR)
        print("Tekrar indirmeye gerek yok.")
        return

    print("\nModel indiriliyor: unitary/toxic-bert")
    print("Hedef klasor: " + LOCAL_MODEL_DIR)
    print("Bu islem yaklasik 1-2 dakika surer (438MB)...\n")

    try:
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        os.makedirs(LOCAL_MODEL_DIR, exist_ok=True)

        print("-> Tokenizer indiriliyor...")
        tokenizer = AutoTokenizer.from_pretrained("unitary/toxic-bert")
        tokenizer.save_pretrained(LOCAL_MODEL_DIR)
        print("[OK] Tokenizer kaydedildi.")

        print("-> Model indiriliyor (438MB)...")
        model = AutoModelForSequenceClassification.from_pretrained("unitary/toxic-bert")
        model.save_pretrained(LOCAL_MODEL_DIR)
        print("[OK] Model kaydedildi.")

        print("\nTamamlandi! Model buraya kaydedildi:")
        print("   " + LOCAL_MODEL_DIR)
        print("\nArtik internet olmadan da calisir.")

    except Exception as e:
        print("\nHata: " + str(e))
        print("Internet baglantinizi kontrol edin.")
        sys.exit(1)

if __name__ == "__main__":
    download()
