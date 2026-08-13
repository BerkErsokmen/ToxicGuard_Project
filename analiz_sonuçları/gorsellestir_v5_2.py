import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import matplotlib.gridspec as gridspec
import numpy as np

# ── RENK PALETİ ──────────────────────────────────────────────
BG        = '#0f172a'
SURFACE   = '#1e293b'
SURFACE2  = '#273548'
BORDER    = '#334155'
TEXT      = '#e2e8f0'
MUTED     = '#94a3b8'
PRIMARY   = '#818cf8'
GREEN     = '#34d399'
RED       = '#f87171'
YELLOW    = '#fbbf24'
ORANGE    = '#fb923c'

# ── FİGÜR ─────────────────────────────────────────────────────
fig = plt.figure(figsize=(16, 10), facecolor=BG)
fig.patch.set_facecolor(BG)

gs = gridspec.GridSpec(
    3, 3,
    figure=fig,
    left=0.05, right=0.97,
    top=0.88, bottom=0.07,
    hspace=0.55, wspace=0.35
)

# ── BAŞLIK ────────────────────────────────────────────────────
fig.text(
    0.5, 0.955,
    '🛡️  ToxicGuard V5.2 — Model Test Sonuçları',
    ha='center', va='center',
    fontsize=20, fontweight='bold', color=TEXT,
    fontfamily='DejaVu Sans'
)
fig.text(
    0.5, 0.925,
    'XLM-RoBERTa-base  |  Focal Loss  |  EN + TR  |  293K Eğitim Verisi',
    ha='center', va='center',
    fontsize=11, color=MUTED
)

# ── YARDIMCI: axes zemin ──────────────────────────────────────
def style_ax(ax, title=None):
    ax.set_facecolor(SURFACE)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)
        spine.set_linewidth(0.8)
    ax.tick_params(colors=MUTED, labelsize=9)
    if title:
        ax.set_title(title, color=TEXT, fontsize=11,
                     fontweight='semibold', pad=10)

# ═══════════════════════════════════════════════════════════════
# BÖLÜM 1 — Versiyon F1 Karşılaştırması (sol üst, 2 sütun)
# ═══════════════════════════════════════════════════════════════
ax_ver = fig.add_subplot(gs[0, :2])
style_ax(ax_ver, 'Versiyon Karşılaştırması — F1-Macro (Optimize Threshold)')

versions = ['V1\nXGBoost', 'V2\nSVM', 'V3\nDistilBERT', 'V4\nXLM-R', 'V5\nXLM-R', 'V5.2 ★\nXLM-R']
f1_vals  = [0.599, 0.599, 0.693, 0.0, 0.6967, 0.7478]
labels_f1 = ['0.599', '0.599', '0.693', 'N/A', '0.697', '0.7478']
colors_v  = [MUTED, MUTED, YELLOW, BORDER, PRIMARY, GREEN]

x = np.arange(len(versions))
bars = ax_ver.bar(x, f1_vals, color=colors_v, width=0.55,
                   edgecolor=BORDER, linewidth=0.5, zorder=3)

# hedef çizgisi
ax_ver.axhline(0.720, color=GREEN, linewidth=1.2, linestyle='--', alpha=0.7, zorder=2)
ax_ver.text(5.45, 0.723, 'Hedef: 0.720', color=GREEN, fontsize=8.5, va='bottom')

# değer etiketleri
for bar, lbl, val in zip(bars, labels_f1, f1_vals):
    if val > 0:
        ax_ver.text(bar.get_x() + bar.get_width()/2,
                    val + 0.008, lbl,
                    ha='center', va='bottom',
                    fontsize=9, color=TEXT, fontweight='bold')

ax_ver.set_xticks(x)
ax_ver.set_xticklabels(versions, fontsize=9, color=MUTED)
ax_ver.set_ylim(0, 0.85)
ax_ver.set_ylabel('F1-Macro', color=MUTED, fontsize=9)
ax_ver.yaxis.label.set_color(MUTED)
ax_ver.tick_params(axis='y', colors=MUTED)
ax_ver.grid(axis='y', color=BORDER, linewidth=0.5, alpha=0.6, zorder=1)

# V5.2 vurgula
bars[5].set_edgecolor(GREEN)
bars[5].set_linewidth(2)

# ═══════════════════════════════════════════════════════════════
# BÖLÜM 2 — 3 Büyük Stat Kutusu (sağ üst)
# ═══════════════════════════════════════════════════════════════
stats = [
    ('F1-Macro', '0.7478', GREEN),
    ('ROC-AUC',  '0.9769', PRIMARY),
    ('Eğitim\nVerisi', '293K', YELLOW),
]

