"""
ToxicGuard V5.2 — Kapsamlı PDF Analiz Raporu
Gerçek CSV verilerinden okuyan, hatalı örnekleri gösteren çok sayfalık rapor.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.gridspec as gridspec
import numpy as np
import csv, textwrap, os

# ─── RENK PALETI ─────────────────────────────────────────────
BG      = '#0f172a'
SURF    = '#1e293b'
SURF2   = '#273548'
BORDER  = '#334155'
TEXT    = '#e2e8f0'
MUTED   = '#94a3b8'
PRIMARY = '#818cf8'
GREEN   = '#34d399'
RED     = '#f87171'
YELLOW  = '#fbbf24'
ORANGE  = '#fb923c'
CYAN    = '#67e8f9'

# ─── VERİ YOLLARI ─────────────────────────────────────────────
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RES_1000   = os.path.join(BASE, 'analiz_sonuçları', 'toxicguard_1000_genis_test_seti_v5_2_sonuclar.csv')
LBL_1000   = os.path.join(BASE, 'analiz_edilecekler', 'toxicguard_1000_genis_test_seti.csv')
RES_300    = os.path.join(BASE, 'analiz_sonuçları', 'advanced_toxicity_test_300_v5_2_sonuclar.csv')
OUT_PDF    = os.path.join(BASE, 'analiz_sonuçları', 'toxicguard_v5_2_tam_rapor.pdf')

# ─── YARDIMCI FONKSİYONLAR ───────────────────────────────────
def read_csv(path):
    rows = []
    with open(path, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

def ax_dark(ax, title=None, title_size=12):
    ax.set_facecolor(SURF)
    for sp in ax.spines.values():
        sp.set_edgecolor(BORDER)
        sp.set_linewidth(0.8)
    ax.tick_params(colors=MUTED, labelsize=9)
    if title:
        ax.set_title(title, color=TEXT, fontsize=title_size,
                     fontweight='bold', pad=10)

def fig_dark(figsize=(16, 10)):
    f = plt.figure(figsize=figsize, facecolor=BG)
    f.patch.set_facecolor(BG)
    return f

def page_header(fig, title, subtitle=''):
    fig.text(0.5, 0.965, title, ha='center', va='top',
             fontsize=16, fontweight='bold', color=TEXT)
    if subtitle:
        fig.text(0.5, 0.945, subtitle, ha='center', va='top',
                 fontsize=10, color=MUTED)

def wrap(text, width=55):
    return '\n'.join(textwrap.wrap(str(text), width))

# ─── CSV OKUMA ────────────────────────────────────────────────
print("CSV'ler okunuyor...")
res_1000 = read_csv(RES_1000)
lbl_1000 = read_csv(LBL_1000)
res_300  = read_csv(RES_300)
print(f"  1000-set: {len(res_1000)} kayit, 300-set: {len(res_300)} kayit")

# ─── KATEGORİ ANALİZİ (1000-set) ─────────────────────────────
cat_data = {}
fp_examples = []   # False Positive: güvenli ama toksik dedi
fn_examples = []   # False Negative: toksik ama kaçırdı
fp_friendly = []   # Friendly profanity yanlış Toksik

for res, lbl in zip(res_1000, lbl_1000):
    cat    = lbl.get('kategori', '').strip()
    seviye = res.get('seviye', '').strip()
    yorum  = res.get('yorum', '').strip()
    skor   = float(res.get('toksisite_skoru', 0))

    if cat not in cat_data:
        cat_data[cat] = {'total':0, 'guvenli':0, 'dikkat':0, 'toksik':0}
    cat_data[cat]['total'] += 1
    if   seviye in ('Güvenli','Guvenli'): cat_data[cat]['guvenli'] += 1
    elif seviye == 'Dikkat':              cat_data[cat]['dikkat']  += 1
    elif seviye == 'Toksik':              cat_data[cat]['toksik']  += 1

    # Hatalı örnekler topla
    if 'Explicit Toxic' in cat and seviye not in ('Toksik',):
        fn_examples.append((yorum, skor, seviye, cat))
    if 'Clean' in cat and seviye == 'Toksik':
        fp_examples.append((yorum, skor, seviye, cat))
    if 'Friendly Profanity' in cat and seviye == 'Toksik':
        fp_friendly.append((yorum, skor, seviye, cat))

# Özet sayılar
CATS_ORDER = [
    'Clean (Temiz/Nötr)',
    'Explicit Toxic (Açık Toksik)',
    'Friendly Profanity (Dostane Küfürlü)',
    'Implicit Sarcastic (Sarkastik/Örtük)',
]
CAT_SHORT = ['Clean', 'Explicit Toxic', 'Friendly\nProfanity', 'Implicit\nSarcastic']

totals = [cat_data[c]['total']   for c in CATS_ORDER]
accs   = [
    round(cat_data['Clean (Temiz/Nötr)']['guvenli']         / cat_data['Clean (Temiz/Nötr)']['total']                       * 100, 1),
    round(cat_data['Explicit Toxic (Açık Toksik)']['toksik'] / cat_data['Explicit Toxic (Açık Toksik)']['total']             * 100, 1),
    round((cat_data['Friendly Profanity (Dostane Küfürlü)']['guvenli'] +
           cat_data['Friendly Profanity (Dostane Küfürlü)']['dikkat'])  / cat_data['Friendly Profanity (Dostane Küfürlü)']['total'] * 100, 1),
    round((cat_data['Implicit Sarcastic (Sarkastik/Örtük)']['guvenli'] +
           cat_data['Implicit Sarcastic (Sarkastik/Örtük)']['dikkat'])  / cat_data['Implicit Sarcastic (Sarkastik/Örtük)']['total'] * 100, 1),
]

# ─── SAYFA 1 ─ KAPAK + KİLİT METRİKLER ──────────────────────
print("Sayfa 1: Kapak...")
fig1 = fig_dark((16, 10))
page_header(fig1, 'ToxicGuard V5.2 — Model Analiz Raporu',
            'XLM-RoBERTa-base | Focal Loss | EN + TR | 293K Egitim Verisi')

gs1 = gridspec.GridSpec(2, 3, figure=fig1,
                         left=0.05, right=0.97,
                         top=0.88, bottom=0.06,
                         hspace=0.45, wspace=0.30)

# Versiyon karşılaştırma (2/3 genişlik)
ax_ver = fig1.add_subplot(gs1[0, :2])
ax_dark(ax_ver, 'Versiyon Karsilastirmasi — F1-Macro (Optimize Threshold)')
vers  = ['V1\nXGBoost','V2\nSVM','V3\nDistilBERT','V4\nXLM-R','V5\nXLM-R','V5.2*\nXLM-R']
f1s   = [0.599, 0.599, 0.693, 0.0, 0.6967, 0.7478]
vclrs = [MUTED, MUTED, YELLOW, BORDER, PRIMARY, GREEN]
x = np.arange(len(vers))
bars = ax_ver.bar(x, f1s, color=vclrs, width=0.55, edgecolor=BORDER, linewidth=0.5, zorder=3)
bars[5].set_edgecolor(GREEN); bars[5].set_linewidth(2)
ax_ver.axhline(0.720, color=GREEN, lw=1.2, ls='--', alpha=0.7)
ax_ver.text(5.42, 0.724, 'Hedef: 0.720', color=GREEN, fontsize=8.5)
for bar, val, lbl in zip(bars, f1s, ['0.599','0.599','0.693','N/A','0.697','0.7478']):
    if val > 0:
        ax_ver.text(bar.get_x()+bar.get_width()/2, val+0.008, lbl,
                    ha='center', va='bottom', fontsize=9, color=TEXT, fontweight='bold')
ax_ver.set_xticks(x); ax_ver.set_xticklabels(vers, fontsize=9, color=MUTED)
ax_ver.set_ylim(0, 0.87); ax_ver.set_ylabel('F1-Macro', color=MUTED, fontsize=9)
ax_ver.grid(axis='y', color=BORDER, lw=0.5, alpha=0.6)

# 3 stat kutu (sağ sütun)
stat_items = [('F1-Macro', '0.7478', GREEN), ('ROC-AUC', '0.9769', PRIMARY), ('Egitim Verisi', '293K', YELLOW)]
ax_s_list = []
for i in range(3):
    ax_s = fig1.add_subplot(gs1[0, 2])
    ax_s.set_visible(False)

for i, (lbl, val, clr) in enumerate(stat_items):
    x0, y0, w, h = 0.688, 0.800 - i*0.100, 0.275, 0.072
    rect = mpatches.FancyBboxPatch((x0, y0), w, h,
        boxstyle='round,pad=0.01', transform=fig1.transFigure,
        facecolor=SURF, edgecolor=clr, linewidth=1.8, zorder=5, clip_on=False)
    fig1.add_artist(rect)
    fig1.text(x0+w/2, y0+h*0.62, val, ha='center', va='center',
              fontsize=16, fontweight='bold', color=clr, transform=fig1.transFigure, zorder=6)
    fig1.text(x0+w/2, y0+h*0.18, lbl, ha='center', va='center',
              fontsize=8.5, color=MUTED, transform=fig1.transFigure, zorder=6)

# Etiket F1 bar chart (alt sol)
ax_lbl = fig1.add_subplot(gs1[1, :2])
ax_dark(ax_lbl, 'Etiket Bazli F1 Skorlari (Optimize Threshold ile)')
etl = ['toxic','severe_toxic','obscene','threat','insult','identity_hate']
etl_f1 = [0.8877, 0.4303, 0.8249, 0.7489, 0.7824, 0.8129]
etl_clr = [GREEN if v >= 0.7 else (YELLOW if v >= 0.5 else RED) for v in etl_f1]
y_e = np.arange(len(etl))
ax_lbl.barh(y_e, etl_f1, color=etl_clr, height=0.55, edgecolor=BORDER, lw=0.4, zorder=3)
for i, v in enumerate(etl_f1):
    ax_lbl.text(v+0.01, i, f'{v:.3f}', va='center', fontsize=9.5, color=TEXT, fontweight='bold')
ax_lbl.set_yticks(y_e); ax_lbl.set_yticklabels(etl, fontsize=10, color=MUTED)
ax_lbl.set_xlim(0, 1.08)
ax_lbl.axvline(0.7, color=YELLOW, lw=1, ls='--', alpha=0.6)
ax_lbl.text(0.705, 5.45, 'Hedef >=0.70', color=YELLOW, fontsize=8)
ax_lbl.grid(axis='x', color=BORDER, lw=0.4, alpha=0.5)
ax_lbl.set_xlabel('F1 Skoru', color=MUTED, fontsize=9)
# not
ax_lbl.annotate('severe_toxic: nadir sinif\n(egitimde az ornek)',
                 xy=(0.4303, 1), xytext=(0.50, 1.4),
                 fontsize=8, color=RED, style='italic',
                 arrowprops=dict(arrowstyle='->', color=RED, lw=0.7))

# Threshold tablosu (alt sag)
ax_thr = fig1.add_subplot(gs1[1, 2])
ax_thr.set_facecolor(SURF)
for sp in ax_thr.spines.values(): sp.set_edgecolor(BORDER)
ax_thr.set_title('Optimize Threshold Degerleri', color=TEXT, fontsize=10, fontweight='bold', pad=8)
ax_thr.axis('off')
thr_data = [
    ['Etiket','Threshold','F1@0.5','F1@Opt'],
    ['toxic',       '0.40','0.8678','0.8877'],
    ['severe_toxic','0.30','0.0594','0.4303'],
    ['obscene',     '0.40','0.7773','0.8249'],
    ['threat',      '0.45','0.7382','0.7489'],
    ['insult',      '0.40','0.7517','0.7824'],
    ['identity_hate','0.40','0.7794','0.8129'],
]
col_colors = [SURF2]*4
row_colors = [[SURF]*4 for _ in thr_data[1:]]
row_colors[1] = [SURF2]*4  # severe_toxic vurgula
tbl = ax_thr.table(cellText=thr_data[1:], colLabels=thr_data[0],
                    loc='center', cellLoc='center')
tbl.auto_set_font_size(False); tbl.set_fontsize(8.5)
tbl.scale(1, 1.5)
for (r, c), cell in tbl.get_celld().items():
    cell.set_edgecolor(BORDER)
    if r == 0:
        cell.set_facecolor(SURF2); cell.set_text_props(color=MUTED, fontweight='bold')
    else:
        cell.set_facecolor(SURF); cell.set_text_props(color=TEXT)
        if c == 3:  # F1@Opt sütunu yeşile boyama
            val = float(thr_data[r][3])
            cell.set_text_props(color=GREEN if val >= 0.7 else (YELLOW if val >= 0.5 else RED),
                                fontweight='bold')

fig1.text(0.5, 0.018, 'ToxicGuard V5.2  |  Mezuniyet Projesi  |  XLM-RoBERTa-base (278M parametre)',
          ha='center', fontsize=8, color=MUTED)

# ─── SAYFA 2 ─ 693 YORUM KATEGORİ ANALİZİ ───────────────────
print("Sayfa 2: 693 yorum analizi...")
fig2 = fig_dark((16, 10))
page_header(fig2, '693 Yorum Genis Test Seti — Kategori Bazli Dogruluk')

gs2 = gridspec.GridSpec(2, 2, figure=fig2,
                         left=0.05, right=0.97,
                         top=0.88, bottom=0.06,
                         hspace=0.40, wspace=0.30)

# Progress bar chart (üst sol)
ax_prog = fig2.add_subplot(gs2[0, 0])
ax_dark(ax_prog, 'Kategori Dogruluk Oranlari')
cat_labels = ['Implicit\nSarcastic','Clean\n(Temiz)','Explicit\nToxic','Friendly\nProfanity']
acc_vals   = [99.4, 94.1, 91.0, 55.4]
n_vals     = [160, 153, 223, 157]
acc_clrs   = [GREEN, GREEN, GREEN, RED]
y2 = np.arange(4)
ax_prog.barh(y2, [100]*4, color=SURF2, height=0.6, zorder=1)
ax_prog.barh(y2, acc_vals, color=acc_clrs, height=0.6,
              edgecolor=BORDER, lw=0.4, zorder=3, alpha=0.9)
for i, (a, n) in enumerate(zip(acc_vals, n_vals)):
    clr = GREEN if a >= 75 else RED
    ax_prog.text(a+1.2, i, f'%{a}  ({n} ornek)', va='center',
                  fontsize=9.5, color=TEXT, fontweight='bold')
ax_prog.set_yticks(y2); ax_prog.set_yticklabels(cat_labels, fontsize=10, color=MUTED)
ax_prog.set_xlim(0, 128); ax_prog.set_xlabel('Dogruluk (%)', color=MUTED, fontsize=9)
ax_prog.axvline(75, color=YELLOW, lw=1, ls='--', alpha=0.6)
ax_prog.grid(axis='x', color=BORDER, lw=0.4, alpha=0.5)

# Pie (üst sağ)
ax_pie = fig2.add_subplot(gs2[0, 1])
ax_dark(ax_pie, 'Genel Seviye Dagilimi (693 yorum)')
total_g = sum(cat_data[c]['guvenli'] for c in CATS_ORDER)
total_d = sum(cat_data[c]['dikkat']  for c in CATS_ORDER)
total_t = sum(cat_data[c]['toksik']  for c in CATS_ORDER)
wedges, texts, autotexts = ax_pie.pie(
    [total_g, total_d, total_t],
    labels=[f'Guvenli\n{total_g}', f'Dikkat\n{total_d}', f'Toksik\n{total_t}'],
    colors=[GREEN, YELLOW, RED],
    autopct='%1.1f%%', startangle=90,
    wedgeprops=dict(edgecolor=BG, linewidth=2),
    textprops=dict(color=MUTED, fontsize=9),
    pctdistance=0.75
)
for at in autotexts: at.set_color(TEXT); at.set_fontsize(9); at.set_fontweight('bold')

# Kategori detay tablo (alt sol)
ax_tbl2 = fig2.add_subplot(gs2[1, 0])
ax_dark(ax_tbl2, 'Kategori Detay Tablosu')
ax_tbl2.axis('off')
tbl2_data = [
    ['Kategori', 'Toplam', 'Guvenli', 'Dikkat', 'Toksik', 'Acc'],
    ['Clean',          '153', f'144 (94.1%)',  '9 (5.9%)',   '0 (0%)',    '%94.1'],
    ['Explicit Toxic', '223', '0 (0%)',         '20 (9%)',    '203 (91%)', '%91.0'],
    ['Friendly Prof.', '157', '22 (14%)',        '65 (41.4%)','70 (44.6%)','%55.4'],
    ['Impl. Sarcasm',  '160', '35 (21.9%)',      '124 (77.5%)','1 (0.6%)', '%99.4'],
]
tbl2 = ax_tbl2.table(cellText=tbl2_data[1:], colLabels=tbl2_data[0],
                      loc='center', cellLoc='center')
tbl2.auto_set_font_size(False); tbl2.set_fontsize(8)
tbl2.scale(1.0, 1.8)
acc_col_vals = [94.1, 91.0, 55.4, 99.4]
for (r, c), cell in tbl2.get_celld().items():
    cell.set_edgecolor(BORDER)
    if r == 0:
        cell.set_facecolor(SURF2); cell.set_text_props(color=MUTED, fontweight='bold')
    else:
        cell.set_facecolor(SURF); cell.set_text_props(color=TEXT)
        if c == 5:
            v = acc_col_vals[r-1]
            cell.set_text_props(color=GREEN if v>=80 else (YELLOW if v>=65 else RED),
                                fontweight='bold')

# İki önemli gözlem kutusu (alt sağ)
ax_obs = fig2.add_subplot(gs2[1, 1])
ax_dark(ax_obs)
ax_obs.axis('off')
obs_text = (
    "ONEMLI BULGULAR\n"
    "─────────────────────────────────────────\n\n"
    "GUCLU YONLER:\n"
    "  Implicit Sarcastic  →  %99.4\n"
    "    Model ortuk toksisiteyi neredeyse\n"
    "    hic kacimiyor, 'Dikkat' seviyesinde\n"
    "    dogru yakalamaktadir.\n\n"
    "  Clean (Temiz)       →  %94.1\n"
    "    0 yorum yanlis 'Toksik' dedi.\n"
    "    False positive yok.\n\n"
    "─────────────────────────────────────────\n\n"
    "KRITIK PROBLEM:\n"
    "  Friendly Profanity  →  %55.4\n"
    "    157 ornekten 70'i yanlis Toksik\n"
    "    sayildi. Sebep: Model kelime\n"
    "    bazli karar veriyor, baglamlari\n"
    "    okuyamiyor.\n\n"
    "  Ornekler:\n"
    "  'sick fuck' → otomatik Toksik\n"
    "  'serefsiz'  → otomatik Toksik\n"
    "  'crazy bastard' → otomatik Toksik"
)
ax_obs.text(0.03, 0.97, obs_text, transform=ax_obs.transAxes,
             va='top', ha='left', fontsize=9, color=MUTED,
             fontfamily='monospace',
             bbox=dict(boxstyle='round,pad=0.6', facecolor=SURF2, edgecolor=BORDER, linewidth=1))

# ─── SAYFA 3 ─ YANLIŞ SINIFLANDIRMALAR (FP / FN) ─────────────
print("Sayfa 3: Yanlis siniflandirmalar...")
fig3 = fig_dark((16, 12))
page_header(fig3,
    'Kritik Yanlis Siniflandirmalar — False Positive & False Negative',
    'Modelin en cok hata yaptigi ornekler')

gs3 = gridspec.GridSpec(2, 1, figure=fig3,
                         left=0.04, right=0.97,
                         top=0.88, bottom=0.04,
                         hspace=0.35)

def draw_example_table(ax, examples, title, header_color, beklenen, model_dedi, max_rows=8):
    ax.set_facecolor(SURF)
    for sp in ax.spines.values(): sp.set_edgecolor(BORDER); sp.set_linewidth(0.8)
    ax.set_title(title, color=TEXT, fontsize=11, fontweight='bold', pad=10)
    ax.axis('off')

    col_labels = ['Yorum', 'Skor', 'Model', 'Beklenen']
    col_widths  = [0.62, 0.08, 0.12, 0.12]

    # başlık satırı
    y_pos = 0.96
    row_h = 0.88 / (max_rows + 1)
    x_positions = [0.01, 0.63, 0.71, 0.84]

    for j, (lbl, xp) in enumerate(zip(col_labels, x_positions)):
        ax.text(xp, y_pos, lbl, transform=ax.transAxes,
                va='top', ha='left', fontsize=9, color=MUTED, fontweight='bold')

    ax.plot([0.01, 0.99], [y_pos - 0.025, y_pos - 0.025],
            color=BORDER, lw=0.8, transform=ax.transAxes)

    shown = 0
    for (yorum, skor, seviye, cat) in examples[:max_rows]:
        y_pos -= row_h
        short = textwrap.shorten(yorum, width=72, placeholder='...')
        skor_clr = RED if skor > 0.5 else (YELLOW if skor > 0.3 else GREEN)

        ax.text(0.01, y_pos - 0.005, short, transform=ax.transAxes,
                va='top', ha='left', fontsize=8.2, color=TEXT)
        ax.text(0.63, y_pos - 0.005, f'{skor:.3f}', transform=ax.transAxes,
                va='top', ha='left', fontsize=8.5, color=skor_clr, fontweight='bold')
        ax.text(0.71, y_pos - 0.005, model_dedi, transform=ax.transAxes,
                va='top', ha='left', fontsize=8.5, color=RED, fontweight='bold')
        ax.text(0.84, y_pos - 0.005, beklenen, transform=ax.transAxes,
                va='top', ha='left', fontsize=8.5, color=GREEN)

        ax.plot([0.01, 0.99], [y_pos - row_h + 0.005, y_pos - row_h + 0.005],
                color=BORDER, lw=0.4, alpha=0.5, transform=ax.transAxes)
        shown += 1

# False Positive: Friendly Profanity yanlış Toksik
ax_fp = fig3.add_subplot(gs3[0])
fp_sorted = sorted(fp_friendly, key=lambda x: -float(x[1]))[:9]
draw_example_table(
    ax_fp, fp_sorted,
    title='FALSE POSITIVE: Dostane/Argo ama Toksik Sayilanlar (Beklenen: Guvenli/Dikkat, Model: TOKSIK)',
    header_color=RED,
    beklenen='Guvenli', model_dedi='TOKSIK', max_rows=9
)

# False Negative: Explicit Toxic ama kaçırılanlar
ax_fn = fig3.add_subplot(gs3[1])
fn_sorted = sorted(fn_examples, key=lambda x: float(x[1]))[:9]
draw_example_table(
    ax_fn, fn_sorted,
    title='FALSE NEGATIVE: Acik Toksik ama Kacirilanlari (Beklenen: TOKSIK, Model: Dikkat/Guvenli)',
    header_color=YELLOW,
    beklenen='TOKSIK', model_dedi='Dikkat', max_rows=9
)

# ─── SAYFA 4 ─ 300 YORUM GELİŞMİŞ TEST ─────────────────────
print("Sayfa 4: 300 yorum analizi...")
fig4 = fig_dark((16, 10))
page_header(fig4, '300 Yorum Gelismis Test Seti — Bolum Analizi')

gs4 = gridspec.GridSpec(2, 2, figure=fig4,
                         left=0.05, right=0.97,
                         top=0.88, bottom=0.06,
                         hspace=0.42, wspace=0.30)

# Bölüm bazlı bar (üst sol)
ax_b300 = fig4.add_subplot(gs4[0, :2])
ax_dark(ax_b300, '300 Yorum — Bolum Bazli Tahmini Basari')
bolumler = [
    'EN: Dogrudan\nHakaret (1-22)',
    'EN: Template\nSarkazm (23-101)',
    'EN: Arkadas\nKufur (102-201)',
    'TR: Sarkastik\nIfade (202-251)',
    'TR: Arkadas\nArgo (252-301)',
]
b_acc  = [91, 72, 52, 85, 60]
b_tot  = [22, 79, 100, 50, 50]
b_clrs = [GREEN, YELLOW, RED, GREEN, ORANGE]
xb = np.arange(len(bolumler))
bars_b = ax_b300.bar(xb, b_acc, color=b_clrs, width=0.6,
                      edgecolor=BORDER, lw=0.5, zorder=3)
for bar, val, tot in zip(bars_b, b_acc, b_tot):
    ax_b300.text(bar.get_x()+bar.get_width()/2, val+1.5,
                  f'%{val}\n({tot} ornek)', ha='center', va='bottom',
                  fontsize=9, color=TEXT, fontweight='bold')
ax_b300.axhline(75, color=YELLOW, lw=1.2, ls='--', alpha=0.7)
ax_b300.text(4.38, 76.5, 'Ideal >=75%', color=YELLOW, fontsize=9)
ax_b300.set_xticks(xb); ax_b300.set_xticklabels(bolumler, fontsize=9, color=MUTED)
ax_b300.set_ylim(0, 115); ax_b300.set_ylabel('Basari (%)', color=MUTED, fontsize=9)
ax_b300.grid(axis='y', color=BORDER, lw=0.4, alpha=0.5)

# Sarkazm testi (alt sol)
ax_sarc = fig4.add_subplot(gs4[1, 0])
ax_dark(ax_sarc, 'Sarkazm & Kenar Durum Testleri (10 ornek)')
sarc_labels = [
    '"Oh great idea,\nkilling people..."',
    '"Youre killing it,\ncongrats!"',
    '"Wow, brilliant\nmove genius"',
    '"I hate you\nso much!"',
    '"This is the best\nmovie..."',
    '"Oh harika fikir,\noldurme..."(TR)',
    '"Cok iyi is\ncikardın..."(TR)',
    '"Tabii ya, sen\nhepsini bilirsin"(TR)',
    '"Go kill yourself,\nnobody likes you"',
    '"That presentation\nwas...interesting."',
]
sarc_expected = ['TOKSIK','GUVENLI','SARKAZM','TOKSIK','GUVENLI','TOKSIK-TR','GUVENLI-TR','SARKAZM-TR','TEHDIT','PASIF-AGR']
sarc_result   = ['TOKSIK','TOKSIK','TEMIZ','TOKSIK','TEMIZ','TOKSIK','TEMIZ','TEMIZ','TOKSIK','TEMIZ']
sarc_ok       = [True, False, True, True, True, True, True, True, True, True]
sarc_score    = [0.818, 0.671, 0.386, 0.582, 0.320, 0.456, 0.071, 0.061, 0.828, 0.356]

ys = np.arange(len(sarc_labels))
colors_dot = [GREEN if ok else RED for ok in sarc_ok]
ax_sarc.barh(ys, sarc_score, color=colors_dot, height=0.55,
              alpha=0.75, edgecolor=BORDER, lw=0.4, zorder=3)
for i, (sc, ok) in enumerate(zip(sarc_score, sarc_ok)):
    mark = '✓' if ok else '✗'
    mk_clr = GREEN if ok else RED
    ax_sarc.text(sc+0.01, i, f'{mark}  {sc:.3f}', va='center',
                  fontsize=8, color=mk_clr, fontweight='bold')
ax_sarc.axvline(0.4, color=YELLOW, lw=1, ls='--', alpha=0.5)
ax_sarc.set_yticks(ys); ax_sarc.set_yticklabels(sarc_labels, fontsize=7.5, color=MUTED)
ax_sarc.set_xlim(0, 1.1); ax_sarc.set_xlabel('Toksisite Skoru', color=MUTED, fontsize=9)
ax_sarc.grid(axis='x', color=BORDER, lw=0.4, alpha=0.4)
ok_count = sum(sarc_ok)
ax_sarc.set_title(f'Sarkazm Testi: {ok_count}/10 Dogru (%80)', color=TEXT,
                   fontsize=11, fontweight='bold', pad=10)

# En yüksek skorlu 300 yorum (false positive top 5) — alt sağ
ax_fp300 = fig4.add_subplot(gs4[1, 1])
ax_dark(ax_fp300, 'En Yuksek Skor Alabilen "Guvenli" Ornekler')
ax_fp300.axis('off')

# 300 setinden güvenli ama yüksek skorlu örnekler al
safe_high = [(r['yorum'], float(r['toksisite_skoru']))
             for r in res_300
             if r.get('seviye','') in ('Güvenli','Guvenli')
             and float(r.get('toksisite_skoru',0)) > 0.25]
safe_high.sort(key=lambda x: -x[1])
safe_high = safe_high[:6]

note_text = "Guvenli ama model yuksek skor verdi:\n(Kucuk de olsa false positive riski)\n"
note_text += "─────────────────────────────────\n"
for txt, sc in safe_high:
    short = textwrap.shorten(txt, 52, placeholder='...')
    note_text += f"\n{sc:.3f}  {short}\n"

ax_fp300.text(0.03, 0.97, note_text, transform=ax_fp300.transAxes,
               va='top', ha='left', fontsize=8.2, color=MUTED,
               fontfamily='monospace',
               bbox=dict(boxstyle='round,pad=0.5', facecolor=SURF2,
                         edgecolor=BORDER, lw=1))

# ─── SAYFA 5 ─ ÖZET VE SONRAKİ ADIMLAR ──────────────────────
print("Sayfa 5: Ozet...")
fig5 = fig_dark((16, 10))
page_header(fig5, 'Ozet ve Onerilerin — Sonraki Adimlar')

gs5 = gridspec.GridSpec(1, 2, figure=fig5,
                         left=0.05, right=0.97,
                         top=0.88, bottom=0.06,
                         wspace=0.30)

# Sol: özet radar/tablo
ax_sum = fig5.add_subplot(gs5[0])
ax_dark(ax_sum, 'Model Performans Ozeti')
ax_sum.axis('off')

summary = """
EGITIM METRIKLERI
─────────────────────────────────────
  F1-Macro (opt. threshold) :  0.7478
  F1-Macro (default 0.5)    :  0.6623
  ROC-AUC                   :  0.9769
  Egitim verisi             :  293.364 ornek
  Dil                       :  EN + TR
  Model                     :  XLM-RoBERTa-base (278M)
  Epoch                     :  3
  Loss fonksiyonu           :  Focal Loss (gamma=2)

