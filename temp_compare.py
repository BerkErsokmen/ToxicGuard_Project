import pandas as pd
import sys

import os

BASE = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE, 'analiz_sonuçları', 'sinir_testi_toksik_veriseti_v2_analiz_V1_V2_V3_V4_V5_V5_2_V5_02_V5_22.csv')

try:
    df = pd.read_csv(file_path, sep=';')
except Exception as e:
    print("Error reading file:", e)
    sys.exit(1)

versions = ['V1', 'V2', 'V3', 'V4', 'V5', 'V5_2', 'V5_02', 'V5_22']
print("=== Sınır Testi (Boundary Test) Karşılaştırma Sonuçları ===")
print("Toplam Cümle Sayısı:", len(df))
print("-" * 50)

for ver in versions:
    col_seviye = f"{ver}_seviye"
    if col_seviye in df.columns:
        counts = df[col_seviye].value_counts().to_dict()
        guvenli = counts.get('Güvenli', 0)
        dikkat = counts.get('Dikkat', 0)
        toksik = counts.get('Toksik', 0)
        
        # Calculate some average toxicity
        col_skor = f"{ver}_genel_skor"
        avg_skor = df[col_skor].mean() if col_skor in df.columns else 0.0
        
        print(f"{ver.ljust(6)} | Güvenli: {guvenli:<4} | Dikkat: {dikkat:<3} | Toksik: {toksik:<3} | Ort. Skor: {avg_skor:.3f}")

print("-" * 50)