for i, (lbl, val, clr) in enumerate(stats):
    ax_s = fig.add_subplot(gs[0, 2])
    ax_s.set_visible(False)   # placeholder — elle çizeceğiz

# Elle dikdörtgen çiz (gs[0,2] alanı ~)
# Koordinat hesabı: fig transform
for i, (lbl, val, clr) in enumerate(stats):
    x0 = 0.688 + 0.000
    y0 = 0.800 - i * 0.100
    w, h = 0.275, 0.072

    rect = mpatches.FancyBboxPatch(
        (x0, y0), w, h,
        boxstyle='round,pad=0.01',
        transform=fig.transFigure,
        facecolor=SURFACE, edgecolor=clr,
        linewidth=1.5, zorder=5, clip_on=False
    )
    fig.add_artist(rect)

    fig.text(x0 + w/2, y0 + h*0.62, val,
             ha='center', va='center',
             fontsize=16, fontweight='bold', color=clr,
             transform=fig.transFigure, zorder=6)
    fig.text(x0 + w/2, y0 + h*0.18, lbl,
             ha='center', va='center',
             fontsize=8.5, color=MUTED,
             transform=fig.transFigure, zorder=6)

# ═══════════════════════════════════════════════════════════════
# BÖLÜM 3 — 693 Yorum: Kategori Doğruluk (sol orta, progress bar)
# ═══════════════════════════════════════════════════════════════
ax_cat = fig.add_subplot(gs[1, :2])
style_ax(ax_cat, '693 Yorum Geniş Test — Kategori Bazlı Doğruluk')

categories = [
    'Implicit Sarcastic\n(Örtük Sarkastik)',
    'Clean\n(Temiz/Nötr)',
    'Explicit Toxic\n(Açık Toksik)',
    'Friendly Profanity\n(Dostane Küfürlü)',
]
acc    = [99.4, 94.1, 91.0, 55.4]
totals = [160,  153,  223,  157]
clrs   = [GREEN, GREEN, GREEN, RED]

y = np.arange(len(categories))
# arkaplan bar (100%)
ax_cat.barh(y, [100]*4, color=SURFACE2, height=0.5, zorder=2)
# değer bar
bars_cat = ax_cat.barh(y, acc, color=clrs, height=0.5,
                        edgecolor=BORDER, linewidth=0.4, zorder=3)

# etiketler
for i, (a, t) in enumerate(zip(acc, totals)):
    ax_cat.text(a + 1.0, i, f'%{a:.1f}  ({t} örnek)',
                va='center', color=TEXT, fontsize=9.5, fontweight='bold')

ax_cat.set_yticks(y)
ax_cat.set_yticklabels(categories, fontsize=9, color=MUTED)
ax_cat.set_xlim(0, 120)
ax_cat.set_xlabel('Doğruluk (%)', color=MUTED, fontsize=9)
ax_cat.xaxis.label.set_color(MUTED)
ax_cat.tick_params(axis='x', colors=MUTED)
ax_cat.grid(axis='x', color=BORDER, linewidth=0.4, alpha=0.5, zorder=1)
ax_cat.set_xticks([0, 25, 50, 75, 100])
ax_cat.set_xticklabels(['0%', '25%', '50%', '75%', '100%'], fontsize=8)

# ❌ notu
ax_cat.annotate(
    '❌ Ana Sorun: "sick fuck", "şerefsiz" gibi\n   dostane argolar toksik sayılıyor',
    xy=(55.4, 0), xytext=(58, -0.55),
    fontsize=8, color=RED, style='italic',
    arrowprops=dict(arrowstyle='->', color=RED, lw=0.8)
)

# ═══════════════════════════════════════════════════════════════
# BÖLÜM 4 — 693 Yorum: Pie (sağ orta)
# ═══════════════════════════════════════════════════════════════
ax_pie = fig.add_subplot(gs[1, 2])
style_ax(ax_pie, '693 Yorum\nSeviye Dağılımı')
ax_pie.set_aspect('equal')

pie_vals   = [201, 218, 274]
pie_labels = ['Güvenli\n201 (%29)', 'Dikkat\n218 (%31.5)', 'Toksik\n274 (%39.5)']
pie_colors = [GREEN, YELLOW, RED]

wedges, texts = ax_pie.pie(
    pie_vals, colors=pie_colors,
    startangle=90,
    wedgeprops=dict(edgecolor=BG, linewidth=2),
    radius=0.85
)
ax_pie.legend(
    wedges, pie_labels,
    loc='lower center', bbox_to_anchor=(0.5, -0.28),
    fontsize=7.5, frameon=False,
    labelcolor=MUTED
)