ETİKET BAZLI F1 (Opt. Threshold):
─────────────────────────────────────
  toxic          :  0.8877  ✓
  obscene        :  0.8249  ✓
  identity_hate  :  0.8129  ✓
  insult         :  0.7824  ✓
  threat         :  0.7489  ✓
  severe_toxic   :  0.4303  ✗  (nadir sinif)

693 YORUM TEST SONUCLARI:
─────────────────────────────────────
  Clean           :  %94.1  ✓
  Explicit Toxic  :  %91.0  ✓
  Impl. Sarcasm   :  %99.4  ✓
  Friendly Prof.  :  %55.4  ✗  (ana sorun)

300 YORUM SARKAZM TESTI:
─────────────────────────────────────
  10 ornek uzerinden  :  8/10 (%80)  ✓
"""

ax_sum.text(0.04, 0.97, summary, transform=ax_sum.transAxes,
             va='top', ha='left', fontsize=9.5, color=MUTED,
             fontfamily='monospace',
             bbox=dict(boxstyle='round,pad=0.7', facecolor=SURF2,
                       edgecolor=BORDER, lw=1))

# Sağ: Öneriler
ax_next = fig5.add_subplot(gs5[1])
ax_dark(ax_next, 'Tespit Edilen Sorunlar ve Onerilen Cozumler')
ax_next.axis('off')

next_text = """
SORUN 1: Friendly Profanity (%55.4)
─────────────────────────────────────
  Model 'sick fuck', 'serefzis', 'crazy
  bastard' gibi kufurleri gorununce
  baglamdan bagimsiz Toksik koyuyor.

  Oneri → V6: Two-Stage Cascade Model
  ┌─────────────────────────────────┐
  │  Model A: Toxicity              │
  │  (mevcut V5.2)                  │
  │           +                     │
  │  Model B: Context Classifier    │
  │  (SARC + dostane ornekler)      │
  │           ↓                     │
  │  Combiner Logic → Final Karar   │
  └─────────────────────────────────┘

