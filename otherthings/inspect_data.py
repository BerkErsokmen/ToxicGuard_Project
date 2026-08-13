import pandas as pd
df = pd.read_csv("analiz_sonuçları/toxicguard_694_genis_test_seti_analiz_V1_V2_V3_V4_V5_V5_2_V5_02_V5_22.csv", sep=";")
print("Columns:", df.columns.tolist())
print(df.head(2))
