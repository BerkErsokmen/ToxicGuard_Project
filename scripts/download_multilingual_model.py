import os
import sys

# Proje kökü
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_MODEL_DIR = os.path.join(PROJECT_ROOT, 'models', 'baseline_multilingual_toxic')

def download():
    print("=" * 60)
    print("Multilingual ToxicBERT Baseline - Yerel Indirme")
    print("=" * 60)
    
    if os.path.exists(os.path.join(LOCAL_MODEL_DIR, 'config.json')):
        print("\n[OK] Model zaten mevcut: " + LOCAL_MODEL_DIR)
        return

    print("\nModel indiriliyor: unitary/multilingual-toxic-xlm-roberta")
    print("Bu islem yaklasik 2-3 dakika surer (1.11GB). Lutfen bekleyin...\n")

    try:
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        os.makedirs(LOCAL_MODEL_DIR, exist_ok=True)

        print("-> Tokenizer indiriliyor...")
        tokenizer = AutoTokenizer.from_pretrained("unitary/multilingual-toxic-xlm-roberta")
        tokenizer.save_pretrained(LOCAL_MODEL_DIR)
        print("[OK] Tokenizer kaydedildi.")

        print("-> Model indiriliyor (1.11GB)...")
        model = AutoModelForSequenceClassification.from_pretrained("unitary/multilingual-toxic-xlm-roberta")
        model.save_pretrained(LOCAL_MODEL_DIR)
        print("[OK] Model kaydedildi.")

        print("\nTamamlandi! Artik internet olmadan V4 ile karsilastirma yapabilirsiniz.")

    except Exception as e:
        print("\nHata: " + str(e))
        sys.exit(1)

if __name__ == "__main__":
    download()
