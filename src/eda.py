"""
ToxicGuard - Keşifsel Veri Analizi (EDA)
Veri setini analiz edip görselleştirmeler oluşturur.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # GUI olmadan çalıştır
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

# Proje kökünü path'e ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils import LABEL_COLS, LABEL_NAMES_TR, get_path, load_clean_data

# Stil ayarları
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette('husl')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12


def ensure_plots_dir():
    """EDA grafik dizinini oluştur."""
    plots_dir = get_path('reports', 'eda_plots')
    os.makedirs(plots_dir, exist_ok=True)
    return plots_dir


def plot_label_distribution(df, plots_dir):
    """1.1 - Etiket dağılım analizi."""
    print("\n📊 1.1 Etiket Dağılım Analizi")
    
    counts = df[LABEL_COLS].sum().sort_values(ascending=False)
    labels_tr = [LABEL_NAMES_TR[c] for c in counts.index]
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Bar chart
    colors = sns.color_palette('husl', len(LABEL_COLS))
    bars = axes[0].bar(labels_tr, counts.values, color=colors, edgecolor='white', linewidth=1.5)
    axes[0].set_title('Toksisite Etiketlerinin Dağılımı', fontweight='bold')
    axes[0].set_ylabel('Yorum Sayısı')
    axes[0].tick_params(axis='x', rotation=30)
    for bar, count in zip(bars, counts.values):
        axes[0].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 200,
                     f'{count:,}', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # Pie chart
    axes[1].pie(counts.values, labels=labels_tr, autopct='%1.1f%%', colors=colors,
                startangle=90, textprops={'fontsize': 10})
    axes[1].set_title('Etiket Oranları', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, '01_label_distribution.png'), dpi=150, bbox_inches='tight')
    plt.close()
    
    for col, count in counts.items():
        print(f"  {LABEL_NAMES_TR[col]:15s}: {count:>6,} ({count/len(df)*100:.1f}%)")


def plot_class_imbalance(df, plots_dir):
    """1.2 - Sınıf dengesizliği analizi."""
    print("\n⚖️ 1.2 Sınıf Dengesizliği Tespiti")
    
    # Toksik vs zararsız
    has_any_toxic = df[LABEL_COLS].any(axis=1)
    toxic_count = has_any_toxic.sum()
    clean_count = len(df) - toxic_count
    
    print(f"  Zararsız: {clean_count:>6,} ({clean_count/len(df)*100:.1f}%)")
    print(f"  Toksik:   {toxic_count:>6,} ({toxic_count/len(df)*100:.1f}%)")
    print(f"  Oran:     1:{clean_count//toxic_count} (toksik:zararsız)")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Toksik vs Zararsız
    labels = ['Zararsız', 'Toksik']
    sizes = [clean_count, toxic_count]
    colors_pie = ['#2ecc71', '#e74c3c']
    explode = (0, 0.08)
    axes[0].pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                colors=colors_pie, shadow=True, startangle=90,
                textprops={'fontsize': 13, 'fontweight': 'bold'})
    axes[0].set_title('Toksik vs Zararsız Yorum Oranı', fontweight='bold')
    
    # Multi-label analiz: kaç etikete sahip
    label_count = df[LABEL_COLS].sum(axis=1)
    label_dist = label_count.value_counts().sort_index()
    
    axes[1].bar(label_dist.index.astype(str), label_dist.values, color='#3498db', edgecolor='white')
    axes[1].set_title('Yorum Başına Etiket Sayısı Dağılımı', fontweight='bold')
    axes[1].set_xlabel('Etiket Sayısı')
    axes[1].set_ylabel('Yorum Sayısı')
    for i, (idx, val) in enumerate(label_dist.items()):
        axes[1].text(i, val + 500, f'{val:,}', ha='center', fontweight='bold', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, '02_class_imbalance.png'), dpi=150, bbox_inches='tight')
    plt.close()


def plot_label_correlation(df, plots_dir):
    """1.3 - Multi-label korelasyon analizi."""
    print("\n🔗 1.3 Multi-Label Korelasyon Analizi")
    
    corr = df[LABEL_COLS].corr()
    labels_tr = [LABEL_NAMES_TR[c] for c in LABEL_COLS]
    
    fig, ax = plt.subplots(figsize=(10, 8))
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                mask=mask, square=True, linewidths=2, linecolor='white',
                xticklabels=labels_tr, yticklabels=labels_tr,
                ax=ax, vmin=-1, vmax=1,
                annot_kws={'fontsize': 12, 'fontweight': 'bold'})
    ax.set_title('Etiketler Arası Korelasyon Matrisi', fontweight='bold', fontsize=14, pad=20)
    
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, '03_label_correlation.png'), dpi=150, bbox_inches='tight')
    plt.close()
    
    # Yüksek korelasyonları raporla
    for i in range(len(LABEL_COLS)):
        for j in range(i+1, len(LABEL_COLS)):
            c = corr.iloc[i, j]
            if abs(c) > 0.4:
                print(f"  {LABEL_NAMES_TR[LABEL_COLS[i]]} ↔ {LABEL_NAMES_TR[LABEL_COLS[j]]}: {c:.3f}")


def plot_text_stats(df, plots_dir):
    """1.4 - Metin istatistikleri."""
    print("\n📝 1.4 Metin İstatistikleri")
    
    df['word_count'] = df['cleaned_text'].str.split().str.len()
    df['char_count'] = df['cleaned_text'].str.len()
    
    has_toxic = df[LABEL_COLS].any(axis=1)
    
    print(f"  Ortalama kelime (tüm):     {df['word_count'].mean():.1f}")
    print(f"  Ortalama kelime (toksik):   {df[has_toxic]['word_count'].mean():.1f}")
    print(f"  Ortalama kelime (zararsız): {df[~has_toxic]['word_count'].mean():.1f}")
    print(f"  Medyan kelime:              {df['word_count'].median():.0f}")
    print(f"  En kısa yorum:             {df['word_count'].min()} kelime")
    print(f"  En uzun yorum:             {df['word_count'].max()} kelime")
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Kelime sayısı dağılımı - toksik vs zararsız
    axes[0].hist(df[~has_toxic]['word_count'].clip(upper=200), bins=80, alpha=0.6,
                 label='Zararsız', color='#2ecc71', density=True)
    axes[0].hist(df[has_toxic]['word_count'].clip(upper=200), bins=80, alpha=0.6,
                 label='Toksik', color='#e74c3c', density=True)
    axes[0].set_title('Kelime Sayısı Dağılımı (Toksik vs Zararsız)', fontweight='bold')
    axes[0].set_xlabel('Kelime Sayısı')
    axes[0].set_ylabel('Yoğunluk')
    axes[0].legend(fontsize=11)
    axes[0].set_xlim(0, 200)
    
    # Etiket bazlı kelime sayısı box plot
    box_data = []
    box_labels = []
    for col in LABEL_COLS:
        data = df[df[col] == 1]['word_count'].clip(upper=300)
        box_data.append(data)
        box_labels.append(LABEL_NAMES_TR[col])
    
    bp = axes[1].boxplot(box_data, tick_labels=box_labels, patch_artist=True, showfliers=False)
    colors = sns.color_palette('husl', len(LABEL_COLS))
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    axes[1].set_title('Etiket Bazlı Kelime Sayısı Dağılımı', fontweight='bold')
    axes[1].set_ylabel('Kelime Sayısı')
    axes[1].tick_params(axis='x', rotation=30)
    
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, '04_text_statistics.png'), dpi=150, bbox_inches='tight')
    plt.close()
    
    # Temizle
    df.drop(columns=['word_count', 'char_count'], inplace=True, errors='ignore')


def plot_wordclouds(df, plots_dir):
    """1.5 - Kelime bulutu."""
    print("\n☁️ 1.5 Kelime Bulutu (WordCloud)")
    
    has_toxic = df[LABEL_COLS].any(axis=1)
    
    fig, axes = plt.subplots(1, 2, figsize=(18, 7))
    
    # Toksik kelime bulutu
    toxic_text = ' '.join(df[has_toxic]['cleaned_text'].dropna().head(20000))
    if toxic_text.strip():
        wc_toxic = WordCloud(width=800, height=400, background_color='black',
                             colormap='Reds', max_words=150, max_font_size=100).generate(toxic_text)
        axes[0].imshow(wc_toxic, interpolation='bilinear')
    axes[0].set_title('🔴 Toksik Yorumlar — En Sık Kullanılan Kelimeler', fontweight='bold')
    axes[0].axis('off')
    
    # Zararsız kelime bulutu
    clean_text_str = ' '.join(df[~has_toxic]['cleaned_text'].dropna().head(20000))
    if clean_text_str.strip():
        wc_clean = WordCloud(width=800, height=400, background_color='white',
                             colormap='Greens', max_words=150, max_font_size=100).generate(clean_text_str)
        axes[1].imshow(wc_clean, interpolation='bilinear')
    axes[1].set_title('🟢 Zararsız Yorumlar — En Sık Kullanılan Kelimeler', fontweight='bold')
    axes[1].axis('off')
    
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, '05_wordclouds.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  Kelime bulutları oluşturuldu.")


def plot_data_quality(df, plots_dir):
    """1.6 - Veri kalitesi kontrolü."""
    print("\n🔍 1.6 Veri Kalitesi Kontrolü")
    
    total = len(df)
    null_count = df['cleaned_text'].isna().sum()
    empty_count = (df['cleaned_text'].str.strip() == '').sum() if null_count < total else 0
    valid = total - null_count - empty_count
    
    print(f"  Toplam satır:   {total:,}")
    print(f"  NaN satır:      {null_count:,}")
    print(f"  Boş satır:      {empty_count:,}")
    print(f"  Geçerli satır:  {valid:,} ({valid/total*100:.1f}%)")
    
    # Özet istatistik tablosu
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axis('off')
    
    summary_data = [
        ['Toplam Yorum', f'{total:,}'],
        ['Geçerli Yorum', f'{valid:,} ({valid/total*100:.1f}%)'],
        ['NaN / Boş', f'{null_count + empty_count:,}'],
        ['Etiket Sayısı', str(len(LABEL_COLS))],
        ['Toksik Yorum', f'{df[LABEL_COLS].any(axis=1).sum():,}'],
        ['Zararsız Yorum', f'{(~df[LABEL_COLS].any(axis=1)).sum():,}'],
    ]
    
    table = ax.table(cellText=summary_data, colLabels=['Metrik', 'Değer'],
                     loc='center', cellLoc='center',
                     colWidths=[0.35, 0.35])
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 1.8)
    
    # Stil
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor('#34495e')
            cell.set_text_props(color='white', fontweight='bold')
        else:
            cell.set_facecolor('#ecf0f1' if row % 2 == 0 else 'white')
    
    ax.set_title('Veri Seti Özeti', fontweight='bold', fontsize=14, pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, '06_data_summary.png'), dpi=150, bbox_inches='tight')
    plt.close()


def run_eda():
    """Tam EDA pipeline'ını çalıştır."""
    print("=" * 60)
    print("FAZ 1: KEŞİFSEL VERİ ANALİZİ (EDA)")
    print("=" * 60)
    
    plots_dir = ensure_plots_dir()
    
    # Veriyi yükle
    print("\nVeri yükleniyor...")
    df = load_clean_data()
    print(f"Yüklenen veri: {len(df)} satır, {len(df.columns)} sütun")
    print(f"Sütunlar: {list(df.columns)}")
    
    # Tüm analizleri çalıştır
    plot_label_distribution(df, plots_dir)
    plot_class_imbalance(df, plots_dir)
    plot_label_correlation(df, plots_dir)
    plot_text_stats(df, plots_dir)
    plot_wordclouds(df, plots_dir)
    plot_data_quality(df, plots_dir)
    
    print("\n" + "=" * 60)
    print(f"✅ EDA tamamlandı! Grafikler: {plots_dir}")
    print("=" * 60)


if __name__ == '__main__':
    run_eda()
