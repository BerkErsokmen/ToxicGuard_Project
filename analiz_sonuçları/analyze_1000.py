
import csv
from collections import defaultdict

import os

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

results = []
with open(os.path.join(BASE, 'analiz_sonuçları', 'toxicguard_1000_genis_test_seti_v5_2_sonuclar.csv'), encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        results.append(row)

labels = []
with open(os.path.join(BASE, 'analiz_edilecekler', 'toxicguard_1000_genis_test_seti.csv'), encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        labels.append(row)

cat_stats = defaultdict(lambda: {'toplam': 0, 'guvenli': 0, 'dikkat': 0, 'toksik': 0})

for i, (res, lbl) in enumerate(zip(results, labels)):
    cat = lbl.get('kategori', '').strip()
    seviye = res.get('seviye', '').strip()
    cat_stats[cat]['toplam'] += 1
    if seviye == 'Guvenli' or seviye == 'Güvenli':
        cat_stats[cat]['guvenli'] += 1
    elif seviye == 'Dikkat':
        cat_stats[cat]['dikkat'] += 1
    elif seviye == 'Toksik':
        cat_stats[cat]['toksik'] += 1

print('=== KATEGORI BAZLI ANALIZ ===')
for cat, s in sorted(cat_stats.items()):
    t = s['toplam']
    if t == 0:
        continue
    pct_g = round(s['guvenli']/t*100, 1)
    pct_d = round(s['dikkat']/t*100, 1)
    pct_t = round(s['toksik']/t*100, 1)
    print(f"\n{cat}")
    print(f"  Toplam: {t}")
    print(f"  Guvenli: {s['guvenli']} ({pct_g} pct)")
    print(f"  Dikkat:  {s['dikkat']} ({pct_d} pct)")
    print(f"  Toksik:  {s['toksik']} ({pct_t} pct)")

total = len(results)
guvenli = sum(1 for r in results if r.get('seviye','').strip() in ['Guvenli','Güvenli'])
dikkat  = sum(1 for r in results if r.get('seviye','').strip() == 'Dikkat')
toksik  = sum(1 for r in results if r.get('seviye','').strip() == 'Toksik')
print(f'\n=== GENEL TOPLAM: {total} kayit ===')
print(f'Guvenli: {guvenli} ({round(guvenli/total*100,1)} pct)')
print(f'Dikkat:  {dikkat}  ({round(dikkat/total*100,1)} pct)')
print(f'Toksik:  {toksik}  ({round(toksik/total*100,1)} pct)')

scores = [float(r.get('toksisite_skoru', 0)) for r in results]
print(f'\nOrtalama skor: {round(sum(scores)/len(scores),3)}')
print(f'Min skor: {round(min(scores),3)}')
print(f'Max skor: {round(max(scores),3)}')

# Dogru/yanlis siniflandirma tahmini
print('\n=== BEKLENEN vs GERCEK (tahmini) ===')

correct_explicit = 0
wrong_explicit = 0
correct_clean = 0
wrong_clean = 0
correct_friendly = 0
wrong_friendly = 0
correct_sarcasm = 0
wrong_sarcasm = 0

for res, lbl in zip(results, labels):
    cat = lbl.get('kategori', '').strip()
    seviye = res.get('seviye','').strip()

    if 'Explicit Toxic' in cat:
        if seviye == 'Toksik':
            correct_explicit += 1
        else:
            wrong_explicit += 1

    elif 'Clean' in cat:
        if seviye == 'Guvenli' or seviye == 'Güvenli':
            correct_clean += 1
        else:
            wrong_clean += 1

    elif 'Friendly Profanity' in cat:
        if seviye in ['Guvenli','Güvenli','Dikkat']:
            correct_friendly += 1
        else:
            wrong_friendly += 1

    elif 'Implicit Sarcastic' in cat:
        if seviye in ['Guvenli','Güvenli','Dikkat']:
            correct_sarcasm += 1
        else:
            wrong_sarcasm += 1

print(f"Explicit Toxic:     Dogru={correct_explicit}, Yanlis={wrong_explicit} (acc={round(correct_explicit/(correct_explicit+wrong_explicit)*100,1)} pct)")
print(f"Clean:              Dogru={correct_clean}, Yanlis={wrong_clean} (acc={round(correct_clean/(correct_clean+wrong_clean)*100,1)} pct)")
print(f"Friendly Profanity: Dogru={correct_friendly}, Yanlis={wrong_friendly} (acc={round(correct_friendly/(correct_friendly+wrong_friendly)*100,1)} pct)")
print(f"Implicit Sarcastic: Dogru={correct_sarcasm}, Yanlis={wrong_sarcasm} (acc={round(correct_sarcasm/(correct_sarcasm+wrong_sarcasm)*100,1)} pct)")