# ═══════════════════════════════════════════════════════════════
# BÖLÜM 5 — 300 Yorum: Sarkazm Testi (alt sol)
# ═══════════════════════════════════════════════════════════════
ax_sarc = fig.add_subplot(gs[2, :2])
style_ax(ax_sarc, '300 Yorum Gelişmiş Test — Bölüm Bazlı Değerlendirme')

bolumler = [
    'İngilizce\nDoğrudan Hakaret',
    'İngilizce\nİnce Sarkazm',
    'İngilizce\nArkadaşça Küfür',
    'Türkçe\nÖrtülü Sarkazm',
    'Türkçe\nArkadaşça Argo',
]
# Tahmini başarı oranları (analizden)
basari = [91, 72, 52, 85, 60]
b_clrs = [GREEN, YELLOW, RED, GREEN, ORANGE]

x2 = np.arange(len(bolumler))
bar2 = ax_sarc.bar(x2, basari, color=b_clrs, width=0.55,
                    edgecolor=BORDER, linewidth=0.5, zorder=3)

for bar, val in zip(bar2, basari):
    ax_sarc.text(bar.get_x() + bar.get_width()/2,
                 val + 1.5, f'%{val}',
                 ha='center', va='bottom',
                 fontsize=9.5, color=TEXT, fontweight='bold')

ax_sarc.axhline(75, color=YELLOW, linewidth=1, linestyle='--', alpha=0.5)
ax_sarc.text(4.45, 76.5, 'İdeal ≥75%', color=YELLOW, fontsize=8)

ax_sarc.set_xticks(x2)
ax_sarc.set_xticklabels(bolumler, fontsize=8.5, color=MUTED)
ax_sarc.set_ylim(0, 110)
ax_sarc.set_ylabel('Tahmini Doğruluk (%)', color=MUTED, fontsize=9)
ax_sarc.tick_params(axis='y', colors=MUTED)
ax_sarc.grid(axis='y', color=BORDER, linewidth=0.4, alpha=0.5, zorder=1)

# ═══════════════════════════════════════════════════════════════
# BÖLÜM 6 — Etiket Bazlı F1 (alt sağ)
# ═══════════════════════════════════════════════════════════════
ax_lbl = fig.add_subplot(gs[2, 2])
style_ax(ax_lbl, 'Etiket F1 Skorları\n(Opt. Threshold)')

etiketler = ['toxic', 'severe\ntoxic', 'obscene', 'threat', 'insult', 'identity\nhate']
f1_lbl    = [0.8877, 0.4303, 0.8249, 0.7489, 0.7824, 0.8129]
clr_lbl   = [GREEN if v >= 0.7 else (YELLOW if v >= 0.5 else RED) for v in f1_lbl]

y3 = np.arange(len(etiketler))
ax_lbl.barh(y3, f1_lbl, color=clr_lbl, height=0.55,
             edgecolor=BORDER, linewidth=0.4, zorder=3)

for i, v in enumerate(f1_lbl):
    ax_lbl.text(v + 0.01, i, f'{v:.3f}',
                va='center', fontsize=8.5,
                color=TEXT, fontweight='bold')

ax_lbl.set_yticks(y3)
ax_lbl.set_yticklabels(etiketler, fontsize=8.5, color=MUTED)
ax_lbl.set_xlim(0, 1.08)
ax_lbl.axvline(0.7, color=YELLOW, linewidth=0.8, linestyle='--', alpha=0.6)
ax_lbl.tick_params(axis='x', colors=MUTED)
ax_lbl.grid(axis='x', color=BORDER, linewidth=0.4, alpha=0.5, zorder=1)
ax_lbl.set_xlabel('F1 Skoru', color=MUTED, fontsize=8)

# ═══════════════════════════════════════════════════════════════
# ALT NOT
# ═══════════════════════════════════════════════════════════════
fig.text(
    0.5, 0.018,
    'Eğitim: Google Colab T4 GPU  |  Model: xlm-roberta-base (278M parametre)  |  '
    'Veri: Kaggle Jigsaw + SARC + SemEval + Overfit-GM TR + Toygar TR',
    ha='center', fontsize=8, color=MUTED
)

# ═══════════════════════════════════════════════════════════════
# KAYDET
# ═══════════════════════════════════════════════════════════════
out = os.path.join(os.path.dirname(__file__), 'toxicguard_v5_2_python_gorsel.png')
plt.savefig(out, dpi=150, bbox_inches='tight',
            facecolor=BG, edgecolor='none')
plt.close()
print(f'Kaydedildi: {out}')