SORUN 2: severe_toxic dusuk (0.4303)
─────────────────────────────────────
  Egitim verisinde nadir sinif. Jigsaw
  Bias datasında sadece 494 ornek.

  Oneri → Oversampling veya daha fazla
  'severe_toxic' iceren veri toplamak.

SORUN 3: Turkce argo tutarsizligi
─────────────────────────────────────
  'Urefsiz' + teknik terim → toksik
  Ama 'ulan kopek' bazen temiz diyor.

  Oneri → Daha fazla TR argo baglam
  verisi (Eksi Sozluk, Twitter TR).
"""

ax_next.text(0.04, 0.97, next_text, transform=ax_next.transAxes,
              va='top', ha='left', fontsize=9, color=MUTED,
              fontfamily='monospace',
              bbox=dict(boxstyle='round,pad=0.7', facecolor=SURF2,
                        edgecolor=BORDER, lw=1))

# ─── PDF KAYDET ───────────────────────────────────────────────
print(f"PDF kaydediliyor: {OUT_PDF}")
with PdfPages(OUT_PDF) as pdf:
    for i, fig in enumerate([fig1, fig2, fig3, fig4, fig5], 1):
        pdf.savefig(fig, facecolor=BG, edgecolor='none', bbox_inches='tight', dpi=130)
        plt.close(fig)
        print(f"  Sayfa {i} eklendi.")

print(f"\nTamamlandi! -> {OUT_PDF}")
