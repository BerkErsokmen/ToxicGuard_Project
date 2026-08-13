import pandas as pd
df = pd.read_csv("analiz_sonuçları/toxicguard_694_genis_test_seti_analiz_V1_V2_V3_V4_V5_V5_2_V5_02_V5_22.csv", sep=";")

# Let's check columns for level labels:
v1_lbls = df['V1_seviye'].value_counts()
v52_lbls = df['V5_2_seviye'].value_counts()
v522_lbls = df['V5_22_seviye'].value_counts()

print("V1 levels:\n", v1_lbls)
print("V5_2 levels:\n", v52_lbls)
print("V5_22 levels:\n", v522_lbls)

# Sarcastic sentences:
print("\nSome sarcastic sentences and their predictions:")
sarcastic = df[df['yorum'].str.contains('genius|vizyon|şerefsiz|manyak|idiot|hell', case=False, na=False)].head(15)
for idx, row in sarcastic.iterrows():
    print(f"Yorum: {row['yorum']}")
    print(f"  V1: {row['V1_seviye']} (score: {row['V1_genel_skor']:.2f})")
    print(f"  V5.2: {row['V5_2_seviye']} (score: {row['V5_2_genel_skor']:.2f})")
    print(f"  V5.22: {row['V5_22_seviye']} (score: {row['V5_22_genel_skor']:.2f})")
